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

## 2026-03-18T10:50:30-0500 PRE-RUN: creativity-direction pilot layer sweep

- tmux session: N/A
- Script: `scripts/run_creativity_direction_layer_sweep.py`
- Command: `.venv/bin/python scripts/run_creativity_direction_layer_sweep.py --output-dir results/creativity_direction/20260318-gemma2-2b-layer-sweep-pilot`
- Device: `mps`
- Model: `google/gemma-2-2b`
- SAE: `N/A for this run`; this is still the dense-direction pilot selection step before decomposition
- Data slice: `creative_direction_v1_pilot / 32 prompt pairs / all transformer layers`
- Output path: `results/creativity_direction/20260318-gemma2-2b-layer-sweep-pilot`
- What I'm testing: which dense-direction extraction layer best separates creative and uncreative prompt pairs on the frozen pilot split under the same extraction math used in the first smoke artifact.
- Expected outcome: a ranked layer table, saved directions, and a provisional best layer for the next generation-side steering smoke.
- Checkpoint path: N/A
- Checkpoint cadence: N/A
- Log path: `sessions/20260318-session006.md`
- Resume command: `.venv/bin/python scripts/run_creativity_direction_layer_sweep.py --output-dir results/creativity_direction/20260318-gemma2-2b-layer-sweep-pilot --overwrite`
- Main confound to watch: training-pair separation is a pilot heuristic for layer choice, not a claim that the chosen layer produces genuinely more creative generations.
- Implementation verified: YES - unit tests for layer parsing/ranking plus prior dense-direction smoke on the same prompt split
- Status: LAUNCHING

## 2026-03-18T10:50:00-0500 POST-RUN: creativity-direction pilot layer sweep

- Command: `.venv/bin/python scripts/run_creativity_direction_layer_sweep.py --output-dir results/creativity_direction/20260318-gemma2-2b-layer-sweep-pilot`
- Outcome: SUCCESS
- Key metric: raw sweep winner `layer 0` with `1.000000` positive-greater-than-negative fraction; best later-layer candidate `layer 7` with `0.906250`
- Artifacts saved: `results/creativity_direction/20260318-gemma2-2b-layer-sweep-pilot/`
- Latest checkpoint: none
- Anomalies: the raw winner is likely confounded by lexical differences between the creative and uncreative instruction templates, so it should not be treated as a frozen creativity layer
- Next step: compare layer `0` and layer `7` in a generation-side smoke before promoting either one

## 2026-03-18T10:58:30-0500 PRE-RUN: generation-side creativity smoke

- tmux session: N/A
- Script: `scripts/run_generation_side_creativity_smoke.py`
- Command: `.venv/bin/python scripts/run_generation_side_creativity_smoke.py --sweep-dir results/creativity_direction/20260318-gemma2-2b-layer-sweep-pilot --output-dir results/steering_eval/20260318-gemma2-2b-generation-smoke`
- Device: `mps`
- Model: `google/gemma-2-2b`
- SAE: `N/A for this run`; this is dense-direction steering before SAE decomposition
- Data slice: `creative_direction_v1_pilot / first 4 prompts / neutral prompt comparison plus prompt-only creativity baseline`
- Output path: `results/steering_eval/20260318-gemma2-2b-generation-smoke`
- What I'm testing: whether the raw sweep winner layer `0` and the next-ranked layer `7` produce meaningfully different generation behavior under the same neutral prompt setup.
- Expected outcome: a small saved comparison showing whether early-layer steering looks like lexical template leakage rather than a usable creativity control.
- Checkpoint path: N/A
- Checkpoint cadence: N/A
- Log path: `sessions/20260318-session006.md`
- Resume command: `.venv/bin/python scripts/run_generation_side_creativity_smoke.py --sweep-dir results/creativity_direction/20260318-gemma2-2b-layer-sweep-pilot --output-dir results/steering_eval/20260318-gemma2-2b-generation-smoke --overwrite`
- Main confound to watch: sampled generations are noisy, so a tiny smoke run can only surface obvious failure modes or gross qualitative differences, not establish a real creativity effect.
- Implementation verified: YES - unit tests for condition construction plus saved layer-sweep artifact and saved directions
- Status: LAUNCHING

## 2026-03-18T11:00:35-0500 POST-RUN: generation-side creativity smoke

- Command: `.venv/bin/python scripts/run_generation_side_creativity_smoke.py --sweep-dir results/creativity_direction/20260318-gemma2-2b-layer-sweep-pilot --output-dir results/steering_eval/20260318-gemma2-2b-generation-smoke --overwrite`
- Outcome: PARTIAL
- Key metric: all four conditions completed on four prompts, but the outputs were mostly prompt-meta continuations instead of clean short stories
- Artifacts saved: `results/steering_eval/20260318-gemma2-2b-generation-smoke/`
- Latest checkpoint: none
- Anomalies: `repeng` control wrapping on Gemma 2 required restoring `attention_type` on wrapped layers for generation to work, and the resulting outputs exposed a base-model prompting mismatch rather than a clean creativity-steering effect
- Next step: repair the base-model story prompting harness before interpreting any steering-side creativity differences

## 2026-03-18T11:10:30-0500 PRE-RUN: base-model story prompt harness probe

- tmux session: N/A
- Script: `scripts/probe_base_model_story_prompts.py`
- Command: `.venv/bin/python scripts/probe_base_model_story_prompts.py --output-dir results/steering_eval/20260318-gemma2-2b-prompt-harness-probe`
- Device: `mps`
- Model: `google/gemma-2-2b`
- SAE: `N/A`; this is an unsteered harness repair probe
- Data slice: `creative_direction_v1_pilot / first 3 prompts / 5 prompt scaffold candidates`
- Output path: `results/steering_eval/20260318-gemma2-2b-prompt-harness-probe`
- What I'm testing: which base-model-compatible story prompt scaffold minimizes prompt-meta continuation behavior on a tiny pilot slice.
- Expected outcome: a ranked prompt-template artifact with one candidate clearly less contaminated by meta/forum-style continuation markers.
- Checkpoint path: N/A
- Checkpoint cadence: N/A
- Log path: `sessions/20260318-session007.md`
- Resume command: `.venv/bin/python scripts/probe_base_model_story_prompts.py --output-dir results/steering_eval/20260318-gemma2-2b-prompt-harness-probe --overwrite`
- Main confound to watch: the meta-marker heuristic is only a harness-selection aid, not a real creativity metric.
- Implementation verified: YES - unit tests for candidate template coverage and meta-marker scoring
- Status: LAUNCHING

