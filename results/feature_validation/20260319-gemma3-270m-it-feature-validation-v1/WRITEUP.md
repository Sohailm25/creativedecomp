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
- An independent second-rater pass on the same blinded packet is now recorded. Inter-rater agreement is `0.833` (Cohen's κ `0.710`) for prompt-grounded creativity and `0.944` (Cohen's κ `0.894`) for coherence.
- The first prereg two-family benchmark confirmation run now exists at `results/creativity_benchmarks/20260320-gemma3-270m-it-feature-validation-benchmark-confirmation-v1/` (`20` audited pairs total, beyond the `18`-pair pilot slice) and does **not** confirm the pilot bundle-over-dense pattern.
- Benchmark-family net wins (`bundle - dense`) are negative on prompt-grounded creativity in both families: association/divergent `-0.200`, writing/diversity `-0.300`; coherence is `-0.100` and `0.000` respectively.

## Limitations

- The benchmark-family confirmation pass currently fails the prereg two-family gate, so stronger feature-level claim language remains blocked.
- Current automatic judge limitations still apply and remain tracked in `creativedecomp-183`.

## Next Steps

- Keep feature-level interpretation tied to the same prompt-grounded creativity and coherence rubric used in instruction-tuned gate work.
- Run a root-cause follow-up on why bundle performance drops off the pilot slice (prompt-family shift, feature selection instability, or intervention scaling mismatch) before any claim upgrade attempt.
