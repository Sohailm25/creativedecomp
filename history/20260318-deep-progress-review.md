# Deep Progress Review

Date: 2026-03-18

## Purpose

This note is the cross-session synthesis after the first full day of implementation. Its job is to separate true progress from convenient optimism and to realign the next steps with the novelty memo, the MacBook-feasible execution path, and the prereg.

## What The Repo Has Actually Established

1. The operating scaffold is solid.
   The repo now has the `resattn`-level structure, a real runtime freeze, local paper cache, issue tracking, session logs, and regression coverage. Structural rigor is no longer the bottleneck.

2. The local execution path is real.
   `google/gemma-2-2b` plus the frozen `.venv` stack runs locally on MPS, extracts hidden states, performs pilot layer sweeps, and supports bounded steering artifacts.

3. The first contrast was invalid and was correctly rejected.
   The instruction-template path selected layer `0`, but the template-control artifact showed that result was dominated by prompt wording.

4. The response-centered `v2` redesign was a real methodological improvement.
   It removed the original extraction-wrapper confound and recovered a legitimate late-layer band, with layer `24` as the best current candidate.

5. The recovered `v2` signal is still too weak for mechanistic claims.
   Pair separation is only `19 / 32`, generation-side differences are subtle, and the bounded calibration sweep does not show a stable coefficient-response pattern.

6. The `v2` audit surfaced a real data-quality problem.
   Several strongest losses are not junk negatives; they stay as prompt-specific or more prompt-specific than the paired positives. This means the current pair construction can still make creativity look more distributed or unstable than it really is.

## Where The Repo Was Still Slightly Misaligned

1. The current `v2` pair builder is cleaner than `v1`, but it is still weaker than the source-paper path.
   Olson-style counterpart construction preserves more content between the creative and uncreative sides. Our `v2` rows are independently sampled continuations from `Creative story` and `Plain story` source prompts, which leaves more room for content drift.

2. The issue graph was one gate too permissive.
   It treated "better contrast plus internal calibration" as enough to reopen decomposition. That is weaker than the prereg and weaker than the novelty framing. A dense direction that only looks plausible in hidden-state probes is not yet the object the paper cares about.

3. The repo needed to say the real handoff to Phase 2 out loud.
   The dense direction should have to clear a bounded pilot output-level creativity gate, with a coherence/usefulness check, before any signed decomposition comparison becomes ready.

## Revised Phase Order

1. `creativedecomp-02c`
   Build an audited `v3` contrast with tighter content preservation and pair-quality rules. Prefer content-preserving creative/plain counterparts or rewrites when feasible. Rerun layer selection and bounded calibration, using response-only diagnostics if full-text probing obscures the result.

2. `creativedecomp-roq`
   Freeze the missing Phase 1 output gate. Lock a pilot-only creativity-side metric and a coherence/usefulness check, save the exact evaluation prompts or settings, and show that the dense direction changes outputs at the sequence level.

3. `creativedecomp-npt`
   Only after both gates pass should signed decomposition comparison begin.

4. Feature validation and baseline comparison
   Output-feature filtering, feature interventions, and matched refusal/sentiment baselines remain the novelty-bearing path after decomposition, not before.

## What Would Count As Meaningful Next Progress

- A `v3` pair set whose negatives are truly plain counterparts rather than merely different stories
- A late-layer direction that survives bounded calibration without obviously unstable coefficient behavior
- A pilot output-level effect that is creativity-positive and does not obviously trade coherence for formatting or verbosity

## What Would Count As An Honest Negative Result

If an audited counterpart-style `v3` contrast still fails to recover a stable late-layer direction, or if the revised direction still cannot clear the pilot output-level gate, then the project should treat that as stronger evidence that creativity is mechanistically weaker, more distributed, or less linearly steerable than simpler concepts on this stack. That is still aligned with the original novelty framing.
