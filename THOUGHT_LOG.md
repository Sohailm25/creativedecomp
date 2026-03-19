# Thought Log

Research reflections for the mechanistic creativity experiment.

Purpose:

- capture the qualitative feel of the experiment as it unfolds
- preserve hunches, predictions, guesses, and competing hypotheses
- note surprises, tensions, weird facts, and confidence shifts
- leave behind a readable reflective trail for the end-of-project write-up

Important rule:

- entries here are not claim-bearing evidence
- use this file for research reflections, intuitions, and interesting facts
- validated conclusions still belong in `CURRENT_STATE.md`, `DECISIONS.md`, run artifacts, and the prereg-aware result docs

Suggested entry format:

```text
## [TIMESTAMP] [short title]
- Stage: [planning / implementation / analysis / synthesis]
- Feel of the Experiment: [1-3 sentences]
- Working Hypotheses:
  - [hypothesis]
- Hunches and Guesses:
  - [guess]
- Predictions:
  - [what I think will happen]
- Surprises and Tensions:
  - [unexpected fact or inconsistency]
- Confidence:
  - [low / medium / high] in [what]
- Interesting facts:
  - [paper fact, implementation detail, or pattern worth remembering]
```

## Working Hypotheses

- [ ] A creativity direction can be recovered reliably on a small open model using a frozen prompt split.
- [ ] The direction decomposes into a limited set of SAE features rather than pure diffuse noise.
- [ ] At least some top creativity-aligned features are cross-domain bridge features rather than genre-only features.
- [ ] Output-feature filtering will matter more than raw alignment scores.
- [ ] Feature-level steering will be more interpretable than the dense direction even if it is weaker.

## Hunches and Guesses

- The biggest failure mode is mistaking stylistic looseness for creativity.
- The second biggest failure mode is clean but invalid SAE decomposition caused by signed-feature loss.
- The strongest paper path probably comes from explaining why creativity is harder to steer than refusal or sentiment, not from claiming an all-purpose creativity controller.

## Feel of the Experiment

- The experiment looks strongest when it stays narrow and mechanistic.
- The broader controller ideas are exciting, but they currently feel more like follow-on work than the first publishable result.

## Predictions

- The first decomposition pass will be messier and less sparse than refusal-style feature decompositions.
- Cross-domain bridge evidence will probably appear before a single canonical "creativity feature" does.

## Surprises and Tensions

- The underlying tooling is mature enough that the main risk is experimental honesty, not raw feasibility.
- The creativity literature and SAE literature are close enough to connect, but nobody seems to have actually done the connection cleanly.

## Interesting Facts

- The feasibility review strongly favors `Gemma 2 2B + GemmaScope` as the MacBook path.
- The novelty review makes naive direct SAE encoding of steering vectors look methodologically indefensible.

## [2026-03-18T10:08:00-0500] First Runtime Freeze Landed

- Stage: implementation
- Feel of the Experiment: The project finally feels like an experiment instead of a scaffold. The first real risk is no longer "can this repo stay organized?" but "does the frozen stack actually let us recover a creativity direction honestly?"
- Working Hypotheses:
  - The first blocked step is more likely to be model access or generation throughput than package compatibility.
- Hunches and Guesses:
  - If the first smoke run fails, the failure will probably come from Gemma access or the creativity contrast construction rather than the SAE tooling itself.
- Predictions:
  - The frozen WritingPrompts slice will be good enough for the first direction smoke, but not yet good enough to support the final benchmark claim on its own.
- Surprises and Tensions:
  - Python `3.14.2` was less of a blocker than expected for the base stack.
  - Optional steering packages already want a different `transformers` line, so environment discipline is going to matter early.
- Confidence:
  - medium in the frozen runtime
  - low-to-medium in immediate model-access smoothness
- Interesting facts:
  - `repeng` imported cleanly on the frozen stack, which is enough to start the first bounded creativity-direction replication slice without adding more tooling.

## [2026-03-18T10:40:00-0500] First Dense Creativity Smoke Is Alive But Not Clean Enough To Overinterpret

