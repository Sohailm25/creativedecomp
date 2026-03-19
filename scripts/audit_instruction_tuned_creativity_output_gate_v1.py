# ABOUTME: Builds a blinded manual-audit packet from the cached instruction-tuned creativity gate without regenerating outputs.
# ABOUTME: Scores manual annotations back against hidden condition labels so the matched creativity continuation does not trust the collapsed automatic judge.

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import random
import sys
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from audit_creativity_output_gate_v1 import (  # noqa: E402
    load_jsonl,
    map_label_to_condition_id,
    normalize_winner_label,
    prepare_output_dir,
    select_prompt_ids_for_audit,
)
from run_creativity_direction_smoke import (  # noqa: E402
    ROOT,
    write_json,
    write_jsonl,
)


DEFAULT_ARTIFACT_DIR = ROOT / "results" / "steering_eval" / "20260319-gemma3-270m-it-output-gate-v1"
DEFAULT_REFERENCE_CONDITION_ID = "neutral_unsteered"
DEFAULT_SAMPLE_SIZE = 12
DEFAULT_SEED = 20260319
DEFAULT_AXIS_NAMES = ["prompt_grounded_creativity", "coherence"]


def default_output_dir() -> Path:
    run_date = datetime.now().strftime("%Y%m%d")
    return ROOT / "results" / "steering_eval" / f"{run_date}-gemma3-270m-it-output-gate-v1-manual-audit"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build and score a blinded manual audit from cached instruction-tuned creativity outputs."
    )
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--reference-condition-id", default=DEFAULT_REFERENCE_CONDITION_ID)
    parser.add_argument("--candidate-condition-ids", default=None)
    parser.add_argument("--sample-size", type=int, default=DEFAULT_SAMPLE_SIZE)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--annotations-path", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def parse_candidate_condition_ids_argument(raw_value: str | None) -> list[str] | None:
    if raw_value is None:
        return None
    candidate_condition_ids = [
        token.strip()
        for token in raw_value.split(",")
        if token.strip()
    ]
    deduped_candidate_condition_ids: list[str] = []
    for candidate_condition_id in candidate_condition_ids:
        if candidate_condition_id not in deduped_candidate_condition_ids:
            deduped_candidate_condition_ids.append(candidate_condition_id)
    return deduped_candidate_condition_ids


def resolve_candidate_condition_ids(
    output_rows: list[dict[str, Any]],
    reference_condition_id: str,
    candidate_condition_ids: list[str] | None,
) -> list[str]:
    available_condition_ids = sorted({str(row["condition_id"]) for row in output_rows})
    if reference_condition_id not in available_condition_ids:
        raise ValueError(f"missing reference condition id: {reference_condition_id}")

    if candidate_condition_ids is None:
        resolved_candidate_condition_ids = [
            condition_id
            for condition_id in available_condition_ids
            if condition_id != reference_condition_id
        ]
    else:
        resolved_candidate_condition_ids = []
        for candidate_condition_id in candidate_condition_ids:
            if candidate_condition_id == reference_condition_id:
                raise ValueError("candidate condition ids must exclude the reference condition")
            if candidate_condition_id not in available_condition_ids:
                raise ValueError(f"missing candidate condition id: {candidate_condition_id}")
            if candidate_condition_id not in resolved_candidate_condition_ids:
                resolved_candidate_condition_ids.append(candidate_condition_id)

    if not resolved_candidate_condition_ids:
        raise ValueError("need at least one candidate condition id for the audit")
    return resolved_candidate_condition_ids


