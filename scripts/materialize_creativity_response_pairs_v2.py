# ABOUTME: Materializes a response-centered creativity-vs-plain pilot pair set using shared extraction wrappers and continuation-style source prompts.
# ABOUTME: Replaces the v1 instruction-template contrast with matched positive and negative story continuations before the next layer sweep.

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import sys
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from probe_base_model_story_prompts import compute_meta_marker_score  # noqa: E402
from run_creativity_direction_smoke import (  # noqa: E402
    ROOT,
    DEFAULT_MODEL_ID,
    DEFAULT_SPLIT_PATH,
    load_model_and_tokenizer,
    load_prompt_rows,
    load_templates,
    select_device,
    write_json,
    write_jsonl,
)
from run_generation_side_creativity_smoke import generate_completion  # noqa: E402


DEFAULT_MAX_PROMPTS = 32
DEFAULT_MAX_NEW_TOKENS = 96
DEFAULT_SEED = 2400
DEFAULT_SOURCE_TEMPLATES_PATH = ROOT / "prompts" / "creative_direction_v1_templates.json"
DEFAULT_PAIR_PATH = ROOT / "prompts" / "creative_direction_v2_pilot_pairs.jsonl"
DEFAULT_METADATA_PATH = ROOT / "prompts" / "creative_direction_v2_metadata.json"
DEFAULT_TEMPLATES_PATH = ROOT / "prompts" / "creative_direction_v2_templates.json"


def default_output_dir() -> Path:
    run_date = datetime.now().strftime("%Y%m%d")
    return ROOT / "results" / "creativity_direction" / f"{run_date}-gemma2-2b-response-pairs-v2-pilot"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Materialize a response-centered creativity-vs-plain pilot pair set."
    )
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID)
    parser.add_argument("--split-path", type=Path, default=DEFAULT_SPLIT_PATH)
    parser.add_argument("--source-templates-path", type=Path, default=DEFAULT_SOURCE_TEMPLATES_PATH)
    parser.add_argument("--pair-path", type=Path, default=DEFAULT_PAIR_PATH)
    parser.add_argument("--metadata-path", type=Path, default=DEFAULT_METADATA_PATH)
    parser.add_argument("--templates-path", type=Path, default=DEFAULT_TEMPLATES_PATH)
    parser.add_argument("--max-prompts", type=int, default=DEFAULT_MAX_PROMPTS)
    parser.add_argument("--max-new-tokens", type=int, default=DEFAULT_MAX_NEW_TOKENS)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--device", choices=["auto", "mps", "cpu"], default="auto")
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def prepare_output_dir(path: Path, overwrite: bool) -> None:
    if path.exists() and any(path.iterdir()) and not overwrite:
        raise FileExistsError(
            f"output directory already exists and is not empty: {path}. Use --overwrite to replace artifacts."
        )
    path.mkdir(parents=True, exist_ok=True)


def build_response_pair_templates(base_templates: dict[str, str]) -> dict[str, str]:
    templates = dict(base_templates)
    templates.update(
        {
            "generation_plain_story_opening": "Prompt: {prompt}\n\nPlain story:\nOnce",
            "response_pair_positive_source_prompt": "Prompt: {prompt}\n\nCreative story:\nOnce",
            "response_pair_negative_source_prompt": "Prompt: {prompt}\n\nPlain story:\nOnce",
            "response_pair_extraction_shared_prompt": "Prompt: {prompt}\n\nStory:\nOnce",
            "response_pair_template_control": "Prompt: {prompt}\n\nStory:\nOnce",
        }
    )
    return templates


def render_extraction_text(
    prompt_text: str,
    completion_text: str,
    templates: dict[str, str],
) -> str:
    shared_prompt = templates["response_pair_extraction_shared_prompt"].format(prompt=prompt_text)
    completion = completion_text.lstrip()
    spacer = "" if not completion or completion[0] in ",.;:!?)" else " "
    return f"{shared_prompt}{spacer}{completion}"


def build_response_pair_row(
    prompt_row: dict[str, Any],
    templates: dict[str, str],
    positive_completion_text: str,
    negative_completion_text: str,
    positive_seed: int,
    negative_seed: int,
) -> dict[str, Any]:
    prompt_text = str(prompt_row["prompt_text"])
    return {
        "split": str(prompt_row.get("split", "pilot")),
        "prompt_id": str(prompt_row["prompt_id"]),
        "prompt_text": prompt_text,
        "positive_source_prompt_text": templates["response_pair_positive_source_prompt"].format(prompt=prompt_text),
        "negative_source_prompt_text": templates["response_pair_negative_source_prompt"].format(prompt=prompt_text),
        "positive_completion_text": positive_completion_text,
        "negative_completion_text": negative_completion_text,
        "positive_text": render_extraction_text(prompt_text, positive_completion_text, templates),
        "negative_text": render_extraction_text(prompt_text, negative_completion_text, templates),
        "template_control_positive_text": templates["response_pair_template_control"].format(prompt=""),
        "template_control_negative_text": templates["response_pair_template_control"].format(prompt=""),
        "positive_seed": positive_seed,
        "negative_seed": negative_seed,
        "positive_word_count": len(positive_completion_text.split()),
        "negative_word_count": len(negative_completion_text.split()),
        "positive_meta_marker_score": compute_meta_marker_score(positive_completion_text),
        "negative_meta_marker_score": compute_meta_marker_score(negative_completion_text),
    }


