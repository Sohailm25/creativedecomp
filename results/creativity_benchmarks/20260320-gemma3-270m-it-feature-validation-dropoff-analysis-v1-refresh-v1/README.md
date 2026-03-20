# ABOUTME: Diagnoses refreshed-bundle benchmark-family behavior at coeffs 1.0 and 0.5.
# ABOUTME: Captures whether remaining failures are family-specific transfer issues or global scale mismatch.

# Feature Validation Dropoff Analysis (v1, prompt-matched refresh)

- Generated at: `2026-03-20T14:16:46-05:00`
- Baseline coefficient: `1.0`
- Low coefficient sensitivity: `0.5`
- Refreshed feature method: `fista_dense_topk_prompt_matched_refresh_v1`
- Audit lock mode: deterministic heuristic lock (`prompt grounding - repetition`), pending independent human rerating

Root-cause summary:
- Families analyzed: `2`
- Creativity dropoff families (`bundle < dense`): `1`
- Coherence dropoff families (`bundle < dense`): `1`
- Lower prompt-grounding families (`bundle < dense`): `1`
- Higher repetition families (`bundle > dense`): `1`

Per-family read:
- Writing/diversity (`coeff=1.0`): bundle beats dense on both axes (creativity net `+0.100`, coherence net `+0.200`) with slightly lower grounding but lower repetition.
- Association/divergent (`coeff=1.0`): bundle stays below dense on both axes (creativity net `-0.300`, coherence net `-0.500`) with higher grounding but higher repetition.
- Coeff `0.5` shift: association/divergent improves (`+0.200` creativity and coherence net deltas) while writing/diversity worsens (`-0.300` creativity and `-0.200` coherence net deltas).

Interpretation:
- Prompt-matched refresh removes all-family failure but still does not give robust two-family transfer. The residual problem remains family-heterogeneous rather than a single global coefficient bug.

Artifacts:
- `summary.json`
