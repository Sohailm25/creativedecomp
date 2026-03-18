# ABOUTME: Verifies the pilot layer-sweep runner ranks layers by explicit evidence instead of ad hoc inspection.
# ABOUTME: Keeps the next dense-direction layer choice reproducible without loading Gemma weights in tests.

from __future__ import annotations

import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
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
    def test_path_for_summary_normalizes_repo_relative_paths(self) -> None:
        sweep = load_layer_sweep_module()

        summary_path = sweep.path_for_summary(Path("prompts/creative_direction_v2_pilot_pairs.jsonl"))

        self.assertEqual("prompts/creative_direction_v2_pilot_pairs.jsonl", summary_path)

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

    def test_add_template_control_metrics_measures_excess_over_template_signal(self) -> None:
        sweep = load_layer_sweep_module()
        row = {
            "hidden_layer": 7,
            "positive_gt_negative_fraction": 0.90625,
            "margin_zscore": 1.75,
            "mean_margin": 1.2,
        }
        template_control_summary = {
            "positive_gt_negative_fraction": 0.625,
            "margin_zscore": 0.5,
            "mean_margin": 0.2,
        }

        controlled_row = sweep.add_template_control_metrics(
            row=row,
            template_control_summary=template_control_summary,
            direction=[1.0, 1.0],
            template_direction=[1.0, 0.0],
        )

        self.assertAlmostEqual(0.28125, controlled_row["controlled_fraction_delta"])
        self.assertAlmostEqual(1.25, controlled_row["controlled_margin_zscore_delta"])
        self.assertAlmostEqual(0.2, controlled_row["template_control_mean_margin"])
        self.assertAlmostEqual(0.70710678, controlled_row["template_direction_cosine"], places=6)

    def test_rank_controlled_layers_penalizes_template_lexical_winners(self) -> None:
        sweep = load_layer_sweep_module()
        rows = [
            {
                "hidden_layer": 0,
                "controlled_fraction_delta": 0.0,
                "controlled_margin_zscore_delta": 0.0,
                "template_direction_cosine": 0.99,
                "positive_gt_negative_fraction": 1.0,
            },
            {
                "hidden_layer": 7,
                "controlled_fraction_delta": 0.25,
                "controlled_margin_zscore_delta": 0.8,
                "template_direction_cosine": 0.25,
                "positive_gt_negative_fraction": 0.90625,
            },
            {
                "hidden_layer": 12,
                "controlled_fraction_delta": 0.25,
                "controlled_margin_zscore_delta": 0.8,
                "template_direction_cosine": 0.55,
                "positive_gt_negative_fraction": 0.96875,
            },
        ]

        ranked = sweep.rank_controlled_layer_rows(rows)

        self.assertEqual([7, 12, 0], [row["hidden_layer"] for row in ranked])

    def test_select_controlled_best_layer_requires_positive_excess_signal(self) -> None:
        sweep = load_layer_sweep_module()
        rows = [
            {
                "hidden_layer": 0,
                "controlled_fraction_delta": 0.0,
                "controlled_margin_zscore_delta": -1.8,
            },
            {
                "hidden_layer": 7,
                "controlled_fraction_delta": -0.09375,
                "controlled_margin_zscore_delta": -2.3,
            },
        ]

        selected = sweep.select_controlled_best_layer(rows)

        self.assertIsNone(selected)

    def test_build_template_control_strings_uses_shared_control_for_response_pairs(self) -> None:
        sweep = load_layer_sweep_module()
        prompt_rows = [
            {
                "prompt_id": "p1",
                "prompt_text": "A violinist on Mars.",
                "positive_text": "Prompt: A violinist on Mars.\n\nStory:\nOnce red dust sang.",
                "negative_text": "Prompt: A violinist on Mars.\n\nStory:\nOnce he played a song.",
            }
        ]
        templates = {
            "response_pair_template_control": "Prompt: {prompt}\n\nStory:\nOnce",
        }

        positive_control, negative_control = sweep.build_template_control_strings(
            prompt_rows=prompt_rows,
            templates=templates,
        )

        self.assertEqual("Prompt: \n\nStory:\nOnce", positive_control)
        self.assertEqual("Prompt: \n\nStory:\nOnce", negative_control)

    def test_cleanup_optional_output_files_removes_stale_controlled_pair_details(self) -> None:
        sweep = load_layer_sweep_module()
        with TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            stale_path = output_dir / "controlled_best_layer_pair_details.jsonl"
            stale_path.write_text("stale\n", encoding="utf-8")

            sweep.cleanup_optional_output_files(output_dir, has_controlled_best_layer=False)

            self.assertFalse(stale_path.exists())


if __name__ == "__main__":
    unittest.main()
