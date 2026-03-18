# Mechanistic Interpretability Guidance

Use this note when the experiment starts to feel methodologically shaky.

## Non-Negotiable Method Rules

- Never directly encode the dense creativity steering vector through an SAE and trust the coefficients.
- Preserve signed structure. Suppressed features are part of the mechanism.
- Decompose creative and uncreative activations separately before subtracting, or use a pursuit-style method that works on signed vectors.
- Do not confuse interpretability with causality. Feature labels and cosine similarity are descriptive only.
- Always compare feature-level interventions against the dense direction and matched random-feature controls.

## Recommended Decomposition Order

1. Replicate the dense creativity direction on a frozen split.
2. Use the pilot slice to freeze layer choice and steering scale before any confirmatory run.
3. Choose one legal decomposition method only after comparing at least two signed candidates on the pilot slice.
4. If the default `65K residual` lane fails, run one bounded width/site sensitivity check before claiming creativity is inherently diffuse.
5. Inspect top positive and top negative features.
6. Validate output effects with individual and bundled interventions.
7. Only then ask whether bridge features or benchmark gains tell a larger story.

## Evaluation Discipline

- Pair every creativity score with a coherence or usefulness score.
- Inspect outputs manually before trusting automated judges.
- Keep sequence-level paired comparisons as the default statistical unit.
- Use two complementary benchmark families whenever the local runtime permits it; one benchmark alone is too easy to game.
- If a benchmark saturates easily, say so and weaken claims.
- Track formatting, verbosity, and metadata artifacts explicitly so stylistic drift does not masquerade as creativity.

## Baseline Discipline

- unsteered model
- dense creativity direction
- matched random SAE features
- high-activation but non-aligned SAE features
- prompt-only creativity instruction baseline
- refusal and sentiment baselines through the same model, SAE release, layer/site, and decomposition pipeline whenever feasible

## Bridge-Claim Discipline

- Treat LatentQA and Activation Oracles as descriptive support, not primary evidence.
- Do not call something a bridge feature from activation breadth alone; require intervention evidence or task-grounded output checks.
