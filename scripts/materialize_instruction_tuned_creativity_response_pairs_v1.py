# ABOUTME: Materializes the matched instruction-tuned creativity counterpart pairs on Gemma 3 270M IT before any decomposition work reopens.
# ABOUTME: Keeps the creativity contrast response-centered by generating creative stories with an explicit story-writing user prompt and then rewriting them plainly as content-preserving counterparts.

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

from materialize_creativity_response_pairs_v3 import (  # noqa: E402
    DEFAULT_MAX_NEGATIVE_PROMPT_GROUNDING_DELTA,
    DEFAULT_MIN_COUNTERPART_OVERLAP,
    evaluate_pair_quality,
    path_for_summary,
    prepare_output_dir,
    summarize_quality,
)
from probe_base_model_story_prompts import compute_meta_marker_score  # noqa: E402
from run_creativity_direction_smoke import (  # noqa: E402
    ROOT,
    load_model_and_tokenizer,
    load_prompt_rows,
    select_device,
    write_json,
    write_jsonl,
)
from run_generation_side_creativity_smoke import generate_completion  # noqa: E402
from run_instruction_tuned_refusal_pivot import render_chat_transcript  # noqa: E402


DEFAULT_MODEL_ID = "google/gemma-3-270m-it"
DEFAULT_SOURCE_SPLIT_PATH = ROOT / "prompts" / "creative_direction_v1_pilot.jsonl"
DEFAULT_TEMPLATES_PATH = ROOT / "prompts" / "creative_direction_it_v1_templates.json"
DEFAULT_PAIR_PATH = ROOT / "prompts" / "creative_direction_it_v1_pilot_pairs.jsonl"
DEFAULT_REJECTED_PAIR_PATH = ROOT / "prompts" / "creative_direction_it_v1_rejected_pairs.jsonl"
DEFAULT_METADATA_PATH = ROOT / "prompts" / "creative_direction_it_v1_metadata.json"
DEFAULT_MAX_PROMPTS = 32
DEFAULT_MAX_NEW_TOKENS = 96
DEFAULT_SEED = 9100


def default_output_dir() -> Path:
    run_date = datetime.now().strftime("%Y%m%d")
    return ROOT / "results" / "creativity_direction" / f"{run_date}-gemma3-270m-it-response-pairs-v1-pilot"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Materialize the matched instruction-tuned creativity counterpart pairs on Gemma 3 270M IT."
    )
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID)
    parser.add_argument("--source-split-path", type=Path, default=DEFAULT_SOURCE_SPLIT_PATH)
    parser.add_argument("--templates-path", type=Path, default=DEFAULT_TEMPLATES_PATH)
    parser.add_argument("--pair-path", type=Path, default=DEFAULT_PAIR_PATH)
    parser.add_argument("--rejected-pair-path", type=Path, default=DEFAULT_REJECTED_PAIR_PATH)
    parser.add_argument("--metadata-path", type=Path, default=DEFAULT_METADATA_PATH)
    parser.add_argument("--max-prompts", type=int, default=DEFAULT_MAX_PROMPTS)
    parser.add_argument("--max-new-tokens", type=int, default=DEFAULT_MAX_NEW_TOKENS)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--min-counterpart-overlap", type=float, default=DEFAULT_MIN_COUNTERPART_OVERLAP)
    parser.add_argument(
        "--max-negative-prompt-grounding-delta",
        type=float,
        default=DEFAULT_MAX_NEGATIVE_PROMPT_GROUNDING_DELTA,
    )
    parser.add_argument("--device", choices=["auto", "mps", "cpu"], default="auto")
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def load_templates(path: Path) -> dict[str, str]:
    templates = json.loads(path.read_text(encoding="utf-8"))
    for key in (
        "neutral_story_user_prompt",
        "prompt_only_creativity_user_prompt",
        "response_pair_negative_counterpart_prompt",
    ):
        if key not in templates:
            raise KeyError(f"missing template key: {key}")
    return templates


def build_positive_source_messages(
    prompt_text: str,
    templates: dict[str, str],
) -> list[dict[str, str]]:
    return [
        {
            "role": "user",
            "content": templates["prompt_only_creativity_user_prompt"].format(prompt=prompt_text),
        }
    ]


def build_negative_counterpart_messages(
    prompt_text: str,
    source_story: str,
    templates: dict[str, str],
) -> list[dict[str, str]]:
    return [
        {
            "role": "user",
            "content": templates["response_pair_negative_counterpart_prompt"].format(
                prompt=prompt_text,
                source_story=source_story,
            ),
        }
    ]


