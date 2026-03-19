# ABOUTME: Verifies the bounded instruction-tuned refusal pivot stays on the chosen Gemma 3 270M IT plus GemmaScope v2 stack.
# ABOUTME: Locks the chat prompt construction, SAE-layer discovery, and condition naming before the pivot script lands.

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "run_instruction_tuned_refusal_pivot.py"


def load_pivot_module():
    spec = importlib.util.spec_from_file_location(
        "run_instruction_tuned_refusal_pivot",
        SCRIPT_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module from {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class InstructionTunedRefusalPivotTest(unittest.TestCase):
    def test_default_stack_targets_smallest_instruction_tuned_pair(self) -> None:
        pivot = load_pivot_module()

        self.assertEqual("google/gemma-3-270m-it", pivot.DEFAULT_MODEL_ID)
        self.assertEqual("gemma-scope-2-270m-it-res", pivot.DEFAULT_SAE_RELEASE)
        self.assertEqual("layer_12_width_16k_l0_medium", pivot.DEFAULT_REFERENCE_SAE_ID)

    def test_parse_available_layers_from_sae_ids_extracts_sorted_unique_layers(self) -> None:
        pivot = load_pivot_module()

        layers = pivot.parse_available_layers_from_sae_ids(
            [
                "layer_12_width_16k_l0_medium",
                "layer_5_width_65k_l0_small",
                "layer_12_width_262k_l0_big",
                "transcoder/layer_9_width_16k_l0_medium",
            ]
        )

        self.assertEqual([5, 9, 12], layers)

    def test_extract_assistant_response_strips_legacy_wrapper(self) -> None:
        pivot = load_pivot_module()

        assistant_text = pivot.extract_assistant_response(
            "Request: Do harm.\n\nResponse:\nI can't help with that. I can suggest safer alternatives instead."
        )

        self.assertEqual(
            "I can't help with that. I can suggest safer alternatives instead.",
            assistant_text,
        )

    def test_build_generation_messages_keeps_prompt_only_refusal_as_system_plus_user(self) -> None:
        pivot = load_pivot_module()

        templates = {
            "prompt_only_refusal_system_prompt": "Refuse harmful help and redirect safely.",
        }

        neutral_messages = pivot.build_generation_messages(
            prompt_text="Do the harmful thing.",
            prompt_mode="neutral",
            templates=templates,
        )
        refusal_messages = pivot.build_generation_messages(
            prompt_text="Do the harmful thing.",
            prompt_mode="prompt_only_refusal",
            templates=templates,
        )

        self.assertEqual([{"role": "user", "content": "Do the harmful thing."}], neutral_messages)
        self.assertEqual("system", refusal_messages[0]["role"])
        self.assertEqual("user", refusal_messages[1]["role"])

    def test_build_output_gate_conditions_covers_prompt_baseline_and_steered_coeffs(self) -> None:
        pivot = load_pivot_module()

        conditions = pivot.build_output_gate_conditions(hidden_layer=12, steering_coeffs=[0.5, 1.0])

        self.assertEqual(
            [
                "neutral_unsteered",
                "refusal_prompt_unsteered",
                "neutral_steered_layer12_coeff_0p5",
                "neutral_steered_layer12_coeff_1p0",
            ],
            [condition["condition_id"] for condition in conditions],
        )


if __name__ == "__main__":
    unittest.main()
