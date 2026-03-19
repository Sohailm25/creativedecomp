# ABOUTME: Verifies that the live strategy docs follow the novelty memo's recommended framing and controls.
# ABOUTME: Prevents the repo from drifting toward a generic creativity project instead of the novelty-backed experiment.

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]

PREREG = (ROOT / "history/PREREG.md").read_text(encoding="utf-8")
POSITIONING = (ROOT / "background-work/RESEARCH_POSITIONING.md").read_text(
    encoding="utf-8"
)
CURRENT_STATE = (ROOT / "CURRENT_STATE.md").read_text(encoding="utf-8")
CONFIG = (ROOT / "configs/experiment.yaml").read_text(encoding="utf-8")
AGENTS = (ROOT / "AGENTS.md").read_text(encoding="utf-8")


class ResearchDirectionAlignmentTest(unittest.TestCase):
    def test_positioning_frames_question_as_mechanistic_difference(self) -> None:
        self.assertIn("mechanistically different", POSITIONING)

    def test_prereg_requires_baseline_comparisons_to_simpler_concepts(self) -> None:
        self.assertIn("refusal", PREREG)
        self.assertIn("sentiment", PREREG)

    def test_prereg_requires_multi_method_or_pilot_method_comparison(self) -> None:
        self.assertTrue(
            "multiple decomposition methods" in PREREG
            or "compare at least two" in PREREG
        )

    def test_prereg_requires_multiple_benchmark_families(self) -> None:
        self.assertTrue(
            "at least two benchmark families" in PREREG
            or "two complementary benchmark families" in PREREG
        )

    def test_prereg_requires_pilot_only_layer_and_scale_freeze(self) -> None:
        self.assertIn("Freeze the selected layer and steering scale", PREREG)

    def test_prereg_requires_output_level_gate_before_phase2(self) -> None:
        self.assertIn("internal projection movement alone is insufficient", PREREG)
        self.assertIn("output-level creativity effect", PREREG)

    def test_prereg_requires_matched_pipeline_baselines(self) -> None:
        self.assertIn("same model, SAE release, layer/site, and decomposition pipeline", PREREG)

    def test_current_state_tracks_output_filtering_and_negative_result_path(self) -> None:
        self.assertIn("output-feature", CURRENT_STATE)
        self.assertIn("negative result", CURRENT_STATE)

    def test_current_state_tracks_first_strong_negative_result_after_metric_followup(self) -> None:
        self.assertIn("first strong Phase 1 negative result", CURRENT_STATE)
        self.assertIn("prompt-grounded creativity", CURRENT_STATE)

    def test_current_state_tracks_bounded_olson_style_sensitivity_before_output_gate(self) -> None:
        self.assertIn("Olson-style", CURRENT_STATE)
        self.assertTrue("mean-difference" in CURRENT_STATE or "CAA" in CURRENT_STATE)

    def test_current_state_tracks_mean_difference_recovery_as_new_phase1_path(self) -> None:
        self.assertIn("mean_difference", CURRENT_STATE)
        self.assertIn("layer `23`", CURRENT_STATE)

    def test_current_state_keeps_decomposition_blocked_after_order_robust_output_gate(self) -> None:
        self.assertIn("order-robust", CURRENT_STATE)
        self.assertIn("decomposition remains blocked", CURRENT_STATE)

    def test_current_state_requires_cached_output_reuse_before_new_generation(self) -> None:
        self.assertIn("cached generated outputs", CURRENT_STATE)
        self.assertIn("manual audit", CURRENT_STATE)

    def test_current_state_chooses_matched_simpler_concept_control_as_next_lane(self) -> None:
        self.assertIn("matched refusal baseline", CURRENT_STATE)
        self.assertIn("before any model-scale escalation", CURRENT_STATE)

    def test_current_state_escalates_to_model_scale_if_refusal_dense_control_is_not_clean(self) -> None:
        self.assertIn("stack or harness weakness", CURRENT_STATE)
        self.assertIn("model-scale sensitivity", CURRENT_STATE)

    def test_current_state_records_refusal_control_as_not_cleanly_positive(self) -> None:
        self.assertIn("prompt-only refusal baseline", CURRENT_STATE)
        self.assertIn("dense refusal steering still does not clear a clean output-level gate", CURRENT_STATE)

    def test_current_state_tracks_9b_scale_sensitivity_as_not_rescuing_dense_refusal(self) -> None:
        self.assertIn("Gemma 2 `9B`", CURRENT_STATE)
        self.assertIn("scale alone does not rescue dense output-level refusal steering", CURRENT_STATE)

    def test_current_state_chooses_alternate_method_control_after_cross_scale_dense_failure(self) -> None:
        self.assertIn("alternate-method control lane", CURRENT_STATE)
        self.assertIn("stop further dense base-model steering sweeps", CURRENT_STATE)

    def test_current_state_tracks_sparse_refusal_control_as_not_rescuing_output_gate(self) -> None:
        self.assertIn("sparse SAE-latent refusal control", CURRENT_STATE)
        self.assertIn("write-up-grade negative result", CURRENT_STATE)
        self.assertIn("instruction-tuned pivot", CURRENT_STATE)

    def test_current_state_tracks_instruction_tuned_refusal_pivot_as_failed_final_sensitivity(self) -> None:
        self.assertIn("instruction-tuned refusal pivot", CURRENT_STATE)
        self.assertIn("google/gemma-3-270m-it", CURRENT_STATE)
        self.assertIn("write-up-grade negative result", CURRENT_STATE)

    def test_config_uses_65k_as_base_sae_configuration(self) -> None:
        self.assertIn("default_width: 65k", CONFIG)

    def test_agents_defines_current_phase_doc_priority(self) -> None:
        self.assertIn("priority order is", AGENTS)
        self.assertIn("research/experiment-novelty.md", AGENTS)
        self.assertIn("research/experiment-macbook-guide.md", AGENTS)


if __name__ == "__main__":
    unittest.main()
