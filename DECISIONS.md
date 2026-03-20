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

## [2026-03-18T11:48:00-0500] DECISION: Rebuild the pilot contrast around matched response pairs under a shared extraction wrapper

- Trigger: the template-control failure showed that the original instruction-template contrast was not a defensible proxy for creativity.
- Decision: keep the same WritingPrompts pilot prompts, but regenerate the positive and negative sides as model continuations from `Creative story` versus `Plain story` source prompts and rewrap both sides under the same `Story` extraction scaffold before hidden-state extraction.
- Rationale: the experiment claims to study a creativity-related behavioral contrast, not lexical differences between two prompt prefixes.
- Impact: the active pilot pair file now lives under `prompts/creative_direction_v2_*`, `scripts/run_creativity_direction_smoke.py` now supports row-provided positive/negative texts, and the controlled sweep logic now supports response-centered datasets.

## [2026-03-18T12:02:00-0500] DECISION: Treat layer 24 as a provisional late-layer candidate, not a frozen creativity mechanism

- Trigger: the response-centered `v2` controlled sweep recovered layer `24` as both the raw and controlled winner after the original instruction-template confound was removed.
- Decision: record layer `24` as the current best late-layer candidate and use it for bounded smoke-level follow-up, but require a calibration step before any decomposition or mechanistic claim treats it as settled.
- Rationale: a real but weak signal is better than a confounded win, but `19 / 32` pair separation is not strong enough to support decomposition by default.
- Impact: `creativedecomp-wtf` is closed, `creativedecomp-6lm` is now the critical-path task, and `creativedecomp-npt` remains blocked until the recovered direction is calibrated.

## [2026-03-18T12:44:00-0500] DECISION: Keep decomposition blocked after the v2 calibration sweep

- Trigger: the bounded `v2` calibration sweep and audit slice finished, and they did not show a stable enough late-layer creativity-control signal.
- Decision: close the calibration task as a completed negative gate, but do not unblock decomposition. Instead, create a new blocker to strengthen the response-centered contrast before rerunning layer selection and calibration.
- Rationale: the current `v2` direction recovered a layer candidate, but the coefficient-response behavior is not cleanly monotone and the audit slice shows that several strong losses come from pair-quality weakness rather than simple model noise.
- Impact: `creativedecomp-6lm` is closed, `creativedecomp-02c` is the new critical-path task, and `creativedecomp-npt` now depends on `creativedecomp-02c` instead of treating `v2` as decomposition-ready.

## [2026-03-18T13:00:00-0500] DECISION: Tighten Phase 1 around counterpart quality and an output-level gate before decomposition

- Trigger: the deep progress review found two remaining sources of optimism drift: the current `v2` pair construction is weaker than the Olson-style counterpart path in the research docs, and the issue graph still treated internal calibration as the last gate before decomposition.
- Decision: treat content-preserving creative/plain counterparts or audited rewrites as the preferred `v3` contrast target when feasible, and require a pilot output-level creativity/coherence gate before any Phase 2 decomposition work becomes ready.
- Rationale: a dense direction that only looks plausible in hidden-state probes is not yet the creativity object the thesis cares about, and a weak pair construction can make the experiment look more distributed than it really is.
- Impact: `creativedecomp-02c` now explicitly targets a stronger counterpart-style contrast, `creativedecomp-roq` exists as a new Phase 1 gate, and `creativedecomp-npt` remains blocked until both gates pass.

## [2026-03-18T14:40:00-0500] DECISION: Treat the landed `v3` contrast as a stronger negative gate and insert one bounded Olson-style extraction sensitivity before broader conclusions

- Trigger: the audited `v3` counterpart slice accepted `31 / 32` rows with high lexical overlap, but both the full-text and response-only sweeps still failed to recover a stable dense creativity direction, and both calibration branches remained non-monotone.
- Decision: close `creativedecomp-02c` as completed, keep `creativedecomp-roq` and `creativedecomp-npt` blocked, and make one bounded Olson-style mean-difference or CAA sensitivity the next ready task.
- Rationale: `v3` removes most of the old pair-quality excuses, so the next honest uncertainty is whether the extraction method is the last major mismatch to the strongest prior creativity-steering paper rather than whether decomposition or output gating should start anyway.
- Impact: the next ready task is now `creativedecomp-173`, not `creativedecomp-roq`, and a failure there will count as the first serious negative result for the Gemma 2 2B MacBook lane.

