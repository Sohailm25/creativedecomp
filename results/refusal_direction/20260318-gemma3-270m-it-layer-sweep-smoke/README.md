# Instruction-Tuned Refusal Layer Sweep

- Generated at: `2026-03-18T22:54:19.828965`
- Model: `google/gemma-3-270m-it`
- Device: `mps`
- SAE release: `gemma-scope-2-270m-it-res`
- Reference SAE id: `layer_12_width_16k_l0_medium`
- Candidate layers: `[5, 9, 12, 15]`
- Pair count: `4`
- Best layer: `12`

Top layers:
- layer `12`: fraction `1.000000`, margin `2052.036621`, z-score `14.605062`
- layer `15`: fraction `1.000000`, margin `4374.102051`, z-score `13.189101`
- layer `9`: fraction `1.000000`, margin `498.739929`, z-score `10.984205`
- layer `5`: fraction `1.000000`, margin `60.302078`, z-score `5.407584`

Artifacts:
- `summary.json`
- `layer_metrics.jsonl`
- `best_layer_pair_details.jsonl`
- `directions.npz`
