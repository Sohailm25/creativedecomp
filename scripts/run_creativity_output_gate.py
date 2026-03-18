# ABOUTME: Runs the pilot output-level gate for the recovered dense creativity direction before decomposition opens.
# ABOUTME: Compares dense steering against neutral and prompt-only baselines with locked pairwise creativity and coherence judgments.

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
import torch


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from probe_base_model_story_prompts import compute_meta_marker_score  # noqa: E402
from run_creativity_direction_calibration import (  # noqa: E402
    compute_distinct_unigram_ratio,
    format_coeff_slug,
    parse_steering_coeffs_argument,
)
from run_creativity_direction_smoke import (  # noqa: E402
    ROOT,
    DEFAULT_MODEL_ID,
    load_model_and_tokenizer,
    load_prompt_rows,
    load_templates,
    select_device,
    write_json,
    write_jsonl,
)
from run_generation_side_creativity_smoke import (  # noqa: E402
    build_prompt_text,
    generate_completion,
    generate_with_control,
    load_directions,
    load_ranked_layer_rows,
    path_for_summary,
    prepare_output_dir,
)


DEFAULT_SPLIT_PATH = ROOT / "prompts" / "creative_direction_v3_pilot_pairs.jsonl"
DEFAULT_TEMPLATES_PATH = ROOT / "prompts" / "creative_direction_v3_templates.json"
DEFAULT_JUDGE_TEMPLATES_PATH = ROOT / "prompts" / "creative_direction_output_gate_v1_judges.json"
DEFAULT_SWEEP_DIR = (
    ROOT
    / "results"
    / "creativity_direction"
    / "20260318-gemma2-2b-layer-sweep-response-pairs-v3-mean-difference"
)
DEFAULT_MAX_PROMPTS = 31
DEFAULT_MAX_NEW_TOKENS = 96
DEFAULT_JUDGE_MAX_NEW_TOKENS = 6
DEFAULT_STEERING_COEFFS = "0.5,1.0"
DEFAULT_SEED = 4100


