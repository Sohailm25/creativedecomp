# ABOUTME: Runs the smallest reproducible creativity-direction extraction on the frozen pilot split.
# ABOUTME: Saves a dense repeng control direction and projection summary so Phase 1 starts with a real local artifact.

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
from typing import Any

import numpy as np
from repeng import DatasetEntry
from repeng.extract import batched_get_hiddens
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL_ID = "google/gemma-2-2b"
DEFAULT_HIDDEN_LAYER = 12
DEFAULT_BATCH_SIZE = 4
DEFAULT_MAX_PAIRS = 32
DEFAULT_SPLIT_PATH = ROOT / "prompts" / "creative_direction_v1_pilot.jsonl"
DEFAULT_TEMPLATES_PATH = ROOT / "prompts" / "creative_direction_v1_templates.json"


def default_output_dir(hidden_layer: int) -> Path:
    run_date = datetime.now().strftime("%Y%m%d")
    return (
        ROOT
        / "results"
        / "creativity_direction"
        / f"{run_date}-gemma2-2b-repeng-smoke-layer{hidden_layer}"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the first creativity-direction extraction smoke on the frozen pilot split."
    )
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID)
    parser.add_argument("--split-path", type=Path, default=DEFAULT_SPLIT_PATH)
    parser.add_argument("--templates-path", type=Path, default=DEFAULT_TEMPLATES_PATH)
    parser.add_argument("--hidden-layer", type=int, default=DEFAULT_HIDDEN_LAYER)
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--max-pairs", type=int, default=DEFAULT_MAX_PAIRS)
    parser.add_argument("--device", choices=["auto", "mps", "cpu"], default="auto")
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def load_prompt_rows(path: Path, max_pairs: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        rows.append(row)
        if len(rows) == max_pairs:
            break
    if not rows:
        raise ValueError(f"no prompt rows found in {path}")
    return rows


def load_templates(path: Path) -> dict[str, str]:
    templates = json.loads(path.read_text(encoding="utf-8"))
    for key in ["creative_instruction", "uncreative_instruction"]:
        if key not in templates:
            raise KeyError(f"missing template key: {key}")
    return templates


def build_contrastive_dataset(
    prompt_rows: list[dict[str, Any]],
    templates: dict[str, str],
) -> list[DatasetEntry]:
    return [
        DatasetEntry(
            positive=templates["creative_instruction"].format(prompt=row["prompt_text"]),
            negative=templates["uncreative_instruction"].format(prompt=row["prompt_text"]),
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


def project_onto_direction_safe(
    hiddens: list[list[float]] | np.ndarray,
    direction: list[float] | np.ndarray,
) -> np.ndarray:
    hidden_array = np.asarray(hiddens, dtype=np.float64)
    direction_array = np.asarray(direction, dtype=np.float64)
    direction_norm = np.linalg.norm(direction_array)
    if direction_norm == 0.0:
        raise ValueError("cannot project onto a zero-norm direction")
    projections = np.multiply(hidden_array, direction_array, dtype=np.float64).sum(axis=1) / direction_norm
    return projections.astype(np.float32)


def align_direction_sign(hidden_states: np.ndarray, direction: np.ndarray) -> np.ndarray:
    projections = project_onto_direction_safe(hidden_states, direction)
    positive = projections[::2]
    negative = projections[1::2]
    if float(np.mean(positive < negative)) > float(np.mean(positive > negative)):
        return -direction
    return direction


def summarize_pairwise_projections(
    prompt_rows: list[dict[str, Any]],
    projections: list[float] | np.ndarray,
) -> dict[str, Any]:
    projection_array = np.asarray(projections, dtype=np.float32)
    expected_count = len(prompt_rows) * 2
    if projection_array.shape[0] != expected_count:
        raise ValueError(
            f"expected {expected_count} projections for {len(prompt_rows)} prompt pairs but got {projection_array.shape[0]}"
        )

    positive = projection_array[::2]
    negative = projection_array[1::2]
    margins = positive - negative
    pair_details = [
        {
            "prompt_id": row["prompt_id"],
            "prompt_text": row["prompt_text"],
            "positive_projection": float(pos),
            "negative_projection": float(neg),
            "margin": float(pos - neg),
        }
        for row, pos, neg in zip(prompt_rows, positive, negative, strict=True)
    ]
    return {
        "pair_count": len(prompt_rows),
        "positive_mean_projection": float(np.mean(positive)),
        "negative_mean_projection": float(np.mean(negative)),
        "mean_margin": float(np.mean(margins)),
        "positive_gt_negative_fraction": float(np.mean(margins > 0)),
        "pair_details": pair_details,
    }


def select_device(requested_device: str) -> str:
    if requested_device == "auto":
        return "mps" if torch.backends.mps.is_available() else "cpu"
    if requested_device == "mps" and not torch.backends.mps.is_available():
        raise RuntimeError("requested device 'mps' but MPS is not available")
    return requested_device


def load_model_and_tokenizer(model_id: str, device: str):
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    if tokenizer.pad_token is None and tokenizer.eos_token is not None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(model_id, dtype=torch.float32)
    model.to(device)
    model.eval()
    return model, tokenizer


def train_direction_and_projections(
    model,
    tokenizer,
    dataset: list[DatasetEntry],
    hidden_layer: int,
    batch_size: int,
) -> tuple[np.ndarray, np.ndarray]:
    train_strings = [text for entry in dataset for text in (entry.positive, entry.negative)]
    hidden_states = batched_get_hiddens(
        model,
        tokenizer,
        train_strings,
        [hidden_layer],
        batch_size=batch_size,
    )
    layer_hiddens = np.asarray(hidden_states[hidden_layer], dtype=np.float32)
    train_matrix = layer_hiddens[::2].astype(np.float64) - layer_hiddens[1::2].astype(np.float64)
    direction = compute_pca_direction(train_matrix)
    direction = align_direction_sign(layer_hiddens, direction)
    projections = project_onto_direction_safe(layer_hiddens, direction)
    return direction, projections


def prepare_output_dir(path: Path, overwrite: bool) -> None:
    if path.exists() and any(path.iterdir()) and not overwrite:
        raise FileExistsError(
            f"output directory already exists and is not empty: {path}. Use --overwrite to replace artifacts."
        )
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    text = "\n".join(json.dumps(row, ensure_ascii=True) for row in rows) + "\n"
    path.write_text(text, encoding="utf-8")


def write_readme(path: Path, summary: dict[str, Any]) -> None:
    readme_lines = [
        "# Creativity Direction Smoke",
        "",
        f"- Generated at: `{summary['created_at']}`",
        f"- Model: `{summary['model_id']}`",
        f"- Device: `{summary['device']}`",
        f"- Hidden layer: `{summary['hidden_layer']}`",
        f"- Pair count: `{summary['pair_count']}`",
        f"- Vector norm: `{summary['vector_norm']:.6f}`",
        f"- Positive mean projection: `{summary['positive_mean_projection']:.6f}`",
        f"- Negative mean projection: `{summary['negative_mean_projection']:.6f}`",
        f"- Mean margin: `{summary['mean_margin']:.6f}`",
        f"- Positive > negative fraction: `{summary['positive_gt_negative_fraction']:.6f}`",
        "",
        "Artifacts:",
        "- `summary.json`",
        "- `pair_details.jsonl`",
        f"- `direction_layer{summary['hidden_layer']}.npy`",
    ]
    path.write_text("\n".join(readme_lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir or default_output_dir(args.hidden_layer)
    prepare_output_dir(output_dir, overwrite=args.overwrite)

    prompt_rows = load_prompt_rows(args.split_path, max_pairs=args.max_pairs)
    templates = load_templates(args.templates_path)
    dataset = build_contrastive_dataset(prompt_rows, templates)
    device = select_device(args.device)
    model, tokenizer = load_model_and_tokenizer(args.model_id, device)
    direction, projections = train_direction_and_projections(
        model=model,
        tokenizer=tokenizer,
        dataset=dataset,
        hidden_layer=args.hidden_layer,
        batch_size=args.batch_size,
    )
    summary = summarize_pairwise_projections(prompt_rows, projections)
    summary.update(
        {
            "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "model_id": args.model_id,
            "device": device,
            "hidden_layer": args.hidden_layer,
            "batch_size": args.batch_size,
            "vector_norm": float(np.linalg.norm(direction)),
            "split_path": str(args.split_path.relative_to(ROOT)),
            "templates_path": str(args.templates_path.relative_to(ROOT)),
            "direction_path": f"direction_layer{args.hidden_layer}.npy",
        }
    )

    write_json(output_dir / "summary.json", summary)
    write_jsonl(output_dir / "pair_details.jsonl", summary["pair_details"])
    np.save(output_dir / f"direction_layer{args.hidden_layer}.npy", direction)
    write_readme(output_dir / "README.md", summary)

    print(f"wrote smoke artifact to {output_dir}")
    print(f"mean margin: {summary['mean_margin']:.6f}")
    print(f"positive > negative fraction: {summary['positive_gt_negative_fraction']:.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
