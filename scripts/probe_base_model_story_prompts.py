# ABOUTME: Probes continuation-style prompt harnesses for base Gemma story generation on a tiny pilot slice.
# ABOUTME: Saves comparable unsteered outputs so the steering harness can be repaired with evidence instead of prompt folklore.

from __future__ import annotations

import argparse
from collections import OrderedDict
from datetime import datetime
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from run_creativity_direction_smoke import (  # noqa: E402
    ROOT,
    DEFAULT_MODEL_ID,
    DEFAULT_SPLIT_PATH,
    load_model_and_tokenizer,
    load_prompt_rows,
    select_device,
    write_json,
    write_jsonl,
)
from run_generation_side_creativity_smoke import generate_completion  # noqa: E402


DEFAULT_MAX_PROMPTS = 3
DEFAULT_MAX_NEW_TOKENS = 96
DEFAULT_SEED = 1729
META_MARKERS = (
    "prompt",
    "google doc",
    "discord",
    "creative writing",
    "feedback",
    "<em>",
    "writer in the process",
    "class for college",
    "word count",
    "i posted",
    "i would like to add",
)


def default_output_dir() -> Path:
    run_date = datetime.now().strftime("%Y%m%d")
    return ROOT / "results" / "steering_eval" / f"{run_date}-gemma2-2b-prompt-harness-probe"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Probe a small set of base-model story prompt harnesses on the frozen pilot split."
    )
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID)
    parser.add_argument("--split-path", type=Path, default=DEFAULT_SPLIT_PATH)
    parser.add_argument("--max-prompts", type=int, default=DEFAULT_MAX_PROMPTS)
    parser.add_argument("--max-new-tokens", type=int, default=DEFAULT_MAX_NEW_TOKENS)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--device", choices=["auto", "mps", "cpu"], default="auto")
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def build_prompt_templates() -> OrderedDict[str, str]:
    return OrderedDict(
        [
            ("instruction_v1", "Write a short story inspired by the prompt below.\n\nPrompt: {prompt}"),
            ("story_label_v1", "Prompt: {prompt}\n\nStory:\n"),
            ("writing_prompt_v1", "Writing prompt: {prompt}\n\nShort story:\n"),
            ("bare_prompt_v1", "{prompt}\n\n"),
            ("story_opening_once_v1", "Prompt: {prompt}\n\nStory:\nOnce"),
        ]
    )


def compute_meta_marker_score(text: str) -> int:
    lowered = text.lower()
    return sum(marker in lowered for marker in META_MARKERS)


def prepare_output_dir(path: Path, overwrite: bool) -> None:
    if path.exists() and any(path.iterdir()) and not overwrite:
        raise FileExistsError(
            f"output directory already exists and is not empty: {path}. Use --overwrite to replace artifacts."
        )
    path.mkdir(parents=True, exist_ok=True)


def path_for_summary(path: Path) -> str:
    absolute_path = path if path.is_absolute() else (ROOT / path)
    return str(absolute_path.resolve().relative_to(ROOT))


def summarize_template_outputs(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(str(row["template_id"]), []).append(row)

    summaries: list[dict[str, Any]] = []
    for template_id, template_rows in grouped.items():
        meta_scores = [int(row["meta_marker_score"]) for row in template_rows]
        word_counts = [int(row["completion_word_count"]) for row in template_rows]
        summaries.append(
            {
                "template_id": template_id,
                "sample_count": len(template_rows),
                "mean_meta_marker_score": float(np.mean(meta_scores)),
                "meta_marker_fraction": float(np.mean([score > 0 for score in meta_scores])),
                "mean_completion_word_count": float(np.mean(word_counts)),
            }
        )
    return sorted(
        summaries,
        key=lambda row: (
            float(row["meta_marker_fraction"]),
            float(row["mean_meta_marker_score"]),
            -float(row["mean_completion_word_count"]),
        ),
    )


def write_readme(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Base Model Story Prompt Probe",
        "",
        f"- Generated at: `{summary['created_at']}`",
        f"- Model: `{summary['model_id']}`",
        f"- Device: `{summary['device']}`",
        f"- Prompt count: `{summary['prompt_count']}`",
        f"- Max new tokens: `{summary['max_new_tokens']}`",
        f"- Seed base: `{summary['seed']}`",
        f"- Best template by meta-marker heuristic: `{summary['best_template_id']}`",
        "",
        "Template ranking:",
    ]
    for row in summary["template_summaries"]:
        lines.append(
            f"- `{row['template_id']}`: meta fraction `{row['meta_marker_fraction']:.3f}`, "
            f"mean meta score `{row['mean_meta_marker_score']:.3f}`, "
            f"mean words `{row['mean_completion_word_count']:.2f}`"
        )
    lines.extend(
        [
            "",
            "Artifacts:",
            "- `summary.json`",
            "- `outputs.jsonl`",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir or default_output_dir()
    prepare_output_dir(output_dir, overwrite=args.overwrite)

    prompt_rows = load_prompt_rows(args.split_path, max_pairs=args.max_prompts)
    prompt_templates = build_prompt_templates()
    device = select_device(args.device)
    model, tokenizer = load_model_and_tokenizer(args.model_id, device)

    output_rows: list[dict[str, Any]] = []
    for prompt_index, prompt_row in enumerate(prompt_rows):
        for template_index, (template_id, template_text) in enumerate(prompt_templates.items()):
            prompt_text_full = template_text.format(prompt=prompt_row["prompt_text"])
            seed = args.seed + (prompt_index * 100) + template_index
            completion_text, full_text = generate_completion(
                model,
                tokenizer,
                prompt_text=prompt_text_full,
                seed=seed,
                max_new_tokens=args.max_new_tokens,
            )
            output_rows.append(
                {
                    "prompt_id": prompt_row["prompt_id"],
                    "prompt_text": prompt_row["prompt_text"],
                    "template_id": template_id,
                    "prompt_text_full": prompt_text_full,
                    "seed": seed,
                    "completion_text": completion_text,
                    "full_text": full_text,
                    "completion_word_count": len(completion_text.split()),
                    "meta_marker_score": compute_meta_marker_score(completion_text),
                }
            )

    template_summaries = summarize_template_outputs(output_rows)
    summary = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "model_id": args.model_id,
        "device": device,
        "prompt_count": len(prompt_rows),
        "max_new_tokens": args.max_new_tokens,
        "seed": args.seed,
        "split_path": path_for_summary(args.split_path),
        "template_ids": list(prompt_templates),
        "best_template_id": template_summaries[0]["template_id"],
        "template_summaries": template_summaries,
        "outputs_path": "outputs.jsonl",
    }

    write_json(output_dir / "summary.json", summary)
    write_jsonl(output_dir / "outputs.jsonl", output_rows)
    write_readme(output_dir / "README.md", summary)

    print(f"wrote prompt-harness probe artifact to {output_dir}")
    print(f"best template: {summary['best_template_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