- Stage: implementation
- Feel of the Experiment: This is the first point where the research question touches the actual model instead of the plan. The result feels encouraging as an execution checkpoint and underwhelming as evidence, which is exactly the kind of distinction the repo needs to preserve.
- Working Hypotheses:
  - Layer 12 may be usable as a baseline extraction site but is not obviously the cleanest creativity layer on this model.
- Hunches and Guesses:
  - The interesting signal is not that the default layer works, but that it only separates `23 / 32` training pairs despite being trained on them.
- Predictions:
  - A small layer sweep will probably find stronger separation than the scaffold-default layer.
  - The first generation-side smoke may expose that some of the current contrast is style control rather than deeper creativity.
- Surprises and Tensions:
  - The main numerical instability was in the projection math path, not the model itself.
  - A bounded smoke artifact can succeed and still argue against complacent "we already replicated it" language.
- Confidence:
  - high in the local runtime path
  - low in any strong interpretation of the current layer-12 metric
- Interesting facts:
  - Switching from BLAS-backed matrix multiply to explicit multiply-plus-sum removed the projection warnings without changing the metric.

## [2026-03-18T11:05:00-0500] The Prompting Channel Is Still Louder Than The Creativity Claim

- Stage: implementation
- Feel of the Experiment: This is the useful kind of annoying. The repo is doing its job because the artifacts are surfacing confounds early enough to fix, instead of letting them fossilize into a paper-shaped story.
- Working Hypotheses:
  - Layer `0` is mostly detecting template wording, not a mechanistic creativity variable.
  - The base Gemma prompt harness is still too continuation-like to serve as a credible steering evaluation setup.
- Hunches and Guesses:
  - Once the prompt format is made continuation-compatible, the apparent gap between layer `0` and layer `7` will shrink or flip.
- Predictions:
  - A better story scaffold will make the generation-side differences easier to interpret than any extra steering coefficient sweep would right now.
- Surprises and Tensions:
  - The cleanest layer on the pilot objective was the least believable mechanistically.
  - The first generation smoke was informative precisely because it failed to produce the kind of outputs we wanted.
- Confidence:
  - high that the current layer-`0` result is confounded
  - medium that layer `7` is the right later-layer candidate to carry forward
- Interesting facts:
  - The neutral prompt and the prompt-only creativity prompt both elicited writing-forum/meta continuations from the base model, which means prompt-format repair is a real prerequisite rather than polish.

## [2026-03-18T11:36:00-0500] One Confound Is Gone, The Other Just Got Stronger

- Stage: implementation
- Feel of the Experiment: This is better than a fake win. The steering harness is now credible enough to use, and the layer-selection path is less comfortable because the control says the current contrast is still not honest enough.
- Working Hypotheses:
  - The current instruction-pair extraction setup is mostly teaching the model to distinguish prompt wording, not creativity as a stable mechanism.
  - A more tightly matched creativity-vs-plain continuation contrast may still recover a usable later-layer direction.
- Hunches and Guesses:
  - The next real progress is more likely to come from redesigning the extraction prompt pair than from more steering sweeps on the current layer set.
- Predictions:
  - If a revised contrast survives the template control, the surviving layer will be later than `0` and possibly later than `7`.
- Surprises and Tensions:
  - The generation harness fix worked cleanly and quickly, but the layer-control result became harsher rather than softer once measured honestly.
  - Very low cosine with the template-control direction at some later layers did not rescue them, because the template-control projections still separated the pairs too well.
- Confidence:
  - high that the generation harness is now fit for smoke-level evaluation
  - high that no current layer should be frozen from the existing instruction-template contrast
- Interesting facts:
  - The template-only control achieved `1.0` positive-greater-than-negative fraction at layers `0`, `7`, `9`, `15`, `20`, and `25`, which is strong evidence that prompt-template leakage remains dominant in the current extraction setup.

## [2026-03-18T12:05:00-0500] The Structural Fix Worked, But The Signal Is Still Fragile

- Stage: implementation
- Feel of the Experiment: This is the right kind of partial recovery. The repo is no longer trying to learn "creative wording versus plain wording," but the rescued late-layer direction is still weak enough that it would be easy to oversell it.
- Working Hypotheses:
  - The `v2` response-centered redesign recovered a real late-layer behavior signal that the instruction-template setup had buried.
  - The remaining weakness is more about pair quality and steering-scale calibration than about total absence of a creativity-related direction.
