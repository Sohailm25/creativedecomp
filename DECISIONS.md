# Decisions Log

## [2026-03-18T01:20:00-0500] DECISION: Reuse the `resattn` operating scaffold for this workspace

- Trigger: Sohail asked for the `~/resattn` directory structure and AGENTS shape to be copied into this experiment.
- Decision: mirror the `resattn` scaffold shape and adapt the content to the creativity-decomposition experiment.
- Rationale: the value is in the operational discipline and file layout, not in the depth-routing-specific thesis.
- Impact: this repo now tracks state, prereg, decisions, reflections, results, and sessions using the same research operating pattern.

## [2026-03-18T01:25:00-0500] DECISION: Lock the primary lane to creativity-direction decomposition on a MacBook-feasible stack

- Trigger: the local feasibility and novelty docs converge on one clear primary experiment.
- Decision: make `Gemma 2 2B + GemmaScope + creativity-direction decomposition` the default lane, and treat controller-style creativity navigation as an extension lane.
- Rationale: this is the lowest-risk and most publishable experiment supported by the local research docs.
- Impact: results directories, prereg, and guidance docs all prioritize the creativity-direction, decomposition, and feature-validation workflow.

## [2026-03-18T01:30:00-0500] DECISION: Treat naive dense-vector SAE encoding as invalid by default

- Trigger: the novelty review identifies out-of-distribution and signed-contribution failure modes for direct SAE encoding of steering vectors.
- Decision: require contrastive decomposition, gradient pursuit, FISTA, or another signed method before any creativity-feature claim.
- Rationale: a clean-looking but invalid decomposition would be worse than no decomposition.
- Impact: `AGENTS.md`, `history/PREREG.md`, and `background-work/MECH_INTERP_GUIDANCE.md` now all encode this restriction.

## [2026-03-18T01:35:00-0500] DECISION: Record the git-state blocker explicitly instead of faking cleanliness

- Trigger: the workspace lives under `/Users/sohailmo`, and the inherited git branch is unrelated to this experiment.
- Decision: document that `creativedecomp/` is not yet a standalone repo and that branch hygiene is pending Sohail's approval.
- Rationale: pretending the parent repo branch is the experiment branch would corrupt history and violate the local operating rules.
- Impact: current-state files now call this out as an unresolved but important setup item.

## [2026-03-18T01:40:00-0500] DECISION: Add a structure regression test for the research scaffold

- Trigger: scaffolds drift unless there is an explicit check.
- Decision: add `tests/test_scaffold_structure.py` and treat it as the first guardrail for this workspace.
- Rationale: the directory contract is part of the experiment's operating system, not just documentation.
- Impact: future sessions can verify scaffold integrity with one local test command.

## [2026-03-18T02:20:00-0500] DECISION: Initialize `creativedecomp/` as its own git repository and wire the real remote

- Trigger: Sohail created the remote repository and asked for the work to be pushed from the correct project root.
- Decision: initialize `creativedecomp/` as a standalone repo, attach `origin`, create the task branch `wip/creativedecomp-scaffold-lock`, and initialize `bd` locally.
- Rationale: the experiment needs its own history, issue tracking, hooks, and pushes rather than leaking into the home-directory repo.
- Impact: current-state files, issue tracking, and push workflow now belong to this repo instead of the parent workspace.

## [2026-03-18T02:30:00-0500] DECISION: Keep `resattn` visible only as a structural source, not as a live thesis dependency

- Trigger: the rereview surfaced a few core-doc references that still named the old routing thesis directly.
- Decision: trim explicit sibling-project thesis language out of the core operating docs and keep those references only in adaptation-history material.
- Rationale: structure should be inherited; thesis language should not be.
- Impact: the main docs now stay focused on the creativity experiment while the historical adaptation note still records where the scaffold came from.

## [2026-03-18T03:05:00-0500] DECISION: Match `resattn` execution rigor more closely by restoring missing persistent scaffold pieces

- Trigger: the final audit showed that the repo kept the broad top-level shape but not all of the clone-surviving and execution-surviving structure that makes `resattn` robust.
- Decision: add tracked placeholders for empty directories, add `validation/`, add the standard runtime-freeze file locations, and expand `AGENTS.md` to the same operational section coverage as `resattn`.
- Rationale: a directory that exists only on one machine or an operating contract that drops half the control sections is structurally weaker even if it looks similar at a glance.
- Impact: fresh clones now preserve the intended scaffold, and the live operating contract now covers execution order, guardrails, required lanes, results registration, write-ups, and branch truth.

## [2026-03-18T03:12:00-0500] DECISION: Align the live experiment framing to the strongest version in `research/experiment-novelty.md`

- Trigger: the final audit found that the repo captured the decomposition idea but not the full novelty memo's strongest framing.
- Decision: center the project on whether creativity is mechanistically different from simpler behavioral concepts, require pilot comparison of at least two signed decomposition methods, keep refusal and sentiment as required reference baselines, and preserve the publishable negative-result path.
- Rationale: this framing is stronger and more defensible than a generic "decompose the creativity vector" story.
- Impact: `CURRENT_STATE.md`, `history/PREREG.md`, `background-work/RESEARCH_POSITIONING.md`, `background-work/GAPS_SYNTHESIS.md`, and `configs/experiment.yaml` now all reflect the same novelty-backed direction.

