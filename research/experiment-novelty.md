# Mechanistic creativity decomposition: what exists and what doesn't

**The proposed experiment — decomposing an LLM creativity steering vector into interpretable SAE features — has not been done.** Every individual methodological component exists and has been validated on other behavioral concepts (refusal, sycophancy, sentiment), and a creativity steering vector has been extracted in at least one published study, but no one has connected these two lines of work. The gap is real, significant, and well-positioned for a novel contribution. However, several technical pitfalls — particularly the out-of-distribution problem with SAE decomposition of steering vectors — must be addressed for the experiment to succeed.

This report maps every relevant piece of prior work, identifies exactly where the novelty lies, and flags the critical methodological decisions that will determine success or failure.

---

## The creativity steering vector already exists — but remains a black box

**Olson et al. (arXiv:2412.06060, December 2024)** is the most directly relevant prior work for the first half of the proposed experiment. Working at Intel Labs, they extracted a creativity direction from **Llama-3-8B at layer 8** using contrastive activation addition. Their method: sample 500 writing prompts from Fan et al.'s creative writing dataset, generate creative stories, then use GPT-4o to craft "uncreative" counterparts. The creativity direction is the normalized difference in mean activations between creative and uncreative instructions. At inference, they add this vector (scaled by **λ = 3**) to layer 8 activations, producing outputs judges rate as substantially more creative. They also demonstrate a cosine-similarity-based creativity scoring method that aligns with human judgment far better than prompt-based self-evaluation.

What Olson et al. explicitly did **not** do: any form of decomposition, mechanistic analysis, or interpretability investigation. They treat the creativity direction as a monolithic vector. No SAEs, no feature analysis, no investigation of what the vector encodes. The paper even cites Gao et al. (2024) on scaling SAEs and Templeton et al. (2024) on interpretable features but does not apply these methods.

**Von Rütte et al. (ICML 2024, arXiv:2402.14433)** — likely the paper misremembered as "Laurito et al." — provides crucial complementary evidence. Working with **Mistral-7B**, they used linear probes (logistic regression, difference-in-means) to study creativity, humor, quality, truthfulness, and appropriateness as internal representations. Their central finding: **creativity can be detected in activations but is significantly harder to guide than truthfulness**. Probes with optimal detection accuracy do not make optimal steering guides — a finding that contradicts earlier results for simpler concepts. This paper introduces a perplexity-normalized effect size metric but provides no mechanistic explanation for why creativity guidance fails, creating a direct motivation for SAE decomposition.

Two additional creativity-steering papers provide context. **BILLY (Pai et al., arXiv:2510.10157, October 2025)** extracts persona vectors (e.g., "creative professional") and blends them in activation space for creative generation, outperforming multi-agent approaches but without SAE analysis. **Bystroński et al. (arXiv:2507.13874, July 2025)** — the "Geometry of Knowledge" paper — achieves **AUT originality scores of 4.99/5.0** but through latent-space exploration with an xRAG-style projector, not activation steering. Their 4.99 score reflects a best-of-500 selection, not per-generation creativity increase, and their method is fundamentally about diversity sampling rather than representation engineering.

No paper by "Laurito et al." on creativity and humor representations was found despite exhaustive searching. This citation appears to be erroneous.

---

## SAE decomposition of steering vectors: a maturing but treacherous field

The methodological foundation for projecting steering vectors onto SAE features is well-established but comes with **critical technical warnings** that will make or break the proposed experiment.

**The GDM team's early work (Conmy, Nanda et al., Alignment Forum, 2024)** was the first to decompose steering vectors into SAE features. Using GPT-2 XL with a layer 20 residual stream SAE, they decomposed "anger" and "wedding" vectors. For anger, a single SAE feature provided a **Pareto improvement** over the original steering vector. For weddings, results were mixed — the SAE reconstruction was slightly worse, though removing irrelevant features helped. This established both the promise and the limitations of the approach.

