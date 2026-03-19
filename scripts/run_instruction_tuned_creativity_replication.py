# ABOUTME: Runs the bounded instruction-tuned creativity replication on the matched Gemma 3 270M IT plus GemmaScope v2 stack.
# ABOUTME: Materializes counterpart-style creativity pairs, freezes the best mean-difference layer on that stack, and runs a hardened output gate without reopening decomposition.

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import sys
from typing import Any

import numpy as np
from repeng import DatasetEntry
from repeng.extract import batched_get_hiddens


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from materialize_instruction_tuned_creativity_response_pairs_v1 import (  # noqa: E402
    DEFAULT_METADATA_PATH,
    DEFAULT_MODEL_ID,
    DEFAULT_PAIR_PATH,
    DEFAULT_REJECTED_PAIR_PATH,
    DEFAULT_SOURCE_SPLIT_PATH,
    DEFAULT_TEMPLATES_PATH,
    DEFAULT_MAX_NEGATIVE_PROMPT_GROUNDING_DELTA,
    DEFAULT_MIN_COUNTERPART_OVERLAP,
    load_templates as load_pair_templates,
    run_pair_materialization,
)
from probe_base_model_story_prompts import compute_meta_marker_score  # noqa: E402
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
    load_judge_templates,
    map_judge_winner_to_condition_id,
    parse_label_judgment_or_tie,
    render_pairwise_judge_prompt,
    resolve_order_robust_winner,
    summarize_condition_outputs,
    summarize_gate_assessment,
    summarize_pairwise_judgments,
    validate_generated_outputs,
)
from run_generation_side_creativity_smoke import (  # noqa: E402
    generate_completion,
    generate_with_control,
    path_for_summary,
    prepare_output_dir,
)
from run_instruction_tuned_refusal_pivot import (  # noqa: E402
    compute_repeated_bigram_fraction,
    generate_judge_response_chat,
    load_available_layers_for_release,
    load_reference_sae_summary,
    render_chat_transcript,
)


DEFAULT_SAE_RELEASE = "gemma-scope-2-270m-it-res"
DEFAULT_REFERENCE_SAE_ID = "layer_12_width_16k_l0_medium"
DEFAULT_JUDGE_TEMPLATES_PATH = ROOT / "prompts" / "creative_direction_output_gate_v2_judges.json"
DEFAULT_MAX_PROMPTS = 12
DEFAULT_MAX_NEW_TOKENS = 96
DEFAULT_JUDGE_MAX_NEW_TOKENS = 6
DEFAULT_STEERING_COEFFS = "0.5,1.0"
DEFAULT_SEED = 9300


def default_pair_output_dir() -> Path:
    run_date = datetime.now().strftime("%Y%m%d")
    return ROOT / "results" / "creativity_direction" / f"{run_date}-gemma3-270m-it-response-pairs-v1-pilot"


def default_sweep_output_dir() -> Path:
    run_date = datetime.now().strftime("%Y%m%d")
    return ROOT / "results" / "creativity_direction" / f"{run_date}-gemma3-270m-it-layer-sweep-v1-mean-difference"