- Hunches and Guesses:
  - A small pair audit will show that some of the `13 / 32` failures are mediocre or ambiguously "plain" negative examples rather than pure model noise.
  - If the direction is real, a bounded scale sweep will probably sharpen visible differences before any SAE decomposition does.
- Predictions:
  - Decomposition attempted now would mostly teach us that weak dense directions decompose badly, which is true but not the central claim we need first.
  - Late layers in roughly the `18` to `24` band will remain more plausible than the early layers once calibration is finished.
- Surprises and Tensions:
  - Removing the template-control signal entirely did not produce a strong direction; it produced an honest but modest one.
  - The `v2` generation smoke did not collapse or look fake, but it also did not produce an obvious steering win.
- Confidence:
  - high that the `v2` redesign is methodologically better than `v1`
  - medium that layer `24` will survive a bounded calibration step strongly enough to justify decomposition
- Interesting facts:
  - The top five `v2` layers by the controlled rule are all late layers and all share the same `0.593750` pair-separation fraction, which feels more like a weak distributed band than a single canonical creativity site.

## [2026-03-18T12:44:30-0500] Calibration Was Honest, And The Honest Answer Is Still No

- Stage: analysis
- Feel of the Experiment: This is a useful refusal, not a dead end. The response-centered redesign rescued the experiment from a structural confound, but the next gate exposed that the rescued signal is still not disciplined enough for feature work.
- Working Hypotheses:
  - The main weakness is pair quality and contrast sharpness more than total absence of a late-layer creativity-relevant variable.
  - Some of the current dense-direction instability is caused by positive completions that are generic rather than distinctly more creative.
- Hunches and Guesses:
  - An audited `v3` pair set with rejection rules will matter more than more coefficient sweeps on the current `v2` direction.
  - Response-only probing may end up being a cleaner calibration diagnostic than full prompt-plus-response probing once the pair set is rebuilt.
- Predictions:
  - If the pair set is tightened, the late-layer band will probably remain late, but the ranking will compress less and the coefficient-response pattern will get easier to read.
  - If a tightened pair set still fails, that will be much stronger evidence against fast decomposition than the current `v2` failure is.
- Surprises and Tensions:
  - The top recovered layer survived the control sweep but still did not behave cleanly under coefficient scaling.
  - The pair audit is awkward in exactly the right way: several "plain" negatives are not low-quality junk, which means the experiment still has to earn a better contrast.
- Confidence:
  - high that decomposition should remain blocked
  - medium that a cleaner `v3` pair set can recover a usable dense direction
- Interesting facts:
  - On the bounded calibration slice, the unsteered neutral baseline had a more positive mean layer-24 probe projection than most of the positive-coefficient steering conditions, which is a strong sign that the current `v2` direction is not yet a stable control handle.

## [2026-03-18T13:02:00-0500] The Hidden Drift Was Treating Internal Recovery As Enough

- Stage: synthesis
- Feel of the Experiment: The repo has been honest about failures, but the phase order was still one step too eager. We had started acting as if "cleaner contrast plus internal calibration" would be enough to reopen decomposition, and that is weaker than both the prereg and the novelty framing.
- Working Hypotheses:
  - A better `v3` pair set should look more like Olson-style counterparts than two independently sampled stories with different stylistic instructions.
  - The real handoff to Phase 2 should be output-level behavior, not hidden-state plausibility alone.
- Hunches and Guesses:
  - If the dense direction cannot clear an output-level pilot gate after a stronger counterpart-style contrast, that negative result will be much more meaningful than the current `v2` failure.
- Predictions:
  - Tightening pair construction and forcing a pilot output gate will slow the repo down in the short term but make any eventual decomposition result more novel and much harder to dismiss.
- Surprises and Tensions:
  - The prereg already implied this stricter order, but the issue graph and immediate-next-step language had drifted toward a looser interpretation.
- Confidence:
  - high that the revised gate order is more faithful to the original experiment path
  - medium that the model will still yield a usable dense direction after the stronger gate
