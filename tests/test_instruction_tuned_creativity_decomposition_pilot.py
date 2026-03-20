# ABOUTME: Verifies the signed instruction-tuned creativity decomposition pilot stays matched to the frozen creativity stack.
# ABOUTME: Prevents the pilot from drifting into naive dense SAE encoding or unsigned feature ranking.

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "run_instruction_tuned_creativity_decomposition_pilot.py"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "run_instruction_tuned_creativity_decomposition_pilot",
        SCRIPT_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module from {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class InstructionTunedCreativityDecompositionPilotTest(unittest.TestCase):
    def test_default_stack_matches_instruction_tuned_phase2_pivot(self) -> None:
        module = load_module()

        self.assertEqual("google/gemma-3-270m-it", module.DEFAULT_MODEL_ID)
        self.assertEqual("gemma-scope-2-270m-it-res", module.DEFAULT_SAE_RELEASE)
        self.assertEqual("layer_12_width_16k_l0_medium", module.DEFAULT_REFERENCE_SAE_ID)
        self.assertIn("gemma3-270m-it", str(module.DEFAULT_SWEEP_DIR))

    def test_keep_top_k_signed_preserves_largest_signed_coefficients(self) -> None:
        module = load_module()

        coefficients = np.asarray([0.1, -0.7, 0.4, -0.2, 0.9], dtype=np.float32)
        sparse = module.keep_top_k_signed(coefficients, top_k=2)

        np.testing.assert_allclose(
            np.asarray([0.0, -0.7, 0.0, 0.0, 0.9], dtype=np.float32),
            sparse,
        )

    def test_build_random_feature_control_preserves_signed_values_and_count(self) -> None:
        module = load_module()

        coefficients = np.asarray([0.0, -0.7, 0.0, 0.2, 0.0, 1.1], dtype=np.float32)
        randomized = module.build_random_feature_control(
            coefficients,
            seed=17,
            candidate_feature_count=6,
        )

        self.assertEqual(3, int(np.count_nonzero(randomized)))
        self.assertCountEqual(
            list(np.round(coefficients[np.nonzero(coefficients)], 6)),
            list(np.round(randomized[np.nonzero(randomized)], 6)),
        )
        self.assertFalse(np.array_equal(coefficients, randomized))

    def test_run_fista_signed_sparse_coding_recovers_signed_solution(self) -> None:
        module = load_module()

        decoder_matrix = np.eye(3, dtype=np.float32)
        target_direction = np.asarray([0.8, 0.0, -0.4], dtype=np.float32)

        coefficients = module.run_fista_signed_sparse_coding(
            target_direction=target_direction,
            decoder_matrix=decoder_matrix,
            l1_alpha=0.01,
            max_steps=200,
            tolerance=1e-8,
        )

        self.assertGreater(coefficients[0], 0.0)
        self.assertLess(coefficients[2], 0.0)
        self.assertLess(abs(float(coefficients[1])), 1e-3)

    def test_extract_top_signed_features_separates_positive_and_negative(self) -> None:
        module = load_module()

        coefficients = np.asarray([0.0, -0.7, 0.5, -0.1, 0.9], dtype=np.float32)
        feature_summary = module.extract_top_signed_features(coefficients, top_n=2)

        self.assertEqual([4, 2], [row["feature_id"] for row in feature_summary["top_positive_features"]])
        self.assertEqual([1, 3], [row["feature_id"] for row in feature_summary["top_negative_features"]])


if __name__ == "__main__":
    unittest.main()
