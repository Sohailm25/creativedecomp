# ABOUTME: Runs the first generation-side smoke for dense creativity steering using the pilot layer-sweep artifact.
# ABOUTME: Compares neutral prompting, prompt-only creativity, and the top two sweep layers so lexical prompt leakage is easier to spot.

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
from repeng import ControlVector
from repeng.control import ControlModel
import torch


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from run_creativity_direction_smoke import (  # noqa: E402
    ROOT,
    DEFAULT_MODEL_ID,
    DEFAULT_SPLIT_PATH,
    DEFAULT_TEMPLATES_PATH,
    load_model_and_tokenizer,
    load_prompt_rows,
    load_templates,
    select_device,
    write_json,
    write_jsonl,
)


DEFAULT_MAX_PROMPTS = 4
DEFAULT_MAX_NEW_TOKENS = 96
DEFAULT_STEERING_COEFF = 1.0
DEFAULT_SEED = 1729
NEUTRAL_GENERATION_TEMPLATE = "Write a short story inspired by the prompt below.\n\nPrompt: {prompt}"
DEFAULT_SWEEP_DIR = ROOT / "results" / "creativity_direction" / "20260318-gemma2-2b-layer-sweep-pilot"


def default_output_dir() -> Path:
    run_date = datetime.now().strftime("%Y%m%d")
    return ROOT / "results" / "steering_eval" / f"{run_date}-gemma2-2b-generation-smoke"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the first generation-side smoke for dense creativity steering."
    )
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID)
    parser.add_argument("--split-path", type=Path, default=DEFAULT_SPLIT_PATH)
    parser.add_argument("--templates-path", type=Path, default=DEFAULT_TEMPLATES_PATH)
    parser.add_argument("--sweep-dir", type=Path, default=DEFAULT_SWEEP_DIR)
    parser.add_argument("--max-prompts", type=int, default=DEFAULT_MAX_PROMPTS)
    parser.add_argument("--max-new-tokens", type=int, default=DEFAULT_MAX_NEW_TOKENS)
    parser.add_argument("--steering-coeff", type=float, default=DEFAULT_STEERING_COEFF)
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


def path_for_summary(path: Path) -> str:
    absolute_path = path if path.is_absolute() else (ROOT / path)
    return str(absolute_path.resolve().relative_to(ROOT))


def load_ranked_layer_rows(path: Path) -> list[dict[str, Any]]:
    rows = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if not rows:
        raise ValueError(f"no ranked rows found in {path}")
    return rows


def select_candidate_layers(ranked_rows: list[dict[str, Any]]) -> list[int]:
    unique_layers: list[int] = []
    for row in ranked_rows:
        layer = int(row["hidden_layer"])
        if layer not in unique_layers:
            unique_layers.append(layer)
        if len(unique_layers) == 2:
            break
    if len(unique_layers) < 2:
        raise ValueError("need at least two distinct layers for the generation-side comparison")
    return unique_layers


def build_generation_conditions(
    candidate_layers: list[int],
    steering_coeff: float,
) -> list[dict[str, Any]]:
    conditions = [
        {
            "condition_id": "neutral_unsteered",
            "prompt_mode": "neutral",
            "hidden_layer": None,
            "steering_coeff": 0.0,
            "normalize_control": False,
        },
        {
            "condition_id": "creative_prompt_unsteered",
            "prompt_mode": "prompt_only_creativity",
            "hidden_layer": None,
            "steering_coeff": 0.0,
            "normalize_control": False,
        },
    ]
    for layer in candidate_layers:
        conditions.append(
            {
                "condition_id": f"neutral_steered_layer{layer}",
                "prompt_mode": "neutral",
                "hidden_layer": layer,
                "steering_coeff": steering_coeff,
                "normalize_control": True,
            }
        )
    return conditions


def load_directions(path: Path, layers: list[int]) -> dict[int, np.ndarray]:
    with np.load(path) as archive:
        directions = {}
        for layer in layers:
            key = f"layer_{layer}"
            if key not in archive:
                raise KeyError(f"missing direction for layer {layer} in {path}")
            directions[layer] = archive[key].astype(np.float32)
    return directions


