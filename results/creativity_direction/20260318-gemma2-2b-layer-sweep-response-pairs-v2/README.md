# Creativity Direction Layer Sweep

- Generated at: `2026-03-18T12:01:31-05:00`
- Model: `google/gemma-2-2b`
- Device: `mps`
- Candidate layers: `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]`
- Pair count: `32`
- Raw ranking rule: `positive_gt_negative_fraction, margin_zscore, mean_margin`
- Controlled ranking rule: `controlled_fraction_delta, controlled_margin_zscore_delta, abs(template_direction_cosine), positive_gt_negative_fraction`
- Raw best layer: `24`
- Controlled best layer: `24`

Top controlled layers:
- Controlled best raw fraction: `0.593750`
- Controlled best template-control fraction: `0.000000`
- Controlled best fraction delta: `0.593750`
- Controlled best cosine: `0.000000`

- layer `24`: raw fraction `0.593750`, template fraction `0.000000`, delta `0.593750`, cosine `0.000000`
- layer `20`: raw fraction `0.593750`, template fraction `0.000000`, delta `0.593750`, cosine `0.000000`
- layer `19`: raw fraction `0.593750`, template fraction `0.000000`, delta `0.593750`, cosine `0.000000`
- layer `18`: raw fraction `0.593750`, template fraction `0.000000`, delta `0.593750`, cosine `0.000000`
- layer `22`: raw fraction `0.593750`, template fraction `0.000000`, delta `0.593750`, cosine `0.000000`

Top raw layers:
- layer `24`: raw fraction `0.593750`, margin `41.727730`, z-score `0.223602`
- layer `20`: raw fraction `0.593750`, margin `20.445059`, z-score `0.182228`
- layer `19`: raw fraction `0.593750`, margin `18.285555`, z-score `0.181639`
- layer `18`: raw fraction `0.593750`, margin `15.452930`, z-score `0.177485`
- layer `22`: raw fraction `0.593750`, margin `23.999130`, z-score `0.160862`

Artifacts:
- `summary.json`
- `layer_metrics.jsonl`
- `layer_metrics_raw.jsonl`
- `controlled_best_layer_pair_details.jsonl`
- `raw_best_layer_pair_details.jsonl`
- `directions.npz`
