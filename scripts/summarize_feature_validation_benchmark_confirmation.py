# ABOUTME: Aggregates benchmark-family manual-audit summaries for feature-validation bundle-vs-dense confirmation.
# ABOUTME: Enforces a two-family prereg gate before stronger feature-level claim language is allowed.

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import sys
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from run_creativity_direction_smoke import ROOT, write_json  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize two benchmark-family manual audits for feature-validation bundle-vs-dense confirmation."
    )
    parser.add_argument("--association-summary-path", type=Path, required=True)
    parser.add_argument("--writing-summary-path", type=Path, required=True)
    parser.add_argument("--output-path", type=Path, required=True)
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def extract_bundle_vs_dense_row(summary_payload: dict[str, Any]) -> dict[str, Any]:
    for row in summary_payload.get("comparison_summaries", []):
        if (
            str(row.get("candidate_condition_id")) == "bundle_feature_group"
            and str(row.get("reference_condition_id")) == "dense_direction"
        ):
            return row
    raise ValueError("missing bundle_feature_group_vs_dense_direction comparison summary")


def compute_family_confirmation_row(
    family_id: str,
    family_label: str,
    summary_payload: dict[str, Any],
) -> dict[str, Any]:
    row = extract_bundle_vs_dense_row(summary_payload)
    creativity_net = float(row["prompt_grounded_creativity_candidate_win_fraction"]) - float(
        row["prompt_grounded_creativity_reference_win_fraction"]
    )
    coherence_net = float(row["coherence_candidate_win_fraction"]) - float(
        row["coherence_reference_win_fraction"]
    )
    return {
        "family_id": family_id,
        "family_label": family_label,
        "sample_count": int(row["sample_count"]),
        "prompt_grounded_creativity_net_win": creativity_net,
        "coherence_net_win": coherence_net,
        "bundle_beats_dense_on_creativity": creativity_net > 0.0,
        "bundle_nonnegative_on_coherence": coherence_net >= 0.0,
    }


def compute_confirmation_summary(family_rows: list[dict[str, Any]]) -> dict[str, Any]:
    has_minimum_family_count = len(family_rows) >= 2
    per_family_pass = [
        bool(row["bundle_beats_dense_on_creativity"]) and bool(row["bundle_nonnegative_on_coherence"])
        for row in family_rows
    ]
    passes = has_minimum_family_count and all(per_family_pass)
    return {
        "family_count": len(family_rows),
        "has_minimum_family_count": has_minimum_family_count,
        "passes_prereg_two_family_confirmation": passes,
    }


def path_for_summary(path: Path) -> str:
    resolved = path.resolve()
    if resolved.is_relative_to(ROOT):
        return str(resolved.relative_to(ROOT))
    return str(resolved)


def main() -> int:
    args = parse_args()
    association_summary = load_json(args.association_summary_path)
    writing_summary = load_json(args.writing_summary_path)

    family_rows = [
        compute_family_confirmation_row(
            family_id="association_divergent_family",
            family_label="Association / Divergent (CREATE-style)",
            summary_payload=association_summary,
        ),
        compute_family_confirmation_row(
            family_id="writing_diversity_family",
            family_label="Writing / Diversity (WritingPrompts-style)",
            summary_payload=writing_summary,
        ),
    ]

    confirmation_summary = compute_confirmation_summary(family_rows)
    payload = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "association_summary_path": path_for_summary(args.association_summary_path),
        "writing_summary_path": path_for_summary(args.writing_summary_path),
        "family_summaries": family_rows,
        "confirmation": confirmation_summary,
        "claim_boundary": (
            "two_family_manual_audit_confirmation"
            if confirmation_summary["passes_prereg_two_family_confirmation"]
            else "benchmark_family_confirmation_not_met"
        ),
    }
    args.output_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(args.output_path, payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
