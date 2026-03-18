# AGENTS.md - Codex Agent Directives for Mechanistic Creativity Decomposition

## Scope and Precedence

This file governs all work within `creativedecomp/` and supersedes any AGENTS.md found in parent directories for this workspace.

Parent-workspace assumptions that do not apply here:

- no inherited experimental claims or phase names from sibling projects belong here
- this workspace is local-first and MacBook-first; no Modal, cluster, or remote runner assumptions belong here
- the primary scientific target is not a broad creativity platform, but a bounded mechanistic experiment
- safety and alignment steering papers are comparison references here, not the thesis itself
- this repository is standalone; its git history, issue tracking, and branches belong to `creativedecomp/`

Everything below this section is the authoritative directive set for this experiment.

This experiment is grounded in local source documents, not in inherited assumptions from sibling projects.

## Mission

Execute the mechanistic creativity experiment defined by:

- `research/transcript.md`
- `research/experiment-ideas.md`
- `research/experiment-macbook-guide.md`
- `research/experiment-novelty.md`

The goal is to show, as rigorously as possible, whether a creativity steering direction in a small open model can be decomposed into interpretable SAE features and whether those features support controlled, cross-domain creative generation.

The default paper-shaped framing is not "we solved machine creativity." It is: creativity steering appears to rely on specific latent features, and those features may be analyzable as a distinct mechanistic object.

## Issue Tracking

This project uses **bd (beads)** for issue tracking.
Run `bd prime` for workflow context, or install hooks with `bd hooks install`.

Quick reference:

- `bd ready` - find unblocked work
- `bd create "Title" --type task --priority 2` - create issue
- `bd update <id> --status in_progress` - claim work
- `bd close <id>` - complete work
- `bd sync` - sync issue state at session end

## Thesis Locks

These are not optional. Every implementation and write-up must preserve them.

1. The primary experiment is creativity-direction decomposition, not a broad latent-navigation program.
2. The default implementation path is `Gemma 2 2B + GemmaScope + RepE/CAA + SAE decomposition`, because that is the best-supported MacBook-feasible lane.
3. The first claim is about interpretable latent structure, not about autonomous scientific discovery.
4. Do not naively encode a dense steering vector through an SAE and call the result mechanistic. Use contrastive decomposition, gradient pursuit, FISTA, or another method that respects signed contributions and out-of-distribution risk.
5. Treat positive and negative feature contributions as first-class objects. Suppressed features matter.
6. Separate input features from output features. A feature that appears on creative text is not yet a creativity feature unless it causally changes outputs.
7. Cross-domain bridge features are a hypothesis, not a default conclusion.
8. Every creativity gain must be reported alongside coherence, usefulness, and formatting side effects.
9. Controller-style latent navigation and thermodynamic basin-hopping are extension lanes. They are not allowed to replace the primary lane before the decomposition experiment is honestly resolved.

## Runtime Assumptions

- Primary machine: MacBook Pro
- Python environment: `.venv`
- Primary backend: PyTorch + MPS
- Fallback tooling: CPU where MPS coverage is incomplete
- no Modal
- no remote training assumptions

## Epistemic Standards

You are doing scientific work. Act like it.

1. Assumption quarantine. Any unverified statement is a hypothesis, not a fact. Label claims with `known`, `observed`, `inferred`, or `unknown`.
2. Evidence-first reasoning. Base conclusions on artifacts you can inspect: prompts, feature tables, cached activations, judge outputs, benchmark summaries, and saved result files.
3. No forced logic. Reject the jump from "feature aligned with direction" to "feature causes creativity" unless causal interventions support it.
4. Claim-evidence proportionality. Never write `validated`, `confirmed`, or `significant` without the metric, comparison, and threshold.
5. Adversarial self-questioning is mandatory before claim-bearing runs:
   - What is the simplest explanation besides creativity?
   - Is this really creativity, or just stylistic looseness or verbosity?
   - Could the steering artifact be mostly formatting, genre, or lexical diversity?
   - If the result looks unusually clean immediately, what is the probability the implementation is wrong?
