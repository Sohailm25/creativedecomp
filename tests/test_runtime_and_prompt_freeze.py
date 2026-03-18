# ABOUTME: Verifies that the initial experiment runtime and prompt split are frozen as real artifacts.
# ABOUTME: Prevents the first replication slice from drifting across sessions or reusing unfrozen prompts.

from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def read_jsonl(path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class RuntimeAndPromptFreezeTest(unittest.TestCase):
    def test_requirements_files_are_real_freezes(self) -> None:
        requirements_text = (ROOT / "requirements.txt").read_text(encoding="utf-8")
        lock_text = (ROOT / "requirements.lock.txt").read_text(encoding="utf-8")

        self.assertNotIn("pending `creativedecomp-1ie`", requirements_text)
        self.assertNotIn("pending `creativedecomp-1ie`", lock_text)

        for dependency in [
            "torch==",
            "transformers==",
            "sae-lens==",
            "repeng==",
            "datasets==",
            "accelerate==",
            "safetensors==",
            "sentencepiece==",
            "scipy==",
        ]:
            self.assertIn(dependency, requirements_text)

    def test_prompt_split_files_exist_and_are_disjoint(self) -> None:
        pilot_path = ROOT / "prompts/creative_direction_v1_pilot.jsonl"
        confirm_path = ROOT / "prompts/creative_direction_v1_confirm.jsonl"
        metadata_path = ROOT / "prompts/creative_direction_v1_metadata.json"
        templates_path = ROOT / "prompts/creative_direction_v1_templates.json"

        for path in [pilot_path, confirm_path, metadata_path, templates_path]:
            self.assertTrue(path.exists(), f"missing prompt-freeze artifact: {path}")

        pilot_rows = read_jsonl(pilot_path)
        confirm_rows = read_jsonl(confirm_path)

        self.assertEqual(32, len(pilot_rows))
        self.assertEqual(128, len(confirm_rows))

        pilot_ids = {row["prompt_id"] for row in pilot_rows}
        confirm_ids = {row["prompt_id"] for row in confirm_rows}
        self.assertFalse(
            pilot_ids & confirm_ids,
            "pilot and confirm splits must not share prompt ids",
        )

        for row in pilot_rows + confirm_rows:
            self.assertIn("source_dataset", row)
            self.assertIn("source_split", row)
            self.assertIn("source_index", row)
            self.assertIn("prompt_text", row)
            self.assertTrue(str(row["prompt_text"]).strip())

        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        self.assertEqual("creative_direction_v1", metadata["split_id"])
        self.assertEqual(32, metadata["pilot_count"])
        self.assertEqual(128, metadata["confirm_count"])

        templates = json.loads(templates_path.read_text(encoding="utf-8"))
        self.assertIn("creative_instruction", templates)
        self.assertIn("uncreative_instruction", templates)
        self.assertIn("prompt_only_creativity_baseline", templates)


if __name__ == "__main__":
    unittest.main()
