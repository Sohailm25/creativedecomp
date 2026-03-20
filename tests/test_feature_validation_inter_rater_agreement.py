# ABOUTME: Verifies inter-rater agreement computation for locked feature-validation manual audits.
# ABOUTME: Prevents claim upgrades without explicit agreement metrics and pair-id integrity checks.

from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "compute_feature_validation_inter_rater_agreement.py"


def load_script_module():
    spec = importlib.util.spec_from_file_location(
        "compute_feature_validation_inter_rater_agreement",
        SCRIPT_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module from {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FeatureValidationInterRaterAgreementTest(unittest.TestCase):
    def test_compute_cohens_kappa_returns_one_for_perfect_agreement(self) -> None:
        script = load_script_module()
        kappa = script.compute_cohens_kappa(
            rater1_labels=["A", "B", "tie", "A"],
            rater2_labels=["A", "B", "tie", "A"],
            label_space=["A", "B", "tie"],
        )
        self.assertEqual(1.0, kappa)

    def test_summarize_axis_agreement_reports_fraction_and_kappa(self) -> None:
        script = load_script_module()
        rater1_lookup = {
            "p1": {"prompt_grounded_creativity_winner_label": "A"},
            "p2": {"prompt_grounded_creativity_winner_label": "B"},
            "p3": {"prompt_grounded_creativity_winner_label": "tie"},
            "p4": {"prompt_grounded_creativity_winner_label": "A"},
        }
        rater2_lookup = {
            "p1": {"prompt_grounded_creativity_winner_label": "A"},
            "p2": {"prompt_grounded_creativity_winner_label": "A"},
            "p3": {"prompt_grounded_creativity_winner_label": "tie"},
            "p4": {"prompt_grounded_creativity_winner_label": "A"},
        }

        summary = script.summarize_axis_agreement(
            rater1_lookup=rater1_lookup,
            rater2_lookup=rater2_lookup,
            axis_name="prompt_grounded_creativity",
        )

        self.assertEqual(4, summary["sample_count"])
        self.assertAlmostEqual(0.75, summary["percent_agreement"])
        self.assertLess(summary["cohens_kappa"], 1.0)
        self.assertGreaterEqual(summary["cohens_kappa"], 0.0)

    def test_build_annotation_lookup_rejects_mismatched_pair_ids(self) -> None:
        script = load_script_module()

        with tempfile.TemporaryDirectory() as tmp:
            path1 = Path(tmp) / "r1.jsonl"
            path2 = Path(tmp) / "r2.jsonl"
            path1.write_text(
                '{"audit_pair_id":"pair-1","prompt_grounded_creativity_winner_label":"A","coherence_winner_label":"B"}\n',
                encoding="utf-8",
            )
            path2.write_text(
                '{"audit_pair_id":"pair-2","prompt_grounded_creativity_winner_label":"A","coherence_winner_label":"B"}\n',
                encoding="utf-8",
            )
            r1_rows = script.load_jsonl(path1)
            r2_rows = script.load_jsonl(path2)
            r1_lookup = script.build_annotation_lookup(r1_rows, axis_names=script.DEFAULT_AXIS_NAMES)
            r2_lookup = script.build_annotation_lookup(r2_rows, axis_names=script.DEFAULT_AXIS_NAMES)

            with self.assertRaises(ValueError):
                script.validate_pair_ids_match(r1_lookup, r2_lookup)

    def test_summarize_per_comparison_agreement_keeps_comparison_ids(self) -> None:
        script = load_script_module()
        answer_key_rows = [
            {"audit_pair_id": "pair-1", "comparison_id": "c1"},
            {"audit_pair_id": "pair-2", "comparison_id": "c1"},
            {"audit_pair_id": "pair-3", "comparison_id": "c2"},
        ]
        rater1_lookup = {
            "pair-1": {
                "prompt_grounded_creativity_winner_label": "A",
                "coherence_winner_label": "A",
            },
            "pair-2": {
                "prompt_grounded_creativity_winner_label": "B",
                "coherence_winner_label": "A",
            },
            "pair-3": {
                "prompt_grounded_creativity_winner_label": "A",
                "coherence_winner_label": "B",
            },
        }
        rater2_lookup = {
            "pair-1": {
                "prompt_grounded_creativity_winner_label": "A",
                "coherence_winner_label": "A",
            },
            "pair-2": {
                "prompt_grounded_creativity_winner_label": "A",
                "coherence_winner_label": "A",
            },
            "pair-3": {
                "prompt_grounded_creativity_winner_label": "A",
                "coherence_winner_label": "B",
            },
        }

        rows = script.summarize_per_comparison_agreement(
            answer_key_rows=answer_key_rows,
            rater1_lookup=rater1_lookup,
            rater2_lookup=rater2_lookup,
            axis_names=script.DEFAULT_AXIS_NAMES,
        )

        self.assertEqual(["c1", "c2"], [row["comparison_id"] for row in rows])
        c1 = rows[0]
        self.assertEqual(2, c1["sample_count"])
        self.assertIn("prompt_grounded_creativity_percent_agreement", c1)
        self.assertIn("coherence_percent_agreement", c1)


if __name__ == "__main__":
    unittest.main()
