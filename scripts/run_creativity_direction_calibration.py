# ABOUTME: Runs a bounded calibration pass for the response-centered v2 creativity direction before decomposition.
# ABOUTME: Sweeps steering coefficients on the top late-layer candidates and records output-side quality plus probe-layer projections.

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import sys
from typing import Any

import numpy as np
from repeng.extract import batched_get_hiddens


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from probe_base_model_story_prompts import compute_meta_marker_score  # noqa: E402
from run_creativity_direction_smoke import (  # noqa: E402
    ROOT,
    DEFAULT_BATCH_SIZE,
    DEFAULT_MODEL_ID,
    load_model_and_tokenizer,
    load_prompt_rows,
    load_templates,
    project_onto_direction_safe,
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
    select_candidate_layers,
)


DEFAULT_SPLIT_PATH = ROOT / "prompts" / "creative_direction_v2_pilot_pairs.jsonl"
DEFAULT_TEMPLATES_PATH = ROOT / "prompts" / "creative_direction_v2_templates.json"
DEFAULT_SWEEP_DIR = (
    ROOT
    / "results"
    / "creativity_direction"
    / "20260318-gemma2-2b-layer-sweep-response-pairs-v2"
)
DEFAULT_MAX_PROMPTS = 6
DEFAULT_MAX_NEW_TOKENS = 96
DEFAULT_STEERING_COEFFS = "-1.0,0.5,1.0,2.0"
DEFAULT_SEED = 3100


def default_output_dir() -> Path:
    run_date = datetime.now().strftime("%Y%m%d")
    return ROOT / "results" / "steering_eval" / f"{run_date}-gemma2-2b-v2-direction-calibration"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a bounded calibration pass for the response-centered v2 creativity direction."
    )
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID)
    parser.add_argument("--split-path", type=Path, default=DEFAULT_SPLIT_PATH)
    parser.add_argument("--templates-path", type=Path, default=DEFAULT_TEMPLATES_PATH)
    parser.add_argument("--sweep-dir", type=Path, default=DEFAULT_SWEEP_DIR)
    parser.add_argument("--max-prompts", type=int, default=DEFAULT_MAX_PROMPTS)
    parser.add_argument("--max-new-tokens", type=int, default=DEFAULT_MAX_NEW_TOKENS)
    parser.add_argument("--steering-coeffs", default=DEFAULT_STEERING_COEFFS)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--device", choices=["auto", "mps", "cpu"], default="auto")
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def parse_steering_coeffs_argument(raw_value: str) -> list[float]:
    coeffs: list[float] = []
    seen: set[float] = set()
    for piece in raw_value.split(","):
        value = piece.strip()
        if not value:
            continue
        coeff = float(value)
        if coeff not in seen:
            coeffs.append(coeff)
            seen.add(coeff)
    if not coeffs:
        raise ValueError("at least one steering coefficient is required")
    return coeffs


def format_coeff_slug(coeff: float) -> str:
    normalized = f"{coeff:.1f}".replace("-", "neg").replace(".", "p")
    return normalized


