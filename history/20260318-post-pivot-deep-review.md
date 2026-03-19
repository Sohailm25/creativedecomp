# ABOUTME: Reassesses the local steering lane after the instruction-tuned refusal pivot.
# ABOUTME: Refines the next-step order so the repo stops regime-shopping without freezing the final claim too early.

# Post-Pivot Deep Review

Date: 2026-03-18
Agent: codex-gpt5

## Question

After the dense, cross-scale, sparse, and instruction-tuned refusal controls, what do we truthfully understand, what do we still not understand, and what is the next step that stays aligned with the original creativity-decomposition experiment?

## What The Repo Has Actually Established

1. Hidden-state behavioral directions are recoverable on the local Gemma plus SAE path.

- Creativity recovered a usable hidden-state candidate on the `v3` counterpart slice after the Olson-style `mean_difference` sensitivity.
- Refusal recovered clean hidden-state directions on Gemma 2 `2B`, Gemma 2 `9B`, and `google/gemma-3-270m-it`.

2. Output-level steering success has not been recovered for a simpler concept.

- Creativity dense steering never cleared the bounded output gate after the judge and metric corrections.
- Refusal dense steering stayed output-weak on Gemma 2 `2B`.
- Refusal stayed output-weak again on Gemma 2 `9B`.
- Refusal stayed output-weak under a sparse SAE-latent control.
- The instruction-tuned refusal pivot also stayed output-weak under the current gate.

3. The original "creativity is mechanistically different from simpler concepts" claim is therefore still unearned.

- We do not have a local simpler-concept output-side success case to compare against.
- We have not run sentiment, but sentiment is not the main missing piece because it would not resolve the more basic ambiguity that the local simpler-concept steering story is not yet clean.

## What The Repo Has Not Established

- Not that creativity is more distributed than refusal.
- Not that SAE decomposition fails in general.
- Not that dense steering fails in general.
- Not that sentiment would behave the same way as refusal.
- Not that the current instruction-tuned refusal all-tie gate is fully settled as an evaluation result.

## The Remaining Weak Spot

The final instruction-tuned refusal pivot did not get the same evaluation hardening that creativity needed.

- Creativity required an order-robust rerun, a cached-output manual audit, and a stronger prompt-grounded metric before the claim boundary was trusted.
- Instruction-tuned refusal currently has raw-output inspection, but not yet a locked manual audit on the cached outputs.
- Some prompt-only refusal generations are visibly more refusal-like than neutral generations, so freezing the final bundle without the cached-output audit would be slightly too eager.

## Revised Next-Step Order

1. Do not run another steering regime.

- No new base-model sweep
- no new instruction-tuned model pivot
- no sentiment run yet

2. Audit the cached instruction-tuned refusal outputs next.

- Use a locked manual rubric.
- Reuse cached outputs only.
- The purpose is to resolve judge-insensitivity risk, not to rescue the lane by changing the model or prompts.

3. Then freeze the final negative-result framing.

- If the audit still shows no clearer prompt-only refusal effect, finalize the local lane as a write-up-grade negative result.
- If the audit recovers prompt-only refusal but still no dense effect, finalize the bundle with the narrower claim that stronger evaluation recovers a baseline but still does not rescue local causal steering.

4. Keep the original experimental path parked, not abandoned.

- `creativedecomp-npt` stays blocked.
- The original creativity-decomposition thesis is not disproved globally.
- It is paused because this local Gemma plus SAE steering lane has not earned the simpler-concept control it would need before decomposition reopens.

## Why This Is The Most Truthful Alignment

This preserves all three priorities:

- truthful understanding, because it narrows the claim instead of overgeneralizing
- meaningful novelty, because the emerging result is about the gap between hidden-state recoverability and output-side causal control on a realistic local stack
- the original experimental path, because it refuses to smuggle in controller-style extensions or decomposition claims that the current evidence does not support