def summarize_pair_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summaries = []
    for side in ("positive", "negative"):
        word_counts = [int(row[f"{side}_word_count"]) for row in rows]
        meta_scores = [int(row[f"{side}_meta_marker_score"]) for row in rows]
        summaries.append(
            {
                "side": side,
                "sample_count": len(rows),
                "mean_word_count": sum(word_counts) / len(word_counts),
                "mean_meta_marker_score": sum(meta_scores) / len(meta_scores),
                "meta_marker_fraction": sum(score > 0 for score in meta_scores) / len(meta_scores),
            }
        )
    return summaries


def path_for_summary(path: Path) -> str:
    absolute_path = path if path.is_absolute() else (ROOT / path)
    return str(absolute_path.resolve().relative_to(ROOT))


def write_readme(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Creativity Response Pairs V2",
        "",
        f"- Generated at: `{summary['created_at']}`",
        f"- Model: `{summary['model_id']}`",
        f"- Device: `{summary['device']}`",
        f"- Pair count: `{summary['pair_count']}`",
        f"- Max new tokens: `{summary['max_new_tokens']}`",
        f"- Seed base: `{summary['seed']}`",
        f"- Positive source prompt: `{summary['templates']['response_pair_positive_source_prompt']}`",
        f"- Negative source prompt: `{summary['templates']['response_pair_negative_source_prompt']}`",
        f"- Shared extraction prompt: `{summary['templates']['response_pair_extraction_shared_prompt']}`",
        "",
        "Side summaries:",
    ]
    for row in summary["side_summaries"]:
        lines.append(
            f"- `{row['side']}`: mean words `{row['mean_word_count']:.2f}`, "
            f"meta fraction `{row['meta_marker_fraction']:.3f}`, "
            f"mean meta score `{row['mean_meta_marker_score']:.3f}`"
        )
    lines.extend(
        [
            "",
            "Artifacts:",
            f"- `{summary['pair_path']}`",
            f"- `{summary['metadata_path']}`",
            f"- `{summary['templates_path']}`",
            "- `summary.json`",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir or default_output_dir()
    prepare_output_dir(output_dir, overwrite=args.overwrite)

    prompt_rows = load_prompt_rows(args.split_path, max_pairs=args.max_prompts)
    base_templates = load_templates(args.source_templates_path)
    templates = build_response_pair_templates(base_templates)

    device = select_device(args.device)
    model, tokenizer = load_model_and_tokenizer(args.model_id, device)

    pair_rows: list[dict[str, Any]] = []
    for prompt_index, prompt_row in enumerate(prompt_rows):
        prompt_text = str(prompt_row["prompt_text"])
        positive_seed = args.seed + (prompt_index * 2)
        negative_seed = args.seed + (prompt_index * 2) + 1
        positive_completion_text, _ = generate_completion(
            model,
            tokenizer,
            prompt_text=templates["response_pair_positive_source_prompt"].format(prompt=prompt_text),
            seed=positive_seed,
            max_new_tokens=args.max_new_tokens,
        )
        negative_completion_text, _ = generate_completion(
            model,
            tokenizer,
            prompt_text=templates["response_pair_negative_source_prompt"].format(prompt=prompt_text),
            seed=negative_seed,
            max_new_tokens=args.max_new_tokens,
        )
        pair_rows.append(
            build_response_pair_row(
                prompt_row=prompt_row,
                templates=templates,
                positive_completion_text=positive_completion_text,
                negative_completion_text=negative_completion_text,
                positive_seed=positive_seed,
                negative_seed=negative_seed,
            )
        )

    metadata = {
        "split_id": "creative_direction_v2",
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "base_split_path": path_for_summary(args.split_path),
        "pair_generation_method": "same-prompt continuation pair generation with shared extraction wrapper",
        "pair_count": len(pair_rows),
        "model_id": args.model_id,
        "max_new_tokens": args.max_new_tokens,
        "seed": args.seed,
        "pair_file": path_for_summary(args.pair_path),
        "templates_file": path_for_summary(args.templates_path),
    }
    side_summaries = summarize_pair_rows(pair_rows)
    summary = {
        "created_at": metadata["created_at"],
        "model_id": args.model_id,
        "device": device,
        "pair_count": len(pair_rows),
        "max_new_tokens": args.max_new_tokens,
        "seed": args.seed,
        "split_path": path_for_summary(args.split_path),
        "pair_path": path_for_summary(args.pair_path),
        "metadata_path": path_for_summary(args.metadata_path),
        "templates_path": path_for_summary(args.templates_path),
        "templates": {
            "response_pair_positive_source_prompt": templates["response_pair_positive_source_prompt"],
            "response_pair_negative_source_prompt": templates["response_pair_negative_source_prompt"],
            "response_pair_extraction_shared_prompt": templates["response_pair_extraction_shared_prompt"],
        },
        "side_summaries": side_summaries,
    }

    args.pair_path.write_text("", encoding="utf-8") if False else None
    write_jsonl(args.pair_path, pair_rows)
    write_json(args.metadata_path, metadata)
    write_json(args.templates_path, templates)
    write_json(output_dir / "summary.json", summary)
    write_readme(output_dir / "README.md", summary)

    print(f"wrote response-pair artifact to {output_dir}")
    print(f"pair file: {args.pair_path}")
    print(f"pair count: {len(pair_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
