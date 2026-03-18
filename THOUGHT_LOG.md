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
