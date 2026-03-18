# Paper Index

This directory is the local paper corpus for the experiment. Every artifact listed in `DOWNLOAD_MANIFEST.md` is intended to exist as a full local file under `background-work/papers/files/` so future agents can review methods and citations without relying on truncated web snippets.

The corpus is organized by how the research docs use it:

- `Current-Phase Core`: papers that directly constrain the active experiment in `research/experiment-novelty.md` and `research/experiment-macbook-guide.md`.
- `Extension And Context`: papers cited in `research/transcript.md` or `research/experiment-ideas.md` that shape secondary directions, controls, or follow-on designs.

Two citation corrections are locked here to prevent future drift:

- The creativity-representation paper cited in the docs is `Von Rütte et al.` rather than the earlier mistaken `Laurito et al.` memory.
- `MuCoLa` in the transcript maps to the gradient-based constrained sampling paper on arXiv (`2205.12558`).
- The transcript's `Large Language Models as Innovators` reference is treated as the same Bystroński line of work now titled `Geometry of Knowledge Allows Extending Diversity Boundaries of Large Language Models` on arXiv (`2507.13874`).

Operational note:

- OpenReview-hosted PDFs in this corpus are materialized through a browser-context fetch in `scripts/download_reference_papers.py` because raw shell HTTP requests to `openreview.net/pdf` return `403` for these papers.
- `Scaling Monosemanticity` is materialized as a browser-rendered PDF from the canonical Transformer Circuits publication because the site serves the thread as HTML rather than a raw PDF download.
- The OCSAI divergent-thinking paper is stored from the full ERIC-hosted preprint because the publisher PDF endpoint is not openly fetchable from this environment.

## Current-Phase Core

- `Olson et al. creativity steering direction`
  Local file: `background-work/papers/files/olson-creativity-direction-2024.pdf`
  Used by: `research/experiment-novelty.md`, `research/experiment-macbook-guide.md`, `research/experiment-ideas.md`
- `Von Rutte et al. creativity and humor representations`
  Local file: `background-work/papers/files/von-rutte-creativity-humor-representations-2024.pdf`
  Used by: `research/experiment-novelty.md`, `research/experiment-ideas.md`
- `Mayne et al. steering-vector SAE decomposition warnings`
  Local file: `background-work/papers/files/mayne-sae-steering-vector-decomposition-2024.pdf`
  Used by: `research/experiment-novelty.md`
- `SAE-TS`
  Local file: `background-work/papers/files/sae-ts-2024.pdf`
  Used by: `research/experiment-novelty.md`, `research/experiment-macbook-guide.md`, `research/experiment-ideas.md`
- `FGAA`
  Local file: `background-work/papers/files/fgaa-2025.pdf`
  Used by: `research/experiment-novelty.md`, `research/transcript.md`
- `SAS`
  Local file: `background-work/papers/files/sas-2025.pdf`
  Used by: `research/experiment-novelty.md`
- `Arad et al. input versus output SAE features`
  Local file: `background-work/papers/files/arad-input-output-sae-features-2025.pdf`
  Used by: `research/experiment-novelty.md`, `research/experiment-ideas.md`
- `CREATE benchmark`
  Local file: `background-work/papers/files/create-benchmark-2026.pdf`
  Used by: `research/experiment-novelty.md`, `research/experiment-macbook-guide.md`
- `BILLY persona steering for creative generation`
  Local file: `background-work/papers/files/billy-persona-steering-2025.pdf`
  Used by: `research/experiment-novelty.md`
- `Geometry of Knowledge creative latent exploration`
  Local file: `background-work/papers/files/geometry-of-knowledge-creative-latent-exploration-2025.pdf`
  Used by: `research/experiment-novelty.md`
- `There Is More to Refusal`
  Local file: `background-work/papers/files/there-is-more-to-refusal-2026.pdf`
  Used by: `research/experiment-novelty.md`
- `CreativityPrism`
  Local file: `background-work/papers/files/creativityprism-2025.pdf`
  Used by: `research/experiment-novelty.md`
- `LatentQA`
  Local file: `background-work/papers/files/latentqa-2024.pdf`
  Used by: `research/experiment-macbook-guide.md`, `research/experiment-ideas.md`, `research/transcript.md`
- `Activation Oracles`
  Local file: `background-work/papers/files/activation-oracles-2025.pdf`
  Used by: `research/experiment-macbook-guide.md`, `research/transcript.md`