## [2026-03-18T15:00:00-0500] DECISION: Promote the full-text `mean_difference` v3 path to the primary Phase 1 dense-direction candidate

- Trigger: the bounded Olson-style extraction sensitivity recovered controlled winners on the landed `v3` slice, and the full-text `mean_difference` calibration is substantially cleaner than the failed PCA calibration.
- Decision: treat the full-text `mean_difference` path at layer `23` as the primary dense-direction candidate for the pilot output gate, use the `0.5` to `1.0` steering band as the bounded coefficient range to evaluate first, and keep the response-only `mean_difference` path as a diagnostic support lane rather than the main claim path.
- Rationale: the research review said the last major mismatch to Olson was the extraction method, and the new artifacts show that this mismatch was real. The full-text `mean_difference` path is the strongest recovered signal on the same data slice.
- Impact: `creativedecomp-173` can close, `creativedecomp-roq` becomes the next ready task, and decomposition remains blocked until the output-level gate runs on the recovered direction.

## [2026-03-18T16:02:00-0500] DECISION: Invalidate the single-order output-gate pass and keep decomposition blocked behind an order-robust metric follow-up

- Trigger: the first pilot output-gate artifact on the recovered full-text `mean_difference` direction looked weakly positive, but the secondary review found that the local judge chose story `A` on `152 / 155` creativity comparisons, which made the initial pass signal an order artifact rather than evidence.
- Decision: rerun the gate with order-robust paired judging that requires the same winner under both A/B orderings, treat the corrected artifact as the new source of truth, and keep decomposition blocked because the corrected gate collapses prompt-only versus neutral and dense versus neutral almost entirely to ties.
- Rationale: a gate that can be passed by label-order bias is not a real gate. The corrected artifact also shows that the current local creativity-side metric is too insensitive to distinguish even the prompt-only creativity baseline from neutral, so the next honest blocker is evaluation sensitivity rather than decomposition.
- Impact: `creativedecomp-roq` can close as a completed gate-definition task, `creativedecomp-8o1` is now the next ready follow-up, and `creativedecomp-npt` remains blocked until a stronger pilot creativity metric either recovers a real output-level effect or supports a clean negative-result write-up.

## [2026-03-18T16:18:00-0500] DECISION: The next evaluation follow-up must reuse cached gate outputs before any new generation or retuning

- Trigger: the deep post-gate review confirmed that the current bottleneck is evaluation sensitivity, not pair construction or hidden-state recovery, and the existing `creativedecomp-8o1` task was still broad enough to invite metric-shopping.
- Decision: force the next-step order to be: first a small blinded manual audit on the cached output-gate stories; then one stronger creativity-side pilot metric grounded in that audit and the evaluation papers; then a gate rerun on the same cached generated outputs. Do not generate new stories or retune layer `23` / coeffs `0.5` and `1.0` until that sequence is complete.
- Rationale: if we change the outputs and the metric at the same time, we lose the ability to tell whether the failure is in the dense direction, the evaluation setup, or both. Reusing the cached outputs keeps the next test falsifiable.
- Impact: `creativedecomp-8o1` is now a narrower and more trustworthy blocker, and any later negative conclusion about the Gemma 2 2B lane will be much harder to dismiss as evaluation drift.

## [2026-03-18T16:43:00-0500] DECISION: Treat the prompt-grounded-creativity rerun as the first strong Phase 1 negative result for the Gemma 2 2B lane

- Trigger: the cached-output follow-up required by `creativedecomp-8o1` is complete: a blinded manual audit weakly favored the prompt-only creativity baseline over neutral, and the stricter prompt-grounded-creativity rerun on the same cached stories also weakly recovered that baseline while still showing no dense effect versus neutral.
- Decision: close `creativedecomp-8o1`, keep `creativedecomp-npt` blocked, and treat the Gemma 2 2B MacBook lane as the first strong Phase 1 negative result rather than as an unresolved evaluation ambiguity.
- Rationale: the repo's own decision rule said that if a stronger metric can distinguish prompt-only creativity prompting from neutral but still shows no dense effect, the result becomes a strong negative for this lane. That condition is now met.
- Impact: the next task is no longer "fix the metric." It is to synthesize what this negative result means and choose one bounded next lane before any new implementation begins.

