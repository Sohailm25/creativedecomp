# ABOUTME: Verifies the rubric-based cached-output evaluator is order-debiased and parse-robust.
# ABOUTME: Prevents claim-bearing creativity evaluation from inheriting the brittle A/B label judge behavior.

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "evaluate_instruction_tuned_creativity_output_gate_rubric_v1.py"


def load_eval_module():
    spec = importlib.util.spec_from_file_location(
        "evaluate_instruction_tuned_creativity_output_gate_rubric_v1",
        SCRIPT_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module from {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class InstructionTunedCreativityRubricEvalTest(unittest.TestCase):
    def test_parse_rubric_scores_accepts_json_with_wrapping_text(self) -> None:
        evaluator = load_eval_module()
        raw_text = (
            "analysis follows\n"
            '{"story_a":{"prompt_grounded_creativity":4,"coherence":3},'
            '"story_b":{"prompt_grounded_creativity":2,"coherence":5}}\n'
            "done"
        )

        parsed = evaluator.parse_rubric_scores(raw_text)

        self.assertEqual(4, parsed["story_a"]["prompt_grounded_creativity"])
        self.assertEqual(3, parsed["story_a"]["coherence"])
        self.assertEqual(2, parsed["story_b"]["prompt_grounded_creativity"])
        self.assertEqual(5, parsed["story_b"]["coherence"])

    def test_parse_rubric_scores_recovers_nested_story_b_shape(self) -> None:
        evaluator = load_eval_module()
        raw_text = (
            '{"story_a":{"prompt_grounded_creativity":1,"coherence":2,'
            '"story_b":{"prompt_grounded_creativity":4,"coherence":5}}}'
        )

        parsed = evaluator.parse_rubric_scores(raw_text)

        self.assertEqual(1, parsed["story_a"]["prompt_grounded_creativity"])
        self.assertEqual(2, parsed["story_a"]["coherence"])
        self.assertEqual(4, parsed["story_b"]["prompt_grounded_creativity"])
        self.assertEqual(5, parsed["story_b"]["coherence"])

    def test_resolve_order_debiased_axis_result_maps_reverse_story_slots(self) -> None:
        evaluator = load_eval_module()
        forward_scores = {
            "story_a": {"prompt_grounded_creativity": 4, "coherence": 3},
            "story_b": {"prompt_grounded_creativity": 2, "coherence": 4},
        }
        reverse_scores = {
            "story_a": {"prompt_grounded_creativity": 1, "coherence": 2},
            "story_b": {"prompt_grounded_creativity": 5, "coherence": 4},
        }

        axis_result = evaluator.resolve_order_debiased_axis_result(
            axis_name="prompt_grounded_creativity",
            forward_scores=forward_scores,
            reverse_scores=reverse_scores,
            candidate_condition_id="candidate",
            reference_condition_id="reference",
            min_margin=0.5,
        )

        self.assertEqual(4.5, axis_result["candidate_mean_score"])
        self.assertEqual(1.5, axis_result["reference_mean_score"])
        self.assertEqual(3.0, axis_result["score_delta"])
        self.assertEqual("candidate", axis_result["winner_condition_id"])

    def test_summarize_rubric_judgments_reports_candidate_and_reference_win_rates(self) -> None:
        evaluator = load_eval_module()
        judgment_rows = [
            {
                "comparison_id": "cand_vs_ref",
                "candidate_condition_id": "cand",
                "reference_condition_id": "ref",
                "prompt_grounded_creativity_winner_condition_id": "cand",
                "coherence_winner_condition_id": "ref",
                "prompt_grounded_creativity_candidate_mean_score": 4.0,
                "prompt_grounded_creativity_reference_mean_score": 3.0,
                "coherence_candidate_mean_score": 3.0,
                "coherence_reference_mean_score": 4.0,
                "parse_success": True,
            },
            {
                "comparison_id": "cand_vs_ref",
                "candidate_condition_id": "cand",
                "reference_condition_id": "ref",
                "prompt_grounded_creativity_winner_condition_id": "tie",
                "coherence_winner_condition_id": "cand",
                "prompt_grounded_creativity_candidate_mean_score": 3.0,
                "prompt_grounded_creativity_reference_mean_score": 3.0,
                "coherence_candidate_mean_score": 4.0,
                "coherence_reference_mean_score": 3.0,
                "parse_success": True,
            },
            {
                "comparison_id": "cand_vs_ref",
                "candidate_condition_id": "cand",
                "reference_condition_id": "ref",
                "prompt_grounded_creativity_winner_condition_id": "ref",
                "coherence_winner_condition_id": "tie",
                "prompt_grounded_creativity_candidate_mean_score": 2.0,
                "prompt_grounded_creativity_reference_mean_score": 4.0,
                "coherence_candidate_mean_score": 3.0,
                "coherence_reference_mean_score": 3.0,
                "parse_success": False,
            },
        ]

        summary_rows = evaluator.summarize_rubric_judgments(judgment_rows)

        self.assertEqual(1, len(summary_rows))
        row = summary_rows[0]
        self.assertEqual("cand_vs_ref", row["comparison_id"])
        self.assertAlmostEqual(1.0 / 3.0, row["prompt_grounded_creativity_candidate_win_fraction"])
        self.assertAlmostEqual(1.0 / 3.0, row["prompt_grounded_creativity_reference_win_fraction"])
        self.assertAlmostEqual(1.0 / 3.0, row["prompt_grounded_creativity_tie_fraction"])
        self.assertAlmostEqual(1.0 / 3.0, row["coherence_reference_win_fraction"])
        self.assertAlmostEqual(1.0 / 3.0, row["coherence_tie_fraction"])
        self.assertAlmostEqual(2.0 / 3.0, row["parse_success_fraction"])

    def test_summarize_judge_health_flags_collapsed_constant_ties(self) -> None:
        evaluator = load_eval_module()
        judgment_rows = [
            {
                "parse_success": True,
                "prompt_grounded_creativity_winner_condition_id": "tie",
                "coherence_winner_condition_id": "tie",
                "prompt_grounded_creativity_candidate_mean_score": 1.0,
                "prompt_grounded_creativity_reference_mean_score": 1.0,
                "coherence_candidate_mean_score": 1.0,
                "coherence_reference_mean_score": 1.0,
            },
            {
                "parse_success": True,
                "prompt_grounded_creativity_winner_condition_id": "tie",
                "coherence_winner_condition_id": "tie",
                "prompt_grounded_creativity_candidate_mean_score": 1.0,
                "prompt_grounded_creativity_reference_mean_score": 1.0,
                "coherence_candidate_mean_score": 1.0,
                "coherence_reference_mean_score": 1.0,
            },
        ]

        judge_health = evaluator.summarize_judge_health(judgment_rows)

        self.assertEqual(1.0, judge_health["overall_parse_success_fraction"])
        self.assertFalse(judge_health["usable_for_claim_bearing"])
        self.assertIn(
            "prompt_grounded_creativity_collapsed_to_constant_ties",
            judge_health["failure_reasons"],
        )
        self.assertIn("coherence_collapsed_to_constant_ties", judge_health["failure_reasons"])


if __name__ == "__main__":
    unittest.main()