**Mayne, Yang & Mahdi (arXiv:2411.08790, November 2024)** then delivered the most important methodological caution. Their paper, "Can Sparse Autoencoders Be Used to Decompose and Interpret Steering Vectors?", identifies **two fundamental problems** with directly encoding steering vectors through SAEs. First, steering vectors (computed as activation differences) have L2 norms outside the distribution SAEs are trained on, causing the encoder bias to dominate decomposition and produce misleading results. Second, SAEs enforce non-negative reconstruction coefficients, but steering vectors have meaningful *negative* projections onto features (features that should be suppressed). In their study of corrigibility, **51.2%** of relevant features activated more strongly on negative prompts — information entirely lost by standard SAE encoding. They recommend alternative approaches: gradient pursuit, FISTA, or decomposing positive and negative prompt activations separately before subtracting.

**The neverix/Kharlapenko/Conmy/Nanda team (Alignment Forum, October 2024)** validated the gradient pursuit approach, successfully decomposing refusal and sycophancy steering vectors into SAE features in Phi-3 Mini and Gemma 1. For refusal, just **2 SAE features** via gradient pursuit reconstructed and even surpassed the original vector. A "truthful" feature extracted from the sycophancy vector correctly identified MMLU answers 56.1% of the time. This is the strongest proof-of-concept that behavioral directions decompose into a small number of interpretable features.

Three major 2025 papers advance SAE-based steering further. **SAE-TS (Chalnev, Siu & Conmy, arXiv:2411.02193)** constructs steering vectors by optimizing in SAE-feature-effect space using **Gemma-2-2B/9B with GemmaScope 16k SAEs at layer 12**. Their critical insight: cosine-similar decoder directions do NOT necessarily correspond to similar behavioral effects. **FGAA (Soo et al., arXiv:2501.09929, ICLR 2025 Building Trust Workshop)** combines contrastive decomposition in SAE space with SAE-TS optimization, outperforming all alternatives on 8/9 tasks. **SAS (Bayat et al., arXiv:2503.00177, COLM 2025)** constructs steering vectors entirely in sparse space, sidestepping OOD issues by never trying to encode dense vectors through the SAE.

**Arad, Mueller & Belinkov (EMNLP 2025, arXiv:2505.20063)** contribute the crucial distinction between **input features** (activated by relevant inputs) and **output features** (causally modify outputs when amplified). These rarely co-occur. After filtering for output features, SAE steering achieves **2-3× improvement**, making it competitive with supervised methods on AxBench.

---

## Nobody has looked for creativity features in SAEs

Despite the existence of **400+ freely available GemmaScope SAEs** covering Gemma 2 2B, 9B, and select 27B layers, and despite Neuronpedia hosting **50M+ feature dashboards** with auto-generated explanations, no published work has systematically searched for creativity-related features. The closest precedent is a Stanford CS191 project (Tey, 2024) that identified fantasy-genre features for style transfer — demonstrating that writing-style features exist in SAE latent spaces — but "creativity" as a broader concept remains unexplored.

Anthropic's Scaling Monosemanticity work (Templeton et al., 2024) found highly abstract features in Claude 3 Sonnet — including sycophantic praise, deception, and code-bug features that span languages and modalities — proving that behavioral concepts can be captured as monosemantic features at scale. Some features implicitly bridge domains (e.g., a "popular tourist attractions" feature responding to diverse locations globally), but **no one has studied cross-domain bridging as a mechanism for creative association**.

A critical caveat from **Karvonen et al. (2024)**: SAE features are highly dataset-dependent. SAEs trained on generic web text may entirely miss creativity-specific features. The most refusal-related feature from a web-text SAE underperformed the refusal direction, while chat-specific SAEs produced far better features. For creativity, SAEs trained on corpora including creative writing may be necessary.

---

## Behavioral decomposition via SAEs is well-established for other concepts

Refusal is the most extensively studied behavioral direction in SAE feature space. **Arditi et al. (NeurIPS 2024)** showed refusal is mediated by a single direction. Subsequent work revealed a more nuanced picture: "There Is More to Refusal" (arXiv:2602.02132, 2025) found a reusable refusal core of shared SAE latents plus category-specific specialized features across 11 refusal categories. Multiple teams have identified minimal feature sets whose ablation flips refusal to compliance.

