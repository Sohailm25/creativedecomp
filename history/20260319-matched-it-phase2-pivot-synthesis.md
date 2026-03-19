# ABOUTME: Synthesizes the matched instruction-tuned creativity and refusal evidence against the prereg and research docs.
# ABOUTME: Records why Phase 2 can open as a bounded pilot on the instruction-tuned stack without widening the broader claim boundary.

# Matched Instruction-Tuned Phase 2 Pivot Synthesis

Date: 2026-03-19
Agent: codex-gpt5

## Question

After the matched instruction-tuned creativity manual audit landed, should the repo keep Phase 2 blocked behind one more confirmatory creativity follow-up, or is there now enough evidence to open pilot decomposition on the same instruction-tuned stack?

## Sources Re-Checked

- `history/PREREG.md`
- `research/experiment-novelty.md`
- `research/experiment-macbook-guide.md`
- `background-work/IMPLEMENTATION_GROUNDING.md`
- `history/20260319-instruction-tuned-refusal-manual-audit-review.md`
- `history/20260319-instruction-tuned-creativity-replication-review.md`
- `results/steering_eval/20260319-gemma3-270m-it-refusal-output-gate-v1-manual-audit/summary.json`
- `results/steering_eval/20260319-gemma3-270m-it-output-gate-v1-manual-audit/summary.json`

## What The Evidence Now Establishes

1. The matched instruction-tuned stack clears the prereg's minimum Phase 1 gate for a pilot decomposition pivot.

- The prereg requires a bounded output-level creativity effect plus a coherence or usefulness check before Phase 2 opens.
- On `google/gemma-3-270m-it` plus `gemma-scope-2-270m-it-res`, the locked manual audit now shows dense creativity at `layer 12`, coeff `1.0`, beating neutral on prompt-grounded creativity (`0.583333` vs `0.083333`) and coherence (`0.916667` vs `0.083333`).
- On the same stack, refusal already has both a clear prompt-only baseline and modest dense output-side wins under the same manual-audit style.

2. Another generic creativity rerun would add less information than a bounded decomposition pilot.

- The main remaining weaknesses are judge quality and confirmatory evaluation breadth, not the absence of any output-side creativity effect.
- Requiring another generic creativity gate now would mostly repeat Phase 1 with slightly different wrappers while delaying the actual novelty-bearing question.

3. The instruction-tuned stack should not replace the repo's full thesis framing.

- The MacBook guide and AGENTS thesis locks still anchor the default base configuration at `google/gemma-2-2b` plus GemmaScope `65K`.
- The instruction-tuned pivot exists because it is the first locally matched creativity/refusal stack with manual-audit-supported output effects, not because the old base lane has become irrelevant.

## What This Still Does Not Establish

- Not that the automatic creativity judge is fixed.
- Not that prompt-only creativity is strong on this stack.
- Not that the full "creativity is mechanistically different from simpler concepts" claim is already earned.
- Not that confirmatory feature-validation or benchmark-heavy claims can proceed without stronger evaluation.

## Decision

Open Phase 2 as a bounded pilot on `google/gemma-3-270m-it` plus `gemma-scope-2-270m-it-res`.

The next implementation task is `creativedecomp-npt`, now interpreted as:

- compare at least two signed decomposition methods on the matched instruction-tuned creativity direction
- keep the work pilot-scoped
- preserve the broader claim boundary until evaluation hardening catches up

## Why This Is The Most Truthful Alignment

- It follows the prereg literally enough to avoid Phase 1 drift.
- It uses the first stack where creativity and refusal can finally be compared within the same local regime.
- It avoids pretending that a 12-prompt manual audit settles the later claim boundary.
- It keeps the original experiment intact: mechanistic creativity decomposition remains the primary lane, and the instruction-tuned pivot is a bounded means of reaching it honestly.
