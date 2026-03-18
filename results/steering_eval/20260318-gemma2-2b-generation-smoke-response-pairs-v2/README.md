# Generation-Side Creativity Smoke

- Generated at: `2026-03-18T12:03:40-05:00`
- Model: `google/gemma-2-2b`
- Device: `mps`
- Prompt count: `4`
- Candidate layers from sweep: `[24, 20]`
- Steering coefficient: `1.0`
- Max new tokens: `96`
- Seed base: `1729`
- Neutral prompt template: `Prompt: {prompt}

Story:
Once`
- Creative baseline prompt template: `Prompt: {prompt}

Creative story:
Once`

Conditions:
- `neutral_unsteered`: prompt mode `neutral`, layer `None`, coeff `0.0`
- `creative_prompt_unsteered`: prompt mode `prompt_only_creativity`, layer `None`, coeff `0.0`
- `neutral_steered_layer24`: prompt mode `neutral`, layer `24`, coeff `1.0`
- `neutral_steered_layer20`: prompt mode `neutral`, layer `20`, coeff `1.0`

Condition summaries:
- `creative_prompt_unsteered`: mean words `80.25`, mean chars `395.50`
- `neutral_steered_layer20`: mean words `83.50`, mean chars `410.50`
- `neutral_steered_layer24`: mean words `78.25`, mean chars `388.75`
- `neutral_unsteered`: mean words `80.50`, mean chars `392.50`

Artifacts:
- `summary.json`
- `outputs.jsonl`