def generate_assistant_completion(
    model,
    tokenizer,
    messages: list[dict[str, str]],
    *,
    seed: int,
    max_new_tokens: int,
) -> str:
    rendered_prompt = render_chat_transcript(
        tokenizer,
        messages,
        add_generation_prompt=True,
    )
    completion_text, _ = generate_completion(
        model,
        tokenizer,
        prompt_text=rendered_prompt,
        seed=seed,
        max_new_tokens=max_new_tokens,
    )
    return completion_text


def build_response_pair_row(
    prompt_row: dict[str, Any],
    positive_assistant_text: str,
    negative_assistant_text: str,
    positive_seed: int,
    negative_seed: int,
    quality: dict[str, Any],
) -> dict[str, Any]:
    return {
        "split": str(prompt_row.get("split", "pilot")),
        "prompt_id": str(prompt_row["prompt_id"]),
        "prompt_text": str(prompt_row["prompt_text"]),
        "negative_generation_mode": "plain_counterpart_rewrite",
        "positive_assistant_text": positive_assistant_text,
        "negative_assistant_text": negative_assistant_text,
        "positive_seed": positive_seed,
        "negative_seed": negative_seed,
        "positive_word_count": len(positive_assistant_text.split()),
        "negative_word_count": len(negative_assistant_text.split()),
        "positive_meta_marker_score": compute_meta_marker_score(positive_assistant_text),
        "negative_meta_marker_score": compute_meta_marker_score(negative_assistant_text),
        "counterpart_overlap_ratio": float(quality["counterpart_overlap_ratio"]),
        "positive_prompt_grounding_ratio": float(quality["positive_prompt_grounding_ratio"]),
        "negative_prompt_grounding_ratio": float(quality["negative_prompt_grounding_ratio"]),
        "prompt_grounding_delta": float(quality["prompt_grounding_delta"]),
        "pair_quality_pass": bool(quality["accepted"]),
        "pair_rejection_reasons": list(quality["rejection_reasons"]),
    }


def summarize_pair_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
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