def copy_wrapped_layer_attributes(
    model,
    hidden_layer: int,
    attribute_names: tuple[str, ...] = ("attention_type",),
) -> None:
    wrapped_layer = model.model.layers[hidden_layer]
    block = getattr(wrapped_layer, "block", None)
    if block is None:
        return
    for attribute_name in attribute_names:
        if hasattr(block, attribute_name) and not hasattr(wrapped_layer, attribute_name):
            setattr(wrapped_layer, attribute_name, getattr(block, attribute_name))


def build_prompt_text(prompt_text: str, prompt_mode: str, templates: dict[str, str]) -> str:
    if prompt_mode == "neutral":
        return NEUTRAL_GENERATION_TEMPLATE.format(prompt=prompt_text)
    if prompt_mode == "prompt_only_creativity":
        return templates["prompt_only_creativity_baseline"].format(prompt=prompt_text)
    raise ValueError(f"unknown prompt mode: {prompt_mode}")


def generate_completion(
    model,
    tokenizer,
    prompt_text: str,
    seed: int,
    max_new_tokens: int,
) -> tuple[str, str]:
    encoded = tokenizer(prompt_text, return_tensors="pt")
    encoded = {key: value.to(model.device) for key, value in encoded.items()}
    torch.manual_seed(seed)
    output_ids = model.generate(
        **encoded,
        do_sample=True,
        temperature=0.8,
        top_p=0.95,
        max_new_tokens=max_new_tokens,
        pad_token_id=tokenizer.pad_token_id,
        eos_token_id=tokenizer.eos_token_id,
    )[0]
    prompt_length = int(encoded["input_ids"].shape[1])
    completion_ids = output_ids[prompt_length:]
    completion_text = tokenizer.decode(completion_ids, skip_special_tokens=True).strip()
    full_text = tokenizer.decode(output_ids, skip_special_tokens=True).strip()
    return completion_text, full_text


def generate_with_control(
    model,
    tokenizer,
    prompt_text: str,
    hidden_layer: int,
    direction: np.ndarray,
    steering_coeff: float,
    seed: int,
    max_new_tokens: int,
    normalize_control: bool,
) -> tuple[str, str]:
    control_model = ControlModel(model, [hidden_layer])
    copy_wrapped_layer_attributes(control_model.model, hidden_layer=hidden_layer)
    control_vector = ControlVector(
        model_type=model.config.model_type,
        directions={hidden_layer: direction},
    )
    control_model.set_control(control_vector, coeff=steering_coeff, normalize=normalize_control)
    try:
        completion_text, full_text = generate_completion(
            control_model,
            tokenizer,
            prompt_text=prompt_text,
            seed=seed,
            max_new_tokens=max_new_tokens,
        )
    finally:
        control_model.reset()
        control_model.unwrap()
    return completion_text, full_text