def default_gate_output_dir() -> Path:
    run_date = datetime.now().strftime("%Y%m%d")
    return ROOT / "results" / "steering_eval" / f"{run_date}-gemma3-270m-it-output-gate-v1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the bounded instruction-tuned creativity replication on the matched Gemma 3 270M IT stack."
    )
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID)
    parser.add_argument("--sae-release", default=DEFAULT_SAE_RELEASE)
    parser.add_argument("--reference-sae-id", default=DEFAULT_REFERENCE_SAE_ID)
    parser.add_argument("--source-split-path", type=Path, default=DEFAULT_SOURCE_SPLIT_PATH)
    parser.add_argument("--pair-path", type=Path, default=DEFAULT_PAIR_PATH)
    parser.add_argument("--rejected-pair-path", type=Path, default=DEFAULT_REJECTED_PAIR_PATH)
    parser.add_argument("--metadata-path", type=Path, default=DEFAULT_METADATA_PATH)
    parser.add_argument("--templates-path", type=Path, default=DEFAULT_TEMPLATES_PATH)
    parser.add_argument("--judge-templates-path", type=Path, default=DEFAULT_JUDGE_TEMPLATES_PATH)
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--max-pairs", type=int, default=32)
    parser.add_argument("--max-prompts", type=int, default=DEFAULT_MAX_PROMPTS)
    parser.add_argument("--max-new-tokens", type=int, default=DEFAULT_MAX_NEW_TOKENS)
    parser.add_argument("--judge-max-new-tokens", type=int, default=DEFAULT_JUDGE_MAX_NEW_TOKENS)
    parser.add_argument("--steering-coeffs", default=DEFAULT_STEERING_COEFFS)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--min-counterpart-overlap", type=float, default=DEFAULT_MIN_COUNTERPART_OVERLAP)
    parser.add_argument(
        "--max-negative-prompt-grounding-delta",
        type=float,
        default=DEFAULT_MAX_NEGATIVE_PROMPT_GROUNDING_DELTA,
    )
    parser.add_argument("--device", choices=["auto", "mps", "cpu"], default="auto")
    parser.add_argument("--pair-output-dir", type=Path, default=None)
    parser.add_argument("--sweep-output-dir", type=Path, default=None)
    parser.add_argument("--gate-output-dir", type=Path, default=None)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def build_generation_messages(
    prompt_text: str,
    prompt_mode: str,
    templates: dict[str, str],
) -> list[dict[str, str]]:
    if prompt_mode == "neutral":
        return [
            {
                "role": "user",
                "content": templates["neutral_story_user_prompt"].format(prompt=prompt_text),
            }
        ]
    if prompt_mode == "prompt_only_creativity":
        return [
            {
                "role": "user",
                "content": templates["prompt_only_creativity_user_prompt"].format(prompt=prompt_text),
            }
        ]
    raise ValueError(f"unknown prompt mode: {prompt_mode}")


