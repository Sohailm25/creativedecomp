# ABOUTME: Runs the bounded instruction-tuned refusal pivot on the smallest GemmaScope v2-backed Gemma stack that passed local feasibility.
# ABOUTME: Freezes the paired Gemma 3 270M IT plus GemmaScope v2 residual release, then runs a refusal layer sweep and matched output gate on that stack.

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime
import json
from pathlib import Path
import re
import sys
from typing import Any

import numpy as np
from repeng import DatasetEntry
from repeng.extract import batched_get_hiddens
from sae_lens import SAE
from sae_lens.loading.pretrained_saes_directory import get_pretrained_saes_directory


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from run_creativity_direction_calibration import (  # noqa: E402
    compute_distinct_unigram_ratio,
    format_coeff_slug,
    parse_steering_coeffs_argument,
)
from run_creativity_direction_layer_sweep import (  # noqa: E402
    compute_margin_zscore,
    compute_mean_difference_direction,
    rank_layer_rows,
)
from run_creativity_direction_smoke import (  # noqa: E402
    ROOT,
    DEFAULT_BATCH_SIZE,
    DEFAULT_MAX_PAIRS,
    align_direction_sign,
    load_model_and_tokenizer,
    load_prompt_rows,
    project_onto_direction_safe,
    select_device,
    summarize_pairwise_projections,
    write_json,
    write_jsonl,
)
from run_creativity_output_gate import (  # noqa: E402
    build_condition_lookup,
    map_judge_winner_to_condition_id,
    parse_label_judgment_or_tie,
    render_pairwise_judge_prompt,
    resolve_order_robust_winner,
    summarize_condition_outputs,
    validate_generated_outputs,
)
from run_generation_side_creativity_smoke import (  # noqa: E402
    generate_completion,
    generate_with_control,
    path_for_summary,
    prepare_output_dir,
)
from run_refusal_output_gate import (  # noqa: E402
    build_pairwise_comparisons,
    load_judge_templates,
    summarize_gate_assessment,
    summarize_pairwise_judgments,
)


DEFAULT_MODEL_ID = "google/gemma-3-270m-it"
DEFAULT_SAE_RELEASE = "gemma-scope-2-270m-it-res"
DEFAULT_REFERENCE_SAE_ID = "layer_12_width_16k_l0_medium"
DEFAULT_SPLIT_PATH = ROOT / "prompts" / "refusal_direction_v1_pilot_pairs.jsonl"
DEFAULT_TEMPLATES_PATH = ROOT / "prompts" / "refusal_direction_it_v1_templates.json"
DEFAULT_JUDGE_TEMPLATES_PATH = ROOT / "prompts" / "refusal_direction_output_gate_v1_judges.json"
DEFAULT_MAX_PROMPTS = 12
DEFAULT_MAX_NEW_TOKENS = 96
DEFAULT_JUDGE_MAX_NEW_TOKENS = 6
DEFAULT_STEERING_COEFFS = "0.5,1.0"
DEFAULT_SEED = 8100


def default_sweep_output_dir() -> Path:
    run_date = datetime.now().strftime("%Y%m%d")
    return ROOT / "results" / "refusal_direction" / f"{run_date}-gemma3-270m-it-layer-sweep-v1-mean-difference"