6. Pre-register before running. The local prereg lives in `history/PREREG.md` and is the mandatory prereg artifact for this repo.
7. Skepticism toward clean results. Creativity benchmarks are easy to game. A strong result needs stronger controls, not applause.
8. Implementation skepticism is critical. A plausible feature ranking is not a validated decomposition.

## Directory Map

```text
creativedecomp/
├── AGENTS.md
├── CURRENT_STATE.md
├── DECISIONS.md
├── README.md
├── SCRATCHPAD.md
├── THOUGHT_LOG.md
├── background-work/
│   ├── REFERENCES.md
│   ├── MECH_INTERP_GUIDANCE.md
│   ├── GAPS_SYNTHESIS.md
│   ├── PROPOSAL_REVIEW.md
│   ├── RESEARCH_POSITIONING.md
│   ├── SAFETY_PUBLICATION_POLICY.md
│   └── papers/
│       ├── DOWNLOAD_MANIFEST.md
│       └── files/
├── configs/
│   └── experiment.yaml
├── history/
│   ├── PREREG.md
│   ├── 20260318-resattn-scaffold-adaptation.md
│   └── 20260318-final-rigor-audit.md
├── journal/
│   ├── current_state.md
│   └── logs/
├── knowledge/
│   └── general/
│       ├── accomplishments/
│       ├── insights/
│       ├── learnings/
│       └── references/
├── notebooks/
├── prompts/
├── research/
├── requirements.txt
├── requirements.lock.txt
├── results/
│   ├── infrastructure/
│   ├── creativity_direction/
│   ├── feature_decomposition/
│   ├── feature_validation/
│   ├── bridge_features/
│   ├── steering_eval/
│   ├── creativity_benchmarks/
│   ├── controller_extensions/
│   ├── basin_dynamics/
│   └── figures/
├── scratch/
├── scripts/
│   └── download_reference_papers.py
├── sessions/
│   └── SESSION_TEMPLATE.md
├── validation/
│   └── __init__.py
└── tests/
```

## Research Navigation Guide

The source material is split across a transcript, an experiment landscape, a local-feasibility review, and a novelty audit. Do not re-read everything blindly every session.

### Always read first in a fresh session

1. `CURRENT_STATE.md`
2. `journal/current_state.md`
3. `SCRATCHPAD.md`
4. `THOUGHT_LOG.md`
5. `DECISIONS.md`
6. `history/PREREG.md`
7. `history/20260318-resattn-scaffold-adaptation.md`
8. `history/20260318-final-rigor-audit.md`

### Read by question

- What exactly are we trying to prove?
  - `research/transcript.md`
- Which experiment is most feasible and publishable on this machine?
  - `research/experiment-macbook-guide.md`
- What is novel versus derivative?
  - `research/experiment-novelty.md`
- What broader directions exist beyond the primary lane?
  - `research/experiment-ideas.md`

### Read only when needed

- `background-work/REFERENCES.md` when you need a paper or official URL
- `background-work/papers/DOWNLOAD_MANIFEST.md` when you need the local paper cache index
- `background-work/papers/files/*` when you need to read a locally cached paper directly
- `background-work/MECH_INTERP_GUIDANCE.md` when decomposition methods or evaluation choices feel shaky
- `background-work/GAPS_SYNTHESIS.md` when you need the short list of non-negotiables
- `background-work/SAFETY_PUBLICATION_POLICY.md` before writing anything that leans on refusal, sycophancy, or other safety-adjacent baselines

## Operating Rules

### 1. Document Discipline

Before starting a non-trivial work session:

1. Read `CURRENT_STATE.md`
2. Create or update a session log in `sessions/`
3. Confirm the next task against the active phase and prereg

During work:

