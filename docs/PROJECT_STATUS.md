# Project status

Last reviewed: 5 September 2026

## Readiness snapshot

| Area | Status | Evidence |
| --- | --- | --- |
| Package and CLI | Working | Installable package with modelling, benchmarking, effect-summary and intake-validation commands |
| Automated quality | Working | Ruff plus automated tests on Python 3.10 and 3.12 in GitHub Actions |
| Data contribution gate | Working | Minimum reactor-time-point contract with machine-readable errors and evidence-limit warnings |
| Real-data contract import | Reproducible, source conflict flagged | 7,575 observations from 15 Kozłowski reactors, including individual blanks; [validation and gaps](../results/intake/README.md) |
| Synthetic workflow | Reproducible | Labelled synthetic input and deterministic reporting pipeline |
| Open experimental benchmark | Reproducible | Kozłowski et al. (2025) reactor-level trajectories and reference output |
| Zhang integration | Limited by source | Hash-verified private ingestion and summary analysis; original triplicates were lost |
| Independent dose-response challenge | Falsified as tested | Valentin & Białowiec (2024) external table: log-linear beats the twin's log-quadratic form on leave-one-dose-out RMSE |
| Global dose–temperature hypothesis | Not independently validated | Requires multi-dose, multi-temperature reactor trajectories; the dose-response *form* is now externally challenged (see above) |

## What can be claimed now

- The software executes an auditable end-to-end BMP modelling workflow.
- Reactor-level contributions can be checked for identity, controls, replicate structure,
  raw/processed coexistence, QC and row-level provenance before modelling.
- Modified Gompertz has the lowest mean reactor-held-out RMSE within each treatment of the
  included Kozłowski et al. (2025) experiment.
- Author-shared Zhang et al. (2022) summaries can be analysed without inventing
  pseudo-replicates or publishing the private workbook.
- An independent 2024 glucose BMP dataset (Valentin & Białowiec) was used to stress-test the
  digital twin's log-quadratic dose-response form against simpler alternatives, and the
  repository reports the negative result rather than hiding it.

## What cannot be claimed now

- That biochar causally improves anaerobic digestion across studies.
- That the exploratory dose–temperature response generalises beyond the demonstration.
- That the digital twin's log-quadratic dose-response form is supported by independent data —
  on the Valentin & Białowiec (2024) table, held-out prediction favours a simpler log-linear
  form instead, for both methane potential and maximum rate.
- That an external kinetic-parameter table validates full reactor trajectories — it is a
  parameter-level challenge only; the paper's raw reactor time series were not obtained.
- That summary-curve residuals replace biological replicate uncertainty.
- That this research prototype is already an operational plant digital twin.

## Next validation gate

The next publication-level gate is an independent dataset containing:

1. reactor-level methane or biogas trajectories;
2. at least three biochar doses and more than one temperature;
3. biological or reactor replicates plus inoculum-only controls;
4. substrate, inoculum, S/I ratio, reactor and material metadata;
5. a preregistered held-out-study comparison against parsimonious baselines.

The Valentin & Białowiec (2024) table satisfies part of criterion 2 (five doses) at the
kinetic-parameter level, but not criteria 1 or 3: it has one temperature and no raw reactor
trajectories or replicate-level residuals. Independent reactor-level, multi-temperature data
with intact replicates is still required.

Until that gate is passed, the repository should be described as a **reproducible research
prototype for falsifiable kinetic modelling**, not as a validated predictive product.

## Maintenance checklist

- Keep `main` green on every merge.
- Regenerate committed reference results after model or data-processing changes.
- Record every public dataset's license, DOI, source hash and transformation decisions.
- Never commit author-shared files without explicit redistribution permission.
- Update this page whenever the scientific evidence boundary changes.
