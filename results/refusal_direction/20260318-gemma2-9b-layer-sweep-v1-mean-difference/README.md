# Refusal Direction Layer Sweep

- Generated at: `2026-03-18T20:39:14-05:00`
- Model: `google/gemma-2-9b`
- Device: `mps`
- Direction method: `mean_difference`
- Candidate layers: `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41]`
- Pair count: `32`
- Raw ranking rule: `positive_gt_negative_fraction, margin_zscore, mean_margin`
- Controlled ranking rule: `controlled_fraction_delta, controlled_margin_zscore_delta, abs(template_direction_cosine), positive_gt_negative_fraction`
- Raw best layer: `18`
- Controlled best layer: `18`

Top controlled layers:
- Controlled best raw fraction: `1.000000`
- Controlled best template-control fraction: `0.000000`
- Controlled best fraction delta: `1.000000`
- Controlled best cosine: `0.000000`

- layer `18`: raw fraction `1.000000`, template fraction `0.000000`, delta `1.000000`, cosine `0.000000`
- layer `20`: raw fraction `1.000000`, template fraction `0.000000`, delta `1.000000`, cosine `0.000000`
- layer `19`: raw fraction `1.000000`, template fraction `0.000000`, delta `1.000000`, cosine `0.000000`
- layer `16`: raw fraction `1.000000`, template fraction `0.000000`, delta `1.000000`, cosine `0.000000`
- layer `21`: raw fraction `1.000000`, template fraction `0.000000`, delta `1.000000`, cosine `0.000000`

Top raw layers:
- layer `18`: raw fraction `1.000000`, margin `99.187210`, z-score `8.339555`
- layer `20`: raw fraction `1.000000`, margin `105.778305`, z-score `8.173344`
- layer `19`: raw fraction `1.000000`, margin `100.859901`, z-score `7.920706`
- layer `16`: raw fraction `1.000000`, margin `81.190147`, z-score `7.743508`
- layer `21`: raw fraction `1.000000`, margin `112.801987`, z-score `7.522220`

Artifacts:
- `summary.json`
- `layer_metrics.jsonl`
- `layer_metrics_raw.jsonl`
- `controlled_best_layer_pair_details.jsonl`
- `raw_best_layer_pair_details.jsonl`
- `directions.npz`
