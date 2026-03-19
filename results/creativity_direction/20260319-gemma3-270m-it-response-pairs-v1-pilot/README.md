# Instruction-Tuned Creativity Response Pairs

- Generated at: `2026-03-19T08:49:52-05:00`
- Model: `google/gemma-3-270m-it`
- Device: `mps`
- Candidate prompt count: `32`
- Accepted pair count: `18`
- Max new tokens: `96`
- Seed base: `9300`
- Min counterpart overlap: `0.30`
- Max negative prompt-grounding delta: `0.10`
- Neutral story prompt: `Write a short story inspired by the prompt below.

Prompt: {prompt}`
- Creativity source prompt: `Write a creative short story inspired by the prompt below. Be imaginative, specific, vivid, and surprising while staying coherent.

Prompt: {prompt}`
- Plain rewrite prompt: `Rewrite the assistant story below in a plain, literal style.
Keep the same characters, setting, sequence of events, and ending.
Do not add new plot points, remove major content, or change the point of view.
Avoid figurative language and unusual turns of phrase.
Return only the rewritten story.

Prompt: {prompt}

Assistant story:
{source_story}`

Side summaries:
- `positive`: mean words `76.89`, meta fraction `0.000`, mean meta score `0.000`
- `negative`: mean words `71.00`, meta fraction `0.000`, mean meta score `0.000`

- Mean counterpart overlap: `0.506`
- Mean prompt-grounding delta: `0.000`

Rejection counts:
- `low_counterpart_overlap`: `14`
- `positive_meta_marker`: `1`

Artifacts:
- `prompts/creative_direction_it_v1_pilot_pairs.jsonl`
- `prompts/creative_direction_it_v1_rejected_pairs.jsonl`
- `prompts/creative_direction_it_v1_metadata.json`
- `prompts/creative_direction_it_v1_templates.json`
- `summary.json`
