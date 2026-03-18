# ABOUTME: Verifies the v2 pair audit keeps the most informative wins, losses, and contaminated examples.
# ABOUTME: Prevents the calibration audit from silently biasing toward only positive-looking examples.

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "audit_creativity_response_pairs_v2.py"


def load_audit_module():
    spec = importlib.util.spec_from_file_location(
        "audit_creativity_response_pairs_v2",
        SCRIPT_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module from {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AuditCreativityResponsePairsV2Test(unittest.TestCase):
    def test_select_audit_rows_keeps_strong_wins_losses_and_flagged_rows(self) -> None:
        audit = load_audit_module()
        rows = [
            {"prompt_id": "win1", "margin": 4.0, "negative_meta_marker_score": 0},
            {"prompt_id": "win2", "margin": 3.0, "negative_meta_marker_score": 0},
            {"prompt_id": "loss1", "margin": -5.0, "negative_meta_marker_score": 0},
            {"prompt_id": "loss2", "margin": -2.0, "negative_meta_marker_score": 0},
            {"prompt_id": "flagged", "margin": 1.0, "negative_meta_marker_score": 1},
        ]

        selected = audit.select_audit_rows(
            rows,
            strongest_per_bucket=2,
            flagged_limit=1,
        )

        self.assertEqual(
            ["win1", "win2", "loss1", "loss2", "flagged"],
            [row["prompt_id"] for row in selected],
        )

    def test_summarize_audit_rows_counts_margin_buckets_and_flags(self) -> None:
        audit = load_audit_module()
        rows = [
            {"prompt_id": "win1", "margin": 4.0, "negative_meta_marker_score": 0},
            {"prompt_id": "loss1", "margin": -5.0, "negative_meta_marker_score": 0},
            {"prompt_id": "flagged", "margin": 1.0, "negative_meta_marker_score": 1},
        ]

        summary = audit.summarize_audit_rows(rows)

        self.assertEqual(3, summary["selected_count"])
        self.assertEqual(2, summary["win_count"])
        self.assertEqual(1, summary["loss_count"])
        self.assertEqual(1, summary["negative_meta_flag_count"])


if __name__ == "__main__":
    unittest.main()
