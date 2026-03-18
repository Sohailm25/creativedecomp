# Current State

**Last updated:** 2026-03-18
**Updated by:** codex-gpt5
**Status:** in_progress
**Current phase:** Phase 1 - Response-centered contrast landed; provisional late-layer recovered but not yet calibrated

## Active Thesis Lock

- `known`: this workspace is now a standalone git repository with remote `git@github.com:Sohailm25/creativedecomp.git`.
- `known`: the active task branch is `wip/creativedecomp-scaffold-lock`.
- `known`: `bd` is initialized locally; `creativedecomp-1ie`, `creativedecomp-9cm`, `creativedecomp-x99`, `creativedecomp-2eh`, `creativedecomp-yk4`, `creativedecomp-e0r`, and `creativedecomp-wtf` are closed; `creativedecomp-6lm` is the next ready task; and `creativedecomp-npt` now explicitly depends on `creativedecomp-6lm`.
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
- `inferred`: the experiment has moved past the structural confound and into a calibration problem; the honest blocker is not "find any layer" anymore but "show the recovered late-layer direction matters enough to justify decomposition."
- `known`: the local operating files now exist for state tracking, preregistration, session logging, result indexing, validation code, and tracked empty directories that survive fresh clones.
- `known`: the final rigor audit is landed in `history/20260318-final-rigor-audit.md` and `results/infrastructure/20260318-final-rigor-audit.md`.
- `known`: no remaining structural differences from `resattn` look detrimental to execution rigor; the remaining differences are experiment-specific lanes and source documents.
- `known`: the full local test suite is currently green, including scaffold structure, helper-script parsing, core-doc baggage checks, AGENTS rigor coverage, and novelty-alignment checks.

## Immediate Next Steps

1. Calibrate the recovered `v2` late-layer direction (`creativedecomp-6lm`) with a bounded steering-scale sanity sweep plus a small pair-quality or creativity-side audit before allowing decomposition.
2. Reopen signed decomposition comparison (`creativedecomp-npt`) only if the calibration step shows that the provisional late-layer direction is real enough to matter beyond a weak pair-separation metric.
3. Lock a two-family benchmark bundle plus matched refusal/sentiment baseline plans so the "mechanistically different" framing stays testable once the dense-direction path is honest enough to carry forward.
