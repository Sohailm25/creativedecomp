# ABOUTME: Runs a bounded pilot sweep over dense refusal-direction layers on a frozen response-centered pilot pack.
# ABOUTME: Saves per-layer separation metrics and the best-layer direction so the simpler-concept control stays pipeline-matched.

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
from repeng import DatasetEntry
from repeng.extract import batched_get_hiddens


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from run_creativity_direction_smoke import (  # noqa: E402
    ROOT,
    DEFAULT_BATCH_SIZE,
    DEFAULT_MAX_PAIRS,
    DEFAULT_MODEL_ID,
    align_direction_sign,
    load_model_and_tokenizer,
    load_prompt_rows,
    project_onto_direction_safe,
    select_device,
    summarize_pairwise_projections,
    write_json,
    write_jsonl,
)
from run_creativity_direction_layer_sweep import (  # noqa: E402
    add_template_control_metrics,
    build_template_control_strings,
    cleanup_optional_output_files,
    compute_margin_zscore,
    compute_mean_difference_direction,
    parse_direction_method,
    parse_layers_argument,
    path_for_summary,
    prepare_output_dir,
    rank_controlled_layer_rows,
    rank_layer_rows,
    select_controlled_best_layer,
)


DEFAULT_SPLIT_PATH = ROOT / "prompts" / "refusal_direction_v1_pilot_pairs.jsonl"
DEFAULT_TEMPLATES_PATH = ROOT / "prompts" / "refusal_direction_v1_templates.json"


def default_output_dir() -> Path:
    run_date = datetime.now().strftime("%Y%m%d")
    return ROOT / "results" / "refusal_direction" / f"{run_date}-gemma2-2b-layer-sweep-v1-mean-difference"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a pilot layer sweep for the dense refusal direction on the frozen pilot split."
    )
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID)
    parser.add_argument("--split-path", type=Path, default=DEFAULT_SPLIT_PATH)
    parser.add_argument("--templates-path", type=Path, default=DEFAULT_TEMPLATES_PATH)
    parser.add_argument(
        "--direction-method",
        default="mean_difference",
        choices=["pca", "mean_difference"],
        help="Dense direction extraction method to compare on the same refusal pair slice.",
    )
    parser.add_argument("--layers", default=None, help="Comma-separated layer ids to evaluate; defaults to all layers.")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--max-pairs", type=int, default=DEFAULT_MAX_PAIRS)
    parser.add_argument("--device", choices=["auto", "mps", "cpu"], default="auto")
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def load_templates(path: Path) -> dict[str, str]:
    templates = json.loads(path.read_text(encoding="utf-8"))
    if "response_pair_template_control" not in templates:
        raise KeyError("missing template key: response_pair_template_control")
    return templates


def build_contrastive_dataset(prompt_rows: list[dict[str, Any]]) -> list[DatasetEntry]:
    return [
        DatasetEntry(
            positive=str(row["positive_text"]),
            negative=str(row["negative_text"]),
        )
        for row in prompt_rows
    ]


def compute_pca_direction(train_matrix: list[list[float]] | np.ndarray) -> np.ndarray:
    train_array = np.asarray(train_matrix, dtype=np.float64)
    if train_array.ndim != 2:
        raise ValueError(f"expected a 2D train matrix but got shape {train_array.shape}")
    centered = train_array - train_array.mean(axis=0, keepdims=True)
    _, _, right_singular_vectors = np.linalg.svd(centered, full_matrices=False)
    direction = right_singular_vectors[0].astype(np.float32)
    direction_norm = float(np.linalg.norm(direction))
    if direction_norm == 0.0:
        raise ValueError("PCA direction has zero norm")
    return direction / direction_norm


def compute_layer_direction(
    layer_hiddens: list[list[float]] | np.ndarray,
    direction_method: str,
) -> np.ndarray:
    layer_hidden_array = np.asarray(layer_hiddens, dtype=np.float32)
    positive_hidden = layer_hidden_array[::2]
    negative_hidden = layer_hidden_array[1::2]
    if direction_method == "pca":
        train_matrix = positive_hidden.astype(np.float64) - negative_hidden.astype(np.float64)
        direction = compute_pca_direction(train_matrix)
    elif direction_method == "mean_difference":
        direction = compute_mean_difference_direction(positive_hidden, negative_hidden)
    else:
        raise ValueError(f"unsupported direction method: {direction_method}")
    return align_direction_sign(layer_hidden_array, direction)


def compute_difference_direction(
    positive_hidden: list[float] | np.ndarray,
    negative_hidden: list[float] | np.ndarray,
) -> np.ndarray:
    direction = np.asarray(positive_hidden, dtype=np.float64) - np.asarray(negative_hidden, dtype=np.float64)
    direction_norm = float(np.linalg.norm(direction))
    if direction_norm == 0.0:
        raise ValueError("difference direction has zero norm")
    return (direction / direction_norm).astype(np.float32)