## [2026-03-18T16:55:00-0500] DECISION: Choose a matched refusal control as the next bounded lane before scaling models

- Trigger: the negative-result synthesis task compared the live follow-up options after the first strong Gemma 2 2B creativity negative result.
- Decision: make a matched refusal baseline on the same Gemma 2 `2B` stack the next task, and defer both a pure negative-result write-up and any model-scale sensitivity until after that control is run.
- Rationale: this choice gives the highest information gain for the novelty claim. A local simpler-concept control can show whether the current failure is creativity-specific or whether the whole `2B` steering stack is weak. Jumping straight to a larger model changes too much at once; stopping at a write-up now would leave the strongest "mechanistically different from refusal" framing under-supported.
- Impact: `creativedecomp-rcf` is now the next ready task, `creativedecomp-ty9` can close, and `creativedecomp-npt` stays blocked behind the matched refusal control.

## [2026-03-18T20:12:00-0500] DECISION: Escalate to bounded model-scale sensitivity after the refusal dense-control stays output-weak

- Trigger: the matched refusal baseline on Gemma 2 `2B` recovered a very strong hidden-state refusal direction but still failed to produce a clean dense output-level win under the pilot gate.
- Decision: close the refusal-baseline task as a mixed result, keep decomposition blocked, and make bounded model-scale sensitivity the next lane before any more 2B-specific decomposition work.
- Rationale: the refusal control changed the interpretation of the creativity negative result. Because the same base-model `2B` stack does not produce a clean dense output-level success case even on refusal, the strongest claim is no longer "creativity is uniquely distributed on this stack." The stronger reading is that dense output-level steering on this `2B` lane is broadly weak or prompt-sensitive, which makes a bounded scale-up the highest-information next step.
- Impact: `creativedecomp-rcf` can close, `creativedecomp-c4t` becomes the next ready task, and `creativedecomp-npt` remains blocked behind the scale sensitivity check.

## [2026-03-18T21:12:00-0500] DECISION: Treat the bounded Gemma 2 9B refusal check as evidence that scale alone does not rescue dense output-level control

- Trigger: Gemma 2 `9B` loaded successfully on the MacBook lane, the matched refusal layer sweep recovered a perfect hidden-state control at layer `18`, and the bounded output gate at coeff `0.5` still failed versus neutral.
- Decision: close `creativedecomp-c4t`, keep `creativedecomp-npt` blocked, and treat the current base-model dense-steering weakness as cross-scale rather than as a Gemma 2 `2B`-only issue.
- Rationale: the scale-up improved hidden-state extraction but not the causal output-side control claim. That makes "2B is just too small" a weaker explanation than before.
- Impact: the next honest move is synthesis, not decomposition. The follow-up task should decide whether to stop on a write-up-grade negative result, try an instruction-tuned or alternate-method control lane, or abandon dense base-model steering on the MacBook path.

## [2026-03-18T21:13:00-0500] DECISION: Record the 9B sampled-calibration slowdown as a real MacBook constraint and bound the claim-bearing gate accordingly

- Trigger: the full Gemma 2 `9B` sampled calibration grid on `mps` remained live but extremely slow; process sampling showed repeated waits inside MPS `multinomial` and copy synchronization rather than a transient bug.
- Decision: stop the broad 9B calibration grid and replace it with one bounded claim-bearing output gate at the gentlest previously viable coefficient (`0.5`) on the selected layer.
- Rationale: continuing the broad grid would spend large amounts of local time on sampled decoding overhead without changing the scientific question of `creativedecomp-c4t`, which is whether scale alone rescues a clean simpler-concept dense control effect.
- Impact: the 9B result remains scientifically useful and honestly bounded, and future sessions now know that full sampled calibration grids on this lane are a throughput risk rather than an invisible missing artifact.

## [2026-03-18T21:36:00-0500] DECISION: Stop more dense base-model steering sweeps and choose an alternate-method control lane on the same stack

