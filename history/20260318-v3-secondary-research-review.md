# V3 Secondary Research Review

Date: 2026-03-18

## Purpose

This note records the promised second-pass research review after the `v3` counterpart contrast landed. Its job is to answer a narrow question: after the stronger `v3` contrast, are we still aligned with the experiment documents and the cited papers, and what is the next honest move?

## What Landed

- `v3` replaced independently sampled negative continuations with plain counterpart rewrites of the same story material.
- `31 / 32` rows passed the quality filter.
- Mean counterpart overlap is `0.913658`.
- Mean prompt-grounding delta is `0.002251`.
- The full-text sweep does not recover a usable dense creativity direction.
- The response-only sweep changes the raw best layer but does not recover a usable dense creativity direction either.
- Both calibration branches remain non-monotone.

## Alignment Check Against The Research Docs

### `research/experiment-novelty.md`

Aligned:
- The repo now treats content-preserving counterparts as the preferred contrast object, which matches the strongest Olson-style framing in the novelty memo.
- The repo still blocks decomposition until Phase 1 is honest.
- The repo still treats a negative result as publishable if it survives bounded checks.

Still incomplete:
- Olson's strongest path is not just better pairs. It is also a higher-quality counterpart construction regime and a mean-difference or CAA-style direction extraction. We have now reduced the pair-quality mismatch substantially, but we have not yet run the extraction-method sensitivity.

### `research/experiment-macbook-guide.md`

Aligned:
- The work stayed on the MacBook-feasible stack.
- The work used bounded pilot artifacts and did not jump prematurely to larger infrastructure or the extension lanes.

Tension:
- The negative result is now more credible, but it still should not be treated as the final answer for the MacBook lane until the last major methodological mismatch is checked in a bounded way.

### `research/transcript.md` and `research/experiment-ideas.md`

Aligned:
- The project is still executing the narrow mechanistic experiment rather than drifting into controller-style or basin-style creative navigation.
- The work is still focused on discovering whether creativity behaves differently from simpler concepts at the mechanistic level.

## Alignment Check Against The Papers

### Olson

`v3` is materially closer to the paper path because the negative side is now a counterpart rewrite of the same story material. But the current implementation still differs on one important axis: the extraction method. The next honest sensitivity is to compare our current PCA-on-pair-differences extraction against an Olson-style mean-difference or CAA direction on the landed `v3` slice.

### Von Rütte

The current result is consistent with the warning that creativity-like concepts can be detectable yet hard to guide. Even after improving the contrast object, the dense direction remains unstable and view-dependent.

### AxBench and CREATE

The repo remains aligned with the requirement not to confuse internal movement with meaningful creativity effects. Nothing in the landed `v3` artifacts justifies opening the pilot output gate yet.

## Objective Reading Of Progress

`v3` is not a failure. It did exactly what the research review said it needed to do:

- it reduced the pair-quality ambiguity
- it made the negative result harder to dismiss as simple content drift

But it also did not recover the dense direction. That means the experiment is now in a more informative state:

- pair construction is better
- direction extraction is still weak
- calibration is still unstable

## Next Honest Step

Run one bounded Olson-style extraction sensitivity on the landed `v3` counterpart slice:

1. Compare the current PCA-on-pair-differences direction against a mean-difference or CAA extraction.
2. Keep the comparison on the same `v3` slice so the only major variable is the extraction method.
3. Allow a tiny hand-audited subset only if the automatic counterpart rewrites still look qualitatively too weak.

If that bounded sensitivity also fails, the repo should treat the result as the first serious negative result for the Gemma 2 2B MacBook lane instead of quietly searching for another excuse to proceed.
