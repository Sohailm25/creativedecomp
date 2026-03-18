# ABOUTME: Verifies the response-centered creativity pair builder preserves a shared extraction wrapper while varying only the continuation text.
# ABOUTME: Prevents the v2 contrast redesign from silently slipping back into instruction-template leakage.

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "materialize_creativity_response_pairs_v2.py"


def load_pairs_module():
    spec = importlib.util.spec_from_file_location(
        "materialize_creativity_response_pairs_v2",
        SCRIPT_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module from {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CreativityResponsePairsV2Test(unittest.TestCase):
    def test_build_response_pair_templates_adds_response_centered_keys(self) -> None:
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
        self.assertEqual(
            "Prompt: {prompt}\n\nPlain story:\nOnce",
            templates["response_pair_negative_source_prompt"],
        )
        self.assertEqual(
            "Prompt: {prompt}\n\nStory:\nOnce",
            templates["response_pair_extraction_shared_prompt"],
        )
        self.assertEqual(
            "Prompt: {prompt}\n\nStory:\nOnce",
            templates["response_pair_template_control"],
        )

    def test_render_extraction_text_keeps_shared_wrapper(self) -> None:
        pairs = load_pairs_module()
        templates = {
            "response_pair_extraction_shared_prompt": "Prompt: {prompt}\n\nStory:\nOnce",
        }

        rendered = pairs.render_extraction_text(
            prompt_text="A clockmaker builds a weather machine.",
            completion_text="upon a time, the brass clouds answered back.",
            templates=templates,
        )

        self.assertEqual(
            "Prompt: A clockmaker builds a weather machine.\n\nStory:\nOnce upon a time, the brass clouds answered back.",
            rendered,
        )

    def test_build_response_pair_row_uses_shared_extraction_wrapper_for_both_sides(self) -> None:
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
            positive_completion_text="upon a time, the sand hummed in concert pitch.",
            negative_completion_text="there was a man who played music every day.",
            positive_seed=2400,
            negative_seed=2401,
        )

        self.assertEqual("p1", row["prompt_id"])
        self.assertIn("Story:\nOnce upon a time", row["positive_text"])
        self.assertIn("Story:\nOnce there was a man", row["negative_text"])
        self.assertNotIn("Creative story", row["positive_text"])
        self.assertNotIn("Plain story", row["negative_text"])
        self.assertEqual(
            "Prompt: \n\nStory:\nOnce",
            row["template_control_positive_text"],
        )
        self.assertEqual(
            "Prompt: \n\nStory:\nOnce",
            row["template_control_negative_text"],
        )