def write_readme(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Instruction-Tuned Creativity Response Pairs",
        "",
        f"- Generated at: `{summary['created_at']}`",
        f"- Model: `{summary['model_id']}`",
        f"- Device: `{summary['device']}`",
        f"- Candidate prompt count: `{summary['pair_count']}`",
        f"- Accepted pair count: `{summary['accepted_count']}`",
        f"- Max new tokens: `{summary['max_new_tokens']}`",
        f"- Seed base: `{summary['seed']}`",
        f"- Min counterpart overlap: `{summary['min_counterpart_overlap']:.2f}`",
        f"- Max negative prompt-grounding delta: `{summary['max_negative_prompt_grounding_delta']:.2f}`",
        f"- Neutral story prompt: `{summary['templates']['neutral_story_user_prompt']}`",
        f"- Creativity source prompt: `{summary['templates']['prompt_only_creativity_user_prompt']}`",
        f"- Plain rewrite prompt: `{summary['templates']['response_pair_negative_counterpart_prompt']}`",
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
            f"- Mean counterpart overlap: `{summary['mean_counterpart_overlap_ratio']:.3f}`",
            f"- Mean prompt-grounding delta: `{summary['mean_prompt_grounding_delta']:.3f}`",
            "",
            "Rejection counts:",
        ]
    )
    if summary["rejection_reason_counts"]:
        for key, value in summary["rejection_reason_counts"].items():
            lines.append(f"- `{key}`: `{value}`")
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "Artifacts:",
            f"- `{summary['pair_path']}`",
            f"- `{summary['rejected_pair_path']}`",
            f"- `{summary['metadata_path']}`",
            f"- `{summary['templates_path']}`",
            "- `summary.json`",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_pair_materialization(
    *,
    model,
    tokenizer,
    model_id: str,
    prompt_rows: list[dict[str, Any]],
    templates: dict[str, str],
    source_split_path: Path,
    templates_path: Path,
    pair_path: Path,
    rejected_pair_path: Path,
    metadata_path: Path,
    output_dir: Path,
    max_new_tokens: int,
    seed: int,
    min_counterpart_overlap: float,
    max_negative_prompt_grounding_delta: float,
    device: str,
    overwrite: bool,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    prepare_output_dir(output_dir, overwrite=overwrite)

    pair_rows: list[dict[str, Any]] = []
    for prompt_index, prompt_row in enumerate(prompt_rows):
        prompt_text = str(prompt_row["prompt_text"])
        positive_seed = seed + (prompt_index * 2)
        negative_seed = seed + (prompt_index * 2) + 1
        positive_assistant_text = generate_assistant_completion(
            model,
            tokenizer,
            build_positive_source_messages(prompt_text, templates),
            seed=positive_seed,
            max_new_tokens=max_new_tokens,
        )
        negative_assistant_text = generate_assistant_completion(
            model,
            tokenizer,
            build_negative_counterpart_messages(
                prompt_text,
                positive_assistant_text,
                templates,
            ),
            seed=negative_seed,
            max_new_tokens=max_new_tokens,
        )
        quality = evaluate_pair_quality(
            prompt_text=prompt_text,
            positive_completion_text=positive_assistant_text,
            negative_completion_text=negative_assistant_text,
            positive_meta_marker_score=compute_meta_marker_score(positive_assistant_text),
            negative_meta_marker_score=compute_meta_marker_score(negative_assistant_text),
            min_counterpart_overlap=min_counterpart_overlap,
            max_negative_prompt_grounding_delta=max_negative_prompt_grounding_delta,
        )
        pair_rows.append(
            build_response_pair_row(
                prompt_row=prompt_row,
                positive_assistant_text=positive_assistant_text,
                negative_assistant_text=negative_assistant_text,
                positive_seed=positive_seed,
                negative_seed=negative_seed,
                quality=quality,
            )
        )

    accepted_rows = [row for row in pair_rows if bool(row["pair_quality_pass"])]
    rejected_rows = [row for row in pair_rows if not bool(row["pair_quality_pass"])]
    if not accepted_rows:
        raise ValueError("no accepted instruction-tuned creativity pair rows were generated")

    pair_path.parent.mkdir(parents=True, exist_ok=True)
    rejected_pair_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(pair_path, accepted_rows)
    write_jsonl(rejected_pair_path, rejected_rows)

    metadata = {
        "split_id": "creative_direction_it_v1",
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "model_id": model_id,
        "pair_file": path_for_summary(pair_path),
        "rejected_pair_file": path_for_summary(rejected_pair_path),
        "source_split_file": path_for_summary(source_split_path),
        "templates_file": path_for_summary(templates_path),
        "pilot_count": len(accepted_rows),
        "candidate_prompt_count": len(prompt_rows),
    }
    write_json(metadata_path, metadata)

    quality_summary = summarize_quality(pair_rows)
    summary = {
        "created_at": metadata["created_at"],
        "model_id": model_id,
        "device": device,
        "pair_count": len(prompt_rows),
        "accepted_count": len(accepted_rows),
        "max_new_tokens": max_new_tokens,
        "seed": seed,
        "min_counterpart_overlap": min_counterpart_overlap,
        "max_negative_prompt_grounding_delta": max_negative_prompt_grounding_delta,
        "pair_path": path_for_summary(pair_path),
        "rejected_pair_path": path_for_summary(rejected_pair_path),
        "metadata_path": path_for_summary(metadata_path),
        "templates_path": path_for_summary(templates_path),
        "templates": templates,
        "side_summaries": summarize_pair_rows(accepted_rows),
        **quality_summary,
    }
    write_json(output_dir / "summary.json", summary)
    write_readme(output_dir / "README.md", summary)
    return summary, accepted_rows


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir or default_output_dir()
    prompt_rows = load_prompt_rows(args.source_split_path, max_pairs=args.max_prompts)
    templates = load_templates(args.templates_path)
    device = select_device(args.device)
    model, tokenizer = load_model_and_tokenizer(args.model_id, device)
    run_pair_materialization(
        model=model,
        tokenizer=tokenizer,
        model_id=args.model_id,
        prompt_rows=prompt_rows,
        templates=templates,
        source_split_path=args.source_split_path,
        templates_path=args.templates_path,
        pair_path=args.pair_path,
        rejected_pair_path=args.rejected_pair_path,
        metadata_path=args.metadata_path,
        output_dir=output_dir,
        max_new_tokens=args.max_new_tokens,
        seed=args.seed,
        min_counterpart_overlap=args.min_counterpart_overlap,
        max_negative_prompt_grounding_delta=args.max_negative_prompt_grounding_delta,
        device=device,
        overwrite=args.overwrite,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
