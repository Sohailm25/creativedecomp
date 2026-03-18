# ABOUTME: Verifies the paper-manifest helper parses only real manifest entries and skips documentation examples.
# ABOUTME: Prevents the download script from treating fenced-code examples as files to fetch.

from pathlib import Path
import tempfile
import textwrap
import unittest

from scripts.download_reference_papers import (
    parse_manifest,
    should_browser_render_pdf,
    verify_downloaded_artifact,
)


class DownloadReferencePapersTest(unittest.TestCase):
    def test_parse_manifest_skips_fenced_code_examples(self) -> None:
        manifest_text = textwrap.dedent(
            """
            # Manifest

            ```text
            - [ ] Example Title | https://example.com/example | example.html
            ```

            ## Planned Downloads

            - [ ] Real Title | https://example.com/real | real.html
            """
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest_path = Path(temp_dir) / "DOWNLOAD_MANIFEST.md"
            manifest_path.write_text(manifest_text, encoding="utf-8")
            specs = parse_manifest(manifest_path)

        self.assertEqual(1, len(specs))
        self.assertEqual("Real Title", specs[0].title)

    def test_verify_downloaded_artifact_accepts_pdf_header(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            artifact_path = Path(temp_dir) / "paper.pdf"
            artifact_path.write_bytes(b"%PDF-1.7\n" + (b"x" * 2048))

            verify_downloaded_artifact(artifact_path)

    def test_verify_downloaded_artifact_rejects_non_pdf_content(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            artifact_path = Path(temp_dir) / "paper.pdf"
            artifact_path.write_bytes(b"not-a-pdf" + (b"x" * 2048))

            with self.assertRaises(ValueError):
                verify_downloaded_artifact(artifact_path)

    def test_should_browser_render_pdf_handles_transformer_circuits_articles(self) -> None:
        self.assertTrue(
            should_browser_render_pdf(
                "https://transformer-circuits.pub/2024/scaling-monosemanticity/index.html",
                Path("scaling-monosemanticity-2024.pdf"),
            )
        )
        self.assertFalse(
            should_browser_render_pdf(
                "https://arxiv.org/pdf/2310.01405",
                Path("representation-engineering-2023.pdf"),
            )
        )


if __name__ == "__main__":
    unittest.main()
