# ABOUTME: Selects a prompt-family-matched signed feature bundle for corrective feature-validation reruns.
# ABOUTME: Scores single-feature interventions on held-out tuning prompts using prompt-grounding and repetition diagnostics.

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import sys
from typing import Any

from sae_lens import SAE
import torch


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from analyze_feature_validation_dropoff import (  # noqa: E402
    compute_prompt_grounding_ratio,
    compute_repetition_rate,
)
from run_creativity_direction_smoke import (  # noqa: E402
    ROOT,
    load_model_and_tokenizer,
    load_prompt_rows,
    load_templates,
    select_device,
    write_json,
)
from run_generation_side_creativity_smoke import build_prompt_text, generate_with_control  # noqa: E402
from run_instruction_tuned_creativity_decomposition_pilot import load_dense_direction_bundle  # noqa: E402
from run_instruction_tuned_creativity_feature_validation_pilot import (  # noqa: E402
    DEFAULT_FEATURE_METHOD,
    DEFAULT_FEATURE_TABLE,
    DEFAULT_MAX_NEW_TOKENS,
    DEFAULT_REFERENCE_SAE_ID,
    DEFAULT_SAE_RELEASE,
    build_feature_direction,
    load_feature_table,
    prepare_output_dir,
)


DEFAULT_MODEL_ID = "google/gemma-3-270m-it"
DEFAULT_WRITING_PAIR_PATH = ROOT / "prompts" / "writing_diversity_tuning_v1.jsonl"
DEFAULT_ASSOCIATION_PAIR_PATH = ROOT / "prompts" / "create_style_association_tuning_v1.jsonl"
DEFAULT_TEMPLATES_PATH = ROOT / "prompts" / "creative_direction_v1_templates.json"
DEFAULT_SWEEP_DIR = ROOT / "results" / "creativity_direction" / "20260319-gemma3-270m-it-layer-sweep-v1-mean-difference"
DEFAULT_CANDIDATE_COUNT_PER_SIGN = 8
DEFAULT_SELECT_COUNT_PER_SIGN = 3
DEFAULT_STEERING_COEFF = 1.0
DEFAULT_SEED = 9070
DEFAULT_REFRESHED_METHOD_ID = "fista_dense_topk_prompt_matched_refresh_v1"


def default_output_dir() -> Path:
    run_date = datetime.now().strftime("%Y%m%d")
    return ROOT / "results" / "feature_decomposition" / f"{run_date}-gemma3-270m-it-bundle-refresh-v1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Select a prompt-family-matched signed bundle for corrective benchmark reruns."
    )
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID)
    parser.add_argument("--writing-pair-path", type=Path, default=DEFAULT_WRITING_PAIR_PATH)
    parser.add_argument("--association-pair-path", type=Path, default=DEFAULT_ASSOCIATION_PAIR_PATH)
    parser.add_argument("--templates-path", type=Path, default=DEFAULT_TEMPLATES_PATH)
    parser.add_argument("--sweep-dir", type=Path, default=DEFAULT_SWEEP_DIR)
    parser.add_argument("--feature-table-path", type=Path, default=DEFAULT_FEATURE_TABLE)
    parser.add_argument("--feature-method", default=DEFAULT_FEATURE_METHOD)
    parser.add_argument("--sae-release", default=DEFAULT_SAE_RELEASE)
    parser.add_argument("--reference-sae-id", default=DEFAULT_REFERENCE_SAE_ID)
    parser.add_argument("--candidate-count-per-sign", type=int, default=DEFAULT_CANDIDATE_COUNT_PER_SIGN)
    parser.add_argument("--select-count-per-sign", type=int, default=DEFAULT_SELECT_COUNT_PER_SIGN)
    parser.add_argument("--steering-coeff", type=float, default=DEFAULT_STEERING_COEFF)
    parser.add_argument("--max-new-tokens", type=int, default=DEFAULT_MAX_NEW_TOKENS)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--refreshed-method-id", default=DEFAULT_REFRESHED_METHOD_ID)
    parser.add_argument("--device", choices=["auto", "mps", "cpu"], default="auto")
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def compute_feature_candidate_score(
    *,
    mean_prompt_grounding_ratio: float,
    mean_repetition_rate: float,
) -> float:
    return float(mean_prompt_grounding_ratio - mean_repetition_rate)