def build_contrastive_dataset(
    prompt_rows: list[dict[str, Any]],
    tokenizer,
    templates: dict[str, str],
) -> list[DatasetEntry]:
    dataset: list[DatasetEntry] = []
    for row in prompt_rows:
        prompt_text = templates["neutral_story_user_prompt"].format(prompt=str(row["prompt_text"]))
        positive = render_chat_transcript(
            tokenizer,
            [
                {"role": "user", "content": prompt_text},
                {"role": "assistant", "content": str(row["positive_assistant_text"])},
            ],
            add_generation_prompt=False,
        )
        negative = render_chat_transcript(
            tokenizer,
            [
                {"role": "user", "content": prompt_text},
                {"role": "assistant", "content": str(row["negative_assistant_text"])},
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
            "condition_id": "creative_prompt_unsteered",
            "prompt_mode": "prompt_only_creativity",
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


def build_pairwise_comparisons(dense_condition_ids: list[str]) -> list[dict[str, str]]:
    comparisons: list[dict[str, str]] = [
        {
            "comparison_id": "creative_prompt_unsteered_vs_neutral_unsteered",
            "candidate_condition_id": "creative_prompt_unsteered",
            "reference_condition_id": "neutral_unsteered",
        }
    ]
    for condition_id in dense_condition_ids:
        comparisons.append(
            {
                "comparison_id": f"{condition_id}_vs_neutral_unsteered",
                "candidate_condition_id": condition_id,
                "reference_condition_id": "neutral_unsteered",
            }
        )
    for condition_id in dense_condition_ids:
        comparisons.append(
            {
                "comparison_id": f"{condition_id}_vs_creative_prompt_unsteered",
                "candidate_condition_id": condition_id,
                "reference_condition_id": "creative_prompt_unsteered",
            }
        )
    return comparisons


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
        "direction_method": "mean_difference",
    }
    return row, direction, summary["pair_details"]


def write_sweep_readme(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Instruction-Tuned Creativity Layer Sweep",
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
        "# Instruction-Tuned Creativity Output Gate",
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
        f"- Neutral story prompt: `{summary['templates']['neutral_story_user_prompt']}`",
        f"- Creativity baseline prompt: `{summary['templates']['prompt_only_creativity_user_prompt']}`",
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
            f"- `{row['comparison_id']}`: creativity candidate win `{row['creativity_candidate_win_fraction']:.3f}`, "
            f"creativity reference win `{row['creativity_reference_win_fraction']:.3f}`, "
            f"coherence candidate win `{row['coherence_candidate_win_fraction']:.3f}`, "
            f"coherence reference win `{row['coherence_reference_win_fraction']:.3f}`"
        )
    lines.extend(
        [
            "",
            "Artifacts:",
            "- `summary.json`",
            "- `generated_outputs.jsonl`",
            "- `pairwise_judgments.jsonl`",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_layer_sweep(
    *,
    model,
    tokenizer,
    prompt_rows: list[dict[str, Any]],
    templates: dict[str, str],
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
    dataset = build_contrastive_dataset(prompt_rows, tokenizer, templates)
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
        "direction_method": "mean_difference",
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
    judge_templates_path: Path,
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
                    "seed": sample_seed,
                    "rendered_prompt_text": rendered_prompt,
                    "completion_text": completion_text,
                    "full_text": full_text,
                    "completion_word_count": len(completion_text.split()),
                    "completion_char_count": len(completion_text),
                    "meta_marker_score": compute_meta_marker_score(completion_text),
                    "distinct_unigram_ratio": compute_distinct_unigram_ratio(completion_text),
                    "repeated_bigram_fraction": compute_repeated_bigram_fraction(completion_text),
                }
            )

    validate_generated_outputs(output_rows, prompt_rows[: len(prompt_rows)], conditions)
    condition_lookup = build_condition_lookup(output_rows)
    dense_condition_ids = [
        str(condition["condition_id"])
        for condition in conditions
        if condition["hidden_layer"] is not None
    ]
    comparisons = build_pairwise_comparisons(dense_condition_ids)
    judgment_rows: list[dict[str, Any]] = []
    for comparison in comparisons:
        candidate_condition_id = comparison["candidate_condition_id"]
        reference_condition_id = comparison["reference_condition_id"]
        for prompt_row in prompt_rows:
            prompt_id = str(prompt_row["prompt_id"])
            candidate_row = condition_lookup[(prompt_id, candidate_condition_id)]
            reference_row = condition_lookup[(prompt_id, reference_condition_id)]

            creativity_forward_prompt = render_pairwise_judge_prompt(
                prompt_text=str(prompt_row["prompt_text"]),
                story_a=str(candidate_row["completion_text"]),
                story_b=str(reference_row["completion_text"]),
                judge_template=judge_templates["pairwise_creativity_label_judge"],
            )
            creativity_reverse_prompt = render_pairwise_judge_prompt(
                prompt_text=str(prompt_row["prompt_text"]),
                story_a=str(reference_row["completion_text"]),
                story_b=str(candidate_row["completion_text"]),
                judge_template=judge_templates["pairwise_creativity_label_judge"],
            )
            coherence_forward_prompt = render_pairwise_judge_prompt(
                prompt_text=str(prompt_row["prompt_text"]),
                story_a=str(candidate_row["completion_text"]),
                story_b=str(reference_row["completion_text"]),
                judge_template=judge_templates["pairwise_coherence_label_judge"],
            )
            coherence_reverse_prompt = render_pairwise_judge_prompt(
                prompt_text=str(prompt_row["prompt_text"]),
                story_a=str(reference_row["completion_text"]),
                story_b=str(candidate_row["completion_text"]),
                judge_template=judge_templates["pairwise_coherence_label_judge"],
            )

            creativity_forward_raw = generate_judge_response_chat(
                model,
                tokenizer,
                creativity_forward_prompt,
                judge_max_new_tokens,
            )
            creativity_reverse_raw = generate_judge_response_chat(
                model,
                tokenizer,
                creativity_reverse_prompt,
                judge_max_new_tokens,
            )
            coherence_forward_raw = generate_judge_response_chat(
                model,
                tokenizer,
                coherence_forward_prompt,
                judge_max_new_tokens,
            )
            coherence_reverse_raw = generate_judge_response_chat(
                model,
                tokenizer,
                coherence_reverse_prompt,
                judge_max_new_tokens,
            )

            creativity_forward_label = parse_label_judgment_or_tie(creativity_forward_raw)
            creativity_reverse_label = parse_label_judgment_or_tie(creativity_reverse_raw)
            coherence_forward_label = parse_label_judgment_or_tie(coherence_forward_raw)
            coherence_reverse_label = parse_label_judgment_or_tie(coherence_reverse_raw)

            creativity_forward_winner = map_judge_winner_to_condition_id(
                creativity_forward_label,
                candidate_condition_id,
                reference_condition_id,
            )
            creativity_reverse_winner = map_judge_winner_to_condition_id(
                creativity_reverse_label,
                reference_condition_id,
                candidate_condition_id,
            )
            coherence_forward_winner = map_judge_winner_to_condition_id(
                coherence_forward_label,
                candidate_condition_id,
                reference_condition_id,
            )
            coherence_reverse_winner = map_judge_winner_to_condition_id(
                coherence_reverse_label,
                reference_condition_id,
                candidate_condition_id,
            )

            judgment_rows.append(
                {
                    "comparison_id": comparison["comparison_id"],
                    "prompt_id": prompt_id,
                    "creativity_forward_raw": creativity_forward_raw,
                    "creativity_reverse_raw": creativity_reverse_raw,
                    "coherence_forward_raw": coherence_forward_raw,
                    "coherence_reverse_raw": coherence_reverse_raw,
                    "creativity_winner_condition_id": resolve_order_robust_winner(
                        creativity_forward_winner,
                        creativity_reverse_winner,
                    ),
                    "coherence_winner_condition_id": resolve_order_robust_winner(
                        coherence_forward_winner,
                        coherence_reverse_winner,
                    ),
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
        "judge_templates_path": path_for_summary(judge_templates_path),
        "condition_summaries": summarize_condition_outputs(output_rows),
        "comparison_summaries": comparison_summaries,
        "gate_assessment": gate_assessment,
        "reused_generated_outputs": False,
        "artifacts": {
            "generated_outputs_jsonl": path_for_summary(output_dir / "generated_outputs.jsonl"),
            "pairwise_judgments_jsonl": path_for_summary(output_dir / "pairwise_judgments.jsonl"),
        },
    }
    write_json(output_dir / "summary.json", summary)
    write_jsonl(output_dir / "generated_outputs.jsonl", output_rows)
    write_jsonl(output_dir / "pairwise_judgments.jsonl", judgment_rows)
    write_gate_readme(output_dir / "README.md", summary)
    return summary


def main() -> int:
    args = parse_args()
    pair_output_dir = args.pair_output_dir or default_pair_output_dir()
    sweep_output_dir = args.sweep_output_dir or default_sweep_output_dir()
    gate_output_dir = args.gate_output_dir or default_gate_output_dir()

    source_prompt_rows = load_prompt_rows(args.source_split_path, max_pairs=args.max_pairs)
    templates = load_pair_templates(args.templates_path)
    judge_templates = load_judge_templates(args.judge_templates_path)
    steering_coeffs = parse_steering_coeffs_argument(args.steering_coeffs)

    device = select_device(args.device)
    model, tokenizer = load_model_and_tokenizer(args.model_id, device)

    _, pair_rows = run_pair_materialization(
        model=model,
        tokenizer=tokenizer,
        model_id=args.model_id,
        prompt_rows=source_prompt_rows,
        templates=templates,
        source_split_path=args.source_split_path,
        templates_path=args.templates_path,
        pair_path=args.pair_path,
        rejected_pair_path=args.rejected_pair_path,
        metadata_path=args.metadata_path,
        output_dir=pair_output_dir,
        max_new_tokens=args.max_new_tokens,
        seed=args.seed,
        min_counterpart_overlap=args.min_counterpart_overlap,
        max_negative_prompt_grounding_delta=args.max_negative_prompt_grounding_delta,
        device=device,
        overwrite=args.overwrite,
    )

    candidate_layers = load_available_layers_for_release(args.sae_release)
    reference_sae_summary = load_reference_sae_summary(args.sae_release, args.reference_sae_id)
    sweep_summary, direction = run_layer_sweep(
        model=model,
        tokenizer=tokenizer,
        prompt_rows=pair_rows,
        templates=templates,
        candidate_layers=candidate_layers,
        batch_size=args.batch_size,
        model_id=args.model_id,
        device=device,
        sae_release=args.sae_release,
        reference_sae_summary=reference_sae_summary,
        output_dir=sweep_output_dir,
        overwrite=args.overwrite,
    )
    gate_prompt_rows = pair_rows[: min(args.max_prompts, len(pair_rows))]
    run_output_gate(
        model=model,
        tokenizer=tokenizer,
        prompt_rows=gate_prompt_rows,
        templates=templates,
        judge_templates_path=args.judge_templates_path,
        judge_templates=judge_templates,
        hidden_layer=int(sweep_summary["best_layer"]),
        direction=direction,
        steering_coeffs=steering_coeffs,
        max_new_tokens=args.max_new_tokens,
        judge_max_new_tokens=args.judge_max_new_tokens,
        seed=args.seed + 1000,
        model_id=args.model_id,
        device=device,
        sae_release=args.sae_release,
        output_dir=gate_output_dir,
        overwrite=args.overwrite,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