For sycophancy, gradient pursuit decomposition revealed interpretable features including a "truthful" feature with practical utility. For sentiment, **SAE-SSV (He et al., EMNLP 2025)** reported top-10 SAE features per task with Neuronpedia labels, finding sentiment features are concentrated while truthfulness features are more distributed. The consistent finding across all behavioral concepts: **2-30 SAE features** typically capture a behavioral direction. The key open question for creativity is whether it follows this pattern or is more diffusely distributed — which would be an important finding either way.

Methods that have been validated for behavioral decomposition include:

- **Gradient pursuit / FISTA**: Best for decomposing arbitrary vectors into SAE features (avoids OOD issues)
- **Contrastive decomposition in SAE space**: Encode positive and negative prompt activations separately, then subtract
- **Supervised feature selection**: Train classifiers to identify discriminative SAE dimensions (SAE-SSV)
- **Semantic denoising**: Use LLM judges to filter relevant vs. irrelevant features (SAE-RSV)
- **Output-score filtering**: Select features that causally affect outputs, not just those activated by inputs (Arad et al.)

---

## The evaluation toolkit for creativity is mature and growing

A robust battery of creativity metrics exists. **CREATE (arXiv:2603.09970, March 2026)** is brand-new — published just one week ago — and tests associative creativity by requiring LLMs to generate multi-hop reasoning paths connecting real-world concepts across domains, scored on specificity and diversity. It explicitly addresses the saturation problem: standard creativity tests like AUT, DAT, and RAT are "comparatively easy for LLMs."

For divergent thinking, **AUT with Ocsai scoring** (Organisciak et al., 2023) achieves **r = 0.81** correlation with human raters via fine-tuned LLMs — approaching the inter-rater reliability ceiling. LLM-as-judge approaches show high inter-model agreement (Spearman > 0.7) for AUT evaluation (Rabeyah et al., ICCC 2025).

For creative writing, **TTCW (Chakrabarty et al., CHI 2024)** provides 14 binary tests across four Torrance dimensions. The automated reference-based extension (EMNLP 2025 Findings) achieves 0.75 pairwise accuracy, enabling scalable evaluation.

**NoveltyBench (COLM 2025)** measures output diversity using functional equivalence classes rather than surface metrics, finding all frontier models produce fewer than 4 distinct responses across 10 queries. **CreativityPrism (arXiv:2510.20091)** provides the most comprehensive framework with 9 tasks, 3 domains, and 20 metrics.

Self-BLEU, Distinct-n, and MAUVE serve as baseline diversity metrics but are increasingly recognized as insufficient alone. Self-BLEU captures only lexical overlap; MAUVE captures distributional quality-diversity tradeoffs but requires large sample sizes. The Vendi Score and NoveltyBench's equivalence-class approach are more principled alternatives.

---

## Tools and implementation are ready for this experiment

The technical infrastructure exists. **SAELens** (github.com/decoderesearch/SAELens) supports loading GemmaScope SAEs with a single function call. The core projection operation is straightforward:

```python
sae = SAE.from_pretrained(
    release="gemma-scope-2b-pt-res-canonical",
    sae_id="layer_12/width_16k/canonical"
)
cosine_sims = F.cosine_similarity(creativity_vector.unsqueeze(0), sae.W_dec, dim=-1)
```

**repeng** (github.com/vgel/repeng) extracts control vectors from any HuggingFace model via PCA on contrastive activation differences. It works with Gemma 2 models and exports per-layer vectors that can be manually projected onto SAE features. The **steering-vectors** library (github.com/steering-vectors/steering-vectors) provides an alternative with explicit Gemma support.

The **SAE-TS repository** (github.com/slavachalnev/SAE-TS) provides the most complete combined pipeline: steering vectors → SAE feature effects → optimization, using Gemma-2-2B with GemmaScope SAEs. The EffectVis tool (effectvis.vercel.app) offers interactive exploration. **GemmaScope** provides SAEs at multiple widths (16k, 32k, 65k, 131k) across all layers and sublayers for Gemma 2 2B and 9B.

The key implementation caveat: repeng has no native SAE integration, so interfacing requires extracting per-layer vectors and manually feeding them to SAELens. TransformerLens v2.0 moved HookedSAE to SAELens, so the recommended stack is SAELens's `HookedSAETransformer` for integrated analysis.