def rank_feature_rows_by_score(rows: list[dict[str, Any]], select_count: int) -> list[dict[str, Any]]:
    ranked = sorted(
        rows,
        key=lambda row: (
            float(row["selection_score"]),
            abs(float(row.get("signed_coefficient", 0.0))),
        ),
        reverse=True,
    )
    return ranked[:select_count]


def build_refreshed_method_payload(
    *,
    positive_rows: list[dict[str, Any]],
    negative_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "top_positive_features": [
            {
                "feature_id": int(row["feature_id"]),
                "signed_coefficient": float(row["signed_coefficient"]),
            }
            for row in positive_rows
        ],
        "top_negative_features": [
            {
                "feature_id": int(row["feature_id"]),
                "signed_coefficient": float(row["signed_coefficient"]),
            }
            for row in negative_rows
        ],
        "nonzero_feature_count": len(positive_rows) + len(negative_rows),
    }


def load_prompt_rows_with_family(path: Path, family_id: str) -> list[dict[str, Any]]:
    raw_rows = load_prompt_rows(path, max_pairs=1000000)
    rows: list[dict[str, Any]] = []
    for row in raw_rows:
        rows.append(
            {
                "family_id": family_id,
                "prompt_id": str(row["prompt_id"]),
                "prompt_text": str(row["prompt_text"]),
            }
        )
    return rows


def score_single_feature_candidate(
    *,
    candidate_row: dict[str, Any],
    hidden_layer: int,
    vector_length: int,
    decoder_matrix,
    prompts: list[dict[str, Any]],
    templates: dict[str, str],
    model,
    tokenizer,
    steering_coeff: float,
    max_new_tokens: int,
    seed: int,
) -> dict[str, Any]:
    direction, _ = build_feature_direction(
        feature_rows=[
            {
                "feature_id": int(candidate_row["feature_id"]),
                "signed_coefficient": float(candidate_row["signed_coefficient"]),
            }
        ],
        vector_length=vector_length,
        decoder_matrix=decoder_matrix,
    )
    grounding_values: list[float] = []
    repetition_values: list[float] = []
    for prompt_index, prompt in enumerate(prompts):
        prompt_text_full = build_prompt_text(
            prompt_text=prompt["prompt_text"],
            prompt_mode="neutral",
            templates=templates,
        )
        completion_text, _ = generate_with_control(
            model,
            tokenizer,
            prompt_text=prompt_text_full,
            hidden_layer=hidden_layer,
            direction=direction,
            steering_coeff=steering_coeff,
            seed=seed + prompt_index,
            max_new_tokens=max_new_tokens,
            normalize_control=True,
        )
        grounding_values.append(
            compute_prompt_grounding_ratio(
                prompt_text=prompt["prompt_text"],
                completion_text=completion_text,
            )
        )
        repetition_values.append(compute_repetition_rate(completion_text))
    mean_prompt_grounding_ratio = float(sum(grounding_values) / len(grounding_values))
    mean_repetition_rate = float(sum(repetition_values) / len(repetition_values))
    selection_score = compute_feature_candidate_score(
        mean_prompt_grounding_ratio=mean_prompt_grounding_ratio,
        mean_repetition_rate=mean_repetition_rate,
    )
    return {
        "feature_id": int(candidate_row["feature_id"]),
        "signed_coefficient": float(candidate_row["signed_coefficient"]),
        "mean_prompt_grounding_ratio": mean_prompt_grounding_ratio,
        "mean_repetition_rate": mean_repetition_rate,
        "selection_score": selection_score,
    }