## 2026-03-18T11:13:49-0500 POST-RUN: base-model story prompt harness probe

- Command: `.venv/bin/python scripts/probe_base_model_story_prompts.py --output-dir results/steering_eval/20260318-gemma2-2b-prompt-harness-probe`
- Outcome: SUCCESS
- Key metric: `story_opening_once_v1` ranked first with `0.000` meta-marker fraction and `82.33` mean completion words; the old instruction-style harness had `1.000` meta-marker fraction
- Artifacts saved: `results/steering_eval/20260318-gemma2-2b-prompt-harness-probe/`
- Latest checkpoint: none
- Anomalies: the creative baseline was not part of the saved probe, so I separately spot-checked continuation-style creative variants before selecting the repaired creative prompt harness
- Next step: move the generation smoke to continuation-style neutral and creative prompt scaffolds and rerun it

## 2026-03-18T11:20:45-0500 PRE-RUN: repaired generation-side creativity smoke

- tmux session: N/A
- Script: `scripts/run_generation_side_creativity_smoke.py`
- Command: `.venv/bin/python scripts/run_generation_side_creativity_smoke.py --sweep-dir results/creativity_direction/20260318-gemma2-2b-layer-sweep-pilot --output-dir results/steering_eval/20260318-gemma2-2b-generation-smoke --overwrite`
- Device: `mps`
- Model: `google/gemma-2-2b`
- SAE: `N/A for this run`; this remains dense-direction steering before SAE decomposition
- Data slice: `creative_direction_v1_pilot / first 4 prompts / repaired continuation-style neutral and creative prompt baselines`
- Output path: `results/steering_eval/20260318-gemma2-2b-generation-smoke`
- What I'm testing: whether replacing the assignment-style harness with continuation-style story openings removes the prompt-meta failure mode enough to make the smoke artifact interpretable.
- Expected outcome: the saved smoke run should contain mostly story-like continuations instead of forum or homework-style prompt reflections.
- Checkpoint path: N/A
- Checkpoint cadence: N/A
- Log path: `sessions/20260318-session007.md`
- Resume command: `.venv/bin/python scripts/run_generation_side_creativity_smoke.py --sweep-dir results/creativity_direction/20260318-gemma2-2b-layer-sweep-pilot --output-dir results/steering_eval/20260318-gemma2-2b-generation-smoke --overwrite`
- Main confound to watch: layer `0` is still in the condition set because the lexical-confound control issue is not resolved yet.
- Implementation verified: YES - unit tests for repaired prompt templates and generation condition construction
- Status: LAUNCHING

## 2026-03-18T11:23:13-0500 POST-RUN: repaired generation-side creativity smoke

- Command: `.venv/bin/python scripts/run_generation_side_creativity_smoke.py --sweep-dir results/creativity_direction/20260318-gemma2-2b-layer-sweep-pilot --output-dir results/steering_eval/20260318-gemma2-2b-generation-smoke --overwrite`
- Outcome: SUCCESS
- Key metric: all four conditions completed with `0.000` prompt-meta marker fraction under the repaired continuation-style harness
- Artifacts saved: `results/steering_eval/20260318-gemma2-2b-generation-smoke/`
- Latest checkpoint: none
- Anomalies: outputs are now story-like, but the layer set still inherits the unresolved lexical-confound risk from the raw layer sweep
- Next step: add template-control to the layer sweep before using any layer as a real creativity candidate

## 2026-03-18T11:32:15-0500 PRE-RUN: template-controlled creativity layer sweep

- tmux session: N/A
- Script: `scripts/run_creativity_direction_layer_sweep.py`
- Command: `.venv/bin/python scripts/run_creativity_direction_layer_sweep.py --output-dir results/creativity_direction/20260318-gemma2-2b-layer-sweep-template-control`
- Device: `mps`
- Model: `google/gemma-2-2b`
- SAE: `N/A`; this is still dense-direction extraction
- Data slice: `creative_direction_v1_pilot / 32 prompt pairs / all layers`
- Output path: `results/creativity_direction/20260318-gemma2-2b-layer-sweep-template-control`
- What I'm testing: whether early-layer wins survive after subtracting a template-only control signal built from the creative vs uncreative instruction prefixes with empty prompt content.
- Expected outcome: the raw layer-`0` winner should be penalized if it mostly reflects instruction-template wording, and a later layer may become the controlled winner.
- Checkpoint path: N/A
- Checkpoint cadence: N/A

## 2026-03-18T13:35:00-0500 PRE-RUN: v3 counterpart pair materialization

- tmux session: N/A
- Script: `scripts/materialize_creativity_response_pairs_v3.py`
- Command: `.venv/bin/python scripts/materialize_creativity_response_pairs_v3.py --output-dir results/creativity_direction/20260318-gemma2-2b-response-pairs-v3-pilot --overwrite`
- Device: `mps`
- Model: `google/gemma-2-2b`
- SAE: `N/A`; this is still the dense-direction input pair construction step
- Data slice: `creative_direction_v1_pilot / 32 prompt rows`
- Output path: `results/creativity_direction/20260318-gemma2-2b-response-pairs-v3-pilot`
- What I'm testing: whether creative-source plus plain-counterpart rewrite produces cleaner, more content-preserving creativity pairs than the `v2` independently sampled negatives.
- Expected outcome: most rows should pass the overlap and prompt-grounding filters, and accepted pairs should be visibly closer in content than `v2`.
- Checkpoint path: N/A
- Checkpoint cadence: N/A
- Log path: `sessions/20260318-session012.md`
- Resume command: `.venv/bin/python scripts/materialize_creativity_response_pairs_v3.py --output-dir results/creativity_direction/20260318-gemma2-2b-response-pairs-v3-pilot --overwrite`
- Main confound to watch: the rewrite prompt could flatten the story so aggressively that the negative side becomes too short or formulaic to remain a meaningful counterpart.
- Implementation verified: YES - targeted `v3` unit tests for template construction and quality heuristics
- Status: LAUNCHING

## 2026-03-18T13:35:30-0500 PRE-RUN: v3 full-text layer sweep

