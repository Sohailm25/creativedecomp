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
