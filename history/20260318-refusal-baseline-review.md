# ABOUTME: Synthesizes what the matched refusal baseline established on the Gemma 2 2B lane.
# ABOUTME: Records why the refusal result weakens creativity-specific claims and makes model-scale sensitivity the next step.

# Refusal Baseline Review

Date: 2026-03-18
Agent: codex-gpt5

## Question

Does the same Gemma 2 `2B` stack produce a clean simpler-concept dense steering success case on refusal?

## What Landed

1. Hidden-state refusal extraction

- The refusal layer sweep under `results/refusal_direction/20260318-gemma2-2b-layer-sweep-v1-mean-difference/` is extremely clean.
- Layer `15` separates all `32 / 32` refusal/compliance pairs with mean margin `101.736717` and margin z-score `7.607582`.

2. Bounded calibration

- The refusal calibration under `results/steering_eval/20260318-gemma2-2b-refusal-direction-calibration/` and the prefixed-refusal rerun under `results/steering_eval/20260318-gemma2-2b-refusal-direction-calibration-v3-prefilled-refusal/` show that clean hidden-state refusal does not automatically become clean dense output control.
- Outputs stay prompt-sensitive and often drift into noisy, partially compliant, or generally low-quality continuations.

3. Output-level gate

- The first gate under `results/steering_eval/20260318-gemma2-2b-refusal-output-gate-v1/` did not recover a usable prompt-only refusal baseline.
- The stronger prefixed-refusal gate under `results/steering_eval/20260318-gemma2-2b-refusal-output-gate-v2-prefilled-refusal/` weakly recovers the prompt-only refusal baseline:
  - prompt-only refusal vs neutral: refusal net preference `0.250000`, coherence net preference `0.000000`
  - best dense refusal vs neutral: refusal net preference `0.083333`, coherence net preference `-0.083333`
- Dense refusal steering still does not clear the gate.

## What This Means

- The refusal control is not a clean positive dense-control success case.
- It does show something important:
  - the stack can represent refusal cleanly in hidden state
  - the same stack still struggles to turn that into a robust dense output-level effect
- That weakens the strongest creativity-specific reading of the current Gemma 2 `2B` result.

## Updated Interpretation

The leading explanation is now broader `2B` stack or harness weakness for dense output-level steering, not creativity-specific failure alone.

That does not erase the creativity negative result. It changes its scope:

- stronger than before on hidden-state extraction methodology
- weaker than before as evidence that creativity is uniquely difficult on this stack

## Next Step

Run one bounded model-scale sensitivity check before reopening decomposition.

Preferred path:

- Gemma `2 9B`, if locally feasible
- same pilot-only layer/scale discipline
- at least one matched output-level gate