def summarize_outputs(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(str(row["condition_id"]), []).append(row)

    summaries: list[dict[str, Any]] = []
    for condition_id, condition_rows in grouped.items():
        word_counts = [int(row["completion_word_count"]) for row in condition_rows]
        char_counts = [int(row["completion_char_count"]) for row in condition_rows]
        summaries.append(
            {
                "condition_id": condition_id,
                "sample_count": len(condition_rows),
                "mean_completion_word_count": float(np.mean(word_counts)),
                "mean_completion_char_count": float(np.mean(char_counts)),
            }
        )
    return sorted(summaries, key=lambda row: row["condition_id"])


def write_readme(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Generation-Side Creativity Smoke",
        "",
        f"- Generated at: `{summary['created_at']}`",
        f"- Model: `{summary['model_id']}`",
        f"- Device: `{summary['device']}`",
        f"- Prompt count: `{summary['prompt_count']}`",
        f"- Candidate layers from sweep: `{summary['candidate_layers']}`",
        f"- Steering coefficient: `{summary['steering_coeff']}`",
        f"- Max new tokens: `{summary['max_new_tokens']}`",
        f"- Seed base: `{summary['seed']}`",
        f"- Neutral prompt template: `{summary['neutral_generation_template']}`",
        "",
        "Conditions:",
    ]
    for condition in summary["conditions"]:
        lines.append(
            f"- `{condition['condition_id']}`: prompt mode `{condition['prompt_mode']}`, "
            f"layer `{condition['hidden_layer']}`, coeff `{condition['steering_coeff']}`"
        )
    lines.extend(
        [
            "",
            "Condition summaries:",
        ]
    )
    for row in summary["condition_summaries"]:
        lines.append(
            f"- `{row['condition_id']}`: mean words `{row['mean_completion_word_count']:.2f}`, "
            f"mean chars `{row['mean_completion_char_count']:.2f}`"
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
    templates = load_templates(args.templates_path)
    ranked_rows = load_ranked_layer_rows(args.sweep_dir / "layer_metrics.jsonl")
    candidate_layers = select_candidate_layers(ranked_rows)
    directions = load_directions(args.sweep_dir / "directions.npz", candidate_layers)
    conditions = build_generation_conditions(candidate_layers, steering_coeff=args.steering_coeff)

    device = select_device(args.device)
    model, tokenizer = load_model_and_tokenizer(args.model_id, device)

    output_rows: list[dict[str, Any]] = []
    for prompt_index, prompt_row in enumerate(prompt_rows):
        for condition_index, condition in enumerate(conditions):
            prompt_text = build_prompt_text(
                prompt_text=str(prompt_row["prompt_text"]),
                prompt_mode=str(condition["prompt_mode"]),
                templates=templates,
            )
            seed = args.seed + (prompt_index * 100) + condition_index
            hidden_layer = condition["hidden_layer"]
            if hidden_layer is None:
                completion_text, full_text = generate_completion(
                    model,
                    tokenizer,
                    prompt_text=prompt_text,
                    seed=seed,
                    max_new_tokens=args.max_new_tokens,
                )
            else:
                completion_text, full_text = generate_with_control(
                    model,
                    tokenizer,
                    prompt_text=prompt_text,
                    hidden_layer=int(hidden_layer),
                    direction=directions[int(hidden_layer)],
                    steering_coeff=float(condition["steering_coeff"]),
                    seed=seed,
                    max_new_tokens=args.max_new_tokens,
                    normalize_control=bool(condition["normalize_control"]),
                )

            output_rows.append(
                {
                    "prompt_id": prompt_row["prompt_id"],
                    "prompt_text": prompt_row["prompt_text"],
                    "condition_id": condition["condition_id"],
                    "prompt_mode": condition["prompt_mode"],
                    "hidden_layer": hidden_layer,
                    "steering_coeff": condition["steering_coeff"],
                    "seed": seed,
                    "prompt_text_full": prompt_text,
                    "completion_text": completion_text,
                    "full_text": full_text,
                    "completion_char_count": len(completion_text),
                    "completion_word_count": len(completion_text.split()),
                }
            )

    summary = {
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "model_id": args.model_id,
        "device": device,
        "prompt_count": len(prompt_rows),
        "candidate_layers": candidate_layers,
        "steering_coeff": args.steering_coeff,
        "max_new_tokens": args.max_new_tokens,
        "seed": args.seed,
        "split_path": path_for_summary(args.split_path),
        "templates_path": path_for_summary(args.templates_path),
        "sweep_dir": path_for_summary(args.sweep_dir),
        "neutral_generation_template": NEUTRAL_GENERATION_TEMPLATE,
        "conditions": conditions,
        "condition_summaries": summarize_outputs(output_rows),
        "outputs_path": "outputs.jsonl",
    }

    write_json(output_dir / "summary.json", summary)
    write_jsonl(output_dir / "outputs.jsonl", output_rows)
    write_readme(output_dir / "README.md", summary)

    print(f"wrote generation smoke artifact to {output_dir}")
    print(f"candidate layers: {candidate_layers}")
    print(f"conditions: {[condition['condition_id'] for condition in conditions]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
