from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
import sys
from typing import Any

import numpy as np
from sae_lens import SAE
import torch

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from run_creativity_direction_smoke import (
    DEFAULT_BATCH_SIZE,
    ROOT,
    load_model_and_tokenizer,
    load_prompt_rows,
    load_templates,
    select_device,
    write_json,
    write_jsonl,
)
from run_generation_side_creativity_smoke import (
    build_prompt_text,
    generate_with_control,
    summarize_outputs,
)
from run_instruction_tuned_creativity_decomposition_pilot import (
    DEFAULT_PAIR_PATH as _,
    decode_feature_coefficients,
    load_dense_direction_bundle,
    normalize_feature_coefficients,
)

DEFAULT_PAIR_PATH = ROOT / "prompts" / "creative_direction_it_v1_pilot_pairs.jsonl"
DEFAULT_TEMPLATES_PATH = ROOT / "prompts" / "creative_direction_v1_templates.json"
DEFAULT_SWEPT_DIRECTION = ROOT / "results" / "creativity_direction" / "20260319-gemma3-270m-it-layer-sweep-v1-mean-difference"
DEFAULT_FEATURE_TABLE = (
    ROOT / "results" / "feature_decomposition" / "20260319-gemma3-270m-it-signed-decomposition-pilot-v1" / "feature_tables.json"
)
DEFAULT_SAE_RELEASE = "gemma-scope-2-270m-it-res"
DEFAULT_REFERENCE_SAE_ID = "layer_12_width_16k_l0_medium"
DEFAULT_FEATURE_METHOD = "fista_dense_topk"
DEFAULT_MAX_PROMPTS = 6
DEFAULT_MAX_NEW_TOKENS = 96
DEFAULT_STEERING_COEFF = 1.0
DEFAULT_BUNDLE_POSITIVE_COUNT = 3
DEFAULT_BUNDLE_NEGATIVE_COUNT = 3
DEFAULT_SEED = 8200


def default_output_dir() -> Path:
    run_date = datetime.now().strftime("%Y%m%d")
    return ROOT / "results" / "feature_validation" / f"{run_date}-gemma3-270m-it-feature-validation-v1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a bounded instruction-tuned creativity feature-validation pilot with the frozen signed bundle."
    )
    parser.add_argument("--model-id", default="google/gemma-3-270m-it")
    parser.add_argument("--pair-path", type=Path, default=DEFAULT_PAIR_PATH)
    parser.add_argument("--templates-path", type=Path, default=DEFAULT_TEMPLATES_PATH)
    parser.add_argument("--sweep-dir", type=Path, default=DEFAULT_SWEPT_DIRECTION)
    parser.add_argument("--feature-table-path", type=Path, default=DEFAULT_FEATURE_TABLE)
    parser.add_argument("--feature-method", default=DEFAULT_FEATURE_METHOD)
    parser.add_argument("--sae-release", default=DEFAULT_SAE_RELEASE)
    parser.add_argument("--reference-sae-id", default=DEFAULT_REFERENCE_SAE_ID)
    parser.add_argument("--max-prompts", type=int, default=DEFAULT_MAX_PROMPTS)
    parser.add_argument("--max-new-tokens", type=int, default=DEFAULT_MAX_NEW_TOKENS)
    parser.add_argument("--steering-coeff", type=float, default=DEFAULT_STEERING_COEFF)
    parser.add_argument("--bundle-positive-count", type=int, default=DEFAULT_BUNDLE_POSITIVE_COUNT)
    parser.add_argument("--bundle-negative-count", type=int, default=DEFAULT_BUNDLE_NEGATIVE_COUNT)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--device", choices=["auto", "mps", "cpu"], default="auto")
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def prepare_output_dir(path: Path, overwrite: bool) -> None:
    if path.exists() and any(path.iterdir()) and not overwrite:
        raise FileExistsError(f"{path} already exists and is not empty; use --overwrite to replace.")
    path.mkdir(parents=True, exist_ok=True)


def load_feature_table(path: Path, method_id: str) -> dict[str, Any]:
    table = json.loads(path.read_text(encoding="utf-8"))
    if method_id not in table:
        raise KeyError(f"method id {method_id!r} not found in feature table {path}")
    return table[method_id]


