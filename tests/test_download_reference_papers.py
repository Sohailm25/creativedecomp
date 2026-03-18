# ABOUTME: Verifies the paper-manifest helper parses only real manifest entries and skips documentation examples.
# ABOUTME: Prevents the download script from treating fenced-code examples as files to fetch.

from pathlib import Path
import tempfile
import textwrap
import unittest

from scripts.download_reference_papers import parse_manifest


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


if __name__ == "__main__":
    unittest.main()
