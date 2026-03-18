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