def default_gate_output_dir() -> Path:
    run_date = datetime.now().strftime("%Y%m%d")
    return ROOT / "results" / "steering_eval" / f"{run_date}-gemma3-270m-it-refusal-output-gate-v1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the bounded instruction-tuned refusal pivot on the smallest paired Gemma 3 plus GemmaScope v2 stack."
    )
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID)
    parser.add_argument("--sae-release", default=DEFAULT_SAE_RELEASE)
    parser.add_argument("--reference-sae-id", default=DEFAULT_REFERENCE_SAE_ID)
    parser.add_argument("--split-path", type=Path, default=DEFAULT_SPLIT_PATH)
    parser.add_argument("--templates-path", type=Path, default=DEFAULT_TEMPLATES_PATH)
    parser.add_argument("--judge-templates-path", type=Path, default=DEFAULT_JUDGE_TEMPLATES_PATH)
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--max-pairs", type=int, default=DEFAULT_MAX_PAIRS)
    parser.add_argument("--max-prompts", type=int, default=DEFAULT_MAX_PROMPTS)
    parser.add_argument("--max-new-tokens", type=int, default=DEFAULT_MAX_NEW_TOKENS)
    parser.add_argument("--judge-max-new-tokens", type=int, default=DEFAULT_JUDGE_MAX_NEW_TOKENS)
    parser.add_argument("--steering-coeffs", default=DEFAULT_STEERING_COEFFS)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--device", choices=["auto", "mps", "cpu"], default="auto")
    parser.add_argument("--sweep-output-dir", type=Path, default=None)
    parser.add_argument("--gate-output-dir", type=Path, default=None)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def load_templates(path: Path) -> dict[str, str]:
    templates = json.loads(path.read_text(encoding="utf-8"))
    required_keys = ("prompt_only_refusal_system_prompt",)
    for key in required_keys:
        if key not in templates:
            raise KeyError(f"missing template key: {key}")
    return templates


def parse_available_layers_from_sae_ids(sae_ids: list[str]) -> list[int]:
    layers: set[int] = set()
    for sae_id in sae_ids:
        match = re.search(r"(?:^|/)layer_(\d+)_", sae_id)
        if match is None:
            continue
        layers.add(int(match.group(1)))
    if not layers:
        raise ValueError("no layer ids found in sae ids")
    return sorted(layers)


def load_available_layers_for_release(release: str) -> list[int]:
    pretrained_directory = get_pretrained_saes_directory()
    if release not in pretrained_directory:
        raise KeyError(f"unknown SAE release: {release}")
    entry = pretrained_directory[release]
    return parse_available_layers_from_sae_ids(list(entry.saes_map.keys()))


def extract_assistant_response(text: str) -> str:
    delimiter = "\n\nResponse:\n"
    if delimiter not in text:
        raise ValueError(f"could not extract assistant response from transcript: {text!r}")
    return text.split(delimiter, maxsplit=1)[1].strip()


def build_generation_messages(
    prompt_text: str,
    prompt_mode: str,
    templates: dict[str, str],
) -> list[dict[str, str]]:
    if prompt_mode == "neutral":
        return [{"role": "user", "content": prompt_text}]
    if prompt_mode == "prompt_only_refusal":
        return [
            {
                "role": "system",
                "content": templates["prompt_only_refusal_system_prompt"],
            },
            {"role": "user", "content": prompt_text},
        ]
    raise ValueError(f"unknown prompt mode: {prompt_mode}")


def render_chat_transcript(
    tokenizer,
    messages: list[dict[str, str]],
    *,
    add_generation_prompt: bool,
) -> str:
    return tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=add_generation_prompt,
    )


def build_contrastive_dataset(
    prompt_rows: list[dict[str, Any]],
    tokenizer,
) -> list[DatasetEntry]:
    dataset: list[DatasetEntry] = []
    for row in prompt_rows:
        prompt_text = str(row["prompt_text"])
        positive_assistant = extract_assistant_response(str(row["positive_text"]))
        negative_assistant = extract_assistant_response(str(row["negative_text"]))
        positive = render_chat_transcript(
            tokenizer,
            [
                {"role": "user", "content": prompt_text},
                {"role": "assistant", "content": positive_assistant},
            ],
            add_generation_prompt=False,
        )
        negative = render_chat_transcript(
            tokenizer,
            [
                {"role": "user", "content": prompt_text},
                {"role": "assistant", "content": negative_assistant},
            ],
            add_generation_prompt=False,
        )
        dataset.append(DatasetEntry(positive=positive, negative=negative))
    return dataset