- Trigger: the cross-scale synthesis after the Gemma 2 `2B` and bounded Gemma 2 `9B` refusal controls showed the same pattern: strong hidden-state extraction and weak dense output-side control.
- Decision: close the synthesis question by stopping further dense base-model steering sweeps on this MacBook lane and making the next bounded task an alternate-method control on the same Gemma 2 `2B` plus GemmaScope stack, starting with refusal and an SAE-aware effect-oriented or sparse intervention family.
- Rationale: a pure write-up stop would leave the strongest local method family from `SAE-TS`, `FGAA`, `SAS`, and output-feature filtering untested, while an instruction-tuned pivot would change model behavior, prompting regime, and likely SAE assumptions at the same time. The highest-information next step is to test whether the failure is specific to dense additive steering rather than broader than the intervention family.
- Impact: `creativedecomp-174` can close once the follow-up issue is filed, `creativedecomp-npt` stays blocked, and the repo should no longer spend time on more dense-vector sweeps unless a later decision explicitly reopens them.

## [2026-03-18T22:15:00-0500] DECISION: Treat the sparse SAE-latent refusal control as a failed alternate-method rescue and move back to synthesis

- Trigger: the bounded sparse SAE-latent refusal gate on Gemma 2 `2B` completed on the same refusal slice and still did not produce a clean output-level win versus neutral.
- Decision: close `creativedecomp-175`, keep `creativedecomp-npt` blocked, and make the next task a synthesis decision between a write-up-grade negative result for the local lane and one bounded instruction-tuned pivot.
- Rationale: the alternate-method control answered the main open question from the cross-scale synthesis. The simpler-concept failure is no longer just a dense-vector story, because it now survives a sparse SAE-latent intervention on the same stack. Continuing to try more base-model steering variants would now look like lane-shopping rather than disciplined falsification.
- Impact: the repo is back in a strategic-decision phase. The next honest move is not another base-model steering method; it is deciding whether the current local lane is exhausted enough to write up or whether one instruction-tuned pivot is still justified.

## [2026-03-18T22:35:00-0500] DECISION: Use one bounded instruction-tuned refusal pivot as the last pre-writeup sensitivity

- Trigger: `creativedecomp-176` synthesized the post-sparse-control base-model lane against the novelty and MacBook feasibility docs.
- Decision: do not stop at the base-model negative result yet. Run exactly one bounded instruction-tuned refusal pivot on a GemmaScope v2-backed instruction-tuned Gemma stack, choosing the smallest locally feasible paired checkpoint and SAE release inside the next task. If that pivot also fails, stop and write up the local steering lane as a negative result instead of shopping more regimes.
- Rationale: the current base-model lane is exhausted enough to rule out more base-model sweeps, but not enough to rule out the paper-backed regime dependence highlighted by dataset-dependent and chat-specific SAE evidence. The MacBook guide says GemmaScope v2 makes instruction-tuned Gemma stacks locally feasible, so one bounded pivot is still aligned with the original Gemma plus SAE thesis rather than a random escape hatch.
- Impact: `creativedecomp-176` can close, `creativedecomp-177` becomes the only ready task, `creativedecomp-npt` stays blocked, and a write-up-grade negative result becomes the default only if the instruction-tuned refusal pivot also fails.

## [2026-03-18T22:58:00-0500] DECISION: Freeze the instruction-tuned pivot to the smallest locally feasible GemmaScope v2-backed Gemma stack

- Trigger: `creativedecomp-177` required choosing one instruction-tuned regime without turning the task into a broad model search.
- Decision: freeze the pivot to `google/gemma-3-270m-it` plus `gemma-scope-2-270m-it-res`, using `layer_12_width_16k_l0_medium` as the reference SAE and the release-derived residual candidate layers `[5, 9, 12, 15]`.
- Rationale: this is the smallest paired instruction-tuned Gemma plus GemmaScope v2 stack that is locally feasible on the MacBook lane for chat generation, hidden-state extraction, control wrapping, and SAE loading.
- Impact: the instruction-tuned pivot stays bounded, reproducible, and aligned with the original Gemma plus SAE thesis instead of drifting into a broad instruction-tuned model comparison.

## [2026-03-18T23:00:00-0500] DECISION: Treat the failed instruction-tuned refusal pivot as the stop signal for steering-regime shopping

