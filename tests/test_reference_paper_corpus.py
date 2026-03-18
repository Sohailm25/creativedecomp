# ABOUTME: Verifies the local paper corpus covers the core papers cited across the research docs.
# ABOUTME: Prevents the repo from regressing back to a partial or placeholder-only paper cache.

from pathlib import Path
import unittest

from scripts.download_reference_papers import parse_manifest


REQUIRED_TITLES = {
    "Olson et al. creativity steering direction",
    "Von Rutte et al. creativity and humor representations",
    "Mayne et al. steering-vector SAE decomposition warnings",
    "SAE-TS",
    "FGAA",
    "SAS",
    "Arad et al. input versus output SAE features",
    "CREATE benchmark",
    "BILLY persona steering for creative generation",
    "Geometry of Knowledge creative latent exploration",
    "There Is More to Refusal",
    "LatentQA",
    "Activation Oracles",
    "Generative Meta-Models",
    "Patchscopes",
    "CS-ReFT",
    "Weighted Activation Steering",
    "LayerNavigator",
    "Concept Attractors",
    "COLD Decoding",
    "MuCoLa",
}


class ReferencePaperCorpusTest(unittest.TestCase):
    def test_manifest_covers_required_research_references(self) -> None:
        manifest_path = Path("background-work/papers/DOWNLOAD_MANIFEST.md")
        titles = {spec.title for spec in parse_manifest(manifest_path)}

        self.assertFalse(
            REQUIRED_TITLES - titles,
            f"manifest is missing required paper entries: {sorted(REQUIRED_TITLES - titles)}",
        )

    def test_manifest_uses_full_paper_artifacts(self) -> None:
        manifest_path = Path("background-work/papers/DOWNLOAD_MANIFEST.md")
        specs = parse_manifest(manifest_path)

        self.assertGreaterEqual(len(specs), 20)
        self.assertTrue(all(spec.filename.endswith(".pdf") for spec in specs))

    def test_paper_index_exists_for_future_agents(self) -> None:
        index_path = Path("background-work/papers/PAPER_INDEX.md")
        self.assertTrue(index_path.exists(), "expected a checked-in paper index for future agents")

        index_text = index_path.read_text(encoding="utf-8")
        self.assertIn("## Current-Phase Core", index_text)
        self.assertIn("## Extension And Context", index_text)

    def test_manifest_entries_exist_as_local_artifacts(self) -> None:
        manifest_path = Path("background-work/papers/DOWNLOAD_MANIFEST.md")
        specs = parse_manifest(manifest_path)

        missing_files = [
            str(Path("background-work/papers/files") / spec.filename)
            for spec in specs
            if not (Path("background-work/papers/files") / spec.filename).exists()
        ]
        self.assertFalse(
            missing_files,
            f"expected every manifest entry to exist locally, missing: {missing_files}",
        )


if __name__ == "__main__":
    unittest.main()
