# Instruction-Tuned Creativity Output Gate Manual Audit

- Generated at: `2026-03-19T16:35:20-05:00`
- Source artifact: `scratch/feature_validation_audit_source`
- Candidate conditions: `['positive_feature_3222', 'negative_feature_16008', 'bundle_feature_group']`
- Reference condition: `dense_direction`
- Sample size: `18`
- Seed: `20260319`
- Annotation mode: `simulated_heuristic_annotation` (non-claim-bearing triage only)

Artifacts:
- `blinded_pairs.jsonl`
- `blinded_packet.md`
- `answer_key.jsonl`
- `manual_annotations_template.jsonl`
- `manual_annotations.jsonl`
- `summary.json`

Manual audit summary:
- `positive_feature_3222_vs_dense_direction`: prompt-grounded creativity candidate win `0.500`, reference win `0.333`, coherence candidate win `0.500`, coherence reference win `0.333`
- `negative_feature_16008_vs_dense_direction`: prompt-grounded creativity candidate win `0.333`, reference win `0.500`, coherence candidate win `0.500`, coherence reference win `0.333`
- `bundle_feature_group_vs_dense_direction`: prompt-grounded creativity candidate win `0.667`, reference win `0.333`, coherence candidate win `0.667`, coherence reference win `0.167`
