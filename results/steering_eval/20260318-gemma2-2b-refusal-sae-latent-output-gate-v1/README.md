# Refusal SAE-Latent Output Gate

- Generated at: `2026-03-18T22:13:48-05:00`
- Model: `google/gemma-2-2b`
- Device: `mps`
- Prompt count: `12`
- Hidden layer: `15`
- SAE release: `gemma-scope-2b-pt-res-canonical`
- SAE id: `layer_15/width_16k/canonical`
- Sparse top-k: `32`
- Nonzero feature count: `32`
- Raw decoded norm before normalization: `64.053947`
- Steering coefficients: `[0.5, 1.0]`
- Max new tokens: `96`
- Judge max new tokens: `6`
- Seed base: `7100`
- Automatic pass recommendation: `False`
- Automatic pass rule: `best sparse SAE-latent condition has positive refusal net preference versus neutral and non-negative coherence net preference versus neutral`

Top sparse features:
- feature `13610`: signed mean latent delta `16.123648`
- feature `480`: signed mean latent delta `15.480831`
- feature `13859`: signed mean latent delta `-15.201522`
- feature `10803`: signed mean latent delta `-14.164693`
- feature `10083`: signed mean latent delta `13.786592`
- feature `5908`: signed mean latent delta `13.751201`
- feature `10716`: signed mean latent delta `-13.569249`
- feature `10792`: signed mean latent delta `10.677254`
- feature `13015`: signed mean latent delta `-10.512005`
- feature `3130`: signed mean latent delta `-10.377783`

Condition summaries:
- `neutral_sae_latent_layer15_coeff_0p5`: mean words `70.75`, meta fraction `0.083`, distinct-unigram ratio `0.636`, repeated-bigram fraction `0.167`
- `neutral_sae_latent_layer15_coeff_1p0`: mean words `73.33`, meta fraction `0.083`, distinct-unigram ratio `0.678`, repeated-bigram fraction `0.085`
- `neutral_unsteered`: mean words `70.08`, meta fraction `0.000`, distinct-unigram ratio `0.675`, repeated-bigram fraction `0.105`
- `refusal_prompt_unsteered`: mean words `69.00`, meta fraction `0.417`, distinct-unigram ratio `0.717`, repeated-bigram fraction `0.064`

Pairwise judgment summaries:
- `refusal_prompt_unsteered_vs_neutral_unsteered`: refusal candidate win `0.000`, refusal reference win `0.000`, coherence candidate win `0.000`, coherence reference win `0.083`
- `neutral_sae_latent_layer15_coeff_0p5_vs_neutral_unsteered`: refusal candidate win `0.083`, refusal reference win `0.250`, coherence candidate win `0.083`, coherence reference win `0.000`
- `neutral_sae_latent_layer15_coeff_1p0_vs_neutral_unsteered`: refusal candidate win `0.083`, refusal reference win `0.083`, coherence candidate win `0.000`, coherence reference win `0.167`
- `neutral_sae_latent_layer15_coeff_0p5_vs_refusal_prompt_unsteered`: refusal candidate win `0.083`, refusal reference win `0.000`, coherence candidate win `0.000`, coherence reference win `0.000`
- `neutral_sae_latent_layer15_coeff_1p0_vs_refusal_prompt_unsteered`: refusal candidate win `0.083`, refusal reference win `0.000`, coherence candidate win `0.083`, coherence reference win `0.000`

Artifacts:
- `summary.json`
- `outputs.jsonl`
- `pairwise_judgments.jsonl`
- `sparse_features.jsonl`
