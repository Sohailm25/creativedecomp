# ABOUTME: Diagnoses benchmark-family bundle-vs-dense dropoff using locked audit summaries and cached outputs.
# ABOUTME: Produces a bounded root-cause report for prompt-family shift, feature stability symptoms, and scale-sensitivity planning.

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import re
import sys
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from run_creativity_direction_smoke import ROOT, write_json  # noqa: E402


TOKEN_PATTERN = re.compile(r"[a-z0-9']+")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze feature-validation benchmark-family dropoff from existing artifacts."
    )
    parser.add_argument("--writing-artifact-dir", type=Path, required=True)
    parser.add_argument("--writing-audit-summary-path", type=Path, required=True)
    parser.add_argument("--association-artifact-dir", type=Path, required=True)
    parser.add_argument("--association-audit-summary-path", type=Path, required=True)
    parser.add_argument("--writing-low-coeff-audit-summary-path", type=Path, default=None)
    parser.add_argument("--association-low-coeff-audit-summary-path", type=Path, default=None)
    parser.add_argument("--output-path", type=Path, required=True)
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.lower())


def compute_prompt_grounding_ratio(prompt_text: str, completion_text: str) -> float:
    prompt_tokens = set(tokenize(prompt_text))
    if not prompt_tokens:
        return 0.0
    completion_tokens = set(tokenize(completion_text))
    overlap = prompt_tokens & completion_tokens
    return float(len(overlap) / len(prompt_tokens))


def compute_repetition_rate(completion_text: str) -> float:
    tokens = tokenize(completion_text)
    if not tokens:
        return 0.0
    unique_ratio = len(set(tokens)) / len(tokens)
    return float(1.0 - unique_ratio)