def build_output_gate_conditions(
    hidden_layer: int,
    steering_coeffs: list[float],
) -> list[dict[str, Any]]:
    conditions: list[dict[str, Any]] = [
        {
            "condition_id": "neutral_unsteered",
            "prompt_mode": "neutral",
            "hidden_layer": None,
            "steering_coeff": 0.0,
            "normalize_control": False,
        },
        {
            "condition_id": "refusal_prompt_unsteered",
            "prompt_mode": "prompt_only_refusal",
            "hidden_layer": None,
            "steering_coeff": 0.0,
            "normalize_control": False,
        },
    ]
    for coeff in steering_coeffs:
        conditions.append(
            {
                "condition_id": f"neutral_steered_layer{hidden_layer}_coeff_{format_coeff_slug(coeff)}",
                "prompt_mode": "neutral",
                "hidden_layer": hidden_layer,
                "steering_coeff": coeff,
                "normalize_control": True,
            }
        )
    return conditions


def generate_judge_response_chat(
    model,
    tokenizer,
    prompt_text: str,
    max_new_tokens: int,
) -> str:
    chat_prompt = render_chat_transcript(
        tokenizer,
        [{"role": "user", "content": prompt_text}],
        add_generation_prompt=True,
    )
    encoded = tokenizer(chat_prompt, return_tensors="pt")
    encoded = {key: value.to(model.device) for key, value in encoded.items()}
    output_ids = model.generate(
        **encoded,
        do_sample=False,
        temperature=None,
        top_p=None,
        top_k=None,
        min_new_tokens=1,
        max_new_tokens=max_new_tokens,
        pad_token_id=tokenizer.pad_token_id,
        eos_token_id=tokenizer.eos_token_id,
    )[0]
    prompt_length = int(encoded["input_ids"].shape[1])
    completion_ids = output_ids[prompt_length:]
    return tokenizer.decode(completion_ids, skip_special_tokens=True).strip()


def compute_repeated_bigram_fraction(text: str) -> float:
    tokens = [token for token in text.lower().split() if token]
    if len(tokens) < 2:
        return 0.0
    bigrams = list(zip(tokens[:-1], tokens[1:]))
    counts = Counter(bigrams)
    repeated_bigram_count = sum(count - 1 for count in counts.values() if count > 1)
    return float(repeated_bigram_count / len(bigrams))


def load_reference_sae_summary(release: str, sae_id: str) -> dict[str, Any]:
    sae = SAE.from_pretrained(release=release, sae_id=sae_id)
    return {
        "release": release,
        "sae_id": sae_id,
        "d_in": int(sae.cfg.d_in),
        "d_sae": int(sae.cfg.d_sae),
        "dtype": str(sae.cfg.dtype),
    }


def build_layer_row(
    hidden_layer: int,
    prompt_rows: list[dict[str, Any]],
    layer_hiddens: np.ndarray,
) -> tuple[dict[str, Any], np.ndarray, list[dict[str, Any]]]:
    direction = compute_mean_difference_direction(
        layer_hiddens[::2],
        layer_hiddens[1::2],
    )
    direction = align_direction_sign(layer_hiddens, direction)
    projections = project_onto_direction_safe(layer_hiddens, direction)
    summary = summarize_pairwise_projections(prompt_rows, projections)
    margins = np.asarray([detail["margin"] for detail in summary["pair_details"]], dtype=np.float64)
    row = {
        "hidden_layer": hidden_layer,
        "pair_count": summary["pair_count"],
        "positive_mean_projection": summary["positive_mean_projection"],
        "negative_mean_projection": summary["negative_mean_projection"],
        "mean_margin": summary["mean_margin"],
        "positive_gt_negative_fraction": summary["positive_gt_negative_fraction"],
        "margin_std": float(np.std(margins, ddof=0)),
        "margin_zscore": compute_margin_zscore(margins),
        "vector_norm": float(np.linalg.norm(direction)),
    }
    return row, direction, summary["pair_details"]


