# Creativity Direction Layer Sweep

- Generated at: `2026-03-18T14:49:54-05:00`
- Model: `google/gemma-2-2b`
- Device: `mps`
- Direction method: `mean_difference`
- Candidate layers: `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]`
- Pair count: `31`
- Raw ranking rule: `positive_gt_negative_fraction, margin_zscore, mean_margin`
- Controlled ranking rule: `controlled_fraction_delta, controlled_margin_zscore_delta, abs(template_direction_cosine), positive_gt_negative_fraction`
- Raw best layer: `9`
- Controlled best layer: `9`

Top controlled layers:
- Controlled best raw fraction: `0.548387`
- Controlled best template-control fraction: `0.000000`
- Controlled best fraction delta: `0.548387`
- Controlled best cosine: `0.000000`

- layer `9`: raw fraction `0.548387`, template fraction `0.000000`, delta `0.548387`, cosine `0.000000`
- layer `4`: raw fraction `0.548387`, template fraction `0.000000`, delta `0.548387`, cosine `0.000000`
- layer `5`: raw fraction `0.548387`, template fraction `0.000000`, delta `0.548387`, cosine `0.000000`
- layer `10`: raw fraction `0.548387`, template fraction `0.000000`, delta `0.548387`, cosine `0.000000`
- layer `8`: raw fraction `0.548387`, template fraction `0.000000`, delta `0.548387`, cosine `0.000000`

Top raw layers:
- layer `9`: raw fraction `0.548387`, margin `13.131884`, z-score `0.828694`
- layer `4`: raw fraction `0.548387`, margin `10.079990`, z-score `0.826042`
- layer `5`: raw fraction `0.548387`, margin `10.847376`, z-score `0.822753`
- layer `10`: raw fraction `0.548387`, margin `14.331758`, z-score `0.821236`
- layer `8`: raw fraction `0.548387`, margin `11.729274`, z-score `0.819453`

Artifacts:
- `summary.json`
- `layer_metrics.jsonl`
- `layer_metrics_raw.jsonl`
- `controlled_best_layer_pair_details.jsonl`
- `raw_best_layer_pair_details.jsonl`
- `directions.npz`
