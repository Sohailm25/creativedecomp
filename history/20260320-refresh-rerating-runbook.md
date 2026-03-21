# ABOUTME: Defines the exact rerating workflow for replacing heuristic refresh audits with locked human ratings.
# ABOUTME: Provides one-pass commands to regenerate confirmation/dropoff summaries and choose the next corrective path.

# Prompt-Matched Refresh Rerating Runbook (d1j)

## Scope

Replace heuristic-locked annotations with independent human-locked annotations for all four refresh audit packets:

1. `coeff=1.0`, writing/diversity  
   `results/creativity_benchmarks/20260320-gemma3-270m-it-feature-validation-benchmark-writing-v1-refresh-v1-manual-audit/`
2. `coeff=1.0`, association/divergent  
   `results/creativity_benchmarks/20260320-gemma3-270m-it-feature-validation-benchmark-association-v1-refresh-v1-manual-audit/`
3. `coeff=0.5`, writing/diversity  
   `results/creativity_benchmarks/20260320-gemma3-270m-it-feature-validation-benchmark-writing-v1-coeff05-refresh-v1-manual-audit/`
4. `coeff=0.5`, association/divergent  
   `results/creativity_benchmarks/20260320-gemma3-270m-it-feature-validation-benchmark-association-v1-coeff05-refresh-v1-manual-audit/`

## Human Lock Procedure

For each packet:

1. Read `blinded_packet.md` using the locked rubric.
2. Fill `manual_annotations_template.jsonl`.
3. Save finalized labels to `manual_annotations_locked_v1.jsonl`.
4. Keep labels restricted to `A`, `B`, or `tie`.
5. Do not edit `answer_key.jsonl`.

## Recompute Commands

After all four `manual_annotations_locked_v1.jsonl` files are complete:

