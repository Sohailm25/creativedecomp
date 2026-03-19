# ABOUTME: Records what the bounded Gemma 2 9B refusal sensitivity check established after the 2B refusal control stayed output-weak.
# ABOUTME: Explains why the 9B result sharpens the interpretation without reopening decomposition.

# Gemma 2 9B Model-Scale Sensitivity Review

Date: 2026-03-18
Agent: codex-gpt5

## Question

Does a bounded scale-up from Gemma 2 `2B` to Gemma 2 `9B` rescue a clean dense output-level simpler-concept control on the same local stack?

## What Landed

1. Local feasibility

- Gemma 2 `9B` loaded successfully on the MacBook lane in float32 on `mps`.
- Hidden-state extraction is therefore a real local lane, not a hypothetical extension.

2. Hidden-state refusal extraction

- The 9B refusal layer sweep under `results/refusal_direction/20260318-gemma2-9b-layer-sweep-v1-mean-difference/` is extremely clean.
- Layer `18` separates all `32 / 32` refusal/compliance pairs with mean margin `99.187210`, margin z-score `8.339555`, and zero template-control signal.

3. Output-level gate

- The bounded 9B refusal output gate under `results/steering_eval/20260318-gemma2-9b-refusal-output-gate-v1-bounded/` still fails.
- Prompt-only refusal versus neutral is only weakly positive on refusal quality and slightly negative on coherence:
  - refusal net preference `0.083333`
  - coherence net preference `-0.083333`
- Dense refusal steering at layer `18`, coeff `0.5` is worse than neutral on refusal quality:
  - refusal net preference `-0.083333`
  - coherence net preference `0.083333`

## Important Constraint

- A broad 9B sampled calibration grid was not a sane MacBook pilot step.
- Live process sampling showed generation spending most of its time in synchronous MPS `multinomial` and copy waits.
- That is a real local throughput constraint, not a software bug we fixed.
- The bounded gate is therefore the claim-bearing 9B output artifact, not the aborted full calibration grid.

## What This Means

- Scaling from Gemma 2 `2B` to Gemma 2 `9B` helps hidden-state simpler-concept extraction.
- It does not rescue dense output-level refusal steering on this stack.
- That weakens the "maybe 2B is just too small" story.
- It also means the main blocker is now broader than creativity alone: base-model dense steering plus sampled decoding looks weak across both sizes on this local lane.

## Consequence For The Main Experiment

- Decomposition does not reopen.
- The next honest step is synthesis, not feature work.
- We now need to decide whether the right continuation is:
  - a write-up-grade negative result on dense base-model steering
  - a bounded instruction-tuned or alternate-method control lane
  - or a stop on this steering path before decomposition
