# Creativity Output Gate

- Generated at: `2026-03-18T15:58:38-05:00`
- Model: `google/gemma-2-2b`
- Device: `mps`
- Prompt count: `31`
- Primary hidden layer: `23`
- Steering coefficients: `[0.5, 1.0]`
- Max new tokens: `96`
- Judge max new tokens: `6`
- Seed base: `4100`
- Judge template path: `prompts/creative_direction_output_gate_v1_judges.json`
- Reused generated outputs: `True`
- Order-robust judging: `True` (winner must agree under both A/B orders or the result becomes `tie`)
- Automatic pass recommendation: `False`
- Automatic pass rule: `best dense condition has positive creativity net preference versus neutral and non-negative coherence net preference versus neutral`

Condition summaries:
- `creative_prompt_unsteered`: mean words `80.06`, meta fraction `0.000`, distinct-unigram ratio `0.641`, repeated-bigram fraction `0.078`
- `neutral_steered_layer23_coeff_0p5`: mean words `80.35`, meta fraction `0.000`, distinct-unigram ratio `0.649`, repeated-bigram fraction `0.085`
- `neutral_steered_layer23_coeff_1p0`: mean words `82.16`, meta fraction `0.000`, distinct-unigram ratio `0.630`, repeated-bigram fraction `0.101`
- `neutral_unsteered`: mean words `79.84`, meta fraction `0.000`, distinct-unigram ratio `0.644`, repeated-bigram fraction `0.092`

Pairwise judgment summaries:
- `creative_prompt_unsteered_vs_neutral_unsteered`: creativity candidate win `0.000`, creativity reference win `0.000`, coherence candidate win `0.000`, coherence reference win `0.000`
- `neutral_steered_layer23_coeff_0p5_vs_neutral_unsteered`: creativity candidate win `0.000`, creativity reference win `0.000`, coherence candidate win `0.000`, coherence reference win `0.000`
- `neutral_steered_layer23_coeff_1p0_vs_neutral_unsteered`: creativity candidate win `0.000`, creativity reference win `0.000`, coherence candidate win `0.000`, coherence reference win `0.000`
- `neutral_steered_layer23_coeff_0p5_vs_creative_prompt_unsteered`: creativity candidate win `0.065`, creativity reference win `0.032`, coherence candidate win `0.000`, coherence reference win `0.032`
- `neutral_steered_layer23_coeff_1p0_vs_creative_prompt_unsteered`: creativity candidate win `0.000`, creativity reference win `0.065`, coherence candidate win `0.000`, coherence reference win `0.000`

Artifacts:
- `summary.json`
- `generated_outputs.jsonl`
- `pairwise_judgments.jsonl`
