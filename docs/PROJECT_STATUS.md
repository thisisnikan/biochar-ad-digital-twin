# Project status

Last reviewed: 2 September 2026

## Readiness snapshot

| Area | Status | Evidence |
| --- | --- | --- |
| Package and CLI | Working | Installable package with `demo`, `fit`, `benchmark-experimental`, and `benchmark-external-dose` commands |
| Automated quality | Working | Ruff plus 22 tests on Python 3.10 and 3.12 in GitHub Actions |
| Synthetic workflow | Reproducible | Labelled synthetic input and deterministic reporting pipeline |
| Open experimental benchmark | Reproducible | Kozłowski et al. (2025) reactor-level trajectories and reference output |
| García Prats 2024 integration | Design-ready, outcome-limited | Open characteristics, context and treatment design; no exact reactor trajectories |
| García Prats 2025 intake | Waiting for raw data and permission | Metadata-only gate; unpublished abstract and numeric derivatives are not committed |
| Zhang integration | Limited by source | Hash-verified private ingestion and summary analysis; original triplicates were lost |
| Independent dose-response challenge | Falsified as tested | Valentin & Białowiec (2024) external table: log-linear beats the twin's log-quadratic form on leave-one-dose-out RMSE |
| Global dose–temperature hypothesis | Not independently validated | Requires multi-dose, multi-temperature reactor trajectories; the dose-response *form* is now externally challenged (see above) |

## What can be claimed now

- The software executes an auditable end-to-end BMP modelling workflow.
- Modified Gompertz has the lowest mean reactor-held-out RMSE within each treatment of the
  included Kozłowski et al. (2025) experiment.
- Author-shared Zhang et al. (2022) summaries can be analysed without inventing
  pseudo-replicates or publishing the private workbook.
- An independent 2024 glucose BMP dataset (Valentin & Białowiec) was used to stress-test the
  digital twin's log-quadratic dose-response form against simpler alternatives, and the
  repository reports the negative result rather than hiding it.
- The García Prats et al. (2024) material and experimental design can be integrated
  reproducibly without presenting prose summaries or digitized plots as raw outcomes.

## What cannot be claimed now

- That biochar causally improves anaerobic digestion across studies.
- That the exploratory dose–temperature response generalises beyond the demonstration.
- That the digital twin's log-quadratic dose-response form is supported by independent data —
  on the Valentin & Białowiec (2024) table, held-out prediction favours a simpler log-linear
  form instead, for both methane potential and maximum rate.
- That an external kinetic-parameter table validates full reactor trajectories — it is a
  parameter-level challenge only; the paper's raw reactor time series were not obtained.
- That summary-curve residuals replace biological replicate uncertainty.
- That García Prats et al. (2024) descriptor coverage validates a material-property
  response model; exact outcomes and reactor identities are still absent.
- That the author-shared García Prats 2025 abstract is a redistributable dataset.
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

For the pending García Prats study, the first permissible analysis after raw delivery is
same-batch treatment-versus-control estimation. Dose must not stand in for collection or
experimental batch; descriptor models then require leave-one-material and leave-one-study
validation. See [`GARCIA_PRATS_INTEGRATION.md`](GARCIA_PRATS_INTEGRATION.md).

## Maintenance checklist

- Keep `main` green on every merge.
- Regenerate committed reference results after model or data-processing changes.
- Record every public dataset's license, DOI, source hash and transformation decisions.
- Never commit author-shared files without explicit redistribution permission.
- Update this page whenever the scientific evidence boundary changes.
