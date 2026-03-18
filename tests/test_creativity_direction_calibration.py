# ABOUTME: Verifies the bounded v2 calibration harness sweeps steering coefficients without dropping baseline conditions.
# ABOUTME: Prevents the late-layer calibration pass from turning into an untracked one-off generation script.

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "run_creativity_direction_calibration.py"


def load_calibration_module():
    spec = importlib.util.spec_from_file_location(
        "run_creativity_direction_calibration",
        SCRIPT_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module from {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CreativityDirectionCalibrationTest(unittest.TestCase):
    def test_parse_steering_coeffs_argument_preserves_unique_order(self) -> None:
        calibration = load_calibration_module()

        coeffs = calibration.parse_steering_coeffs_argument("-1.0, 0.5, 1.0, 0.5, 2")

        self.assertEqual([-1.0, 0.5, 1.0, 2.0], coeffs)

    def test_build_calibration_conditions_keeps_baselines_and_coeff_sweep(self) -> None:
        calibration = load_calibration_module()

        conditions = calibration.build_calibration_conditions(
            candidate_layers=[24, 20],
            steering_coeffs=[-1.0, 0.5, 1.0],
        )

        self.assertEqual("neutral_unsteered", conditions[0]["condition_id"])
        self.assertEqual("creative_prompt_unsteered", conditions[1]["condition_id"])
        self.assertEqual(
            [
                "neutral_steered_layer24_coeff_neg1p0",
                "neutral_steered_layer24_coeff_0p5",
                "neutral_steered_layer24_coeff_1p0",
                "neutral_steered_layer20_coeff_neg1p0",
                "neutral_steered_layer20_coeff_0p5",
                "neutral_steered_layer20_coeff_1p0",
            ],
            [condition["condition_id"] for condition in conditions[2:]],
        )
        self.assertEqual(24, conditions[2]["hidden_layer"])
        self.assertEqual(-1.0, conditions[2]["steering_coeff"])
        self.assertTrue(conditions[2]["normalize_control"])

    def test_summarize_outputs_includes_projection_and_quality_metrics(self) -> None:
        calibration = load_calibration_module()
        rows = [
            {
                "condition_id": "neutral_unsteered",
                "completion_word_count": 10,
                "completion_char_count": 40,
                "meta_marker_score": 0,
                "distinct_unigram_ratio": 0.9,
                "probe_projections": {"24": 1.0, "20": -1.0},
            },
            {
                "condition_id": "neutral_unsteered",
                "completion_word_count": 12,
                "completion_char_count": 48,
                "meta_marker_score": 1,
                "distinct_unigram_ratio": 0.8,
                "probe_projections": {"24": 3.0, "20": -3.0},
            },
        ]

        summaries = calibration.summarize_outputs(rows, probe_layers=[24, 20])

        self.assertEqual(1, len(summaries))
        self.assertEqual("neutral_unsteered", summaries[0]["condition_id"])
        self.assertEqual(11.0, summaries[0]["mean_completion_word_count"])
        self.assertEqual(0.5, summaries[0]["meta_marker_fraction"])
        self.assertAlmostEqual(0.85, summaries[0]["mean_distinct_unigram_ratio"])
        self.assertEqual(2.0, summaries[0]["mean_probe_projection_layer_24"])
        self.assertEqual(-2.0, summaries[0]["mean_probe_projection_layer_20"])


if __name__ == "__main__":
    unittest.main()
