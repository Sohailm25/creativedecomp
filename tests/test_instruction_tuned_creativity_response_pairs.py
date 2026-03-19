# ABOUTME: Verifies the instruction-tuned creativity pair builder stays on the matched Gemma 3 270M IT stack and preserves the counterpart-style contrast.
# ABOUTME: Prevents the instruction-tuned creativity port from drifting into a fresh dataset or storing only prompt-template differences.

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "materialize_instruction_tuned_creativity_response_pairs_v1.py"


def load_pairs_module():
    spec = importlib.util.spec_from_file_location(
        "materialize_instruction_tuned_creativity_response_pairs_v1",
        SCRIPT_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module from {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class InstructionTunedCreativityResponsePairsTest(unittest.TestCase):
    def test_default_stack_reuses_instruction_tuned_creativity_source_slice(self) -> None:
        pairs = load_pairs_module()

        self.assertEqual("google/gemma-3-270m-it", pairs.DEFAULT_MODEL_ID)
        self.assertEqual(
            ROOT / "prompts" / "creative_direction_v1_pilot.jsonl",
            pairs.DEFAULT_SOURCE_SPLIT_PATH,
        )

    def test_build_positive_and_negative_messages_keep_creativity_generation_and_plain_rewrite_separate(self) -> None:
        pairs = load_pairs_module()

        templates = {
            "prompt_only_creativity_user_prompt": "Write a creative short story.\n\nPrompt: {prompt}",
            "response_pair_negative_counterpart_prompt": (
                "Rewrite the story below plainly.\n\nPrompt: {prompt}\n\nSource story:\n{source_story}"
            ),
        }

        positive_messages = pairs.build_positive_source_messages(
            prompt_text="A clock learns to dream.",
            templates=templates,
        )
        negative_messages = pairs.build_negative_counterpart_messages(
            prompt_text="A clock learns to dream.",
            source_story="Once the brass heart started ticking in moonlight.",
            templates=templates,
        )

        self.assertEqual([{"role": "user", "content": "Write a creative short story.\n\nPrompt: A clock learns to dream."}], positive_messages)
        self.assertEqual("user", negative_messages[0]["role"])
        self.assertIn("Rewrite the story below plainly.", negative_messages[0]["content"])
        self.assertIn("Once the brass heart started ticking in moonlight.", negative_messages[0]["content"])

    def test_build_response_pair_row_records_assistant_text_and_quality_fields(self) -> None:
        pairs = load_pairs_module()

        row = pairs.build_response_pair_row(
            prompt_row={
                "split": "pilot",
                "prompt_id": "p1",
                "prompt_text": "A lighthouse swallows the moon.",
            },
            positive_assistant_text="The lighthouse gulped the moon and the harbor glowed blue.",
            negative_assistant_text="The lighthouse took in the moon and the harbor turned blue.",
            positive_seed=7100,
            negative_seed=7101,
            quality={
                "accepted": True,
                "counterpart_overlap_ratio": 0.72,
                "positive_prompt_grounding_ratio": 0.21,
                "negative_prompt_grounding_ratio": 0.18,
                "prompt_grounding_delta": -0.03,
                "rejection_reasons": [],
            },
        )

        self.assertEqual("pilot", row["split"])
        self.assertEqual("plain_counterpart_rewrite", row["negative_generation_mode"])
        self.assertEqual(
            "The lighthouse gulped the moon and the harbor glowed blue.",
            row["positive_assistant_text"],
        )
        self.assertTrue(row["pair_quality_pass"])
        self.assertEqual([], row["pair_rejection_reasons"])
        self.assertEqual(0.72, row["counterpart_overlap_ratio"])


if __name__ == "__main__":
    unittest.main()
