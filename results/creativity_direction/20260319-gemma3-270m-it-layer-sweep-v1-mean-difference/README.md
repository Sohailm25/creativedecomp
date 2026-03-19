# Instruction-Tuned Creativity Layer Sweep

- Generated at: `2026-03-19T08:49:58.470648`
- Model: `google/gemma-3-270m-it`
- Device: `mps`
- SAE release: `gemma-scope-2-270m-it-res`
- Reference SAE id: `layer_12_width_16k_l0_medium`
- Candidate layers: `[5, 9, 12, 15]`
- Pair count: `18`
- Best layer: `12`

Top layers:
- layer `12`: fraction `0.611111`, margin `864.182495`, z-score `0.725631`
- layer `15`: fraction `0.611111`, margin `1809.045044`, z-score `0.718191`
- layer `5`: fraction `0.500000`, margin `56.950943`, z-score `0.679300`
- layer `9`: fraction `0.500000`, margin `230.124054`, z-score `0.572687`

Artifacts:
- `summary.json`
- `layer_metrics.jsonl`
- `best_layer_pair_details.jsonl`
- `directions.npz`
