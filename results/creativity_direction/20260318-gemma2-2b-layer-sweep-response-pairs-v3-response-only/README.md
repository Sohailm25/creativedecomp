# Creativity Direction Layer Sweep

- Generated at: `2026-03-18T14:26:29-05:00`
- Model: `google/gemma-2-2b`
- Device: `mps`
- Candidate layers: `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]`
- Pair count: `31`
- Raw ranking rule: `positive_gt_negative_fraction, margin_zscore, mean_margin`
- Controlled ranking rule: `controlled_fraction_delta, controlled_margin_zscore_delta, abs(template_direction_cosine), positive_gt_negative_fraction`
- Raw best layer: `22`
- Controlled best layer: `None`

Top controlled layers:
- Controlled winner status: no layer cleared the template-control threshold (positive fraction delta and positive margin-zscore delta).

- layer `22`: raw fraction `0.387097`, template fraction `0.000000`, delta `0.387097`, cosine `0.000000`
- layer `0`: raw fraction `0.354839`, template fraction `0.000000`, delta `0.354839`, cosine `0.000000`
- layer `9`: raw fraction `0.354839`, template fraction `0.000000`, delta `0.354839`, cosine `0.000000`
- layer `5`: raw fraction `0.354839`, template fraction `0.000000`, delta `0.354839`, cosine `0.000000`
- layer `8`: raw fraction `0.354839`, template fraction `0.000000`, delta `0.354839`, cosine `0.000000`

Top raw layers:
- layer `22`: raw fraction `0.387097`, margin `-4.458102`, z-score `-0.039457`
- layer `0`: raw fraction `0.354839`, margin `1.243626`, z-score `0.056874`
- layer `9`: raw fraction `0.354839`, margin `-1.077213`, z-score `-0.031657`
- layer `5`: raw fraction `0.354839`, margin `-0.792916`, z-score `-0.033630`
- layer `8`: raw fraction `0.354839`, margin `-1.378834`, z-score `-0.046044`

Artifacts:
- `summary.json`
- `layer_metrics.jsonl`
- `layer_metrics_raw.jsonl`
- `raw_best_layer_pair_details.jsonl`
- `directions.npz`
