# ABOUTME: Verifies the refusal-direction pilot pack is response-centered and large enough for a matched same-stack control.
# ABOUTME: Prevents the refusal baseline from inheriting creativity-template confounds or an underspecified prompt set.

from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PILOT_PATH = ROOT / "prompts" / "refusal_direction_v1_pilot_pairs.jsonl"
TEMPLATES_PATH = ROOT / "prompts" / "refusal_direction_v1_templates.json"


class RefusalDirectionLayerSweepTest(unittest.TestCase):
    def test_refusal_pilot_pairs_are_response_centered_and_sized_for_pilot(self) -> None:
        rows = [
            json.loads(line)
            for line in PILOT_PATH.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

        self.assertEqual(32, len(rows))
        for row in rows:
            self.assertIn("prompt_id", row)
            self.assertIn("prompt_text", row)
            self.assertIn("positive_text", row)
            self.assertIn("negative_text", row)
            self.assertIn("Request:", row["positive_text"])
            self.assertIn("Response:", row["positive_text"])
            self.assertIn("Request:", row["negative_text"])
            self.assertIn("Response:", row["negative_text"])

    def test_refusal_templates_include_generation_and_template_control_keys(self) -> None:
        templates = json.loads(TEMPLATES_PATH.read_text(encoding="utf-8"))

        self.assertIn("generation_neutral_request_opening", templates)
        self.assertIn("generation_refusal_request_opening", templates)
        self.assertIn("response_pair_template_control", templates)


if __name__ == "__main__":
    unittest.main()
