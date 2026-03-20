# ABOUTME: Verifies prompt-family-matched feature-bundle refresh helpers for corrective feature-validation experiments.
# ABOUTME: Keeps feature ranking and refreshed table construction deterministic and auditable.

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "select_prompt_matched_bundle_v1.py"


def load_script_module():
    spec = importlib.util.spec_from_file_location(
        "select_prompt_matched_bundle_v1",
        SCRIPT_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module from {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SelectPromptMatchedBundleV1Test(unittest.TestCase):
    def test_compute_feature_candidate_score(self) -> None:
        script = load_script_module()

        score = script.compute_feature_candidate_score(
            mean_prompt_grounding_ratio=0.35,
            mean_repetition_rate=0.10,
        )

        self.assertAlmostEqual(0.25, score)

    def test_rank_feature_rows_by_score(self) -> None:
        script = load_script_module()
        rows = [
            {"feature_id": 1, "selection_score": 0.1},
            {"feature_id": 2, "selection_score": 0.4},
            {"feature_id": 3, "selection_score": 0.2},
        ]

        ranked = script.rank_feature_rows_by_score(rows, select_count=2)

        self.assertEqual([2, 3], [row["feature_id"] for row in ranked])

    def test_build_refreshed_method_payload(self) -> None:
        script = load_script_module()
        positive_rows = [
            {"feature_id": 10, "signed_coefficient": 0.15},
            {"feature_id": 11, "signed_coefficient": 0.12},
        ]
        negative_rows = [
            {"feature_id": 21, "signed_coefficient": -0.18},
            {"feature_id": 22, "signed_coefficient": -0.11},
        ]

        payload = script.build_refreshed_method_payload(
            positive_rows=positive_rows,
            negative_rows=negative_rows,
        )

        self.assertEqual(2, len(payload["top_positive_features"]))
        self.assertEqual(2, len(payload["top_negative_features"]))
        self.assertEqual(4, payload["nonzero_feature_count"])


if __name__ == "__main__":
    unittest.main()