def main() -> int:
    args = parse_args()
    device = select_device(args.device)
    output_dir = args.output_dir or default_output_dir()
    prepare_output_dir(output_dir, overwrite=args.overwrite)

    templates = load_templates(args.templates_path)
    writing_rows = load_prompt_rows_with_family(args.writing_pair_path, family_id="writing_diversity_tuning")
    association_rows = load_prompt_rows_with_family(
        args.association_pair_path,
        family_id="association_divergent_tuning",
    )
    tuning_rows = writing_rows + association_rows
    if not tuning_rows:
        raise ValueError("no tuning rows loaded")

    hidden_layer, _, _ = load_dense_direction_bundle(args.sweep_dir, hidden_layer=None)
    feature_table_payload = json.loads(args.feature_table_path.read_text(encoding="utf-8"))
    source_method_table = load_feature_table(args.feature_table_path, args.feature_method)
    positive_candidates = source_method_table["top_positive_features"][: args.candidate_count_per_sign]
    negative_candidates = source_method_table["top_negative_features"][: args.candidate_count_per_sign]

    model, tokenizer = load_model_and_tokenizer(args.model_id, device=device)
    sae = SAE.from_pretrained(release=args.sae_release, sae_id=args.reference_sae_id)
    sae = sae.to(device=model.device, dtype=torch.float32)
    sae.eval()
    decoder_matrix = sae.W_dec.detach().cpu().numpy().astype("float32")
    vector_length = decoder_matrix.shape[0]

    positive_scores: list[dict[str, Any]] = []
    for feature_index, candidate in enumerate(positive_candidates):
        positive_scores.append(
            score_single_feature_candidate(
                candidate_row=candidate,
                hidden_layer=hidden_layer,
                vector_length=vector_length,
                decoder_matrix=decoder_matrix,
                prompts=tuning_rows,
                templates=templates,
                model=model,
                tokenizer=tokenizer,
                steering_coeff=args.steering_coeff,
                max_new_tokens=args.max_new_tokens,
                seed=args.seed + feature_index * 1000,
            )
        )

    negative_scores: list[dict[str, Any]] = []
    negative_seed_offset = 100000
    for feature_index, candidate in enumerate(negative_candidates):
        negative_scores.append(
            score_single_feature_candidate(
                candidate_row=candidate,
                hidden_layer=hidden_layer,
                vector_length=vector_length,
                decoder_matrix=decoder_matrix,
                prompts=tuning_rows,
                templates=templates,
                model=model,
                tokenizer=tokenizer,
                steering_coeff=args.steering_coeff,
                max_new_tokens=args.max_new_tokens,
                seed=args.seed + negative_seed_offset + feature_index * 1000,
            )
        )

    selected_positive = rank_feature_rows_by_score(positive_scores, args.select_count_per_sign)
    selected_negative = rank_feature_rows_by_score(negative_scores, args.select_count_per_sign)
    refreshed_method_payload = build_refreshed_method_payload(
        positive_rows=selected_positive,
        negative_rows=selected_negative,
    )

    feature_table_payload[args.refreshed_method_id] = refreshed_method_payload
    refreshed_feature_table_path = output_dir / "feature_tables_refreshed.json"
    refreshed_feature_table_path.write_text(json.dumps(feature_table_payload, indent=2) + "\n", encoding="utf-8")

    summary = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "model_id": args.model_id,
        "device": device,
        "source_feature_method": args.feature_method,
        "refreshed_method_id": args.refreshed_method_id,
        "tuning_prompt_counts": {
            "writing_diversity_tuning": len(writing_rows),
            "association_divergent_tuning": len(association_rows),
            "total": len(tuning_rows),
        },
        "candidate_count_per_sign": args.candidate_count_per_sign,
        "select_count_per_sign": args.select_count_per_sign,
        "steering_coeff": args.steering_coeff,
        "max_new_tokens": args.max_new_tokens,
        "source_feature_table_path": str(args.feature_table_path.resolve()),
        "refreshed_feature_table_path": str(refreshed_feature_table_path.resolve()),
        "selected_positive_features": selected_positive,
        "selected_negative_features": selected_negative,
        "positive_candidate_scores": positive_scores,
        "negative_candidate_scores": negative_scores,
    }
    write_json(output_dir / "summary.json", summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
