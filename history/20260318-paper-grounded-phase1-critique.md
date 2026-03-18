# Paper-Grounded Phase 1 Critique

Date: 2026-03-18

## Purpose

This note records the paper-level critique of the current Phase 1 path after the first implementation cycle. It is narrower than the broader deep progress review. Its job is to identify where the papers themselves expose weaknesses or missing gates in our current approach.

## Papers Reviewed Against The Current Path

- Olson et al. on creativity steering directions
- Von Rütte et al. on creativity/humor detection versus guidance
- Mayne et al. on steering-vector decomposition failure modes
- Arad et al. on input features versus output features
- AxBench on steering evaluation and prompting baselines
- CREATE on associative-creativity evaluation design

## Objective Critique

### 1. Our current `v2` contrast is still weaker than the paper path it is meant to approximate

Olson does not just contrast two different styles of independent generations. The paper stresses the need for high-quality contrastive pairs and builds less-creative counterparts of the same prompt material. Our `v2` pair set improved over the old instruction-template setup, but it still uses independently sampled positive and negative continuations from `Creative story` and `Plain story` source prompts. The audit results show the cost of that choice: several negatives remain as prompt-specific or more prompt-specific than the positives.

Implication:
- `creativedecomp-02c` should move toward content-preserving creative/plain counterparts or audited rewrites when feasible, not merely another independently sampled pair set.

### 2. Hidden-state plausibility is not a sufficient gate for decomposition

Von Rütte is the strongest warning here. The paper finds that better concept detection does not reliably produce better concept guidance for creativity-like concepts, unlike the cleaner truthfulness case. That maps directly onto our current state: a recovered late-layer signal plus a calibration probe trend is still not enough to justify treating the direction as the decomposition target.

Implication:
- Phase 2 should remain blocked until the dense direction shows an output-level effect, not merely a hidden-state effect.

### 3. Our current gating needed an explicit output-side requirement

Arad makes the input/output distinction operational: features that align with inputs are often not the ones that causally affect outputs. Even though Arad is about SAE features rather than dense directions, the lesson transfers. A direction that looks coherent in activations but fails to move outputs in an interpretable way is not yet the right mechanistic object to decompose.

Implication:
- `creativedecomp-roq` is the right missing gate: pilot output-level creativity plus coherence/usefulness before decomposition.

### 4. The pilot output gate should compare against prompting, but not demand immediate superiority

AxBench is the clearest reason not to over-tighten the wrong bar. Prompting often outperforms representation steering on average. That does not mean representation steering is useless; it means the first honest question is whether the steering method has a real causal effect and what tradeoff it introduces. Requiring dense steering to beat the prompt-only creativity baseline on the pilot slice would be a stronger condition than the literature justifies.

Implication:
- The pilot output gate should include the prompt-only creativity baseline explicitly.
- The pilot gate should not require dense steering to outperform prompting; it should require a measurable effect with an honest tradeoff profile.

### 5. Our evaluation plans should lean away from generic “creative style” judging

CREATE reinforces that harder creativity evaluations care about specificity and diversity of associations, not just generic stylistic liveliness. This matters even before confirmatory benchmarking: if our pilot output gate relies only on vague “more creative” judgments, we risk selecting for style drift instead of creativity-relevant behavior.

Implication:
- Even the pilot output gate should prefer metrics or manual audits that can distinguish specificity and meaningful novelty from generic flourish when possible.

### 6. Mayne still constrains how we interpret negative Phase 1 results

Mayne’s warning is not only about Phase 2 decomposition. It also cautions against overinterpreting unstable dense directions as evidence that creativity is inherently diffuse. If the pair construction is still weak, then a weak or unstable dense direction is ambiguous between "creativity is distributed" and "the contrast object is still poor."

Implication:
- A strong negative thesis requires a stronger `v3` contrast first.
- Response-only diagnostics remain important if prompt-plus-response texts blur the object being extracted.

## Revised Reading Of Our Progress

The project is aligned on the big picture, but the papers tighten the phase order:

1. Fix the contrast object properly.
2. Show a bounded output-level effect with a coherence/usefulness check.
3. Only then ask decomposition questions.

That order is stricter than “recover a plausible layer and proceed,” but it is more faithful to both the novelty framing and the methodological literature.
