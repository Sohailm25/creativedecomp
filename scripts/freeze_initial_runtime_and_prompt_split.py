# ABOUTME: Freezes the first working local runtime and materializes the initial creativity-direction prompt registry.
# ABOUTME: Keeps Phase 1 setup reproducible by pinning direct dependencies, lockfile contents, prompt splits, and instruction templates.

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
from importlib.metadata import version
from pathlib import Path
import re
import subprocess
import sys

from datasets import load_dataset


ROOT = Path(__file__).resolve().parents[1]
PROMPTS_DIR = ROOT / "prompts"
RESULTS_DIR = ROOT / "results" / "infrastructure"
SPLIT_ID = "creative_direction_v1"
PILOT_COUNT = 32
CONFIRM_COUNT = 128
SOURCE_DATASET = "euclaise/writingprompts"
SOURCE_SPLIT = "train"
MAX_TOTAL_COUNT = PILOT_COUNT + CONFIRM_COUNT
LEADING_TAG_RE = re.compile(r"^\[\s*WP\s*\]\s*", re.IGNORECASE)
WHITESPACE_RE = re.compile(r"\s+")
PUNCT_SPACING_RE = re.compile(r"\s+([,.;:!?])")
CONTRACTION_SPACING = [
    (" n't", "n't"),
    (" 're", "'re"),
    (" 's", "'s"),
    (" 've", "'ve"),
    (" 'll", "'ll"),
    (" 'd", "'d"),
    (" 'm", "'m"),
]

DIRECT_DEPENDENCIES = [
    ("accelerate", "accelerate"),
    ("datasets", "datasets"),
    ("playwright", "playwright"),
    ("repeng", "repeng"),
    ("sae-lens", "sae-lens"),
    ("safetensors", "safetensors"),
    ("scipy", "scipy"),
    ("sentencepiece", "sentencepiece"),
    ("torch", "torch"),
    ("transformers", "transformers"),
]

TEMPLATES = {
    "creative_instruction": (
        "Write a short story inspired by the prompt below. "
        "Be imaginative, original, vivid, and surprising while staying coherent.\n\n"
        "Prompt: {prompt}"
    ),
    "uncreative_instruction": (
        "Write a short story inspired by the prompt below. "
        "Keep it conventional, literal, unsurprising, and stylistically plain. "
        "Avoid figurative language and unusual twists.\n\n"
        "Prompt: {prompt}"
    ),
    "prompt_only_creativity_baseline": (
        "Write a creative short story inspired by the prompt below.\n\n"
        "Prompt: {prompt}"
    ),
    "generation_neutral_story_opening": "Prompt: {prompt}\n\nStory:\nOnce",
    "generation_creative_story_opening": "Prompt: {prompt}\n\nCreative story:\nOnce",
}


@dataclass(frozen=True)
class PromptRow:
    prompt_id: str
    source_dataset: str
    source_split: str
    source_index: int
    raw_prompt_text: str
    prompt_text: str

    def as_dict(self, split: str) -> dict[str, object]:
        return {
            "split": split,
            "prompt_id": self.prompt_id,
            "source_dataset": self.source_dataset,
            "source_split": self.source_split,
            "source_index": self.source_index,
            "raw_prompt_text": self.raw_prompt_text,
            "prompt_text": self.prompt_text,
        }


def clean_prompt_text(text: str) -> str:
    text = LEADING_TAG_RE.sub("", text.strip())
    text = WHITESPACE_RE.sub(" ", text)
    text = PUNCT_SPACING_RE.sub(r"\1", text)
    for source, target in CONTRACTION_SPACING:
        text = text.replace(source, target)
    return text.strip()


def is_usable_prompt(text: str) -> bool:
    if len(text) < 40 or len(text) > 280:
        return False
    word_count = len(text.split())
    if word_count < 8 or word_count > 60:
        return False
    if "http://" in text or "https://" in text:
        return False
    return True


def select_prompts() -> tuple[list[PromptRow], int]:
    dataset = load_dataset(SOURCE_DATASET, split=SOURCE_SPLIT)
    deduped: dict[str, PromptRow] = {}
    considered = 0
    for index, row in enumerate(dataset):
        raw_prompt = str(row["prompt"])
        prompt_text = clean_prompt_text(raw_prompt)
        if not is_usable_prompt(prompt_text):
            continue
        considered += 1
        prompt_id = hashlib.sha256(prompt_text.encode("utf-8")).hexdigest()[:16]
        deduped.setdefault(
            prompt_id,
            PromptRow(
                prompt_id=prompt_id,
                source_dataset=SOURCE_DATASET,
                source_split=SOURCE_SPLIT,
                source_index=index,
                raw_prompt_text=raw_prompt,
                prompt_text=prompt_text,
            ),
        )

    selected = sorted(deduped.values(), key=lambda row: row.prompt_id)[:MAX_TOTAL_COUNT]
    if len(selected) < MAX_TOTAL_COUNT:
        raise RuntimeError(
            f"expected at least {MAX_TOTAL_COUNT} prompts but found {len(selected)} usable rows"
        )
    return selected, considered


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    text = "\n".join(json.dumps(row, ensure_ascii=True) for row in rows) + "\n"
    path.write_text(text, encoding="utf-8")


