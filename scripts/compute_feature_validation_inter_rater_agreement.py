# ABOUTME: Computes inter-rater agreement for locked feature-validation manual-audit annotations.
# ABOUTME: Updates the feature-validation summary with agreement metrics so stronger claims require explicit agreement evidence.

from __future__ import annotations

import argparse
from collections import OrderedDict
from datetime import datetime
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AUDIT_DIR = (
    ROOT
    / "results"
    / "feature_validation"
    / "20260319-gemma3-270m-it-feature-validation-v1-manual-audit"
)
DEFAULT_AXIS_NAMES = ["prompt_grounded_creativity", "coherence"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute inter-rater agreement for feature-validation manual audit annotations."
    )
    parser.add_argument("--audit-dir", type=Path, default=DEFAULT_AUDIT_DIR)
    parser.add_argument("--rater1-path", type=Path, default=None)
    parser.add_argument("--rater2-path", type=Path, default=None)
    parser.add_argument("--answer-key-path", type=Path, default=None)
    parser.add_argument("--summary-path", type=Path, default=None)
    parser.add_argument("--output-path", type=Path, default=None)
    parser.add_argument("--update-summary", action="store_true")
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def normalize_label(raw_value: str) -> str:
    normalized = str(raw_value).strip().lower()
    if normalized in {"a", "b"}:
        return normalized.upper()
    if normalized == "tie":
        return "tie"
    raise ValueError(f"invalid winner label: {raw_value!r}")


def build_annotation_lookup(
    annotation_rows: list[dict[str, Any]],
    axis_names: list[str],
) -> dict[str, dict[str, str]]:
    lookup: dict[str, dict[str, str]] = {}
    for row in annotation_rows:
        pair_id = str(row["audit_pair_id"])
        axis_labels: dict[str, str] = {}
        for axis_name in axis_names:
            axis_labels[f"{axis_name}_winner_label"] = normalize_label(
                str(row[f"{axis_name}_winner_label"])
            )
        lookup[pair_id] = axis_labels
    return lookup


def validate_pair_ids_match(
    rater1_lookup: dict[str, dict[str, str]],
    rater2_lookup: dict[str, dict[str, str]],
) -> None:
    if set(rater1_lookup) != set(rater2_lookup):
        raise ValueError("rater annotation files must contain the exact same audit_pair_id set")


def compute_cohens_kappa(
    rater1_labels: list[str],
    rater2_labels: list[str],
    label_space: list[str],
) -> float:
    if len(rater1_labels) != len(rater2_labels):
        raise ValueError("rater label lists must have equal length")
    if not rater1_labels:
        raise ValueError("need at least one label to compute kappa")

    observed = float(np.mean([left == right for left, right in zip(rater1_labels, rater2_labels)]))
    expected = 0.0
    for label in label_space:
        p1 = float(np.mean([value == label for value in rater1_labels]))
        p2 = float(np.mean([value == label for value in rater2_labels]))
        expected += p1 * p2

    if np.isclose(1.0 - expected, 0.0):
        return 1.0 if np.isclose(observed, 1.0) else 0.0
    return float((observed - expected) / (1.0 - expected))


def summarize_axis_agreement(
    rater1_lookup: dict[str, dict[str, str]],
    rater2_lookup: dict[str, dict[str, str]],
    axis_name: str,
    pair_ids: list[str] | None = None,
) -> dict[str, Any]:
    resolved_pair_ids = sorted(rater1_lookup) if pair_ids is None else sorted(pair_ids)
    label_key = f"{axis_name}_winner_label"
    rater1_labels = [rater1_lookup[pair_id][label_key] for pair_id in resolved_pair_ids]
    rater2_labels = [rater2_lookup[pair_id][label_key] for pair_id in resolved_pair_ids]
    return {
        "sample_count": len(resolved_pair_ids),
        "percent_agreement": float(
            np.mean([left == right for left, right in zip(rater1_labels, rater2_labels)])
        ),
        "cohens_kappa": compute_cohens_kappa(
            rater1_labels=rater1_labels,
            rater2_labels=rater2_labels,
            label_space=["A", "B", "tie"],
        ),
        "rater1_label_distribution": {
            label: float(np.mean([value == label for value in rater1_labels]))
            for label in ["A", "B", "tie"]
        },
        "rater2_label_distribution": {
            label: float(np.mean([value == label for value in rater2_labels]))
            for label in ["A", "B", "tie"]
        },
    }


