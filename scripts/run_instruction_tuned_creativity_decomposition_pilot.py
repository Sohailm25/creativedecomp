# ABOUTME: Compares two legal signed decomposition methods for the matched instruction-tuned creativity direction on the frozen pilot slice.
# ABOUTME: Evaluates contrastive SAE latents and FISTA-style signed sparse coding against matched random-feature controls before any confirmatory method freeze.

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
from repeng.extract import batched_get_hiddens
from sae_lens import SAE
import torch


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from run_creativity_direction_layer_sweep import compute_margin_zscore  # noqa: E402
from run_creativity_direction_smoke import (  # noqa: E402
    ROOT,
    DEFAULT_BATCH_SIZE,
    align_direction_sign,
    load_model_and_tokenizer,
    project_onto_direction_safe,
    select_device,
    summarize_pairwise_projections,
    write_json,
    write_jsonl,
)
from run_instruction_tuned_creativity_replication import (  # noqa: E402
    DEFAULT_MODEL_ID,
    DEFAULT_SAE_RELEASE,
    DEFAULT_REFERENCE_SAE_ID,
    build_contrastive_dataset,
    load_pair_templates,
)
from run_instruction_tuned_refusal_pivot import load_reference_sae_summary  # noqa: E402


DEFAULT_PAIR_PATH = ROOT / "prompts" / "creative_direction_it_v1_pilot_pairs.jsonl"
DEFAULT_TEMPLATES_PATH = ROOT / "prompts" / "creative_direction_it_v1_templates.json"
DEFAULT_SWEEP_DIR = ROOT / "results" / "creativity_direction" / "20260319-gemma3-270m-it-layer-sweep-v1-mean-difference"
DEFAULT_TOP_K = 32
DEFAULT_RANDOM_CONTROL_SAMPLES = 16
DEFAULT_FEATURE_SUMMARY_COUNT = 16
DEFAULT_FISTA_L1_ALPHA = 0.002
DEFAULT_FISTA_MAX_STEPS = 400
DEFAULT_FISTA_TOLERANCE = 1e-6
DEFAULT_SEED = 20260319


def default_output_dir() -> Path:
    run_date = datetime.now().strftime("%Y%m%d")
    return ROOT / "results" / "feature_decomposition" / f"{run_date}-gemma3-270m-it-signed-decomposition-pilot-v1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare legal signed decomposition methods on the matched instruction-tuned creativity pilot slice."
    )
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID)
    parser.add_argument("--pair-path", type=Path, default=DEFAULT_PAIR_PATH)
    parser.add_argument("--templates-path", type=Path, default=DEFAULT_TEMPLATES_PATH)
    parser.add_argument("--sweep-dir", type=Path, default=DEFAULT_SWEEP_DIR)
    parser.add_argument("--sae-release", default=DEFAULT_SAE_RELEASE)
    parser.add_argument("--reference-sae-id", default=DEFAULT_REFERENCE_SAE_ID)
    parser.add_argument("--hidden-layer", type=int, default=None)
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K)
    parser.add_argument("--feature-summary-count", type=int, default=DEFAULT_FEATURE_SUMMARY_COUNT)
    parser.add_argument("--random-control-samples", type=int, default=DEFAULT_RANDOM_CONTROL_SAMPLES)
    parser.add_argument("--fista-l1-alpha", type=float, default=DEFAULT_FISTA_L1_ALPHA)
    parser.add_argument("--fista-max-steps", type=int, default=DEFAULT_FISTA_MAX_STEPS)
    parser.add_argument("--fista-tolerance", type=float, default=DEFAULT_FISTA_TOLERANCE)
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--device", choices=["auto", "mps", "cpu"], default="auto")
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def prepare_output_dir(path: Path, overwrite: bool) -> None:
    if path.exists() and any(path.iterdir()) and not overwrite:
        raise FileExistsError(
            f"output directory already exists and is not empty: {path}. Use --overwrite to replace artifacts."
        )
    path.mkdir(parents=True, exist_ok=True)


