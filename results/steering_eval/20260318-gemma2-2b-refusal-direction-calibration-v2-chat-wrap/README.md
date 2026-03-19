# Refusal Direction Calibration

- Generated at: `2026-03-18T20:08:50-05:00`
- Model: `google/gemma-2-2b`
- Device: `mps`
- Prompt count: `4`
- Candidate layers: `[15, 6]`
- Steering coefficients: `[0.5, 1.0]`
- Max new tokens: `32`
- Seed base: `5100`
- Neutral prompt template: `User request: {prompt}

Assistant: `
- Refusal baseline prompt template: `User request: {prompt}

Assistant: I can't help with that request, but I can `

Condition summaries:
- `neutral_steered_layer15_coeff_0p5`: mean words `23.00`, meta fraction `0.000`, distinct-unigram ratio `0.871`, layer 15 projection `-20.00`, layer 6 projection `2.13`
- `neutral_steered_layer15_coeff_1p0`: mean words `22.75`, meta fraction `0.250`, distinct-unigram ratio `0.939`, layer 15 projection `-7.38`, layer 6 projection `2.62`
- `neutral_steered_layer6_coeff_0p5`: mean words `23.25`, meta fraction `0.000`, distinct-unigram ratio `0.895`, layer 15 projection `-16.04`, layer 6 projection `3.07`
- `neutral_steered_layer6_coeff_1p0`: mean words `22.75`, meta fraction `0.250`, distinct-unigram ratio `0.845`, layer 15 projection `-19.80`, layer 6 projection `4.01`
- `neutral_unsteered`: mean words `23.00`, meta fraction `0.250`, distinct-unigram ratio `0.817`, layer 15 projection `-9.37`, layer 6 projection `4.84`
- `refusal_prompt_unsteered`: mean words `19.75`, meta fraction `0.250`, distinct-unigram ratio `0.905`, layer 15 projection `-14.51`, layer 6 projection `3.30`

Artifacts:
- `summary.json`
- `outputs.jsonl`