- Interesting facts:
  - The current weak point is not tooling anymore; it is whether the data construction and gating discipline are strong enough to keep "mechanistic creativity" from collapsing into "mechanistic style control."

## [2026-03-18T13:12:00-0500] The Papers Suggest A Narrower Success Criterion Than My Intuition Wanted

- Stage: synthesis
- Feel of the Experiment: The literature is useful here because it trims both optimism and perfectionism. It says our current gate is too weak if it only trusts hidden-state movement, but it also says the next gate should not demand that steering already beat prompting at everything.
- Working Hypotheses:
  - A dense creativity direction can still be mechanistically interesting even if prompt-only creativity remains stronger on average in pilot evaluation.
  - What matters first is whether the direction causes a measurable output effect with an honest tradeoff profile.

## [2026-03-18T21:15:00-0500] Scale Helped The Hidden State But Not The Causal Story

- Stage: analysis
- Feel of the Experiment: This is clarifying in a harsher way than I expected. The 9B model removes one easy excuse, but it does not give the clean dense-control win that would reopen the feature path.
- Working Hypotheses:
  - The hidden-state extraction method is not the main weakness on the refusal control anymore.
  - The bigger issue is the base-model dense-steering plus sampled-decoding lane itself, not just 2B capacity.
- Hunches and Guesses:
  - If we keep pushing this exact base-model dense-steering lane, the next result is more likely to be another honest negative than a rescue.
  - An instruction-tuned control or a different causal intervention method would be more informative than one more near-identical base-model sweep.
- Predictions:
  - The strongest next step is synthesis and lane selection, not decomposition.
  - If we do continue experimentally, the next good control will probably change either model regime or intervention method, not just scale.
- Surprises and Tensions:
  - Gemma 2 `9B` is feasible locally for hidden-state work, which is encouraging.
  - Gemma 2 `9B` generation on MPS still pays a painful sampled-decoding cost, and the cleaner hidden-state control still does not become a clean dense output effect.
- Confidence:
  - high that decomposition should remain blocked
  - medium-to-high that "2B was just too small" is no longer the right primary explanation
- Interesting facts:
  - Process sampling during the 9B calibration attempt showed the main thread spending its time in synchronous MPS `multinomial` and copy waits, which makes broad sampled calibration grids a real MacBook constraint on this lane.
- Hunches and Guesses:
  - If `v3` works, the strongest early result may be "steering has a distinct effect with different failure modes than prompting," not "steering is simply better than prompting."
- Predictions:
  - Forcing the pilot gate to compare against prompting without requiring superiority will keep the experiment more truthful and less likely to die on an unnecessary bar.
- Surprises and Tensions:
  - AxBench is a good reminder that many steering methods lose to prompting on average, which means "beats prompting" is the wrong default pilot criterion.
- Confidence:
  - high that the new pilot gate should be effect-and-tradeoff focused, not supremacy focused
- Interesting facts:
  - Von Rütte weakens hidden-state optimism, and AxBench weakens benchmarking optimism in almost the opposite direction; together they give a more realistic gate than either paper alone.

## [2026-03-18T14:42:00-0500] V3 Fixed The Data Problem Better Than It Fixed The Direction Problem

- Stage: synthesis
- Feel of the Experiment: This feels like progress because it narrowed the ambiguity, even though the answer is still no. The pair construction got much cleaner, but the direction did not get cleaner with it.
- Working Hypotheses:
  - The automatic counterpart rewrite is now good enough to weaken the old content-drift excuse substantially.
  - The biggest remaining phase-1 uncertainty is whether PCA-on-differences is the wrong extraction object for this contrast on Gemma 2 2B.
- Hunches and Guesses:
  - If an Olson-style mean-difference or CAA extraction also fails on the same `v3` slice, the MacBook lane probably deserves a real negative-result write-up before any broader escalation.
  - If that sensitivity works materially better, then the current failure mode is more about method mismatch than about creativity being absent or fully diffuse.
- Predictions:
  - The next bounded sensitivity will matter more than adding more pair heuristics or more calibration coefficients.
