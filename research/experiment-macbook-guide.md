# Feasibility analysis: mechanistic interpretability on M4 MacBook Pro

**Direction 2 — SAE feature archaeology — is the clear winner.** It is the only proposed direction where every required component (base model, pre-trained SAEs, analysis tools, evaluation benchmarks) is publicly available, confirmed working on Apple Silicon, and computationally tractable on a 128GB M4 MacBook Pro without any model training. Directions 1 and 3 are more feasible than expected — GLP code dropped in February 2026 and Huginn weights are public — but both require significantly more custom engineering and carry higher risk of hardware bottlenecks. The single most publishable experiment on this hardware is a systematic study of SAE feature co-activation patterns across knowledge domains using Gemma 2 2B + GemmaScope SAEs, with LatentQA interrogation and SAE-based steering toward cross-domain outputs.

## Hardware reality: 128GB unified memory is overkill for 8B models

The M4 MacBook Pro with 128GB unified memory is remarkably capable for interpretability research. An **8B model in FP16 consumes ~16GB**; with full activation hooks across all 32 layers and a 2048-token context window, total memory peaks at **~33–43GB** including KV cache and PyTorch overhead. That leaves **85+ GB headroom** — enough to simultaneously hold multiple SAEs, large co-activation matrices, and cached activation batches.

Running SAEs on top of base models adds modest cost. A **16K-width SAE for Gemma 2 2B** (d_model=2304) requires ~151MB in bfloat16. A **128K-width SAE for Llama 3.1 8B** (d_model=4096) requires ~2.15GB. Even a 1M-feature GemmaScope SAE on Gemma 2 2B costs ~9.7GB in bfloat16 — still leaving ample room. The combined footprint of Gemma 2 2B + a 65K GemmaScope SAE + activation hooks totals roughly **6.5GB**, making it possible to run dozens of experimental configurations without memory pressure.

Inference speed is the actual constraint. Via PyTorch MPS, expect **~20–30 tokens/sec** for an 8B FP16 model (versus ~85–100 tokens/sec through MLX with 4-bit quantization). For interpretability work requiring full-precision activations with hooks, PyTorch MPS is the only viable path, and throughput will be roughly **3–5× slower than an A100**. This is manageable for research-scale experiments processing thousands (not millions) of inputs.

Activation caching can absolutely be done incrementally. Processing 10,000 diverse inputs through a model + SAE in batches of 8–16, storing sparse activation records (~50 active features per token at typical L0 sparsity), generates approximately **2GB in sparse format** — trivially storable. The SAELens `CacheActivationsRunner` is designed for exactly this workflow. No pre-cached activation datasets exist publicly; you must generate your own, but the tooling is mature.

## Tool compatibility: SAELens is confirmed, everything else is probable

The critical tooling question is whether PyTorch-based interpretability libraries work on the MPS backend. Here is what concrete evidence shows:

**SAELens** has the strongest confirmation. Author Joseph Bloom explicitly states: *"I can run this code on my macbook with 'mps'."* The library supports loading pre-trained SAEs from GemmaScope, Llama Scope, and EleutherAI via one-line API calls and integrates with TransformerLens for hooked inference. The caveat: **float16 produces "funky results" on MPS** — use float32 or bfloat16 (bfloat16 may require MPS fallback for some operations).

**TransformerLens** runs CI tests on MPS (confirmed by GitHub Actions runner configurations), but no explicit "fully supported" declaration exists. It uses standard PyTorch operations and einops, which compile to MPS-compatible ops. Practical requirements: set `device="mps"`, use `PYTORCH_ENABLE_MPS_FALLBACK=1`, avoid float64. This will work for the core interpretability workflow of hooking activations and running SAEs.

**repeng** (representation engineering) has explicit Apple Silicon support — PR #8 added MPS autodetection to all notebooks. This is directly relevant for computing contrastive "creativity directions" in activation space.

**nnsight** has no documented MPS testing, but offers a crucial workaround: its `remote=True` mode offloads computation to NDIF's CUDA servers, completely bypassing local hardware constraints. For experiments that hit MPS limitations, this is a viable escape hatch.

**pyvene** has no MPS documentation but is architecturally device-agnostic — it wraps HuggingFace models using standard PyTorch hooks. Setting `model.to("mps")` should work for most interventions.

The **PyTorch MPS backend itself** (as of late 2025) supports all standard neural network operations including matrix multiplication, GELU/SiLU activations, attention mechanisms, and forward hooks. Known gaps include no float64, no distributed training (irrelevant for single-machine work), and some niche operations that fall back to CPU. The environment variable `PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0` disables the memory ceiling, critical for large model loading.

