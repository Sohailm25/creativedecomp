# ABOUTME: Downloads reference papers listed in the local markdown manifest into the experiment paper cache.
# ABOUTME: Keeps paper acquisition reproducible instead of relying on ad hoc browser downloads across sessions.

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
from urllib.request import urlretrieve


MANIFEST_LINE = re.compile(
    r"^- \[(?P<checked>[ xX])\] (?P<title>.+?) \| (?P<url>\S+) \| (?P<filename>.+)$"
)


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


def download_specs(
    specs: list[DownloadSpec],
    output_dir: Path,
    overwrite: bool,
    dry_run: bool,
) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    downloaded = 0
    for spec in specs:
        target_path = output_dir / spec.filename
        action = "skip"
        if target_path.exists() and not overwrite:
            action = "exists"
        elif dry_run:
            action = "dry-run"
            downloaded += 1
        else:
            urlretrieve(spec.url, target_path)
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
    )
    print(f"processed {len(specs)} manifest entries; actions taken for {downloaded}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
