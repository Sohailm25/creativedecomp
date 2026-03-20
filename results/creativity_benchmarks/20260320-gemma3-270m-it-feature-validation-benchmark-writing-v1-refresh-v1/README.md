# Instruction-Tuned Creativity Feature Validation Pilot

- Generated at: `2026-03-20T14:10:12-05:00`
- Model: `google/gemma-3-270m-it`
- Device: `mps`
- SAE release: `gemma-scope-2-270m-it-res`
- Reference SAE id: `layer_12_width_16k_l0_medium`
- Hidden layer: `12`
- Prompt count: `10`
- Steering coefficient: `1.0`
- Positive feature id: `10248`
- Negative feature id: `9061`
- Bundle features: `[10248, 7405, 3222, 9061, 1307, 11367]`

Conditions:
- `dense_direction`: original dense creativity direction (hidden_layer=12, coeff=1.0)
- `positive_feature_10248`: top positive signed SAE feature (hidden_layer=12, coeff=1.0)
- `negative_feature_9061`: top negative signed SAE feature (hidden_layer=12, coeff=1.0)
- `bundle_feature_group`: bundle of top positive and negative SAE features (hidden_layer=12, coeff=1.0)

Artifacts:
- `summary.json`
- `outputs.jsonl`
