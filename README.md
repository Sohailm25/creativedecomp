# Mechanistic Creativity Decomposition

This workspace mirrors the operating scaffold used in `~/resattn`, but it is adapted to the creativity-direction and SAE-decomposition experiment defined by the local `research/` materials.

## Source Documents

- `research/transcript.md`
- `research/experiment-ideas.md`
- `research/experiment-macbook-guide.md`
- `research/experiment-novelty.md`

## Local Runtime Assumptions

- Execution happens on this MacBook Pro, locally.
- Python runs through `.venv`.
- The expected accelerator is PyTorch MPS with CPU fallback when needed.
- No Modal or remote cluster assumptions belong here.

## Quick Start

```bash
python3 -m venv .venv
.venv/bin/python -m unittest discover -s tests -p 'test*.py'
```

Optional setup:

```bash
.venv/bin/pip install pre-commit
.venv/bin/pre-commit install
bd prime
```

## Operating Scaffold

- `AGENTS.md` is the local operating contract.
- `CURRENT_STATE.md` is the current single-source status file.
- `DECISIONS.md` records non-trivial decisions and pivots.
- `SCRATCHPAD.md` is the pre-run and post-run execution log.
- `THOUGHT_LOG.md` captures research reflections: hunches, predictions, surprises, confidence shifts, and the evolving feel of the experiment.
- `history/PREREG.md` is the preregistered claim and gate document.
- `history/20260318-resattn-scaffold-adaptation.md` records how this scaffold was adapted from `resattn`.
- `background-work/papers/DOWNLOAD_MANIFEST.md` indexes the local paper cache for this experiment.
- `scripts/download_reference_papers.py` refreshes the local paper cache from that manifest.
- `tests/test_scaffold_structure.py` keeps the research scaffold from drifting.
