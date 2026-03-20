# ABOUTME: Documents the prompt-family-matched signed bundle refresh artifact for corrective benchmark reruns.
# ABOUTME: Records selected refreshed features and the scoring proxy used for reproducibility.

# Prompt-Family-Matched Bundle Refresh (v1)

- Generated at: `2026-03-20T14:00:32-05:00`
- Stack: `google/gemma-3-270m-it` + `gemma-scope-2-270m-it-res` (layer `12`)
- Source method: `fista_dense_topk`
- Refreshed method id: `fista_dense_topk_prompt_matched_refresh_v1`
- Selection proxy: `mean_prompt_grounding_ratio - mean_repetition_rate`
- Tuning prompts: `16` total (`8` writing/diversity + `8` association/divergent)

Selected features:
- Positive: `10248`, `7405`, `3222`
- Negative: `9061`, `1307`, `11367`

Artifacts:
- `summary.json`
- `feature_tables_refreshed.json`
