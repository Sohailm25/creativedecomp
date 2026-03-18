# Creativity Response Pairs V3

- Generated at: `2026-03-18T14:25:12-05:00`
- Model: `google/gemma-2-2b`
- Device: `mps`
- Candidate prompt count: `32`
- Accepted pair count: `31`
- Max new tokens: `96`
- Seed base: `3600`
- Min counterpart overlap: `0.30`
- Max negative prompt-grounding delta: `0.10`
- Positive source prompt: `Prompt: {prompt}

Creative story:
Once`
- Negative rewrite prompt: `Rewrite the story below in a plain, literal style.
Keep the same characters, setting, sequence of events, and ending.
Do not add new plot points, remove major content, or change the point of view.

Prompt: {prompt}

Source story:
{source_story}

Plain rewrite:
Once`
- Shared extraction prompt: `Prompt: {prompt}

Story:
Once`

Side summaries:
- `positive`: mean words `79.77`, meta fraction `0.000`, mean meta score `0.000`
- `negative`: mean words `79.23`, meta fraction `0.000`, mean meta score `0.000`

- Mean counterpart overlap: `0.914`
- Mean prompt-grounding delta: `0.002`

Rejection counts:
- `low_counterpart_overlap`: `1`

Artifacts:
- `prompts/creative_direction_v3_pilot_pairs.jsonl`
- `prompts/creative_direction_v3_response_only_pairs.jsonl`
- `prompts/creative_direction_v3_rejected_pairs.jsonl`
- `prompts/creative_direction_v3_metadata.json`
- `prompts/creative_direction_v3_templates.json`
- `summary.json`