- tmux session: N/A
- Script: `scripts/run_creativity_direction_layer_sweep.py`
- Command: `.venv/bin/python scripts/run_creativity_direction_layer_sweep.py --split-path prompts/creative_direction_v3_pilot_pairs.jsonl --templates-path prompts/creative_direction_v3_templates.json --output-dir results/creativity_direction/20260318-gemma2-2b-layer-sweep-response-pairs-v3 --overwrite`
- Device: `mps`
- Model: `google/gemma-2-2b`
- SAE: `N/A`; this is still dense-direction extraction
- Data slice: `creative_direction_v3_pilot_pairs / accepted rows / all layers`
- Output path: `results/creativity_direction/20260318-gemma2-2b-layer-sweep-response-pairs-v3`
- What I'm testing: whether the counterpart-style `v3` contrast strengthens late-layer pair separation on the full-text extraction view.
- Expected outcome: pair separation should improve over `v2`, and the best layer should look more stable than the failed `v2` calibration candidate.
- Checkpoint path: N/A
- Checkpoint cadence: N/A
- Log path: `sessions/20260318-session012.md`
- Resume command: `.venv/bin/python scripts/run_creativity_direction_layer_sweep.py --split-path prompts/creative_direction_v3_pilot_pairs.jsonl --templates-path prompts/creative_direction_v3_templates.json --output-dir results/creativity_direction/20260318-gemma2-2b-layer-sweep-response-pairs-v3 --overwrite`
- Main confound to watch: stronger raw separation could still come from the rewrite template rather than the creativity contrast, so the template-control outputs still matter.
- Implementation verified: YES - existing layer-sweep tests plus green `v3` pair-builder tests
- Status: LAUNCHING

## 2026-03-18T13:36:00-0500 PRE-RUN: v3 response-only layer sweep

- tmux session: N/A
- Script: `scripts/run_creativity_direction_layer_sweep.py`
- Command: `.venv/bin/python scripts/run_creativity_direction_layer_sweep.py --split-path prompts/creative_direction_v3_response_only_pairs.jsonl --templates-path prompts/creative_direction_v3_templates.json --output-dir results/creativity_direction/20260318-gemma2-2b-layer-sweep-response-pairs-v3-response-only --overwrite`
- Device: `mps`
- Model: `google/gemma-2-2b`
- SAE: `N/A`; this is a diagnostic rerun without prompt text in the contrast rows
- Data slice: `creative_direction_v3_response_only_pairs / accepted rows / all layers`
- Output path: `results/creativity_direction/20260318-gemma2-2b-layer-sweep-response-pairs-v3-response-only`
- What I'm testing: whether the `v3` layer signal survives when only the response text is kept.
- Expected outcome: the best layer should stay in the same late-layer band if the recovered signal is not mainly prompt-wrapper dependent.
- Checkpoint path: N/A
- Checkpoint cadence: N/A
- Log path: `sessions/20260318-session012.md`
- Resume command: `.venv/bin/python scripts/run_creativity_direction_layer_sweep.py --split-path prompts/creative_direction_v3_response_only_pairs.jsonl --templates-path prompts/creative_direction_v3_templates.json --output-dir results/creativity_direction/20260318-gemma2-2b-layer-sweep-response-pairs-v3-response-only --overwrite`
- Main confound to watch: the response-only view has no meaningful template-control difference, so agreement with the full-text view matters more than the control delta itself.
- Implementation verified: YES - existing layer-sweep tests plus green `v3` pair-builder tests
- Status: LAUNCHING

## 2026-03-18T13:36:30-0500 PRE-RUN: v3 bounded calibration

- tmux session: N/A
- Script: `scripts/run_creativity_direction_calibration.py`
- Command: `.venv/bin/python scripts/run_creativity_direction_calibration.py --split-path prompts/creative_direction_v3_pilot_pairs.jsonl --templates-path prompts/creative_direction_v3_templates.json --sweep-dir results/creativity_direction/20260318-gemma2-2b-layer-sweep-response-pairs-v3 --output-dir results/steering_eval/20260318-gemma2-2b-v3-direction-calibration --overwrite`
- Device: `mps`
- Model: `google/gemma-2-2b`
- SAE: `N/A`; this is still dense-direction steering before decomposition
- Data slice: `creative_direction_v3_pilot_pairs / first 6 prompts / full-text sweep winner band`
- Output path: `results/steering_eval/20260318-gemma2-2b-v3-direction-calibration`
- What I'm testing: whether the `v3` late-layer candidate shows a saner coefficient-response pattern than the unstable `v2` direction.
- Expected outcome: the selected layer should move in a more interpretable direction as coefficient changes, even if the effect remains modest.
- Checkpoint path: N/A
- Checkpoint cadence: N/A
- Log path: `sessions/20260318-session012.md`
- Resume command: `.venv/bin/python scripts/run_creativity_direction_calibration.py --split-path prompts/creative_direction_v3_pilot_pairs.jsonl --templates-path prompts/creative_direction_v3_templates.json --sweep-dir results/creativity_direction/20260318-gemma2-2b-layer-sweep-response-pairs-v3 --output-dir results/steering_eval/20260318-gemma2-2b-v3-direction-calibration --overwrite`
- Main confound to watch: internal probe movement may still look cleaner than the actual outputs, which is not enough to reopen Phase 2.
- Implementation verified: YES - existing calibration tests plus green `v3` pair-builder tests
- Status: LAUNCHING

## 2026-03-18T14:27:15-0500 PRE-RUN: v3 response-only bounded calibration

- tmux session: N/A
- Script: `scripts/run_creativity_direction_calibration.py`
- Command: `.venv/bin/python scripts/run_creativity_direction_calibration.py --split-path prompts/creative_direction_v3_response_only_pairs.jsonl --templates-path prompts/creative_direction_v3_templates.json --sweep-dir results/creativity_direction/20260318-gemma2-2b-layer-sweep-response-pairs-v3-response-only --output-dir results/steering_eval/20260318-gemma2-2b-v3-direction-calibration-response-only --overwrite`
- Device: `mps`
- Model: `google/gemma-2-2b`
- SAE: `N/A`; this is still dense-direction steering before decomposition
- Data slice: `creative_direction_v3_response_only_pairs / first 6 prompts / response-only sweep winner band`
- Output path: `results/steering_eval/20260318-gemma2-2b-v3-direction-calibration-response-only`
- What I'm testing: whether the response-only winner band behaves any more cleanly under steering than the full-text view after the `v3` diagnostic split.
- Expected outcome: if the response-only sweep found a real signal, its calibration should look less erratic than the full-text band.
- Checkpoint path: N/A
- Checkpoint cadence: N/A
- Log path: `sessions/20260318-session012.md`
- Resume command: `.venv/bin/python scripts/run_creativity_direction_calibration.py --split-path prompts/creative_direction_v3_response_only_pairs.jsonl --templates-path prompts/creative_direction_v3_templates.json --sweep-dir results/creativity_direction/20260318-gemma2-2b-layer-sweep-response-pairs-v3-response-only --output-dir results/steering_eval/20260318-gemma2-2b-v3-direction-calibration-response-only --overwrite`
- Main confound to watch: agreement on a raw best layer is still not enough if the coefficient-response pattern or outputs remain unstable.
- Implementation verified: YES - existing calibration tests plus landed `v3` sweep artifacts
- Status: LAUNCHING

