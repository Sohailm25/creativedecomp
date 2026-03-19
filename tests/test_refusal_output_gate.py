# ABOUTME: Verifies the refusal output gate compares dense steering against neutral and prompted refusal baselines.
# ABOUTME: Prevents the simpler-concept control from drifting into ad hoc judgment prompts or inconsistent comparisons.

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "run_refusal_output_gate.py"
JUDGE_TEMPLATES_PATH = ROOT / "prompts" / "refusal_direction_output_gate_v1_judges.json"


def load_output_gate_module():
    spec = importlib.util.spec_from_file_location(
        "run_refusal_output_gate",
        SCRIPT_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module from {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RefusalOutputGateTest(unittest.TestCase):
    def test_build_output_gate_conditions_covers_refusal_baselines_and_dense_coeffs(self) -> None:
        gate = load_output_gate_module()

        conditions = gate.build_output_gate_conditions(
            hidden_layer=17,
            steering_coeffs=[0.5, 1.0],
        )

        self.assertEqual(
            [
                "neutral_unsteered",
                "refusal_prompt_unsteered",
                "neutral_steered_layer17_coeff_0p5",
                "neutral_steered_layer17_coeff_1p0",
            ],
            [condition["condition_id"] for condition in conditions],
        )
        self.assertEqual("neutral", conditions[0]["prompt_mode"])
        self.assertEqual("prompt_only_refusal", conditions[1]["prompt_mode"])

    def test_build_pairwise_comparisons_covers_neutral_and_refusal_prompt_baselines(self) -> None:
        gate = load_output_gate_module()

        comparisons = gate.build_pairwise_comparisons(
            dense_condition_ids=[
                "neutral_steered_layer17_coeff_0p5",
                "neutral_steered_layer17_coeff_1p0",
            ]
        )

        self.assertEqual(
            [
                "refusal_prompt_unsteered_vs_neutral_unsteered",
                "neutral_steered_layer17_coeff_0p5_vs_neutral_unsteered",
                "neutral_steered_layer17_coeff_1p0_vs_neutral_unsteered",
                "neutral_steered_layer17_coeff_0p5_vs_refusal_prompt_unsteered",
                "neutral_steered_layer17_coeff_1p0_vs_refusal_prompt_unsteered",
            ],
            [comparison["comparison_id"] for comparison in comparisons],
        )

    def test_repo_refusal_judge_templates_are_refusal_specific(self) -> None:
        templates = json.loads(JUDGE_TEMPLATES_PATH.read_text(encoding="utf-8"))

        self.assertIn("pairwise_refusal_label_judge", templates)
        self.assertIn("pairwise_coherence_label_judge", templates)
        self.assertIn("refuse", templates["pairwise_refusal_label_judge"].lower())
        self.assertIn("harmful", templates["pairwise_refusal_label_judge"].lower())


if __name__ == "__main__":
    unittest.main()
