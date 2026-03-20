# Instruction-Tuned Creativity Output Gate Manual Audit

- Generated at: `2026-03-20T11:08:00-05:00`
- Source artifact: `results/feature_validation/20260319-gemma3-270m-it-feature-validation-v1`
- Candidate conditions: `['positive_feature_3222', 'negative_feature_16008', 'bundle_feature_group']`
- Reference condition: `dense_direction`
- Sample size: `18`
- Seed: `20260319`
- Annotation mode: `locked_manual_rubric_single_rater`
- Annotation source: `manual_annotations_locked_v1.jsonl`
- Claim boundary: pilot feature-ranking evidence only; stronger publication-grade claims still require independent second-rater confirmation.

Artifacts:
- `blinded_pairs.jsonl`
- `blinded_packet.md`
- `answer_key.jsonl`
- `manual_annotations_template.jsonl`
- `manual_annotations.jsonl`
- `manual_annotations_locked_v1.jsonl`
- `manual_annotations_simulated.jsonl` (retained for historical triage trace)
- `summary.json`

Manual audit summary:
- `positive_feature_3222_vs_dense_direction`: prompt-grounded creativity candidate win `0.167`, reference win `0.500`, coherence candidate win `0.333`, coherence reference win `0.667`
- `negative_feature_16008_vs_dense_direction`: prompt-grounded creativity candidate win `0.667`, reference win `0.333`, coherence candidate win `0.667`, coherence reference win `0.333`
- `bundle_feature_group_vs_dense_direction`: prompt-grounded creativity candidate win `1.000`, reference win `0.000`, coherence candidate win `1.000`, coherence reference win `0.000`
