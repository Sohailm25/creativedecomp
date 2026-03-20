# ABOUTME: Verifies artifact-based root-cause analysis helpers for benchmark-family bundle-vs-dense dropoff.
# ABOUTME: Prevents diagnostic drift by enforcing deterministic prompt-grounding and condition-delta computations.

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "analyze_feature_validation_dropoff.py"


def load_script_module():
    spec = importlib.util.spec_from_file_location(
        "analyze_feature_validation_dropoff",
        SCRIPT_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module from {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FeatureValidationDropoffAnalysisTest(unittest.TestCase):
    def test_compute_prompt_grounding_ratio(self) -> None:
        script = load_script_module()

        ratio = script.compute_prompt_grounding_ratio(
            prompt_text="A red fox finds a brass key",
            completion_text="The red fox kept the brass key safe.",
        )

        self.assertGreater(ratio, 0.3)

    def test_compute_repetition_rate(self) -> None:
        script = load_script_module()

        repetitive = script.compute_repetition_rate("echo echo echo echo")
        non_repetitive = script.compute_repetition_rate("echo drifts across the valley")

        self.assertGreater(repetitive, non_repetitive)

    def test_extract_bundle_vs_dense_net_wins(self) -> None:
        script = load_script_module()
        payload = {
            "comparison_summaries": [
                {
                    "candidate_condition_id": "bundle_feature_group",
                    "reference_condition_id": "dense_direction",
                    "prompt_grounded_creativity_candidate_win_fraction": 0.2,
                    "prompt_grounded_creativity_reference_win_fraction": 0.5,
                    "coherence_candidate_win_fraction": 0.4,
                    "coherence_reference_win_fraction": 0.4,
                }
            ]
        }

        result = script.extract_bundle_vs_dense_net_wins(payload)

        self.assertAlmostEqual(-0.3, result["prompt_grounded_creativity_net_win"])
        self.assertAlmostEqual(0.0, result["coherence_net_win"])

    def test_summarize_condition_metrics(self) -> None:
        script = load_script_module()
        output_rows = [
            {
                "condition_id": "dense_direction",
                "prompt_text": "forest cat and moonlight",
                "completion_text": "A forest cat walked under moonlight.",
            },
            {
                "condition_id": "bundle_feature_group",
                "prompt_text": "forest cat and moonlight",
                "completion_text": "A cat wandered.",
            },
        ]

        summary = script.summarize_condition_metrics(output_rows)

        self.assertIn("dense_direction", summary)
        self.assertIn("bundle_feature_group", summary)
        self.assertGreater(
            summary["dense_direction"]["mean_prompt_grounding_ratio"],
            summary["bundle_feature_group"]["mean_prompt_grounding_ratio"],
        )

    def test_compute_sensitivity_delta(self) -> None:
        script = load_script_module()
        baseline = {"prompt_grounded_creativity_net_win": -0.3, "coherence_net_win": 0.0}
        low_coeff = {"prompt_grounded_creativity_net_win": -0.2, "coherence_net_win": 0.1}

        delta = script.compute_sensitivity_delta(
            baseline_net_wins=baseline,
            low_coeff_net_wins=low_coeff,
        )

        self.assertAlmostEqual(0.1, delta["prompt_grounded_creativity_net_win_delta"])
        self.assertAlmostEqual(0.1, delta["coherence_net_win_delta"])


if __name__ == "__main__":
    unittest.main()
