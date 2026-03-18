# Current State

**Last updated:** 2026-03-18
**Updated by:** codex-gpt5
**Status:** in_progress
**Current phase:** Phase 1 - Dense creativity-direction smoke artifact landed

## Active Thesis Lock

- `known`: this workspace is now a standalone git repository with remote `git@github.com:Sohailm25/creativedecomp.git`.
- `known`: the active task branch is `wip/creativedecomp-scaffold-lock`.
- `known`: `bd` is initialized locally; `creativedecomp-1ie` and `creativedecomp-9cm` are closed, and the next ready tasks are `creativedecomp-x99`, `creativedecomp-2eh`, and `creativedecomp-npt`.
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
- `known`: the local operating files now exist for state tracking, preregistration, session logging, result indexing, validation code, and tracked empty directories that survive fresh clones.
- `known`: the final rigor audit is landed in `history/20260318-final-rigor-audit.md` and `results/infrastructure/20260318-final-rigor-audit.md`.
- `known`: no remaining structural differences from `resattn` look detrimental to execution rigor; the remaining differences are experiment-specific lanes and source documents.
- `known`: the full local test suite is currently green, including scaffold structure, helper-script parsing, core-doc baggage checks, AGENTS rigor coverage, and novelty-alignment checks.

## Immediate Next Steps

1. Extend the pilot run from the single default layer to a controlled layer sweep so layer choice is frozen by evidence rather than by scaffold default.
2. Add the first steering-output smoke at the chosen pilot layer so dense direction extraction is followed by an observable generation-side check.
3. Compare at least two legal signed decomposition methods on the pilot slice before freezing the confirm path.
4. Lock a two-family benchmark bundle plus matched refusal/sentiment baseline plans so the "mechanistically different" framing stays testable.
