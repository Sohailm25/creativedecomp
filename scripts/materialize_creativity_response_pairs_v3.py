# ABOUTME: Materializes a v3 creativity-vs-plain pilot pair set by rewriting each creative story into a plain counterpart with tighter content preservation.
# ABOUTME: Filters weak rows using overlap and prompt-grounding heuristics so Phase 1 stops treating content drift as creativity structure.

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime
import json
from pathlib import Path
import re
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
DEFAULT_SEED = 3600
DEFAULT_MIN_COUNTERPART_OVERLAP = 0.30
DEFAULT_MAX_NEGATIVE_PROMPT_GROUNDING_DELTA = 0.10
DEFAULT_SOURCE_TEMPLATES_PATH = ROOT / "prompts" / "creative_direction_v1_templates.json"
DEFAULT_PAIR_PATH = ROOT / "prompts" / "creative_direction_v3_pilot_pairs.jsonl"
DEFAULT_RESPONSE_ONLY_PAIR_PATH = ROOT / "prompts" / "creative_direction_v3_response_only_pairs.jsonl"
DEFAULT_REJECTED_PAIR_PATH = ROOT / "prompts" / "creative_direction_v3_rejected_pairs.jsonl"
DEFAULT_METADATA_PATH = ROOT / "prompts" / "creative_direction_v3_metadata.json"
DEFAULT_TEMPLATES_PATH = ROOT / "prompts" / "creative_direction_v3_templates.json"

STOPWORDS = {
    "a",
    "about",
    "above",
    "after",
    "against",
    "all",
    "an",
    "and",
    "any",
    "are",
    "as",
    "at",
    "be",
    "because",
    "been",
    "before",
    "being",
    "below",
    "between",
    "both",
    "but",
    "by",
    "could",
    "did",
    "do",
    "does",
    "doing",
    "down",
    "during",
    "each",
    "few",
    "for",
    "from",
    "further",
    "had",
    "has",
    "have",
    "having",
    "he",
    "her",
    "here",
    "hers",
    "herself",
    "him",
    "himself",
    "his",
    "how",
    "i",
    "if",
    "in",
    "into",
    "is",
    "it",
    "its",
    "itself",
    "just",
    "me",
    "more",
    "most",
    "my",
    "myself",
    "no",
    "nor",
    "not",
    "now",
    "of",
    "off",
    "on",
    "once",
    "only",
    "or",
    "other",
    "our",
    "ours",
    "ourselves",
    "out",
    "over",
    "own",
    "same",
    "she",
    "should",
    "so",
    "some",
    "such",
    "than",
    "that",
    "the",
    "their",
    "theirs",
    "them",
    "themselves",
    "then",
    "there",
    "these",
    "they",
    "this",
    "those",
    "through",
    "to",
    "too",
    "under",
    "until",
    "up",
    "very",
    "was",
    "we",
    "were",
    "what",
    "when",
    "where",
    "which",
    "while",
    "who",
    "whom",
    "why",
    "will",
    "with",
    "you",
    "your",
    "yours",
    "yourself",
    "yourselves",
}


def default_output_dir() -> Path:
    run_date = datetime.now().strftime("%Y%m%d")
    return ROOT / "results" / "creativity_direction" / f"{run_date}-gemma2-2b-response-pairs-v3-pilot"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Materialize a v3 creativity-vs-plain pair set using content-preserving rewrites."
    )
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID)
    parser.add_argument("--split-path", type=Path, default=DEFAULT_SPLIT_PATH)
    parser.add_argument("--source-templates-path", type=Path, default=DEFAULT_SOURCE_TEMPLATES_PATH)
    parser.add_argument("--pair-path", type=Path, default=DEFAULT_PAIR_PATH)
    parser.add_argument("--response-only-pair-path", type=Path, default=DEFAULT_RESPONSE_ONLY_PAIR_PATH)
    parser.add_argument("--rejected-pair-path", type=Path, default=DEFAULT_REJECTED_PAIR_PATH)
    parser.add_argument("--metadata-path", type=Path, default=DEFAULT_METADATA_PATH)
    parser.add_argument("--templates-path", type=Path, default=DEFAULT_TEMPLATES_PATH)
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
            "response_pair_negative_counterpart_prompt": (
                "Rewrite the story below in a plain, literal style.\n"
                "Keep the same characters, setting, sequence of events, and ending.\n"
                "Do not add new plot points, remove major content, or change the point of view.\n\n"
                "Prompt: {prompt}\n\n"
                "Source story:\n{source_story}\n\n"
                "Plain rewrite:\nOnce"
            ),
            "response_pair_extraction_shared_prompt": "Prompt: {prompt}\n\nStory:\nOnce",
            "response_pair_template_control": "Prompt: {prompt}\n\nStory:\nOnce",
        }
    )
    return templates


