# Creativity Direction Layer Sweep

- Generated at: `2026-03-18T10:50:00-05:00`
- Model: `google/gemma-2-2b`
- Device: `mps`
- Candidate layers: `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]`
- Pair count: `32`
- Ranking rule: `positive_gt_negative_fraction, margin_zscore, mean_margin`
- Best layer: `0`
- Best positive > negative fraction: `1.000000`
- Best mean margin: `0.704925`
- Best margin z-score: `0.932329`

Top layers:
- layer `0`: fraction `1.000000`, margin `0.704925`, z-score `0.932329`
- layer `7`: fraction `0.906250`, margin `0.897024`, z-score `0.519957`
- layer `10`: fraction `0.781250`, margin `1.653073`, z-score `0.465009`
- layer `25`: fraction `0.750000`, margin `4.445136`, z-score `0.597613`
- layer `15`: fraction `0.750000`, margin `3.584769`, z-score `0.531641`

Artifacts:
- `summary.json`
- `layer_metrics.jsonl`
- `best_layer_pair_details.jsonl`
- `directions.npz`
