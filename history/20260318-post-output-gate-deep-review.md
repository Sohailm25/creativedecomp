# ABOUTME: Cross-session synthesis after the order-robust output-gate collapse and before any new evaluation changes.
# ABOUTME: Records the refined next-step order so future sessions preserve falsifiability and avoid metric-shopping.

# Post-Output-Gate Deep Review

Date: 2026-03-18
Agent: codex-gpt5

## Scope

This review rereads the active research docs, prereg, current-state files, and the session trail from the first runtime freeze through the corrected order-robust output gate.

The purpose is not to restate every artifact. It is to answer a narrower question: what do we now know well enough to act on, what remains uncertain, and what next step best preserves truthful discovery rather than convenience.

## What Is Established

- The local MacBook lane is real. The runtime, model path, prompt registry, hidden-state extraction path, and output-gate harness all execute and save reproducible artifacts.
- The early positive result was confounded. The original instruction-template contrast was not a defensible creativity object, and the template-control result caught that correctly.
- Tightening counterpart quality mattered. The `v3` response-centered pairs removed most of the easy content-drift excuses from the earlier `v2` path.
- Extraction method mattered materially. PCA-on-differences failed on the landed `v3` slice, while Olson-style `mean_difference` recovered a usable hidden-state candidate at layer `23`.
- Hidden-state recovery is still not enough. The corrected output gate on saved stories collapses prompt-only creativity versus neutral and dense versus neutral to ties under the current order-robust local judge.

## What Is Not Established

- We do not yet know whether the Gemma 2 2B lane is a true negative result for dense creativity steering or whether the current pilot creativity metric is too weak to detect an existing effect.
- We do not yet have evidence strong enough to reopen signed decomposition. A hidden-state handle without a trustworthy output-level gate is still weaker than the prereg and weaker than the novelty framing.
- We do not yet know whether the response-only `mean_difference` lane matters beyond diagnostics. The full-text layer-23 path remains the primary candidate.

## Main Risk

The main risk is no longer prompt-template confounding or pair-quality drift. It is metric-shopping.

If the next step changes both the generated outputs and the evaluation metric, then the experiment loses the ability to tell whether the remaining weakness is in the dense direction, the judge, the prompt harness, or all three. That would weaken both a positive result and a negative result.

## Refined Next-Step Order

1. Reuse the cached generated outputs in `results/steering_eval/20260318-gemma2-2b-output-gate-v1/`.
2. Run a small blinded manual audit on those stories with a locked rubric focused on visible creativity, specificity, and coherence.
3. Choose one stronger pilot creativity-side metric grounded in that audit and the creativity-evaluation papers.
4. Rerun the gate on the same cached outputs with the stronger metric and the existing order-bias controls.
5. Only after that decide whether to treat the Gemma 2 2B MacBook lane as a strong Phase 1 negative result or an evaluation-quality failure.

## What Not To Do Yet

- Do not reopen `creativedecomp-npt`.
- Do not generate new stories for the next evaluation pass.
- Do not retune layer `23` or the `0.5` to `1.0` coefficient band before rescoring the cached outputs.
- Do not pivot into bridge features, basin dynamics, or controller-style work.
- Do not broaden to a larger model or different SAE stack before the cached-output follow-up resolves.

## Decision Tree

- If a stronger metric can separate prompt-only creativity prompting from neutral on the cached stories but still shows no dense effect, that is the first strong Phase 1 negative result for this Gemma 2 2B lane.
- If the stronger metric still cannot separate prompt-only from neutral on the cached stories, the bottleneck remains evaluation sensitivity or prompt-harness quality rather than the dense direction alone.
- If a stronger metric separates prompt-only from neutral and also recovers a dense effect with a coherent tradeoff profile, only then does decomposition become an honest next discussion.

## Alignment Check Against The Research Docs

- This order stays aligned with `research/experiment-novelty.md` because it keeps the novelty claim tied to a bounded mechanistic test rather than drifting into generic creativity-steering demos.
- It stays aligned with `research/experiment-macbook-guide.md` because it preserves the low-cost local lane rather than escalating prematurely to a different stack.
- It stays aligned with `research/transcript.md` and `research/experiment-ideas.md` because it does not discard the broader ideas, but it keeps them clearly downstream of the main publishable path.

## Bottom Line

The experiment is still on its original path. The evidence so far is meaningful, but its meaning is narrower than a decomposition-ready win: creativity on this stack has been harder to recover, more method-sensitive, and more evaluation-fragile than simpler behavioral steering targets.

The honest next move is not to push farther forward. It is to make the current output-level claim falsifiable on the cached stories before anything else changes.
