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
| Full-text `v3` Olson-style `mean_difference` sweep recovering layer `23` as a controlled dense-direction winner on the same counterpart slice | creativity direction | pass | `results/creativity_direction/20260318-gemma2-2b-layer-sweep-response-pairs-v3-mean-difference/README.md` |
| Response-only `v3` Olson-style `mean_difference` sweep recovering layer `9` while remaining weaker than the full-text path | creativity direction | mixed | `results/creativity_direction/20260318-gemma2-2b-layer-sweep-response-pairs-v3-response-only-mean-difference/README.md` |

## Simpler-Concept Baselines

| Artifact | Lane | Status | Path |
|---|---|---|---|
| Matched refusal layer sweep on the same Gemma 2 2B stack recovering a very clean hidden-state refusal direction at layer `15` | refusal baseline | pass | `results/refusal_direction/20260318-gemma2-2b-layer-sweep-v1-mean-difference/README.md` |
| Bounded Gemma 2 9B refusal layer sweep showing that the larger base model still yields a perfectly clean hidden-state refusal control at layer `18` | refusal baseline | pass | `results/refusal_direction/20260318-gemma2-9b-layer-sweep-v1-mean-difference/README.md` |
| Smoke instruction-tuned refusal layer sweep on the smallest feasible GemmaScope v2-backed Gemma stack confirming the hidden-state extraction path works end to end | refusal baseline | partial | `results/refusal_direction/20260318-gemma3-270m-it-layer-sweep-smoke/README.md` |
| Full instruction-tuned refusal layer sweep on `google/gemma-3-270m-it` recovering a perfect hidden-state refusal direction at layer `9` | refusal baseline | pass | `results/refusal_direction/20260318-gemma3-270m-it-layer-sweep-v1-mean-difference/README.md` |

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
| Full-text `v3` Olson-style `mean_difference` calibration showing a usable bounded control regime around layer `23` and coeffs `0.5` to `1.0` | steering evaluation | pass | `results/steering_eval/20260318-gemma2-2b-v3-direction-calibration-mean-difference/README.md` |
| Response-only `v3` Olson-style `mean_difference` calibration improving over PCA but remaining weaker and more view-dependent | steering evaluation | mixed | `results/steering_eval/20260318-gemma2-2b-v3-direction-calibration-response-only-mean-difference/README.md` |
| Pilot output-level gate on the recovered full-text `mean_difference` direction, corrected to order-robust paired judging and collapsing almost entirely to ties under the current local metric | steering evaluation | mixed | `results/steering_eval/20260318-gemma2-2b-output-gate-v1/README.md` |
| Blinded cached-output manual audit showing only a weak prompt-only edge under a stricter prompt-grounded-creativity plus coherence rubric | steering evaluation | mixed | `results/steering_eval/20260318-gemma2-2b-output-gate-v1-manual-audit/README.md` |
| Stricter prompt-grounded-creativity gate rerun on cached outputs that weakly recovers the prompt-only baseline but still shows no dense steering effect versus neutral | steering evaluation | mixed | `results/steering_eval/20260318-gemma2-2b-output-gate-v2-prompt-grounded-creativity/README.md` |
| First matched refusal calibration on the same 2B stack showing clean hidden-state refusal but noisy prompt-sensitive dense generations | steering evaluation | mixed | `results/steering_eval/20260318-gemma2-2b-refusal-direction-calibration/README.md` |
| Chat-style refusal calibration rerun showing that the base-model lane becomes less grounded under a chat wrapper | steering evaluation | fail | `results/steering_eval/20260318-gemma2-2b-refusal-direction-calibration-v2-chat-wrap/README.md` |
| Prefilled-refusal calibration rerun restoring grounded requests while still showing noisy dense refusal outputs | steering evaluation | mixed | `results/steering_eval/20260318-gemma2-2b-refusal-direction-calibration-v3-prefilled-refusal/README.md` |
| First refusal output gate showing no usable prompt-only refusal baseline and no clean dense refusal win under the generic wrapper | steering evaluation | fail | `results/steering_eval/20260318-gemma2-2b-refusal-output-gate-v1/README.md` |
| Prefilled-refusal output gate weakly recovering the prompt-only refusal baseline while dense refusal steering still fails the clean output gate | steering evaluation | mixed | `results/steering_eval/20260318-gemma2-2b-refusal-output-gate-v2-prefilled-refusal/README.md` |
| Bounded Gemma 2 9B refusal output gate showing that the larger model still does not rescue a clean dense refusal win versus neutral | steering evaluation | fail | `results/steering_eval/20260318-gemma2-9b-refusal-output-gate-v1-bounded/README.md` |
| Bounded sparse SAE-latent refusal output gate showing that a top-32 GemmaScope intervention also fails to rescue the matched refusal gate on Gemma 2 2B | steering evaluation | fail | `results/steering_eval/20260318-gemma2-2b-refusal-sae-latent-output-gate-v1/README.md` |
| Smoke instruction-tuned refusal output gate confirming that the matched gate runs cleanly on the smallest feasible GemmaScope v2-backed Gemma stack | steering evaluation | partial | `results/steering_eval/20260318-gemma3-270m-it-refusal-output-gate-smoke/README.md` |
| Full instruction-tuned refusal output gate showing that prompt-only and dense refusal still collapse to ties versus neutral on `google/gemma-3-270m-it` | steering evaluation | fail | `results/steering_eval/20260318-gemma3-270m-it-refusal-output-gate-v1/README.md` |

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