## 2026-03-18T14:25:12-0500 POST-RUN: v3 counterpart pair materialization

- Command: `.venv/bin/python scripts/materialize_creativity_response_pairs_v3.py --output-dir results/creativity_direction/20260318-gemma2-2b-response-pairs-v3-pilot --overwrite`
- Outcome: SUCCESS
- Key metric: accepted `31 / 32` rows with mean counterpart overlap `0.913658`
- Artifacts saved: `results/creativity_direction/20260318-gemma2-2b-response-pairs-v3-pilot/`, `prompts/creative_direction_v3_*.json*`
- Latest checkpoint: none
- Anomalies: the lone rejected row drifted semantically despite the rewrite instruction, which is useful evidence that the filter is catching real failures instead of silently trusting the rewrite prompt
- Next step: rerun dense-direction layer selection on the landed `v3` slice in full-text and response-only form

## 2026-03-18T14:25:39-0500 POST-RUN: v3 full-text layer sweep

- Command: `.venv/bin/python scripts/run_creativity_direction_layer_sweep.py --split-path prompts/creative_direction_v3_pilot_pairs.jsonl --templates-path prompts/creative_direction_v3_templates.json --output-dir results/creativity_direction/20260318-gemma2-2b-layer-sweep-response-pairs-v3 --overwrite`
- Outcome: SUCCESS
- Key metric: raw best layer `6` with `0.354839` positive-greater-than-negative fraction and no controlled winner
- Artifacts saved: `results/creativity_direction/20260318-gemma2-2b-layer-sweep-response-pairs-v3/`
- Latest checkpoint: none
- Anomalies: the contrast got cleaner but the dense direction got weaker rather than stronger, which is exactly the opposite of what a rescued Phase 1 signal would look like
- Next step: run the response-only sweep before deciding whether the failure is prompt-wrapper specific

## 2026-03-18T14:26:29-0500 POST-RUN: v3 response-only layer sweep

- Command: `.venv/bin/python scripts/run_creativity_direction_layer_sweep.py --split-path prompts/creative_direction_v3_response_only_pairs.jsonl --templates-path prompts/creative_direction_v3_templates.json --output-dir results/creativity_direction/20260318-gemma2-2b-layer-sweep-response-pairs-v3-response-only --overwrite`
- Outcome: SUCCESS
- Key metric: raw best layer `22` with `0.387097` positive-greater-than-negative fraction and no controlled winner
- Artifacts saved: `results/creativity_direction/20260318-gemma2-2b-layer-sweep-response-pairs-v3-response-only/`
- Latest checkpoint: none
- Anomalies: the best raw layer changed from `6` to `22`, but the weakness did not disappear, which points to view-dependence rather than a hidden robust direction
- Next step: calibrate both winner bands rather than pretending one of the sweeps is obviously authoritative

## 2026-03-18T14:30:37-0500 POST-RUN: v3 bounded calibration

- Command: `.venv/bin/python scripts/run_creativity_direction_calibration.py --split-path prompts/creative_direction_v3_pilot_pairs.jsonl --templates-path prompts/creative_direction_v3_templates.json --sweep-dir results/creativity_direction/20260318-gemma2-2b-layer-sweep-response-pairs-v3 --output-dir results/steering_eval/20260318-gemma2-2b-v3-direction-calibration --overwrite`
- Outcome: SUCCESS
- Key metric: layer `6` mean probe projection moved from `-1.633606` unsteered to `-7.025127`, `-15.897805`, and `-3.596284` across positive coefficients, which is not a sane monotone control pattern
- Artifacts saved: `results/steering_eval/20260318-gemma2-2b-v3-direction-calibration/`
- Latest checkpoint: none
- Anomalies: the candidate layer band came from a weak sweep and behaved like one; positive coefficients did not create a consistent movement toward a clearer creativity-like state
- Next step: run the response-only calibration before finalizing the Phase 1 interpretation

## 2026-03-18T14:34:08-0500 POST-RUN: v3 response-only bounded calibration

- Command: `.venv/bin/python scripts/run_creativity_direction_calibration.py --split-path prompts/creative_direction_v3_response_only_pairs.jsonl --templates-path prompts/creative_direction_v3_templates.json --sweep-dir results/creativity_direction/20260318-gemma2-2b-layer-sweep-response-pairs-v3-response-only --output-dir results/steering_eval/20260318-gemma2-2b-v3-direction-calibration-response-only --overwrite`
- Outcome: SUCCESS
- Key metric: layer `22` mean probe projection moved from `95.376869` unsteered to `119.561817`, `82.285971`, and `91.711067`, while layer `0` flipped sign at coeff `1.0`
- Artifacts saved: `results/steering_eval/20260318-gemma2-2b-v3-direction-calibration-response-only/`
- Latest checkpoint: none
- Anomalies: the alternative sweep view changes the candidate layers but not the instability, which strengthens the negative interpretation rather than rescuing it
- Next step: update the repo truth, perform the secondary research alignment review, and decide whether one bounded Olson-style extraction sensitivity is still warranted before a phase-level negative conclusion

## 2026-03-18T14:45:00-0500 PRE-RUN: v3 mean-difference full-text layer sweep

- tmux session: N/A
- Script: `scripts/run_creativity_direction_layer_sweep.py`
- Command: `.venv/bin/python scripts/run_creativity_direction_layer_sweep.py --split-path prompts/creative_direction_v3_pilot_pairs.jsonl --templates-path prompts/creative_direction_v3_templates.json --direction-method mean_difference --output-dir results/creativity_direction/20260318-gemma2-2b-layer-sweep-response-pairs-v3-mean-difference --overwrite`
- Device: `mps`
- Model: `google/gemma-2-2b`
- SAE: `N/A`; this is still dense-direction extraction
- Data slice: `creative_direction_v3_pilot_pairs / 31 accepted rows / all layers`
- Output path: `results/creativity_direction/20260318-gemma2-2b-layer-sweep-response-pairs-v3-mean-difference`
- What I'm testing: whether Olson-style mean-difference extraction recovers a stronger or cleaner dense creativity direction than the current PCA path on the same `v3` counterpart slice.
- Expected outcome: if extraction method is the remaining mismatch, the raw fraction or margin signal should improve enough to justify bounded calibration.
- Checkpoint path: N/A
- Checkpoint cadence: N/A
- Log path: `sessions/20260318-session013.md`
- Resume command: `.venv/bin/python scripts/run_creativity_direction_layer_sweep.py --split-path prompts/creative_direction_v3_pilot_pairs.jsonl --templates-path prompts/creative_direction_v3_templates.json --direction-method mean_difference --output-dir results/creativity_direction/20260318-gemma2-2b-layer-sweep-response-pairs-v3-mean-difference --overwrite`
- Main confound to watch: a better raw winner alone is not enough if the method still yields inverted margins or unstable calibration.
- Implementation verified: YES - targeted layer-sweep tests now cover `mean_difference` extraction support
- Status: LAUNCHING

