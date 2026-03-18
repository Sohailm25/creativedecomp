# ABOUTME: Builds a blinded manual-audit packet from the cached output-gate artifact without regenerating stories.
# ABOUTME: Scores manual annotations back against hidden condition labels so the metric follow-up stays falsifiable.

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import random
import sys
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from run_creativity_direction_smoke import (  # noqa: E402
    ROOT,
    write_json,
    write_jsonl,
)


DEFAULT_ARTIFACT_DIR = ROOT / "results" / "steering_eval" / "20260318-gemma2-2b-output-gate-v1"
DEFAULT_CANDIDATE_CONDITION_ID = "creative_prompt_unsteered"
DEFAULT_REFERENCE_CONDITION_ID = "neutral_unsteered"
DEFAULT_SAMPLE_SIZE = 12
DEFAULT_SEED = 20260318
DEFAULT_AXIS_NAMES = ["prompt_grounded_creativity", "coherence"]


def default_output_dir() -> Path:
    run_date = datetime.now().strftime("%Y%m%d")
    return ROOT / "results" / "steering_eval" / f"{run_date}-gemma2-2b-output-gate-v1-manual-audit"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build and score a blinded manual-audit packet from cached output-gate stories."
    )
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--candidate-condition-id", default=DEFAULT_CANDIDATE_CONDITION_ID)
    parser.add_argument("--reference-condition-id", default=DEFAULT_REFERENCE_CONDITION_ID)
    parser.add_argument("--sample-size", type=int, default=DEFAULT_SAMPLE_SIZE)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--annotations-path", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def prepare_output_dir(path: Path, overwrite: bool) -> None:
    if path.exists() and any(path.iterdir()) and not overwrite:
        raise FileExistsError(
            f"output directory already exists and is not empty: {path}. Use --overwrite to replace artifacts."
        )
    path.mkdir(parents=True, exist_ok=True)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def select_prompt_ids_for_audit(
    prompt_ids: list[str],
    sample_size: int,
    seed: int,
) -> list[str]:
    deduped_prompt_ids = sorted(set(prompt_ids))
    rng = random.Random(seed)
    rng.shuffle(deduped_prompt_ids)
    return deduped_prompt_ids[: min(sample_size, len(deduped_prompt_ids))]


