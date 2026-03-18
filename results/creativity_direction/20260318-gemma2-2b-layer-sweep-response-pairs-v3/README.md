# Creativity Direction Layer Sweep

- Generated at: `2026-03-18T14:25:39-05:00`
- Model: `google/gemma-2-2b`
- Device: `mps`
- Candidate layers: `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]`
- Pair count: `31`
- Raw ranking rule: `positive_gt_negative_fraction, margin_zscore, mean_margin`
- Controlled ranking rule: `controlled_fraction_delta, controlled_margin_zscore_delta, abs(template_direction_cosine), positive_gt_negative_fraction`
- Raw best layer: `6`
- Controlled best layer: `None`

Top controlled layers:
- Controlled winner status: no layer cleared the template-control threshold (positive fraction delta and positive margin-zscore delta).

- layer `6`: raw fraction `0.354839`, template fraction `0.000000`, delta `0.354839`, cosine `0.000000`
- layer `8`: raw fraction `0.354839`, template fraction `0.000000`, delta `0.354839`, cosine `0.000000`
- layer `9`: raw fraction `0.354839`, template fraction `0.000000`, delta `0.354839`, cosine `0.000000`
- layer `22`: raw fraction `0.354839`, template fraction `0.000000`, delta `0.354839`, cosine `0.000000`
- layer `11`: raw fraction `0.354839`, template fraction `0.000000`, delta `0.354839`, cosine `0.000000`

Top raw layers:
- layer `6`: raw fraction `0.354839`, margin `-0.268858`, z-score `-0.010884`
- layer `8`: raw fraction `0.354839`, margin `-1.147804`, z-score `-0.038082`
- layer `9`: raw fraction `0.354839`, margin `-1.741356`, z-score `-0.049187`
- layer `22`: raw fraction `0.354839`, margin `-8.120711`, z-score `-0.072293`
- layer `11`: raw fraction `0.354839`, margin `-3.843065`, z-score `-0.083740`

Artifacts:
- `summary.json`
- `layer_metrics.jsonl`
- `layer_metrics_raw.jsonl`
- `raw_best_layer_pair_details.jsonl`
- `directions.npz`
