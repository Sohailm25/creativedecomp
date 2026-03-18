# Results Index

Register every experimental artifact here. Never delete entries; mark superseded artifacts explicitly.

## Rules

- Every artifact saved under `results/` must appear here.
- Every entry should state the relevant lane.
- Every entry should state `pass`, `fail`, `mixed`, `partial`, or `planning`.
- Every summary must respect the prereg framing lock.

## Infrastructure

| Artifact | Lane | Status | Path |
|---|---|---|---|
| Scaffold adaptation from `resattn` plus structure regression test | infrastructure | pass | `results/infrastructure/20260318-scaffold-adaptation.md` |
| Standalone repo bootstrap plus core-doc baggage cleanup | infrastructure | pass | `results/infrastructure/20260318-standalone-repo-bootstrap.md` |
| Final structural and novelty-alignment rigor audit | infrastructure | pass | `results/infrastructure/20260318-final-rigor-audit.md` |
| Initial runtime freeze plus deterministic WritingPrompts pilot/confirm split | infrastructure | pass | `results/infrastructure/20260318-initial-runtime-and-prompt-freeze.md` |

## Creativity Direction

| Artifact | Lane | Status | Path |
|---|---|---|---|
| First dense creativity-direction smoke on `google/gemma-2-2b` layer 12 over the frozen pilot split | creativity direction | partial | `results/creativity_direction/20260318-gemma2-2b-repeng-smoke-layer12/README.md` |
| Pilot dense-direction layer sweep over all Gemma 2 2B transformer layers | creativity direction | mixed | `results/creativity_direction/20260318-gemma2-2b-layer-sweep-pilot/README.md` |
| Template-controlled layer sweep showing no layer clears the instruction-template leakage control | creativity direction | mixed | `results/creativity_direction/20260318-gemma2-2b-layer-sweep-template-control/README.md` |
| Response-centered `v2` pilot artifact with matched creativity-vs-plain continuation pairs under a shared extraction wrapper | creativity direction | pass | `results/creativity_direction/20260318-gemma2-2b-response-pairs-v2-pilot/README.md` |
| Response-centered `v2` controlled layer sweep recovering a provisional late-layer candidate after removing the instruction-template confound | creativity direction | mixed | `results/creativity_direction/20260318-gemma2-2b-layer-sweep-response-pairs-v2/README.md` |
| Audit slice over the response-centered `v2` pair set showing that several strongest losses are still semantically competitive negatives rather than junk rows | creativity direction | mixed | `results/creativity_direction/20260318-gemma2-2b-response-pairs-v2-audit/README.md` |
| Audited `v3` counterpart rewrite artifact with `31 / 32` accepted rows and high content-preservation overlap | creativity direction | pass | `results/creativity_direction/20260318-gemma2-2b-response-pairs-v3-pilot/README.md` |
| Full-text `v3` layer sweep showing that the cleaner counterpart contrast still does not recover a usable dense creativity direction | creativity direction | fail | `results/creativity_direction/20260318-gemma2-2b-layer-sweep-response-pairs-v3/README.md` |
| Response-only `v3` layer sweep showing view-dependent raw winners without a stable dense creativity direction | creativity direction | fail | `results/creativity_direction/20260318-gemma2-2b-layer-sweep-response-pairs-v3-response-only/README.md` |

## Feature Decomposition

| Artifact | Lane | Status | Path |
|---|---|---|---|

## Feature Validation

| Artifact | Lane | Status | Path |
|---|---|---|---|

## Bridge Features

| Artifact | Lane | Status | Path |
|---|---|---|---|

## Steering Evaluation

| Artifact | Lane | Status | Path |
|---|---|---|---|
| Generation-side dense-direction smoke rerun with continuation-style neutral and creative prompt harnesses | steering evaluation | mixed | `results/steering_eval/20260318-gemma2-2b-generation-smoke/README.md` |
| Generation-side dense-direction smoke rerun from the response-centered `v2` sweep using the provisional late-layer candidates | steering evaluation | mixed | `results/steering_eval/20260318-gemma2-2b-generation-smoke-response-pairs-v2/README.md` |
| Bounded steering-scale calibration sweep on the response-centered `v2` late-layer band showing unstable coefficient-response behavior | steering evaluation | mixed | `results/steering_eval/20260318-gemma2-2b-v2-direction-calibration/README.md` |
| Full-text `v3` calibration sweep showing that the cleaner counterpart contrast still yields non-monotone dense-direction control behavior | steering evaluation | fail | `results/steering_eval/20260318-gemma2-2b-v3-direction-calibration/README.md` |
| Response-only `v3` calibration sweep showing that the alternative view changes candidate layers but not the instability | steering evaluation | fail | `results/steering_eval/20260318-gemma2-2b-v3-direction-calibration-response-only/README.md` |

## Creativity Benchmarks

| Artifact | Lane | Status | Path |
|---|---|---|---|

## Controller Extensions

| Artifact | Lane | Status | Path |
|---|---|---|---|

## Basin Dynamics

| Artifact | Lane | Status | Path |
|---|---|---|---|

## Figures

| Artifact | Lane | Status | Path |
|---|---|---|---|
