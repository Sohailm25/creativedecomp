# Creativity Direction Layer Sweep

- Generated at: `2026-03-18T14:49:39-05:00`
- Model: `google/gemma-2-2b`
- Device: `mps`
- Direction method: `mean_difference`
- Candidate layers: `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]`
- Pair count: `31`
- Raw ranking rule: `positive_gt_negative_fraction, margin_zscore, mean_margin`
- Controlled ranking rule: `controlled_fraction_delta, controlled_margin_zscore_delta, abs(template_direction_cosine), positive_gt_negative_fraction`
- Raw best layer: `23`
- Controlled best layer: `23`

Top controlled layers:
- Controlled best raw fraction: `0.580645`
- Controlled best template-control fraction: `0.000000`
- Controlled best fraction delta: `0.580645`
- Controlled best cosine: `0.000000`

- layer `23`: raw fraction `0.580645`, template fraction `0.000000`, delta `0.580645`, cosine `0.000000`
- layer `10`: raw fraction `0.580645`, template fraction `0.000000`, delta `0.580645`, cosine `0.000000`
- layer `13`: raw fraction `0.580645`, template fraction `0.000000`, delta `0.580645`, cosine `0.000000`
- layer `11`: raw fraction `0.580645`, template fraction `0.000000`, delta `0.580645`, cosine `0.000000`
- layer `22`: raw fraction `0.548387`, template fraction `0.000000`, delta `0.548387`, cosine `0.000000`

Top raw layers:
- layer `23`: raw fraction `0.580645`, margin `58.126850`, z-score `0.829265`
- layer `10`: raw fraction `0.580645`, margin `14.042850`, z-score `0.802422`
- layer `13`: raw fraction `0.580645`, margin `18.282431`, z-score `0.801434`
- layer `11`: raw fraction `0.580645`, margin `15.490515`, z-score `0.744299`
- layer `22`: raw fraction `0.548387`, margin `52.112438`, z-score `0.841149`

Artifacts:
- `summary.json`
- `layer_metrics.jsonl`
- `layer_metrics_raw.jsonl`
- `controlled_best_layer_pair_details.jsonl`
- `raw_best_layer_pair_details.jsonl`
- `directions.npz`