## 2026-03-18T14:45:30-0500 PRE-RUN: v3 mean-difference response-only layer sweep

- tmux session: N/A
- Script: `scripts/run_creativity_direction_layer_sweep.py`
- Command: `.venv/bin/python scripts/run_creativity_direction_layer_sweep.py --split-path prompts/creative_direction_v3_response_only_pairs.jsonl --templates-path prompts/creative_direction_v3_templates.json --direction-method mean_difference --output-dir results/creativity_direction/20260318-gemma2-2b-layer-sweep-response-pairs-v3-response-only-mean-difference --overwrite`
- Device: `mps`
- Model: `google/gemma-2-2b`
- SAE: `N/A`; this is still dense-direction extraction
- Data slice: `creative_direction_v3_response_only_pairs / 31 accepted rows / all layers`
- Output path: `results/creativity_direction/20260318-gemma2-2b-layer-sweep-response-pairs-v3-response-only-mean-difference`
- What I'm testing: whether the mean-difference method behaves differently when the same `v3` counterpart slice is viewed through response-only extraction.
- Expected outcome: if the response-only view is the cleaner object, it should either stabilize the same band or clearly beat the full-text view.
- Checkpoint path: N/A
- Checkpoint cadence: N/A
- Log path: `sessions/20260318-session013.md`
- Resume command: `.venv/bin/python scripts/run_creativity_direction_layer_sweep.py --split-path prompts/creative_direction_v3_response_only_pairs.jsonl --templates-path prompts/creative_direction_v3_templates.json --direction-method mean_difference --output-dir results/creativity_direction/20260318-gemma2-2b-layer-sweep-response-pairs-v3-response-only-mean-difference --overwrite`
- Main confound to watch: method sensitivity can still leave the view-dependence unresolved, which would strengthen the negative result rather than weaken it.
- Implementation verified: YES - targeted layer-sweep tests now cover `mean_difference` extraction support
- Status: LAUNCHING

## 2026-03-18T14:51:00-0500 PRE-RUN: v3 mean-difference full-text calibration

- tmux session: N/A
- Script: `scripts/run_creativity_direction_calibration.py`
- Command: `.venv/bin/python scripts/run_creativity_direction_calibration.py --split-path prompts/creative_direction_v3_pilot_pairs.jsonl --templates-path prompts/creative_direction_v3_templates.json --sweep-dir results/creativity_direction/20260318-gemma2-2b-layer-sweep-response-pairs-v3-mean-difference --output-dir results/steering_eval/20260318-gemma2-2b-v3-direction-calibration-mean-difference --overwrite`
- Device: `mps`
- Model: `google/gemma-2-2b`
- SAE: `N/A`; this is still dense-direction steering before decomposition
- Data slice: `creative_direction_v3_pilot_pairs / first 6 prompts / mean-difference candidate layers`
- Output path: `results/steering_eval/20260318-gemma2-2b-v3-direction-calibration-mean-difference`
- What I'm testing: whether the recovered full-text `mean_difference` direction behaves like a usable control signal rather than just a better layer-ranking heuristic.
- Expected outcome: the top late-layer band should show a cleaner, more interpretable coefficient-response pattern than the failed PCA calibration.
- Checkpoint path: N/A
- Checkpoint cadence: N/A
- Log path: `sessions/20260318-session013.md`
- Resume command: `.venv/bin/python scripts/run_creativity_direction_calibration.py --split-path prompts/creative_direction_v3_pilot_pairs.jsonl --templates-path prompts/creative_direction_v3_templates.json --sweep-dir results/creativity_direction/20260318-gemma2-2b-layer-sweep-response-pairs-v3-mean-difference --output-dir results/steering_eval/20260318-gemma2-2b-v3-direction-calibration-mean-difference --overwrite`
- Main confound to watch: a recovered sweep winner still fails the thesis if positive coefficients do not move outputs or probe projections coherently.
- Implementation verified: YES - existing calibration tests plus landed `mean_difference` sweep artifact
- Status: LAUNCHING

## 2026-03-18T14:51:30-0500 PRE-RUN: v3 mean-difference response-only calibration

- tmux session: N/A
- Script: `scripts/run_creativity_direction_calibration.py`
- Command: `.venv/bin/python scripts/run_creativity_direction_calibration.py --split-path prompts/creative_direction_v3_response_only_pairs.jsonl --templates-path prompts/creative_direction_v3_templates.json --sweep-dir results/creativity_direction/20260318-gemma2-2b-layer-sweep-response-pairs-v3-response-only-mean-difference --output-dir results/steering_eval/20260318-gemma2-2b-v3-direction-calibration-response-only-mean-difference --overwrite`
- Device: `mps`
- Model: `google/gemma-2-2b`
- SAE: `N/A`; this is still dense-direction steering before decomposition
- Data slice: `creative_direction_v3_response_only_pairs / first 6 prompts / mean-difference candidate layers`
- Output path: `results/steering_eval/20260318-gemma2-2b-v3-direction-calibration-response-only-mean-difference`
- What I'm testing: whether the response-only `mean_difference` signal is as stable as the recovered full-text signal or still weaker and view-dependent.
- Expected outcome: either the response-only band should corroborate the full-text recovery or the calibration should show that the rescue is narrower than the sweep metrics alone imply.
- Checkpoint path: N/A
- Checkpoint cadence: N/A
- Log path: `sessions/20260318-session013.md`
- Resume command: `.venv/bin/python scripts/run_creativity_direction_calibration.py --split-path prompts/creative_direction_v3_response_only_pairs.jsonl --templates-path prompts/creative_direction_v3_templates.json --sweep-dir results/creativity_direction/20260318-gemma2-2b-layer-sweep-response-pairs-v3-response-only-mean-difference --output-dir results/steering_eval/20260318-gemma2-2b-v3-direction-calibration-response-only-mean-difference --overwrite`
- Main confound to watch: a sweep-level recovery that collapses under calibration would still count as a narrow negative for the response-only view.
- Implementation verified: YES - existing calibration tests plus landed `mean_difference` sweep artifact
- Status: LAUNCHING