def compute_cosine_similarity(lhs: list[float] | np.ndarray, rhs: list[float] | np.ndarray) -> float:
    lhs_array = np.asarray(lhs, dtype=np.float64)
    rhs_array = np.asarray(rhs, dtype=np.float64)
    denominator = float(np.linalg.norm(lhs_array) * np.linalg.norm(rhs_array))
    if denominator == 0.0:
        raise ValueError("cannot compute cosine similarity with a zero-norm vector")
    return float(np.dot(lhs_array, rhs_array) / denominator)


def build_layer_row(
    hidden_layer: int,
    prompt_rows: list[dict[str, Any]],
    layer_hiddens: np.ndarray,
    template_control_hiddens: np.ndarray,
    direction_method: str,
) -> tuple[dict[str, Any], np.ndarray, np.ndarray | None, list[dict[str, Any]]]:
    direction = compute_layer_direction(layer_hiddens, direction_method=direction_method)
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
    template_difference = template_control_hiddens[0].astype(np.float64) - template_control_hiddens[1].astype(np.float64)
    if float(np.linalg.norm(template_difference)) == 0.0:
        template_direction = None
        template_control_summary = {
            "positive_gt_negative_fraction": 0.0,
            "mean_margin": 0.0,
            "margin_zscore": 0.0,
        }
    else:
        template_direction = compute_difference_direction(
            template_control_hiddens[0],
            template_control_hiddens[1],
        )
        template_control_projections = project_onto_direction_safe(layer_hiddens, template_direction)
        template_control_summary = summarize_pairwise_projections(prompt_rows, template_control_projections)
        template_control_margins = np.asarray(
            [detail["margin"] for detail in template_control_summary["pair_details"]],
            dtype=np.float64,
        )
        template_control_summary["margin_zscore"] = compute_margin_zscore(template_control_margins)
    row = add_template_control_metrics(
        row=row,
        template_control_summary=template_control_summary,
        direction=direction,
        template_direction=template_direction,
    )
    return row, direction, template_direction, summary["pair_details"]


