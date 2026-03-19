# ABOUTME: Synthesizes what the 2B plus 9B dense-steering controls do and do not establish.
# ABOUTME: Records why the next honest lane is an alternate-method control on the same Gemma and GemmaScope stack.

# Cross-Scale Dense Steering Synthesis

Date: 2026-03-18
Agent: codex-gpt5

## Question

After the matched Gemma 2 `2B` refusal control and the bounded Gemma 2 `9B` refusal scale check both stay output-weak, what is the scientifically honest continuation that still serves the original creativity-decomposition thesis?

## What The Evidence Now Establishes

1. Dense hidden-state extraction is not the bottleneck.

- Creativity on Gemma 2 `2B` recovered a hidden-state candidate after the `v3` counterpart redesign and Olson-style `mean_difference` extraction.
- Refusal on Gemma 2 `2B` and Gemma 2 `9B` is cleaner still, with perfect `32 / 32` pair separation on both sizes.

2. Dense output-side control is weak across the local base-model lane.

- Creativity dense steering on Gemma 2 `2B` never cleared the bounded output gate after the judge and metric fixes.
- Refusal dense steering on Gemma 2 `2B` also stayed weaker than the prompt-only baseline.
- Gemma 2 `9B` improved the hidden-state refusal signal but still failed the bounded refusal gate.

3. The current negative result is therefore broader than creativity alone.

- The best current reading is not "creativity is uniquely hard on this stack."
- The better reading is "dense additive steering on this base-model sampled-decoding lane is output-weak even for a simpler concept."

## Why Not Stop At A Write-Up

- A write-up-grade negative result is now legitimate, but it is still not the highest-information next step.
- The papers we already grounded on do not treat dense additive steering as the only serious intervention family. `SAE-TS`, `FGAA`, `SAS`, and Arad-style output-feature work all point to effect-aware or sparse interventions as the stronger causal lane.
- Stopping now would leave the strongest local Gemma plus GemmaScope method family untested, which would weaken any claim that the MacBook path itself has been honestly exhausted.

## Why Not Pivot To An Instruction-Tuned Lane Next

- That pivot changes too much at once:
  - model behavior and prompt format
  - likely SAE release or availability assumptions
  - the comparability of the current 2B and 9B base-model artifacts
- It is a valid future follow-up, but not the next bounded step if the goal is to learn whether the failure is specific to dense additive steering or broader than that.

## Chosen Next Lane

Run a bounded alternate-method control lane on the same Gemma 2 `2B` plus GemmaScope stack.

- Start with refusal, not creativity, because refusal remains the cleanest simpler-concept control in the literature and in our local hidden-state artifacts.
- Use an SAE-aware effect-oriented or sparse intervention family rather than another dense additive vector sweep.
- Treat this as a method-family control, not as reopening decomposition.

## Operational Consequence

- Stop further dense base-model steering sweeps on the current MacBook lane unless a later result explicitly reopens them.
- Keep `creativedecomp-npt` blocked.
- The next issue should define one bounded refusal control using the same local stack and output gate, but with an alternate intervention family aligned with `SAE-TS`, `FGAA`, or `SAS`.

## Why This Stays Aligned With The Original Experiment

- It preserves the original thesis: mechanistic structure behind creativity steering compared against simpler concepts.
- It keeps the same local Gemma plus GemmaScope path that the MacBook feasibility memo selected.
- It uses more of the paper-backed method stack rather than quietly downgrading the project to a generic steering write-up.
- It keeps the eventual decomposition claim honest by refusing to reopen Phase 2 until the intervention family question is cleaner.