def summarize_condition_metrics(output_rows: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in output_rows:
        grouped.setdefault(str(row["condition_id"]), []).append(row)

    summary: dict[str, dict[str, float]] = {}
    for condition_id, rows in grouped.items():
        prompt_grounding_values = [
            compute_prompt_grounding_ratio(
                prompt_text=str(row["prompt_text"]),
                completion_text=str(row["completion_text"]),
            )
            for row in rows
        ]
        repetition_values = [
            compute_repetition_rate(str(row["completion_text"]))
            for row in rows
        ]
        word_count_values = [
            float(len(str(row["completion_text"]).split()))
            for row in rows
        ]
        summary[condition_id] = {
            "sample_count": float(len(rows)),
            "mean_prompt_grounding_ratio": float(sum(prompt_grounding_values) / len(prompt_grounding_values)),
            "mean_repetition_rate": float(sum(repetition_values) / len(repetition_values)),
            "mean_completion_word_count": float(sum(word_count_values) / len(word_count_values)),
        }
    return summary


def extract_bundle_vs_dense_net_wins(audit_summary_payload: dict[str, Any]) -> dict[str, float]:
    for row in audit_summary_payload.get("comparison_summaries", []):
        if (
            str(row.get("candidate_condition_id")) == "bundle_feature_group"
            and str(row.get("reference_condition_id")) == "dense_direction"
        ):
            return {
                "prompt_grounded_creativity_net_win": float(
                    row["prompt_grounded_creativity_candidate_win_fraction"]
                )
                - float(row["prompt_grounded_creativity_reference_win_fraction"]),
                "coherence_net_win": float(row["coherence_candidate_win_fraction"])
                - float(row["coherence_reference_win_fraction"]),
            }
    raise ValueError("missing bundle_feature_group vs dense_direction row in audit summary")


def compute_sensitivity_delta(
    baseline_net_wins: dict[str, float],
    low_coeff_net_wins: dict[str, float],
) -> dict[str, float]:
    return {
        "prompt_grounded_creativity_net_win_delta": low_coeff_net_wins[
            "prompt_grounded_creativity_net_win"
        ]
        - baseline_net_wins["prompt_grounded_creativity_net_win"],
        "coherence_net_win_delta": low_coeff_net_wins["coherence_net_win"]
        - baseline_net_wins["coherence_net_win"],
    }


def load_output_rows(artifact_dir: Path) -> list[dict[str, Any]]:
    generated_path = artifact_dir / "generated_outputs.jsonl"
    outputs_path = artifact_dir / "outputs.jsonl"
    if generated_path.exists():
        return load_jsonl(generated_path)
    return load_jsonl(outputs_path)


def compute_bundle_dense_deltas(condition_summary: dict[str, dict[str, float]]) -> dict[str, float]:
    if "bundle_feature_group" not in condition_summary or "dense_direction" not in condition_summary:
        raise ValueError("condition summary must contain bundle_feature_group and dense_direction")
    bundle = condition_summary["bundle_feature_group"]
    dense = condition_summary["dense_direction"]
    return {
        "prompt_grounding_delta": bundle["mean_prompt_grounding_ratio"] - dense["mean_prompt_grounding_ratio"],
        "repetition_delta": bundle["mean_repetition_rate"] - dense["mean_repetition_rate"],
        "word_count_delta": bundle["mean_completion_word_count"] - dense["mean_completion_word_count"],
    }


def path_for_summary(path: Path) -> str:
    resolved = path.resolve()
    if resolved.is_relative_to(ROOT):
        return str(resolved.relative_to(ROOT))
    return str(resolved)


def analyze_family(
    family_id: str,
    artifact_dir: Path,
    audit_summary_path: Path,
    low_coeff_audit_summary_path: Path | None = None,
) -> dict[str, Any]:
    output_rows = load_output_rows(artifact_dir)
    condition_summary = summarize_condition_metrics(output_rows)
    bundle_dense_deltas = compute_bundle_dense_deltas(condition_summary)
    audit_summary = load_json(audit_summary_path)
    audit_net_wins = extract_bundle_vs_dense_net_wins(audit_summary)
    low_coeff_section: dict[str, Any] | None = None
    if low_coeff_audit_summary_path is not None:
        low_coeff_summary = load_json(low_coeff_audit_summary_path)
        low_coeff_net_wins = extract_bundle_vs_dense_net_wins(low_coeff_summary)
        low_coeff_section = {
            "audit_summary_path": path_for_summary(low_coeff_audit_summary_path),
            "audit_net_wins": low_coeff_net_wins,
            "net_win_deltas_vs_baseline": compute_sensitivity_delta(
                baseline_net_wins=audit_net_wins,
                low_coeff_net_wins=low_coeff_net_wins,
            ),
        }
    return {
        "family_id": family_id,
        "artifact_dir": path_for_summary(artifact_dir),
        "audit_summary_path": path_for_summary(audit_summary_path),
        "audit_net_wins": audit_net_wins,
        "condition_metrics": condition_summary,
        "bundle_dense_condition_deltas": bundle_dense_deltas,
        "diagnostic_flags": {
            "bundle_under_dense_on_creativity": audit_net_wins["prompt_grounded_creativity_net_win"] < 0.0,
            "bundle_under_dense_on_coherence": audit_net_wins["coherence_net_win"] < 0.0,
            "bundle_lower_prompt_grounding": bundle_dense_deltas["prompt_grounding_delta"] < 0.0,
            "bundle_higher_repetition": bundle_dense_deltas["repetition_delta"] > 0.0,
        },
        "low_coeff_sensitivity": low_coeff_section,
    }


def build_root_cause_summary(family_rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "family_count": len(family_rows),
        "creativity_dropoff_family_count": sum(
            bool(row["diagnostic_flags"]["bundle_under_dense_on_creativity"]) for row in family_rows
        ),
        "coherence_dropoff_family_count": sum(
            bool(row["diagnostic_flags"]["bundle_under_dense_on_coherence"]) for row in family_rows
        ),
        "lower_prompt_grounding_family_count": sum(
            bool(row["diagnostic_flags"]["bundle_lower_prompt_grounding"]) for row in family_rows
        ),
        "higher_repetition_family_count": sum(
            bool(row["diagnostic_flags"]["bundle_higher_repetition"]) for row in family_rows
        ),
    }


def main() -> int:
    args = parse_args()
    family_rows = [
        analyze_family(
            family_id="writing_diversity_family",
            artifact_dir=args.writing_artifact_dir,
            audit_summary_path=args.writing_audit_summary_path,
            low_coeff_audit_summary_path=args.writing_low_coeff_audit_summary_path,
        ),
        analyze_family(
            family_id="association_divergent_family",
            artifact_dir=args.association_artifact_dir,
            audit_summary_path=args.association_audit_summary_path,
            low_coeff_audit_summary_path=args.association_low_coeff_audit_summary_path,
        ),
    ]

    payload = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "families": family_rows,
        "root_cause_summary": build_root_cause_summary(family_rows),
        "recommended_minimum_corrective_experiment": (
            "rerun bundle-vs-dense with prompt-family-matched feature selection and a bounded "
            "coefficient sensitivity slice before any claim upgrade."
        ),
    }
    args.output_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(args.output_path, payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