## [2026-03-18T03:24:00-0500] DECISION: Resolve the internal doc hierarchy explicitly

- Trigger: the research set mixes broad-program documents with tighter execution documents, and they are not equally binding for the current phase.
- Decision: treat `research/experiment-novelty.md` and `research/experiment-macbook-guide.md` as the highest-priority current-phase documents; treat `research/transcript.md` and `research/experiment-ideas.md` as motivation and extension-space docs unless a narrower spec promotes one of their ideas into the active phase.
- Rationale: without an explicit hierarchy, the repo can drift back toward broad controller or basin-hopping work before the novelty-backed primary experiment is honestly executed.
- Impact: `AGENTS.md` now states the priority order directly, reducing ambiguity for future sessions.

## [2026-03-18T10:06:00-0500] DECISION: Freeze the initial runtime on the stack that actually imports locally, and defer optional steering tooling that conflicts with it

- Trigger: the first runtime-freeze task required moving from placeholder dependency files to a real local stack on the MacBook path.
- Decision: freeze the initial runtime around Python `3.14.2`, `torch==2.10.0`, `transformers==5.3.0`, `sae-lens==6.38.0`, `repeng==0.4.0`, `datasets==4.8.2`, `accelerate==1.13.0`, `safetensors==0.7.0`, `sentencepiece==0.2.1`, and `scipy==1.17.1`, and leave `steering-vectors` out of the base freeze for now.
- Rationale: this exact stack installs and imports locally, while `steering-vectors` resolves against the `transformers<5` line and would make the initial freeze ambiguous before the first experiment run.
- Impact: the repo now has a real reproducible runtime freeze in `requirements.txt` and `requirements.lock.txt`, and any later addition of `steering-vectors` must be logged as an intentional runtime revision rather than silently folded into the base environment.

## [2026-03-18T10:55:00-0500] DECISION: Do not treat the raw layer-0 winner from the pilot sweep as the provisional creativity layer

- Trigger: the all-layer pilot sweep ranked layer `0` first with perfect training-pair separation.
- Decision: record layer `0` as the raw sweep winner, but do not freeze it as the creativity layer; instead, carry both layer `0` and the next-ranked layer `7` into the first generation-side smoke and treat the result as a confound check.
- Rationale: perfect separation at the earliest layer is more plausibly explained by lexical differences between the creative and uncreative instruction templates than by a clean creativity representation.
- Impact: the next steering smoke compares two candidate layers rather than blindly promoting layer `0`, and a new follow-up issue now tracks explicit lexical-confound control.

## [2026-03-18T11:02:00-0500] DECISION: Treat the current base-model prompting harness as invalid for steering-side creativity interpretation

- Trigger: the first generation-side smoke on neutral prompts plus layers `0` and `7` produced mostly prompt-meta continuations and writing-forum style text rather than clean short stories.
- Decision: do not interpret the current generation smoke as evidence for or against creativity steering; treat it as a harness-validation artifact and prioritize a base-model-compatible story prompting redesign before deeper steering claims.
- Rationale: if the model is not reliably producing the target output mode, steering differences cannot be cleanly attributed to creativity rather than prompt-format mismatch.
- Impact: a new prompt-harness repair issue is now on the critical path ahead of deeper steering evaluation, while the saved smoke artifact remains a useful negative checkpoint.

## [2026-03-18T11:24:00-0500] DECISION: Use continuation-style story-opening harnesses for generation-side steering smoke

- Trigger: the prompt-harness probe showed the instruction-style generation prompt continuing into assignment/forum text, while continuation-style story openings produced story-like completions.
- Decision: move the neutral generation harness to `Prompt: {prompt}\n\nStory:\nOnce` and the prompt-only creativity baseline to `Prompt: {prompt}\n\nCreative story:\nOnce`, and record both in the frozen prompt registry.
- Rationale: the steering smoke needs a base-model-compatible output mode before any qualitative creativity differences can be interpreted.
- Impact: the saved generation smoke artifact is now a real story-generation comparison instead of a prompt-format failure artifact.

## [2026-03-18T11:35:00-0500] DECISION: Do not freeze any dense creativity layer from the current instruction-template contrast

- Trigger: the template-controlled layer sweep found that raw layer `0` still wins the uncorrected sweep, but no layer has positive excess over the template-only control.
- Decision: treat the current creative-vs-uncreative instruction pair as too confounded to freeze any dense creativity layer, and require a revised contrastive extraction setup before decomposition work assumes a settled layer.
- Rationale: a control that yields no surviving layer is a negative result, not a license to quietly keep the raw winner.
- Impact: `creativedecomp-npt` is now blocked on a cleaner extraction contrast, and the template-controlled sweep becomes the current truth artifact for layer selection.
