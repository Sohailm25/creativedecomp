# ABOUTME: Verifies the bounded SAE-latent refusal control stays sparse, signed, and gate-compatible.
# ABOUTME: Prevents the alternate-method control from drifting back into dense-vector behavior or ad hoc condition naming.

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "run_refusal_sae_latent_output_gate.py"


def load_gate_module():
    spec = importlib.util.spec_from_file_location(
        "run_refusal_sae_latent_output_gate",
        SCRIPT_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module from {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RefusalSaeLatentOutputGateTest(unittest.TestCase):
    def test_compute_sparse_signed_latent_delta_keeps_top_absolute_features(self) -> None:
        gate = load_gate_module()

        sparse = gate.compute_sparse_signed_latent_delta(
            np.asarray([0.1, -0.7, 0.4, -0.2, 0.9], dtype=np.float32),
            top_k=2,
        )

        self.assertEqual(2, int(np.count_nonzero(sparse)))
        self.assertTrue(np.allclose(sparse, np.asarray([0.0, -0.7, 0.0, 0.0, 0.9], dtype=np.float32)))

    def test_normalize_latent_delta_matches_unit_decoded_norm(self) -> None:
        gate = load_gate_module()

        latent_delta = np.asarray([3.0, 4.0], dtype=np.float32)
        decoder_matrix = np.asarray(
            [
                [1.0, 0.0],
                [0.0, 2.0],
            ],
            dtype=np.float32,
        )

        normalized = gate.normalize_latent_delta(latent_delta, decoder_matrix)
        decoded = gate.decode_latent_delta(normalized, decoder_matrix)

        self.assertAlmostEqual(1.0, float(np.linalg.norm(decoded)), places=6)

    def test_build_output_gate_conditions_covers_sparse_refusal_baselines_and_coeffs(self) -> None:
        gate = load_gate_module()

        conditions = gate.build_output_gate_conditions(
            hidden_layer=15,
            steering_coeffs=[0.5, 1.0],
        )

        self.assertEqual(
            [
                "neutral_unsteered",
                "refusal_prompt_unsteered",
                "neutral_sae_latent_layer15_coeff_0p5",
                "neutral_sae_latent_layer15_coeff_1p0",
            ],
            [condition["condition_id"] for condition in conditions],
        )
        self.assertEqual("neutral", conditions[0]["prompt_mode"])
        self.assertEqual("prompt_only_refusal", conditions[1]["prompt_mode"])


if __name__ == "__main__":
    unittest.main()