- Surprises and Tensions:
  - `v3` achieved mean counterpart overlap above `0.9`, yet the best raw fractions still stayed below `0.4`.
  - The creative prompt baseline is not obviously cleaner or stronger than neutral prompting on this stack, which makes the base model feel weaker for this thesis than I wanted.
- Confidence:
  - high that decomposition should remain blocked
  - medium that a bounded Olson-style extraction sensitivity is the right last serious Phase 1 check
- Interesting facts:
  - The full-text `v3` sweep lands on layer `6`, while the response-only view shifts to layer `22`, which is exactly the kind of view-dependence that should stop us from pretending we have a settled creativity direction.

## [2026-03-18T15:03:00-0500] The Extraction Method Mismatch Was Real

- Stage: synthesis
- Feel of the Experiment: This is the first time in a while that the experiment got stricter and stronger at the same time. The data did not change, but the phase picture did.
- Working Hypotheses:
  - The Olson-style `mean_difference` path is much closer to the right Phase 1 object on this stack than PCA-on-pair-differences.
  - The full-text view is the primary claim path now, while the response-only view is useful but still weaker.
- Hunches and Guesses:
  - The output gate now has a real chance to pass on the full-text `mean_difference` path.
  - If the output gate still fails after this rescue, that negative result will be much more meaningful than any of the earlier failures.
- Predictions:
  - Layer `23` with a coefficient in the `0.5` to `1.0` band will be the best candidate for the next pilot evaluation.
- Surprises and Tensions:
  - The same `v3` slice went from no controlled winner under PCA to a clear controlled winner under `mean_difference`, which is a larger method effect than I expected.
  - The response-only path also improved, but not enough to make the view-dependence disappear.
- Confidence:
  - high that `creativedecomp-roq` is now the right next task
  - medium that the recovered direction will translate cleanly into output-level gains
- Interesting facts:
  - Full-text layer `23` moves from `15.27` unsteered to `26.42` at coeff `0.5` and `34.47` at coeff `1.0`, then collapses at coeff `2.0`, which looks like a bounded useful regime rather than random behavior.

## [2026-03-18T16:04:00-0500] The Judge Was Weaker Than The Direction

- Stage: synthesis
- Feel of the Experiment: The first output-gate result looked barely positive, but the second look was more important than the first number. The gate did not really fail because steering obviously does nothing; it failed because the local judge was not strong enough to be trusted without order controls.
- Working Hypotheses:
  - The dense direction may still have a weak real output effect, but the current local pairwise metric cannot separate that effect from order bias and general indecision.
  - If a stronger bounded metric still cannot distinguish prompt-only creativity prompting from neutral, then the MacBook lane becomes much closer to a clean negative result.
- Hunches and Guesses:
  - The right next step is not decomposition and not another hidden-state sweep. It is a tighter pilot creativity metric or manual audit slice that can discriminate obvious prompting differences before it is asked to judge dense steering.
- Predictions:
  - Order-robust judging will collapse most current comparisons to ties whenever the local judge is dominated by positional preference.
  - The next meaningful signal will come from improving the metric, not from slightly retuning the same layer-23 coefficients.
- Surprises and Tensions:
  - The first single-order gate recommended `True`, but almost all of that signal disappeared as soon as the judge had to agree under both A/B orderings.
  - Even the prompt-only creativity baseline versus neutral collapsed to ties, which means the evaluation bottleneck is now stronger than I expected.
- Confidence:
  - high that decomposition must remain blocked
  - medium that a bounded stronger local metric can still rescue Phase 1 without escalating the stack
- Interesting facts:
  - Under order-robust judging, prompt-only versus neutral is `31 / 31` ties on both creativity and coherence, and dense versus neutral is also `31 / 31` ties for both tested coefficients.

## [2026-03-18T16:19:00-0500] The Next Risk Is Metric-Shopping, Not Just Metric Weakness

- Stage: synthesis
- Feel of the Experiment: The repo is now at a subtle fork. The danger is no longer “we might naively decompose a bad direction.” The danger is “we might keep changing the evaluation setup until something looks positive.”
- Working Hypotheses:
  - Some of the cached output-gate stories do look meaningfully different by eye, especially prompt-only versus neutral on a subset of prompts.
  - That means the next step should begin by testing metric sensitivity on the existing outputs, not by regenerating better-looking stories.
