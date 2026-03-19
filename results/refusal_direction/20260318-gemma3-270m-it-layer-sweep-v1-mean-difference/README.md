# Instruction-Tuned Refusal Layer Sweep

- Generated at: `2026-03-18T22:55:12.641992`
- Model: `google/gemma-3-270m-it`
- Device: `mps`
- SAE release: `gemma-scope-2-270m-it-res`
- Reference SAE id: `layer_12_width_16k_l0_medium`
- Candidate layers: `[5, 9, 12, 15]`
- Pair count: `32`
- Best layer: `9`

Top layers:
- layer `9`: fraction `1.000000`, margin `431.563232`, z-score `4.048515`
- layer `12`: fraction `1.000000`, margin `1628.116333`, z-score `3.661479`
- layer `15`: fraction `1.000000`, margin `3523.222168`, z-score `3.463804`
- layer `5`: fraction `1.000000`, margin `68.312958`, z-score `2.001950`

Artifacts:
- `summary.json`
- `layer_metrics.jsonl`
- `best_layer_pair_details.jsonl`
- `directions.npz`