- Trigger: the final bounded instruction-tuned refusal pivot recovered perfect hidden-state refusal on `google/gemma-3-270m-it` but still failed the matched output gate. Prompt-only refusal versus neutral and both dense conditions versus neutral stayed `12 / 12` ties on refusal.
- Decision: close `creativedecomp-177`, keep `creativedecomp-npt` blocked, and treat the local steering lane as exhausted enough for a write-up-grade negative result rather than running more steering-regime variants.
- Rationale: the last paper-backed regime shift did not rescue the simpler-concept output claim. Continuing to try new steering regimes after dense, cross-scale, sparse SAE-latent, and instruction-tuned refusal controls would now look like regime shopping rather than disciplined falsification.
- Impact: the next honest task is synthesis and write-up framing, not more steering implementation. Any future reopening of the lane now requires a specific new confound or paper-backed reason, not generic optimism.

## [2026-03-18T23:30:00-0500] DECISION: Do not finalize the negative-result bundle before auditing the cached instruction-tuned refusal outputs

- Trigger: the deep post-pivot review found that the instruction-tuned refusal gate was being treated as final even though it had not received the same cached-output manual-audit treatment that the creativity gate required after judge brittleness surfaced there.
- Decision: keep steering-regime shopping closed, but insert one low-cost evaluation-side follow-up before the final write-up-grade negative result. Audit the cached instruction-tuned refusal outputs under a locked manual rubric, then freeze the narrowest truthful claim supported by that audit.
- Rationale: this preserves the stop on new steering regimes while still handling the last remaining evaluation-side confound honestly. The prompt-only instruction-tuned refusals are visibly different on some prompts, so collapsing straight to a final negative-result bundle without the cached-output audit would be one step too eager.
- Impact: `creativedecomp-178` remains the synthesis umbrella, `creativedecomp-179` becomes the next ready task, and `creativedecomp-npt` stays blocked. The stronger claim about creativity versus simpler concepts remains unearned until the local simpler-concept evaluation story is as rigorous as the creativity one.

## [2026-03-19T08:10:00-0500] DECISION: Treat the instruction-tuned refusal manual audit as a real claim-boundary correction, not as a footnote

- Trigger: `creativedecomp-179` completed the locked manual audit on the cached instruction-tuned refusal outputs from `results/steering_eval/20260318-gemma3-270m-it-refusal-output-gate-v1/`.
- Decision: reject the pre-audit "all ties, final negative result" reading. The repo now records that the manual audit recovers a clear prompt-only refusal baseline and modest dense refusal wins versus neutral on `google/gemma-3-270m-it`, while keeping decomposition blocked because that success is on an unmatched instruction-tuned stack rather than the active creativity pipeline.
- Rationale: once the cached-output manual audit corrected the judge-insensitive all-tie interpretation, freezing the old negative-result bundle would misstate the evidence. At the same time, overreading the new result as if it were a matched creativity control would be equally wrong.
- Impact: the local steering lane is no longer ready for a write-up-grade negative-result freeze. The next task is post-audit synthesis to choose one matched continuation, `creativedecomp-npt` remains blocked, and no new steering-regime shopping is reopened by default.

## [2026-03-19T08:30:00-0500] DECISION: Choose a bounded instruction-tuned creativity replication as the matched continuation

- Trigger: `creativedecomp-180` synthesized the corrected instruction-tuned refusal result against the novelty memo, prereg, and implementation grounding docs.
- Decision: the next implementation task is one bounded instruction-tuned creativity Phase 1 replication on the same `google/gemma-3-270m-it` plus `gemma-scope-2-270m-it-res` stack, not a write-up stop, not sentiment, and not another refusal-side lane.
- Rationale: the instruction-tuned refusal manual audit created the first local simpler-concept output-side steering success case. That changes the highest-information next step. The repo now needs the active creativity question on that same instruction-tuned stack so the comparison is finally regime-matched. Stopping now would leave the main novelty claim unresolved, while reopening decomposition now would still jump ahead of a matched creativity-side output gate.
- Impact: `creativedecomp-180` can close once the follow-up issue is filed, `creativedecomp-181` becomes the next ready task, and `creativedecomp-npt` remains blocked behind that bounded instruction-tuned creativity continuation.