def build_feature_coefficients(
    feature_rows: list[dict[str, Any]],
    vector_length: int,
) -> np.ndarray:
    coefficients = np.zeros(vector_length, dtype=np.float32)
    for entry in feature_rows:
        idx = int(entry["feature_id"])
        if idx < 0 or idx >= vector_length:
            raise ValueError(f"feature id {idx} out of range [0, {vector_length})")
        coefficients[idx] = float(entry["signed_coefficient"])
    return coefficients


def build_feature_direction(
    feature_rows: list[dict[str, Any]],
    vector_length: int,
    decoder_matrix: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    coefficients = build_feature_coefficients(feature_rows, vector_length)
    normalized = normalize_feature_coefficients(coefficients, decoder_matrix)
    direction = decode_feature_coefficients(normalized, decoder_matrix)
    return direction.astype(np.float32), normalized


def build_bundle_rows(
    positive_rows: list[dict[str, Any]],
    negative_rows: list[dict[str, Any]],
    positive_count: int,
    negative_count: int,
) -> list[dict[str, Any]]:
    bundle: list[dict[str, Any]] = []
    bundle.extend(positive_rows[:positive_count])
    bundle.extend(negative_rows[:negative_count])
    return bundle


def build_feature_conditions(
    hidden_layer: int,
    decoder_matrix: np.ndarray,
    vector_length: int,
    feature_table: dict[str, Any],
    positive_count: int,
    negative_count: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    positive_rows = feature_table["top_positive_features"]
    negative_rows = feature_table["top_negative_features"]
    bundle_rows = build_bundle_rows(positive_rows, negative_rows, positive_count, negative_count)

    conditions: list[dict[str, Any]] = []
    metadata: dict[str, Any] = {
        "positive_feature_id": int(positive_rows[0]["feature_id"]) if positive_rows else None,
        "negative_feature_id": int(negative_rows[0]["feature_id"]) if negative_rows else None,
        "bundle_feature_ids": [
            int(entry["feature_id"]) for entry in bundle_rows
        ],
    }

    if positive_rows:
        direction, normalized = build_feature_direction(
            [positive_rows[0]],
            vector_length,
            decoder_matrix,
        )
        conditions.append(
            {
                "condition_id": f"positive_feature_{metadata['positive_feature_id']}",
                "prompt_mode": "neutral",
                "hidden_layer": hidden_layer,
                "direction": direction,
                "normalized_coefficients": normalized,
                "description": "top positive signed SAE feature",
            }
        )
    if negative_rows:
        direction, normalized = build_feature_direction(
            [negative_rows[0]],
            vector_length,
            decoder_matrix,
        )
        conditions.append(
            {
                "condition_id": f"negative_feature_{metadata['negative_feature_id']}",
                "prompt_mode": "neutral",
                "hidden_layer": hidden_layer,
                "direction": direction,
                "normalized_coefficients": normalized,
                "description": "top negative signed SAE feature",
            }
        )

    if bundle_rows:
        direction, normalized = build_feature_direction(
            bundle_rows,
            vector_length,
            decoder_matrix,
        )
        conditions.append(
            {
                "condition_id": "bundle_feature_group",
                "prompt_mode": "neutral",
                "hidden_layer": hidden_layer,
                "direction": direction,
                "normalized_coefficients": normalized,
                "description": "bundle of top positive and negative SAE features",
            }
        )

    return conditions, metadata


def write_readme(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Instruction-Tuned Creativity Feature Validation Pilot",
        "",
        f"- Generated at: `{summary['created_at']}`",
        f"- Model: `{summary['model_id']}`",
        f"- Device: `{summary['device']}`",
        f"- SAE release: `{summary['sae_release']}`",
        f"- Reference SAE id: `{summary['reference_sae']['sae_id']}`",
        f"- Hidden layer: `{summary['hidden_layer']}`",
        f"- Prompt count: `{summary['prompt_count']}`",
        f"- Steering coefficient: `{summary['steering_coeff']}`",
        f"- Positive feature id: `{summary['feature_metadata']['positive_feature_id']}`",
        f"- Negative feature id: `{summary['feature_metadata']['negative_feature_id']}`",
        f"- Bundle features: `{summary['feature_metadata']['bundle_feature_ids']}`",
        "",
        "Conditions:",
    ]
    for row in summary["conditions"]:
        lines.append(
            f"- `{row['condition_id']}`: {row['description']} (hidden_layer={row['hidden_layer']}, coeff={row['steering_coeff']})"
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
    device = select_device(args.device)
    output_dir = args.output_dir or default_output_dir()
    prepare_output_dir(output_dir, overwrite=args.overwrite)

    prompt_rows = load_prompt_rows(args.pair_path, max_pairs=args.max_prompts)
    templates = load_templates(args.templates_path)

    hidden_layer, dense_direction, _ = load_dense_direction_bundle(args.sweep_dir, hidden_layer=None)
    feature_table = load_feature_table(args.feature_table_path, args.feature_method)

    model, tokenizer = load_model_and_tokenizer(args.model_id, device=device)
    sae = SAE.from_pretrained(release=args.sae_release, sae_id=args.reference_sae_id)
    sae = sae.to(device=model.device, dtype=torch.float32)
    sae.eval()
    decoder_matrix = sae.W_dec.detach().cpu().numpy().astype(np.float32)
    vector_length = decoder_matrix.shape[0]

    conditions, metadata = build_feature_conditions(
        hidden_layer=hidden_layer,
        decoder_matrix=decoder_matrix,
        vector_length=vector_length,
        feature_table=feature_table,
        positive_count=args.bundle_positive_count,
        negative_count=args.bundle_negative_count,
    )

    dense_condition = {
        "condition_id": "dense_direction",
        "prompt_mode": "neutral",
        "hidden_layer": hidden_layer,
        "direction": dense_direction.astype(np.float32),
        "normalized_coefficients": None,
        "description": "original dense creativity direction",
    }
    conditions.insert(0, dense_condition)

    output_rows: list[dict[str, Any]] = []
    for prompt_index, prompt_row in enumerate(prompt_rows):
        for condition_index, condition in enumerate(conditions):
            prompt_text = build_prompt_text(
                prompt_text=str(prompt_row["prompt_text"]),
                prompt_mode=str(condition["prompt_mode"]),
                templates=templates,
            )
            seed = args.seed + prompt_index * 100 + condition_index
            completion_text, full_text = generate_with_control(
                model,
                tokenizer,
                prompt_text=prompt_text,
                hidden_layer=int(condition["hidden_layer"]),
                direction=np.asarray(condition["direction"], dtype=np.float32),
                steering_coeff=args.steering_coeff,
                seed=seed,
                max_new_tokens=args.max_new_tokens,
                normalize_control=True,
            )
            output_rows.append(
                {
                    "prompt_id": prompt_row["prompt_id"],
                    "condition_id": condition["condition_id"],
                    "description": condition["description"],
                    "seed": seed,
                    "prompt_text": prompt_row["prompt_text"],
                    "prompt_text_full": prompt_text,
                    "completion_text": completion_text,
                    "full_text": full_text,
                    "completion_word_count": len(completion_text.split()),
                    "completion_char_count": len(completion_text),
                }
            )

    summary = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "model_id": args.model_id,
        "device": device,
        "sae_release": args.sae_release,
        "reference_sae": {"sae_id": args.reference_sae_id},
        "hidden_layer": hidden_layer,
        "prompt_count": len(prompt_rows),
        "steering_coeff": args.steering_coeff,
        "max_new_tokens": args.max_new_tokens,
        "seed": args.seed,
        "templates_path": str(args.templates_path),
        "sweep_dir": str(args.sweep_dir),
        "feature_method": args.feature_method,
        "feature_table_path": str(args.feature_table_path),
        "feature_metadata": metadata,
        "conditions": [
            {
                "condition_id": row["condition_id"],
                "description": row["description"],
                "hidden_layer": row["hidden_layer"],
                "steering_coeff": args.steering_coeff,
            }
            for row in conditions
        ],
        "condition_summaries": summarize_outputs(output_rows),
        "outputs_path": "outputs.jsonl",
    }

    summary_path = output_dir / "summary.json"
    outputs_path = output_dir / "outputs.jsonl"
    write_json(summary_path, summary)
    write_jsonl(outputs_path, output_rows)
    write_readme(output_dir / "README.md", summary)

    print(f"wrote feature validation artifact to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
