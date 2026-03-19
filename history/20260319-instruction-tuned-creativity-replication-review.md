# ABOUTME: Reviews the bounded instruction-tuned creativity replication after the matched-stack manual audit lands.
# ABOUTME: Captures what the corrected harness and cached-output audit do and do not establish before Phase 2 is reconsidered.

# Instruction-Tuned Creativity Replication Review

## Question

After the instruction-tuned refusal manual audit recovered a real simpler-concept effect on `google/gemma-3-270m-it`, does the matched creativity-side continuation on that same stack recover any bounded output-side effect, or does the regime-matched comparison still support the older "creativity is uniquely harder" story?

## Artifacts Reviewed

- `results/creativity_direction/20260319-gemma3-270m-it-response-pairs-v1-pilot/`
- `results/creativity_direction/20260319-gemma3-270m-it-layer-sweep-v1-mean-difference/`
- `results/steering_eval/20260319-gemma3-270m-it-output-gate-v1/`
- `results/steering_eval/20260319-gemma3-270m-it-output-gate-v1-manual-audit/`

## What Changed

- The first instruction-tuned creativity attempt copied the refusal pivot's bare neutral prompt too literally. On a chat model, that was a malformed neutral condition because it often failed to request a story at all.
- Replacing the bare neutral prompt with a neutral story-writing prompt materially improved the contrast quality and the cached generations. Accepted counterpart rows rose from `6 / 32` to `18 / 32`, and the gate conditions all became story-like enough to compare.
- The automatic judge still failed. It hard-selected story `A` under both A/B orderings, so the order-robust scorer turned every comparison into a tie.

## Main Findings

- The corrected pair builder is usable enough for a bounded matched-stack Phase 1 read. It accepts `18 / 32` rows with mean counterpart overlap `0.506`.
- The corrected mean-difference sweep recovers layer `12` as the best hidden-state creativity layer on this instruction-tuned stack.
- The automatic output gate is not claim-bearing on this lane because the local judge remains order-biased even after the generation harness is fixed.
- The cached manual audit changes the conclusion. Prompt-only creativity versus neutral is roughly tied on prompt-grounded creativity (`0.416667` vs `0.416667`), but dense layer `12`, coeff `1.0`, beats neutral on both prompt-grounded creativity (`0.583333` vs `0.083333`) and coherence (`0.916667` vs `0.083333`). Dense coeff `0.5` does not.

## Interpretation

- The old unmatched-stack objection is gone. Creativity now has a manual-audit-supported dense output-side effect on the same instruction-tuned stack where refusal also has one.
- The strongest old "creativity is uniquely harder than simpler concepts" story is not supported on this matched instruction-tuned stack.
- This is not yet a clean "decomposition now" signal by itself. The prompt-only creativity baseline does not clearly beat neutral, and the automatic judge is still unusable, so the correct next move is a synthesis step that decides whether the repo should pivot Phase 2 onto this stack or require one narrower confirmatory follow-up first.

## Next Step

Run `creativedecomp-182`: synthesize the matched instruction-tuned creativity and refusal results and decide whether Phase 2 decomposition should temporarily pivot onto `google/gemma-3-270m-it` plus `gemma-scope-2-270m-it-res`.
