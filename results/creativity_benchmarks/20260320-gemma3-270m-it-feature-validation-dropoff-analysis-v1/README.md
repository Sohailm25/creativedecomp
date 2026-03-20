# Feature Validation Dropoff Analysis (v1)

- Generated at: `2026-03-20T13:24:03-05:00`
- Scope: bounded root-cause diagnosis for `creativedecomp-e4p`
- Inputs:
  - baseline two-family benchmark confirmation (`coeff=1.0`)
  - bounded sensitivity rerun (`coeff=0.5`) with locked bundle-vs-dense audits

## Root-Cause Signals

- Bundle under dense on prompt-grounded creativity in both families at baseline.
- Bundle has lower prompt-grounding ratio than dense in both families.
- Bundle has slightly higher repetition rate than dense in both families.
- Coefficient sensitivity does not cleanly rescue the pattern:
  - Writing/diversity improves slightly at `0.5` (`-0.3` to `-0.2` creativity net win) but remains negative.
  - Association/divergent worsens at `0.5` (`-0.2` to `-0.3` creativity net win; coherence also drops).

## Interpretation

- The dropoff is unlikely to be primarily a single global coefficient mismatch.
- The stronger signal points to feature-selection and prompt-family transfer issues:
  - the frozen pilot bundle appears under-grounded outside the pilot slice
  - mild repetition increases suggest style drift without creativity gains

## Minimum Corrective Experiment

Run one prompt-family-matched feature-selection refresh and re-audit bundle-vs-dense under the same locked rubric:

1. Re-select a compact signed bundle using only a held-out benchmark-family tuning subset.
2. Keep the same model, layer, SAE release, and evaluation packet structure.
3. Run one bounded coeff sweep (`0.5`, `1.0`) and lock manual audits before deciding on any claim upgrade.

## Artifacts

- `summary.json`