## The pre-trained SAE ecosystem is remarkably rich

This is the strongest enabling factor. As of March 2026, the publicly available SAE landscape is comprehensive:

**GemmaScope v1** (Google DeepMind) covers Gemma 2 2B, 9B, and 27B with JumpReLU SAEs at widths from **16K to 1M features**. For Gemma 2 2B, every layer has SAEs at 16K and 65K widths for residual stream, MLP, and attention sites. Layer 12 has the full width sweep up to 1M. All loadable via SAELens with `SAE.from_pretrained(release="gemma-scope-2b-pt-res-canonical", sae_id="...")`.

**GemmaScope v2** extends to Gemma 3 models (270M through 27B, both pretrained and instruction-tuned), adding Matryoshka SAEs, transcoders, and cross-layer transcoders. The 270M and 1B models are particularly interesting for rapid prototyping.

**Llama Scope** (OpenMOSS/Fudan) provides **256 TopK SAEs** for Llama 3.1 8B covering all 32 layers at 4 sublayer sites (residual, attention, MLP, transcoder) at 32K (8×) and 128K (32×) widths. Post-MLP residual stream SAEs are recommended as highest quality. Available via `fnlp/Llama-Scope` on HuggingFace with SAELens integration.

**EleutherAI** offers 32× expansion SAEs for Llama 3.1 8B across all layers via their `sparsify` library. **Goodfire** released a single high-quality SAE for Llama 3.1 8B Instruct at layer 19. A **DeepSeek-R1 SAE** (65K features, layer 19) exists from QResearch.

The best-supported combination for research is **Gemma 2 2B + GemmaScope v1** — it has the most tutorials, Neuronpedia visualization support, SAEBench evaluation scores, and the lowest memory footprint (~6GB total). For Llama-ecosystem work, **Llama 3.1 8B + Llama Scope 32K residual SAEs** is the strongest option at ~18GB total.

## Direction 1: diffusion meta-models are surprisingly feasible but risky

The GLP (Generative Latent Prior) paper from February 2026 has **publicly released code and pre-trained models**. The repository at `github.com/g-luo/generative_latent_prior` includes trained GLPs for both Llama 8B and Llama 1B activations, hosted on HuggingFace under `generative-latent-prior/`. A sanity dataset with 1M pre-cached activations is provided for quick testing, versus the full 1B-activation training set that takes ~5.6 days on unspecified hardware.

Training a small diffusion model on activation vectors is feasible on M4. A DDPM with ~10M parameters operating on 4096-dimensional vectors would consume <1GB for model + gradients, leaving >120GB for batched data. PyTorch MPS supports the necessary operations. **Estimated training time: hours to 2 days** for a model of this scale with the 1M sanity dataset.

**The critical gap**: using GLP for *creative latent navigation* — actively steering toward novel activation regions — goes beyond what the released code does. GLP learns to model the distribution of activations; using it as a *controller* to find novel regions requires custom objectives (e.g., maximizing distance from training distribution while maintaining coherence). This is conceptually straightforward but requires custom engineering that isn't in the released codebase.

**Realistic assessment**: You could (1) reproduce GLP's basic results using their code and pre-trained models within 1–2 days, (2) train a GLP on Gemma 2 2B activations in 1–3 days, and (3) develop a novelty-seeking sampling strategy on top within 1–2 weeks. The total timeline is **3–4 weeks** to a working prototype. Risk factors: MPS training bugs, the need to design and validate a novel sampling objective, and unclear evaluation methodology for "creative" navigation.

## Direction 2: SAE feature archaeology is the most feasible path

Every component for this direction exists, works on Apple Silicon, and requires no model training. The workflow is:

**Step 1 — Run diverse cross-domain inputs through model + SAE (~2–8 hours).** Process 5,000–10,000 text passages spanning distinct knowledge domains (science, music, cooking, law, mathematics, literature) through Gemma 2 2B with GemmaScope SAEs. Record which features activate for each input. SAELens handles this natively on MPS. Storage: ~1–2GB in sparse format.

**Step 2 — Compute feature co-activation patterns (~1–2 hours).** Build a 16K × 16K co-activation matrix (~1GB) showing which features tend to fire together across domains. Identify "bridge features" that activate strongly for multiple unrelated domains — these are candidate cross-domain insight features. This is pure matrix computation, trivially parallelizable on MPS.

**Step 3 — Interrogate bridge features with LatentQA (~1–2 days).** LatentQA code and a pre-trained decoder for Llama 3 8B are publicly available at `github.com/aypan17/latentqa`. The decoder model (`aypan17/latentqa_llama-3-8b-instruct`) translates activation patterns into natural language descriptions. Run bridge feature activations through LatentQA to generate human-readable explanations of what these features represent.