## 2026-03-18T14:49:39-0500 POST-RUN: v3 mean-difference full-text layer sweep

- Command: `.venv/bin/python scripts/run_creativity_direction_layer_sweep.py --split-path prompts/creative_direction_v3_pilot_pairs.jsonl --templates-path prompts/creative_direction_v3_templates.json --direction-method mean_difference --output-dir results/creativity_direction/20260318-gemma2-2b-layer-sweep-response-pairs-v3-mean-difference --overwrite`
- Outcome: SUCCESS
- Key metric: controlled best layer `23` with `0.580645` positive-greater-than-negative fraction, mean margin `58.126850`, and margin z-score `0.829265`
- Artifacts saved: `results/creativity_direction/20260318-gemma2-2b-layer-sweep-response-pairs-v3-mean-difference/`
- Latest checkpoint: none
- Anomalies: none obvious; the same `v3` slice that failed under PCA now recovers a clear controlled winner, which means the extraction-method mismatch was genuinely material
- Next step: run the response-only `mean_difference` sweep to test whether the recovery is robust across views

## 2026-03-18T14:49:54-0500 POST-RUN: v3 mean-difference response-only layer sweep

- Command: `.venv/bin/python scripts/run_creativity_direction_layer_sweep.py --split-path prompts/creative_direction_v3_response_only_pairs.jsonl --templates-path prompts/creative_direction_v3_templates.json --direction-method mean_difference --output-dir results/creativity_direction/20260318-gemma2-2b-layer-sweep-response-pairs-v3-response-only-mean-difference --overwrite`
- Outcome: SUCCESS
- Key metric: controlled best layer `9` with `0.548387` positive-greater-than-negative fraction, mean margin `13.131884`, and margin z-score `0.828694`
- Artifacts saved: `results/creativity_direction/20260318-gemma2-2b-layer-sweep-response-pairs-v3-response-only-mean-difference/`
- Latest checkpoint: none
- Anomalies: the response-only view also recovers under `mean_difference`, but it remains weaker than the full-text path
- Next step: calibrate both recovered winner bands before changing the phase order

## 2026-03-18T14:54:27-0500 POST-RUN: v3 mean-difference full-text calibration

- Command: `.venv/bin/python scripts/run_creativity_direction_calibration.py --split-path prompts/creative_direction_v3_pilot_pairs.jsonl --templates-path prompts/creative_direction_v3_templates.json --sweep-dir results/creativity_direction/20260318-gemma2-2b-layer-sweep-response-pairs-v3-mean-difference --output-dir results/steering_eval/20260318-gemma2-2b-v3-direction-calibration-mean-difference --overwrite`
- Outcome: SUCCESS
- Key metric: layer `23` mean probe projection moved from `15.270608` unsteered to `26.416735` at coeff `0.5` and `34.472979` at coeff `1.0`, then overshot to `-7.573171` at coeff `2.0`
- Artifacts saved: `results/steering_eval/20260318-gemma2-2b-v3-direction-calibration-mean-difference/`
- Latest checkpoint: none
- Anomalies: the recovered direction still has an overshoot regime at `2.0`, so the useful coefficient range appears bounded rather than open-ended
- Next step: run the response-only `mean_difference` calibration before deciding how much of the recovery is view-specific

## 2026-03-18T14:58:12-0500 POST-RUN: v3 mean-difference response-only calibration

- Command: `.venv/bin/python scripts/run_creativity_direction_calibration.py --split-path prompts/creative_direction_v3_response_only_pairs.jsonl --templates-path prompts/creative_direction_v3_templates.json --sweep-dir results/creativity_direction/20260318-gemma2-2b-layer-sweep-response-pairs-v3-response-only-mean-difference --output-dir results/steering_eval/20260318-gemma2-2b-v3-direction-calibration-response-only-mean-difference --overwrite`
- Outcome: SUCCESS
- Key metric: layer `9` mean probe projection improved from `-5.527642` unsteered to `-2.083943` at coeff `0.5`, then slipped to `-9.066536` at coeff `1.0`
- Artifacts saved: `results/steering_eval/20260318-gemma2-2b-v3-direction-calibration-response-only-mean-difference/`
- Latest checkpoint: none
- Anomalies: the response-only branch improves over PCA but remains noticeably weaker and more view-dependent than the full-text `mean_difference` path
- Next step: update the repo truth and promote the full-text `mean_difference` path to the pilot output-gate candidate
- Log path: `sessions/20260318-session007.md`
- Resume command: `.venv/bin/python scripts/run_creativity_direction_layer_sweep.py --output-dir results/creativity_direction/20260318-gemma2-2b-layer-sweep-template-control --overwrite`
- Main confound to watch: this control isolates template-prefix leakage, not every possible prompt-format confound.
- Implementation verified: YES - unit tests for controlled-metric computation and controlled ranking
- Status: LAUNCHING

## 2026-03-18T11:39:32-0500 POST-RUN: template-controlled creativity layer sweep

- Command: `.venv/bin/python scripts/run_creativity_direction_layer_sweep.py --output-dir results/creativity_direction/20260318-gemma2-2b-layer-sweep-template-control --overwrite`
- Outcome: SUCCESS
- Key metric: raw winner remained `layer 0`, but no layer cleared the template-control threshold; the best controlled excess score was `0.000000`
- Artifacts saved: `results/creativity_direction/20260318-gemma2-2b-layer-sweep-template-control/`
- Latest checkpoint: none
- Anomalies: template-only control directions separated the actual creative-vs-uncreative prompt pairs nearly as well as or better than the learned directions at every layer, so the current instruction-template contrast is not clean enough for freezing a creativity layer; a stale optional controlled-pair-details file from an earlier intermediate run was explicitly removed before the final overwrite artifact was accepted
- Next step: redesign the contrastive extraction templates or selection procedure before any decomposition run that assumes a settled dense creativity direction layer

## 2026-03-18T11:57:30-0500 PRE-RUN: response-centered creativity pair materialization v2