def append_to_story_opening(opening: str, completion_text: str) -> str:
    completion = completion_text.lstrip()
    spacer = "" if not completion or completion[0] in ",.;:!?)" else " "
    return f"{opening}{spacer}{completion}"


def render_extraction_text(
    prompt_text: str,
    completion_text: str,
    templates: dict[str, str],
) -> str:
    shared_prompt = templates["response_pair_extraction_shared_prompt"].format(prompt=prompt_text)
    return append_to_story_opening(shared_prompt, completion_text)


def render_response_only_text(completion_text: str) -> str:
    return append_to_story_opening("Once", completion_text)


def tokenize_content_words(text: str) -> list[str]:
    return [
        token
        for token in re.findall(r"[A-Za-z']+", text.lower())
        if len(token) > 2 and token not in STOPWORDS
    ]


def compute_content_token_overlap_ratio(reference_text: str, candidate_text: str) -> float:
    reference_tokens = set(tokenize_content_words(reference_text))
    candidate_tokens = set(tokenize_content_words(candidate_text))
    union = reference_tokens | candidate_tokens
    if not union:
        return 0.0
    return float(len(reference_tokens & candidate_tokens) / len(union))


def compute_prompt_grounding_ratio(story_text: str, prompt_text: str) -> float:
    return compute_content_token_overlap_ratio(story_text, prompt_text)


def evaluate_pair_quality(
    prompt_text: str,
    positive_completion_text: str,
    negative_completion_text: str,
    positive_meta_marker_score: int,
    negative_meta_marker_score: int,
    min_counterpart_overlap: float,
    max_negative_prompt_grounding_delta: float,
) -> dict[str, Any]:
    positive_prompt_grounding_ratio = compute_prompt_grounding_ratio(positive_completion_text, prompt_text)
    negative_prompt_grounding_ratio = compute_prompt_grounding_ratio(negative_completion_text, prompt_text)
    counterpart_overlap_ratio = compute_content_token_overlap_ratio(
        positive_completion_text,
        negative_completion_text,
    )
    prompt_grounding_delta = negative_prompt_grounding_ratio - positive_prompt_grounding_ratio
    rejection_reasons: list[str] = []
    if positive_meta_marker_score > 0:
        rejection_reasons.append("positive_meta_marker")
    if negative_meta_marker_score > 0:
        rejection_reasons.append("negative_meta_marker")
    if counterpart_overlap_ratio < min_counterpart_overlap:
        rejection_reasons.append("low_counterpart_overlap")
    if prompt_grounding_delta > max_negative_prompt_grounding_delta:
        rejection_reasons.append("negative_more_prompt_grounded")
    return {
        "accepted": not rejection_reasons,
        "counterpart_overlap_ratio": counterpart_overlap_ratio,
        "positive_prompt_grounding_ratio": positive_prompt_grounding_ratio,
        "negative_prompt_grounding_ratio": negative_prompt_grounding_ratio,
        "prompt_grounding_delta": prompt_grounding_delta,
        "rejection_reasons": rejection_reasons,
    }