def build_condition_lookup(output_rows: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    return {
        (str(row["prompt_id"]), str(row["condition_id"])): row
        for row in output_rows
    }


def build_blinded_audit_rows(
    output_rows: list[dict[str, Any]],
    candidate_condition_ids: list[str],
    reference_condition_id: str,
    selected_prompt_ids: list[str],
    seed: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    lookup = build_condition_lookup(output_rows)
    rng = random.Random(seed)
    blinded_rows: list[dict[str, Any]] = []
    answer_key_rows: list[dict[str, Any]] = []

    for comparison_index, candidate_condition_id in enumerate(candidate_condition_ids, start=1):
        comparison_id = f"{candidate_condition_id}_vs_{reference_condition_id}"
        for prompt_index, prompt_id in enumerate(selected_prompt_ids, start=1):
            candidate_row = lookup[(prompt_id, candidate_condition_id)]
            reference_row = lookup[(prompt_id, reference_condition_id)]
            audit_pair_id = f"audit-{comparison_index:02d}-{prompt_index:02d}"
            candidate_first = rng.random() < 0.5
            story_a_row = candidate_row if candidate_first else reference_row
            story_b_row = reference_row if candidate_first else candidate_row

            blinded_rows.append(
                {
                    "audit_pair_id": audit_pair_id,
                    "prompt_id": prompt_id,
                    "prompt_text": candidate_row["prompt_text"],
                    "story_a_text": story_a_row["completion_text"],
                    "story_b_text": story_b_row["completion_text"],
                }
            )
            answer_key_rows.append(
                {
                    "audit_pair_id": audit_pair_id,
                    "comparison_id": comparison_id,
                    "candidate_condition_id": candidate_condition_id,
                    "reference_condition_id": reference_condition_id,
                    "prompt_id": prompt_id,
                    "prompt_text": candidate_row["prompt_text"],
                    "story_a_condition_id": story_a_row["condition_id"],
                    "story_b_condition_id": story_b_row["condition_id"],
                }
            )

    return blinded_rows, answer_key_rows


def build_annotation_template_rows(blinded_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "audit_pair_id": row["audit_pair_id"],
            "prompt_grounded_creativity_winner_label": "",
            "coherence_winner_label": "",
            "notes": "",
        }
        for row in blinded_rows
    ]


def summarize_manual_annotations(
    answer_key_rows: list[dict[str, Any]],
    annotation_rows: list[dict[str, Any]],
    axis_names: list[str],
) -> dict[str, Any]:
    answer_key_by_pair_id = {
        str(row["audit_pair_id"]): row
        for row in answer_key_rows
    }
    annotation_rows_by_pair_id = {
        str(row["audit_pair_id"]): row
        for row in annotation_rows
    }
    if set(answer_key_by_pair_id) != set(annotation_rows_by_pair_id):
        raise ValueError("annotation rows must match the blinded audit packet exactly")

    comparison_order: list[str] = []
    rows_by_comparison: dict[str, list[dict[str, Any]]] = {}
    for row in answer_key_rows:
        comparison_id = str(row["comparison_id"])
        if comparison_id not in rows_by_comparison:
            comparison_order.append(comparison_id)
            rows_by_comparison[comparison_id] = []
        rows_by_comparison[comparison_id].append(row)

    comparison_summaries: list[dict[str, Any]] = []
    for comparison_id in comparison_order:
        comparison_rows = rows_by_comparison[comparison_id]
        candidate_condition_id = str(comparison_rows[0]["candidate_condition_id"])
        reference_condition_id = str(comparison_rows[0]["reference_condition_id"])
        comparison_summary: dict[str, Any] = {
            "comparison_id": comparison_id,
            "candidate_condition_id": candidate_condition_id,
            "reference_condition_id": reference_condition_id,
            "sample_count": len(comparison_rows),
        }
        for axis_name in axis_names:
            winner_condition_ids: list[str] = []
            for answer_key_row in comparison_rows:
                annotation_row = annotation_rows_by_pair_id[str(answer_key_row["audit_pair_id"])]
                winner_label = normalize_winner_label(annotation_row[f"{axis_name}_winner_label"])
                winner_condition_ids.append(
                    map_label_to_condition_id(
                        winner_label=winner_label,
                        story_a_condition_id=str(answer_key_row["story_a_condition_id"]),
                        story_b_condition_id=str(answer_key_row["story_b_condition_id"]),
                    )
                )

            comparison_summary[f"{axis_name}_candidate_win_fraction"] = sum(
                winner_condition_id == candidate_condition_id
                for winner_condition_id in winner_condition_ids
            ) / len(winner_condition_ids)
            comparison_summary[f"{axis_name}_reference_win_fraction"] = sum(
                winner_condition_id == reference_condition_id
                for winner_condition_id in winner_condition_ids
            ) / len(winner_condition_ids)
            comparison_summary[f"{axis_name}_tie_fraction"] = sum(
                winner_condition_id == "tie"
                for winner_condition_id in winner_condition_ids
            ) / len(winner_condition_ids)

        comparison_summaries.append(comparison_summary)

    return {
        "sample_count": len(answer_key_rows),
        "comparison_summaries": comparison_summaries,
    }


def write_blinded_packet(path: Path, blinded_rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Instruction-Tuned Creativity Output Gate Manual Audit Packet",
        "",
        "Rubric:",
        "- `prompt_grounded_creativity`: choose the story that is more specific, concrete, less generic, and more meaningfully novel while still fitting the prompt. If one story is more novel but less grounded, answer `tie`.",
        "- `coherence`: choose the story that is more readable, internally consistent, and less broken or repetitive.",
        "- Allowed labels per axis: `A`, `B`, or `tie`.",
        "",
    ]
    for row in blinded_rows:
        lines.extend(
            [
                f"## {row['audit_pair_id']}",
                "",
                "Prompt:",
                row["prompt_text"],
                "",
                "Story A:",
                row["story_a_text"],
                "",
                "Story B:",
                row["story_b_text"],
                "",
            ]
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_readme(path: Path, summary: dict[str, Any], has_annotations: bool) -> None:
    lines = [
        "# Instruction-Tuned Creativity Output Gate Manual Audit",
        "",
        f"- Generated at: `{summary['created_at']}`",
        f"- Source artifact: `{summary['artifact_dir']}`",
        f"- Candidate conditions: `{summary['candidate_condition_ids']}`",
        f"- Reference condition: `{summary['reference_condition_id']}`",
        f"- Sample size: `{summary['sample_count']}`",
        f"- Seed: `{summary['seed']}`",
        "",
        "Artifacts:",
        "- `blinded_pairs.jsonl`",
        "- `blinded_packet.md`",
        "- `answer_key.jsonl`",
        "- `manual_annotations_template.jsonl`",
    ]
    if has_annotations:
        lines.extend(
            [
                "- `manual_annotations.jsonl`",
                "- `summary.json`",
                "",
                "Manual audit summary:",
            ]
        )
        for row in summary["comparison_summaries"]:
            lines.append(
                f"- `{row['comparison_id']}`: prompt-grounded creativity candidate win `{row['prompt_grounded_creativity_candidate_win_fraction']:.3f}`, "
                f"reference win `{row['prompt_grounded_creativity_reference_win_fraction']:.3f}`, "
                f"coherence candidate win `{row['coherence_candidate_win_fraction']:.3f}`, "
                f"coherence reference win `{row['coherence_reference_win_fraction']:.3f}`"
            )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir or default_output_dir()
    prepare_output_dir(output_dir, overwrite=args.overwrite)

    output_rows = load_jsonl(args.artifact_dir / "generated_outputs.jsonl")
    candidate_condition_ids = resolve_candidate_condition_ids(
        output_rows=output_rows,
        reference_condition_id=args.reference_condition_id,
        candidate_condition_ids=parse_candidate_condition_ids_argument(args.candidate_condition_ids),
    )
    selected_prompt_ids = select_prompt_ids_for_audit(
        prompt_ids=[str(row["prompt_id"]) for row in output_rows],
        sample_size=args.sample_size,
        seed=args.seed,
    )
    blinded_rows, answer_key_rows = build_blinded_audit_rows(
        output_rows=output_rows,
        candidate_condition_ids=candidate_condition_ids,
        reference_condition_id=args.reference_condition_id,
        selected_prompt_ids=selected_prompt_ids,
        seed=args.seed,
    )
    annotation_template_rows = build_annotation_template_rows(blinded_rows)

    write_jsonl(output_dir / "blinded_pairs.jsonl", blinded_rows)
    write_jsonl(output_dir / "answer_key.jsonl", answer_key_rows)
    write_jsonl(output_dir / "manual_annotations_template.jsonl", annotation_template_rows)
    write_blinded_packet(output_dir / "blinded_packet.md", blinded_rows)

    summary: dict[str, Any] = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "artifact_dir": str(args.artifact_dir.resolve().relative_to(ROOT)),
        "candidate_condition_ids": candidate_condition_ids,
        "reference_condition_id": args.reference_condition_id,
        "sample_count": len(blinded_rows),
        "seed": args.seed,
    }

    has_annotations = args.annotations_path is not None
    if has_annotations:
        annotation_rows = load_jsonl(args.annotations_path)
        summary.update(
            summarize_manual_annotations(
                answer_key_rows=answer_key_rows,
                annotation_rows=annotation_rows,
                axis_names=DEFAULT_AXIS_NAMES,
            )
        )
        write_jsonl(output_dir / "manual_annotations.jsonl", annotation_rows)
        write_json(output_dir / "summary.json", summary)

    write_readme(output_dir / "README.md", summary, has_annotations=has_annotations)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