- tmux session: N/A
- Script: `scripts/materialize_creativity_response_pairs_v2.py`
- Command: `.venv/bin/python scripts/materialize_creativity_response_pairs_v2.py --output-dir results/creativity_direction/20260318-gemma2-2b-response-pairs-v2-pilot`
- Device: `mps`
- Model: `google/gemma-2-2b`
- SAE: `N/A`; this run materializes contrastive text pairs before any SAE decomposition
- Data slice: `creative_direction_v1_pilot / 32 prompts / creative-source and plain-source continuation pairs`
- Output path: `results/creativity_direction/20260318-gemma2-2b-response-pairs-v2-pilot`, `prompts/creative_direction_v2_*`
- What I'm testing: whether a response-centered pilot artifact can be frozen so the next layer sweep operates on matched story continuations under a shared extraction wrapper rather than mismatched instruction templates.
- Expected outcome: a 32-pair pilot file with story-like positive and negative continuations, zero or near-zero meta contamination, and versioned v2 metadata/templates files.
- Checkpoint path: N/A
- Checkpoint cadence: N/A
- Log path: `sessions/20260318-session008.md`
- Resume command: `.venv/bin/python scripts/materialize_creativity_response_pairs_v2.py --output-dir results/creativity_direction/20260318-gemma2-2b-response-pairs-v2-pilot --overwrite`
- Main confound to watch: the plain-source prompt could still collapse into awkward genre markers or malformed continuations even though the extraction wrapper itself is shared.
- Implementation verified: YES - focused unit tests for shared-wrapper rendering, pair-row construction, pair-aware dataset loading, and response-pair template control
- Status: LAUNCHING

## 2026-03-18T11:59:40-0500 POST-RUN: response-centered creativity pair materialization v2

- Command: `.venv/bin/python scripts/materialize_creativity_response_pairs_v2.py --output-dir results/creativity_direction/20260318-gemma2-2b-response-pairs-v2-pilot`
- Outcome: SUCCESS
- Key metric: `32` response-centered pilot pairs saved with `0.000` positive meta fraction and `0.03125` negative meta fraction under a shared extraction wrapper
- Artifacts saved: `results/creativity_direction/20260318-gemma2-2b-response-pairs-v2-pilot/`, `prompts/creative_direction_v2_pilot_pairs.jsonl`, `prompts/creative_direction_v2_metadata.json`, `prompts/creative_direction_v2_templates.json`
- Latest checkpoint: none
- Anomalies: one negative continuation still contained prompt-like spillover text, so the `v2` pilot is much cleaner than `v1` but not perfectly sanitized
- Next step: rerun the controlled layer sweep on the `creative_direction_v2` pair file before deciding whether the redesign rescued any dense creativity layer

## 2026-03-18T12:01:10-0500 PRE-RUN: controlled layer sweep on response-centered v2 pairs

- tmux session: N/A
- Script: `scripts/run_creativity_direction_layer_sweep.py`
- Command: `.venv/bin/python scripts/run_creativity_direction_layer_sweep.py --split-path prompts/creative_direction_v2_pilot_pairs.jsonl --templates-path prompts/creative_direction_v2_templates.json --output-dir results/creativity_direction/20260318-gemma2-2b-layer-sweep-response-pairs-v2`
- Device: `mps`
- Model: `google/gemma-2-2b`
- SAE: `N/A`; this remains dense-direction extraction before decomposition
- Data slice: `creative_direction_v2_pilot / 32 response-centered positive-negative continuation pairs / all layers`
- Output path: `results/creativity_direction/20260318-gemma2-2b-layer-sweep-response-pairs-v2`
- What I'm testing: whether moving the creativity-vs-plain contrast into matched generated continuations under a shared extraction wrapper produces at least one layer that beats the template-control baseline.
- Expected outcome: either a later layer now clears the control and becomes the provisional dense creativity layer, or the experiment records a stronger negative result that the redesign still did not isolate a clean layer.
- Checkpoint path: N/A
- Checkpoint cadence: N/A
- Log path: `sessions/20260318-session008.md`
- Resume command: `.venv/bin/python scripts/run_creativity_direction_layer_sweep.py --split-path prompts/creative_direction_v2_pilot_pairs.jsonl --templates-path prompts/creative_direction_v2_templates.json --output-dir results/creativity_direction/20260318-gemma2-2b-layer-sweep-response-pairs-v2 --overwrite`
- Main confound to watch: the source prompts used to generate the positive and negative continuations still differ, so a surviving layer must be interpreted as a promising candidate rather than a settled creativity mechanism.
- Implementation verified: YES - focused unit tests for response-pair loading and response-pair template control plus the existing controlled-sweep regression suite
- Status: LAUNCHING

## 2026-03-18T12:01:31-0500 POST-RUN: controlled layer sweep on response-centered v2 pairs

- Command: `.venv/bin/python scripts/run_creativity_direction_layer_sweep.py --split-path prompts/creative_direction_v2_pilot_pairs.jsonl --templates-path prompts/creative_direction_v2_templates.json --output-dir results/creativity_direction/20260318-gemma2-2b-layer-sweep-response-pairs-v2 --overwrite`
- Outcome: SUCCESS
- Key metric: `layer 24` is now both the raw and controlled winner with `0.593750` positive-greater-than-negative fraction and `0.593750` controlled fraction delta
- Artifacts saved: `results/creativity_direction/20260318-gemma2-2b-layer-sweep-response-pairs-v2/`
- Latest checkpoint: none
- Anomalies: the redesign eliminated the template-only control signal entirely, but the surviving separation is still weak (`19 / 32` pairs), so the layer is a provisional candidate rather than a settled creativity mechanism
- Next step: run a bounded generation-side smoke from the `v2` sweep before allowing the experiment to progress toward decomposition

## 2026-03-18T12:04:00-0500 PRE-RUN: generation-side creativity smoke on response-centered v2 sweep

- tmux session: N/A
- Script: `scripts/run_generation_side_creativity_smoke.py`
- Command: `.venv/bin/python scripts/run_generation_side_creativity_smoke.py --templates-path prompts/creative_direction_v2_templates.json --sweep-dir results/creativity_direction/20260318-gemma2-2b-layer-sweep-response-pairs-v2 --output-dir results/steering_eval/20260318-gemma2-2b-generation-smoke-response-pairs-v2`
- Device: `mps`
- Model: `google/gemma-2-2b`
- SAE: `N/A for this run`; this is still dense-direction steering before decomposition
- Data slice: `creative_direction_v1_pilot / first 4 prompts / repaired continuation-style baselines plus the top two v2 response-pair sweep layers`
- Output path: `results/steering_eval/20260318-gemma2-2b-generation-smoke-response-pairs-v2`
- What I'm testing: whether the provisional late-layer direction recovered from the response-centered `v2` pairs produces qualitatively different story outputs under the repaired generation harness.
- Expected outcome: either a visible creativity/coherence difference from layers `24` and `20`, or a cleaner indication that the recovered direction is still too weak to matter at generation time.
- Checkpoint path: N/A
- Checkpoint cadence: N/A
- Log path: `sessions/20260318-session008.md`
- Resume command: `.venv/bin/python scripts/run_generation_side_creativity_smoke.py --templates-path prompts/creative_direction_v2_templates.json --sweep-dir results/creativity_direction/20260318-gemma2-2b-layer-sweep-response-pairs-v2 --output-dir results/steering_eval/20260318-gemma2-2b-generation-smoke-response-pairs-v2 --overwrite`
- Main confound to watch: because the `v2` direction is weak on pair separation, any visible generation effect could still be noisy or inconsistent across prompts.
- Implementation verified: YES - existing generation-smoke tests plus a completed v2 sweep artifact with saved directions
- Status: LAUNCHING

