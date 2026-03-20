# ABOUTME: Re-evaluates cached instruction-tuned creativity gate outputs with a score-per-story rubric judge.
# ABOUTME: Replaces brittle label-only judging with order-debiased prompt-grounded creativity and coherence scoring.

from __future__ import annotations

import argparse
from collections import OrderedDict
from datetime import datetime
import json
from pathlib import Path
import re
import sys
from typing import Any

import numpy as np


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from run_creativity_direction_smoke import (  # noqa: E402
    ROOT,
    load_model_and_tokenizer,
    select_device,
    write_json,
    write_jsonl,
)
from run_generation_side_creativity_smoke import prepare_output_dir  # noqa: E402
from run_instruction_tuned_refusal_pivot import generate_judge_response_chat  # noqa: E402


DEFAULT_ARTIFACT_DIR = ROOT / "results" / "steering_eval" / "20260319-gemma3-270m-it-output-gate-v1"
DEFAULT_JUDGE_MODEL_ID = "google/gemma-3-270m-it"
DEFAULT_JUDGE_TEMPLATES_PATH = ROOT / "prompts" / "creative_direction_output_gate_rubric_v1_judges.json"
DEFAULT_JUDGE_MAX_NEW_TOKENS = 128
DEFAULT_MIN_MARGIN = 0.5
DEFAULT_AXIS_NAMES = ["prompt_grounded_creativity", "coherence"]


def default_output_dir() -> Path:
    run_date = datetime.now().strftime("%Y%m%d")
    return ROOT / "results" / "steering_eval" / f"{run_date}-gemma3-270m-it-output-gate-v1-rubric-eval"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate cached instruction-tuned creativity outputs with an order-debiased rubric judge."
    )
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--judge-model-id", default=DEFAULT_JUDGE_MODEL_ID)
    parser.add_argument("--judge-templates-path", type=Path, default=DEFAULT_JUDGE_TEMPLATES_PATH)
    parser.add_argument("--judge-max-new-tokens", type=int, default=DEFAULT_JUDGE_MAX_NEW_TOKENS)
    parser.add_argument("--min-margin", type=float, default=DEFAULT_MIN_MARGIN)
    parser.add_argument("--max-prompts", type=int, default=None)
    parser.add_argument("--comparison-ids", default=None)
    parser.add_argument("--device", choices=["auto", "mps", "cpu"], default="auto")
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def load_judge_template(path: Path) -> str:
    payload = load_json(path)
    key = "pairwise_rubric_score_judge"
    if key not in payload:
        raise KeyError(f"missing template key: {key}")
    return str(payload[key])


def parse_comparison_ids_argument(raw_value: str | None) -> list[str] | None:
    if raw_value is None:
        return None
    parsed: list[str] = []
    for token in raw_value.split(","):
        stripped = token.strip()
        if stripped and stripped not in parsed:
            parsed.append(stripped)
    return parsed


def comparison_id_to_condition_ids(comparison_id: str) -> tuple[str, str]:
    if "_vs_" not in comparison_id:
        raise ValueError(f"invalid comparison id format: {comparison_id}")
    candidate_condition_id, reference_condition_id = comparison_id.split("_vs_", maxsplit=1)
    if not candidate_condition_id or not reference_condition_id:
        raise ValueError(f"invalid comparison id format: {comparison_id}")
    return candidate_condition_id, reference_condition_id


def resolve_comparison_ids(
    generated_rows: list[dict[str, Any]],
    pairwise_rows: list[dict[str, Any]],
    requested_comparison_ids: list[str] | None,
) -> list[str]:
    if requested_comparison_ids is not None:
        return requested_comparison_ids

    ordered_comparison_ids: list[str] = []
    for row in pairwise_rows:
        comparison_id = str(row["comparison_id"])
        if comparison_id not in ordered_comparison_ids:
            ordered_comparison_ids.append(comparison_id)
    if ordered_comparison_ids:
        return ordered_comparison_ids

    condition_ids = sorted({str(row["condition_id"]) for row in generated_rows})
    dense_condition_ids = [
        condition_id
        for condition_id in condition_ids
        if condition_id.startswith("neutral_steered_")
    ]
    inferred: list[str] = ["creative_prompt_unsteered_vs_neutral_unsteered"]
    inferred.extend(f"{condition_id}_vs_neutral_unsteered" for condition_id in dense_condition_ids)
    inferred.extend(f"{condition_id}_vs_creative_prompt_unsteered" for condition_id in dense_condition_ids)
    return inferred