- Hunches and Guesses:
  - A small blinded manual audit with a tighter rubric will probably show that the current local label judge is under-sensitive rather than that every condition is truly indistinguishable.
  - If even a human-rubric audit cannot separate prompt-only from neutral on the cached outputs, then the stack is in worse shape than the hidden-state recovery made it appear.
- Predictions:
  - Reusing cached outputs will make the next conclusion much cleaner: either the metric improves and isolates the dense failure, or the metric still fails and the evaluation stack becomes the explicit blocker.
- Surprises and Tensions:
  - The sample outputs look more separable than the order-robust summary does, which is exactly the kind of mismatch that tempts bad metric iteration if it is not controlled carefully.
- Confidence:
  - high that the next step should reuse cached outputs
  - medium that the stronger metric will still leave dense steering negative versus neutral
- Interesting facts:
  - The right falsification test now is whether the metric can recover the prompt-only creativity baseline on the existing stories, not whether a new generation run can be made to look better.

## [2026-03-18T16:44:00-0500] The Strong Negative Result Is Narrower Than Failure And More Useful Than Ambiguity

- Stage: synthesis
- Feel of the Experiment: This is the cleanest no we have gotten so far. It is not a collapse of the whole thesis. It is a bounded refusal from one lane after the ambiguity was stripped away.
- Working Hypotheses:
  - The Gemma 2 2B lane can recover a hidden-state creativity direction and a weak prompt-only output baseline, but that is still not enough to make dense steering behaviorally real on the current slice.
  - The next useful work is comparative and strategic, not more local prompt tweaking on the same lane.
- Hunches and Guesses:
  - A bigger model or a matched simpler-concept baseline is now more informative than another tiny evaluation iteration on Gemma 2 2B.
  - The negative result will read strongest if we keep it narrow: "this lane failed after metric tightening," not "creativity steering is impossible."
- Predictions:
  - If we touch decomposition before a bounded next-lane decision, we will just contaminate the negative result with impatience.
- Surprises and Tensions:
  - The blinded manual audit was harsher than I expected, yet it still gave prompt-only a small edge.
  - The stricter automated rerun agreed with the direction of that edge while staying much weaker than the human audit, which is exactly enough to resolve the old ambiguity without pretending the scorer is ideal.
- Confidence:
  - high that `creativedecomp-8o1` is complete
  - high that decomposition should stay blocked
- Interesting facts:
  - The `v2` prompt-grounded-creativity gate recovers `2 / 31` prompt-only wins versus neutral and still `0 / 31` dense wins versus neutral at both tested coefficients.

## [2026-03-18T16:56:00-0500] The Best Control Is Refusal, Not A Bigger Model

- Stage: synthesis
- Feel of the Experiment: The next move needs to earn more information per unit of change. A larger model would be tempting, but it would also blur whether the current negative result is about creativity or about the whole local stack.
- Working Hypotheses:
  - A matched refusal control on the same Gemma 2 `2B` stack is the sharpest next test of the novelty claim.
  - If refusal succeeds under a matched pipeline, the creativity negative result becomes much more defensible. If refusal also fails, then the right story becomes stack weakness or model-capacity limits, not creativity-specific weirdness.
- Hunches and Guesses:
  - Refusal is the better first control than sentiment because the literature treats it as the cleanest established behavioral direction.
- Predictions:
  - The refusal control will resolve whether the repo should keep leaning into a creativity-specific negative result or escalate to a larger model.
- Surprises and Tensions:
  - The more honest the creativity path became, the more obvious it got that a simpler-concept local control should come before any scale-up.
- Confidence:
  - high that the next lane should be matched refusal
  - medium that the same `2B` stack will show a clearer refusal effect than creativity did
- Interesting facts:
  - The strongest novelty memo already wanted matched refusal and sentiment baselines; the current negative result simply moves one of them onto the critical path much earlier than originally planned.

## [2026-03-18T20:13:00-0500] Refusal Was Clean In Hidden State And Messy In Output