---

## Precise gap analysis and framing recommendations

**What has been done that directly overlaps:**

The creativity direction extraction (Step 1) replicates Olson et al. on a different model. Projecting behavioral vectors onto SAE features (Step 2-3) has been done for refusal, sycophancy, corrigibility, and ICL task vectors. Activating individual features and measuring behavioral effects (Step 4) is standard since Anthropic's Scaling Monosemanticity. Comparing feature-level vs. direction-level steering (Step 6) has been benchmarked across multiple papers for safety and sentiment concepts.

**What has NOT been done — the genuine novelty:**

Nobody has decomposed a creativity steering vector into SAE features. Nobody has identified creativity-specific features in any SAE suite. Nobody has studied whether creativity features bridge knowledge domains. Nobody has compared feature-level vs. direction-level steering for creativity specifically. Nobody has provided a mechanistic explanation for Von Rütte et al.'s finding that creativity is harder to guide than truthfulness. The proposed experiment fills all of these gaps simultaneously.

**Optimal framing for maximum novelty:**

Frame the paper not as "decomposing a creativity vector into SAE features" (which sounds like a straightforward application of existing methods) but as **investigating why creativity is mechanistically different from simpler behavioral concepts at the feature level**. The key question: does creativity decompose into a sparse set of interpretable features like refusal does (2 features sufficed), or is it fundamentally more distributed, polysemantic, and cross-domain? Either answer is interesting — a clean decomposition reveals the anatomy of machine creativity, while a noisy decomposition provides mechanistic evidence for why creativity resists simple steering.

**Anticipated pitfalls and negative results:**

The most serious risk is that the creativity direction decomposes into noise rather than clean features. Von Rütte et al.'s finding that creativity is harder to guide than truthfulness, combined with the superposition hypothesis (creativity may involve simultaneous activation of many cross-domain features), suggests the decomposition may be significantly messier than refusal. Mayne et al.'s OOD and negative-projection warnings apply directly — **do not naively encode the steering vector through the SAE**. Use contrastive decomposition (encode creative and uncreative activations separately, then subtract) or gradient pursuit. SAE training data dependency (Karvonen et al.) means GemmaScope SAEs trained on generic web text may lack creativity-specific features entirely. The Goodfire evaluation found that SAE-based "be creative" steering caused coherence breakdown and repetitive metadata, suggesting creativity features may be entangled with style/formatting features. Finally, Arad et al.'s input-output feature distinction is critical: features that activate on creative text (input features) may not causally produce creative output when amplified (output features).

**The strongest version of this experiment** would: (1) use Gemma-2-9B with GemmaScope SAEs for richer feature spaces; (2) employ multiple decomposition methods (contrastive SAE encoding, gradient pursuit, SAE-SSV's supervised approach) and compare results; (3) validate with both Arad et al.'s output-score metric and direct behavioral measurement (AUT + Ocsai, NoveltyBench, TTCW); (4) explicitly compare the sparsity/interpretability of creativity decomposition against refusal and sentiment as baselines; and (5) test whether top creativity features activate on cross-domain association tasks (CREATE benchmark, ParallelPARC) to probe the domain-bridging hypothesis. This design turns even a negative result — creativity resists clean decomposition — into a publishable finding about the mechanistic structure of abstract behavioral concepts in LLMs.

---

## Conclusion

The proposed experiment sits at a genuine intersection of two active but disconnected research lines. The creativity-steering literature (Olson et al., Von Rütte et al., BILLY) has demonstrated that LLMs encode creativity as a linear direction but has not investigated what this direction is composed of. The SAE-steering literature (SAE-TS, FGAA, SAS, and behavioral decomposition work) has built sophisticated tools for connecting steering vectors to interpretable features but has never applied them to creativity. The proposed work would be the first to bridge this gap. The primary risk is not that the experiment replicates existing work — it clearly does not — but that creativity may prove too distributed or polysemantic for clean SAE decomposition. Designing the experiment to treat this outcome as informative rather than as failure is essential. The tools, SAE suites, evaluation metrics, and methodological precedents are all mature and available; the experiment is ready to execute.