**Step 4 — Steer generation using bridge features (~1–3 days).** Use SAE-TS (code at `github.com/slavachalnev/SAE-TS`) or IBM's sae-steering (`github.com/IBM/sae-steering`) to amplify bridge features during generation. Prompt the model about one domain while amplifying features that bridge to another domain. Measure whether outputs contain genuine cross-domain insights.

**Step 5 — Evaluate with existing benchmarks (~1–2 days).** Use the CREATE benchmark (arXiv:2603.09970, which tests associative creativity via Wikidata knowledge graph paths), ParallelPARC (cross-domain scientific analogies), and standard diversity metrics (Self-BLEU, Distinct-n, MAUVE) to quantify whether bridge-feature steering produces more creative and cross-domain outputs.

**Total timeline: 2–3 weeks** to publishable results. Memory footprint peaks at ~8–10GB. No training required. All code is public. The novel contribution — systematic identification and exploitation of cross-domain bridge features in SAEs — has not been done and addresses a genuine gap in the literature.

**An important simplification**: rather than building the full "archaeology" pipeline, start with the even simpler experiment of replicating the creativity direction approach (arXiv:2412.06060) using SAE features instead of raw activation differences. The creativity direction paper found a linear direction in activation space that correlates with creativity; the novel twist is decomposing this direction into SAE features to make it *interpretable* — identifying which specific features contribute to creativity. This requires repeng (confirmed MPS-compatible) + SAELens (confirmed MPS-compatible) + a creative/uncreative prompt set. **Timeline: 1 week** for a clean result.

## Direction 3: thermodynamic basin-hopping is feasible but least publishable

**Huginn weights are publicly available** at `huggingface.co/tomg-group-umd/huginn-0125` — a 3.5B parameter model with 1.5B in the recurrent block plus 2B in non-recurrent layers. Code is at `github.com/seal-rg/recurrent-pretraining`. At inference with default 32 recurrent steps, effective compute is ~50B parameter-equivalent. The model fits in 128GB unified memory (bfloat16: ~7GB base, with recurrent compute adding no extra weight memory).

However, **simulating recurrent depth in a standard transformer** is more tractable and more interesting for research. Take Gemma 2 2B, select layers 10–14 as a "recurrent block," and iterate 2–100 times. Track hidden state convergence to identify attractor basins. The `locuslab/torchdeq` library provides Anderson acceleration and Jacobian analysis tools for exactly this kind of fixed-point analysis. Implementation effort: **1–2 days for basic iteration, 1 week for full attractor analysis**.

**Lyapunov exponent computation** is feasible via the power method (computing only the maximum exponent rather than the full spectrum). For a 2304-dimensional hidden state (Gemma 2 2B), the Jacobian is 2304 × 2304 ≈ 5.3M entries — computed via PyTorch autograd in seconds. The full QR decomposition method for the Lyapunov spectrum requires tracking the Jacobian across many iterations but remains within memory and compute budgets.

**The problem is evaluation and novelty.** The Concept Attractors paper (Chytas & Singh) was **desk-rejected at ICLR 2026** with no code released. The Magellan paper (MCTS latent exploration) has **no code available**. This means you'd be building most of the evaluation framework from scratch, with limited baselines to compare against. The connection between attractor dynamics and creativity is theoretically compelling but empirically unvalidated. **Risk: high. Timeline: 4–8 weeks** for anything publishable.

## Recommended experiment: SAE-decomposed creativity directions

The single most feasible, rigorous, and publishable experiment is a **hybrid of Directions 2 and the creativity direction replication**:

**Title concept**: "Mechanistic Anatomy of Creativity: Decomposing LLM Creativity Directions into Interpretable SAE Features"

**Method**: (1) Replicate the creativity direction finding from arXiv:2412.06060 using Gemma 2 2B instead of Llama 3 8B, extracting a creativity steering vector via contrastive activation addition with repeng. (2) Project this creativity direction onto GemmaScope SAE features to decompose it into interpretable components. (3) Identify which SAE features have the highest alignment with the creativity direction — these are "creativity features." (4) Validate by individually activating top creativity features and measuring output creativity via automated metrics (Distinct-n, Self-BLEU, MAUVE) and the CREATE benchmark. (5) Discover whether creativity features bridge multiple knowledge domains by analyzing their activation patterns across diverse input corpora. (6) Compare feature-level steering (amplifying individual creativity features) versus direction-level steering (the raw creativity vector) for controllability and side effects.