def build_response_pair_row(
    prompt_row: dict[str, Any],
    templates: dict[str, str],
    positive_completion_text: str,
    negative_completion_text: str,
    positive_seed: int,
    negative_seed: int,
    quality: dict[str, Any],
) -> dict[str, Any]:
    prompt_text = str(prompt_row["prompt_text"])
    return {
        "split": str(prompt_row.get("split", "pilot")),
        "prompt_id": str(prompt_row["prompt_id"]),
        "prompt_text": prompt_text,
        "positive_source_prompt_text": templates["response_pair_positive_source_prompt"].format(prompt=prompt_text),
        "negative_source_prompt_text": templates["response_pair_negative_counterpart_prompt"].format(
            prompt=prompt_text,
            source_story=append_to_story_opening("Once", positive_completion_text),
        ),
        "negative_generation_mode": "plain_counterpart_rewrite",
        "positive_completion_text": positive_completion_text,
        "negative_completion_text": negative_completion_text,
        "positive_text": render_extraction_text(prompt_text, positive_completion_text, templates),
        "negative_text": render_extraction_text(prompt_text, negative_completion_text, templates),
        "response_only_positive_text": render_response_only_text(positive_completion_text),
        "response_only_negative_text": render_response_only_text(negative_completion_text),
        "template_control_positive_text": templates["response_pair_template_control"].format(prompt=""),
        "template_control_negative_text": templates["response_pair_template_control"].format(prompt=""),
        "positive_seed": positive_seed,
        "negative_seed": negative_seed,
        "positive_word_count": len(positive_completion_text.split()),
        "negative_word_count": len(negative_completion_text.split()),
        "positive_meta_marker_score": compute_meta_marker_score(positive_completion_text),
        "negative_meta_marker_score": compute_meta_marker_score(negative_completion_text),
        "counterpart_overlap_ratio": float(quality["counterpart_overlap_ratio"]),
        "positive_prompt_grounding_ratio": float(quality["positive_prompt_grounding_ratio"]),
        "negative_prompt_grounding_ratio": float(quality["negative_prompt_grounding_ratio"]),
        "prompt_grounding_delta": float(quality["prompt_grounding_delta"]),
        "pair_quality_pass": bool(quality["accepted"]),
        "pair_rejection_reasons": list(quality["rejection_reasons"]),
    }


def build_response_only_pair_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    response_only_rows: list[dict[str, Any]] = []
    for row in rows:
        response_only_row = dict(row)
        response_only_row["positive_text"] = str(row["response_only_positive_text"])
        response_only_row["negative_text"] = str(row["response_only_negative_text"])
        response_only_rows.append(response_only_row)
    return response_only_rows


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


def summarize_quality(rows: list[dict[str, Any]]) -> dict[str, Any]:
    rejection_counts = Counter(
        reason
        for row in rows
        for reason in row.get("pair_rejection_reasons", [])
    )
    counterpart_overlaps = [float(row["counterpart_overlap_ratio"]) for row in rows]
    grounding_deltas = [float(row["prompt_grounding_delta"]) for row in rows]
    return {
        "pair_count": len(rows),
        "accepted_count": sum(bool(row["pair_quality_pass"]) for row in rows),
        "mean_counterpart_overlap_ratio": sum(counterpart_overlaps) / len(counterpart_overlaps),
        "mean_prompt_grounding_delta": sum(grounding_deltas) / len(grounding_deltas),
        "rejection_reason_counts": dict(sorted(rejection_counts.items())),
    }


def path_for_summary(path: Path) -> str:
    absolute_path = path if path.is_absolute() else (ROOT / path)
    return str(absolute_path.resolve().relative_to(ROOT))


