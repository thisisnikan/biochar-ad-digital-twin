# Changelog

## 2026-09-05

- Compare constant, log-linear and log-quadratic candidates on identical batch
  holdouts, with shared fitting settings and per-model summaries.
- Fix Q10 at one training temperature, reject unsupported temperature holdouts,
  and surface failed optimizer convergence.
- Document dose-first, temperature-second validation and public-source access;
  independent raw data acquisition remains pending.
- Added a hash-verified real-data intake export for all 15 Kozłowski reactors,
  including individual blanks, cell references, VS denominators and source-dose conflicts.
- Added the deterministic compressed CSV, validation JSON and remaining-evidence report;
  preserved the original benchmark CSV and exclusions.
- Hardened the experimental intake gate against empty files, non-finite numeric values,
  missing dose units and positive doses without a physical unit.
- Compare parsed times and metadata consistently while preserving source values.
- Distinguish substrate controls from inoculum blanks and count only QC-included
  reactors for control and replication warnings, retaining all submitted records.

## 2026-09-03

- Added a minimum experimental record for reactor-level Biochar–AD contributions.
- Added `biochar-ad validate-intake` with machine-readable errors and scientific-limit warnings.
- Added a worked CSV template and tests for duplicate keys, changing reactor metadata and missing blanks.

All notable project changes are documented here. The project follows a research-prototype
release model while the public API remains experimental.

## Unreleased

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