## [2026-03-19T09:05:00-0500] DECISION: Treat the corrected instruction-tuned creativity manual audit as the first regime-matched creativity output-side effect, but keep decomposition blocked pending synthesis

- Trigger: `creativedecomp-181` corrected the malformed bare neutral prompt on the instruction-tuned creativity lane, reran the matched-stack pair builder, layer sweep, and output gate, then audited the cached outputs after the automatic judge again collapsed to story-`A` ties.
- Decision: reject the old matched-stack null read from the automatic gate. The live repo truth is now that the corrected instruction-tuned creativity lane on `google/gemma-3-270m-it` plus `gemma-scope-2-270m-it-res` recovers a bounded dense output-side effect at layer `12`, coeff `1.0`, versus neutral under a locked manual audit. Do not reopen decomposition automatically from that fact alone; first run a synthesis task to decide whether Phase 2 should pivot onto this same instruction-tuned stack or require one narrower confirmatory follow-up.
- Rationale: once the neutral harness is corrected, the pair set quality improves materially (`18 / 32` accepted instead of `6 / 32`) and the cached manual audit recovers a real dense creativity effect on the same stack where refusal also works. That removes the old unmatched-stack objection. But prompt-only creativity versus neutral is still roughly tied, and the automatic judge remains unusable, so jumping straight into decomposition would still skip the claim-boundary synthesis the repo requires after a major regime change.
- Impact: `creativedecomp-181` can close, `creativedecomp-182` becomes the next ready task, and `creativedecomp-npt` remains blocked behind that synthesis rather than reopening immediately.

## [2026-03-19T09:25:00-0500] DECISION: Open a bounded Phase 2 pilot on the matched instruction-tuned stack, while keeping confirmatory evaluation gated

- Trigger: `creativedecomp-182` compared the prereg Phase 1 gate, the novelty memo, the MacBook guide, and the matched instruction-tuned refusal and creativity manual audits.
- Decision: reopen Phase 2 as a bounded pilot on `google/gemma-3-270m-it` plus `gemma-scope-2-270m-it-res`. `creativedecomp-npt` should now run on that matched instruction-tuned stack. Do not require another generic creativity steering follow-up before pilot decomposition. At the same time, do not upgrade the broader claim boundary: claim-bearing evaluation and later feature-validation claims remain gated on a stronger judge path or additional locked manual audits plus the prereg benchmark work.
- Rationale: the prereg requires a bounded output-level creativity effect with a coherence or usefulness check before Phase 2 opens. The matched instruction-tuned creativity manual audit now satisfies that minimum pilot gate, and it does so on the same stack where refusal already has a manual-audit-supported output-side effect. Forcing one more generic creativity gate would be Phase 1 drift rather than better science. But the automatic creativity judge is still unusable, prompt-only creativity remains roughly tied with neutral, and the default MacBook thesis still centers `google/gemma-2-2b` plus GemmaScope `65K`. So the honest move is a temporary pilot pivot, not a full thesis rewrite.
- Impact: `creativedecomp-182` can close, `creativedecomp-npt` becomes the next ready task, and evaluation hardening should be tracked as explicit follow-up work rather than silently assumed solved.

## [2026-03-19T16:34:00-0500] DECISION: Treat feature-validation simulated annotations as triage-only and require locked manual replacement for any claim

- Trigger: the bounded feature-validation pilot completed, and the next step was to compare `positive_feature_3222`, `negative_feature_16008`, and `bundle_feature_group` against `dense_direction` without waiting on a full manual pass.
- Decision: generate a blinded feature-validation audit packet and run a simulated heuristic annotation pass to rank conditions quickly, but explicitly mark the result as non-claim-bearing and require locked manual annotations before interpretation upgrades.
- Rationale: this preserves momentum and helps prioritize where manual effort should focus, while preventing metric drift or accidental overclaiming from heuristic labels.
- Impact: a new triage artifact now exists at `results/feature_validation/20260319-gemma3-270m-it-feature-validation-v1-manual-audit/`, and `creativedecomp-183` remains the next ready blocker for claim-bearing evaluation hardening.