## 2026-03-18T12:05:10-0500 POST-RUN: generation-side creativity smoke on response-centered v2 sweep

- Command: `.venv/bin/python scripts/run_generation_side_creativity_smoke.py --templates-path prompts/creative_direction_v2_templates.json --sweep-dir results/creativity_direction/20260318-gemma2-2b-layer-sweep-response-pairs-v2 --output-dir results/steering_eval/20260318-gemma2-2b-generation-smoke-response-pairs-v2`
- Outcome: SUCCESS
- Key metric: all four conditions completed with `0.000` meta-marker fraction, but condition-level mean word counts stayed tightly clustered between `78.25` and `83.50`
- Artifacts saved: `results/steering_eval/20260318-gemma2-2b-generation-smoke-response-pairs-v2/`
- Latest checkpoint: none
- Anomalies: the recovered late-layer directions from the `v2` sweep do not produce an obvious qualitative steering jump on the bounded four-prompt smoke, so calibration is now the honest blocker
- Next step: start `creativedecomp-6lm` and test whether a bounded scale sweep or pair-quality audit strengthens the provisional late-layer signal enough for decomposition

## 2026-03-18T12:37:30-0500 PRE-RUN: v2 late-layer direction calibration sweep

- tmux session: N/A
- Script: `scripts/run_creativity_direction_calibration.py`
- Command: `.venv/bin/python scripts/run_creativity_direction_calibration.py --output-dir results/steering_eval/20260318-gemma2-2b-v2-direction-calibration`
- Device: `mps`
- Model: `google/gemma-2-2b`
- SAE: `N/A`; this remains dense-direction calibration before decomposition
- Data slice: `creative_direction_v2_pilot / first 6 prompts / top two late-layer candidates / steering coeffs -1.0, 0.5, 1.0, 2.0`
- Output path: `results/steering_eval/20260318-gemma2-2b-v2-direction-calibration`
- What I'm testing: whether the recovered `v2` late-layer direction shows a sane scale-response pattern in probe-layer projections without immediately collapsing output quality.
- Expected outcome: at least one late-layer candidate should show more positive mean probe projection at positive coefficients than at the unsteered baseline, with low prompt-meta contamination.
- Checkpoint path: N/A
- Checkpoint cadence: N/A
- Log path: `sessions/20260318-session009.md`
- Resume command: `.venv/bin/python scripts/run_creativity_direction_calibration.py --output-dir results/steering_eval/20260318-gemma2-2b-v2-direction-calibration --overwrite`
- Main confound to watch: a monotone internal probe shift could still reflect generic verbosity or stylistic drift rather than a useful creativity-related change.
- Implementation verified: YES - focused unit tests for coefficient parsing, condition construction, and projection-aware condition summaries
- Status: LAUNCHING

## 2026-03-18T12:38:00-0500 PRE-RUN: v2 response-pair audit slice

- tmux session: N/A
- Script: `scripts/audit_creativity_response_pairs_v2.py`
- Command: `.venv/bin/python scripts/audit_creativity_response_pairs_v2.py --output-dir results/creativity_direction/20260318-gemma2-2b-response-pairs-v2-audit`
- Device: `cpu`
- Model: `N/A`; this is an artifact selection pass over saved pair and sweep outputs
- SAE: `N/A`
- Data slice: `creative_direction_v2_pilot / strongest wins / strongest losses / flagged rows`
- Output path: `results/creativity_direction/20260318-gemma2-2b-response-pairs-v2-audit`
- What I'm testing: whether the weak `v2` signal looks like noisy or contaminated pair construction rather than total absence of a late-layer contrast.
- Expected outcome: the audit slice should expose whether the largest failures cluster around generic positives, stronger-than-expected negatives, or contaminated continuations.
- Checkpoint path: N/A
- Checkpoint cadence: N/A
- Log path: `sessions/20260318-session009.md`
- Resume command: `.venv/bin/python scripts/audit_creativity_response_pairs_v2.py --output-dir results/creativity_direction/20260318-gemma2-2b-response-pairs-v2-audit --overwrite`
- Main confound to watch: an audit slice can surface problems but does not by itself prove which replacement contrast will fix them.
- Implementation verified: YES - focused unit tests for audit-row selection and audit summary counts
- Status: LAUNCHING

## 2026-03-18T12:40:11-0500 POST-RUN: v2 response-pair audit slice

- Command: `.venv/bin/python scripts/audit_creativity_response_pairs_v2.py --output-dir results/creativity_direction/20260318-gemma2-2b-response-pairs-v2-audit`
- Outcome: SUCCESS
- Key metric: `7` audit rows selected, including `3` strongest losses and `1` flagged negative-meta row
- Artifacts saved: `results/creativity_direction/20260318-gemma2-2b-response-pairs-v2-audit/`
- Latest checkpoint: none
- Anomalies: several strongest losses are not low-quality negatives; they remain as prompt-specific or more prompt-specific than the paired positives, which means pair quality is still a live blocker
- Next step: compare the audit diagnosis against the bounded calibration sweep before deciding whether decomposition remains blocked

## 2026-03-18T12:43:30-0500 POST-RUN: v2 late-layer direction calibration sweep

- Command: `.venv/bin/python scripts/run_creativity_direction_calibration.py --output-dir results/steering_eval/20260318-gemma2-2b-v2-direction-calibration`
- Outcome: SUCCESS
- Key metric: layer `24` remained the best available candidate, but its mean probe projection moved from `13.361952` unsteered to `-13.657598` at coeff `0.5`, `-42.777972` at coeff `1.0`, and only `1.912126` at coeff `2.0`
- Artifacts saved: `results/steering_eval/20260318-gemma2-2b-v2-direction-calibration/`
- Latest checkpoint: none
- Anomalies: all conditions stayed free of prompt-meta contamination, but the coefficient-response pattern was not cleanly monotone or stable enough to justify decomposition
- Next step: keep decomposition blocked and create a new contrast-quality task to build an audited `v3` pair set before rerunning layer selection and calibration