def default_output_dir() -> Path:
    run_date = datetime.now().strftime("%Y%m%d")
    return ROOT / "results" / "steering_eval" / f"{run_date}-gemma2-2b-output-gate-v1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the pilot output-level gate for the recovered creativity direction."
    )
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID)
    parser.add_argument("--split-path", type=Path, default=DEFAULT_SPLIT_PATH)
    parser.add_argument("--templates-path", type=Path, default=DEFAULT_TEMPLATES_PATH)
    parser.add_argument("--judge-templates-path", type=Path, default=DEFAULT_JUDGE_TEMPLATES_PATH)
    parser.add_argument("--sweep-dir", type=Path, default=DEFAULT_SWEEP_DIR)
    parser.add_argument("--hidden-layer", type=int, default=None)
    parser.add_argument("--max-prompts", type=int, default=DEFAULT_MAX_PROMPTS)
    parser.add_argument("--max-new-tokens", type=int, default=DEFAULT_MAX_NEW_TOKENS)
    parser.add_argument("--judge-max-new-tokens", type=int, default=DEFAULT_JUDGE_MAX_NEW_TOKENS)
    parser.add_argument("--steering-coeffs", default=DEFAULT_STEERING_COEFFS)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--device", choices=["auto", "mps", "cpu"], default="auto")
    parser.add_argument("--generated-outputs-path", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def load_judge_templates(path: Path) -> dict[str, str]:
    templates = json.loads(path.read_text(encoding="utf-8"))
    for key in ("pairwise_creativity_label_judge", "pairwise_coherence_label_judge"):
        if key not in templates:
            raise KeyError(f"missing template key: {key}")
    return templates


def select_primary_layer(ranked_rows: list[dict[str, Any]]) -> int:
    if not ranked_rows:
        raise ValueError("need at least one ranked layer row")
    return int(ranked_rows[0]["hidden_layer"])


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


def render_pairwise_judge_prompt(
    prompt_text: str,
    story_a: str,
    story_b: str,
    judge_template: str,
) -> str:
    return judge_template.format(
        prompt=prompt_text,
        story_a=story_a,
        story_b=story_b,
    )


def parse_label_judgment(raw_text: str) -> str:
    normalized = str(raw_text).strip().lower()
    if normalized in {"a", "b", "tie"}:
        return normalized.upper() if normalized in {"a", "b"} else "tie"

    tokens = re.findall(r"[A-Za-z]+", normalized)
    for token in reversed(tokens):
        if token == "a":
            return "A"
        if token == "b":
            return "B"
        if token == "tie":
            return "tie"
    raise ValueError(f"could not parse label judgment from response: {raw_text!r}")


def compute_repeated_bigram_fraction(text: str) -> float:
    tokens = [token for token in text.lower().split() if token]
    if len(tokens) < 2:
        return 0.0
    bigrams = list(zip(tokens[:-1], tokens[1:]))
    counts = Counter(bigrams)
    repeated_bigram_count = sum(count - 1 for count in counts.values() if count > 1)
    return float(repeated_bigram_count / len(bigrams))


def generate_judge_response(
    model,
    tokenizer,
    prompt_text: str,
    max_new_tokens: int,
) -> str:
    encoded = tokenizer(prompt_text, return_tensors="pt")
    encoded = {key: value.to(model.device) for key, value in encoded.items()}
    output_ids = model.generate(
        **encoded,
        do_sample=False,
        max_new_tokens=max_new_tokens,
        pad_token_id=tokenizer.pad_token_id,
        eos_token_id=tokenizer.eos_token_id,
    )[0]
    prompt_length = int(encoded["input_ids"].shape[1])
    completion_ids = output_ids[prompt_length:]
    return tokenizer.decode(completion_ids, skip_special_tokens=True).strip()


def load_jsonl_rows(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def build_condition_lookup(rows: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    return {
        (str(row["prompt_id"]), str(row["condition_id"])): row
        for row in rows
    }


def map_judge_winner_to_condition_id(
    winner_label: str,
    story_a_condition_id: str,
    story_b_condition_id: str,
) -> str:
    if winner_label == "A":
        return story_a_condition_id
    if winner_label == "B":
        return story_b_condition_id
    return "tie"


def resolve_order_robust_winner(
    forward_winner_condition_id: str,
    reverse_winner_condition_id: str,
) -> str:
    if forward_winner_condition_id == reverse_winner_condition_id:
        return forward_winner_condition_id
    return "tie"


def validate_generated_outputs(
    output_rows: list[dict[str, Any]],
    prompt_rows: list[dict[str, Any]],
    conditions: list[dict[str, Any]],
) -> None:
    expected_keys = {
        (str(prompt_row["prompt_id"]), str(condition["condition_id"]))
        for prompt_row in prompt_rows
        for condition in conditions
    }
    actual_keys = {
        (str(row["prompt_id"]), str(row["condition_id"]))
        for row in output_rows
    }
    missing_keys = expected_keys - actual_keys
    unexpected_keys = actual_keys - expected_keys
    if missing_keys or unexpected_keys:
        raise ValueError(
            "generated outputs do not match the requested prompt/condition grid: "
            f"missing={len(missing_keys)} unexpected={len(unexpected_keys)}"
        )


def summarize_condition_outputs(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(str(row["condition_id"]), []).append(row)

    summaries: list[dict[str, Any]] = []
    for condition_id, condition_rows in grouped.items():
        word_counts = [int(row["completion_word_count"]) for row in condition_rows]
        char_counts = [int(row["completion_char_count"]) for row in condition_rows]
        meta_scores = [int(row["meta_marker_score"]) for row in condition_rows]
        distinct_ratios = [float(row["distinct_unigram_ratio"]) for row in condition_rows]
        repeated_bigram_fractions = [
            float(row["repeated_bigram_fraction"]) for row in condition_rows
        ]
        summaries.append(
            {
                "condition_id": condition_id,
                "sample_count": len(condition_rows),
                "mean_completion_word_count": float(np.mean(word_counts)),
                "mean_completion_char_count": float(np.mean(char_counts)),
                "meta_marker_fraction": float(np.mean([score > 0 for score in meta_scores])),
                "mean_meta_marker_score": float(np.mean(meta_scores)),
                "mean_distinct_unigram_ratio": float(np.mean(distinct_ratios)),
                "mean_repeated_bigram_fraction": float(np.mean(repeated_bigram_fractions)),
            }
        )
    return sorted(summaries, key=lambda row: row["condition_id"])


def summarize_pairwise_judgments(
    judgment_rows: list[dict[str, Any]],
    comparisons: list[dict[str, str]],
) -> list[dict[str, Any]]:
    rows_by_comparison: dict[str, list[dict[str, Any]]] = {}
    for row in judgment_rows:
        rows_by_comparison.setdefault(str(row["comparison_id"]), []).append(row)

    summaries: list[dict[str, Any]] = []
    for comparison in comparisons:
        comparison_id = comparison["comparison_id"]
        comparison_rows = rows_by_comparison.get(comparison_id, [])
        if not comparison_rows:
            continue

        candidate_condition_id = comparison["candidate_condition_id"]
        reference_condition_id = comparison["reference_condition_id"]
        sample_count = len(comparison_rows)

        def fraction_for(axis: str, winner: str) -> float:
            key = f"{axis}_winner_condition_id"
            return float(np.mean([str(row[key]) == winner for row in comparison_rows]))

        creativity_candidate_win_fraction = fraction_for("creativity", candidate_condition_id)
        creativity_reference_win_fraction = fraction_for("creativity", reference_condition_id)
        coherence_candidate_win_fraction = fraction_for("coherence", candidate_condition_id)
        coherence_reference_win_fraction = fraction_for("coherence", reference_condition_id)

        summaries.append(
            {
                "comparison_id": comparison_id,
                "candidate_condition_id": candidate_condition_id,
                "reference_condition_id": reference_condition_id,
                "sample_count": sample_count,
                "creativity_candidate_win_fraction": creativity_candidate_win_fraction,
                "creativity_reference_win_fraction": creativity_reference_win_fraction,
                "creativity_tie_fraction": fraction_for("creativity", "tie"),
                "creativity_candidate_net_preference": (
                    creativity_candidate_win_fraction - creativity_reference_win_fraction
                ),
                "coherence_candidate_win_fraction": coherence_candidate_win_fraction,
                "coherence_reference_win_fraction": coherence_reference_win_fraction,
                "coherence_tie_fraction": fraction_for("coherence", "tie"),
                "coherence_candidate_net_preference": (
                    coherence_candidate_win_fraction - coherence_reference_win_fraction
                ),
            }
        )
    return summaries


def summarize_gate_assessment(comparison_summaries: list[dict[str, Any]]) -> dict[str, Any]:
    dense_vs_neutral = [
        row
        for row in comparison_summaries
        if str(row["candidate_condition_id"]).startswith("neutral_steered_")
        and str(row["reference_condition_id"]) == "neutral_unsteered"
    ]
    if not dense_vs_neutral:
        raise ValueError("no dense-vs-neutral comparison summaries found")

    best_dense_vs_neutral = max(
        dense_vs_neutral,
        key=lambda row: (
            float(row["creativity_candidate_net_preference"]),
            float(row["coherence_candidate_net_preference"]),
        ),
    )
    prompt_vs_neutral = next(
        row
        for row in comparison_summaries
        if str(row["comparison_id"]) == "creative_prompt_unsteered_vs_neutral_unsteered"
    )
    dense_vs_prompt = next(
        (
            row
            for row in comparison_summaries
            if row["candidate_condition_id"] == best_dense_vs_neutral["candidate_condition_id"]
            and row["reference_condition_id"] == "creative_prompt_unsteered"
        ),
        None,
    )
    return {
        "best_dense_condition_id": best_dense_vs_neutral["candidate_condition_id"],
        "best_dense_vs_neutral": best_dense_vs_neutral,
        "prompt_vs_neutral": prompt_vs_neutral,
        "best_dense_vs_prompt_baseline": dense_vs_prompt,
        "automatic_pass_recommendation": bool(
            float(best_dense_vs_neutral["creativity_candidate_net_preference"]) > 0.0
            and float(best_dense_vs_neutral["coherence_candidate_net_preference"]) >= 0.0
        ),
        "automatic_pass_rule": (
            "best dense condition has positive creativity net preference versus neutral "
            "and non-negative coherence net preference versus neutral"
        ),
    }


def write_readme(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Creativity Output Gate",
        "",
        f"- Generated at: `{summary['created_at']}`",
        f"- Model: `{summary['model_id']}`",
        f"- Device: `{summary['device']}`",
        f"- Prompt count: `{summary['prompt_count']}`",
        f"- Primary hidden layer: `{summary['hidden_layer']}`",
        f"- Steering coefficients: `{summary['steering_coeffs']}`",
        f"- Max new tokens: `{summary['max_new_tokens']}`",
        f"- Judge max new tokens: `{summary['judge_max_new_tokens']}`",
        f"- Seed base: `{summary['seed']}`",
        f"- Judge template path: `{summary['judge_templates_path']}`",
        f"- Reused generated outputs: `{summary['reused_generated_outputs']}`",
        "- Order-robust judging: `True` (winner must agree under both A/B orders or the result becomes `tie`)",
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
    lines.extend(
        [
            "",
            "Pairwise judgment summaries:",
        ]
    )
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


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir or default_output_dir()
    prepare_output_dir(output_dir, overwrite=args.overwrite)

    prompt_rows = load_prompt_rows(args.split_path, max_pairs=args.max_prompts)
    templates = load_templates(args.templates_path)
    judge_templates = load_judge_templates(args.judge_templates_path)
    ranked_rows = load_ranked_layer_rows(args.sweep_dir / "layer_metrics.jsonl")
    hidden_layer = args.hidden_layer if args.hidden_layer is not None else select_primary_layer(ranked_rows)
    steering_coeffs = parse_steering_coeffs_argument(args.steering_coeffs)
    directions = load_directions(args.sweep_dir / "directions.npz", [hidden_layer])
    direction = directions[hidden_layer]

    conditions = build_output_gate_conditions(hidden_layer=hidden_layer, steering_coeffs=steering_coeffs)
    dense_condition_ids = [
        str(condition["condition_id"])
        for condition in conditions
        if condition["hidden_layer"] is not None
    ]
    comparisons = build_pairwise_comparisons(dense_condition_ids=dense_condition_ids)

    generated_outputs_path = args.generated_outputs_path or (output_dir / "generated_outputs.jsonl")
    reused_generated_outputs = generated_outputs_path.exists()
    device = select_device(args.device)
    model, tokenizer = load_model_and_tokenizer(args.model_id, device)

    if reused_generated_outputs:
        output_rows = load_jsonl_rows(generated_outputs_path)
    else:
        output_rows = []
        for prompt_index, prompt_row in enumerate(prompt_rows):
            for condition_index, condition in enumerate(conditions):
                prompt_text_full = build_prompt_text(
                    prompt_text=str(prompt_row["prompt_text"]),
                    prompt_mode=str(condition["prompt_mode"]),
                    templates=templates,
                )
                seed = args.seed + (prompt_index * 100) + condition_index
                hidden_layer_value = condition["hidden_layer"]
                if hidden_layer_value is None:
                    completion_text, full_text = generate_completion(
                        model,
                        tokenizer,
                        prompt_text=prompt_text_full,
                        seed=seed,
                        max_new_tokens=args.max_new_tokens,
                    )
                else:
                    completion_text, full_text = generate_with_control(
                        model,
                        tokenizer,
                        prompt_text=prompt_text_full,
                        hidden_layer=int(hidden_layer_value),
                        direction=direction,
                        steering_coeff=float(condition["steering_coeff"]),
                        seed=seed,
                        max_new_tokens=args.max_new_tokens,
                        normalize_control=bool(condition["normalize_control"]),
                    )

                output_rows.append(
                    {
                        "prompt_id": prompt_row["prompt_id"],
                        "prompt_text": prompt_row["prompt_text"],
                        "condition_id": condition["condition_id"],
                        "prompt_mode": condition["prompt_mode"],
                        "hidden_layer": hidden_layer_value,
                        "steering_coeff": condition["steering_coeff"],
                        "seed": seed,
                        "prompt_text_full": prompt_text_full,
                        "completion_text": completion_text,
                        "full_text": full_text,
                        "completion_char_count": len(completion_text),
                        "completion_word_count": len(completion_text.split()),
                        "meta_marker_score": compute_meta_marker_score(completion_text),
                        "distinct_unigram_ratio": compute_distinct_unigram_ratio(completion_text),
                        "repeated_bigram_fraction": compute_repeated_bigram_fraction(completion_text),
                    }
                )

    validate_generated_outputs(output_rows, prompt_rows=prompt_rows, conditions=conditions)

    condition_lookup = build_condition_lookup(output_rows)
    judgment_rows: list[dict[str, Any]] = []
    for prompt_row in prompt_rows:
        prompt_id = str(prompt_row["prompt_id"])
        for comparison in comparisons:
            candidate_row = condition_lookup[(prompt_id, comparison["candidate_condition_id"])]
            reference_row = condition_lookup[(prompt_id, comparison["reference_condition_id"])]

            creativity_forward_prompt = render_pairwise_judge_prompt(
                prompt_text=str(prompt_row["prompt_text"]),
                story_a=str(candidate_row["completion_text"]),
                story_b=str(reference_row["completion_text"]),
                judge_template=judge_templates["pairwise_creativity_label_judge"],
            )
            creativity_forward_raw = generate_judge_response(
                model,
                tokenizer,
                prompt_text=creativity_forward_prompt,
                max_new_tokens=args.judge_max_new_tokens,
            )
            creativity_reverse_prompt = render_pairwise_judge_prompt(
                prompt_text=str(prompt_row["prompt_text"]),
                story_a=str(reference_row["completion_text"]),
                story_b=str(candidate_row["completion_text"]),
                judge_template=judge_templates["pairwise_creativity_label_judge"],
            )
            creativity_reverse_raw = generate_judge_response(
                model,
                tokenizer,
                prompt_text=creativity_reverse_prompt,
                max_new_tokens=args.judge_max_new_tokens,
            )
            coherence_forward_prompt = render_pairwise_judge_prompt(
                prompt_text=str(prompt_row["prompt_text"]),
                story_a=str(candidate_row["completion_text"]),
                story_b=str(reference_row["completion_text"]),
                judge_template=judge_templates["pairwise_coherence_label_judge"],
            )
            coherence_forward_raw = generate_judge_response(
                model,
                tokenizer,
                prompt_text=coherence_forward_prompt,
                max_new_tokens=args.judge_max_new_tokens,
            )
            coherence_reverse_prompt = render_pairwise_judge_prompt(
                prompt_text=str(prompt_row["prompt_text"]),
                story_a=str(reference_row["completion_text"]),
                story_b=str(candidate_row["completion_text"]),
                judge_template=judge_templates["pairwise_coherence_label_judge"],
            )
            coherence_reverse_raw = generate_judge_response(
                model,
                tokenizer,
                prompt_text=coherence_reverse_prompt,
                max_new_tokens=args.judge_max_new_tokens,
            )

            creativity_forward_label = parse_label_judgment(creativity_forward_raw)
            creativity_reverse_label = parse_label_judgment(creativity_reverse_raw)
            coherence_forward_label = parse_label_judgment(coherence_forward_raw)
            coherence_reverse_label = parse_label_judgment(coherence_reverse_raw)

            candidate_condition_id = str(candidate_row["condition_id"])
            reference_condition_id = str(reference_row["condition_id"])
            creativity_forward_winner_condition_id = map_judge_winner_to_condition_id(
                creativity_forward_label,
                story_a_condition_id=candidate_condition_id,
                story_b_condition_id=reference_condition_id,
            )
            creativity_reverse_winner_condition_id = map_judge_winner_to_condition_id(
                creativity_reverse_label,
                story_a_condition_id=reference_condition_id,
                story_b_condition_id=candidate_condition_id,
            )
            coherence_forward_winner_condition_id = map_judge_winner_to_condition_id(
                coherence_forward_label,
                story_a_condition_id=candidate_condition_id,
                story_b_condition_id=reference_condition_id,
            )
            coherence_reverse_winner_condition_id = map_judge_winner_to_condition_id(
                coherence_reverse_label,
                story_a_condition_id=reference_condition_id,
                story_b_condition_id=candidate_condition_id,
            )

            judgment_rows.append(
                {
                    "prompt_id": prompt_id,
                    "prompt_text": prompt_row["prompt_text"],
                    "comparison_id": comparison["comparison_id"],
                    "candidate_condition_id": comparison["candidate_condition_id"],
                    "reference_condition_id": comparison["reference_condition_id"],
                    "forward_story_a_condition_id": candidate_condition_id,
                    "forward_story_b_condition_id": reference_condition_id,
                    "reverse_story_a_condition_id": reference_condition_id,
                    "reverse_story_b_condition_id": candidate_condition_id,
                    "creativity_forward_prompt_text": creativity_forward_prompt,
                    "creativity_reverse_prompt_text": creativity_reverse_prompt,
                    "coherence_forward_prompt_text": coherence_forward_prompt,
                    "coherence_reverse_prompt_text": coherence_reverse_prompt,
                    "creativity_forward_raw_response": creativity_forward_raw,
                    "creativity_reverse_raw_response": creativity_reverse_raw,
                    "coherence_forward_raw_response": coherence_forward_raw,
                    "coherence_reverse_raw_response": coherence_reverse_raw,
                    "creativity_forward_winner_label": creativity_forward_label,
                    "creativity_reverse_winner_label": creativity_reverse_label,
                    "coherence_forward_winner_label": coherence_forward_label,
                    "coherence_reverse_winner_label": coherence_reverse_label,
                    "creativity_forward_winner_condition_id": creativity_forward_winner_condition_id,
                    "creativity_reverse_winner_condition_id": creativity_reverse_winner_condition_id,
                    "coherence_forward_winner_condition_id": coherence_forward_winner_condition_id,
                    "coherence_reverse_winner_condition_id": coherence_reverse_winner_condition_id,
                    "creativity_winner_condition_id": resolve_order_robust_winner(
                        creativity_forward_winner_condition_id,
                        creativity_reverse_winner_condition_id,
                    ),
                    "coherence_winner_condition_id": resolve_order_robust_winner(
                        coherence_forward_winner_condition_id,
                        coherence_reverse_winner_condition_id,
                    ),
                }
            )

    condition_summaries = summarize_condition_outputs(output_rows)
    comparison_summaries = summarize_pairwise_judgments(judgment_rows, comparisons=comparisons)
    gate_assessment = summarize_gate_assessment(comparison_summaries)

    summary = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "model_id": args.model_id,
        "device": device,
        "prompt_count": len(prompt_rows),
        "hidden_layer": hidden_layer,
        "steering_coeffs": steering_coeffs,
        "max_new_tokens": args.max_new_tokens,
        "judge_max_new_tokens": args.judge_max_new_tokens,
        "seed": args.seed,
        "split_path": path_for_summary(args.split_path),
        "templates_path": path_for_summary(args.templates_path),
        "judge_templates_path": path_for_summary(args.judge_templates_path),
        "sweep_dir": path_for_summary(args.sweep_dir),
        "reused_generated_outputs": reused_generated_outputs,
        "condition_summaries": condition_summaries,
        "comparison_summaries": comparison_summaries,
        "gate_assessment": gate_assessment,
    }

    write_json(output_dir / "summary.json", summary)
    write_jsonl(generated_outputs_path, output_rows)
    write_jsonl(output_dir / "pairwise_judgments.jsonl", judgment_rows)
    write_readme(output_dir / "README.md", summary)

    print(f"wrote creativity output gate artifact to {output_dir}")
    print(f"best dense condition: {gate_assessment['best_dense_condition_id']}")
    print(f"automatic pass recommendation: {gate_assessment['automatic_pass_recommendation']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
