# Implementation Grounding

This note is the pre-implementation reference audit for the active experiment. Its job is to keep the work grounded in prior papers, prevent accidental replication of already-solved subproblems, and force each phase to inherit the strongest available methods and controls.

## Top Findings

1. The main novelty is still intact.
   The literature has black-box creativity steering, SAE decomposition for other behaviors, and several creativity evaluation suites, but not a signed SAE decomposition of a creativity steering direction with causal feature validation and matched simpler-concept baselines.

2. The biggest risk is not "redoing Olson et al."
   The bigger risk is doing a weaker version of the already-known steering and SAE work by skipping signed decomposition, output-feature filtering, matched refusal/sentiment baselines, or plural benchmark families.

3. Bridge-feature and latent-navigation ideas remain secondary.
   They are useful hypothesis generators and follow-on lanes, but the papers do not justify leading with them before the creativity-direction decomposition and validation lane is honestly resolved.

4. A negative result only becomes meaningful after bounded sensitivity checks.
   The papers on OOD steering-vector decomposition and dataset-dependent SAEs mean a failed default `Gemma 2 2B + GemmaScope 65K residual` run is informative, but not decisive, until width/site sensitivity has been checked in a controlled way.

## Phase Crosswalk

### Phase 1: Creativity Direction Replication

- Primary papers:
  [olson-creativity-direction-2024.pdf](/Users/sohailmo/creativedecomp/background-work/papers/files/olson-creativity-direction-2024.pdf)
  [von-rutte-creativity-humor-representations-2024.pdf](/Users/sohailmo/creativedecomp/background-work/papers/files/von-rutte-creativity-humor-representations-2024.pdf)
  [representation-engineering-2023.pdf](/Users/sohailmo/creativedecomp/background-work/papers/files/representation-engineering-2023.pdf)
  [steering-language-models-activation-engineering-2023.pdf](/Users/sohailmo/creativedecomp/background-work/papers/files/steering-language-models-activation-engineering-2023.pdf)
  [steering-llama2-contrastive-activation-addition-2023.pdf](/Users/sohailmo/creativedecomp/background-work/papers/files/steering-llama2-contrastive-activation-addition-2023.pdf)
- What we must not redo:
  Extracting a creativity direction and stopping there. That is already known territory.
- What must be inherited:
  Contrastive prompt construction, paired evaluation, pilot-only layer/scale sweeps, frozen confirmatory splits, and pair construction that preserves topic/content tightly enough that creativity is not reduced to specificity drift.
- Code and tooling to use:
  `repeng`, `steering-vectors`, `SAELens`, `TransformerLens`.
- Implementation consequence:
  Freeze the selected layer, steering scale, and judge configuration on the pilot slice before touching the confirmatory split, and do not open Phase 2 on hidden-state probes alone; the dense direction must clear a bounded pilot output-level creativity/coherence gate first.

### Phase 2: Signed Feature Decomposition

- Primary papers:
  [mayne-sae-steering-vector-decomposition-2024.pdf](/Users/sohailmo/creativedecomp/background-work/papers/files/mayne-sae-steering-vector-decomposition-2024.pdf)
  [sae-ts-2024.pdf](/Users/sohailmo/creativedecomp/background-work/papers/files/sae-ts-2024.pdf)
  [fgaa-2025.pdf](/Users/sohailmo/creativedecomp/background-work/papers/files/fgaa-2025.pdf)
  [sas-2025.pdf](/Users/sohailmo/creativedecomp/background-work/papers/files/sas-2025.pdf)
  [sae-ssv-2025.pdf](/Users/sohailmo/creativedecomp/background-work/papers/files/sae-ssv-2025.pdf)
- What we must not redo:
  Naive dense-vector SAE encoding, unsigned feature ranking, or cosine-only decoder alignment as if that were mechanistic evidence.
- What must be inherited:
  Signed methods, positive and negative feature accounting, multi-method pilot comparison, and matched random-feature controls.
- Code and tooling to use:
  `SAE-TS`, `IBM/sae-steering`, `EffectVis`, `Neuronpedia`, local GemmaScope SAEs via `SAELens`.