def build_condition_lookup(output_rows: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    return {
        (str(row["prompt_id"]), str(row["condition_id"])): row
        for row in output_rows
    }


def build_blinded_audit_rows(
    output_rows: list[dict[str, Any]],
    candidate_condition_id: str,
    reference_condition_id: str,
    selected_prompt_ids: list[str],
    seed: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    lookup = build_condition_lookup(output_rows)
    rng = random.Random(seed)
    blinded_rows: list[dict[str, Any]] = []
    answer_key_rows: list[dict[str, Any]] = []

    for index, prompt_id in enumerate(selected_prompt_ids, start=1):
        candidate_row = lookup[(prompt_id, candidate_condition_id)]
        reference_row = lookup[(prompt_id, reference_condition_id)]
        audit_pair_id = f"audit-{index:02d}-{prompt_id}"
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


def normalize_winner_label(raw_value: str) -> str:
    normalized = str(raw_value).strip().lower()
    if normalized in {"a", "b"}:
        return normalized.upper()
    if normalized == "tie":
        return "tie"
    raise ValueError(f"invalid winner label: {raw_value!r}")


def map_label_to_condition_id(
    winner_label: str,
    story_a_condition_id: str,
    story_b_condition_id: str,
) -> str:
    if winner_label == "A":
        return story_a_condition_id
    if winner_label == "B":
        return story_b_condition_id
    return "tie"


def summarize_manual_annotations(
    answer_key_rows: list[dict[str, Any]],
    annotation_rows: list[dict[str, Any]],
    candidate_condition_id: str,
    reference_condition_id: str,
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

    summary: dict[str, Any] = {
        "sample_count": len(answer_key_rows),
    }
    for axis_name in axis_names:
        winner_condition_ids: list[str] = []
        for audit_pair_id, answer_key_row in answer_key_by_pair_id.items():
            annotation_row = annotation_rows_by_pair_id[audit_pair_id]
            winner_label = normalize_winner_label(annotation_row[f"{axis_name}_winner_label"])
            winner_condition_ids.append(
                map_label_to_condition_id(
                    winner_label=winner_label,
                    story_a_condition_id=str(answer_key_row["story_a_condition_id"]),
                    story_b_condition_id=str(answer_key_row["story_b_condition_id"]),
                )
            )

        summary[f"{axis_name}_candidate_win_fraction"] = sum(
            winner_condition_id == candidate_condition_id
            for winner_condition_id in winner_condition_ids
        ) / len(winner_condition_ids)
        summary[f"{axis_name}_reference_win_fraction"] = sum(
            winner_condition_id == reference_condition_id
            for winner_condition_id in winner_condition_ids
        ) / len(winner_condition_ids)
        summary[f"{axis_name}_tie_fraction"] = sum(
            winner_condition_id == "tie"
            for winner_condition_id in winner_condition_ids
        ) / len(winner_condition_ids)

    return summary


def write_blinded_packet(path: Path, blinded_rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Output Gate Manual Audit Packet",
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
        "# Output Gate Manual Audit",
        "",
        f"- Generated at: `{summary['created_at']}`",
        f"- Source artifact: `{summary['artifact_dir']}`",
        f"- Candidate condition: `{summary['candidate_condition_id']}`",
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
                f"- `prompt_grounded_creativity`: candidate win `{summary['prompt_grounded_creativity_candidate_win_fraction']:.3f}`, reference win `{summary['prompt_grounded_creativity_reference_win_fraction']:.3f}`, tie `{summary['prompt_grounded_creativity_tie_fraction']:.3f}`",
                f"- `coherence`: candidate win `{summary['coherence_candidate_win_fraction']:.3f}`, reference win `{summary['coherence_reference_win_fraction']:.3f}`, tie `{summary['coherence_tie_fraction']:.3f}`",
            ]
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir or default_output_dir()
    prepare_output_dir(output_dir, overwrite=args.overwrite)

    generated_outputs_path = args.artifact_dir / "generated_outputs.jsonl"
    output_rows = load_jsonl(generated_outputs_path)
    selected_prompt_ids = select_prompt_ids_for_audit(
        prompt_ids=[str(row["prompt_id"]) for row in output_rows],
        sample_size=args.sample_size,
        seed=args.seed,
    )
    blinded_rows, answer_key_rows = build_blinded_audit_rows(
        output_rows=output_rows,
        candidate_condition_id=args.candidate_condition_id,
        reference_condition_id=args.reference_condition_id,
        selected_prompt_ids=selected_prompt_ids,
        seed=args.seed,
    )

    annotation_template_rows = build_annotation_template_rows(blinded_rows)
    summary: dict[str, Any] = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "artifact_dir": str(args.artifact_dir.resolve().relative_to(ROOT)),
        "candidate_condition_id": args.candidate_condition_id,
        "reference_condition_id": args.reference_condition_id,
        "sample_count": len(blinded_rows),
        "seed": args.seed,
    }

    has_annotations = args.annotations_path is not None and args.annotations_path.exists()
    if has_annotations:
        annotation_rows = load_jsonl(args.annotations_path)
        summary.update(
            summarize_manual_annotations(
                answer_key_rows=answer_key_rows,
                annotation_rows=annotation_rows,
                candidate_condition_id=args.candidate_condition_id,
                reference_condition_id=args.reference_condition_id,
                axis_names=DEFAULT_AXIS_NAMES,
            )
        )
        write_jsonl(output_dir / "manual_annotations.jsonl", annotation_rows)

    write_json(output_dir / "summary.json", summary)
    write_jsonl(output_dir / "blinded_pairs.jsonl", blinded_rows)
    write_jsonl(output_dir / "answer_key.jsonl", answer_key_rows)
    write_jsonl(output_dir / "manual_annotations_template.jsonl", annotation_template_rows)
    write_blinded_packet(output_dir / "blinded_packet.md", blinded_rows)
    write_readme(output_dir / "README.md", summary, has_annotations=has_annotations)

    print(f"wrote output-gate manual audit artifact to {output_dir}")
    print(f"sample size: {summary['sample_count']}")
    if has_annotations:
        print(
            "prompt-grounded creativity candidate win fraction: "
            f"{summary['prompt_grounded_creativity_candidate_win_fraction']:.3f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
