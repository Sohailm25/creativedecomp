# Paper Index

This directory is the local paper corpus for the experiment. Every artifact listed in `DOWNLOAD_MANIFEST.md` is intended to exist as a full local file under `background-work/papers/files/` so future agents can review methods and citations without relying on truncated web snippets.

The corpus is organized by how the research docs use it:

- `Current-Phase Core`: papers that directly constrain the active experiment in `research/experiment-novelty.md` and `research/experiment-macbook-guide.md`.
- `Extension And Context`: papers cited in `research/transcript.md` or `research/experiment-ideas.md` that shape secondary directions, controls, or follow-on designs.

Two citation corrections are locked here to prevent future drift:

- The creativity-representation paper cited in the docs is `Von Rütte et al.` rather than the earlier mistaken `Laurito et al.` memory.
- `MuCoLa` in the transcript maps to the gradient-based constrained sampling paper on arXiv (`2205.12558`).

Operational note:

- OpenReview-hosted PDFs in this corpus are materialized through a browser-context fetch in `scripts/download_reference_papers.py` because raw shell HTTP requests to `openreview.net/pdf` return `403` for these papers.

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
- `Concept Attractors`
  Local file: `background-work/papers/files/concept-attractors-2026.pdf`
  Used by: `research/experiment-ideas.md`, `research/experiment-macbook-guide.md`
- `COLD Decoding`
  Local file: `background-work/papers/files/cold-decoding-2022.pdf`
  Used by: `research/experiment-ideas.md`
- `MuCoLa`
  Local file: `background-work/papers/files/mucola-2022.pdf`
  Used by: `research/experiment-ideas.md`
- `Gemma Scope`
  Local file: `background-work/papers/files/gemmascope-2024.pdf`
  Used by: `research/experiment-macbook-guide.md`
