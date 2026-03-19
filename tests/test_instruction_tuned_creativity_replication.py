# ABOUTME: Verifies the bounded instruction-tuned creativity replication stays matched to the refusal pivot stack and output-gate bookkeeping.
# ABOUTME: Prevents the creativity-side continuation from smuggling system-prompt artifacts into extraction or drifting away from the hardened gate structure.

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "run_instruction_tuned_creativity_replication.py"


def load_replication_module():
    spec = importlib.util.spec_from_file_location(
        "run_instruction_tuned_creativity_replication",
        SCRIPT_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module from {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeTokenizer:
    def apply_chat_template(self, messages, tokenize, add_generation_prompt):  # noqa: ANN001
        rendered_messages = [f"{message['role']}::{message['content']}" for message in messages]
        if add_generation_prompt:
            rendered_messages.append("assistant::")
        return "\n".join(rendered_messages)


class InstructionTunedCreativityReplicationTest(unittest.TestCase):
    def test_default_stack_targets_same_instruction_tuned_pair_as_refusal_success_case(self) -> None:
        replication = load_replication_module()

        self.assertEqual("google/gemma-3-270m-it", replication.DEFAULT_MODEL_ID)
        self.assertEqual("gemma-scope-2-270m-it-res", replication.DEFAULT_SAE_RELEASE)
        self.assertEqual("layer_12_width_16k_l0_medium", replication.DEFAULT_REFERENCE_SAE_ID)
        self.assertEqual(
            ROOT / "prompts" / "creative_direction_output_gate_v2_judges.json",
            replication.DEFAULT_JUDGE_TEMPLATES_PATH,
        )

    def test_build_generation_messages_use_task_matched_story_prompts(self) -> None:
        replication = load_replication_module()

        templates = {
            "neutral_story_user_prompt": "Write a short story.\n\nPrompt: {prompt}",
            "prompt_only_creativity_user_prompt": "Write a creative short story.\n\nPrompt: {prompt}",
        }

        neutral_messages = replication.build_generation_messages(
            prompt_text="A lighthouse swallows the moon.",
            prompt_mode="neutral",
            templates=templates,
        )
        creativity_messages = replication.build_generation_messages(
            prompt_text="A lighthouse swallows the moon.",
            prompt_mode="prompt_only_creativity",
            templates=templates,
        )

        self.assertEqual(
            [{"role": "user", "content": "Write a short story.\n\nPrompt: A lighthouse swallows the moon."}],
            neutral_messages,
        )
        self.assertEqual(
            [{"role": "user", "content": "Write a creative short story.\n\nPrompt: A lighthouse swallows the moon."}],
            creativity_messages,
        )

    def test_build_contrastive_dataset_uses_neutral_story_prompt_plus_assistant_transcripts(self) -> None:
        replication = load_replication_module()

        dataset = replication.build_contrastive_dataset(
            prompt_rows=[
                {
                    "prompt_text": "A clock learns to dream.",
                    "positive_assistant_text": "The clock dreamed in brass and fog.",
                    "negative_assistant_text": "The clock had a dream.",
                }
            ],
            tokenizer=FakeTokenizer(),
            templates={"neutral_story_user_prompt": "Write a short story.\n\nPrompt: {prompt}"},
        )

        self.assertEqual(1, len(dataset))
        self.assertIn("user::Write a short story.\n\nPrompt: A clock learns to dream.", dataset[0].positive)
        self.assertIn("assistant::The clock dreamed in brass and fog.", dataset[0].positive)
        self.assertNotIn("system::", dataset[0].positive)

    def test_build_output_gate_conditions_covers_prompt_baseline_and_dense_coeffs(self) -> None:
        replication = load_replication_module()

        conditions = replication.build_output_gate_conditions(hidden_layer=9, steering_coeffs=[0.5, 1.0])

        self.assertEqual(
            [
                "neutral_unsteered",
                "creative_prompt_unsteered",
                "neutral_steered_layer9_coeff_0p5",
                "neutral_steered_layer9_coeff_1p0",
            ],
            [condition["condition_id"] for condition in conditions],
        )

    def test_build_pairwise_comparisons_covers_neutral_and_prompt_baselines(self) -> None:
        replication = load_replication_module()

        comparisons = replication.build_pairwise_comparisons(
            dense_condition_ids=[
                "neutral_steered_layer9_coeff_0p5",
                "neutral_steered_layer9_coeff_1p0",
            ]
        )

        self.assertEqual(
            [
                "creative_prompt_unsteered_vs_neutral_unsteered",
                "neutral_steered_layer9_coeff_0p5_vs_neutral_unsteered",
                "neutral_steered_layer9_coeff_1p0_vs_neutral_unsteered",
                "neutral_steered_layer9_coeff_0p5_vs_creative_prompt_unsteered",
                "neutral_steered_layer9_coeff_1p0_vs_creative_prompt_unsteered",
            ],
            [comparison["comparison_id"] for comparison in comparisons],
        )


if __name__ == "__main__":
    unittest.main()
