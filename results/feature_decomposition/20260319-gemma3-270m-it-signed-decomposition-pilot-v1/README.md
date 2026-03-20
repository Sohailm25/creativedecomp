# Instruction-Tuned Creativity Signed Decomposition Pilot

- Generated at: `2026-03-19T09:31:37.153039`
- Model: `google/gemma-3-270m-it`
- Device: `mps`
- SAE release: `gemma-scope-2-270m-it-res`
- Reference SAE id: `layer_12_width_16k_l0_medium`
- Hidden layer: `12`
- Pair count: `18`
- Top-k sparsity budget: `32`
- Random control samples per method: `16`
- Recommended method: `fista_dense_topk`
- Pilot freeze recommendation: `True`

Method summaries:
- `contrastive_latent_topk`: fraction `0.611111`, margin `689.660034`, dense cosine `0.798049`, random-fraction mean `0.510417`, random-cosine mean `0.079822`
- `fista_dense_topk`: fraction `0.666667`, margin `719.617920`, dense cosine `0.832715`, random-fraction mean `0.472222`, random-cosine mean `0.067649`

Method agreement:
- decoded-direction cosine: `0.718854`
- top-feature jaccard: `0.115385`

Artifacts:
- `summary.json`
- `method_metrics.jsonl`
- `feature_tables.json`
- `random_control_metrics.jsonl`
