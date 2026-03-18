# Creativity Direction Calibration

- Generated at: `2026-03-18T14:34:08-05:00`
- Model: `google/gemma-2-2b`
- Device: `mps`
- Prompt count: `6`
- Candidate layers: `[22, 0]`
- Steering coefficients: `[-1.0, 0.5, 1.0, 2.0]`
- Max new tokens: `96`
- Seed base: `3100`
- Neutral prompt template: `Prompt: {prompt}

Story:
Once`
- Creative baseline prompt template: `Prompt: {prompt}

Creative story:
Once`

Condition summaries:
- `creative_prompt_unsteered`: mean words `80.83`, meta fraction `0.000`, distinct-unigram ratio `0.653`, layer 22 projection `112.86`, layer 0 projection `4.15`
- `neutral_steered_layer0_coeff_0p5`: mean words `77.50`, meta fraction `0.000`, distinct-unigram ratio `0.575`, layer 22 projection `131.90`, layer 0 projection `8.41`
- `neutral_steered_layer0_coeff_1p0`: mean words `80.83`, meta fraction `0.000`, distinct-unigram ratio `0.577`, layer 22 projection `125.27`, layer 0 projection `-2.86`
- `neutral_steered_layer0_coeff_2p0`: mean words `81.50`, meta fraction `0.000`, distinct-unigram ratio `0.672`, layer 22 projection `99.94`, layer 0 projection `3.29`
- `neutral_steered_layer0_coeff_neg1p0`: mean words `78.17`, meta fraction `0.000`, distinct-unigram ratio `0.687`, layer 22 projection `93.80`, layer 0 projection `-1.83`
- `neutral_steered_layer22_coeff_0p5`: mean words `82.83`, meta fraction `0.000`, distinct-unigram ratio `0.639`, layer 22 projection `119.56`, layer 0 projection `9.41`
- `neutral_steered_layer22_coeff_1p0`: mean words `83.00`, meta fraction `0.000`, distinct-unigram ratio `0.675`, layer 22 projection `82.29`, layer 0 projection `-6.28`
- `neutral_steered_layer22_coeff_2p0`: mean words `77.83`, meta fraction `0.000`, distinct-unigram ratio `0.652`, layer 22 projection `91.71`, layer 0 projection `3.98`
- `neutral_steered_layer22_coeff_neg1p0`: mean words `84.67`, meta fraction `0.000`, distinct-unigram ratio `0.626`, layer 22 projection `101.10`, layer 0 projection `2.24`
- `neutral_unsteered`: mean words `75.83`, meta fraction `0.000`, distinct-unigram ratio `0.682`, layer 22 projection `95.38`, layer 0 projection `5.70`

Artifacts:
- `summary.json`
- `outputs.jsonl`