def write_requirements_files() -> dict[str, str]:
    pinned_versions = {package_name: version(distribution_name) for distribution_name, package_name in DIRECT_DEPENDENCIES}
    requirements_lines = [
        "# Initial direct dependency freeze for creativity-direction replication.",
        "# Generated by scripts/freeze_initial_runtime_and_prompt_split.py.",
        *(f"{package_name}=={pinned_versions[package_name]}" for _, package_name in DIRECT_DEPENDENCIES),
        "",
    ]
    (ROOT / "requirements.txt").write_text("\n".join(requirements_lines), encoding="utf-8")

    freeze_result = subprocess.run(
        [sys.executable, "-m", "pip", "freeze"],
        check=True,
        capture_output=True,
        text=True,
    )
    lock_text = (
        "# Fully resolved dependency lock for the first creativity-direction replication slice.\n"
        "# Generated by scripts/freeze_initial_runtime_and_prompt_split.py.\n"
        f"{freeze_result.stdout}"
    )
    (ROOT / "requirements.lock.txt").write_text(lock_text, encoding="utf-8")
    return pinned_versions


def write_prompt_files(now: str) -> dict[str, object]:
    selected_prompts, considered = select_prompts()
    pilot_rows = [row.as_dict("pilot") for row in selected_prompts[:PILOT_COUNT]]
    confirm_rows = [row.as_dict("confirm") for row in selected_prompts[PILOT_COUNT:MAX_TOTAL_COUNT]]

    pilot_path = PROMPTS_DIR / f"{SPLIT_ID}_pilot.jsonl"
    confirm_path = PROMPTS_DIR / f"{SPLIT_ID}_confirm.jsonl"
    metadata_path = PROMPTS_DIR / f"{SPLIT_ID}_metadata.json"
    templates_path = PROMPTS_DIR / f"{SPLIT_ID}_templates.json"

    write_jsonl(pilot_path, pilot_rows)
    write_jsonl(confirm_path, confirm_rows)
    templates_path.write_text(json.dumps(TEMPLATES, indent=2) + "\n", encoding="utf-8")

    metadata = {
        "split_id": SPLIT_ID,
        "created_at": now,
        "source_dataset": SOURCE_DATASET,
        "source_split": SOURCE_SPLIT,
        "selection_method": "hash_sort_after_detokenize_filter_v1",
        "filter_rules": {
            "min_chars": 40,
            "max_chars": 280,
            "min_words": 8,
            "max_words": 60,
            "disallow_urls": True,
            "deduplicate_on_cleaned_prompt_text": True,
        },
        "pilot_count": len(pilot_rows),
        "confirm_count": len(confirm_rows),
        "usable_source_rows_considered": considered,
        "pilot_file": str(pilot_path.relative_to(ROOT)),
        "confirm_file": str(confirm_path.relative_to(ROOT)),
        "templates_file": str(templates_path.relative_to(ROOT)),
    }
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return metadata


def write_result_note(now: str, pinned_versions: dict[str, str], metadata: dict[str, object]) -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    result_path = RESULTS_DIR / "20260318-initial-runtime-and-prompt-freeze.md"
    body = "\n".join(
        [
            "# Initial Runtime And Prompt Freeze",
            "",
            f"- Generated at: `{now}`",
            f"- Python: `{sys.version.split()[0]}`",
            f"- Source dataset: `{metadata['source_dataset']}` / `{metadata['source_split']}`",
            f"- Prompt split: `{metadata['pilot_count']}` pilot / `{metadata['confirm_count']}` confirm",
            "- Direct dependencies:",
            *(f"  - `{package}=={pinned_versions[package]}`" for _, package in DIRECT_DEPENDENCIES),
            "- Artifacts:",
            f"  - `{metadata['pilot_file']}`",
            f"  - `{metadata['confirm_file']}`",
            f"  - `{metadata['templates_file']}`",
            "  - `requirements.txt`",
            "  - `requirements.lock.txt`",
            "",
            "This freeze is the starting point for the first local creativity-direction replication slice.",
            "The prompt split is deterministic and must not be changed without logging a new split id.",
        ]
    )
    result_path.write_text(body + "\n", encoding="utf-8")
    return result_path


def main() -> int:
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    pinned_versions = write_requirements_files()
    metadata = write_prompt_files(now)
    result_path = write_result_note(now, pinned_versions, metadata)
    print(f"wrote runtime freeze to {ROOT / 'requirements.txt'} and {ROOT / 'requirements.lock.txt'}")
    print(f"wrote prompt files for split {SPLIT_ID} under {PROMPTS_DIR}")
    print(f"wrote result note to {result_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
