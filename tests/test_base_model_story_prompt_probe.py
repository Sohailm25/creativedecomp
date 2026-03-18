# ABOUTME: Verifies the base-model story prompt probe uses a fixed candidate harness set and a stable meta-marker heuristic.
# ABOUTME: Prevents the prompting-repair step from drifting into ad hoc prompt tweaks that are hard to compare across runs.

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "probe_base_model_story_prompts.py"


def load_prompt_probe_module():
    spec = importlib.util.spec_from_file_location(
        "probe_base_model_story_prompts",
        SCRIPT_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module from {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class BaseModelStoryPromptProbeTest(unittest.TestCase):
    def test_build_prompt_templates_includes_continuation_candidates(self) -> None:
        probe = load_prompt_probe_module()

        templates = probe.build_prompt_templates()

        self.assertEqual(
            [
                "instruction_v1",
                "story_label_v1",
                "writing_prompt_v1",
                "bare_prompt_v1",
                "story_opening_once_v1",
            ],
            list(templates),
        )

    def test_compute_meta_marker_score_flags_forum_style_continuations(self) -> None:
        probe = load_prompt_probe_module()

        meta_score = probe.compute_meta_marker_score(
            "I posted this prompt in my google doc after asking on discord for feedback."
        )
        story_score = probe.compute_meta_marker_score(
            "Rain pressed against the diner window as Mara counted the spoons twice."
        )

        self.assertGreater(meta_score, 0)
        self.assertEqual(0, story_score)


if __name__ == "__main__":
    unittest.main()
