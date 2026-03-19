# Instruction-Tuned Creativity Output Gate Manual Audit

- Generated at: `2026-03-19T08:59:25-05:00`
- Source artifact: `results/steering_eval/20260319-gemma3-270m-it-output-gate-v1`
- Candidate conditions: `['creative_prompt_unsteered', 'neutral_steered_layer12_coeff_0p5', 'neutral_steered_layer12_coeff_1p0']`
- Reference condition: `neutral_unsteered`
- Sample size: `36`
- Seed: `20260319`

Artifacts:
- `blinded_pairs.jsonl`
- `blinded_packet.md`
- `answer_key.jsonl`
- `manual_annotations_template.jsonl`
- `manual_annotations.jsonl`
- `summary.json`

Manual audit summary:
- `creative_prompt_unsteered_vs_neutral_unsteered`: prompt-grounded creativity candidate win `0.417`, reference win `0.417`, coherence candidate win `0.500`, coherence reference win `0.333`
- `neutral_steered_layer12_coeff_0p5_vs_neutral_unsteered`: prompt-grounded creativity candidate win `0.333`, reference win `0.417`, coherence candidate win `0.500`, coherence reference win `0.417`
- `neutral_steered_layer12_coeff_1p0_vs_neutral_unsteered`: prompt-grounded creativity candidate win `0.583`, reference win `0.083`, coherence candidate win `0.917`, coherence reference win `0.083`
