# ABOUTME: Builds a small audit slice for the response-centered v2 pair set after the late-layer sweep.
# ABOUTME: Surfaces the strongest wins, strongest losses, and contaminated examples so weak-signal diagnosis is evidence-backed.

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

from run_creativity_direction_smoke import (  # noqa: E402
    ROOT,
    write_json,
    write_jsonl,
)


DEFAULT_PAIR_PATH = ROOT / "prompts" / "creative_direction_v2_pilot_pairs.jsonl"
DEFAULT_SWEEP_DIR = (
    ROOT
    / "results"
    / "creativity_direction"
    / "20260318-gemma2-2b-layer-sweep-response-pairs-v2"
)
DEFAULT_STRONGEST_PER_BUCKET = 3
DEFAULT_FLAGGED_LIMIT = 2


def default_output_dir() -> Path:
    run_date = datetime.now().strftime("%Y%m%d")
    return ROOT / "results" / "creativity_direction" / f"{run_date}-gemma2-2b-response-pairs-v2-audit"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a small audit slice for the response-centered v2 pair set."
    )
    parser.add_argument("--pair-path", type=Path, default=DEFAULT_PAIR_PATH)
    parser.add_argument("--sweep-dir", type=Path, default=DEFAULT_SWEEP_DIR)
    parser.add_argument("--strongest-per-bucket", type=int, default=DEFAULT_STRONGEST_PER_BUCKET)
    parser.add_argument("--flagged-limit", type=int, default=DEFAULT_FLAGGED_LIMIT)
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
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def select_pair_detail_path(sweep_dir: Path) -> tuple[Path, str]:
    controlled_path = sweep_dir / "controlled_best_layer_pair_details.jsonl"
    if controlled_path.exists():
        return controlled_path, "controlled_best_layer_pair_details.jsonl"
    raw_path = sweep_dir / "raw_best_layer_pair_details.jsonl"
    if raw_path.exists():
        return raw_path, "raw_best_layer_pair_details.jsonl"
    raise FileNotFoundError(f"no pair detail file found under {sweep_dir}")


def enrich_pair_rows(
    pair_rows: list[dict[str, Any]],
    pair_detail_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    pair_rows_by_id = {str(row["prompt_id"]): row for row in pair_rows}
    enriched_rows: list[dict[str, Any]] = []
    for detail in pair_detail_rows:
        prompt_id = str(detail["prompt_id"])
        source = pair_rows_by_id[prompt_id]
        enriched = dict(source)
        enriched.update(
            {
                "positive_projection": float(detail["positive_projection"]),
                "negative_projection": float(detail["negative_projection"]),
                "margin": float(detail["margin"]),
            }
        )
        enriched_rows.append(enriched)
    return enriched_rows


def extend_unique(selected: list[dict[str, Any]], rows: list[dict[str, Any]]) -> None:
    seen_prompt_ids = {str(row["prompt_id"]) for row in selected}
    for row in rows:
        prompt_id = str(row["prompt_id"])
        if prompt_id in seen_prompt_ids:
            continue
        selected.append(row)
        seen_prompt_ids.add(prompt_id)


def select_audit_rows(
    rows: list[dict[str, Any]],
    strongest_per_bucket: int,
    flagged_limit: int,
) -> list[dict[str, Any]]:
    strongest_wins = sorted(
        [row for row in rows if float(row["margin"]) > 0.0],
        key=lambda row: float(row["margin"]),
        reverse=True,
    )[:strongest_per_bucket]
    strongest_losses = sorted(
        [row for row in rows if float(row["margin"]) < 0.0],
        key=lambda row: float(row["margin"]),
    )[:strongest_per_bucket]
    flagged_rows = sorted(
        [row for row in rows if int(row.get("positive_meta_marker_score", 0)) > 0 or int(row.get("negative_meta_marker_score", 0)) > 0],
        key=lambda row: abs(float(row["margin"])),
        reverse=True,
    )[:flagged_limit]

    selected: list[dict[str, Any]] = []
    extend_unique(selected, strongest_wins)
    extend_unique(selected, strongest_losses)
    extend_unique(selected, flagged_rows)
    return selected


def summarize_audit_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    win_count = sum(float(row["margin"]) > 0.0 for row in rows)
    loss_count = sum(float(row["margin"]) < 0.0 for row in rows)
    negative_meta_flag_count = sum(int(row.get("negative_meta_marker_score", 0)) > 0 for row in rows)
    positive_meta_flag_count = sum(int(row.get("positive_meta_marker_score", 0)) > 0 for row in rows)
    return {
        "selected_count": len(rows),
        "win_count": int(win_count),
        "loss_count": int(loss_count),
        "negative_meta_flag_count": int(negative_meta_flag_count),
        "positive_meta_flag_count": int(positive_meta_flag_count),
    }


def write_readme(path: Path, summary: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Creativity Response Pairs V2 Audit",
        "",
        f"- Generated at: `{summary['created_at']}`",
        f"- Source pair file: `{summary['pair_path']}`",
        f"- Source pair-details file: `{summary['pair_details_path']}`",
        f"- Selected rows: `{summary['selected_count']}`",
        f"- Win rows: `{summary['win_count']}`",
        f"- Loss rows: `{summary['loss_count']}`",
        f"- Negative meta-flag rows: `{summary['negative_meta_flag_count']}`",
        f"- Positive meta-flag rows: `{summary['positive_meta_flag_count']}`",
        "",
        "Selected prompts:",
    ]
    for row in rows:
        lines.append(
            f"- `{row['prompt_id']}`: margin `{float(row['margin']):.4f}`, "
            f"positive meta `{int(row.get('positive_meta_marker_score', 0))}`, "
            f"negative meta `{int(row.get('negative_meta_marker_score', 0))}`"
        )
    lines.extend(
        [
            "",
            "Artifacts:",
            "- `summary.json`",
            "- `audit_rows.jsonl`",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir or default_output_dir()
    prepare_output_dir(output_dir, overwrite=args.overwrite)

    pair_rows = load_jsonl(args.pair_path)
    pair_detail_path, pair_detail_name = select_pair_detail_path(args.sweep_dir)
    pair_detail_rows = load_jsonl(pair_detail_path)
    enriched_rows = enrich_pair_rows(pair_rows, pair_detail_rows)
    audit_rows = select_audit_rows(
        enriched_rows,
        strongest_per_bucket=args.strongest_per_bucket,
        flagged_limit=args.flagged_limit,
    )
    summary = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "pair_path": str(args.pair_path.resolve().relative_to(ROOT)),
        "pair_details_path": str(pair_detail_path.resolve().relative_to(ROOT)),
        "pair_details_name": pair_detail_name,
        **summarize_audit_rows(audit_rows),
    }

    write_json(output_dir / "summary.json", summary)
    write_jsonl(output_dir / "audit_rows.jsonl", audit_rows)
    write_readme(output_dir / "README.md", summary, audit_rows)

    print(f"wrote v2 pair audit artifact to {output_dir}")
    print(f"selected rows: {summary['selected_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