def summarize_per_comparison_agreement(
    answer_key_rows: list[dict[str, Any]],
    rater1_lookup: dict[str, dict[str, str]],
    rater2_lookup: dict[str, dict[str, str]],
    axis_names: list[str],
) -> list[dict[str, Any]]:
    pair_ids_by_comparison: OrderedDict[str, list[str]] = OrderedDict()
    for row in answer_key_rows:
        comparison_id = str(row["comparison_id"])
        pair_ids_by_comparison.setdefault(comparison_id, []).append(str(row["audit_pair_id"]))

    rows: list[dict[str, Any]] = []
    for comparison_id, pair_ids in pair_ids_by_comparison.items():
        row: dict[str, Any] = {
            "comparison_id": comparison_id,
            "sample_count": len(pair_ids),
        }
        for axis_name in axis_names:
            axis_summary = summarize_axis_agreement(
                rater1_lookup=rater1_lookup,
                rater2_lookup=rater2_lookup,
                axis_name=axis_name,
                pair_ids=pair_ids,
            )
            row[f"{axis_name}_percent_agreement"] = axis_summary["percent_agreement"]
            row[f"{axis_name}_cohens_kappa"] = axis_summary["cohens_kappa"]
        rows.append(row)
    return rows


def path_for_summary(path: Path) -> str:
    resolved = path.resolve()
    if resolved.is_relative_to(ROOT):
        return str(resolved.relative_to(ROOT))
    return str(resolved)


def main() -> int:
    args = parse_args()
    audit_dir = args.audit_dir
    rater1_path = args.rater1_path or (audit_dir / "manual_annotations_locked_v1.jsonl")
    rater2_path = args.rater2_path or (audit_dir / "manual_annotations_locked_rater2_v1.jsonl")
    answer_key_path = args.answer_key_path or (audit_dir / "answer_key.jsonl")
    summary_path = args.summary_path or (audit_dir / "summary.json")
    output_path = args.output_path or (audit_dir / "inter_rater_agreement.json")

    rater1_rows = load_jsonl(rater1_path)
    rater2_rows = load_jsonl(rater2_path)
    answer_key_rows = load_jsonl(answer_key_path)
    rater1_lookup = build_annotation_lookup(rater1_rows, axis_names=DEFAULT_AXIS_NAMES)
    rater2_lookup = build_annotation_lookup(rater2_rows, axis_names=DEFAULT_AXIS_NAMES)
    validate_pair_ids_match(rater1_lookup, rater2_lookup)

    overall_axis_agreement = {
        axis_name: summarize_axis_agreement(
            rater1_lookup=rater1_lookup,
            rater2_lookup=rater2_lookup,
            axis_name=axis_name,
        )
        for axis_name in DEFAULT_AXIS_NAMES
    }
    per_comparison_agreement = summarize_per_comparison_agreement(
        answer_key_rows=answer_key_rows,
        rater1_lookup=rater1_lookup,
        rater2_lookup=rater2_lookup,
        axis_names=DEFAULT_AXIS_NAMES,
    )

    agreement_summary = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "rater1_path": path_for_summary(rater1_path),
        "rater2_path": path_for_summary(rater2_path),
        "answer_key_path": path_for_summary(answer_key_path),
        "sample_count": len(rater1_lookup),
        "axis_names": DEFAULT_AXIS_NAMES,
        "overall_axis_agreement": overall_axis_agreement,
        "per_comparison_agreement": per_comparison_agreement,
    }
    write_json(output_path, agreement_summary)

    if args.update_summary:
        summary_payload = load_json(summary_path)
        summary_payload["inter_rater_agreement"] = agreement_summary
        write_json(summary_path, summary_payload)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
