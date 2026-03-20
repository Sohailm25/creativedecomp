# Instruction-Tuned Creativity Output Gate Manual Audit

- Generated at: `2026-03-20T11:39:13-05:00`
- Source artifact: `results/creativity_benchmarks/20260320-gemma3-270m-it-feature-validation-benchmark-writing-v1`
- Candidate conditions: `['bundle_feature_group']`
- Reference condition: `dense_direction`
- Sample size: `10`
- Seed: `20260320`

Artifacts:
- `blinded_pairs.jsonl`
- `blinded_packet.md`
- `answer_key.jsonl`
- `manual_annotations_template.jsonl`
- `manual_annotations.jsonl`
- `summary.json`

Manual audit summary:
- `bundle_feature_group_vs_dense_direction`: prompt-grounded creativity candidate win `0.200`, reference win `0.500`, coherence candidate win `0.400`, coherence reference win `0.400`
