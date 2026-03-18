# Creativity Direction Calibration

- Generated at: `2026-03-18T12:43:30-05:00`
- Model: `google/gemma-2-2b`
- Device: `mps`
- Prompt count: `6`
- Candidate layers: `[24, 20]`
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
- `creative_prompt_unsteered`: mean words `80.83`, meta fraction `0.000`, distinct-unigram ratio `0.653`, layer 24 projection `-29.14`, layer 20 projection `-28.29`
- `neutral_steered_layer20_coeff_0p5`: mean words `78.17`, meta fraction `0.000`, distinct-unigram ratio `0.594`, layer 24 projection `-28.02`, layer 20 projection `-49.65`
- `neutral_steered_layer20_coeff_1p0`: mean words `80.17`, meta fraction `0.000`, distinct-unigram ratio `0.578`, layer 24 projection `-61.39`, layer 20 projection `-73.88`
- `neutral_steered_layer20_coeff_2p0`: mean words `82.17`, meta fraction `0.000`, distinct-unigram ratio `0.624`, layer 24 projection `-100.10`, layer 20 projection `-86.28`
- `neutral_steered_layer20_coeff_neg1p0`: mean words `78.83`, meta fraction `0.000`, distinct-unigram ratio `0.693`, layer 24 projection `-9.71`, layer 20 projection `-32.48`
- `neutral_steered_layer24_coeff_0p5`: mean words `82.83`, meta fraction `0.000`, distinct-unigram ratio `0.639`, layer 24 projection `-13.66`, layer 20 projection `-36.87`
- `neutral_steered_layer24_coeff_1p0`: mean words `82.17`, meta fraction `0.000`, distinct-unigram ratio `0.682`, layer 24 projection `-42.78`, layer 20 projection `-46.23`
- `neutral_steered_layer24_coeff_2p0`: mean words `78.67`, meta fraction `0.000`, distinct-unigram ratio `0.623`, layer 24 projection `1.91`, layer 20 projection `-34.13`
- `neutral_steered_layer24_coeff_neg1p0`: mean words `84.67`, meta fraction `0.000`, distinct-unigram ratio `0.626`, layer 24 projection `-27.63`, layer 20 projection `-41.30`
- `neutral_unsteered`: mean words `75.83`, meta fraction `0.000`, distinct-unigram ratio `0.682`, layer 24 projection `13.36`, layer 20 projection `-13.28`

Artifacts:
- `summary.json`
- `outputs.jsonl`
