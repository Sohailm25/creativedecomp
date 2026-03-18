# Preregistration

## Scope

This preregistration covers the local creativity-decomposition experiment defined by:

- `research/transcript.md`
- `research/experiment-ideas.md`
- `research/experiment-macbook-guide.md`
- `research/experiment-novelty.md`

## Framing Lock

- The primary claim is about mechanistic structure behind creativity steering in a frozen open model.
- The default experiment is not a claim about open-ended scientific discovery or autonomous novelty search.
- A creativity-aligned feature is not automatically a creativity mechanism unless interventions support that claim.
- Cross-domain bridge claims require explicit evidence beyond creative-writing style changes.
- The strongest paper framing is whether creativity is mechanistically different from simpler behavioral concepts such as refusal and sentiment.
- Extension lanes such as controller-guided latent navigation are inference or future work unless they are directly executed and validated here.

## Primary Hypothesis

A creativity steering direction on the default model can be decomposed into a signed set of interpretable SAE features whose interventions measurably change creative outputs relative to the unsteered model.

## Secondary Hypotheses

1. Creativity decomposition is less sparse and cleaner than raw stylistic diversity, but less clean than refusal-style concepts.
2. Some top creativity-aligned features are cross-domain bridge features rather than narrow genre features.
3. Output-filtered feature bundles will be more interpretable and more controllable than the original dense direction.
4. Creativity gains can be measured without catastrophic coherence loss.
5. Matched random-feature bundles will not recover the same effect size as the aligned feature bundle.
6. Creativity decomposition differs in sparsity, interpretability, or bridge structure from refusal and sentiment baselines.

## Null and Baseline Conditions

- unsteered model
- prompt-only creativity instruction
- dense creativity direction
- matched random SAE features
- high-activation non-aligned SAE features

## Required Reference Baselines

- refusal
- sentiment

## Required Methods

- frozen creative versus uncreative prompt split before claim-bearing runs
- paired contrast rows must preserve prompt topic and core content tightly enough that creativity is not confounded with specificity or plot drift; content-preserving counterparts or audited rewrites are preferred when feasible
- sequence-level paired evaluation
- pilot-only sweep over candidate layers and steering scales before confirmatory runs
- Freeze the selected layer and steering scale before touching the confirmatory split
- signed decomposition method
- feature-level intervention validation
- output-feature filtering or an equivalent output-score-based selection step
- coherence or usefulness check alongside creativity metrics
- at least two benchmark families for claim-bearing evaluation, with one association/divergent-thinking style family and one writing/diversity style family unless a logged constraint prevents it
- refusal and sentiment baselines should use the same model, SAE release, layer/site, and decomposition pipeline whenever feasible

## Phase Gates

### Phase 1: Creativity Direction Replication

- Minimum confirmatory sample size: `100` prompts
- Tune layer choice, steering scale, and judge settings only on the pilot slice
- Before Phase 2 opens, the selected dense direction must show a bounded output-level creativity effect on the pilot slice using at least one locked creativity-side metric plus a coherence/usefulness check; internal projection movement alone is insufficient
- Primary metric: paired creativity score delta on the frozen confirmatory split
- Required secondary metrics: coherence/usefulness delta plus at least one diversity or creativity benchmark metric
- Significance gate: `p < 0.01` on the sequence-level paired test
- Report bootstrap confidence intervals for claim-bearing estimates

### Phase 2: Feature Decomposition

- Direct dense-vector SAE encoding is not allowed as the primary method
- compare at least two signed decomposition methods on the pilot slice before freezing the confirmatory method
- Report the top positive and top negative feature contributions
- Compare at least one signed decomposition method against a matched random-feature control
- If decomposition does not preserve the sign of the dense creativity effect under intervention, weaken the mechanistic claim accordingly
- If the default `65K residual` lane fails cleanly, run one bounded sensitivity check over nearby SAE width/site choices before treating the result as evidence for distributed creativity rather than simple SAE mismatch

### Phase 3: Feature Validation

- Test individual features and at least one bundled feature set
- Compare against the dense direction and matched random-feature bundles
- A feature is only promoted to a creativity feature if it changes output behavior, not just if it aligns with creative inputs
- Compare output-filtered feature bundles against non-filtered candidate bundles on the pilot slice
- Use at least two complementary benchmark families such as `CREATE` or `AUT + Ocsai` plus `TTCW`, `NoveltyBench`, or `CreativityPrism`; if only one is used, record why
- Record formatting and verbosity side effects alongside creativity gains so style drift does not masquerade as creativity

### Phase 4: Bridge-Feature Analysis

- Use a frozen multi-domain corpus before searching for bridge features
- Report whether bridge candidates activate across distinct domains or collapse to one narrow genre
- Any bridge-feature claim must compare against random-feature activation breadth
- Treat `LatentQA` or `Activation Oracles` outputs as descriptive support only unless intervention evidence and benchmark behavior point in the same direction
- Any bridge-feature claim should be paired with at least one task-grounded output check such as `CREATE` or `ParallelPARC`

### Phase 5: Simpler-Concept Baselines

- Compare the sparsity or interpretability profile of creativity decomposition against refusal and sentiment baselines
- Use the same model, SAE release, layer/site, and decomposition pipeline for refusal and sentiment whenever feasible so the comparison is mechanistic rather than anecdotal
- If the baseline comparison is omitted for a given run, record why in `DECISIONS.md`

### Phase 6: Extension Lanes

- `controller_extensions` and `basin_dynamics` are optional follow-on lanes
- They are not allowed to replace the primary decomposition result as the central contribution

## Overclaim Guardrails

Do not claim:

- that the experiment discovers a universal creativity mechanism
- that creativity features imply scientific discovery ability
- that descriptive feature labels are causal explanations
- that cross-domain activation alone proves useful analogy formation
- that a failed result on one SAE width/site settles the distributed-creativity question
- that a negative result means the experiment failed; a clean distributed-creativity result is still informative

## Implementation Constraints

- Use `.venv` for local execution
- Save prompt splits, hyperparameters, and result artifacts before claim-bearing runs
- Keep the default model-and-SAE pair MacBook-feasible unless a deliberate escalation is logged
- Treat benchmark saturation and judge brittleness as first-class risks

## Reproducibility

- pre-register locally in this document before claim-bearing execution
- fix random seeds before running claim-bearing experiments
- log hyperparameters before runs
- save the frozen prompt split before tuning methods
- keep a result file for every durable artifact under `results/`
