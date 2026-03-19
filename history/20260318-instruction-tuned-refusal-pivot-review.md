# ABOUTME: Reviews the final bounded instruction-tuned refusal pivot against the research framing.
# ABOUTME: Records why the repo now stops steering-regime shopping and moves to a write-up-grade negative result.

# Instruction-Tuned Refusal Pivot Review

Date: 2026-03-18
Agent: codex-gpt5

## Question

Did the last allowed paper-backed regime shift, an instruction-tuned Gemma plus GemmaScope v2 refusal control, rescue a clean simpler-concept output effect after the base-model lane failed across dense, cross-scale, and sparse controls?

## Stack Frozen Inside The Task

- Model: `google/gemma-3-270m-it`
- SAE release: `gemma-scope-2-270m-it-res`
- Reference SAE: `layer_12_width_16k_l0_medium`
- Residual candidate layers: `[5, 9, 12, 15]`

This was the smallest locally feasible instruction-tuned Gemma plus GemmaScope v2 stack that supported chat generation, hidden-state extraction, `repeng` control wrapping, and `sae-lens` loading on the MacBook lane.

## What The Pivot Established

1. Hidden-state refusal is not the missing ingredient.

- The full sweep at `results/refusal_direction/20260318-gemma3-270m-it-layer-sweep-v1-mean-difference/` separates all `32 / 32` refusal/compliance pairs.
- Layer `9` is the best instruction-tuned residual site by the task metric, with mean margin `431.563232` and margin z-score `4.048515`.

2. The output-side simpler-concept claim still does not recover.

- The full gate at `results/steering_eval/20260318-gemma3-270m-it-refusal-output-gate-v1/` stays all ties on refusal for prompt-only versus neutral and for both dense conditions versus neutral.
- Prompt-only refusal versus neutral loses coherence slightly (`-0.083333`).
- The best dense condition (`layer 9`, coeff `1.0`) only ties coherence and does not improve refusal over neutral.

3. The raw outputs do not support a hidden evaluation bug as the main explanation.

- Some prompts still show clear refusal-style text in the prompt-only condition.
- Other prompts remain partially compliant or evasive across conditions.
- The all-tie judgment pattern therefore matches genuinely weak or convergent output behavior rather than a simple replay of the earlier order-bias bug.

## Alignment Check Against The Research Docs

This remains aligned with the novelty and MacBook docs because it:

- stayed on the Gemma plus SAE path instead of jumping to unrelated architectures
- used refusal, not creativity, as the bounded simpler-concept control
- tested the last paper-backed regime dependence that the local docs still left open
- stopped before reopening decomposition or creativity steering on a weak causal output story

## Decision

The instruction-tuned refusal pivot failed as a rescue. The local steering weakness now survives:

- base-model dense refusal control
- cross-scale dense refusal control
- sparse SAE-latent refusal control
- instruction-tuned dense refusal control

The next honest move is a write-up-grade negative-result synthesis, not more steering-regime shopping.
