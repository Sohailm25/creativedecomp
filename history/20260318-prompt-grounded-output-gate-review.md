# ABOUTME: Records the cached-output manual audit and prompt-grounded-creativity rerun that resolved the output-metric ambiguity.
# ABOUTME: Captures why Gemma 2 2B is now treated as the first strong Phase 1 negative-result lane.

# Prompt-Grounded Output Gate Review

Date: 2026-03-18
Agent: codex-gpt5

## Purpose

This note records the `creativedecomp-8o1` follow-up after the order-robust output-gate collapse.

The follow-up had one job: use the same cached generated stories to determine whether the lack of dense output effect was still an evaluation ambiguity or had become a real bounded negative result for the Gemma 2 2B lane.

## What Was Done

1. Built a blinded manual-audit packet from the cached prompt-only versus neutral stories in `results/steering_eval/20260318-gemma2-2b-output-gate-v1/`.
2. Scored a fixed `12`-prompt sample under a locked rubric with two axes:
   - prompt-grounded creativity
   - coherence
3. Used that audit plus the evaluation papers to replace the vague creativity judge with a tighter prompt-grounded-creativity judge.
4. Reran the output gate on the same cached stories, with the same order-robust judging rule, under the new metric.

## Manual Audit Result

The blinded `12`-pair audit under `results/steering_eval/20260318-gemma2-2b-output-gate-v1-manual-audit/` showed:

- prompt-only versus neutral on prompt-grounded creativity:
  - prompt-only win fraction `0.500`
  - neutral win fraction `0.417`
  - tie fraction `0.083`
- prompt-only versus neutral on coherence:
  - prompt-only win fraction `0.583`
  - neutral win fraction `0.333`
  - tie fraction `0.083`

This did not show a dramatic prompt-only advantage. It did show enough of one to justify a stricter automated metric focused on prompt fit, specificity, and meaningful novelty rather than generic "creative vibe."

## Prompt-Grounded Rerun Result

The stricter rerun under `results/steering_eval/20260318-gemma2-2b-output-gate-v2-prompt-grounded-creativity/` weakly recovers the prompt-only baseline on the full `31`-prompt slice:

- prompt-only versus neutral:
  - creativity candidate win fraction `0.064516`
  - creativity reference win fraction `0.000000`
  - creativity tie fraction `0.935484`
  - coherence remains all ties

But the rerun still shows no dense effect versus neutral:

- dense `0.5` versus neutral:
  - creativity `31 / 31` ties
  - coherence `31 / 31` ties
- dense `1.0` versus neutral:
  - creativity `31 / 31` ties
  - coherence `31 / 31` ties

Dense `0.5` also still fails to beat the prompt-only baseline cleanly, losing `0.032258` coherence net preference with all creativity comparisons tied.

## Interpretation

This resolves the old ambiguity.

The stronger metric is still far from perfect, but it now does the one thing `creativedecomp-8o1` required: it can weakly distinguish the prompt-only creativity baseline from neutral on the cached stories without changing generation.

Because the same stronger metric still shows no dense effect versus neutral, the Gemma 2 2B MacBook lane now qualifies as the first strong Phase 1 negative result under the repo's prereg-aware decision rule.

## What This Does Not Mean

- It does not mean creativity steering is impossible in general.
- It does not mean the whole project should pivot away from the original mechanistic path.
- It does not justify reopening decomposition on the current lane.

## What It Does Mean

- The 2B lane is no longer blocked primarily by metric ambiguity.
- The next task is strategic and bounded: decide what follow-up best strengthens or contextualizes this negative result.
- `creativedecomp-npt` should stay blocked until that next-lane decision is made.
