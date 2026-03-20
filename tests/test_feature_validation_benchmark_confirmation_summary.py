# ABOUTME: Verifies benchmark-family confirmation aggregation for feature-validation bundle-vs-dense comparisons.
# ABOUTME: Prevents claim upgrades unless two benchmark families agree on prompt-grounded creativity and coherence direction.

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "summarize_feature_validation_benchmark_confirmation.py"


def load_script_module():
    spec = importlib.util.spec_from_file_location(
        "summarize_feature_validation_benchmark_confirmation",
        SCRIPT_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module from {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_family_summary(
    creativity_candidate_win: float,
    creativity_reference_win: float,
    coherence_candidate_win: float,
    coherence_reference_win: float,
) -> dict[str, object]:
    return {
        "comparison_summaries": [
            {
                "comparison_id": "bundle_feature_group_vs_dense_direction",
                "candidate_condition_id": "bundle_feature_group",
                "reference_condition_id": "dense_direction",
                "sample_count": 10,
                "prompt_grounded_creativity_candidate_win_fraction": creativity_candidate_win,
                "prompt_grounded_creativity_reference_win_fraction": creativity_reference_win,
                "prompt_grounded_creativity_tie_fraction": 1.0
                - creativity_candidate_win
                - creativity_reference_win,
                "coherence_candidate_win_fraction": coherence_candidate_win,
                "coherence_reference_win_fraction": coherence_reference_win,
                "coherence_tie_fraction": 1.0 - coherence_candidate_win - coherence_reference_win,
            }
        ]
    }


class FeatureValidationBenchmarkConfirmationSummaryTest(unittest.TestCase):
    def test_extract_bundle_vs_dense_row(self) -> None:
        script = load_script_module()
        payload = build_family_summary(0.7, 0.2, 0.5, 0.4)

        row = script.extract_bundle_vs_dense_row(payload)

        self.assertEqual("bundle_feature_group_vs_dense_direction", row["comparison_id"])

    def test_extract_bundle_vs_dense_row_raises_when_missing(self) -> None:
        script = load_script_module()
        payload = {"comparison_summaries": []}

        with self.assertRaises(ValueError):
            script.extract_bundle_vs_dense_row(payload)

    def test_compute_family_confirmation_row(self) -> None:
        script = load_script_module()
        payload = build_family_summary(0.6, 0.2, 0.4, 0.3)

        row = script.compute_family_confirmation_row(
            family_id="association_family",
            family_label="Association / Divergent",
            summary_payload=payload,
        )

        self.assertEqual("association_family", row["family_id"])
        self.assertAlmostEqual(0.4, row["prompt_grounded_creativity_net_win"])
        self.assertAlmostEqual(0.1, row["coherence_net_win"])
        self.assertTrue(row["bundle_beats_dense_on_creativity"])
        self.assertTrue(row["bundle_nonnegative_on_coherence"])

    def test_compute_confirmation_summary_requires_two_families(self) -> None:
        script = load_script_module()
        rows = [
            {
                "family_id": "association_family",
                "family_label": "Association / Divergent",
                "sample_count": 10,
                "prompt_grounded_creativity_net_win": 0.3,
                "coherence_net_win": 0.2,
                "bundle_beats_dense_on_creativity": True,
                "bundle_nonnegative_on_coherence": True,
            }
        ]

        summary = script.compute_confirmation_summary(rows)

        self.assertFalse(summary["passes_prereg_two_family_confirmation"])

    def test_compute_confirmation_summary_passes_when_both_families_support_bundle(self) -> None:
        script = load_script_module()
        rows = [
            {
                "family_id": "association_family",
                "family_label": "Association / Divergent",
                "sample_count": 10,
                "prompt_grounded_creativity_net_win": 0.3,
                "coherence_net_win": 0.2,
                "bundle_beats_dense_on_creativity": True,
                "bundle_nonnegative_on_coherence": True,
            },
            {
                "family_id": "writing_diversity_family",
                "family_label": "Writing / Diversity",
                "sample_count": 10,
                "prompt_grounded_creativity_net_win": 0.1,
                "coherence_net_win": 0.0,
                "bundle_beats_dense_on_creativity": True,
                "bundle_nonnegative_on_coherence": True,
            },
        ]

        summary = script.compute_confirmation_summary(rows)

        self.assertTrue(summary["passes_prereg_two_family_confirmation"])


if __name__ == "__main__":
    unittest.main()
