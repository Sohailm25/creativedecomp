# Current State

**Last updated:** 2026-03-18
**Updated by:** codex-gpt5
**Status:** in_progress
**Current phase:** Phase 1 - Response-centered contrast recovered a late-layer candidate, but deeper review says contrast repair and output-level validation still precede decomposition

## Active Thesis Lock

- `known`: this workspace is now a standalone git repository with remote `git@github.com:Sohailm25/creativedecomp.git`.
- `known`: the active task branch is `wip/creativedecomp-scaffold-lock`.
- `known`: `bd` is initialized locally; `creativedecomp-1ie`, `creativedecomp-9cm`, `creativedecomp-x99`, `creativedecomp-2eh`, `creativedecomp-yk4`, `creativedecomp-e0r`, `creativedecomp-wtf`, and `creativedecomp-6lm` are closed; `creativedecomp-02c` is the next ready task; `creativedecomp-roq` is the required pilot output-evaluation gate after that; and `creativedecomp-npt` now explicitly depends on both `creativedecomp-02c` and `creativedecomp-roq`.
- `known`: the primary experiment is `creativity direction -> SAE feature decomposition -> feature-level validation`, not the broader controller and basin-hopping ideas.
- `known`: the strongest default implementation path is `google/gemma-2-2b` plus GemmaScope `65K` residual SAEs on local MPS; narrower SAE widths remain method-specific pilot options, not the base configuration.
- `known`: the main methodological risk is naive SAE decomposition of a dense steering vector; signed, contrastive, or pursuit-based decomposition is mandatory.
- `known`: the strongest novelty framing is explaining why creativity is mechanistically different from simpler behavioral concepts such as refusal and sentiment.
- `known`: input-feature and output-feature separation is a hard requirement for any claim about creativity features.
- `known`: output-feature filtering is part of the planned primary path, not an optional cleanup step.
- `known`: cross-domain bridge features are in scope, but only as a tested hypothesis after the base decomposition lane is live.
- `known`: the experiment has an explicit publishable negative result path if creativity turns out to be more distributed or decomposition-resistant than simpler behavioral concepts.
- `known`: the initial local runtime freeze is now real on Python `3.14.2`, with pinned direct dependencies in `requirements.txt` and a resolved lock in `requirements.lock.txt`.
- `known`: the first frozen prompt registry lives under `prompts/creative_direction_v1_*` with a deterministic `32`-prompt pilot split and `128`-prompt confirm split derived from `euclaise/writingprompts`.
- `known`: the first dense creativity-direction smoke artifact now exists under `results/creativity_direction/20260318-gemma2-2b-repeng-smoke-layer12/`, using `google/gemma-2-2b`, the frozen pilot split, and a layer-12 PCA-on-differences extraction path grounded in `repeng` hidden-state collection.
- `known`: the smoke artifact is only a bounded execution check, not confirmatory evidence; its training-pair summary shows positive projections exceed negative projections on `23 / 32` pilot prompt pairs (`0.71875`), which is enough to prove the local path works but not enough to freeze the layer or make any creativity claim.
- `observed`: the full pilot layer sweep now exists under `results/creativity_direction/20260318-gemma2-2b-layer-sweep-pilot/`; the raw ranking selects layer `0` with perfect pair separation, while layer `7` is the best later-layer candidate by the same pilot rule.
- `inferred`: the raw layer-`0` win is likely dominated by lexical differences in the creative versus uncreative instruction templates rather than a clean creativity representation, so it should not be treated as the frozen creativity layer without control work.
- `observed`: the repaired generation-side smoke under `results/steering_eval/20260318-gemma2-2b-generation-smoke/` now uses continuation-style neutral and creative prompt harnesses from the frozen prompt registry and no longer falls into prompt-meta or writing-forum continuations on the pilot slice.
- `known`: the generation harness repair removes the base-model output-mode confound, but it does not resolve the separate layer-selection confound inherited from the raw instruction-template sweep.
- `observed`: the template-controlled layer sweep under `results/creativity_direction/20260318-gemma2-2b-layer-sweep-template-control/` keeps raw layer `0` as the uncorrected winner but finds that no layer clears the template-control threshold; the best controlled excess score is `0.000000`, so no dense creativity layer is currently frozen.
- `inferred`: the current creative-vs-uncreative instruction contrast is still dominated by prompt-template wording strongly enough that a decomposition run on any supposedly selected layer would be methodologically premature.
- `observed`: the response-centered pair builder under `results/creativity_direction/20260318-gemma2-2b-response-pairs-v2-pilot/` now freezes `32` creativity-vs-plain continuation pairs under a shared extraction wrapper, with `0.000000` positive meta fraction and `0.031250` negative meta fraction.
- `observed`: the controlled layer sweep on the response-centered `v2` pairs under `results/creativity_direction/20260318-gemma2-2b-layer-sweep-response-pairs-v2/` recovers layer `24` as both the raw and controlled winner with `0.593750` positive-greater-than-negative fraction (`19 / 32` pairs) and `0.593750` controlled fraction delta.
- `known`: the `v2` sweep removes the template-only control signal by construction because both sides share the same extraction wrapper; this fixes the original instruction-template confound but does not by itself prove that the recovered signal is strong enough for decomposition.
- `inferred`: layer `24` is now a legitimate late-layer candidate, but the separation is still weak enough that decomposition would be premature without a bounded calibration step.
- `observed`: the bounded `v2` generation smoke under `results/steering_eval/20260318-gemma2-2b-generation-smoke-response-pairs-v2/` stays story-like with `0.000000` meta fraction across all four conditions, but the steered-vs-unsteered differences are subtle rather than decisive.
- `observed`: the bounded calibration sweep under `results/steering_eval/20260318-gemma2-2b-v2-direction-calibration/` shows no clean monotone coefficient-response pattern on the top late-layer band; for layer `24`, the mean probe projection moves from `13.361952` unsteered to `-13.657598` at coeff `0.5`, `-42.777972` at coeff `1.0`, and only back to `1.912126` at coeff `2.0`.
- `observed`: the layer `20` calibration trend is cleaner only in the wrong way; its mean probe projection becomes steadily more negative as positive coefficient increases and is still more negative than the unsteered baseline even at coeff `-1.0`, which does not support a stable creativity-control interpretation.
- `observed`: the `v2` pair audit under `results/creativity_direction/20260318-gemma2-2b-response-pairs-v2-audit/` surfaces `7` informative rows and shows that several strongest losses are not garbage negatives; they are often as prompt-specific or more prompt-specific than the paired positives, while the positives often remain generic.
- `inferred`: the experiment has moved past the original template confound, but the current response-centered pair construction is still too noisy and weak to justify decomposition. The blocker is now contrast quality, not merely layer choice.
- `inferred`: the current `v2` pair construction is still weaker than the Olson-style counterpart path the research docs point to, because the positive and negative sides are independently sampled continuations rather than content-preserving creative/plain counterparts of the same story material.
- `known`: internal probe movement alone is no longer treated as a sufficient readiness signal for Phase 2; a pilot output-level creativity gate with a coherence/usefulness check is now required before any decomposition comparison reopens.
- `known`: the pilot output-level gate must compare against the prompt-only creativity baseline explicitly, but it does not require dense steering to outperform prompting on the pilot slice; the goal is to establish a real causal output effect and characterize the tradeoff honestly.
- `known`: the local operating files now exist for state tracking, preregistration, session logging, result indexing, validation code, and tracked empty directories that survive fresh clones.
- `known`: the final rigor audit is landed in `history/20260318-final-rigor-audit.md` and `results/infrastructure/20260318-final-rigor-audit.md`.
- `known`: no remaining structural differences from `resattn` look detrimental to execution rigor; the remaining differences are experiment-specific lanes and source documents.
- `known`: the full local test suite is currently green, including scaffold structure, helper-script parsing, core-doc baggage checks, AGENTS rigor coverage, and novelty-alignment checks.

## Immediate Next Steps

1. Strengthen the response-centered contrast (`creativedecomp-02c`) by defining audit-backed rejection or filtering rules, rebuilding a cleaner `v3` pair set around content-preserving creative/plain counterparts when feasible, and rerunning the controlled layer sweep plus bounded calibration in response-only and full-text form if those diagnostics diverge.
2. Freeze the missing pilot output-level gate (`creativedecomp-roq`) before Phase 2: run at least one locked creativity-side metric plus one coherence/usefulness check on the revised dense direction, compare against the prompt-only creativity baseline explicitly, and do not treat output-level readiness as interchangeable with internal probe movement.
3. Keep signed decomposition comparison (`creativedecomp-npt`) blocked until both the contrast-quality gate and the output-level gate pass.
4. Lock a two-family benchmark bundle plus matched refusal/sentiment baseline plans only after the dense-direction path is honest enough to carry forward.
