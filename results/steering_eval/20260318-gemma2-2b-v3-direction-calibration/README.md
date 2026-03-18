# Creativity Direction Calibration

- Generated at: `2026-03-18T14:30:37-05:00`
- Model: `google/gemma-2-2b`
- Device: `mps`
- Prompt count: `6`
- Candidate layers: `[6, 8]`
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
- `creative_prompt_unsteered`: mean words `80.83`, meta fraction `0.000`, distinct-unigram ratio `0.653`, layer 6 projection `-6.07`, layer 8 projection `-32.59`
- `neutral_steered_layer6_coeff_0p5`: mean words `82.00`, meta fraction `0.000`, distinct-unigram ratio `0.657`, layer 6 projection `-7.03`, layer 8 projection `-29.19`
- `neutral_steered_layer6_coeff_1p0`: mean words `83.33`, meta fraction `0.000`, distinct-unigram ratio `0.671`, layer 6 projection `-15.90`, layer 8 projection `-46.63`
- `neutral_steered_layer6_coeff_2p0`: mean words `76.67`, meta fraction `0.000`, distinct-unigram ratio `0.657`, layer 6 projection `-3.60`, layer 8 projection `-26.26`
- `neutral_steered_layer6_coeff_neg1p0`: mean words `85.33`, meta fraction `0.000`, distinct-unigram ratio `0.608`, layer 6 projection `-4.25`, layer 8 projection `-25.01`
- `neutral_steered_layer8_coeff_0p5`: mean words `77.67`, meta fraction `0.000`, distinct-unigram ratio `0.579`, layer 6 projection `-3.65`, layer 8 projection `-28.54`
- `neutral_steered_layer8_coeff_1p0`: mean words `80.83`, meta fraction `0.000`, distinct-unigram ratio `0.577`, layer 6 projection `-3.20`, layer 8 projection `-23.78`
- `neutral_steered_layer8_coeff_2p0`: mean words `82.33`, meta fraction `0.000`, distinct-unigram ratio `0.659`, layer 6 projection `-8.87`, layer 8 projection `-32.81`
- `neutral_steered_layer8_coeff_neg1p0`: mean words `78.00`, meta fraction `0.000`, distinct-unigram ratio `0.691`, layer 6 projection `-7.83`, layer 8 projection `-34.72`
- `neutral_unsteered`: mean words `75.83`, meta fraction `0.000`, distinct-unigram ratio `0.682`, layer 6 projection `-1.63`, layer 8 projection `-19.09`

Artifacts:
- `summary.json`
- `outputs.jsonl`
