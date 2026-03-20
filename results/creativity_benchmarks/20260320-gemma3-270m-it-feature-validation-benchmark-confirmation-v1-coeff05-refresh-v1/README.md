# ABOUTME: Summarizes low-coefficient two-family confirmation after prompt-matched feature-bundle refresh.
# ABOUTME: Records whether coeff reduction rescues bundle-vs-dense transfer under the same refreshed bundle.

# Feature Validation Benchmark-Family Confirmation (v1, coeff 0.5, prompt-matched refresh)

- Generated at: `2026-03-20T14:16:46-05:00`
- Steering coefficient: `0.5`
- Refreshed feature method: `fista_dense_topk_prompt_matched_refresh_v1`
- Families: association/divergent + writing/diversity (`10` audited bundle-vs-dense pairs each)
- Audit lock mode: deterministic heuristic lock (`prompt grounding - repetition`), pending independent human rerating

Outcome:
- Prereg two-family confirmation gate: `not met`
- Association/divergent net wins (`bundle - dense`):
  - prompt-grounded creativity: `-0.100`
  - coherence: `-0.300`
- Writing/diversity net wins (`bundle - dense`):
  - prompt-grounded creativity: `-0.200`
  - coherence: `0.000`

Interpretation:
- Lowering coefficient from `1.0` to `0.5` partially improves association/divergent but flips writing/diversity negative, so coefficient-only adjustment still does not produce a consistent two-family recovery.

Artifacts:
- `summary.json`
