# Changelog

All notable project changes are documented here. The project follows a research-prototype
release model while the public API remains experimental.

## Unreleased

- Added a cross-study identifiability audit (`03_identifiability/`, `biochar-ad
  audit-identifiability`): a source-linked study metadata manifest, deterministic
  bipartite-overlap and additive design-matrix-rank diagnostics, and a plain-language
  explanation of why a connected acyclic (nested) design can support additive
  estimation under an explicit assumption while a disconnected design is structurally
  confounded regardless of assumptions. Current result: the three included studies'
  lab-inoculum design is not yet jointly estimable even under additivity, which is a
  data-design finding, not a rejection of the average biochar effect.
- Fixed a lint-only regression in `tests/test_zhang_2022_analysis.py` (a stray
  module-level `import pytest` at end of file) so `ruff check .` passes again.
- Reworked the presentation deck to chart the actual committed results (Kozłowski 2025
  kinetic-baseline comparison and the Valentin & Białowiec 2024 dose-response challenge)
  instead of illustrative figures, so the deck argues from data.
- Added an independent dose-response challenge against Valentin & Białowiec (2024): the
  digital twin's log-quadratic dose response is not supported over this external dose range,
  where a simpler log-linear form has lower held-out error.
- Improved repository navigation, contribution guidance and scientific-status reporting.
- Added `docs/ARCHITECTURE.md`, a plain-language map and glossary for readers new to
  biomethane potential (BMP) modelling.
- Consolidated the two presentation decks into a single general-audience overview deck
  (`presentation/index.html`) and removed the meeting-specific Hohenheim deck.
- Added the open Kozłowski et al. (2025) reactor-level kinetic benchmark.
- Added private, hash-verified Zhang et al. (2022) ingestion and summary-analysis workflows.

## 0.1.0 — 2026-08-20

- Released the initial global dose–temperature BMP modelling workflow.
- Added model comparison, batch-aware bootstrap uncertainty and held-out-batch validation.