- Implementation consequence:
  The confirmatory method freeze happens only after at least two legal signed methods agree enough on the pilot slice to justify one path.

### Phase 3: Feature Validation And Evaluation

- Primary papers:
  [arad-input-output-sae-features-2025.pdf](/Users/sohailmo/creativedecomp/background-work/papers/files/arad-input-output-sae-features-2025.pdf)
  [axbench-2025.pdf](/Users/sohailmo/creativedecomp/background-work/papers/files/axbench-2025.pdf)
  [create-benchmark-2026.pdf](/Users/sohailmo/creativedecomp/background-work/papers/files/create-benchmark-2026.pdf)
  [noveltybench-2025.pdf](/Users/sohailmo/creativedecomp/background-work/papers/files/noveltybench-2025.pdf)
  [art-or-artifice-2023.pdf](/Users/sohailmo/creativedecomp/background-work/papers/files/art-or-artifice-2023.pdf)
  [automated-creativity-evaluation-2025.pdf](/Users/sohailmo/creativedecomp/background-work/papers/files/automated-creativity-evaluation-2025.pdf)
  [ocsai-divergent-thinking-scoring-2023.pdf](/Users/sohailmo/creativedecomp/background-work/papers/files/ocsai-divergent-thinking-scoring-2023.pdf)
  [rabeyah-alternative-uses-evaluation-2024.pdf](/Users/sohailmo/creativedecomp/background-work/papers/files/rabeyah-alternative-uses-evaluation-2024.pdf)
  [creativityprism-2025.pdf](/Users/sohailmo/creativedecomp/background-work/papers/files/creativityprism-2025.pdf)
- What we must not redo:
  Single-benchmark creativity claims, judge-only claims without side-effect inspection, or feature-label claims without interventions.
- What must be inherited:
  Output-feature filtering, benchmark pluralism, coherence/usefulness checks, and explicit style/formatting artifact tracking.
- Code and tooling to use:
  benchmark harnesses where available, local paired-eval scripts, saved manual audit slices, and reusable judge prompts locked before confirmatory runs.
- Implementation consequence:
  Claim-bearing runs should use two complementary benchmark families whenever feasible:
  one association/divergent-thinking style family such as `CREATE` or `AUT + Ocsai`, and one writing/diversity style family such as `TTCW`, `NoveltyBench`, or `CreativityPrism`.

### Phase 4: Bridge-Feature Analysis

- Primary papers:
  [geometry-of-concepts-2024.pdf](/Users/sohailmo/creativedecomp/background-work/papers/files/geometry-of-concepts-2024.pdf)
  [scaling-monosemanticity-2024.pdf](/Users/sohailmo/creativedecomp/background-work/papers/files/scaling-monosemanticity-2024.pdf)
  [parallelparc-2024.pdf](/Users/sohailmo/creativedecomp/background-work/papers/files/parallelparc-2024.pdf)
  [latentqa-2024.pdf](/Users/sohailmo/creativedecomp/background-work/papers/files/latentqa-2024.pdf)
  [activation-oracles-2025.pdf](/Users/sohailmo/creativedecomp/background-work/papers/files/activation-oracles-2025.pdf)
- What we must not redo:
  Calling any broad or cross-domain feature a creativity mechanism without breadth controls, output checks, and causal evidence.
- What must be inherited:
  Activation-breadth controls, random-feature breadth baselines, and task-grounded output checks on cross-domain prompts.
- Code and tooling to use:
  cached activation matrices, Neuronpedia feature inspection, `LatentQA` or `Activation Oracles` only as descriptive support.
- Implementation consequence:
  LatentQA and Activation Oracles are not primary evidence. They can describe candidate bridge features, but the paper claim must still rest on interventions or benchmarked outputs.

### Phase 5: Simpler-Concept Baselines

- Primary papers:
  [refusal-single-direction-2024.pdf](/Users/sohailmo/creativedecomp/background-work/papers/files/refusal-single-direction-2024.pdf)
  [there-is-more-to-refusal-2026.pdf](/Users/sohailmo/creativedecomp/background-work/papers/files/there-is-more-to-refusal-2026.pdf)
  [sae-ssv-2025.pdf](/Users/sohailmo/creativedecomp/background-work/papers/files/sae-ssv-2025.pdf)