def write_readme(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Creativity Response Pairs V3",
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
        f"- Positive source prompt: `{summary['templates']['response_pair_positive_source_prompt']}`",
        f"- Negative rewrite prompt: `{summary['templates']['response_pair_negative_counterpart_prompt']}`",
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
            f"- `{summary['response_only_pair_path']}`",
            f"- `{summary['rejected_pair_path']}`",
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
            prompt_text=templates["response_pair_negative_counterpart_prompt"].format(
                prompt=prompt_text,
                source_story=append_to_story_opening("Once", positive_completion_text),
            ),
            seed=negative_seed,
            max_new_tokens=args.max_new_tokens,
        )
        positive_meta_marker_score = compute_meta_marker_score(positive_completion_text)
        negative_meta_marker_score = compute_meta_marker_score(negative_completion_text)
        quality = evaluate_pair_quality(
            prompt_text=prompt_text,
            positive_completion_text=positive_completion_text,
            negative_completion_text=negative_completion_text,
            positive_meta_marker_score=positive_meta_marker_score,
            negative_meta_marker_score=negative_meta_marker_score,
            min_counterpart_overlap=args.min_counterpart_overlap,
            max_negative_prompt_grounding_delta=args.max_negative_prompt_grounding_delta,
        )
        pair_rows.append(
            build_response_pair_row(
                prompt_row=prompt_row,
                templates=templates,
                positive_completion_text=positive_completion_text,
                negative_completion_text=negative_completion_text,
                positive_seed=positive_seed,
                negative_seed=negative_seed,
                quality=quality,
            )
        )

    accepted_rows = [row for row in pair_rows if bool(row["pair_quality_pass"])]
    rejected_rows = [row for row in pair_rows if not bool(row["pair_quality_pass"])]
    if not accepted_rows:
        raise ValueError("no accepted v3 pair rows were generated")

    response_only_rows = build_response_only_pair_rows(accepted_rows)
    metadata = {
        "split_id": "creative_direction_v3",
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "base_split_path": path_for_summary(args.split_path),
        "pair_generation_method": "creative continuation plus plain counterpart rewrite with quality filtering",
        "pair_count": len(pair_rows),
        "accepted_pair_count": len(accepted_rows),
        "rejected_pair_count": len(rejected_rows),
        "model_id": args.model_id,
        "max_new_tokens": args.max_new_tokens,
        "seed": args.seed,
        "min_counterpart_overlap": args.min_counterpart_overlap,
        "max_negative_prompt_grounding_delta": args.max_negative_prompt_grounding_delta,
        "pair_file": path_for_summary(args.pair_path),
        "response_only_pair_file": path_for_summary(args.response_only_pair_path),
        "rejected_pair_file": path_for_summary(args.rejected_pair_path),
        "templates_file": path_for_summary(args.templates_path),
    }
    quality_summary = summarize_quality(pair_rows)
    summary = {
        "created_at": metadata["created_at"],
        "model_id": args.model_id,
        "device": device,
        "pair_count": len(pair_rows),
        "accepted_count": len(accepted_rows),
        "max_new_tokens": args.max_new_tokens,
        "seed": args.seed,
        "min_counterpart_overlap": args.min_counterpart_overlap,
        "max_negative_prompt_grounding_delta": args.max_negative_prompt_grounding_delta,
        "split_path": path_for_summary(args.split_path),
        "pair_path": path_for_summary(args.pair_path),
        "response_only_pair_path": path_for_summary(args.response_only_pair_path),
        "rejected_pair_path": path_for_summary(args.rejected_pair_path),
        "metadata_path": path_for_summary(args.metadata_path),
        "templates_path": path_for_summary(args.templates_path),
        "templates": {
            "response_pair_positive_source_prompt": templates["response_pair_positive_source_prompt"],
            "response_pair_negative_counterpart_prompt": templates["response_pair_negative_counterpart_prompt"],
            "response_pair_extraction_shared_prompt": templates["response_pair_extraction_shared_prompt"],
        },
        "side_summaries": summarize_pair_rows(accepted_rows),
        **quality_summary,
    }

    write_jsonl(args.pair_path, accepted_rows)
    write_jsonl(args.response_only_pair_path, response_only_rows)
    write_jsonl(args.rejected_pair_path, rejected_rows)
    write_json(args.metadata_path, metadata)
    write_json(args.templates_path, templates)
    write_json(output_dir / "summary.json", summary)
    write_readme(output_dir / "README.md", summary)

    print(f"wrote v3 pair artifact to {output_dir}")
    print(f"accepted pairs: {len(accepted_rows)} / {len(pair_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
