# Creativity Direction Layer Sweep

- Generated at: `2026-03-18T11:39:32-05:00`
- Model: `google/gemma-2-2b`
- Device: `mps`
- Candidate layers: `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]`
- Pair count: `32`
- Raw ranking rule: `positive_gt_negative_fraction, margin_zscore, mean_margin`
- Controlled ranking rule: `controlled_fraction_delta, controlled_margin_zscore_delta, abs(template_direction_cosine), positive_gt_negative_fraction`
- Raw best layer: `0`
- Controlled best layer: `None`

Top controlled layers:
- Controlled winner status: no layer cleared the template-control threshold (positive fraction delta and positive margin-zscore delta).

- layer `0`: raw fraction `1.000000`, template fraction `1.000000`, delta `0.000000`, cosine `0.375621`
- layer `7`: raw fraction `0.906250`, template fraction `1.000000`, delta `-0.093750`, cosine `0.070423`
- layer `10`: raw fraction `0.781250`, template fraction `0.968750`, delta `-0.187500`, cosine `0.012104`
- layer `12`: raw fraction `0.718750`, template fraction `0.937500`, delta `-0.218750`, cosine `-0.073446`
- layer `9`: raw fraction `0.750000`, template fraction `1.000000`, delta `-0.250000`, cosine `0.023789`

Top raw layers:
- layer `0`: raw fraction `1.000000`, margin `0.704925`, z-score `0.932329`
- layer `7`: raw fraction `0.906250`, margin `0.897024`, z-score `0.519957`
- layer `10`: raw fraction `0.781250`, margin `1.653073`, z-score `0.465009`
- layer `25`: raw fraction `0.750000`, margin `4.445136`, z-score `0.597613`
- layer `15`: raw fraction `0.750000`, margin `3.584769`, z-score `0.531641`

Artifacts:
- `summary.json`
- `layer_metrics.jsonl`
- `layer_metrics_raw.jsonl`
- `raw_best_layer_pair_details.jsonl`
- `directions.npz`
