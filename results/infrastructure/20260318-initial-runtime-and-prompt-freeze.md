# Initial Runtime And Prompt Freeze

- Generated at: `2026-03-18T10:04:34-05:00`
- Python: `3.14.2`
- Source dataset: `euclaise/writingprompts` / `train`
- Prompt split: `32` pilot / `128` confirm
- Direct dependencies:
  - `accelerate==1.13.0`
  - `datasets==4.8.2`
  - `playwright==1.58.0`
  - `repeng==0.4.0`
  - `sae-lens==6.38.0`
  - `safetensors==0.7.0`
  - `scipy==1.17.1`
  - `sentencepiece==0.2.1`
  - `torch==2.10.0`
  - `transformers==5.3.0`
- Artifacts:
  - `prompts/creative_direction_v1_pilot.jsonl`
  - `prompts/creative_direction_v1_confirm.jsonl`
  - `prompts/creative_direction_v1_templates.json`
  - `requirements.txt`
  - `requirements.lock.txt`

This freeze is the starting point for the first local creativity-direction replication slice.
The prompt split is deterministic and must not be changed without logging a new split id.
