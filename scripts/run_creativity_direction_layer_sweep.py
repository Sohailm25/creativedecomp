# ABOUTME: Runs a bounded pilot sweep over dense creativity-direction layers on the frozen pilot split.
# ABOUTME: Saves per-layer separation metrics and the best-layer direction so later steering runs use evidence instead of the scaffold default.

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
from repeng.extract import batched_get_hiddens


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from run_creativity_direction_smoke import (  # noqa: E402
    ROOT,
    DEFAULT_BATCH_SIZE,
    DEFAULT_MAX_PAIRS,
    DEFAULT_MODEL_ID,
    DEFAULT_SPLIT_PATH,
    DEFAULT_TEMPLATES_PATH,
    align_direction_sign,
    build_contrastive_dataset,
    compute_pca_direction,
    load_model_and_tokenizer,
    load_prompt_rows,
    load_templates,
    project_onto_direction_safe,
    select_device,
    summarize_pairwise_projections,
    write_json,
    write_jsonl,
)


def default_output_dir() -> Path:
    run_date = datetime.now().strftime("%Y%m%d")
    return ROOT / "results" / "creativity_direction" / f"{run_date}-gemma2-2b-layer-sweep-pilot"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a pilot layer sweep for the dense creativity direction on the frozen pilot split."
    )
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID)
    parser.add_argument("--split-path", type=Path, default=DEFAULT_SPLIT_PATH)
    parser.add_argument("--templates-path", type=Path, default=DEFAULT_TEMPLATES_PATH)
    parser.add_argument("--layers", default=None, help="Comma-separated layer ids to evaluate; defaults to all layers.")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--max-pairs", type=int, default=DEFAULT_MAX_PAIRS)
    parser.add_argument("--device", choices=["auto", "mps", "cpu"], default="auto")
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def parse_layers_argument(layers_arg: str | None, num_hidden_layers: int) -> list[int]:
    if layers_arg is None:
        return list(range(num_hidden_layers))

    layers: list[int] = []
    for raw_value in layers_arg.split(","):
        value = raw_value.strip()
        if not value:
            continue
        layer = int(value)
        if layer < 0 or layer >= num_hidden_layers:
            raise ValueError(f"layer {layer} is outside valid range [0, {num_hidden_layers - 1}]")
        if layer not in layers:
            layers.append(layer)
    if not layers:
        raise ValueError("no valid layers supplied")
    return layers


def prepare_output_dir(path: Path, overwrite: bool) -> None:
    if path.exists() and any(path.iterdir()) and not overwrite:
        raise FileExistsError(
            f"output directory already exists and is not empty: {path}. Use --overwrite to replace artifacts."
        )
    path.mkdir(parents=True, exist_ok=True)


def compute_margin_zscore(margins: np.ndarray) -> float:
    margin_std = float(np.std(margins, ddof=0))
    margin_mean = float(np.mean(margins))
    if margin_std == 0.0:
        if margin_mean > 0:
            return float("inf")
        if margin_mean < 0:
            return float("-inf")
        return 0.0
    return margin_mean / margin_std


def build_layer_row(
    hidden_layer: int,
    prompt_rows: list[dict[str, Any]],
    layer_hiddens: np.ndarray,
) -> tuple[dict[str, Any], np.ndarray, list[dict[str, Any]]]:
    train_matrix = layer_hiddens[::2].astype(np.float64) - layer_hiddens[1::2].astype(np.float64)
    direction = compute_pca_direction(train_matrix)
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


def rank_layer_rows(layer_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        layer_rows,
        key=lambda row: (
            -float(row["positive_gt_negative_fraction"]),
            -float(row["margin_zscore"]),
            -float(row["mean_margin"]),
            int(row["hidden_layer"]),
        ),
    )


def write_readme(path: Path, summary: dict[str, Any]) -> None:
    top_layers = summary["top_layers"]
    lines = [
        "# Creativity Direction Layer Sweep",
        "",
        f"- Generated at: `{summary['created_at']}`",
        f"- Model: `{summary['model_id']}`",
        f"- Device: `{summary['device']}`",
        f"- Candidate layers: `{summary['candidate_layers']}`",
        f"- Pair count: `{summary['pair_count']}`",
        f"- Ranking rule: `{', '.join(summary['ranking_rule'])}`",
        f"- Best layer: `{summary['best_layer']}`",
        f"- Best positive > negative fraction: `{summary['best_layer_metrics']['positive_gt_negative_fraction']:.6f}`",
        f"- Best mean margin: `{summary['best_layer_metrics']['mean_margin']:.6f}`",
        f"- Best margin z-score: `{summary['best_layer_metrics']['margin_zscore']:.6f}`",
        "",
        "Top layers:",
    ]
    for row in top_layers:
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


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir or default_output_dir()
    prepare_output_dir(output_dir, overwrite=args.overwrite)

    prompt_rows = load_prompt_rows(args.split_path, max_pairs=args.max_pairs)
    templates = load_templates(args.templates_path)
    dataset = build_contrastive_dataset(prompt_rows, templates)
    train_strings = [text for entry in dataset for text in (entry.positive, entry.negative)]

    device = select_device(args.device)
    model, tokenizer = load_model_and_tokenizer(args.model_id, device)
    candidate_layers = parse_layers_argument(args.layers, model.config.num_hidden_layers)
    hidden_state_map = batched_get_hiddens(
        model,
        tokenizer,
        train_strings,
        candidate_layers,
        batch_size=args.batch_size,
    )

    layer_rows: list[dict[str, Any]] = []
    pair_details_by_layer: dict[int, list[dict[str, Any]]] = {}
    directions: dict[str, np.ndarray] = {}
    for layer in candidate_layers:
        row, direction, pair_details = build_layer_row(
            hidden_layer=layer,
            prompt_rows=prompt_rows,
            layer_hiddens=np.asarray(hidden_state_map[layer], dtype=np.float32),
        )
        layer_rows.append(row)
        pair_details_by_layer[layer] = pair_details
        directions[f"layer_{layer}"] = direction

    ranked_rows = rank_layer_rows(layer_rows)
    best_row = ranked_rows[0]
    best_layer = int(best_row["hidden_layer"])
    summary = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "model_id": args.model_id,
        "device": device,
        "batch_size": args.batch_size,
        "pair_count": len(prompt_rows),
        "split_path": str(args.split_path.relative_to(ROOT)),
        "templates_path": str(args.templates_path.relative_to(ROOT)),
        "candidate_layers": candidate_layers,
        "ranking_rule": [
            "positive_gt_negative_fraction",
            "margin_zscore",
            "mean_margin",
        ],
        "best_layer": best_layer,
        "best_layer_metrics": best_row,
        "top_layers": ranked_rows[:5],
        "layer_metrics_path": "layer_metrics.jsonl",
        "best_layer_pair_details_path": "best_layer_pair_details.jsonl",
        "directions_path": "directions.npz",
    }

    write_json(output_dir / "summary.json", summary)
    write_jsonl(output_dir / "layer_metrics.jsonl", ranked_rows)
    write_jsonl(output_dir / "best_layer_pair_details.jsonl", pair_details_by_layer[best_layer])
    np.savez(output_dir / "directions.npz", **directions)
    write_readme(output_dir / "README.md", summary)

    print(f"wrote layer-sweep artifact to {output_dir}")
    print(f"best layer: {best_layer}")
    print(f"best positive > negative fraction: {best_row['positive_gt_negative_fraction']:.6f}")
    print(f"best mean margin: {best_row['mean_margin']:.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
