# Resattn Scaffold Adaptation

## Context

This workspace started with only the core research notes under `research/`. Sohail asked for the `~/resattn` operating scaffold and AGENTS shape to be copied here and adapted to this experiment.

## What Was Reused

- top-level operating files: `CURRENT_STATE.md`, `DECISIONS.md`, `SCRATCHPAD.md`, `THOUGHT_LOG.md`
- history, journal, sessions, and results indexing structure
- background-work split for references, synthesis, and methodology notes
- the general AGENTS layout: scope, mission, thesis locks, runtime assumptions, epistemic standards, directory map, navigation guide, and operating rules

## What Was Changed

- removed all depth-routing, oracle-alpha, Figure 8, and tool-breakage assumptions
- replaced the thesis with the creativity-direction and SAE-decomposition experiment
- replaced results lanes with creativity-specific lanes:
  - `creativity_direction`
  - `feature_decomposition`
  - `feature_validation`
  - `bridge_features`
  - `steering_eval`
  - `creativity_benchmarks`
  - `controller_extensions`
  - `basin_dynamics`
- recorded the current git-state blocker honestly instead of pretending this directory is already a standalone repo

## Result

`creativedecomp/` now has the same kind of disciplined research operating scaffold as `resattn`, but aimed at the mechanistic creativity experiment defined by the local research documents.
