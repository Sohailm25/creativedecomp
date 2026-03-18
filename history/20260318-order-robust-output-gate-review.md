# Order-Robust Output Gate Review

Date: 2026-03-18

## Purpose

This note records the secondary review of the pilot output-level gate on the recovered full-text `mean_difference` creativity direction.

The key question was not just whether the gate passed, but whether the gate metric itself was trustworthy enough to support a Phase 1 decision.

## What Happened

The first pilot output-gate artifact on layer `23` with coeffs `0.5` and `1.0` looked weakly positive.

But a secondary review of the saved pairwise judgments showed that the local creativity judge chose story `A` on `152 / 155` creativity comparisons. That made the first automatic pass signal an order artifact rather than evidence.

## Corrective Action

The gate was patched to use order-robust paired judging:

- evaluate each pair in both A/B orders
- only count a winner if the same condition wins in both orders
- collapse all inconsistent pairs to `tie`

The rerun reused the saved `generated_outputs.jsonl` so the correction only redid judging, not story generation.

## Corrected Result

The corrected order-robust artifact under `results/steering_eval/20260318-gemma2-2b-output-gate-v1/` does not pass the gate.

Main result:

- prompt-only creativity versus neutral: `31 / 31` ties on creativity and `31 / 31` ties on coherence
- dense `0.5` versus neutral: `31 / 31` ties on creativity and `31 / 31` ties on coherence
- dense `1.0` versus neutral: `31 / 31` ties on creativity and `31 / 31` ties on coherence

Only remaining non-tie comparison:

- dense `0.5` versus prompt-only baseline: dense wins `2 / 31` creativity comparisons, loses `1 / 31`, and loses `1 / 31` coherence comparisons

Condition-level heuristics stay clean on prompt-meta contamination, but they are small:

- dense `1.0` is slightly longer and more repetitive than neutral
- dense `0.5` is only slightly more lexically diverse than neutral

## Research Alignment Read

This result is more aligned with the prereg and paper grounding than the earlier positive-looking artifact.

Why:

- the prereg requires a bounded output-level effect before decomposition opens
- the corrected artifact does not establish that effect
- the review also confirms the documented risk that judge brittleness is a first-class threat in this experiment

Important nuance:

This is not yet a clean negative result for the MacBook lane, because the same corrected local metric also fails to distinguish the prompt-only creativity baseline from neutral. That means the current pilot creativity-side metric is too insensitive to settle whether the dense direction is behaviorally absent or merely under-measured.

## Conclusion

1. The single-order output-gate pass is invalid and should not be cited.
2. The corrected order-robust output gate does not pass.
3. Decomposition must remain blocked.
4. The next honest step is a bounded follow-up that strengthens the pilot creativity-side metric without reintroducing order bias.

That is now tracked by `creativedecomp-8o1`.
