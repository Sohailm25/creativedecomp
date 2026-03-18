# ABOUTME: Verifies that the core experiment docs stay focused on the creativity experiment rather than the prior routing thesis.
# ABOUTME: Prevents stale standalone-repo blockers and named legacy assumptions from persisting in the main operating docs.

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]

CORE_DOCS = [
    ROOT / "AGENTS.md",
    ROOT / "README.md",
    ROOT / "CURRENT_STATE.md",
    ROOT / "journal/current_state.md",
    ROOT / "history/PREREG.md",
    ROOT / "configs/experiment.yaml",
]

FORBIDDEN_PHRASES = [
    "oracle-alpha",
    "Figure 8",
    "AttnRes",
    "tool-breakage",
    "depth routing",
    "depth-routing",
    "not a standalone git repo",
    "not yet a standalone git repository",
    "pending Sohail's repo decision",
    "inherited home-repo branch",
    "current git root is `/Users/sohailmo`",
]


class CoreDocsNoResidualBaggageTest(unittest.TestCase):
    def test_core_docs_do_not_reference_legacy_thesis_or_stale_repo_state(self) -> None:
        violations: list[str] = []
        for path in CORE_DOCS:
            content = path.read_text(encoding="utf-8")
            for phrase in FORBIDDEN_PHRASES:
                if phrase in content:
                    violations.append(f"{path.relative_to(ROOT)} -> {phrase}")
        self.assertEqual([], violations)


if __name__ == "__main__":
    unittest.main()
