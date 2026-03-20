# Instruction-Tuned Creativity Rubric Re-Evaluation

- Generated at: `2026-03-20T10:46:16-05:00`
- Source artifact: `results/steering_eval/20260319-gemma3-270m-it-output-gate-v1`
- Judge model: `google/gemma-3-270m-it`
- Device: `mps`
- Prompt count: `12`
- Comparisons: `['creative_prompt_unsteered_vs_neutral_unsteered', 'neutral_steered_layer12_coeff_0p5_vs_neutral_unsteered', 'neutral_steered_layer12_coeff_1p0_vs_neutral_unsteered', 'neutral_steered_layer12_coeff_0p5_vs_creative_prompt_unsteered', 'neutral_steered_layer12_coeff_1p0_vs_creative_prompt_unsteered']`
- Judge max new tokens: `128`
- Minimum winner margin: `0.5`
- Automatic pass recommendation: `False`
- Automatic pass rule: `best dense condition has positive prompt-grounded creativity mean score delta and non-negative coherence mean score delta versus neutral`
- Judge usable for claim-bearing: `False`
- Judge health failures: `['prompt_grounded_creativity_collapsed_to_constant_ties', 'coherence_collapsed_to_constant_ties']`

Comparison summaries:
- `creative_prompt_unsteered_vs_neutral_unsteered`: creativity delta `0.000`, coherence delta `0.000`, parse success `1.000`
- `neutral_steered_layer12_coeff_0p5_vs_neutral_unsteered`: creativity delta `0.000`, coherence delta `0.000`, parse success `1.000`
- `neutral_steered_layer12_coeff_1p0_vs_neutral_unsteered`: creativity delta `0.000`, coherence delta `0.000`, parse success `1.000`
- `neutral_steered_layer12_coeff_0p5_vs_creative_prompt_unsteered`: creativity delta `0.000`, coherence delta `0.000`, parse success `1.000`
- `neutral_steered_layer12_coeff_1p0_vs_creative_prompt_unsteered`: creativity delta `0.000`, coherence delta `0.000`, parse success `1.000`

Artifacts:
- `summary.json`
- `rubric_judgments.jsonl`