```bash
.venv/bin/python scripts/audit_instruction_tuned_creativity_output_gate_v1.py \
  --artifact-dir results/creativity_benchmarks/20260320-gemma3-270m-it-feature-validation-benchmark-writing-v1-refresh-v1 \
  --reference-condition-id dense_direction \
  --candidate-condition-ids bundle_feature_group \
  --sample-size 10 \
  --seed 20260320 \
  --annotations-path results/creativity_benchmarks/20260320-gemma3-270m-it-feature-validation-benchmark-writing-v1-refresh-v1-manual-audit/manual_annotations_locked_v1.jsonl \
  --output-dir results/creativity_benchmarks/20260320-gemma3-270m-it-feature-validation-benchmark-writing-v1-refresh-v1-manual-audit \
  --overwrite

.venv/bin/python scripts/audit_instruction_tuned_creativity_output_gate_v1.py \
  --artifact-dir results/creativity_benchmarks/20260320-gemma3-270m-it-feature-validation-benchmark-association-v1-refresh-v1 \
  --reference-condition-id dense_direction \
  --candidate-condition-ids bundle_feature_group \
  --sample-size 10 \
  --seed 20260320 \
  --annotations-path results/creativity_benchmarks/20260320-gemma3-270m-it-feature-validation-benchmark-association-v1-refresh-v1-manual-audit/manual_annotations_locked_v1.jsonl \
  --output-dir results/creativity_benchmarks/20260320-gemma3-270m-it-feature-validation-benchmark-association-v1-refresh-v1-manual-audit \
  --overwrite

.venv/bin/python scripts/audit_instruction_tuned_creativity_output_gate_v1.py \
  --artifact-dir results/creativity_benchmarks/20260320-gemma3-270m-it-feature-validation-benchmark-writing-v1-coeff05-refresh-v1 \
  --reference-condition-id dense_direction \
  --candidate-condition-ids bundle_feature_group \
  --sample-size 10 \
  --seed 20260320 \
  --annotations-path results/creativity_benchmarks/20260320-gemma3-270m-it-feature-validation-benchmark-writing-v1-coeff05-refresh-v1-manual-audit/manual_annotations_locked_v1.jsonl \
  --output-dir results/creativity_benchmarks/20260320-gemma3-270m-it-feature-validation-benchmark-writing-v1-coeff05-refresh-v1-manual-audit \
  --overwrite

.venv/bin/python scripts/audit_instruction_tuned_creativity_output_gate_v1.py \
  --artifact-dir results/creativity_benchmarks/20260320-gemma3-270m-it-feature-validation-benchmark-association-v1-coeff05-refresh-v1 \
  --reference-condition-id dense_direction \
  --candidate-condition-ids bundle_feature_group \
  --sample-size 10 \
  --seed 20260320 \
  --annotations-path results/creativity_benchmarks/20260320-gemma3-270m-it-feature-validation-benchmark-association-v1-coeff05-refresh-v1-manual-audit/manual_annotations_locked_v1.jsonl \
  --output-dir results/creativity_benchmarks/20260320-gemma3-270m-it-feature-validation-benchmark-association-v1-coeff05-refresh-v1-manual-audit \
  --overwrite

.venv/bin/python scripts/summarize_feature_validation_benchmark_confirmation.py \
  --association-summary-path results/creativity_benchmarks/20260320-gemma3-270m-it-feature-validation-benchmark-association-v1-refresh-v1-manual-audit/summary.json \
  --writing-summary-path results/creativity_benchmarks/20260320-gemma3-270m-it-feature-validation-benchmark-writing-v1-refresh-v1-manual-audit/summary.json \
  --output-path results/creativity_benchmarks/20260320-gemma3-270m-it-feature-validation-benchmark-confirmation-v1-refresh-v1/summary.json

.venv/bin/python scripts/summarize_feature_validation_benchmark_confirmation.py \
  --association-summary-path results/creativity_benchmarks/20260320-gemma3-270m-it-feature-validation-benchmark-association-v1-coeff05-refresh-v1-manual-audit/summary.json \
  --writing-summary-path results/creativity_benchmarks/20260320-gemma3-270m-it-feature-validation-benchmark-writing-v1-coeff05-refresh-v1-manual-audit/summary.json \
  --output-path results/creativity_benchmarks/20260320-gemma3-270m-it-feature-validation-benchmark-confirmation-v1-coeff05-refresh-v1/summary.json

.venv/bin/python scripts/analyze_feature_validation_dropoff.py \
  --writing-artifact-dir results/creativity_benchmarks/20260320-gemma3-270m-it-feature-validation-benchmark-writing-v1-refresh-v1 \
  --writing-audit-summary-path results/creativity_benchmarks/20260320-gemma3-270m-it-feature-validation-benchmark-writing-v1-refresh-v1-manual-audit/summary.json \
  --association-artifact-dir results/creativity_benchmarks/20260320-gemma3-270m-it-feature-validation-benchmark-association-v1-refresh-v1 \
  --association-audit-summary-path results/creativity_benchmarks/20260320-gemma3-270m-it-feature-validation-benchmark-association-v1-refresh-v1-manual-audit/summary.json \
  --writing-low-coeff-audit-summary-path results/creativity_benchmarks/20260320-gemma3-270m-it-feature-validation-benchmark-writing-v1-coeff05-refresh-v1-manual-audit/summary.json \
  --association-low-coeff-audit-summary-path results/creativity_benchmarks/20260320-gemma3-270m-it-feature-validation-benchmark-association-v1-coeff05-refresh-v1-manual-audit/summary.json \
  --output-path results/creativity_benchmarks/20260320-gemma3-270m-it-feature-validation-dropoff-analysis-v1-refresh-v1/summary.json
```

## Decision Rule

1. If either coefficient passes two-family confirmation, keep the refreshed bundle and freeze that coefficient as the benchmark default.
2. If neither coefficient passes and both families remain net-negative on creativity at both coefficients, freeze a negative benchmark-transfer read.
3. If one family is positive and one negative (mixed), allow exactly one additional selection retune with a family-robust objective before freezing negative transfer.
