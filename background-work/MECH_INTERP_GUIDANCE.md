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
2. Choose one legal decomposition method.
3. Inspect top positive and top negative features.
4. Validate output effects with individual and bundled interventions.
5. Only then ask whether bridge features or benchmark gains tell a larger story.

## Evaluation Discipline

- Pair every creativity score with a coherence or usefulness score.
- Inspect outputs manually before trusting automated judges.
- Keep sequence-level paired comparisons as the default statistical unit.
- If a benchmark saturates easily, say so and weaken claims.

## Baseline Discipline

- unsteered model
- dense creativity direction
- matched random SAE features
- high-activation but non-aligned SAE features
- prompt-only creativity instruction baseline