## [2026-03-19T16:36:00-0500] DECISION: Close `creativedecomp-npt` and shift active focus to `creativedecomp-183`

- Trigger: `bd` still had `creativedecomp-npt` open even though the signed method comparison and pilot freeze artifacts were already complete.
- Decision: close `creativedecomp-npt` in issue tracking and treat `creativedecomp-183` as the only ready issue.
- Rationale: the decomposition-method-comparison objective is complete and documented; leaving it open obscures the real critical-path blocker.
- Impact: `bd ready` now surfaces `creativedecomp-183` as the next active task, aligning issue tracking with the lived experimental state.

## [2026-03-20T10:48:00-0500] DECISION: Treat rubric-based automatic judging as hardened but still non-usable for claim-bearing creativity evaluation

- Trigger: `creativedecomp-183` added and ran a cached-output rubric re-evaluator (`scripts/evaluate_instruction_tuned_creativity_output_gate_rubric_v1.py`) on `results/steering_eval/20260319-gemma3-270m-it-output-gate-v1/`, with bidirectional score-per-story judging, parse robustness, and explicit judge-health checks.
- Decision: keep this rubric path as the default automatic diagnostic evaluator, but do not treat its outputs as claim-bearing on the current instruction-tuned creativity gate artifact.
- Rationale: parse robustness improved to `1.000000`, but judge health still collapses: both axes reduce to constant score `1.0` and all comparisons tie. This confirms that stronger parsing alone does not rescue the local automatic judge.
- Impact: `creativedecomp-183` can close as completed evaluation hardening; claim-bearing interpretation remains manual-audit-gated.

## [2026-03-20T10:49:00-0500] DECISION: Open `creativedecomp-602` as the next ready blocker for claim-bearing feature validation

- Trigger: after closing `creativedecomp-183`, the feature-validation audit under `results/feature_validation/20260319-gemma3-270m-it-feature-validation-v1-manual-audit/` still relied on simulated heuristic annotations.
- Decision: create `creativedecomp-602` to replace simulated annotations with locked manual rubric annotations before any feature-level claim upgrades.
- Rationale: with both automatic judge paths explicitly failing as claim-bearing creativity evaluators on this stack, manual annotation quality and locking now dominate evidence quality.
- Impact: `bd ready` now points to `creativedecomp-602` as the highest-priority next task.

## [2026-03-20T10:56:00-0500] DECISION: Close `creativedecomp-184` and keep only `creativedecomp-602` ready

- Trigger: issue tracking still had `creativedecomp-184` open even though the bounded feature-validation pilot artifact and write-up were already landed.
- Decision: close `creativedecomp-184` with the completed-pilot reason and keep `creativedecomp-602` as the single ready claim-bearing blocker.
- Rationale: leaving the completed pilot open obscures the actual evidence-quality blocker and can cause accidental task thrash.
- Impact: `bd ready` now returns one item, `creativedecomp-602`, matching the current experiment-critical path.

## [2026-03-20T11:10:00-0500] DECISION: Replace simulated feature-validation annotations with locked rubric pass and keep single-rater boundary explicit

- Trigger: `creativedecomp-602` required replacing simulated feature-validation triage labels with locked manual rubric annotations in `results/feature_validation/20260319-gemma3-270m-it-feature-validation-v1-manual-audit/`.
- Decision: overwrite the audit summary from a locked annotation file (`manual_annotations_locked_v1.jsonl`) and treat the resulting ranking as the active feature-validation read, while explicitly labeling it as single-rater.
- Rationale: this removes the strongest immediate evidence-quality weakness (simulated labels) without pretending that one rater is enough for publication-grade confidence.
- Impact: active feature-validation summary now comes from locked annotations (not simulated triage), `creativedecomp-602` can close, and independent second-rater agreement becomes the next blocker.

## [2026-03-20T11:11:00-0500] DECISION: Open `creativedecomp-yga` for independent second-rater confirmation

- Trigger: the locked single-rater feature-validation summary is now in place, but stronger claims still require rater-agreement evidence.
- Decision: create `creativedecomp-yga` to run an independent second-rater pass on the same blinded packet and report inter-rater agreement before stronger claim language.
- Rationale: this keeps the claim boundary honest while preserving momentum and methodological rigor.
- Impact: `creativedecomp-yga` becomes the next ready task after `creativedecomp-602`.

