# Feature Validation Benchmark-Family Confirmation (v1)

- Generated at: `2026-03-20T11:39:24-05:00`
- Stack: `google/gemma-3-270m-it` + `gemma-scope-2-270m-it-res` (layer `12`)
- Prompt families:
  - `Association / Divergent (CREATE-style)`: `prompts/create_style_association_v1.jsonl`
  - `Writing / Diversity (WritingPrompts-style)`: `prompts/creative_direction_v1_confirm.jsonl` (first `10` prompts)
- Conditions generated per family: `dense_direction`, `positive_feature_3222`, `negative_feature_16008`, `bundle_feature_group`
- Locked audit comparison for confirmation: `bundle_feature_group` vs `dense_direction`
- Sample size: `10` audited pairs per family (`20` total, beyond the `18`-pair pilot slice)

Outcome:
- Prereg two-family benchmark confirmation gate: `not met`
- Association/divergent family net wins (`bundle - dense`):
  - prompt-grounded creativity: `-0.200`
  - coherence: `-0.100`
- Writing/diversity family net wins (`bundle - dense`):
  - prompt-grounded creativity: `-0.300`
  - coherence: `0.000`

Claim boundary:
- `benchmark_family_confirmation_not_met`
- The earlier pilot-slice bundle-over-dense signal does not yet generalize on this first two-family benchmark confirmation pass.

Artifacts:
- `summary.json`
- `../20260320-gemma3-270m-it-feature-validation-benchmark-association-v1/`
- `../20260320-gemma3-270m-it-feature-validation-benchmark-association-v1-manual-audit/`
- `../20260320-gemma3-270m-it-feature-validation-benchmark-writing-v1/`
- `../20260320-gemma3-270m-it-feature-validation-benchmark-writing-v1-manual-audit/`
