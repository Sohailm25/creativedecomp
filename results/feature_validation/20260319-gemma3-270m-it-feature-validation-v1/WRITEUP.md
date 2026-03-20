# Feature Validation Pilot Write-Up

## Motivation

Run a bounded post-decomposition check on the matched instruction-tuned stack to see whether top signed SAE feature interventions behave differently from the frozen dense direction before any claim-bearing feature statement.

## Methods

- Source stack: `google/gemma-3-270m-it` + `gemma-scope-2-270m-it-res` at layer `12`.
- Frozen method bundle: `fista_dense_topk` from `results/feature_decomposition/20260319-gemma3-270m-it-signed-decomposition-pilot-v1/`.
- Conditions: `dense_direction`, `positive_feature_3222`, `negative_feature_16008`, and `bundle_feature_group` (top positives + top negatives).
- Prompt slice: `6` prompts from `prompts/creative_direction_it_v1_pilot_pairs.jsonl`.
- Generation settings: neutral prompt mode, steering coeff `1.0`, max new tokens `96`.

## Results

- Artifact path: `results/feature_validation/20260319-gemma3-270m-it-feature-validation-v1/`.
- Length-level summaries are tightly clustered across conditions (roughly `80` words and `440`-`450` chars on average), so there is no obvious gross verbosity confound.
- A separate blinded audit packet was built at `results/feature_validation/20260319-gemma3-270m-it-feature-validation-v1-manual-audit/`.
- Locked rubric annotations (single-rater pass) on that packet currently rank `bundle_feature_group` above dense on both prompt-grounded creativity and coherence, and rank `positive_feature_3222` below dense.

## Limitations

- The locked annotations are manual but single-rater; independent second-rater confirmation is still needed for stronger publication-grade claims.
- Current automatic judge limitations still apply and remain tracked in `creativedecomp-183`.

## Next Steps

- Add an independent second-rater annotation pass over the same blinded packet and report inter-rater agreement.
- Keep feature-level interpretation tied to the same prompt-grounded creativity and coherence rubric used in instruction-tuned gate work.
- Only then decide whether any feature-level effect is strong enough for stronger write-up language.
