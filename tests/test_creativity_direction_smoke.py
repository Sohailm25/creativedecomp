# ABOUTME: Verifies the first creativity-direction smoke script can build its contrastive dataset and summarize pairwise projections deterministically.
# ABOUTME: Keeps the initial replication slice reproducible without requiring the test suite to load Gemma weights.

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "run_creativity_direction_smoke.py"


def load_smoke_module():
    spec = importlib.util.spec_from_file_location(
        "run_creativity_direction_smoke",
        SCRIPT_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module from {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CreativityDirectionSmokeTest(unittest.TestCase):
    def test_compute_pca_direction_returns_unit_axis_for_simple_matrix(self) -> None:
        smoke = load_smoke_module()
        train_matrix = [
            [3.0, 0.0],
            [1.0, 0.0],
            [-1.0, 0.0],
            [-3.0, 0.0],
        ]

        direction = smoke.compute_pca_direction(train_matrix)

        self.assertAlmostEqual(1.0, abs(float(direction[0])), places=6)
        self.assertAlmostEqual(0.0, float(direction[1]), places=6)

    def test_build_contrastive_dataset_uses_frozen_templates(self) -> None:
        smoke = load_smoke_module()
        templates = {
            "creative_instruction": "Creative: {prompt}",
            "uncreative_instruction": "Plain: {prompt}",
        }
        prompt_rows = [
            {"prompt_id": "p1", "prompt_text": "A violinist on Mars."},
            {"prompt_id": "p2", "prompt_text": "The moon writes letters."},
        ]

        dataset = smoke.build_contrastive_dataset(prompt_rows, templates)

        self.assertEqual(2, len(dataset))
        self.assertEqual("Creative: A violinist on Mars.", dataset[0].positive)
        self.assertEqual("Plain: A violinist on Mars.", dataset[0].negative)
        self.assertEqual("Creative: The moon writes letters.", dataset[1].positive)
        self.assertEqual("Plain: The moon writes letters.", dataset[1].negative)

    def test_build_contrastive_dataset_prefers_response_centered_pair_texts(self) -> None:
        smoke = load_smoke_module()
        templates = {
            "creative_instruction": "Creative: {prompt}",
            "uncreative_instruction": "Plain: {prompt}",
        }
        prompt_rows = [
            {
                "prompt_id": "p1",
                "prompt_text": "A violinist on Mars.",
                "positive_text": "Prompt: A violinist on Mars.\n\nStory:\nOnce red dust sang.",
                "negative_text": "Prompt: A violinist on Mars.\n\nStory:\nOnce he played a song.",
            }
        ]

        dataset = smoke.build_contrastive_dataset(prompt_rows, templates)

        self.assertEqual(1, len(dataset))
        self.assertEqual(
            "Prompt: A violinist on Mars.\n\nStory:\nOnce red dust sang.",
            dataset[0].positive,
        )
        self.assertEqual(
            "Prompt: A violinist on Mars.\n\nStory:\nOnce he played a song.",
            dataset[0].negative,
        )

    def test_project_onto_direction_safe_uses_stable_dot_products(self) -> None:
        smoke = load_smoke_module()
        hiddens = [
            [2.0, 0.0],
            [-1.0, 0.0],
            [0.5, 0.0],
        ]
        direction = [1.0, 0.0]

        projections = smoke.project_onto_direction_safe(hiddens, direction)

        self.assertEqual([2.0, -1.0, 0.5], [round(value, 6) for value in projections.tolist()])

    def test_summarize_pairwise_projections_reports_margin_stats(self) -> None:
        smoke = load_smoke_module()
        pair_rows = [
            {"prompt_id": "p1", "prompt_text": "prompt one"},
            {"prompt_id": "p2", "prompt_text": "prompt two"},
        ]
        projections = [1.5, -0.5, 0.25, -0.75]

        summary = smoke.summarize_pairwise_projections(pair_rows, projections)

        self.assertEqual(2, summary["pair_count"])
        self.assertAlmostEqual(0.875, summary["positive_mean_projection"])
        self.assertAlmostEqual(-0.625, summary["negative_mean_projection"])
        self.assertAlmostEqual(1.5, summary["mean_margin"])
        self.assertEqual(1.0, summary["positive_gt_negative_fraction"])
        self.assertEqual("p1", summary["pair_details"][0]["prompt_id"])
        self.assertAlmostEqual(2.0, summary["pair_details"][0]["margin"])


if __name__ == "__main__":
    unittest.main()
