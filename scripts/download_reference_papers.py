# ABOUTME: Downloads reference papers listed in the local markdown manifest into the experiment paper cache.
# ABOUTME: Keeps paper acquisition reproducible instead of relying on ad hoc browser downloads across sessions.

from __future__ import annotations

import argparse
import base64
from dataclasses import dataclass
from pathlib import Path
import re
import shutil
from tempfile import NamedTemporaryFile
from urllib.parse import parse_qs, urlparse
from urllib.error import HTTPError
from urllib.request import Request, urlopen


MANIFEST_LINE = re.compile(
    r"^- \[(?P<checked>[ xX])\] (?P<title>.+?) \| (?P<url>\S+) \| (?P<filename>.+)$"
)
MIN_FILE_SIZE_BYTES = 1_024
DOWNLOAD_USER_AGENT = "creativedecomp-paper-downloader/1.0"
DEFAULT_CHROME_PATHS = (
    Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
    Path("/Applications/Chromium.app/Contents/MacOS/Chromium"),
)
BROWSER_RENDER_PDF_DOMAINS = {"transformer-circuits.pub"}


@dataclass(frozen=True)
class DownloadSpec:
    title: str
    url: str
    filename: str
    checked: bool


def parse_manifest(manifest_path: Path) -> list[DownloadSpec]:
    specs: list[DownloadSpec] = []
    inside_code_block = False
    for raw_line in manifest_path.read_text(encoding="utf-8").splitlines():
        stripped_line = raw_line.strip()
        if stripped_line.startswith("```"):
            inside_code_block = not inside_code_block
            continue
        if inside_code_block:
            continue
        match = MANIFEST_LINE.match(stripped_line)
        if match is None:
            continue
        specs.append(
            DownloadSpec(
                title=match.group("title").strip(),
                url=match.group("url").strip(),
                filename=match.group("filename").strip(),
                checked=match.group("checked").lower() == "x",
            )
        )
    return specs


def verify_downloaded_artifact(target_path: Path) -> None:
    if not target_path.exists():
        raise FileNotFoundError(f"missing downloaded artifact: {target_path}")
    if target_path.stat().st_size < MIN_FILE_SIZE_BYTES:
        raise ValueError(f"artifact is too small to be a full paper file: {target_path}")

    header = target_path.read_bytes()[:8]
    if target_path.suffix.lower() == ".pdf" and not header.startswith(b"%PDF"):
        raise ValueError(f"expected a PDF artifact but found different content: {target_path}")


def detect_chrome_executable() -> Path:
    for candidate in DEFAULT_CHROME_PATHS:
        if candidate.exists():
            return candidate
    raise RuntimeError(
        "OpenReview fallback requires a local Chrome/Chromium executable in a standard macOS path."
    )


def should_browser_render_pdf(url: str, target_path: Path) -> bool:
    parsed_url = urlparse(url)
    return (
        target_path.suffix.lower() == ".pdf"
        and parsed_url.netloc in BROWSER_RENDER_PDF_DOMAINS
        and not parsed_url.path.lower().endswith(".pdf")
    )


def extract_openreview_id(url: str) -> str | None:
    parsed_url = urlparse(url)
    if parsed_url.netloc != "openreview.net":
        return None
    if parsed_url.path != "/pdf":
        return None
    paper_id = parse_qs(parsed_url.query).get("id", [None])[0]
    return paper_id


def render_webpage_to_pdf(url: str, target_path: Path) -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:  # pragma: no cover - environment-dependent fallback
        raise RuntimeError(
            "Browser-rendered downloads require `playwright` in the active .venv."
        ) from exc

    chrome_path = detect_chrome_executable()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True,
            executable_path=str(chrome_path),
        )
        page = browser.new_page()
        page.goto(url, wait_until="networkidle", timeout=60_000)
        page.pdf(
            path=str(target_path),
            format="A4",
            print_background=True,
        )
        browser.close()


def download_openreview_pdf_with_browser(url: str, target_path: Path) -> None:
    paper_id = extract_openreview_id(url)
    if paper_id is None:
        raise ValueError(f"expected an OpenReview PDF url with an id query parameter: {url}")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:  # pragma: no cover - environment-dependent fallback
        raise RuntimeError(
            "OpenReview downloads require `playwright` in the active .venv because raw HTTP access is blocked."
        ) from exc

    chrome_path = detect_chrome_executable()
    forum_url = f"https://openreview.net/forum?id={paper_id}"
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True,
            executable_path=str(chrome_path),
        )
        page = browser.new_page()
        page.goto(forum_url, wait_until="networkidle", timeout=60_000)
        encoded_body = page.evaluate(
            """
            async (pdfId) => {
                const response = await fetch(`/pdf?id=${pdfId}`);
                const buffer = await response.arrayBuffer();
                const bytes = new Uint8Array(buffer);
                let binary = "";
                const chunkSize = 0x8000;
                for (let index = 0; index < bytes.length; index += chunkSize) {
                    binary += String.fromCharCode(...bytes.subarray(index, index + chunkSize));
                }
                return btoa(binary);
            }
            """,
            paper_id,
        )
        browser.close()
    target_path.write_bytes(base64.b64decode(encoded_body))


def download_file(url: str, target_path: Path) -> None:
    if should_browser_render_pdf(url, target_path):
        render_webpage_to_pdf(url, target_path)
        return

    request = Request(url, headers={"User-Agent": DOWNLOAD_USER_AGENT})
    try:
        with urlopen(request) as response, NamedTemporaryFile(
            delete=False,
            dir=target_path.parent,
            prefix=f"{target_path.name}.",
            suffix=".part",
        ) as temp_file:
            shutil.copyfileobj(response, temp_file)
            temp_path = Path(temp_file.name)
        temp_path.replace(target_path)
    except HTTPError:
        if extract_openreview_id(url) is None:
            raise
        download_openreview_pdf_with_browser(url, target_path)


def download_specs(
    specs: list[DownloadSpec],
    output_dir: Path,
    overwrite: bool,
    dry_run: bool,
    verify_only: bool,
) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    downloaded = 0
    for spec in specs:
        target_path = output_dir / spec.filename
        if dry_run:
            action = "dry-run"
            downloaded += 1
        elif verify_only:
            verify_downloaded_artifact(target_path)
            action = "verified"
        elif target_path.exists() and not overwrite:
            verify_downloaded_artifact(target_path)
            action = "exists"
        else:
            download_file(spec.url, target_path)
            verify_downloaded_artifact(target_path)
            action = "downloaded"
            downloaded += 1
        print(f"{action}: {spec.title} -> {target_path}")
    return downloaded


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("background-work/papers/DOWNLOAD_MANIFEST.md"),
        help="Markdown manifest to parse.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("background-work/papers/files"),
        help="Directory for downloaded paper files.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Redownload files that already exist.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print intended downloads without writing files.",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Validate that every manifest entry already exists locally as a full artifact.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    specs = parse_manifest(args.manifest)
    if not specs:
        print(f"no manifest entries found in {args.manifest}")
        return 0
    downloaded = download_specs(
        specs=specs,
        output_dir=args.output_dir,
        overwrite=args.overwrite,
        dry_run=args.dry_run,
        verify_only=args.verify_only,
    )
    print(f"processed {len(specs)} manifest entries; actions taken for {downloaded}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
