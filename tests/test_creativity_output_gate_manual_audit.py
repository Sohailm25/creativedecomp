# ABOUTME: Verifies the cached-output manual audit stays blinded, deterministic, and summary-safe.
# ABOUTME: Prevents the output-gate follow-up from drifting into ad hoc row selection or unscored notes.

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "audit_creativity_output_gate_v1.py"


def load_audit_module():
    spec = importlib.util.spec_from_file_location(
        "audit_creativity_output_gate_v1",
        SCRIPT_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module from {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CreativityOutputGateManualAuditTest(unittest.TestCase):
    def test_select_prompt_ids_for_audit_is_seeded_and_bounded(self) -> None:
        audit = load_audit_module()

        prompt_ids = [f"prompt-{index}" for index in range(8)]
        selected = audit.select_prompt_ids_for_audit(
            prompt_ids=prompt_ids,
            sample_size=3,
            seed=17,
        )

        self.assertEqual(3, len(selected))
        self.assertEqual(selected, audit.select_prompt_ids_for_audit(prompt_ids, 3, 17))
        self.assertTrue(set(selected).issubset(set(prompt_ids)))

    def test_build_blinded_audit_rows_randomizes_story_order_but_keeps_lookup(self) -> None:
        audit = load_audit_module()

        output_rows = [
            {
                "prompt_id": "p1",
                "prompt_text": "A lighthouse swallows the moon.",
                "condition_id": "creative_prompt_unsteered",
                "completion_text": "Creative continuation",
            },
            {
                "prompt_id": "p1",
                "prompt_text": "A lighthouse swallows the moon.",
                "condition_id": "neutral_unsteered",
                "completion_text": "Neutral continuation",
            },
            {
                "prompt_id": "p2",
                "prompt_text": "A ship writes letters to the harbor.",
                "condition_id": "creative_prompt_unsteered",
                "completion_text": "Creative continuation two",
            },
            {
                "prompt_id": "p2",
                "prompt_text": "A ship writes letters to the harbor.",
                "condition_id": "neutral_unsteered",
                "completion_text": "Neutral continuation two",
            },
        ]

        blinded_rows, answer_key_rows = audit.build_blinded_audit_rows(
            output_rows=output_rows,
            candidate_condition_id="creative_prompt_unsteered",
            reference_condition_id="neutral_unsteered",
            selected_prompt_ids=["p1", "p2"],
            seed=9,
        )

        self.assertEqual(2, len(blinded_rows))
        self.assertEqual(2, len(answer_key_rows))
        self.assertEqual(
            {row["audit_pair_id"] for row in blinded_rows},
            {row["audit_pair_id"] for row in answer_key_rows},
        )
        self.assertIn(blinded_rows[0]["story_a_text"], {"Creative continuation", "Neutral continuation"})
        self.assertIn(answer_key_rows[0]["story_a_condition_id"], {"creative_prompt_unsteered", "neutral_unsteered"})

    def test_summarize_manual_annotations_reports_axis_win_fractions(self) -> None:
        audit = load_audit_module()

        answer_key_rows = [
            {
                "audit_pair_id": "pair-1",
                "story_a_condition_id": "creative_prompt_unsteered",
                "story_b_condition_id": "neutral_unsteered",
            },
            {
                "audit_pair_id": "pair-2",
                "story_a_condition_id": "neutral_unsteered",
                "story_b_condition_id": "creative_prompt_unsteered",
            },
        ]
        annotation_rows = [
            {
                "audit_pair_id": "pair-1",
                "prompt_grounded_creativity_winner_label": "A",
                "coherence_winner_label": "tie",
            },
            {
                "audit_pair_id": "pair-2",
                "prompt_grounded_creativity_winner_label": "B",
                "coherence_winner_label": "A",
            },
        ]

        summary = audit.summarize_manual_annotations(
            answer_key_rows=answer_key_rows,
            annotation_rows=annotation_rows,
            candidate_condition_id="creative_prompt_unsteered",
            reference_condition_id="neutral_unsteered",
            axis_names=["prompt_grounded_creativity", "coherence"],
        )

        self.assertEqual(2, summary["sample_count"])
        self.assertEqual(1.0, summary["prompt_grounded_creativity_candidate_win_fraction"])
        self.assertEqual(0.0, summary["prompt_grounded_creativity_reference_win_fraction"])
        self.assertEqual(0.5, summary["coherence_reference_win_fraction"])


if __name__ == "__main__":
    unittest.main()
