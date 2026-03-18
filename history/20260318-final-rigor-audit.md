# Final Rigor Audit

## Goal

Compare `creativedecomp/` against the `resattn` operating scaffold and tighten any structural or methodological gaps that could weaken experimental execution rigor.

## Main Conclusions

- The top-level scaffold was directionally correct but initially too thin in three places:
  - tracked empty directories did not survive a fresh clone
  - `validation/` and runtime-freeze file locations were missing
  - `AGENTS.md` lacked several of the operational-control sections that make `resattn` resilient in long-running research
- The live strategy also needed stronger alignment to `research/experiment-novelty.md`, especially around:
  - framing the contribution as why creativity is mechanistically different from simpler concepts
  - comparing at least two signed decomposition methods on the pilot slice
  - keeping refusal and sentiment as required baseline comparisons
  - preserving the publishable negative-result path

## Changes Landed

- restored tracked empty-directory placeholders
- added `validation/`
- added `requirements.txt` and `requirements.lock.txt` placeholder locations
- expanded `AGENTS.md` to include the missing rigor-control sections
- tightened `CURRENT_STATE.md`, `history/PREREG.md`, `background-work/RESEARCH_POSITIONING.md`, and `configs/experiment.yaml`
- added regression tests for scaffold parity, AGENTS rigor, and novelty alignment

## Outcome

The repo now keeps the `resattn` operating structure where that structure matters for execution rigor, while keeping the live thesis and method logic specific to the creativity experiment.