- What we must not redo:
  Loose comparison against published numbers from different models, layers, SAE releases, or decomposition methods.
- What must be inherited:
  Matched-pipeline comparison using the same model, SAE release, layer/site, and decomposition method wherever feasible.
- Implementation consequence:
  The "mechanistically different from refusal and sentiment" claim is only strong if the comparison is local and pipeline-matched, not literature-only.

### Phase 6: Extension Lanes

- Primary papers:
  [generative-meta-models-2026.pdf](/Users/sohailmo/creativedecomp/background-work/papers/files/generative-meta-models-2026.pdf)
  [weighted-activation-steering-2025.pdf](/Users/sohailmo/creativedecomp/background-work/papers/files/weighted-activation-steering-2025.pdf)
  [activation-state-machines-2025.pdf](/Users/sohailmo/creativedecomp/background-work/papers/files/activation-state-machines-2025.pdf)
  [layernavigator-2025.pdf](/Users/sohailmo/creativedecomp/background-work/papers/files/layernavigator-2025.pdf)
  [magellan-2025.pdf](/Users/sohailmo/creativedecomp/background-work/papers/files/magellan-2025.pdf)
  [huginn-recurrent-depth-2025.pdf](/Users/sohailmo/creativedecomp/background-work/papers/files/huginn-recurrent-depth-2025.pdf)
  [coconut-2024.pdf](/Users/sohailmo/creativedecomp/background-work/papers/files/coconut-2024.pdf)
  [ladir-2025.pdf](/Users/sohailmo/creativedecomp/background-work/papers/files/ladir-2025.pdf)
  [colar-2025.pdf](/Users/sohailmo/creativedecomp/background-work/papers/files/colar-2025.pdf)
  [dlcm-2025.pdf](/Users/sohailmo/creativedecomp/background-work/papers/files/dlcm-2025.pdf)
  [concept-attractors-2026.pdf](/Users/sohailmo/creativedecomp/background-work/papers/files/concept-attractors-2026.pdf)
  [critical-phase-transition-llms-2024.pdf](/Users/sohailmo/creativedecomp/background-work/papers/files/critical-phase-transition-llms-2024.pdf)
  [lyapunov-reasoning-mechanisms-2025.pdf](/Users/sohailmo/creativedecomp/background-work/papers/files/lyapunov-reasoning-mechanisms-2025.pdf)
  [cold-decoding-2022.pdf](/Users/sohailmo/creativedecomp/background-work/papers/files/cold-decoding-2022.pdf)
  [mucola-2022.pdf](/Users/sohailmo/creativedecomp/background-work/papers/files/mucola-2022.pdf)
- What we must not redo:
  Reframing the project as a controller or basin-hopping paper before the core decomposition result exists.
- What must be inherited:
  These papers are follow-on design space, not justification for skipping the primary lane.

## Code And Method Assets Worth Using

- `SAELens` for GemmaScope loading, hooks, and activation caching.
- `repeng` or `steering-vectors` for layerwise creativity-direction extraction.
- `SAE-TS` and `IBM/sae-steering` for effect-aware feature interventions rather than decoder-cosine shortcuts.
- `EffectVis` and `Neuronpedia` for rapid sanity checks on candidate features.
- local benchmark wrappers for `CREATE`, `NoveltyBench`, and TTCW-style evaluations when available.
- saved judge prompts, manual audit slices, and random-feature controls as first-class artifacts, not ad hoc notebook output.

## What Counts As Meaningful Forward Progress

- Not another black-box creativity steering result.
- Not another bag of qualitative "creative examples."
- Not another broad latent-navigation manifesto.
- A creativity-direction result becomes field-relevant when it adds:
  signed decomposition,
  causal output validation,
  matched refusal/sentiment baselines,
  benchmark pluralism,
  and a publishable interpretation of either sparse or distributed creativity structure.