def build_condition_lookup(rows: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    return {
        (str(row["prompt_id"]), str(row["condition_id"])): row
        for row in rows
    }


def resolve_prompt_ids(rows: list[dict[str, Any]], max_prompts: int | None) -> list[str]:
    prompt_ids = sorted({str(row["prompt_id"]) for row in rows})
    if max_prompts is None:
        return prompt_ids
    return prompt_ids[:max(0, max_prompts)]


def render_rubric_prompt(
    prompt_text: str,
    story_a: str,
    story_b: str,
    judge_template: str,
) -> str:
    return judge_template.format(
        prompt=prompt_text,
        story_a=story_a,
        story_b=story_b,
    )


def extract_first_json_object(raw_text: str) -> str:
    start = raw_text.find("{")
    if start < 0:
        raise ValueError("no JSON object found")
    depth = 0
    for index in range(start, len(raw_text)):
        char = raw_text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return raw_text[start: index + 1]
    raise ValueError("unterminated JSON object")


def parse_rubric_scores(raw_text: str) -> dict[str, dict[str, int]]:
    raw_str = str(raw_text).strip()
    payload = None
    try:
        payload = json.loads(raw_str)
    except json.JSONDecodeError:
        try:
            payload = json.loads(extract_first_json_object(raw_str))
        except (json.JSONDecodeError, ValueError):
            payload = None

    if isinstance(payload, dict):
        parsed: dict[str, dict[str, int]] = {}
        story_a_payload = payload.get("story_a")
        story_b_payload = payload.get("story_b")
        if story_b_payload is None and isinstance(story_a_payload, dict):
            nested_story_b_payload = story_a_payload.get("story_b")
            if isinstance(nested_story_b_payload, dict):
                story_b_payload = nested_story_b_payload
        story_payloads = {
            "story_a": story_a_payload,
            "story_b": story_b_payload,
        }
        try:
            for story_key in ("story_a", "story_b"):
                story_payload = story_payloads[story_key]
                if not isinstance(story_payload, dict):
                    raise ValueError(f"missing score payload for {story_key}")
                parsed_scores: dict[str, int] = {}
                for axis_name in DEFAULT_AXIS_NAMES:
                    if axis_name not in story_payload:
                        raise ValueError(f"missing axis score `{axis_name}` in {story_key}")
                    score = int(story_payload[axis_name])
                    if score < 1 or score > 5:
                        raise ValueError(f"axis score out of range for `{axis_name}` in {story_key}: {score}")
                    parsed_scores[axis_name] = score
                parsed[story_key] = parsed_scores
            return parsed
        except (TypeError, ValueError):
            pass

    pair_pattern = re.compile(
        r'"prompt_grounded_creativity"\s*:\s*([1-5])\s*,\s*"coherence"\s*:\s*([1-5])'
    )
    matches = pair_pattern.findall(raw_str)
    if len(matches) < 2:
        raise ValueError("could not parse two rubric score pairs from judge response")
    first_pair = matches[0]
    second_pair = matches[1]
    return {
        "story_a": {
            "prompt_grounded_creativity": int(first_pair[0]),
            "coherence": int(first_pair[1]),
        },
        "story_b": {
            "prompt_grounded_creativity": int(second_pair[0]),
            "coherence": int(second_pair[1]),
        },
    }


def resolve_order_debiased_axis_result(
    axis_name: str,
    forward_scores: dict[str, dict[str, int]],
    reverse_scores: dict[str, dict[str, int]],
    candidate_condition_id: str,
    reference_condition_id: str,
    min_margin: float,
) -> dict[str, Any]:
    candidate_forward_score = float(forward_scores["story_a"][axis_name])
    candidate_reverse_score = float(reverse_scores["story_b"][axis_name])
    reference_forward_score = float(forward_scores["story_b"][axis_name])
    reference_reverse_score = float(reverse_scores["story_a"][axis_name])

    candidate_mean_score = float(np.mean([candidate_forward_score, candidate_reverse_score]))
    reference_mean_score = float(np.mean([reference_forward_score, reference_reverse_score]))
    score_delta = candidate_mean_score - reference_mean_score

    winner_condition_id = "tie"
    if score_delta >= min_margin:
        winner_condition_id = candidate_condition_id
    elif score_delta <= -min_margin:
        winner_condition_id = reference_condition_id

    return {
        "candidate_mean_score": candidate_mean_score,
        "reference_mean_score": reference_mean_score,
        "score_delta": score_delta,
        "winner_condition_id": winner_condition_id,
        "candidate_position_shift": candidate_forward_score - candidate_reverse_score,
        "reference_position_shift": reference_forward_score - reference_reverse_score,
    }


def summarize_rubric_judgments(judgment_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows_by_comparison: OrderedDict[str, list[dict[str, Any]]] = OrderedDict()
    for row in judgment_rows:
        comparison_id = str(row["comparison_id"])
        if comparison_id not in rows_by_comparison:
            rows_by_comparison[comparison_id] = []
        rows_by_comparison[comparison_id].append(row)

    summaries: list[dict[str, Any]] = []
    for comparison_id, comparison_rows in rows_by_comparison.items():
        candidate_condition_id = str(comparison_rows[0]["candidate_condition_id"])
        reference_condition_id = str(comparison_rows[0]["reference_condition_id"])
        summary: dict[str, Any] = {
            "comparison_id": comparison_id,
            "candidate_condition_id": candidate_condition_id,
            "reference_condition_id": reference_condition_id,
            "sample_count": len(comparison_rows),
            "parse_success_fraction": float(np.mean([bool(row["parse_success"]) for row in comparison_rows])),
        }
        parsed_rows = [row for row in comparison_rows if bool(row["parse_success"])]
        for axis_name in DEFAULT_AXIS_NAMES:
            winner_key = f"{axis_name}_winner_condition_id"
            candidate_mean_key = f"{axis_name}_candidate_mean_score"
            reference_mean_key = f"{axis_name}_reference_mean_score"
            score_delta_key = f"{axis_name}_score_delta"
            candidate_shift_key = f"{axis_name}_candidate_position_shift"
            reference_shift_key = f"{axis_name}_reference_position_shift"
            summary[f"{axis_name}_candidate_win_fraction"] = float(
                np.mean([str(row[winner_key]) == candidate_condition_id for row in comparison_rows])
            )
            summary[f"{axis_name}_reference_win_fraction"] = float(
                np.mean([str(row[winner_key]) == reference_condition_id for row in comparison_rows])
            )
            summary[f"{axis_name}_tie_fraction"] = float(
                np.mean([str(row[winner_key]) == "tie" for row in comparison_rows])
            )
            if parsed_rows:
                summary[f"{axis_name}_candidate_mean_score"] = float(
                    np.mean([float(row[candidate_mean_key]) for row in parsed_rows])
                )
                summary[f"{axis_name}_reference_mean_score"] = float(
                    np.mean([float(row[reference_mean_key]) for row in parsed_rows])
                )
                summary[f"{axis_name}_mean_score_delta"] = float(
                    np.mean(
                        [
                            float(row.get(score_delta_key, row[candidate_mean_key] - row[reference_mean_key]))
                            for row in parsed_rows
                        ]
                    )
                )
                summary[f"{axis_name}_mean_abs_candidate_position_shift"] = float(
                    np.mean(
                        [
                            abs(float(row.get(candidate_shift_key, 0.0)))
                            for row in parsed_rows
                        ]
                    )
                )
                summary[f"{axis_name}_mean_abs_reference_position_shift"] = float(
                    np.mean(
                        [
                            abs(float(row.get(reference_shift_key, 0.0)))
                            for row in parsed_rows
                        ]
                    )
                )
            else:
                summary[f"{axis_name}_candidate_mean_score"] = None
                summary[f"{axis_name}_reference_mean_score"] = None
                summary[f"{axis_name}_mean_score_delta"] = None
                summary[f"{axis_name}_mean_abs_candidate_position_shift"] = None
                summary[f"{axis_name}_mean_abs_reference_position_shift"] = None

        summaries.append(summary)
    return summaries


def summarize_gate_assessment(comparison_summaries: list[dict[str, Any]]) -> dict[str, Any]:
    dense_vs_neutral = [
        row
        for row in comparison_summaries
        if str(row["candidate_condition_id"]).startswith("neutral_steered_")
        and str(row["reference_condition_id"]) == "neutral_unsteered"
        and row["prompt_grounded_creativity_mean_score_delta"] is not None
        and row["coherence_mean_score_delta"] is not None
    ]
    if not dense_vs_neutral:
        return {
            "best_dense_condition_id": None,
            "best_dense_vs_neutral": None,
            "automatic_pass_recommendation": False,
            "automatic_pass_rule": (
                "best dense condition has positive prompt-grounded creativity mean score delta "
                "and non-negative coherence mean score delta versus neutral"
            ),
        }

    best_dense_vs_neutral = max(
        dense_vs_neutral,
        key=lambda row: (
            float(row["prompt_grounded_creativity_mean_score_delta"]),
            float(row["coherence_mean_score_delta"]),
        ),
    )
    return {
        "best_dense_condition_id": str(best_dense_vs_neutral["candidate_condition_id"]),
        "best_dense_vs_neutral": best_dense_vs_neutral,
        "automatic_pass_recommendation": bool(
            float(best_dense_vs_neutral["prompt_grounded_creativity_mean_score_delta"]) > 0.0
            and float(best_dense_vs_neutral["coherence_mean_score_delta"]) >= 0.0
        ),
        "automatic_pass_rule": (
            "best dense condition has positive prompt-grounded creativity mean score delta "
            "and non-negative coherence mean score delta versus neutral"
        ),
    }


def summarize_judge_health(judgment_rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not judgment_rows:
        return {
            "overall_parse_success_fraction": 0.0,
            "axis_health": {},
            "usable_for_claim_bearing": False,
            "failure_reasons": ["no_judgment_rows"],
        }

    overall_parse_success_fraction = float(
        np.mean([bool(row["parse_success"]) for row in judgment_rows])
    )
    axis_health: dict[str, Any] = {}
    failure_reasons: list[str] = []
    for axis_name in DEFAULT_AXIS_NAMES:
        winner_key = f"{axis_name}_winner_condition_id"
        candidate_score_key = f"{axis_name}_candidate_mean_score"
        reference_score_key = f"{axis_name}_reference_mean_score"
        parsed_rows = [row for row in judgment_rows if bool(row["parse_success"])]
        unique_scores = sorted(
            {
                float(row[candidate_score_key])
                for row in parsed_rows
            }
            | {
                float(row[reference_score_key])
                for row in parsed_rows
            }
        )
        tie_fraction = float(np.mean([str(row[winner_key]) == "tie" for row in judgment_rows]))
        all_tie = tie_fraction == 1.0
        constant_score = len(unique_scores) == 1
        collapsed = bool(parsed_rows) and all_tie and constant_score
        axis_health[axis_name] = {
            "tie_fraction": tie_fraction,
            "unique_scores": unique_scores,
            "collapsed": collapsed,
        }
        if collapsed:
            failure_reasons.append(f"{axis_name}_collapsed_to_constant_ties")

    if overall_parse_success_fraction < 0.95:
        failure_reasons.append("parse_success_below_0p95")
    usable_for_claim_bearing = len(failure_reasons) == 0
    return {
        "overall_parse_success_fraction": overall_parse_success_fraction,
        "axis_health": axis_health,
        "usable_for_claim_bearing": usable_for_claim_bearing,
        "failure_reasons": failure_reasons,
    }


def format_metric(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.3f}"


def write_readme(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Instruction-Tuned Creativity Rubric Re-Evaluation",
        "",
        f"- Generated at: `{summary['created_at']}`",
        f"- Source artifact: `{summary['artifact_dir']}`",
        f"- Judge model: `{summary['judge_model_id']}`",
        f"- Device: `{summary['device']}`",
        f"- Prompt count: `{summary['prompt_count']}`",
        f"- Comparisons: `{summary['comparison_ids']}`",
        f"- Judge max new tokens: `{summary['judge_max_new_tokens']}`",
        f"- Minimum winner margin: `{summary['min_margin']}`",
        f"- Automatic pass recommendation: `{summary['gate_assessment']['automatic_pass_recommendation']}`",
        f"- Automatic pass rule: `{summary['gate_assessment']['automatic_pass_rule']}`",
        f"- Judge usable for claim-bearing: `{summary['judge_health']['usable_for_claim_bearing']}`",
        f"- Judge health failures: `{summary['judge_health']['failure_reasons']}`",
        "",
        "Comparison summaries:",
    ]
    for row in summary["comparison_summaries"]:
        lines.append(
            f"- `{row['comparison_id']}`: creativity delta `{format_metric(row['prompt_grounded_creativity_mean_score_delta'])}`, "
            f"coherence delta `{format_metric(row['coherence_mean_score_delta'])}`, parse success `{row['parse_success_fraction']:.3f}`"
        )
    lines.extend(
        [
            "",
            "Artifacts:",
            "- `summary.json`",
            "- `rubric_judgments.jsonl`",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir or default_output_dir()
    prepare_output_dir(output_dir, overwrite=args.overwrite)

    generated_rows = load_jsonl(args.artifact_dir / "generated_outputs.jsonl")
    pairwise_path = args.artifact_dir / "pairwise_judgments.jsonl"
    pairwise_rows = load_jsonl(pairwise_path) if pairwise_path.exists() else []
    comparison_ids = resolve_comparison_ids(
        generated_rows=generated_rows,
        pairwise_rows=pairwise_rows,
        requested_comparison_ids=parse_comparison_ids_argument(args.comparison_ids),
    )
    prompt_ids = resolve_prompt_ids(generated_rows, max_prompts=args.max_prompts)
    condition_lookup = build_condition_lookup(generated_rows)
    judge_template = load_judge_template(args.judge_templates_path)

    device = select_device(args.device)
    model, tokenizer = load_model_and_tokenizer(args.judge_model_id, device)

    judgment_rows: list[dict[str, Any]] = []
    for comparison_id in comparison_ids:
        candidate_condition_id, reference_condition_id = comparison_id_to_condition_ids(comparison_id)
        for prompt_id in prompt_ids:
            candidate_row = condition_lookup[(prompt_id, candidate_condition_id)]
            reference_row = condition_lookup[(prompt_id, reference_condition_id)]
            prompt_text = str(candidate_row["prompt_text"])
            candidate_text = str(candidate_row["completion_text"])
            reference_text = str(reference_row["completion_text"])

            forward_prompt = render_rubric_prompt(
                prompt_text=prompt_text,
                story_a=candidate_text,
                story_b=reference_text,
                judge_template=judge_template,
            )
            reverse_prompt = render_rubric_prompt(
                prompt_text=prompt_text,
                story_a=reference_text,
                story_b=candidate_text,
                judge_template=judge_template,
            )

            forward_raw = generate_judge_response_chat(
                model=model,
                tokenizer=tokenizer,
                prompt_text=forward_prompt,
                max_new_tokens=args.judge_max_new_tokens,
            )
            reverse_raw = generate_judge_response_chat(
                model=model,
                tokenizer=tokenizer,
                prompt_text=reverse_prompt,
                max_new_tokens=args.judge_max_new_tokens,
            )

            parse_success = True
            parse_error = None
            try:
                forward_scores = parse_rubric_scores(forward_raw)
                reverse_scores = parse_rubric_scores(reverse_raw)
            except (ValueError, json.JSONDecodeError, TypeError) as exc:
                parse_success = False
                parse_error = str(exc)
                forward_scores = None
                reverse_scores = None

            row: dict[str, Any] = {
                "comparison_id": comparison_id,
                "prompt_id": prompt_id,
                "candidate_condition_id": candidate_condition_id,
                "reference_condition_id": reference_condition_id,
                "parse_success": parse_success,
                "parse_error": parse_error,
                "forward_raw": forward_raw,
                "reverse_raw": reverse_raw,
            }

            for axis_name in DEFAULT_AXIS_NAMES:
                if parse_success:
                    axis_result = resolve_order_debiased_axis_result(
                        axis_name=axis_name,
                        forward_scores=forward_scores,
                        reverse_scores=reverse_scores,
                        candidate_condition_id=candidate_condition_id,
                        reference_condition_id=reference_condition_id,
                        min_margin=args.min_margin,
                    )
                else:
                    axis_result = {
                        "candidate_mean_score": None,
                        "reference_mean_score": None,
                        "score_delta": None,
                        "winner_condition_id": "tie",
                        "candidate_position_shift": None,
                        "reference_position_shift": None,
                    }

                row[f"{axis_name}_candidate_mean_score"] = axis_result["candidate_mean_score"]
                row[f"{axis_name}_reference_mean_score"] = axis_result["reference_mean_score"]
                row[f"{axis_name}_score_delta"] = axis_result["score_delta"]
                row[f"{axis_name}_winner_condition_id"] = axis_result["winner_condition_id"]
                row[f"{axis_name}_candidate_position_shift"] = axis_result["candidate_position_shift"]
                row[f"{axis_name}_reference_position_shift"] = axis_result["reference_position_shift"]

            judgment_rows.append(row)

    comparison_summaries = summarize_rubric_judgments(judgment_rows)
    summary = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "artifact_dir": str(args.artifact_dir.resolve().relative_to(ROOT)),
        "judge_model_id": args.judge_model_id,
        "device": device,
        "prompt_count": len(prompt_ids),
        "comparison_ids": comparison_ids,
        "judge_templates_path": str(args.judge_templates_path.resolve().relative_to(ROOT)),
        "judge_max_new_tokens": args.judge_max_new_tokens,
        "min_margin": args.min_margin,
        "comparison_summaries": comparison_summaries,
        "gate_assessment": summarize_gate_assessment(comparison_summaries),
        "judge_health": summarize_judge_health(judgment_rows),
    }

    write_json(output_dir / "summary.json", summary)
    write_jsonl(output_dir / "rubric_judgments.jsonl", judgment_rows)
    write_readme(output_dir / "README.md", summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