- Update `SCRATCHPAD.md` before and after any substantial local run.
- Use `THOUGHT_LOG.md` for research reflections throughout the project. Record hunches, predictions, surprises, confidence shifts, and the current feel of the experiment when those would be useful later.
- Agents may launch bounded parallel sidecar work for literature review, benchmark checking, or methodological validation when it materially improves the experiment without blocking the critical path.
- Log non-obvious pivots in `DECISIONS.md` before proceeding.
- Update `CURRENT_STATE.md` whenever the actual project state changes.
- Register durable outputs in `results/RESULTS_INDEX.md`.

`THOUGHT_LOG.md` rules:

- This file is for research reflections, not claim-bearing evidence.
- It is the right place for hunches, predictions, guesses, interesting facts, surprising failures, qualitative impressions, and “I think this is going to break because...” notes.
- It should preserve the feel of the experiment as it unfolds, including confidence changes and competing hypotheses.
- Keep it high-signal and readable. Write concrete reflections, not filler.
- Label speculative content clearly enough that no one confuses it with validated findings.
- If sidecar research or parallel exploration turns up something useful, summarize the takeaway here or in a durable background-work note instead of letting it vanish.

Long-running process rules:

- Any run that is expensive enough to care about surviving laptop movement, terminal closure, or disconnects must run inside `tmux`.
- Long-running runs must save resumable checkpoints on a defined cadence.
- Before launch, record the `tmux` session name, checkpoint path, checkpoint cadence, log path, and resume command in `SCRATCHPAD.md`.
- After launch, verify that checkpoints are actually being written and that the resume command works against the latest checkpoint.
- Prefer durable checkpoint locations under the relevant `results/` lane rather than ephemeral temp directories.

Pre-run checkpoint format for `SCRATCHPAD.md`:

```text
## [TIMESTAMP] PRE-RUN: [run name]
- tmux session: [session name or N/A]
- Script: scripts/[filename].py
- Command: [exact command]
- Config: [key hyperparameters]
- What I'm testing: [one-sentence hypothesis]
- Expected outcome: [what success looks like]
- Expected duration: ~X minutes
- Checkpoint path: [path or N/A]
- Checkpoint cadence: [every N steps / minutes / epochs]
- Log path: [path]
- Resume command: [exact command]
- Main confound to watch: [one sentence]
- Implementation verified: YES/NO - [what independent check was run]
- Status: LAUNCHING
```

Post-run checkpoint format for `SCRATCHPAD.md`:

```text
## [TIMESTAMP] POST-RUN: [run name]
- Outcome: SUCCESS / FAILURE / PARTIAL
- Key metric: [the number that matters]
- Artifacts saved: [paths]
- Latest checkpoint: [path or none]
- Anomalies: [anything unexpected, or none]
- Next step: [what follows from this result]
```

### 2. Session Check-In Protocol

If context is thin or the session resumed after compaction:

1. Read `CURRENT_STATE.md`
2. Read the latest entries in `SCRATCHPAD.md`
3. Read the latest entries in `THOUGHT_LOG.md`
4. Read the latest entries in `DECISIONS.md`
5. Read the latest session log in `sessions/`
6. Check `results/RESULTS_INDEX.md`
7. Only then return to the research documents

Do not re-explore the whole repo if the state docs already answer the question.

### 3. The Research Documents Are the Spec

- `research/experiment-novelty.md` defines the novelty claim and the main methodological traps.
- `research/experiment-macbook-guide.md` defines the default local-feasibility stack.
- `research/transcript.md` defines the motivating problem and the broader conceptual target.
- `history/PREREG.md` defines what is pre-registered locally.
- If these documents conflict, resolve the conflict explicitly in `DECISIONS.md` before coding.

### 4. Execution Order

Use this as the default phase flow:

1. Phase 0: scaffold, prereg, runtime freeze, prompt freeze, and validation scaffolding
2. Phase 1: creativity-direction replication on the default local model
3. Phase 2: pilot comparison of signed decomposition methods, then confirm-method freeze
4. Phase 3: feature validation, output-feature filtering, and benchmark evaluation
5. Phase 4: cross-domain bridge-feature analysis plus comparisons against simpler behavioral baselines
6. Phase 5: optional controller-extension and basin-dynamics follow-ons
7. Phase 6: synthesis, writing, and artifact cleanup