def build_calibration_conditions(
    candidate_layers: list[int],
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
    for layer in candidate_layers:
        for coeff in steering_coeffs:
            conditions.append(
                {
                    "condition_id": f"neutral_steered_layer{layer}_coeff_{format_coeff_slug(coeff)}",
                    "prompt_mode": "neutral",
                    "hidden_layer": layer,
                    "steering_coeff": coeff,
                    "normalize_control": True,
                }
            )
    return conditions


def compute_distinct_unigram_ratio(text: str) -> float:
    tokens = [token for token in text.lower().split() if token]
    if not tokens:
        return 0.0
    return float(len(set(tokens)) / len(tokens))


def add_probe_projections(
    rows: list[dict[str, Any]],
    model,
    tokenizer,
    probe_layers: list[int],
    directions: dict[int, np.ndarray],
    batch_size: int,
) -> None:
    full_texts = [str(row["full_text"]) for row in rows]
    hidden_state_map = batched_get_hiddens(
        model,
        tokenizer,
        full_texts,
        probe_layers,
        batch_size=batch_size,
    )
    for layer in probe_layers:
        projections = project_onto_direction_safe(hidden_state_map[layer], directions[layer])
        for row, projection in zip(rows, projections, strict=True):
            row.setdefault("probe_projections", {})[str(layer)] = float(projection)


def summarize_outputs(
    rows: list[dict[str, Any]],
    probe_layers: list[int],
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(str(row["condition_id"]), []).append(row)

    summaries: list[dict[str, Any]] = []
    for condition_id, condition_rows in grouped.items():
        word_counts = [int(row["completion_word_count"]) for row in condition_rows]
        char_counts = [int(row["completion_char_count"]) for row in condition_rows]
        meta_scores = [int(row["meta_marker_score"]) for row in condition_rows]
        distinct_ratios = [float(row["distinct_unigram_ratio"]) for row in condition_rows]
        summary = {
            "condition_id": condition_id,
            "sample_count": len(condition_rows),
            "mean_completion_word_count": float(np.mean(word_counts)),
            "mean_completion_char_count": float(np.mean(char_counts)),
            "meta_marker_fraction": float(np.mean([score > 0 for score in meta_scores])),
            "mean_meta_marker_score": float(np.mean(meta_scores)),
            "mean_distinct_unigram_ratio": float(np.mean(distinct_ratios)),
        }
        for layer in probe_layers:
            layer_key = str(layer)
            layer_projections = [float(row["probe_projections"][layer_key]) for row in condition_rows]
            summary[f"mean_probe_projection_layer_{layer}"] = float(np.mean(layer_projections))
        summaries.append(summary)

    return sorted(summaries, key=lambda row: row["condition_id"])


def write_readme(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Creativity Direction Calibration",
        "",
        f"- Generated at: `{summary['created_at']}`",
        f"- Model: `{summary['model_id']}`",
        f"- Device: `{summary['device']}`",
        f"- Prompt count: `{summary['prompt_count']}`",
        f"- Candidate layers: `{summary['candidate_layers']}`",
        f"- Steering coefficients: `{summary['steering_coeffs']}`",
        f"- Max new tokens: `{summary['max_new_tokens']}`",
        f"- Seed base: `{summary['seed']}`",
        f"- Neutral prompt template: `{summary['generation_prompt_templates']['neutral']}`",
        f"- Creative baseline prompt template: `{summary['generation_prompt_templates']['prompt_only_creativity']}`",
        "",
        "Condition summaries:",
    ]
    for row in summary["condition_summaries"]:
        probe_bits = ", ".join(
            f"layer {layer} projection `{row[f'mean_probe_projection_layer_{layer}']:.2f}`"
            for layer in summary["candidate_layers"]
        )
        lines.append(
            f"- `{row['condition_id']}`: mean words `{row['mean_completion_word_count']:.2f}`, "
            f"meta fraction `{row['meta_marker_fraction']:.3f}`, "
            f"distinct-unigram ratio `{row['mean_distinct_unigram_ratio']:.3f}`, "
            f"{probe_bits}"
        )
    lines.extend(
        [
            "",
            "Artifacts:",
            "- `summary.json`",
            "- `outputs.jsonl`",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir or default_output_dir()
    prepare_output_dir(output_dir, overwrite=args.overwrite)

    prompt_rows = load_prompt_rows(args.split_path, max_pairs=args.max_prompts)
    templates = load_templates(args.templates_path)
    ranked_rows = load_ranked_layer_rows(args.sweep_dir / "layer_metrics.jsonl")
    candidate_layers = select_candidate_layers(ranked_rows)
    steering_coeffs = parse_steering_coeffs_argument(args.steering_coeffs)
    conditions = build_calibration_conditions(candidate_layers, steering_coeffs)
    directions = load_directions(args.sweep_dir / "directions.npz", candidate_layers)

    device = select_device(args.device)
    model, tokenizer = load_model_and_tokenizer(args.model_id, device)

    output_rows: list[dict[str, Any]] = []
    for prompt_index, prompt_row in enumerate(prompt_rows):
        for condition_index, condition in enumerate(conditions):
            prompt_text_full = build_prompt_text(
                prompt_text=str(prompt_row["prompt_text"]),
                prompt_mode=str(condition["prompt_mode"]),
                templates=templates,
            )
            seed = args.seed + (prompt_index * 100) + condition_index
            hidden_layer = condition["hidden_layer"]
            if hidden_layer is None:
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
                    hidden_layer=int(hidden_layer),
                    direction=directions[int(hidden_layer)],
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
                    "hidden_layer": hidden_layer,
                    "steering_coeff": condition["steering_coeff"],
                    "seed": seed,
                    "prompt_text_full": prompt_text_full,
                    "completion_text": completion_text,
                    "full_text": full_text,
                    "completion_char_count": len(completion_text),
                    "completion_word_count": len(completion_text.split()),
                    "meta_marker_score": compute_meta_marker_score(completion_text),
                    "distinct_unigram_ratio": compute_distinct_unigram_ratio(completion_text),
                }
            )

    add_probe_projections(
        output_rows,
        model=model,
        tokenizer=tokenizer,
        probe_layers=candidate_layers,
        directions=directions,
        batch_size=args.batch_size,
    )
    condition_summaries = summarize_outputs(output_rows, probe_layers=candidate_layers)
    summary = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "model_id": args.model_id,
        "device": device,
        "prompt_count": len(prompt_rows),
        "candidate_layers": candidate_layers,
        "steering_coeffs": steering_coeffs,
        "max_new_tokens": args.max_new_tokens,
        "seed": args.seed,
        "split_path": path_for_summary(args.split_path),
        "templates_path": path_for_summary(args.templates_path),
        "sweep_dir": path_for_summary(args.sweep_dir),
        "generation_prompt_templates": {
            "neutral": templates["generation_neutral_story_opening"],
            "prompt_only_creativity": templates["generation_creative_story_opening"],
        },
        "conditions": conditions,
        "condition_summaries": condition_summaries,
        "outputs_path": "outputs.jsonl",
    }

    write_json(output_dir / "summary.json", summary)
    write_jsonl(output_dir / "outputs.jsonl", output_rows)
    write_readme(output_dir / "README.md", summary)

    print(f"wrote calibration artifact to {output_dir}")
    print(f"candidate layers: {candidate_layers}")
    print(f"steering coeffs: {steering_coeffs}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
