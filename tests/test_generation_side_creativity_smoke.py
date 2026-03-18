# ABOUTME: Verifies the first generation-side creativity smoke compares explicit baseline and steering conditions.
# ABOUTME: Prevents the steering smoke from quietly collapsing into a single untraceable generation setup.

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "run_generation_side_creativity_smoke.py"


def load_generation_smoke_module():
    spec = importlib.util.spec_from_file_location(
        "run_generation_side_creativity_smoke",
        SCRIPT_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module from {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class GenerationSideCreativitySmokeTest(unittest.TestCase):
    def test_path_for_summary_normalizes_repo_relative_paths(self) -> None:
        smoke = load_generation_smoke_module()

        summary_path = smoke.path_for_summary(Path("results/creativity_direction/example"))

        self.assertEqual("results/creativity_direction/example", summary_path)

    def test_copy_wrapped_layer_attributes_preserves_attention_type(self) -> None:
        smoke = load_generation_smoke_module()
        wrapped_layer = SimpleNamespace(block=SimpleNamespace(attention_type="sliding_attention"))
        fake_model = SimpleNamespace(model=SimpleNamespace(layers=[wrapped_layer]))

        smoke.copy_wrapped_layer_attributes(fake_model, hidden_layer=0)

        self.assertEqual("sliding_attention", wrapped_layer.attention_type)

    def test_select_candidate_layers_uses_top_two_ranked_layers(self) -> None:
        smoke = load_generation_smoke_module()
        ranked_rows = [
            {"hidden_layer": 0},
            {"hidden_layer": 7},
            {"hidden_layer": 10},
        ]

        selected = smoke.select_candidate_layers(ranked_rows)

        self.assertEqual([0, 7], selected)

    def test_build_generation_conditions_covers_baselines_and_steering(self) -> None:
        smoke = load_generation_smoke_module()

        conditions = smoke.build_generation_conditions(
            candidate_layers=[0, 7],
            steering_coeff=1.0,
        )

        self.assertEqual(
            [
                "neutral_unsteered",
                "creative_prompt_unsteered",
                "neutral_steered_layer0",
                "neutral_steered_layer7",
            ],
            [condition["condition_id"] for condition in conditions],
        )
        self.assertEqual("neutral", conditions[0]["prompt_mode"])
        self.assertEqual("prompt_only_creativity", conditions[1]["prompt_mode"])
        self.assertEqual(0, conditions[2]["hidden_layer"])
        self.assertEqual(1.0, conditions[2]["steering_coeff"])


if __name__ == "__main__":
    unittest.main()
