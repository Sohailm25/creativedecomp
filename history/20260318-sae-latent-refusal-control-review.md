# ABOUTME: Records what the bounded sparse SAE-latent refusal control established on the local Gemma 2 2B stack.
# ABOUTME: Explains why the next honest choice is now between a write-up-grade negative result and a bounded instruction-tuned pivot.

# SAE-Latent Refusal Control Review

Date: 2026-03-18
Agent: codex-gpt5

## Question

Does a bounded sparse SAE-latent refusal control rescue the output-level simpler-concept gate after dense refusal steering failed on Gemma 2 `2B` and Gemma 2 `9B`?

## What Landed

1. A matched alternate-method artifact now exists.

- Artifact: `results/steering_eval/20260318-gemma2-2b-refusal-sae-latent-output-gate-v1/`
- Model: `google/gemma-2-2b`
- SAE: `gemma-scope-2b-pt-res-canonical`, `layer_15/width_16k/canonical`
- Sparse control: top-`32` signed refusal features from the pilot refusal/compliance slice

2. The sparse control still does not clear the gate.

- Best sparse condition: `neutral_sae_latent_layer15_coeff_1p0`
- Versus neutral:
  - refusal net preference `0.000000`
  - coherence net preference `-0.166667`
- The weaker coeff `0.5` is worse on refusal:
  - refusal net preference `-0.166667`
  - coherence net preference `0.083333`

3. The prompt-only refusal baseline inside the same run also stays weak.

- Prompt-only refusal versus neutral is all refusal ties and slightly worse on coherence:
  - refusal net preference `0.000000`
  - coherence net preference `-0.083333`

## What This Means

- The local refusal failure is no longer just a dense-vector problem.
- On this MacBook base-model lane, the simpler-concept control has now stayed output-weak across:
  - dense refusal steering on Gemma 2 `2B`
  - dense refusal steering on Gemma 2 `9B`
  - sparse SAE-latent refusal steering on Gemma 2 `2B`
- That makes decomposition even less honest to reopen on the current base-model path.

## What It Does Not Mean

- It does not prove that refusal or creativity are unsteerable in general.
- It does not prove that SAE methods fail in general.
- It does mean that this local base-model steering lane has not produced a clean output-level control success case even after one bounded alternate-method check.

## Consequence For The Main Experiment

- `creativedecomp-npt` stays blocked.
- The next honest choice is now strategic, not local implementation:
  - stop on a write-up-grade negative result for the current local lane
  - or run one bounded instruction-tuned pivot before settling that conclusion
