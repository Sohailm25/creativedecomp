# Instruction-Tuned Creativity Output Gate

- Generated at: `2026-03-19T08:54:19.164355`
- Model: `google/gemma-3-270m-it`
- Device: `mps`
- SAE release: `gemma-scope-2-270m-it-res`
- Prompt count: `12`
- Primary hidden layer: `12`
- Steering coefficients: `[0.5, 1.0]`
- Max new tokens: `96`
- Judge max new tokens: `6`
- Neutral story prompt: `Write a short story inspired by the prompt below.

Prompt: {prompt}`
- Creativity baseline prompt: `Write a creative short story inspired by the prompt below. Be imaginative, specific, vivid, and surprising while staying coherent.

Prompt: {prompt}`
- Automatic pass recommendation: `False`
- Automatic pass rule: `best dense condition has positive creativity net preference versus neutral and non-negative coherence net preference versus neutral`

Condition summaries:
- `creative_prompt_unsteered`: mean words `75.25`, meta fraction `0.000`, distinct-unigram ratio `0.747`, repeated-bigram fraction `0.022`
- `neutral_steered_layer12_coeff_0p5`: mean words `71.08`, meta fraction `0.000`, distinct-unigram ratio `0.650`, repeated-bigram fraction `0.033`
- `neutral_steered_layer12_coeff_1p0`: mean words `76.75`, meta fraction `0.000`, distinct-unigram ratio `0.734`, repeated-bigram fraction `0.029`
- `neutral_unsteered`: mean words `76.58`, meta fraction `0.000`, distinct-unigram ratio `0.738`, repeated-bigram fraction `0.017`

Pairwise judgment summaries:
- `creative_prompt_unsteered_vs_neutral_unsteered`: creativity candidate win `0.000`, creativity reference win `0.000`, coherence candidate win `0.000`, coherence reference win `0.000`
- `neutral_steered_layer12_coeff_0p5_vs_neutral_unsteered`: creativity candidate win `0.000`, creativity reference win `0.000`, coherence candidate win `0.000`, coherence reference win `0.000`
- `neutral_steered_layer12_coeff_1p0_vs_neutral_unsteered`: creativity candidate win `0.000`, creativity reference win `0.000`, coherence candidate win `0.000`, coherence reference win `0.000`
- `neutral_steered_layer12_coeff_0p5_vs_creative_prompt_unsteered`: creativity candidate win `0.000`, creativity reference win `0.000`, coherence candidate win `0.000`, coherence reference win `0.000`
- `neutral_steered_layer12_coeff_1p0_vs_creative_prompt_unsteered`: creativity candidate win `0.000`, creativity reference win `0.000`, coherence candidate win `0.000`, coherence reference win `0.000`

Artifacts:
- `summary.json`
- `generated_outputs.jsonl`
- `pairwise_judgments.jsonl`