- Stage: baseline control
- Feel of the Experiment: The refusal control did its job scientifically even though it did not produce the clean win I wanted. It separated "creativity might be special" from "the 2B dense-steering lane itself may be weak."
- Working Hypotheses:
  - Gemma 2 `2B` can represent refusal cleanly in hidden state, but dense generation control on the base-model lane is still too weak or prompt-sensitive to make strong output claims.
  - The current creativity negative result is therefore less creativity-specific than it looked before the refusal control.
- Hunches and Guesses:
  - A bounded scale-up is now more justified than another round of 2B prompt fiddling.
- Predictions:
  - A stronger model or adjacent scale-up will either recover a cleaner dense refusal control, clarifying that 2B is the bottleneck, or fail similarly and further weaken the whole steering lane.
- Surprises and Tensions:
  - The refusal extraction itself was almost trivially clean, which makes the output-level failure more informative, not less.
  - Prompt-only refusal can be recovered modestly with a prefixed refusal harness, but dense refusal steering still does not beat neutral cleanly.
- Confidence:
  - high that decomposition should remain blocked
  - medium-high that model-scale sensitivity is now the right next lane
- Interesting facts:
  - On the prefixed-refusal gate, prompt-only refusal versus neutral reaches refusal net preference `0.25`, while the best dense refusal condition only reaches `0.083333` and loses the coherence tie-break.

## [2026-03-18T21:34:00-0500] Cross-Scale Failure Looks Like A Method Problem More Than A Size Problem

- Stage: synthesis
- Feel of the Experiment: This is the first point where "just try another dense steering run" would be intellectually dishonest. We have already asked that question at two scales and on a simpler concept.
- Working Hypotheses:
  - Dense additive steering is the weak link on this local lane, not hidden-state extraction itself.
  - An alternate intervention family that uses SAE effects or sparse feature control is the last bounded method question worth testing before the repo settles for a negative-result stop.
- Hunches and Guesses:
  - An instruction-tuned pivot right now would create too much interpretive fog because it changes the model and likely the SAE assumptions at once.
  - A refusal-first alternate-method control will tell us more per unit of work than another creativity-specific tweak.
- Predictions:
  - If the alternate-method refusal control still fails, then the honest conclusion is that this MacBook steering path is negative-result territory and the paper should lean into that directly.
  - If it succeeds, then the dense failure becomes a method-family caution rather than a broader causal failure.
- Surprises and Tensions:
  - The 9B hidden-state refusal result was so clean that it makes the output failure harder to dismiss as "small model noise."
- Confidence:
  - high that we should stop further dense base-model steering sweeps
  - medium-high that the next lane should stay on Gemma plus GemmaScope rather than pivot to an instruction-tuned model
- Interesting facts:
  - The papers we already cited are stronger on effect-aware or sparse steering than on defending dense additive vectors as the only serious causal control method.

## [2026-03-18T22:17:00-0500] The Alternate-Method Check Failed Too

- Stage: alternate-method control
- Feel of the Experiment: This is the first point where the local base-model steering lane feels genuinely exhausted rather than merely under-tuned. The alternate-method check was the remaining serious excuse, and it did not rescue the gate.
- Working Hypotheses:
  - The current MacBook base-model lane is output-weak across more than one intervention family, not just across model sizes.
  - The next useful work is strategic again: either freeze this as a write-up-grade negative result or justify one bounded instruction-tuned pivot.
- Hunches and Guesses:
  - The instruction-tuned pivot is now more defensible than it was before, because the local Gemma plus GemmaScope base-model lane has already had its best dense and sparse shots.
  - If we keep trying more base-model variants here, the work starts to look like method-shopping rather than discovery.
- Predictions:
  - A synthesis pass after this result should narrow the options to two: write it up or pivot once to instruction-tuned behavior.
- Surprises and Tensions:
  - The sparse refusal control is not obviously better than dense refusal steering, and the prompt-only refusal baseline inside the same gate is weaker than I expected.
- Confidence:
  - high that decomposition should stay blocked
  - medium-high that the next issue should be synthesis, not another base-model steering method
- Interesting facts:
  - The best sparse SAE-latent condition only reaches refusal net preference `0.0` versus neutral while losing coherence by `0.166667`.