def write_readme(path: Path, summary: dict[str, Any]) -> None:
    raw_top_layers = summary["raw_top_layers"]
    controlled_top_layers = summary["controlled_top_layers"]
    controlled_best_row = summary["controlled_best_layer_metrics"]
    lines = [
        "# Refusal Direction Layer Sweep",
        "",
        f"- Generated at: `{summary['created_at']}`",
        f"- Model: `{summary['model_id']}`",
        f"- Device: `{summary['device']}`",
        f"- Direction method: `{summary['direction_method']}`",
        f"- Candidate layers: `{summary['candidate_layers']}`",
        f"- Pair count: `{summary['pair_count']}`",
        f"- Raw ranking rule: `{', '.join(summary['raw_ranking_rule'])}`",
        f"- Controlled ranking rule: `{', '.join(summary['controlled_ranking_rule'])}`",
        f"- Raw best layer: `{summary['raw_best_layer']}`",
        f"- Controlled best layer: `{summary['controlled_best_layer']}`",
        "",
        "Top controlled layers:",
    ]
    if controlled_best_row is None:
        lines.extend(
            [
                "- Controlled winner status: no layer cleared the template-control threshold "
                "(positive fraction delta and positive margin-zscore delta).",
                "",
            ]
        )
    else:
        lines.extend(
            [
                f"- Controlled best raw fraction: `{controlled_best_row['positive_gt_negative_fraction']:.6f}`",
                f"- Controlled best template-control fraction: `{controlled_best_row['template_control_positive_gt_negative_fraction']:.6f}`",
                f"- Controlled best fraction delta: `{controlled_best_row['controlled_fraction_delta']:.6f}`",
                f"- Controlled best cosine: `{controlled_best_row['template_direction_cosine']:.6f}`",
                "",
            ]
        )
    for row in controlled_top_layers:
        lines.append(
            f"- layer `{row['hidden_layer']}`: raw fraction `{row['positive_gt_negative_fraction']:.6f}`, "
            f"template fraction `{row['template_control_positive_gt_negative_fraction']:.6f}`, "
            f"delta `{row['controlled_fraction_delta']:.6f}`, cosine `{row['template_direction_cosine']:.6f}`"
        )
    lines.append("")
    lines.append("Top raw layers:")
    for row in raw_top_layers:
        lines.append(
            f"- layer `{row['hidden_layer']}`: raw fraction `{row['positive_gt_negative_fraction']:.6f}`, "
            f"margin `{row['mean_margin']:.6f}`, z-score `{row['margin_zscore']:.6f}`"
        )
    lines.extend(
        [
            "",
            "Artifacts:",
            "- `summary.json`",
            "- `layer_metrics.jsonl`",
            "- `layer_metrics_raw.jsonl`",
            "- `raw_best_layer_pair_details.jsonl`",
            "- `directions.npz`",
        ]
    )
    if summary["best_layer_pair_details_path"] is not None:
        lines.insert(-2, "- `controlled_best_layer_pair_details.jsonl`")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir or default_output_dir()
    prepare_output_dir(output_dir, overwrite=args.overwrite)
    direction_method = parse_direction_method(args.direction_method)

    prompt_rows = load_prompt_rows(args.split_path, max_pairs=args.max_pairs)
    templates = load_templates(args.templates_path)
    dataset = build_contrastive_dataset(prompt_rows)
    train_strings = [text for entry in dataset for text in (entry.positive, entry.negative)]
    template_control_strings = build_template_control_strings(prompt_rows, templates)

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
    template_control_hidden_state_map = batched_get_hiddens(
        model,
        tokenizer,
        list(template_control_strings),
        candidate_layers,
        batch_size=args.batch_size,
    )

    layer_rows: list[dict[str, Any]] = []
    pair_details_by_layer: dict[int, list[dict[str, Any]]] = {}
    directions: dict[str, np.ndarray | None] = {}
    for layer in candidate_layers:
        row, direction, template_direction, pair_details = build_layer_row(
            hidden_layer=layer,
            prompt_rows=prompt_rows,
            layer_hiddens=np.asarray(hidden_state_map[layer], dtype=np.float32),
            template_control_hiddens=np.asarray(
                template_control_hidden_state_map[layer],
                dtype=np.float32,
            ),
            direction_method=direction_method,
        )
        layer_rows.append(row)
        pair_details_by_layer[layer] = pair_details
        directions[f"layer_{layer}"] = direction
        directions[f"template_control_layer_{layer}"] = template_direction

    raw_ranked_rows = rank_layer_rows(layer_rows)
    controlled_ranked_rows = rank_controlled_layer_rows(layer_rows)
    raw_best_row = raw_ranked_rows[0]
    controlled_best_row = select_controlled_best_layer(controlled_ranked_rows)
    raw_best_layer = int(raw_best_row["hidden_layer"])
    controlled_best_layer = (
        int(controlled_best_row["hidden_layer"]) if controlled_best_row is not None else None
    )
    summary = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "model_id": args.model_id,
        "device": device,
        "direction_method": direction_method,
        "batch_size": args.batch_size,
        "pair_count": len(prompt_rows),
        "split_path": path_for_summary(args.split_path),
        "templates_path": path_for_summary(args.templates_path),
        "candidate_layers": candidate_layers,
        "raw_ranking_rule": [
            "positive_gt_negative_fraction",
            "margin_zscore",
            "mean_margin",
        ],
        "controlled_ranking_rule": [
            "controlled_fraction_delta",
            "controlled_margin_zscore_delta",
            "abs(template_direction_cosine)",
            "positive_gt_negative_fraction",
        ],
        "best_layer": controlled_best_layer,
        "raw_best_layer": raw_best_layer,
        "raw_best_layer_metrics": raw_best_row,
        "controlled_best_layer": controlled_best_layer,
        "controlled_best_layer_metrics": controlled_best_row,
        "raw_top_layers": raw_ranked_rows[:5],
        "controlled_top_layers": controlled_ranked_rows[:5],
        "layer_metrics_path": "layer_metrics.jsonl",
        "layer_metrics_raw_path": "layer_metrics_raw.jsonl",
        "best_layer_pair_details_path": (
            "controlled_best_layer_pair_details.jsonl" if controlled_best_layer is not None else None
        ),
        "raw_best_layer_pair_details_path": "raw_best_layer_pair_details.jsonl",
        "directions_path": "directions.npz",
    }

    cleanup_optional_output_files(
        output_dir,
        has_controlled_best_layer=controlled_best_layer is not None,
    )
    write_json(output_dir / "summary.json", summary)
    write_jsonl(output_dir / "layer_metrics.jsonl", controlled_ranked_rows)
    write_jsonl(output_dir / "layer_metrics_raw.jsonl", raw_ranked_rows)
    if controlled_best_layer is not None:
        write_jsonl(
            output_dir / "controlled_best_layer_pair_details.jsonl",
            pair_details_by_layer[controlled_best_layer],
        )
    write_jsonl(
        output_dir / "raw_best_layer_pair_details.jsonl",
        pair_details_by_layer[raw_best_layer],
    )
    np.savez(output_dir / "directions.npz", **directions)
    write_readme(output_dir / "README.md", summary)

    print(f"wrote layer-sweep artifact to {output_dir}")
    print(f"raw best layer: {raw_best_layer}")
    if controlled_best_row is None:
        print("controlled best layer: none")
        print("controlled result: no layer cleared template-control thresholds")
    else:
        print(f"controlled best layer: {controlled_best_layer}")
        print(
            "controlled best fraction delta: "
            f"{controlled_best_row['controlled_fraction_delta']:.6f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
