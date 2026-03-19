# ABOUTME: Synthesizes the post-sparse-control lane choice against the research docs.
# ABOUTME: Records why one instruction-tuned refusal pivot is justified before the local lane is written up as negative.

# Instruction-Tuned Pivot Synthesis

Date: 2026-03-18
Agent: codex-gpt5

## Question

After dense, cross-scale, and sparse SAE-latent refusal controls all fail on the local base-model Gemma lane, should the repo stop on a write-up-grade negative result or run one more bounded pivot?

## What The Current Evidence Actually Establishes

1. The local base-model lane is exhausted enough to stop more base-model steering variants.

- Creativity failed the output gate after the strongest landed `v3` plus `mean_difference` recovery.
- Refusal failed the matched output gate on Gemma 2 `2B`.
- Refusal failed again on Gemma 2 `9B`.
- Refusal failed again under a sparse SAE-latent control on Gemma 2 `2B`.

2. That negative result is meaningful, but it is not yet the cleanest form of the thesis.

- The current best reading is not "creativity is mechanistically special."
- The current best reading is "this local base-model steering lane is output-weak even for a simpler concept."

3. One paper-backed regime-shift explanation is still alive.

- The novelty memo explicitly warns that SAE quality is dataset-dependent and notes that chat-specific behavior features can look materially better than web-text ones.
- The MacBook guide says GemmaScope v2 covers instruction-tuned Gemma checkpoints and treats that path as locally feasible.

## Why Not Stop Immediately

- A write-up stop would now be defensible, but it would still overgeneralize from a lane that is clearly base-model-specific.
- The repo would be stopping before testing the smallest remaining regime change that the local research docs already identify as plausible and feasible.

## Why The Pivot Should Be Instruction-Tuned Refusal, Not Creativity

- Refusal is still the narrowest simpler-concept control.
- The first question is not whether creativity works on a new stack. The first question is whether any cleaner output-level steering effect appears once the model and SAE regime are better aligned.
- If refusal still fails there, the local steering lane is exhausted enough to write up honestly without reopening creativity work.

## Chosen Next Lane

Run one bounded instruction-tuned refusal pivot on a GemmaScope v2-backed instruction-tuned Gemma stack.

- Freeze the smallest locally feasible paired checkpoint and SAE release inside the task.
- Reuse the matched refusal hidden-state and output-gate discipline as closely as the new stack allows.
- Do not reopen creativity decomposition during this pivot.

## Decision Rule

- If the instruction-tuned refusal pivot still fails to recover a clean simpler-concept output-level win, stop and write up the local steering lane as a negative result.
- If it succeeds, only then consider an instruction-tuned creativity-direction replication lane.

## Alignment Check

This stays aligned with the original experiment because it:

- preserves the Gemma plus SAE path rather than jumping to unrelated architectures
- uses a simpler-concept control before reopening creativity claims
- treats decomposition as blocked until the causal output lane is honest again
- respects the negative-result path without taking it too early
