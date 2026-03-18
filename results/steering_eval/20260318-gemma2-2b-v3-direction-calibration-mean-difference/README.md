# Creativity Direction Calibration

- Generated at: `2026-03-18T14:54:27-05:00`
- Model: `google/gemma-2-2b`
- Device: `mps`
- Prompt count: `6`
- Candidate layers: `[23, 10]`
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
- `creative_prompt_unsteered`: mean words `80.83`, meta fraction `0.000`, distinct-unigram ratio `0.653`, layer 23 projection `24.21`, layer 10 projection `3.18`
- `neutral_steered_layer10_coeff_0p5`: mean words `79.33`, meta fraction `0.000`, distinct-unigram ratio `0.589`, layer 23 projection `27.40`, layer 10 projection `7.38`
- `neutral_steered_layer10_coeff_1p0`: mean words `80.17`, meta fraction `0.000`, distinct-unigram ratio `0.578`, layer 23 projection `18.62`, layer 10 projection `7.85`
- `neutral_steered_layer10_coeff_2p0`: mean words `82.17`, meta fraction `0.000`, distinct-unigram ratio `0.650`, layer 23 projection `14.44`, layer 10 projection `6.16`
- `neutral_steered_layer10_coeff_neg1p0`: mean words `78.67`, meta fraction `0.000`, distinct-unigram ratio `0.678`, layer 23 projection `25.49`, layer 10 projection `4.78`
- `neutral_steered_layer23_coeff_0p5`: mean words `82.17`, meta fraction `0.000`, distinct-unigram ratio `0.638`, layer 23 projection `26.42`, layer 10 projection `9.11`
- `neutral_steered_layer23_coeff_1p0`: mean words `82.17`, meta fraction `0.000`, distinct-unigram ratio `0.682`, layer 23 projection `34.47`, layer 10 projection `5.96`
- `neutral_steered_layer23_coeff_2p0`: mean words `78.67`, meta fraction `0.000`, distinct-unigram ratio `0.623`, layer 23 projection `-7.57`, layer 10 projection `7.82`
- `neutral_steered_layer23_coeff_neg1p0`: mean words `84.50`, meta fraction `0.000`, distinct-unigram ratio `0.625`, layer 23 projection `15.68`, layer 10 projection `5.34`
- `neutral_unsteered`: mean words `75.83`, meta fraction `0.000`, distinct-unigram ratio `0.682`, layer 23 projection `15.27`, layer 10 projection `4.83`

Artifacts:
- `summary.json`
- `outputs.jsonl`
