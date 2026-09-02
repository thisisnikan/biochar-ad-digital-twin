# Changelog

All notable project changes are documented here. The project follows a research-prototype
release model while the public API remains experimental.

## Unreleased

- Added CC BY 4.0 García Prats et al. (2024) biochar descriptors, material context and
  treatment-design tables, plus a reproducible coverage/boundary audit.
- Added a metadata-only intake gate for the unpublished García Prats 2025 study; no
  author-shared document, table value or numeric derivative is redistributed.
- Documented the future same-batch treatment-effect formulation and the requirement to
  separate dose from collection/experimental batch before descriptor modelling.
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