def path_for_summary(path: Path) -> str:
    absolute_path = path if path.is_absolute() else (ROOT / path)
    return str(absolute_path.resolve().relative_to(ROOT))


def load_pair_rows(path: Path) -> list[dict[str, Any]]:
    rows = [
        json_row
        for json_row in (
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    ]
    if not rows:
        raise ValueError(f"no pair rows found in {path}")
    return rows


def load_dense_direction_bundle(sweep_dir: Path, hidden_layer: int | None) -> tuple[int, np.ndarray, dict[str, Any]]:
    summary = json.loads((sweep_dir / "summary.json").read_text(encoding="utf-8"))
    selected_layer = int(summary["best_layer"] if hidden_layer is None else hidden_layer)
    with np.load(sweep_dir / "directions.npz") as archive:
        key = f"layer_{selected_layer}"
        if key not in archive:
            raise KeyError(f"missing dense direction for layer {selected_layer} in {sweep_dir / 'directions.npz'}")
        dense_direction = archive[key].astype(np.float32)
    return selected_layer, dense_direction, summary


def keep_top_k_signed(coefficients: np.ndarray, top_k: int) -> np.ndarray:
    if top_k <= 0:
        raise ValueError("top_k must be positive")
    flat = np.asarray(coefficients, dtype=np.float32)
    if flat.ndim != 1:
        raise ValueError(f"expected 1D coefficients but got shape {flat.shape}")
    if top_k >= flat.shape[0]:
        return flat.copy()
    sparse = np.zeros_like(flat)
    top_indices = np.argsort(np.abs(flat))[-top_k:]
    sparse[top_indices] = flat[top_indices]
    return sparse


def soft_threshold(values: np.ndarray, threshold: float) -> np.ndarray:
    return np.sign(values) * np.maximum(np.abs(values) - threshold, 0.0)


def run_fista_signed_sparse_coding(
    *,
    target_direction: np.ndarray,
    decoder_matrix: np.ndarray,
    l1_alpha: float,
    max_steps: int,
    tolerance: float,
) -> np.ndarray:
    target = np.asarray(target_direction, dtype=np.float32)
    decoder = np.asarray(decoder_matrix, dtype=np.float32)
    if target.ndim != 1:
        raise ValueError(f"expected 1D target direction but got shape {target.shape}")
    if decoder.ndim != 2:
        raise ValueError(f"expected 2D decoder matrix but got shape {decoder.shape}")
    if decoder.shape[1] != target.shape[0]:
        raise ValueError(
            f"decoder matrix last dimension {decoder.shape[1]} does not match target size {target.shape[0]}"
        )
    decoder_tensor = torch.from_numpy(decoder).to(device="cpu", dtype=torch.float32)
    target_tensor = torch.from_numpy(target).to(device="cpu", dtype=torch.float32)
    gram = decoder_tensor.T @ decoder_tensor
    lipschitz = float(torch.linalg.eigvalsh(gram).max().item())
    if lipschitz <= 0.0:
        raise ValueError("decoder matrix has non-positive Lipschitz constant")
    previous = torch.zeros(decoder.shape[0], dtype=torch.float32)
    current = previous.clone()
    momentum = 1.0
    for _ in range(max_steps):
        reconstruction = current @ decoder_tensor
        gradient = (reconstruction - target_tensor) @ decoder_tensor.T
        updated = torch.sign(current - (gradient / lipschitz)) * torch.clamp(
            torch.abs(current - (gradient / lipschitz)) - (l1_alpha / lipschitz),
            min=0.0,
        )
        if float(torch.linalg.norm(updated - previous).item()) <= tolerance:
            return updated.detach().cpu().numpy().astype(np.float32)
        next_momentum = 0.5 * (1.0 + np.sqrt(1.0 + 4.0 * momentum * momentum))
        current = updated + ((momentum - 1.0) / next_momentum) * (updated - previous)
        previous = updated
        momentum = next_momentum
    return previous.detach().cpu().numpy().astype(np.float32)


def decode_feature_coefficients(coefficients: np.ndarray, decoder_matrix: np.ndarray) -> np.ndarray:
    coefficient_tensor = torch.from_numpy(np.asarray(coefficients, dtype=np.float32)).to(dtype=torch.float64)
    decoder_tensor = torch.from_numpy(np.asarray(decoder_matrix, dtype=np.float32)).to(dtype=torch.float64)
    return torch.matmul(coefficient_tensor, decoder_tensor).detach().cpu().numpy().astype(np.float32)


def normalize_feature_coefficients(coefficients: np.ndarray, decoder_matrix: np.ndarray) -> np.ndarray:
    decoded = decode_feature_coefficients(coefficients, decoder_matrix)
    decoded_norm = float(np.linalg.norm(decoded))
    if decoded_norm == 0.0:
        raise ValueError("decoded feature bundle has zero norm")
    return (np.asarray(coefficients, dtype=np.float32) / decoded_norm).astype(np.float32)


def build_random_feature_control(
    coefficients: np.ndarray,
    *,
    seed: int,
    candidate_feature_count: int,
) -> np.ndarray:
    flat = np.asarray(coefficients, dtype=np.float32)
    if flat.ndim != 1:
        raise ValueError(f"expected 1D coefficients but got shape {flat.shape}")
    nonzero_indices = np.flatnonzero(flat)
    if nonzero_indices.size == 0:
        raise ValueError("cannot build a random control from an all-zero coefficient vector")
    if candidate_feature_count < flat.shape[0]:
        raise ValueError("candidate_feature_count cannot be smaller than the coefficient vector length")
    rng = np.random.default_rng(seed)
    forbidden = set(int(index) for index in nonzero_indices.tolist())
    available_indices = [index for index in range(candidate_feature_count) if index not in forbidden]
    if len(available_indices) < nonzero_indices.size:
        raise ValueError("not enough alternate feature ids to build a random control")
    target_indices = rng.choice(np.asarray(available_indices, dtype=np.int64), size=nonzero_indices.size, replace=False)
    coefficient_values = flat[nonzero_indices].copy()
    rng.shuffle(coefficient_values)
    randomized = np.zeros_like(flat)
    randomized[target_indices] = coefficient_values
    return randomized


def extract_top_signed_features(coefficients: np.ndarray, top_n: int) -> dict[str, list[dict[str, Any]]]:
    flat = np.asarray(coefficients, dtype=np.float32)
    positive_indices = np.flatnonzero(flat > 0.0)
    negative_indices = np.flatnonzero(flat < 0.0)
    positive_rank = positive_indices[np.argsort(flat[positive_indices])[::-1]]
    negative_rank = negative_indices[np.argsort(flat[negative_indices])]
    return {
        "top_positive_features": [
            {"feature_id": int(index), "signed_coefficient": float(flat[index])}
            for index in positive_rank[:top_n]
        ],
        "top_negative_features": [
            {"feature_id": int(index), "signed_coefficient": float(flat[index])}
            for index in negative_rank[:top_n]
        ],
    }


def build_pair_metric_row(
    *,
    method_id: str,
    decoded_direction: np.ndarray,
    dense_direction: np.ndarray,
    prompt_rows: list[dict[str, Any]],
    layer_hiddens: np.ndarray,
    nonzero_feature_count: int,
) -> dict[str, Any]:
    aligned_direction = align_direction_sign(layer_hiddens, decoded_direction)
    projections = project_onto_direction_safe(layer_hiddens, aligned_direction)
    summary = summarize_pairwise_projections(prompt_rows, projections)
    margins = np.asarray([detail["margin"] for detail in summary["pair_details"]], dtype=np.float64)
    return {
        "method_id": method_id,
        "pair_count": summary["pair_count"],
        "positive_mean_projection": float(summary["positive_mean_projection"]),
        "negative_mean_projection": float(summary["negative_mean_projection"]),
        "mean_margin": float(summary["mean_margin"]),
        "positive_gt_negative_fraction": float(summary["positive_gt_negative_fraction"]),
        "margin_zscore": float(compute_margin_zscore(margins)),
        "dense_direction_cosine": float(
            np.dot(aligned_direction, dense_direction)
            / (np.linalg.norm(aligned_direction) * np.linalg.norm(dense_direction))
        ),
        "decoded_direction_norm": float(np.linalg.norm(decoded_direction)),
        "nonzero_feature_count": int(nonzero_feature_count),
    }


def summarize_random_controls(
    *,
    base_coefficients: np.ndarray,
    decoder_matrix: np.ndarray,
    dense_direction: np.ndarray,
    prompt_rows: list[dict[str, Any]],
    layer_hiddens: np.ndarray,
    sample_count: int,
    seed: int,
) -> tuple[list[dict[str, Any]], dict[str, float]]:
    rows: list[dict[str, Any]] = []
    for sample_index in range(sample_count):
        randomized = build_random_feature_control(
            base_coefficients,
            seed=seed + sample_index,
            candidate_feature_count=int(base_coefficients.shape[0]),
        )
        normalized = normalize_feature_coefficients(randomized, decoder_matrix)
        decoded_direction = decode_feature_coefficients(normalized, decoder_matrix)
        row = build_pair_metric_row(
            method_id=f"random_control_{sample_index}",
            decoded_direction=decoded_direction,
            dense_direction=dense_direction,
            prompt_rows=prompt_rows,
            layer_hiddens=layer_hiddens,
            nonzero_feature_count=int(np.count_nonzero(normalized)),
        )
        rows.append(row)
    aggregate = {
        "sample_count": float(len(rows)),
        "mean_positive_gt_negative_fraction": float(
            np.mean([row["positive_gt_negative_fraction"] for row in rows], dtype=np.float64)
        ),
        "mean_mean_margin": float(np.mean([row["mean_margin"] for row in rows], dtype=np.float64)),
        "mean_margin_zscore": float(np.mean([row["margin_zscore"] for row in rows], dtype=np.float64)),
        "mean_dense_direction_cosine": float(
            np.mean([row["dense_direction_cosine"] for row in rows], dtype=np.float64)
        ),
        "max_positive_gt_negative_fraction": float(
            np.max([row["positive_gt_negative_fraction"] for row in rows], initial=0.0)
        ),
        "max_dense_direction_cosine": float(
            np.max([row["dense_direction_cosine"] for row in rows], initial=0.0)
        ),
    }
    return rows, aggregate


def build_contrastive_latent_method_bundle(
    *,
    positive_latents: np.ndarray,
    negative_latents: np.ndarray,
    decoder_matrix: np.ndarray,
    top_k: int,
    feature_summary_count: int,
) -> dict[str, Any]:
    mean_latent_delta = positive_latents.mean(axis=0) - negative_latents.mean(axis=0)
    sparse_coefficients = keep_top_k_signed(mean_latent_delta.astype(np.float32), top_k=top_k)
    normalized_coefficients = normalize_feature_coefficients(sparse_coefficients, decoder_matrix)
    decoded_direction = decode_feature_coefficients(normalized_coefficients, decoder_matrix)
    feature_summary = extract_top_signed_features(normalized_coefficients, top_n=feature_summary_count)
    return {
        "method_id": "contrastive_latent_topk",
        "raw_coefficients": sparse_coefficients,
        "normalized_coefficients": normalized_coefficients,
        "decoded_direction": decoded_direction,
        "feature_summary": feature_summary,
    }


def build_fista_method_bundle(
    *,
    dense_direction: np.ndarray,
    decoder_matrix: np.ndarray,
    top_k: int,
    feature_summary_count: int,
    l1_alpha: float,
    max_steps: int,
    tolerance: float,
) -> dict[str, Any]:
    raw_coefficients = run_fista_signed_sparse_coding(
        target_direction=dense_direction,
        decoder_matrix=decoder_matrix,
        l1_alpha=l1_alpha,
        max_steps=max_steps,
        tolerance=tolerance,
    )
    sparse_coefficients = keep_top_k_signed(raw_coefficients, top_k=top_k)
    normalized_coefficients = normalize_feature_coefficients(sparse_coefficients, decoder_matrix)
    decoded_direction = decode_feature_coefficients(normalized_coefficients, decoder_matrix)
    feature_summary = extract_top_signed_features(normalized_coefficients, top_n=feature_summary_count)
    return {
        "method_id": "fista_dense_topk",
        "raw_coefficients": sparse_coefficients,
        "normalized_coefficients": normalized_coefficients,
        "decoded_direction": decoded_direction,
        "feature_summary": feature_summary,
    }


def compute_method_agreement(method_bundles: list[dict[str, Any]]) -> dict[str, Any]:
    if len(method_bundles) != 2:
        raise ValueError("agreement summary currently expects exactly two method bundles")
    lhs = method_bundles[0]
    rhs = method_bundles[1]
    lhs_direction = np.asarray(lhs["decoded_direction"], dtype=np.float64)
    rhs_direction = np.asarray(rhs["decoded_direction"], dtype=np.float64)
    direction_cosine = float(
        np.dot(lhs_direction, rhs_direction)
        / (np.linalg.norm(lhs_direction) * np.linalg.norm(rhs_direction))
    )
    lhs_feature_ids = {
        int(row["feature_id"])
        for key in ("top_positive_features", "top_negative_features")
        for row in lhs["feature_summary"][key]
    }
    rhs_feature_ids = {
        int(row["feature_id"])
        for key in ("top_positive_features", "top_negative_features")
        for row in rhs["feature_summary"][key]
    }
    union_ids = lhs_feature_ids | rhs_feature_ids
    jaccard = 0.0 if not union_ids else float(len(lhs_feature_ids & rhs_feature_ids) / len(union_ids))
    return {
        "decoded_direction_cosine": direction_cosine,
        "feature_jaccard_top_sets": jaccard,
        "lhs_method_id": lhs["method_id"],
        "rhs_method_id": rhs["method_id"],
    }


def choose_recommended_method(method_rows: list[dict[str, Any]], agreement: dict[str, Any]) -> dict[str, Any]:
    ranked_rows = sorted(
        method_rows,
        key=lambda row: (
            float(row["positive_gt_negative_fraction"] - row["random_control_mean_positive_gt_negative_fraction"]),
            float(row["dense_direction_cosine"] - row["random_control_mean_dense_direction_cosine"]),
            float(row["mean_margin"] - row["random_control_mean_margin"]),
        ),
        reverse=True,
    )
    if not ranked_rows:
        raise ValueError("no method rows supplied")
    recommended = ranked_rows[0]
    pilot_freeze_ok = bool(
        agreement["decoded_direction_cosine"] >= 0.65
        and agreement["feature_jaccard_top_sets"] >= 0.10
        and float(recommended["positive_gt_negative_fraction"]) > float(recommended["random_control_mean_positive_gt_negative_fraction"])
        and float(recommended["dense_direction_cosine"]) > float(recommended["random_control_mean_dense_direction_cosine"])
    )
    return {
        "recommended_method_id": str(recommended["method_id"]),
        "pilot_freeze_ok": pilot_freeze_ok,
        "ranking_rule": (
            "rank by pair-separation gain over matched random controls, "
            "then dense-direction cosine gain over matched random controls, "
            "then mean-margin gain over matched random controls"
        ),
    }


def write_readme(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Instruction-Tuned Creativity Signed Decomposition Pilot",
        "",
        f"- Generated at: `{summary['created_at']}`",
        f"- Model: `{summary['model_id']}`",
        f"- Device: `{summary['device']}`",
        f"- SAE release: `{summary['sae_release']}`",
        f"- Reference SAE id: `{summary['reference_sae']['sae_id']}`",
        f"- Hidden layer: `{summary['hidden_layer']}`",
        f"- Pair count: `{summary['pair_count']}`",
        f"- Top-k sparsity budget: `{summary['top_k']}`",
        f"- Random control samples per method: `{summary['random_control_samples']}`",
        f"- Recommended method: `{summary['recommendation']['recommended_method_id']}`",
        f"- Pilot freeze recommendation: `{summary['recommendation']['pilot_freeze_ok']}`",
        "",
        "Method summaries:",
    ]
    for row in summary["method_rows"]:
        lines.append(
            f"- `{row['method_id']}`: fraction `{row['positive_gt_negative_fraction']:.6f}`, "
            f"margin `{row['mean_margin']:.6f}`, dense cosine `{row['dense_direction_cosine']:.6f}`, "
            f"random-fraction mean `{row['random_control_mean_positive_gt_negative_fraction']:.6f}`, "
            f"random-cosine mean `{row['random_control_mean_dense_direction_cosine']:.6f}`"
        )
    lines.extend(
        [
            "",
            "Method agreement:",
            f"- decoded-direction cosine: `{summary['agreement']['decoded_direction_cosine']:.6f}`",
            f"- top-feature jaccard: `{summary['agreement']['feature_jaccard_top_sets']:.6f}`",
            "",
            "Artifacts:",
            "- `summary.json`",
            "- `method_metrics.jsonl`",
            "- `feature_tables.json`",
            "- `random_control_metrics.jsonl`",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    device = select_device(args.device)
    output_dir = args.output_dir or default_output_dir()
    prepare_output_dir(output_dir, overwrite=args.overwrite)

    prompt_rows = load_pair_rows(args.pair_path)
    templates = load_pair_templates(args.templates_path)
    hidden_layer, dense_direction, dense_summary = load_dense_direction_bundle(args.sweep_dir, args.hidden_layer)

    model, tokenizer = load_model_and_tokenizer(args.model_id, device=device)
    dataset = build_contrastive_dataset(prompt_rows, tokenizer, templates)
    contrast_texts = [text for entry in dataset for text in (entry.positive, entry.negative)]
    hidden_state_map = batched_get_hiddens(
        model,
        tokenizer,
        contrast_texts,
        [hidden_layer],
        batch_size=args.batch_size,
    )
    layer_hiddens = np.asarray(hidden_state_map[hidden_layer], dtype=np.float32)
    positive_hiddens = torch.from_numpy(layer_hiddens[::2]).to(device=model.device, dtype=torch.float32)
    negative_hiddens = torch.from_numpy(layer_hiddens[1::2]).to(device=model.device, dtype=torch.float32)

    sae = SAE.from_pretrained(
        release=args.sae_release,
        sae_id=args.reference_sae_id,
    )
    sae = sae.to(device=model.device, dtype=torch.float32)
    sae.eval()
    with torch.no_grad():
        positive_latents = sae.encode(positive_hiddens).detach().cpu().numpy().astype(np.float32)
        negative_latents = sae.encode(negative_hiddens).detach().cpu().numpy().astype(np.float32)
    decoder_matrix = sae.W_dec.detach().cpu().numpy().astype(np.float32)

    method_bundles = [
        build_contrastive_latent_method_bundle(
            positive_latents=positive_latents,
            negative_latents=negative_latents,
            decoder_matrix=decoder_matrix,
            top_k=args.top_k,
            feature_summary_count=args.feature_summary_count,
        ),
        build_fista_method_bundle(
            dense_direction=dense_direction,
            decoder_matrix=decoder_matrix,
            top_k=args.top_k,
            feature_summary_count=args.feature_summary_count,
            l1_alpha=args.fista_l1_alpha,
            max_steps=args.fista_max_steps,
            tolerance=args.fista_tolerance,
        ),
    ]

    method_rows: list[dict[str, Any]] = []
    random_control_rows: list[dict[str, Any]] = []
    feature_tables: dict[str, Any] = {}
    for method_index, bundle in enumerate(method_bundles):
        method_row = build_pair_metric_row(
            method_id=str(bundle["method_id"]),
            decoded_direction=np.asarray(bundle["decoded_direction"], dtype=np.float32),
            dense_direction=np.asarray(dense_direction, dtype=np.float32),
            prompt_rows=prompt_rows,
            layer_hiddens=layer_hiddens,
            nonzero_feature_count=int(np.count_nonzero(bundle["normalized_coefficients"])),
        )
        method_random_rows, random_aggregate = summarize_random_controls(
            base_coefficients=np.asarray(bundle["normalized_coefficients"], dtype=np.float32),
            decoder_matrix=decoder_matrix,
            dense_direction=np.asarray(dense_direction, dtype=np.float32),
            prompt_rows=prompt_rows,
            layer_hiddens=layer_hiddens,
            sample_count=args.random_control_samples,
            seed=args.seed + (method_index * 1000),
        )
        random_control_rows.extend(
            [{"method_id": str(bundle["method_id"]), **row} for row in method_random_rows]
        )
        method_row.update(
            {
                "random_control_mean_positive_gt_negative_fraction": random_aggregate["mean_positive_gt_negative_fraction"],
                "random_control_mean_margin": random_aggregate["mean_mean_margin"],
                "random_control_mean_margin_zscore": random_aggregate["mean_margin_zscore"],
                "random_control_mean_dense_direction_cosine": random_aggregate["mean_dense_direction_cosine"],
                "random_control_max_positive_gt_negative_fraction": random_aggregate["max_positive_gt_negative_fraction"],
                "random_control_max_dense_direction_cosine": random_aggregate["max_dense_direction_cosine"],
            }
        )
        method_rows.append(method_row)
        feature_tables[str(bundle["method_id"])] = {
            **bundle["feature_summary"],
            "nonzero_feature_count": int(np.count_nonzero(bundle["normalized_coefficients"])),
        }

    agreement = compute_method_agreement(method_bundles)
    recommendation = choose_recommended_method(method_rows, agreement)
    reference_sae_summary = load_reference_sae_summary(args.sae_release, args.reference_sae_id)
    summary = {
        "created_at": datetime.now().isoformat(),
        "model_id": args.model_id,
        "device": device,
        "sae_release": args.sae_release,
        "reference_sae": reference_sae_summary,
        "hidden_layer": hidden_layer,
        "pair_count": len(prompt_rows),
        "top_k": args.top_k,
        "random_control_samples": args.random_control_samples,
        "dense_direction_source": path_for_summary(args.sweep_dir / "summary.json"),
        "dense_direction_method": dense_summary["direction_method"],
        "method_rows": method_rows,
        "agreement": agreement,
        "recommendation": recommendation,
        "artifacts": {
            "summary_json": path_for_summary(output_dir / "summary.json"),
            "method_metrics_jsonl": path_for_summary(output_dir / "method_metrics.jsonl"),
            "feature_tables_json": path_for_summary(output_dir / "feature_tables.json"),
            "random_control_metrics_jsonl": path_for_summary(output_dir / "random_control_metrics.jsonl"),
        },
    }
    write_json(output_dir / "summary.json", summary)
    write_jsonl(output_dir / "method_metrics.jsonl", method_rows)
    write_json(output_dir / "feature_tables.json", feature_tables)
    write_jsonl(output_dir / "random_control_metrics.jsonl", random_control_rows)
    write_readme(output_dir / "README.md", summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
