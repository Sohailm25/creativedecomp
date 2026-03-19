# ABOUTME: Verifies the refusal calibration harness keeps the matched neutral, prompted, and steered conditions.
# ABOUTME: Prevents coefficient sweeps from drifting away from the same-stack comparison used in the creativity lane.

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "run_refusal_direction_calibration.py"


def load_calibration_module():
    spec = importlib.util.spec_from_file_location(
        "run_refusal_direction_calibration",
        SCRIPT_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module from {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RefusalDirectionCalibrationTest(unittest.TestCase):
    def test_build_calibration_conditions_keeps_refusal_baselines_and_coeff_sweep(self) -> None:
        calibration = load_calibration_module()

        conditions = calibration.build_calibration_conditions(
            candidate_layers=[17, 19],
            steering_coeffs=[0.5, 1.0],
        )

        self.assertEqual(
            [
                "neutral_unsteered",
                "refusal_prompt_unsteered",
                "neutral_steered_layer17_coeff_0p5",
                "neutral_steered_layer17_coeff_1p0",
                "neutral_steered_layer19_coeff_0p5",
                "neutral_steered_layer19_coeff_1p0",
            ],
            [condition["condition_id"] for condition in conditions],
        )
        self.assertEqual("neutral", conditions[0]["prompt_mode"])
        self.assertEqual("prompt_only_refusal", conditions[1]["prompt_mode"])
        self.assertEqual(17, conditions[2]["hidden_layer"])


if __name__ == "__main__":
    unittest.main()
