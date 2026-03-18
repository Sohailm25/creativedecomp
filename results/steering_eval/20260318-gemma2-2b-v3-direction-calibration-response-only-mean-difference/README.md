# Creativity Direction Calibration

- Generated at: `2026-03-18T14:58:12-05:00`
- Model: `google/gemma-2-2b`
- Device: `mps`
- Prompt count: `6`
- Candidate layers: `[9, 4]`
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
- `creative_prompt_unsteered`: mean words `80.83`, meta fraction `0.000`, distinct-unigram ratio `0.653`, layer 9 projection `-9.44`, layer 4 projection `-5.04`
- `neutral_steered_layer4_coeff_0p5`: mean words `79.33`, meta fraction `0.000`, distinct-unigram ratio `0.589`, layer 9 projection `-4.57`, layer 4 projection `-2.29`
- `neutral_steered_layer4_coeff_1p0`: mean words `80.17`, meta fraction `0.000`, distinct-unigram ratio `0.580`, layer 9 projection `-3.48`, layer 4 projection `-1.89`
- `neutral_steered_layer4_coeff_2p0`: mean words `83.67`, meta fraction `0.000`, distinct-unigram ratio `0.649`, layer 9 projection `-6.81`, layer 4 projection `-4.37`
- `neutral_steered_layer4_coeff_neg1p0`: mean words `78.00`, meta fraction `0.000`, distinct-unigram ratio `0.682`, layer 9 projection `-7.73`, layer 4 projection `-3.16`
- `neutral_steered_layer9_coeff_0p5`: mean words `82.00`, meta fraction `0.000`, distinct-unigram ratio `0.657`, layer 9 projection `-2.08`, layer 4 projection `-0.19`
- `neutral_steered_layer9_coeff_1p0`: mean words `82.00`, meta fraction `0.000`, distinct-unigram ratio `0.691`, layer 9 projection `-9.07`, layer 4 projection `-3.18`
- `neutral_steered_layer9_coeff_2p0`: mean words `76.83`, meta fraction `0.000`, distinct-unigram ratio `0.644`, layer 9 projection `-6.96`, layer 4 projection `-2.79`
- `neutral_steered_layer9_coeff_neg1p0`: mean words `84.67`, meta fraction `0.000`, distinct-unigram ratio `0.626`, layer 9 projection `-4.58`, layer 4 projection `-1.97`
- `neutral_unsteered`: mean words `75.83`, meta fraction `0.000`, distinct-unigram ratio `0.682`, layer 9 projection `-5.53`, layer 4 projection `-2.45`

Artifacts:
- `summary.json`
- `outputs.jsonl`