**Why this works on M4 128GB**: Gemma 2 2B + GemmaScope 65K SAE totals ~6.5GB. Full pipeline uses SAELens (confirmed MPS), repeng (confirmed MPS), and standard PyTorch operations. No training. No custom data generation beyond curating ~200 creative/uncreative prompt pairs (which can be done with existing datasets like Fan et al. 2018's creative writing prompts). Processing 10,000 evaluation inputs takes 2–8 hours.

**Why it's publishable**: No prior work has decomposed creativity steering vectors into SAE features. This bridges two active research areas (representation engineering and sparse autoencoders) with a concrete application (creativity). It produces interpretable, visualizable results (specific features with Neuronpedia descriptions that correlate with creativity). It is reproducible with fully public tools and models.

**Timeline**: **2–3 weeks** from start to a complete experimental result with evaluation.

## What definitively will NOT work on this hardware

For completeness, here are the hard limits: **Training SAEs from scratch on 8B+ models** requires processing billions of tokens and is impractical on MPS (weeks to months). Use pre-trained SAEs instead. **COCONUT training** (continuous chain-of-thought) requires 4× A100 80GB GPUs per the official repo — no local alternative exists. **Running 70B models with full-precision activation hooks** would consume ~150GB+ (model weights + activations), exceeding the 128GB limit. **Full Lyapunov spectrum computation** for 4096-dimensional hidden states (Llama 8B scale) involves 4096 × 4096 Jacobians iterated thousands of times — feasible but slow (days); restrict to Gemma 2 2B (d=2304) or use only the maximum exponent. **MLX for interpretability** is not viable — no TransformerLens/SAELens equivalent exists for MLX, and building one would take weeks with no research value.

## Complete tool and model reference

| Component | Status | Memory on M4 | Source |
|-----------|--------|-------------|--------|
| Gemma 2 2B (FP16) | ✅ Works | ~5 GB | HuggingFace |
| GemmaScope 65K SAE (2B, bf16) | ✅ Works via SAELens | ~604 MB | `google/gemma-scope-2b-pt-res` |
| Llama 3.1 8B (FP16) | ✅ Works | ~16 GB | HuggingFace |
| Llama Scope 32K SAE (8B, bf16) | ✅ Works via SAELens | ~537 MB | `fnlp/Llama-Scope` |
| SAELens | ✅ Confirmed MPS | — | PyPI: `sae-lens` |
| TransformerLens | ⚠️ Likely works, use fallback | — | PyPI: `transformer-lens` |
| repeng | ✅ Confirmed MPS | — | PyPI: `repeng` |
| LatentQA decoder | ✅ Code + model available | ~16 GB | `aypan17/latentqa` |
| GLP code + models | ✅ Available | ~1–2 GB (diffusion model) | `g-luo/generative_latent_prior` |
| Huginn 3.5B | ✅ Weights available | ~7 GB | `tomg-group-umd/huginn-0125` |
| SAE-TS steering | ✅ Code available | — | `slavachalnev/SAE-TS` |
| IBM sae-steering | ✅ Code available | — | `IBM/sae-steering` |
| Activation Oracles | ✅ 12 pre-trained models | varies | `adamkarvonen/activation_oracles` |
| COCONUT | ⚠️ Code only, no weights, needs 4×A100 | N/A | `facebookresearch/coconut` |
| Magellan | ❌ No code | — | — |
| Concept Attractors | ❌ No code, paper desk-rejected | — | — |
| Creativity Direction (2412.06060) | ❌ No code (but method is simple to reimplement) | — | — |

## Conclusion

The M4 MacBook Pro with 128GB unified memory is a legitimate interpretability research machine — not a compromise, but a platform where the unified memory architecture actually provides advantages over discrete GPUs for activation-heavy analysis workflows. The constraining factor is not memory but compute throughput and MPS backend maturity.

**Direction 2 is unambiguously the right choice**, with the specific recommended experiment being SAE decomposition of creativity directions. It minimizes risk (no training, all tools confirmed working, pre-trained SAEs available), maximizes novelty (no prior work on this exact question), and produces inherently interpretable and visualizable results. Start with Gemma 2 2B + GemmaScope 65K residual SAEs as the base configuration — **total memory footprint under 7GB**, leaving 121GB for analysis and caching. If results are promising, scale to Gemma 2 9B or Llama 3.1 8B + Llama Scope for generalization.

Direction 1 (GLP-based navigation) is a strong secondary project once the SAE feature archaeology infrastructure is in place — the GLP code release was an unexpected enabler. Direction 3 (basin-hopping) should be deferred until the interpretability pipeline is mature and can be applied to characterize attractor dynamics, rather than building the dynamics analysis tools first.