# ABOUTME: Verifies the pilot output-gate runner compares dense steering against explicit baselines with locked judgment parsing.
# ABOUTME: Prevents the gate from drifting into ad hoc scoring or unstable comparison bookkeeping.

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "run_creativity_output_gate.py"


def load_output_gate_module():
    spec = importlib.util.spec_from_file_location(
        "run_creativity_output_gate",
        SCRIPT_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module from {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CreativityOutputGateTest(unittest.TestCase):
    def test_build_output_gate_conditions_covers_baselines_and_dense_coeffs(self) -> None:
        gate = load_output_gate_module()

        conditions = gate.build_output_gate_conditions(
            hidden_layer=23,
            steering_coeffs=[0.5, 1.0],
        )

        self.assertEqual(
            [
                "neutral_unsteered",
                "creative_prompt_unsteered",
                "neutral_steered_layer23_coeff_0p5",
                "neutral_steered_layer23_coeff_1p0",
            ],
            [condition["condition_id"] for condition in conditions],
        )
        self.assertEqual("neutral", conditions[0]["prompt_mode"])
        self.assertEqual("prompt_only_creativity", conditions[1]["prompt_mode"])
        self.assertEqual(23, conditions[2]["hidden_layer"])

    def test_build_pairwise_comparisons_covers_neutral_and_prompt_baselines(self) -> None:
        gate = load_output_gate_module()

        comparisons = gate.build_pairwise_comparisons(
            dense_condition_ids=[
                "neutral_steered_layer23_coeff_0p5",
                "neutral_steered_layer23_coeff_1p0",
            ]
        )

        self.assertEqual(
            [
                "creative_prompt_unsteered_vs_neutral_unsteered",
                "neutral_steered_layer23_coeff_0p5_vs_neutral_unsteered",
                "neutral_steered_layer23_coeff_1p0_vs_neutral_unsteered",
                "neutral_steered_layer23_coeff_0p5_vs_creative_prompt_unsteered",
                "neutral_steered_layer23_coeff_1p0_vs_creative_prompt_unsteered",
            ],
            [comparison["comparison_id"] for comparison in comparisons],
        )

    def test_render_pairwise_judge_prompt_inserts_prompt_and_story_text(self) -> None:
        gate = load_output_gate_module()

        prompt_text = gate.render_pairwise_judge_prompt(
            prompt_text="A fisherman sees the moon crack open.",
            story_a="Once the harbor filled with blue fire.",
            story_b="Once the fisherman went home.",
            judge_template=(
                "Prompt: {prompt}\n\nStory A:\n{story_a}\n\nStory B:\n{story_b}\n\nReturn JSON."
            ),
        )

        self.assertIn("A fisherman sees the moon crack open.", prompt_text)
        self.assertIn("Once the harbor filled with blue fire.", prompt_text)
        self.assertIn("Once the fisherman went home.", prompt_text)

    def test_repo_judge_templates_format_without_placeholder_collisions(self) -> None:
        gate = load_output_gate_module()
        judge_templates_path = ROOT / "prompts" / "creative_direction_output_gate_v1_judges.json"
        judge_templates = gate.load_judge_templates(judge_templates_path)

        creativity_prompt = gate.render_pairwise_judge_prompt(
            prompt_text="A fisherman sees the moon crack open.",
            story_a="Once the harbor filled with blue fire.",
            story_b="Once the fisherman went home.",
            judge_template=judge_templates["pairwise_creativity_label_judge"],
        )
        coherence_prompt = gate.render_pairwise_judge_prompt(
            prompt_text="A fisherman sees the moon crack open.",
            story_a="Once the harbor filled with blue fire.",
            story_b="Once the fisherman went home.",
            judge_template=judge_templates["pairwise_coherence_label_judge"],
        )

        self.assertIn("Answer with exactly one label", creativity_prompt)
        self.assertIn("Story A:", creativity_prompt)
        self.assertIn("coherent", coherence_prompt.lower())

    def test_parse_label_judgment_accepts_single_label_or_short_phrase(self) -> None:
        gate = load_output_gate_module()

        self.assertEqual("A", gate.parse_label_judgment("A"))
        self.assertEqual("B", gate.parse_label_judgment("The better answer is B."))
        self.assertEqual("tie", gate.parse_label_judgment("tie"))

    def test_compute_repeated_bigram_fraction_flags_looping_text(self) -> None:
        gate = load_output_gate_module()

        looping_fraction = gate.compute_repeated_bigram_fraction(
            "red moon red moon red moon"
        )
        clean_fraction = gate.compute_repeated_bigram_fraction(
            "red moon over the harbor tonight"
        )

        self.assertGreater(looping_fraction, clean_fraction)

    def test_summarize_pairwise_judgments_aggregates_candidate_and_reference_rates(self) -> None:
        gate = load_output_gate_module()
        comparison = {
            "comparison_id": "dense_vs_neutral",
            "candidate_condition_id": "dense",
            "reference_condition_id": "neutral",
        }
        judgment_rows = [
            {
                "comparison_id": "dense_vs_neutral",
                "creativity_winner_condition_id": "dense",
                "coherence_winner_condition_id": "neutral",
            },
            {
                "comparison_id": "dense_vs_neutral",
                "creativity_winner_condition_id": "tie",
                "coherence_winner_condition_id": "dense",
            },
            {
                "comparison_id": "dense_vs_neutral",
                "creativity_winner_condition_id": "dense",
                "coherence_winner_condition_id": "dense",
            },
        ]

        summary = gate.summarize_pairwise_judgments(
            judgment_rows=judgment_rows,
            comparisons=[comparison],
        )

        self.assertEqual(1, len(summary))
        self.assertEqual(2 / 3, summary[0]["creativity_candidate_win_fraction"])
        self.assertEqual(1 / 3, summary[0]["creativity_tie_fraction"])
        self.assertEqual(2 / 3, summary[0]["coherence_candidate_win_fraction"])

    def test_resolve_order_robust_winner_requires_consistent_condition(self) -> None:
        gate = load_output_gate_module()

        self.assertEqual("dense", gate.resolve_order_robust_winner("dense", "dense"))
        self.assertEqual("tie", gate.resolve_order_robust_winner("dense", "neutral"))
        self.assertEqual("tie", gate.resolve_order_robust_winner("tie", "dense"))


if __name__ == "__main__":
    unittest.main()
