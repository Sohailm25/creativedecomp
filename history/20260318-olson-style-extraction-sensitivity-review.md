# Olson-Style Extraction Sensitivity Review

Date: 2026-03-18

## Purpose

This note records the bounded Phase 1 sensitivity requested after the `v3` counterpart rewrite landed. The question was narrow: does the failed `v3` PCA result mean the MacBook lane is genuinely negative, or was the repo still mismatched to Olson's extraction method?

## Compared Conditions

Same landed `v3` slice, same model, same prompt split, same evaluation path.

Changed variable:

- current path: PCA-on-pair-differences
- Olson-style sensitivity: `mean_difference`

Views compared:

- full-text `Prompt + Story`
- response-only `Story`

## Main Result

The extraction-method mismatch was real.

### Full-text view

PCA:
- no controlled winner
- raw best layer `6`
- positive-greater-than-negative fraction `0.354839`
- mean margin `-0.268858`

`mean_difference`:
- controlled winner recovered at layer `23`
- positive-greater-than-negative fraction `0.580645`
- mean margin `58.126850`
- margin z-score `0.829265`

### Response-only view

PCA:
- no controlled winner
- raw best layer `22`
- positive-greater-than-negative fraction `0.387097`
- mean margin `-4.458102`

`mean_difference`:
- controlled winner recovered at layer `9`
- positive-greater-than-negative fraction `0.548387`
- mean margin `13.131884`
- margin z-score `0.828694`

## Calibration Readout

The recovered full-text `mean_difference` direction is substantially cleaner than the failed PCA candidate.

Primary read:

- layer `23` moves from `15.270608` unsteered
- to `26.416735` at coeff `0.5`
- to `34.472979` at coeff `1.0`
- then overshoots to `-7.573171` at coeff `2.0`

Interpretation:

- there appears to be a bounded usable steering regime around `0.5` to `1.0`
- the path is not open-ended, but it is no longer obviously unstable in the same way as PCA

The response-only `mean_difference` path improves over PCA but remains weaker:

- layer `9` moves from `-5.527642` to `-2.083943` at coeff `0.5`
- then slips to `-9.066536` at coeff `1.0`

That is useful support, but not as strong as the full-text path.

## Research Alignment Review

### Olson

This was the key mismatch. Once the repo kept the same counterpart-style `v3` slice and changed only the extraction method, the direction recovered. That is strong evidence that the earlier negative result was not yet the right stack-level conclusion.

### Von Rütte

The repo should still stay cautious. Recovery at the sweep and probe level is not the same thing as a proven output-level creativity effect. The next correct task is still the pilot output gate, not decomposition.

### Experiment docs

The result is aligned with the project docs:

- contrast construction is now good enough for Phase 1
- decomposition remains blocked
- the output-level gate is now the correct next step

## Conclusion

The bounded Olson-style sensitivity succeeded.

It does not prove the full experiment yet, but it does change the phase order honestly:

1. `creativedecomp-173` can close.
2. `creativedecomp-roq` becomes the next ready task.
3. The primary Phase 1 dense-direction candidate is the full-text `mean_difference` path at layer `23`, with coeffs in the `0.5` to `1.0` band.
4. The response-only `mean_difference` path should remain a diagnostic support lane rather than the main claim path.