- `Scaling and evaluating sparse autoencoders`
  Local file: `background-work/papers/files/scaling-and-evaluating-sparse-autoencoders-2024.pdf`
  Used by: `research/experiment-novelty.md`
- `Sparse Autoencoders Find Highly Interpretable Features in Language Models`
  Local file: `background-work/papers/files/sparse-autoencoders-interpretable-features-2023.pdf`
  Used by: `research/experiment-novelty.md`, `research/experiment-ideas.md`
- `Refusal in Language Models Is Mediated by a Single Direction`
  Local file: `background-work/papers/files/refusal-single-direction-2024.pdf`
  Used by: `research/experiment-novelty.md`
- `AxBench`
  Local file: `background-work/papers/files/axbench-2025.pdf`
  Used by: `research/experiment-ideas.md`
- `NoveltyBench`
  Local file: `background-work/papers/files/noveltybench-2025.pdf`
  Used by: `research/experiment-novelty.md`
- `ParallelPARC`
  Local file: `background-work/papers/files/parallelparc-2024.pdf`
  Used by: `research/experiment-macbook-guide.md`
- `Hierarchical Neural Story Generation`
  Local file: `background-work/papers/files/hierarchical-neural-story-generation-2018.pdf`
  Used by: `research/experiment-macbook-guide.md`
- `Art or Artifice? Large Language Models and the False Promise of Creativity`
  Local file: `background-work/papers/files/art-or-artifice-2023.pdf`
  Used by: `research/experiment-novelty.md`
- `Sparking Scientific Creativity via LLM-Driven Interdisciplinary Inspiration`
  Local file: `background-work/papers/files/sparking-scientific-creativity-2026.pdf`
  Used by: `research/transcript.md`

## Extension And Context

- `ReFT`
  Local file: `background-work/papers/files/reft-representation-finetuning-2024.pdf`
  Used by: `research/transcript.md`
- `CS-ReFT`
  Local file: `background-work/papers/files/cs-reft-2025.pdf`
  Used by: `research/transcript.md`
- `Representation Engineering: A Top-Down Approach to AI Transparency`
  Local file: `background-work/papers/files/representation-engineering-2023.pdf`
  Used by: `research/transcript.md`, `research/experiment-ideas.md`
- `Steering Language Models With Activation Engineering`
  Local file: `background-work/papers/files/steering-language-models-activation-engineering-2023.pdf`
  Used by: `research/experiment-ideas.md`
- `Steering Llama 2 via Contrastive Activation Addition`
  Local file: `background-work/papers/files/steering-llama2-contrastive-activation-addition-2023.pdf`
  Used by: `research/experiment-ideas.md`
- `SADI`
  Local file: `background-work/papers/files/sadi-2025.pdf`
  Used by: `research/experiment-ideas.md`
- `CAST`
  Local file: `background-work/papers/files/cast-2025.pdf`
  Used by: `research/experiment-ideas.md`
- `Steering Large Language Models using Conceptors: Improving Addition-Based Activation Engineering`
  Local file: `background-work/papers/files/conceptor-steering-2024.pdf`
  Used by: `research/transcript.md`, `research/experiment-ideas.md`
- `Beyond Linear Steering: Unified Multi-Attribute Control for Language Models`
  Local file: `background-work/papers/files/k-steering-2025.pdf`
  Used by: `research/experiment-ideas.md`
- `Patchscopes`
  Local file: `background-work/papers/files/patchscopes-2024.pdf`
  Used by: `research/transcript.md`
- `Meta-Models`
  Local file: `background-work/papers/files/meta-models-2024.pdf`
  Used by: `research/transcript.md`
- `Generative Meta-Models`
  Local file: `background-work/papers/files/generative-meta-models-2026.pdf`
  Used by: `research/transcript.md`, `research/experiment-macbook-guide.md`
- `Activation State Machines`
  Local file: `background-work/papers/files/activation-state-machines-2025.pdf`
  Used by: `research/transcript.md`
- `Weighted Activation Steering`
  Local file: `background-work/papers/files/weighted-activation-steering-2025.pdf`
  Used by: `research/transcript.md`, `research/experiment-ideas.md`
- `LayerNavigator`
  Local file: `background-work/papers/files/layernavigator-2025.pdf`
  Used by: `research/transcript.md`
- `Magellan: Guided MCTS for Latent Space Exploration and Novelty Generation`
  Local file: `background-work/papers/files/magellan-2025.pdf`
  Used by: `research/transcript.md`, `research/experiment-ideas.md`, `research/experiment-macbook-guide.md`
