# Scratchpad

Use this file for execution checkpoints and transient notes. Every substantial local run should have a pre-run and post-run entry.

## Pre-Run Template

```text
## [TIMESTAMP] PRE-RUN: [run name]
- tmux session: [session name or N/A]
- Script: `scripts/[filename].py`
- Command: `.venv/bin/python ...`
- Device: `mps` / `cpu`
- Model: [exact model id]
- SAE: [release / layer / width or N/A]
- Data slice: [dataset / number of prompts / split]
- Output path: `results/...`
- What I'm testing: [one sentence]
- Expected outcome: [one sentence]
- Checkpoint path: [path or N/A]
- Checkpoint cadence: [every N steps / minutes / epochs]
- Log path: [path]
- Resume command: [exact command]
- Main confound to watch: [one sentence]
- Implementation verified: YES/NO - [what local check was run]
- Status: LAUNCHING
```

## Post-Run Template

```text
## [TIMESTAMP] POST-RUN: [run name]
- Command: `.venv/bin/python ...`
- Outcome: SUCCESS / FAILURE / PARTIAL
- Key metric: [main number]
- Artifacts saved: `results/...`
- Latest checkpoint: [path or none]
- Anomalies: [unexpected behavior or `none`]
- Next step: [single next action]
```

## Bootstrap Notes

- No creativity experiments have been executed from this scaffold yet.
- The first completed verification step is the scaffold structure regression test.
- The repo-boundary decision is still unresolved because the git root is currently `/Users/sohailmo`.

## 2026-03-18T10:00:03-0500 PRE-RUN: initial runtime freeze and prompt split

- tmux session: N/A
- Script: `scripts/freeze_initial_runtime_and_prompt_split.py`
- Command: `.venv/bin/pip install torch transformers sae-lens repeng datasets accelerate safetensors sentencepiece scipy && .venv/bin/python scripts/freeze_initial_runtime_and_prompt_split.py`
- Device: `mps`
- Model: `google/gemma-2-2b`
- SAE: `gemma-scope-2b-pt-res-canonical / layer_12 / width_65k`
- Data slice: `WritingPrompts-derived base prompt split / 32 pilot / 128 confirm`
- Output path: `prompts/creative_direction_v1_*.jsonl`, `requirements*.txt`, `results/infrastructure/...`
- What I'm testing: whether the first local runtime can be frozen around a working Gemma/SAE stack and a deterministic prompt registry.
- Expected outcome: a real requirements freeze, a real lockfile, and disjoint pilot/confirm prompt splits with instruction templates.
- Checkpoint path: N/A
- Checkpoint cadence: N/A
- Log path: `sessions/20260318-session005.md`
- Resume command: `.venv/bin/python scripts/freeze_initial_runtime_and_prompt_split.py`
- Main confound to watch: Python 3.14 dependency resolution may succeed on paper but fail at real install or import time.
- Implementation verified: NO - install and import smoke still pending
- Status: LAUNCHING

## 2026-03-18T10:04:34-0500 POST-RUN: initial runtime freeze and prompt split

- Command: `.venv/bin/pip install torch==2.10.0 transformers==5.3.0 sae-lens==6.38.0 repeng==0.4.0 datasets==4.8.2 accelerate==1.13.0 safetensors==0.7.0 sentencepiece==0.2.1 scipy==1.17.1 && .venv/bin/python scripts/freeze_initial_runtime_and_prompt_split.py`
- Outcome: SUCCESS
- Key metric: `32` pilot prompts and `128` confirm prompts frozen with a real importable runtime
- Artifacts saved: `prompts/creative_direction_v1_*.jsonl`, `prompts/creative_direction_v1_metadata.json`, `prompts/creative_direction_v1_templates.json`, `requirements.txt`, `requirements.lock.txt`, `results/infrastructure/20260318-initial-runtime-and-prompt-freeze.md`
- Latest checkpoint: none
- Anomalies: `steering-vectors` resolves against a different `transformers` line than the base `repeng` stack, so it was intentionally excluded from the first freeze
- Next step: run the first `google/gemma-2-2b` creativity-direction smoke on the pilot split

## 2026-03-18T10:22:00-0500 PRE-RUN: creativity-direction repeng smoke

- tmux session: N/A
- Script: `scripts/run_creativity_direction_smoke.py`
- Command: `.venv/bin/python scripts/run_creativity_direction_smoke.py --output-dir results/creativity_direction/20260318-gemma2-2b-repeng-smoke-layer12`
- Device: `mps`
- Model: `google/gemma-2-2b`
- SAE: `N/A for this smoke`; this run only checks dense creativity-direction extraction before decomposition
- Data slice: `creative_direction_v1_pilot / 32 prompt pairs`
- Output path: `results/creativity_direction/20260318-gemma2-2b-repeng-smoke-layer12`
- What I'm testing: whether the frozen pilot split yields a reproducible dense creativity direction artifact on the default local model and layer.
- Expected outcome: a saved dense direction vector plus pairwise projection summaries showing the extraction path works end to end.
- Checkpoint path: N/A
- Checkpoint cadence: N/A
- Log path: `sessions/20260318-session005.md`
- Resume command: `.venv/bin/python scripts/run_creativity_direction_smoke.py --output-dir results/creativity_direction/20260318-gemma2-2b-repeng-smoke-layer12 --overwrite`
- Main confound to watch: strong positive-vs-negative separation on the training pairs is only a smoke indicator, not confirmatory evidence of useful creativity steering.
- Implementation verified: YES - unit test for dataset/projection summaries plus local two-pair MPS extraction smoke
- Status: LAUNCHING

## 2026-03-18T10:40:15-0500 POST-RUN: creativity-direction repeng smoke

- Command: `.venv/bin/python scripts/run_creativity_direction_smoke.py --output-dir results/creativity_direction/20260318-gemma2-2b-repeng-smoke-layer12 --overwrite`
- Outcome: SUCCESS
- Key metric: positive projections exceeded negative projections on `23 / 32` prompt pairs (`0.71875`), with mean margin `1.579252`
- Artifacts saved: `results/creativity_direction/20260318-gemma2-2b-repeng-smoke-layer12/`
- Latest checkpoint: none
- Anomalies: the first implementation path produced projection warnings from BLAS-backed matrix multiply even though all values were finite; the run artifact was regenerated with a stable multiply-plus-sum projection path to remove that confound
- Next step: run a pilot layer sweep before treating layer 12 as anything more than the scaffold default
