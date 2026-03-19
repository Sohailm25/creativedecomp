# Refusal Direction Layer Sweep

- Generated at: `2026-03-18T19:51:41-05:00`
- Model: `google/gemma-2-2b`
- Device: `mps`
- Direction method: `mean_difference`
- Candidate layers: `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]`
- Pair count: `32`
- Raw ranking rule: `positive_gt_negative_fraction, margin_zscore, mean_margin`
- Controlled ranking rule: `controlled_fraction_delta, controlled_margin_zscore_delta, abs(template_direction_cosine), positive_gt_negative_fraction`
- Raw best layer: `15`
- Controlled best layer: `15`

Top controlled layers:
- Controlled best raw fraction: `1.000000`
- Controlled best template-control fraction: `0.000000`
- Controlled best fraction delta: `1.000000`
- Controlled best cosine: `0.000000`

- layer `15`: raw fraction `1.000000`, template fraction `0.000000`, delta `1.000000`, cosine `0.000000`
- layer `6`: raw fraction `1.000000`, template fraction `0.000000`, delta `1.000000`, cosine `0.000000`
- layer `16`: raw fraction `1.000000`, template fraction `0.000000`, delta `1.000000`, cosine `0.000000`
- layer `13`: raw fraction `1.000000`, template fraction `0.000000`, delta `1.000000`, cosine `0.000000`
- layer `14`: raw fraction `1.000000`, template fraction `0.000000`, delta `1.000000`, cosine `0.000000`

Top raw layers:
- layer `15`: raw fraction `1.000000`, margin `101.736717`, z-score `7.607582`
- layer `6`: raw fraction `1.000000`, margin `15.302435`, z-score `7.441467`
- layer `16`: raw fraction `1.000000`, margin `120.222305`, z-score `7.159396`
- layer `13`: raw fraction `1.000000`, margin `82.089859`, z-score `7.050806`
- layer `14`: raw fraction `1.000000`, margin `86.078972`, z-score `7.043380`

Artifacts:
- `summary.json`
- `layer_metrics.jsonl`
- `layer_metrics_raw.jsonl`
- `controlled_best_layer_pair_details.jsonl`
- `raw_best_layer_pair_details.jsonl`
- `directions.npz`