def write_sweep_readme(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Instruction-Tuned Refusal Layer Sweep",
        "",
        f"- Generated at: `{summary['created_at']}`",
        f"- Model: `{summary['model_id']}`",
        f"- Device: `{summary['device']}`",
        f"- SAE release: `{summary['sae_release']}`",
        f"- Reference SAE id: `{summary['reference_sae']['sae_id']}`",
        f"- Candidate layers: `{summary['candidate_layers']}`",
        f"- Pair count: `{summary['pair_count']}`",
        f"- Best layer: `{summary['best_layer']}`",
        "",
        "Top layers:",
    ]
    for row in summary["top_layers"]:
        lines.append(
            f"- layer `{row['hidden_layer']}`: fraction `{row['positive_gt_negative_fraction']:.6f}`, "
            f"margin `{row['mean_margin']:.6f}`, z-score `{row['margin_zscore']:.6f}`"
        )
    lines.extend(
        [
            "",
            "Artifacts:",
            "- `summary.json`",
            "- `layer_metrics.jsonl`",
            "- `best_layer_pair_details.jsonl`",
            "- `directions.npz`",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_gate_readme(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Instruction-Tuned Refusal Output Gate",
        "",
        f"- Generated at: `{summary['created_at']}`",
        f"- Model: `{summary['model_id']}`",
        f"- Device: `{summary['device']}`",
        f"- SAE release: `{summary['sae_release']}`",
        f"- Prompt count: `{summary['prompt_count']}`",
        f"- Primary hidden layer: `{summary['hidden_layer']}`",
        f"- Steering coefficients: `{summary['steering_coeffs']}`",
        f"- Max new tokens: `{summary['max_new_tokens']}`",
        f"- Judge max new tokens: `{summary['judge_max_new_tokens']}`",
        f"- Refusal baseline system prompt: `{summary['templates']['prompt_only_refusal_system_prompt']}`",
        f"- Automatic pass recommendation: `{summary['gate_assessment']['automatic_pass_recommendation']}`",
        f"- Automatic pass rule: `{summary['gate_assessment']['automatic_pass_rule']}`",
        "",
        "Condition summaries:",
    ]
    for row in summary["condition_summaries"]:
        lines.append(
            f"- `{row['condition_id']}`: mean words `{row['mean_completion_word_count']:.2f}`, "
            f"meta fraction `{row['meta_marker_fraction']:.3f}`, "
            f"distinct-unigram ratio `{row['mean_distinct_unigram_ratio']:.3f}`, "
            f"repeated-bigram fraction `{row['mean_repeated_bigram_fraction']:.3f}`"
        )
    lines.extend(["", "Pairwise judgment summaries:"])
    for row in summary["comparison_summaries"]:
        lines.append(
            f"- `{row['comparison_id']}`: refusal candidate win `{row['refusal_candidate_win_fraction']:.3f}`, "
            f"refusal reference win `{row['refusal_reference_win_fraction']:.3f}`, "
            f"coherence candidate win `{row['coherence_candidate_win_fraction']:.3f}`, "
            f"coherence reference win `{row['coherence_reference_win_fraction']:.3f}`"
        )
    lines.extend(
        [
            "",
            "Artifacts:",
            "- `summary.json`",
            "- `outputs.jsonl`",
            "- `pairwise_judgments.jsonl`",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_layer_sweep(
    *,
    model,
    tokenizer,
    prompt_rows: list[dict[str, Any]],
    candidate_layers: list[int],
    batch_size: int,
    model_id: str,
    device: str,
    sae_release: str,
    reference_sae_summary: dict[str, Any],
    output_dir: Path,
    overwrite: bool,
) -> tuple[dict[str, Any], np.ndarray]:
    prepare_output_dir(output_dir, overwrite=overwrite)
    dataset = build_contrastive_dataset(prompt_rows, tokenizer)
    contrast_texts = [text for entry in dataset for text in (entry.positive, entry.negative)]
    hidden_state_map = batched_get_hiddens(
        model,
        tokenizer,
        contrast_texts,
        candidate_layers,
        batch_size=batch_size,
    )
    layer_rows: list[dict[str, Any]] = []
    directions: dict[str, np.ndarray] = {}
    pair_details_by_layer: dict[int, list[dict[str, Any]]] = {}
    for hidden_layer in candidate_layers:
        row, direction, pair_details = build_layer_row(
            hidden_layer=hidden_layer,
            prompt_rows=prompt_rows,
            layer_hiddens=np.asarray(hidden_state_map[hidden_layer], dtype=np.float32),
        )
        layer_rows.append(row)
        directions[f"layer_{hidden_layer}"] = direction
        pair_details_by_layer[hidden_layer] = pair_details

    ranked_rows = rank_layer_rows(layer_rows)
    best_layer = int(ranked_rows[0]["hidden_layer"])
    summary = {
        "created_at": datetime.now().isoformat(),
        "model_id": model_id,
        "device": device,
        "sae_release": sae_release,
        "reference_sae": reference_sae_summary,
        "pair_count": len(prompt_rows),
        "candidate_layers": candidate_layers,
        "best_layer": best_layer,
        "top_layers": ranked_rows[: min(4, len(ranked_rows))],
        "artifacts": {
            "layer_metrics_jsonl": path_for_summary(output_dir / "layer_metrics.jsonl"),
            "best_layer_pair_details_jsonl": path_for_summary(output_dir / "best_layer_pair_details.jsonl"),
            "directions_npz": path_for_summary(output_dir / "directions.npz"),
        },
    }
    write_json(output_dir / "summary.json", summary)
    write_jsonl(output_dir / "layer_metrics.jsonl", ranked_rows)
    write_jsonl(output_dir / "best_layer_pair_details.jsonl", pair_details_by_layer[best_layer])
    np.savez(output_dir / "directions.npz", **directions)
    write_sweep_readme(output_dir / "README.md", summary)
    return summary, directions[f"layer_{best_layer}"]


def run_output_gate(
    *,
    model,
    tokenizer,
    prompt_rows: list[dict[str, Any]],
    templates: dict[str, str],
    judge_templates: dict[str, str],
    hidden_layer: int,
    direction: np.ndarray,
    steering_coeffs: list[float],
    max_new_tokens: int,
    judge_max_new_tokens: int,
    seed: int,
    model_id: str,
    device: str,
    sae_release: str,
    output_dir: Path,
    overwrite: bool,
) -> dict[str, Any]:
    prepare_output_dir(output_dir, overwrite=overwrite)
    conditions = build_output_gate_conditions(hidden_layer=hidden_layer, steering_coeffs=steering_coeffs)
    output_rows: list[dict[str, Any]] = []

    for prompt_index, prompt_row in enumerate(prompt_rows):
        prompt_id = str(prompt_row["prompt_id"])
        prompt_text = str(prompt_row["prompt_text"])
        for condition_index, condition in enumerate(conditions):
            messages = build_generation_messages(
                prompt_text=prompt_text,
                prompt_mode=str(condition["prompt_mode"]),
                templates=templates,
            )
            rendered_prompt = render_chat_transcript(
                tokenizer,
                messages,
                add_generation_prompt=True,
            )
            sample_seed = seed + (prompt_index * 100) + condition_index
            if condition["hidden_layer"] is None:
                completion_text, full_text = generate_completion(
                    model,
                    tokenizer,
                    prompt_text=rendered_prompt,
                    seed=sample_seed,
                    max_new_tokens=max_new_tokens,
                )
            else:
                completion_text, full_text = generate_with_control(
                    model,
                    tokenizer,
                    prompt_text=rendered_prompt,
                    hidden_layer=int(condition["hidden_layer"]),
                    direction=direction,
                    steering_coeff=float(condition["steering_coeff"]),
                    seed=sample_seed,
                    max_new_tokens=max_new_tokens,
                    normalize_control=bool(condition["normalize_control"]),
                )
            output_rows.append(
                {
                    "prompt_id": prompt_id,
                    "prompt_text": prompt_text,
                    "condition_id": str(condition["condition_id"]),
                    "prompt_mode": str(condition["prompt_mode"]),
                    "hidden_layer": condition["hidden_layer"],
                    "steering_coeff": float(condition["steering_coeff"]),
                    "completion_text": completion_text,
                    "full_text": full_text,
                    "completion_word_count": len(completion_text.split()),
                    "completion_char_count": len(completion_text),
                    "meta_marker_score": 0.0,
                    "distinct_unigram_ratio": compute_distinct_unigram_ratio(completion_text),
                    "repeated_bigram_fraction": compute_repeated_bigram_fraction(completion_text),
                }
            )

    validate_generated_outputs(output_rows, prompt_rows, conditions)
    condition_summaries = summarize_condition_outputs(output_rows)

    dense_condition_ids = [
        str(condition["condition_id"])
        for condition in conditions
        if str(condition["condition_id"]).startswith("neutral_steered_")
    ]
    comparisons = build_pairwise_comparisons(dense_condition_ids)
    condition_lookup = build_condition_lookup(output_rows)
    judgment_rows: list[dict[str, Any]] = []
    for prompt_row in prompt_rows:
        prompt_id = str(prompt_row["prompt_id"])
        prompt_text = str(prompt_row["prompt_text"])
        for comparison in comparisons:
            candidate_row = condition_lookup[(prompt_id, comparison["candidate_condition_id"])]
            reference_row = condition_lookup[(prompt_id, comparison["reference_condition_id"])]

            refusal_forward_prompt = render_pairwise_judge_prompt(
                prompt_text=prompt_text,
                story_a=str(candidate_row["completion_text"]),
                story_b=str(reference_row["completion_text"]),
                judge_template=judge_templates["pairwise_refusal_label_judge"],
            )
            refusal_reverse_prompt = render_pairwise_judge_prompt(
                prompt_text=prompt_text,
                story_a=str(reference_row["completion_text"]),
                story_b=str(candidate_row["completion_text"]),
                judge_template=judge_templates["pairwise_refusal_label_judge"],
            )
            coherence_forward_prompt = render_pairwise_judge_prompt(
                prompt_text=prompt_text,
                story_a=str(candidate_row["completion_text"]),
                story_b=str(reference_row["completion_text"]),
                judge_template=judge_templates["pairwise_coherence_label_judge"],
            )
            coherence_reverse_prompt = render_pairwise_judge_prompt(
                prompt_text=prompt_text,
                story_a=str(reference_row["completion_text"]),
                story_b=str(candidate_row["completion_text"]),
                judge_template=judge_templates["pairwise_coherence_label_judge"],
            )

            refusal_forward_raw = generate_judge_response_chat(
                model,
                tokenizer,
                prompt_text=refusal_forward_prompt,
                max_new_tokens=judge_max_new_tokens,
            )
            refusal_reverse_raw = generate_judge_response_chat(
                model,
                tokenizer,
                prompt_text=refusal_reverse_prompt,
                max_new_tokens=judge_max_new_tokens,
            )
            coherence_forward_raw = generate_judge_response_chat(
                model,
                tokenizer,
                prompt_text=coherence_forward_prompt,
                max_new_tokens=judge_max_new_tokens,
            )
            coherence_reverse_raw = generate_judge_response_chat(
                model,
                tokenizer,
                prompt_text=coherence_reverse_prompt,
                max_new_tokens=judge_max_new_tokens,
            )

            refusal_forward_winner = map_judge_winner_to_condition_id(
                parse_label_judgment_or_tie(refusal_forward_raw),
                comparison["candidate_condition_id"],
                comparison["reference_condition_id"],
            )
            refusal_reverse_winner = map_judge_winner_to_condition_id(
                parse_label_judgment_or_tie(refusal_reverse_raw),
                comparison["reference_condition_id"],
                comparison["candidate_condition_id"],
            )
            coherence_forward_winner = map_judge_winner_to_condition_id(
                parse_label_judgment_or_tie(coherence_forward_raw),
                comparison["candidate_condition_id"],
                comparison["reference_condition_id"],
            )
            coherence_reverse_winner = map_judge_winner_to_condition_id(
                parse_label_judgment_or_tie(coherence_reverse_raw),
                comparison["reference_condition_id"],
                comparison["candidate_condition_id"],
            )

            judgment_rows.append(
                {
                    "prompt_id": prompt_id,
                    "comparison_id": comparison["comparison_id"],
                    "candidate_condition_id": comparison["candidate_condition_id"],
                    "reference_condition_id": comparison["reference_condition_id"],
                    "refusal_winner_condition_id": resolve_order_robust_winner(
                        refusal_forward_winner,
                        refusal_reverse_winner,
                    ),
                    "coherence_winner_condition_id": resolve_order_robust_winner(
                        coherence_forward_winner,
                        coherence_reverse_winner,
                    ),
                    "refusal_forward_response": refusal_forward_raw,
                    "refusal_reverse_response": refusal_reverse_raw,
                    "coherence_forward_response": coherence_forward_raw,
                    "coherence_reverse_response": coherence_reverse_raw,
                }
            )

    comparison_summaries = summarize_pairwise_judgments(judgment_rows, comparisons)
    gate_assessment = summarize_gate_assessment(comparison_summaries)
    summary = {
        "created_at": datetime.now().isoformat(),
        "model_id": model_id,
        "device": device,
        "sae_release": sae_release,
        "prompt_count": len(prompt_rows),
        "hidden_layer": hidden_layer,
        "steering_coeffs": steering_coeffs,
        "max_new_tokens": max_new_tokens,
        "judge_max_new_tokens": judge_max_new_tokens,
        "seed": seed,
        "templates": templates,
        "condition_summaries": condition_summaries,
        "comparison_summaries": comparison_summaries,
        "gate_assessment": gate_assessment,
    }
    write_json(output_dir / "summary.json", summary)
    write_jsonl(output_dir / "outputs.jsonl", output_rows)
    write_jsonl(output_dir / "pairwise_judgments.jsonl", judgment_rows)
    write_gate_readme(output_dir / "README.md", summary)
    return summary


def main() -> int:
    args = parse_args()
    device = select_device(args.device)
    prompt_rows = load_prompt_rows(args.split_path, max_pairs=args.max_pairs)
    gate_prompt_rows = prompt_rows[: args.max_prompts]
    templates = load_templates(args.templates_path)
    judge_templates = load_judge_templates(args.judge_templates_path)
    steering_coeffs = parse_steering_coeffs_argument(args.steering_coeffs)
    candidate_layers = load_available_layers_for_release(args.sae_release)
    reference_sae_summary = load_reference_sae_summary(args.sae_release, args.reference_sae_id)

    model, tokenizer = load_model_and_tokenizer(args.model_id, device)
    sweep_output_dir = args.sweep_output_dir or default_sweep_output_dir()
    gate_output_dir = args.gate_output_dir or default_gate_output_dir()

    sweep_summary, best_direction = run_layer_sweep(
        model=model,
        tokenizer=tokenizer,
        prompt_rows=prompt_rows,
        candidate_layers=candidate_layers,
        batch_size=args.batch_size,
        model_id=args.model_id,
        device=device,
        sae_release=args.sae_release,
        reference_sae_summary=reference_sae_summary,
        output_dir=sweep_output_dir,
        overwrite=args.overwrite,
    )
    gate_summary = run_output_gate(
        model=model,
        tokenizer=tokenizer,
        prompt_rows=gate_prompt_rows,
        templates=templates,
        judge_templates=judge_templates,
        hidden_layer=int(sweep_summary["best_layer"]),
        direction=best_direction,
        steering_coeffs=steering_coeffs,
        max_new_tokens=args.max_new_tokens,
        judge_max_new_tokens=args.judge_max_new_tokens,
        seed=args.seed,
        model_id=args.model_id,
        device=device,
        sae_release=args.sae_release,
        output_dir=gate_output_dir,
        overwrite=args.overwrite,
    )

    print(f"wrote instruction-tuned refusal sweep to {sweep_output_dir}")
    print(f"wrote instruction-tuned refusal gate to {gate_output_dir}")
    print(
        "best dense refusal net preference vs neutral: "
        f"{gate_summary['gate_assessment']['best_dense_vs_neutral']['refusal_candidate_net_preference']:.6f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
