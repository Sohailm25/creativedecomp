# ABOUTME: Verifies that the experiment workspace keeps the adapted resattn scaffold intact.
# ABOUTME: Acts as a regression test so future edits do not silently break the research operating structure.

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_DIRECTORIES = {
    "background-work",
    "background-work/papers",
    "configs",
    "history",
    "journal",
    "journal/logs",
    "knowledge",
    "notebooks",
    "prompts",
    "research",
    "results",
    "results/infrastructure",
    "results/creativity_direction",
    "results/feature_decomposition",
    "results/feature_validation",
    "results/bridge_features",
    "results/steering_eval",
    "results/creativity_benchmarks",
    "results/controller_extensions",
    "results/basin_dynamics",
    "results/figures",
    "scratch",
    "scripts",
    "sessions",
    "tests",
}

REQUIRED_FILES = {
    ".gitignore",
    "AGENTS.md",
    "README.md",
    "CURRENT_STATE.md",
    "DECISIONS.md",
    "SCRATCHPAD.md",
    "THOUGHT_LOG.md",
    "background-work/REFERENCES.md",
    "background-work/MECH_INTERP_GUIDANCE.md",
    "background-work/GAPS_SYNTHESIS.md",
    "background-work/PROPOSAL_REVIEW.md",
    "background-work/RESEARCH_POSITIONING.md",
    "background-work/SAFETY_PUBLICATION_POLICY.md",
    "background-work/papers/DOWNLOAD_MANIFEST.md",
    "configs/experiment.yaml",
    "history/PREREG.md",
    "history/20260318-resattn-scaffold-adaptation.md",
    "journal/current_state.md",
    "results/RESULTS_INDEX.md",
    "sessions/SESSION_TEMPLATE.md",
    "scripts/download_reference_papers.py",
    ".pre-commit-config.yaml",
}


class ScaffoldStructureTest(unittest.TestCase):
    def test_required_directories_exist(self) -> None:
        missing = sorted(
            str(path) for path in REQUIRED_DIRECTORIES if not (ROOT / path).is_dir()
        )
        self.assertEqual([], missing)

    def test_required_files_exist(self) -> None:
        missing = sorted(
            str(path) for path in REQUIRED_FILES if not (ROOT / path).is_file()
        )
        self.assertEqual([], missing)


if __name__ == "__main__":
    unittest.main()
