# ABOUTME: Verifies that the live strategy docs follow the novelty memo's recommended framing and controls.
# ABOUTME: Prevents the repo from drifting toward a generic creativity project instead of the novelty-backed experiment.

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]

PREREG = (ROOT / "history/PREREG.md").read_text(encoding="utf-8")
POSITIONING = (ROOT / "background-work/RESEARCH_POSITIONING.md").read_text(
    encoding="utf-8"
)
CURRENT_STATE = (ROOT / "CURRENT_STATE.md").read_text(encoding="utf-8")


class ResearchDirectionAlignmentTest(unittest.TestCase):
    def test_positioning_frames_question_as_mechanistic_difference(self) -> None:
        self.assertIn("mechanistically different", POSITIONING)

    def test_prereg_requires_baseline_comparisons_to_simpler_concepts(self) -> None:
        self.assertIn("refusal", PREREG)
        self.assertIn("sentiment", PREREG)

    def test_prereg_requires_multi_method_or_pilot_method_comparison(self) -> None:
        self.assertTrue(
            "multiple decomposition methods" in PREREG
            or "compare at least two" in PREREG
        )

    def test_current_state_tracks_output_filtering_and_negative_result_path(self) -> None:
        self.assertIn("output-feature", CURRENT_STATE)
        self.assertIn("negative result", CURRENT_STATE)


if __name__ == "__main__":
    unittest.main()
