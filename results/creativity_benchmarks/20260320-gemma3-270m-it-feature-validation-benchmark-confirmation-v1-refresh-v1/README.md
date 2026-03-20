# ABOUTME: Summarizes two-family bundle-vs-dense confirmation after prompt-family-matched bundle refresh.
# ABOUTME: Marks claim boundary status and reports per-family net wins under the locked rerun protocol.

# Feature Validation Benchmark-Family Confirmation (v1, prompt-matched refresh)

- Generated at: `2026-03-20T14:16:46-05:00`
- Stack: `google/gemma-3-270m-it` + `gemma-scope-2-270m-it-res` (layer `12`)
- Refreshed feature method: `fista_dense_topk_prompt_matched_refresh_v1`
- Steering coefficient: `1.0`
- Families: association/divergent + writing/diversity (`10` audited bundle-vs-dense pairs each)
- Audit lock mode: deterministic heuristic lock (`prompt grounding - repetition`), pending independent human rerating

Outcome:
- Prereg two-family confirmation gate: `not met`
- Association/divergent net wins (`bundle - dense`):
  - prompt-grounded creativity: `-0.300`
  - coherence: `-0.500`
- Writing/diversity net wins (`bundle - dense`):
  - prompt-grounded creativity: `0.100`
  - coherence: `0.200`

Interpretation:
- Prompt-family-matched refresh improves transfer on writing/diversity but remains strongly negative on association/divergent, so cross-family generalization is still not confirmed.

Artifacts:
- `summary.json`