- `Large Language Models for Scientific Idea Generation: A Creativity-Centered Survey`
  Local file: `background-work/papers/files/scientific-idea-generation-creativity-survey-2025.pdf`
  Used by: `research/experiment-ideas.md`
- `Scaling Monosemanticity: Extracting Interpretable Features from Claude 3 Sonnet`
  Local file: `background-work/papers/files/scaling-monosemanticity-2024.pdf`
  Used by: `research/experiment-novelty.md`, `research/experiment-ideas.md`
- `The Geometry of Concepts: Sparse Autoencoder Feature Structure`
  Local file: `background-work/papers/files/geometry-of-concepts-2024.pdf`
  Used by: `research/experiment-ideas.md`
- `Concept Attractors`
  Local file: `background-work/papers/files/concept-attractors-2026.pdf`
  Used by: `research/experiment-ideas.md`, `research/experiment-macbook-guide.md`
- `COLD Decoding`
  Local file: `background-work/papers/files/cold-decoding-2022.pdf`
  Used by: `research/experiment-ideas.md`
- `MuCoLa`
  Local file: `background-work/papers/files/mucola-2022.pdf`
  Used by: `research/experiment-ideas.md`
- `Scaling up Test-Time Compute with Latent Reasoning: A Recurrent Depth Approach`
  Local file: `background-work/papers/files/huginn-recurrent-depth-2025.pdf`
  Used by: `research/experiment-ideas.md`, `research/experiment-macbook-guide.md`
- `Training Large Language Models to Reason in a Continuous Latent Space`
  Local file: `background-work/papers/files/coconut-2024.pdf`
  Used by: `research/experiment-ideas.md`, `research/experiment-macbook-guide.md`
- `LaDiR: Latent Diffusion for Reasoning in Large Language Models`
  Local file: `background-work/papers/files/ladir-2025.pdf`
  Used by: `research/experiment-ideas.md`
- `Think Silently, Think Fast: Dynamic Latent Compression of LLM Reasoning Chains`
  Local file: `background-work/papers/files/colar-2025.pdf`
  Used by: `research/experiment-ideas.md`
- `Dynamic Large Concept Models: Latent Reasoning in an Adaptive Semantic Space`
  Local file: `background-work/papers/files/dlcm-2025.pdf`
  Used by: `research/experiment-ideas.md`
- `Discovering Latent Knowledge in Language Models Without Supervision`
  Local file: `background-work/papers/files/ccs-2022.pdf`
  Used by: `research/experiment-ideas.md`
- `Towards eliciting latent knowledge from LLMs with mechanistic interpretability`
  Local file: `background-work/papers/files/taboo-models-2025.pdf`
  Used by: `research/experiment-ideas.md`
- `Automated Creativity Evaluation for Large Language Models: A Reference-Based Approach`
  Local file: `background-work/papers/files/automated-creativity-evaluation-2025.pdf`
  Used by: `research/experiment-novelty.md`
- `Do LLMs Agree on the Creativity Evaluation of Alternative Uses?`
  Local file: `background-work/papers/files/rabeyah-alternative-uses-evaluation-2024.pdf`
  Used by: `research/experiment-novelty.md`
- `Beyond semantic distance: Automated scoring of divergent thinking greatly improves with large language models`
  Local file: `background-work/papers/files/ocsai-divergent-thinking-scoring-2023.pdf`
  Used by: `research/experiment-novelty.md`
- `Unveiling Attractor Cycles in Large Language Models: A Dynamical Systems View of Successive Paraphrasing`
  Local file: `background-work/papers/files/attractor-cycles-successive-paraphrasing-2025.pdf`
  Used by: `research/experiment-ideas.md`
- `Critical Phase Transition in Large Language Models`
  Local file: `background-work/papers/files/critical-phase-transition-llms-2024.pdf`
  Used by: `research/experiment-ideas.md`
- `Cognitive Activation and Chaotic Dynamics in Large Language Models: A Quasi-Lyapunov Analysis of Reasoning Mechanisms`
  Local file: `background-work/papers/files/lyapunov-reasoning-mechanisms-2025.pdf`
  Used by: `research/experiment-ideas.md`, `research/experiment-macbook-guide.md`
- `SAE-SSV`
  Local file: `background-work/papers/files/sae-ssv-2025.pdf`
  Used by: `research/experiment-novelty.md`
- `Gemma Scope`
  Local file: `background-work/papers/files/gemmascope-2024.pdf`
  Used by: `research/experiment-macbook-guide.md`
