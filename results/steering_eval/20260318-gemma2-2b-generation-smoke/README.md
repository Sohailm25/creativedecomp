# Generation-Side Creativity Smoke

- Generated at: `2026-03-18T11:00:35-05:00`
- Model: `google/gemma-2-2b`
- Device: `mps`
- Prompt count: `4`
- Candidate layers from sweep: `[0, 7]`
- Steering coefficient: `1.0`
- Max new tokens: `96`
- Seed base: `1729`
- Neutral prompt template: `Write a short story inspired by the prompt below.

Prompt: {prompt}`

Conditions:
- `neutral_unsteered`: prompt mode `neutral`, layer `None`, coeff `0.0`
- `creative_prompt_unsteered`: prompt mode `prompt_only_creativity`, layer `None`, coeff `0.0`
- `neutral_steered_layer0`: prompt mode `neutral`, layer `0`, coeff `1.0`
- `neutral_steered_layer7`: prompt mode `neutral`, layer `7`, coeff `1.0`

Condition summaries:
- `creative_prompt_unsteered`: mean words `69.50`, mean chars `375.75`
- `neutral_steered_layer0`: mean words `69.50`, mean chars `361.50`
- `neutral_steered_layer7`: mean words `75.25`, mean chars `386.25`
- `neutral_unsteered`: mean words `71.00`, mean chars `361.50`

Artifacts:
- `summary.json`
- `outputs.jsonl`