Do not skip ahead to bridge claims or controller work until the direction-replication and decomposition gates are honestly cleared.

### 5. Experiment Design Defaults

- When a question is materially underspecified or multiple experimental approaches seem plausible, draft a short plan collaboratively with Sohail before execution.
- That plan should include the motivation, the concrete comparison or measurement, and a mock-up of the main plot or table using fake numbers if needed.
- Approved non-trivial new sprints should create or update a bd issue before execution so the work is visible to future sessions.
- Start with the smallest experiment that can genuinely falsify or support the idea. Do not scale up before the tiny version shows signs of life.
- Prefer tight feedback loops. A five-minute run is excellent, an hour is acceptable, and anything longer than a day requires explicit justification in `DECISIONS.md`.
- Treat most early-stage work as exploratory: the goal is often to gain surface area, expose unknown unknowns, and sharpen the ontology before expensive runs.
- Freeze a pilot/confirmatory split before claim-bearing prompt tuning, judge tuning, or method selection.
- Use parallel sidecar agents for bounded tangential work when helpful, especially for papers, tool caveats, and benchmark details that illuminate the main experiment without blocking it.

### 6. Run Design Guardrails

- Never naively encode a dense steering vector through an SAE and treat the coefficients as mechanistic evidence.
- Never ignore negative feature contributions. Suppressed features are part of the mechanism.
- Never rely on a single signed decomposition method if multiple plausible methods disagree on the pilot slice. Compare at least two before freezing the confirm path.
- Never promote an input feature to a creativity feature without output-facing intervention evidence.
- Never use judge-only creativity gains without at least one coherence, usefulness, or benchmark-based check.
- Never let cross-domain bridge claims rest on creative-writing style drift alone; use domain-breadth evidence and matched random controls.
- Never skip baseline comparisons to simpler behavioral concepts such as refusal or sentiment when making the "creativity is mechanistically different" argument.
- Never let extension lanes such as `controller_extensions` or `basin_dynamics` replace the primary creativity-direction decomposition result.
- Never run claim-bearing analysis on the same prompts used to tune the method. Use a pilot/confirmatory split for thresholds, prompt curation, and design choices.
- Never escalate away from the default `Gemma 2 2B + GemmaScope` local path without logging why the MacBook-feasible lane is insufficient.
- Never treat a negative result as experimental failure if it cleanly supports the thesis that creativity is more distributed or decomposition-resistant than simpler concepts.

### 7. Required Experiment Lanes

The following lanes must remain visible in `CURRENT_STATE.md`, `history/PREREG.md`, and `results/RESULTS_INDEX.md`:

- creativity-direction replication against frozen prompt splits
- signed feature decomposition
- feature validation with output-facing interventions
- benchmark-facing creativity and coherence evaluation
- cross-domain bridge-feature analysis
- baseline comparisons against simpler behavioral concepts
- optional controller-extension follow-up
- optional basin-dynamics follow-up

### 8. Results Registration

Every saved artifact belongs in `results/RESULTS_INDEX.md`.
Do not delete old entries; mark them superseded.

### 9. Experiment Write-Ups

Every non-trivial experiment should end with a concise technical write-up stored near the relevant artifacts. The default structure is:

- Motivation / Methods / Results / Limitations / Next Steps

The main figure or table should be easy to identify from a quick scan of the directory.

### 10. Branch Truth

- `main` is the canonical mainline branch for this repo.
- Completed work branches must be merged back into `main` so that branch remains the source of truth.
- In-progress work may remain on a task branch until the task is actually done. Do not force premature merges for work that is still active.
- Do not leave completed work stranded only on a WIP branch.

## Landing the Plane (Session Completion)

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   bd sync
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds
