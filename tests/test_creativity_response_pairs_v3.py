# ABOUTME: Verifies the v3 counterpart-style pair builder prefers content-preserving plain rewrites over independently sampled negatives.
# ABOUTME: Prevents the next contrast revision from reintroducing content drift while claiming a creativity-only comparison.

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "materialize_creativity_response_pairs_v3.py"


def load_pairs_module():
    spec = importlib.util.spec_from_file_location(
        "materialize_creativity_response_pairs_v3",
        SCRIPT_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module from {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CreativityResponsePairsV3Test(unittest.TestCase):
    def test_build_response_pair_templates_adds_counterpart_rewrite_prompt(self) -> None:
        pairs = load_pairs_module()

        templates = pairs.build_response_pair_templates(
            {
                "creative_instruction": "Creative: {prompt}",
                "uncreative_instruction": "Plain: {prompt}",
                "prompt_only_creativity_baseline": "Creative baseline: {prompt}",
                "generation_neutral_story_opening": "Prompt: {prompt}\n\nStory:\nOnce",
                "generation_creative_story_opening": "Prompt: {prompt}\n\nCreative story:\nOnce",
            }
        )

        self.assertEqual(
            "Prompt: {prompt}\n\nCreative story:\nOnce",
            templates["response_pair_positive_source_prompt"],
        )
        self.assertIn("Rewrite the story below in a plain, literal style.", templates["response_pair_negative_counterpart_prompt"])
        self.assertIn("{source_story}", templates["response_pair_negative_counterpart_prompt"])
        self.assertEqual(
            "Prompt: {prompt}\n\nStory:\nOnce",
            templates["response_pair_extraction_shared_prompt"],
        )

    def test_evaluate_pair_quality_accepts_content_preserving_counterpart(self) -> None:
        pairs = load_pairs_module()

        quality = pairs.evaluate_pair_quality(
            prompt_text="A violinist on Mars plays to a silent crater.",
            positive_completion_text=(
                "upon a time a violinist on Mars played beside a silent crater while red dust drifted over the strings."
            ),
            negative_completion_text=(
                "upon a time a violinist on Mars played beside a crater while dust moved over the strings."
            ),
            positive_meta_marker_score=0,
            negative_meta_marker_score=0,
            min_counterpart_overlap=0.30,
            max_negative_prompt_grounding_delta=0.10,
        )

        self.assertTrue(quality["accepted"])
        self.assertEqual([], quality["rejection_reasons"])
        self.assertGreaterEqual(quality["counterpart_overlap_ratio"], 0.30)

    def test_evaluate_pair_quality_rejects_content_drift_and_prompt_grounding_reversal(self) -> None:
        pairs = load_pairs_module()

        quality = pairs.evaluate_pair_quality(
            prompt_text="A piece of paper travels from a factory to a city alley.",
            positive_completion_text=(
                "upon a time a happy man made paper and sold it at the market after a long day."
            ),
            negative_completion_text=(
                "upon a time a piece of paper left a factory in China, crossed shipping ports, reached a city store, and landed in an alley."
            ),
            positive_meta_marker_score=0,
            negative_meta_marker_score=0,
            min_counterpart_overlap=0.30,
            max_negative_prompt_grounding_delta=0.10,
        )

        self.assertFalse(quality["accepted"])
        self.assertIn("low_counterpart_overlap", quality["rejection_reasons"])
        self.assertIn("negative_more_prompt_grounded", quality["rejection_reasons"])

    def test_build_response_pair_row_records_quality_fields(self) -> None:
        pairs = load_pairs_module()
        templates = pairs.build_response_pair_templates(
            {
                "creative_instruction": "Creative: {prompt}",
                "uncreative_instruction": "Plain: {prompt}",
                "prompt_only_creativity_baseline": "Creative baseline: {prompt}",
                "generation_neutral_story_opening": "Prompt: {prompt}\n\nStory:\nOnce",
                "generation_creative_story_opening": "Prompt: {prompt}\n\nCreative story:\nOnce",
            }
        )

        row = pairs.build_response_pair_row(
            prompt_row={
                "prompt_id": "p1",
                "prompt_text": "A violinist on Mars.",
            },
            templates=templates,
            positive_completion_text="upon a time a violinist on Mars played under a glass dome.",
            negative_completion_text="upon a time a violinist on Mars played under a dome.",
            positive_seed=2400,
            negative_seed=2401,
            quality={
                "accepted": True,
                "counterpart_overlap_ratio": 0.5,
                "positive_prompt_grounding_ratio": 0.4,
                "negative_prompt_grounding_ratio": 0.35,
                "prompt_grounding_delta": -0.05,
                "rejection_reasons": [],
            },
        )

        self.assertEqual("plain_counterpart_rewrite", row["negative_generation_mode"])
        self.assertTrue(row["pair_quality_pass"])
        self.assertEqual([], row["pair_rejection_reasons"])
        self.assertEqual(0.5, row["counterpart_overlap_ratio"])
        self.assertEqual(
            "Prompt: \n\nStory:\nOnce",
            row["template_control_positive_text"],
        )


if __name__ == "__main__":
    unittest.main()