## [2026-03-20T11:22:00-0500] DECISION: Record two-rater agreement for feature-validation manual audit and promote benchmark confirmation as next blocker

- Trigger: `creativedecomp-yga` added a second locked rater and agreement computation under `scripts/compute_feature_validation_inter_rater_agreement.py`, producing `inter_rater_agreement.json` and embedding metrics in the manual-audit summary.
- Decision: accept the feature-validation manual audit as two-rater pilot evidence with explicit agreement (`0.833` / kappa `0.710` for prompt-grounded creativity; `0.944` / kappa `0.894` for coherence), then move the critical path to prereg benchmark-family confirmation.
- Rationale: agreement is strong enough to retire the single-rater confound, but pilot-slice manual judgments alone are still insufficient for stronger publication-grade claims.
- Impact: `creativedecomp-yga` can close and `creativedecomp-tu6` becomes the next ready issue.

## [2026-03-20T11:45:00-0500] DECISION: Treat the first two-family benchmark confirmation pass as a failed generalization gate and pivot to root-cause analysis

- Trigger: `creativedecomp-tu6` ran two benchmark families beyond the `18`-pair pilot slice on the matched instruction-tuned stack with locked bundle-vs-dense rubric audits (`10` pairs per family; `20` total).
- Decision: close `creativedecomp-tu6` as completed execution, but record the prereg benchmark-family confirmation gate as not met. The pilot bundle-over-dense pattern does not generalize in this first pass.
- Rationale: in the association/divergent family, bundle-vs-dense net wins are `-0.200` on prompt-grounded creativity and `-0.100` on coherence; in the writing/diversity family, net wins are `-0.300` on creativity and `0.000` on coherence. This is direct disconfirmation of the pilot-slice ranking as a generalized claim.
- Impact: stronger feature-level claim language remains blocked; `creativedecomp-e4p` is now the next ready task to diagnose prompt-family shift, feature selection stability, and steering-scale sensitivity before any corrective rerun.

## [2026-03-20T13:26:00-0500] DECISION: Coefficient-only rescue is insufficient; queue prompt-family-matched bundle refresh as the minimum corrective experiment

- Trigger: `creativedecomp-e4p` completed bounded dropoff diagnostics plus a locked coeff-`0.5` sensitivity pass on both benchmark families.
- Decision: close `creativedecomp-e4p` as completed analysis and do not treat lower coefficient alone as a fix. Move next to a prompt-family-matched signed-bundle refresh experiment with locked audits at coeffs `0.5` and `1.0`.
- Rationale: lowering coeff from `1.0` to `0.5` gave only partial, non-general rescue (writing/diversity creativity net win `-0.300 -> -0.200`; association/divergent `-0.200 -> -0.300` with worse coherence). Diagnostic metrics also show bundle prompt grounding is lower and repetition is higher than dense in both families, which points to transfer/feature-selection mismatch rather than one global scale bug.
- Impact: `creativedecomp-e4p` can close, `creativedecomp-0jl` is now the next ready corrective task, and feature-level claim upgrades remain blocked until benchmark-family confirmation recovers.

## [2026-03-20T14:20:00-0500] DECISION: Prompt-matched refresh gives mixed family recovery; require independent human rerating before next corrective move

- Trigger: `creativedecomp-0jl` completed the prompt-family-matched selector refresh and four benchmark reruns (`coeff=1.0` and `0.5` on writing/diversity and association/divergent).
- Decision: close `creativedecomp-0jl` as executed corrective work, but do not treat current refresh summaries as claim-bearing because they are heuristic-locked. Open `creativedecomp-d1j` for independent human rerating and post-rerating synthesis.
- Rationale: refreshed coeff `1.0` partially recovers writing/diversity (`+0.100` creativity net win; `+0.200` coherence net win) but remains strongly negative on association/divergent (`-0.300`, `-0.500`). Refreshed coeff `0.5` does not provide consistent rescue across families either. This is informative but still sensitive to audit-label quality.
- Impact: benchmark-family confirmation remains not met; the next critical path is annotation-quality hardening on refresh artifacts plus decision on whether to retune selection or freeze a negative transfer interpretation.
