# ABOUTME: Reviews the cached manual audit on the instruction-tuned refusal gate after the automatic judge collapsed to ties.
# ABOUTME: Records why the repo must revise the negative-result framing without overclaiming a matched creativity control.

# Instruction-Tuned Refusal Manual Audit Review

Date: 2026-03-19
Agent: codex-gpt5

## Question

Did the locked manual audit on the cached instruction-tuned refusal outputs confirm the automatic all-tie interpretation, or did it reveal that the local judge had been underestimating a real output-side refusal effect?

## What The Manual Audit Established

1. The prompt-only refusal baseline is real on the instruction-tuned stack.

- The blinded cached-output audit at `results/steering_eval/20260319-gemma3-270m-it-refusal-output-gate-v1-manual-audit/` scores all `12 / 12` prompt-only refusal-versus-neutral comparisons in favor of the refusal prompt on the refusal axis.
- The same prompt-only baseline also wins coherence `7 / 12` times, loses `4 / 12`, and ties once.

2. Dense instruction-tuned refusal steering is not dead on this lane.

- Dense coeff `0.5` wins refusal `7 / 12` times versus neutral, loses `3 / 12`, and ties `2 / 12`, with coherence split evenly `6 / 6`.
- Dense coeff `1.0` wins refusal `6 / 12` times versus neutral, loses `4 / 12`, and ties `2 / 12`, while also winning coherence `9 / 12` times.

3. The old automatic all-tie read was too harsh.

- The automatic gate artifact at `results/steering_eval/20260318-gemma3-270m-it-refusal-output-gate-v1/` is still a real result, but its judge was not sensitive enough to the qualitative refusal differences on this slice.
- The manual audit is therefore a claim-boundary correction, not an optional side note.

## What This Still Does Not Establish

- Not that the active creativity lane has a matched simpler-concept control.
- Not that creativity is mechanistically different from refusal.
- Not that decomposition should reopen now.
- Not that more steering-regime shopping is justified.

The recovered output-side refusal effect lives on `google/gemma-3-270m-it` plus `gemma-scope-2-270m-it-res`, which is an unmatched instruction-tuned stack relative to the active creativity pipeline.

## Decision

Do not freeze the write-up-grade negative-result bundle from the pre-audit interpretation.

The corrected repo truth is narrower:

- the instruction-tuned refusal lane now provides the first local simpler-concept output-side steering success case
- that success is modest rather than dominant
- it is still not a matched control for the active creativity lane

The next honest move is synthesis: choose one matched continuation for the active creativity question before any new implementation or decomposition work resumes.
