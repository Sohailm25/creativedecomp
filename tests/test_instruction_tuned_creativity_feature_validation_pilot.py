# ABOUTME: Keeps the feature-validation pilot peers honest by locking the signed method defaults and decoder assumptions.

from pathlib import Path
import unittest

try:
    import numpy as np
except ImportError:  # pragma: no cover
    np = None

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "run_instruction_tuned_creativity_feature_validation_pilot.py"


def load_module():
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "run_instruction_tuned_creativity_feature_validation_pilot",
        SCRIPT_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module from {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except ImportError as exc:
        if "numpy" in str(exc):
            raise unittest.SkipTest("numpy is required to import the feature-validation pilot script")
        raise
    return module


def build_identity_decoder():
    return np.eye(4, dtype=np.float32)


class FeatureValidationPilotTest(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_module()
        if np is None:
            self.skipTest("numpy is required for feature validation logic")

    def test_default_feature_method_is_fista(self) -> None:
        self.assertEqual("fista_dense_topk", self.module.DEFAULT_FEATURE_METHOD)

    def test_build_feature_direction_normalizes(self) -> None:
        decoder = build_identity_decoder()
        direction, normalized = self.module.build_feature_direction(
            feature_rows=[{"feature_id": 2, "signed_coefficient": 0.5}],
            vector_length=decoder.shape[0],
            decoder_matrix=decoder,
        )
        self.assertAlmostEqual(1.0, float(np.linalg.norm(direction)))
        self.assertGreater(normalized[2], 0.0)


if __name__ == "__main__":
    unittest.main()
