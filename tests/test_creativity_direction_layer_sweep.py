# ABOUTME: Verifies the pilot layer-sweep runner ranks layers by explicit evidence instead of ad hoc inspection.
# ABOUTME: Keeps the next dense-direction layer choice reproducible without loading Gemma weights in tests.

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "run_creativity_direction_layer_sweep.py"


def load_layer_sweep_module():
    spec = importlib.util.spec_from_file_location(
        "run_creativity_direction_layer_sweep",
        SCRIPT_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module from {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CreativityDirectionLayerSweepTest(unittest.TestCase):
    def test_parse_layers_argument_defaults_to_full_model(self) -> None:
        sweep = load_layer_sweep_module()

        layers = sweep.parse_layers_argument(None, num_hidden_layers=5)

        self.assertEqual([0, 1, 2, 3, 4], layers)

    def test_parse_layers_argument_supports_csv_values(self) -> None:
        sweep = load_layer_sweep_module()

        layers = sweep.parse_layers_argument("0,3,4", num_hidden_layers=8)

        self.assertEqual([0, 3, 4], layers)

    def test_rank_layers_prefers_fraction_then_margin_zscore(self) -> None:
        sweep = load_layer_sweep_module()
        rows = [
            {"hidden_layer": 4, "positive_gt_negative_fraction": 0.75, "margin_zscore": 0.9, "mean_margin": 1.0},
            {"hidden_layer": 12, "positive_gt_negative_fraction": 0.75, "margin_zscore": 1.1, "mean_margin": 0.8},
            {"hidden_layer": 20, "positive_gt_negative_fraction": 0.70, "margin_zscore": 4.0, "mean_margin": 3.0},
        ]

        ranked = sweep.rank_layer_rows(rows)

        self.assertEqual([12, 4, 20], [row["hidden_layer"] for row in ranked])


if __name__ == "__main__":
    unittest.main()
