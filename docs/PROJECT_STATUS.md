# Project status

Last reviewed: 5 September 2026

## Readiness snapshot

| Area | Status | Evidence |
| --- | --- | --- |
| Package and CLI | Working | Installable package with modelling, benchmarking, effect-summary and intake-validation commands |
| Automated quality | Working | Ruff plus automated tests on Python 3.10 and 3.12 in GitHub Actions |
| Data contribution gate | Working | Minimum reactor-time-point contract with machine-readable errors and evidence-limit warnings |
| Synthetic workflow | Reproducible | Labelled synthetic input and deterministic reporting pipeline |
| Open experimental benchmark | Reproducible | Kozłowski et al. (2025) reactor-level trajectories and reference output |
| Zhang integration | Limited by source | Hash-verified private ingestion and summary analysis; original triplicates were lost |
| Independent dose-response challenge | Falsified as tested | Valentin & Białowiec (2024) external table: log-linear beats the twin's log-quadratic form on leave-one-dose-out RMSE |
| Global dose–temperature hypothesis | Not independently validated | Requires multi-dose, multi-temperature reactor trajectories; the dose-response *form* is now externally challenged (see above) |
| Parameter identifiability | Checked, and currently failing on the demo | `fit_global` reports parameter correlation and condition number; the 8-parameter model is already confounded (correlation ≈ 0.96) on the bundled synthetic demo |
| Effect-size uncertainty | Partially reported | Reactor-level percent-change effects now carry a 95% CI and a `low_replication` flag; published-table effects still carry no uncertainty at all |

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
- Every global fit reports whether its own 8 parameters are practically identifiable
  (`max_parameter_correlation`, `parameter_gram_condition_number`), instead of only
  reporting goodness of fit.
- `leave_one_batch_out` distinguishes held-out batches at the edge of the observed
  dose/temperature range (`is_boundary_condition`) from interior ones, so interpolation
  and extrapolation error are never silently averaged together.
- Reactor-level percent-change effect sizes carry a 95% confidence interval (delta method
  on the log response ratio) and a `low_replication` flag for any arm with fewer than
  3 reactors.

## What cannot be claimed now

- That biochar causally improves anaerobic digestion across studies.
- That the exploratory dose–temperature response generalises beyond the demonstration.
- That the digital twin's log-quadratic dose-response form is supported by independent data —
  on the Valentin & Białowiec (2024) table, held-out prediction favours a simpler log-linear
  form instead, for both methane potential and maximum rate.
- That an external kinetic-parameter table validates full reactor trajectories — it is a
  parameter-level challenge only; the paper's raw reactor time series were not obtained.
- That summary-curve residuals replace biological replicate uncertainty.
- That this research prototype is already an operational plant digital twin (see
  [README § Scope and terminology](../README.md#scope-and-terminology)): there is no
  mass/energy balance, reactor hydrodynamics, or live data-assimilation loop here.
- That the 8-parameter global model's individual parameter values are meaningful on their
  own — on the bundled synthetic demo dataset itself, the identifiability diagnostic already
  finds two parameters confounded at correlation ≈ 0.96, above the 0.95 warning threshold.
  No real dataset in this repository varies both dose and temperature with replicates, so
  this has never been checked on real data, only ruled out as achievable on the easiest
  possible (synthetic, noise-controlled) case.
- That the larger reported percent-change effects (e.g. the Valentin & Białowiec dose-response
  table) are statistically distinguishable from no effect — that table has no per-replicate
  standard deviation at all, so no confidence interval can be computed for it, and every row
  from it is flagged `low_replication` for that reason.

## Next validation gate

The next publication-level gate is an independent dataset containing:

1. reactor-level methane or biogas trajectories;
2. at least three biochar doses and more than one temperature;
3. biological or reactor replicates plus inoculum-only controls;
4. substrate, inoculum, S/I ratio, reactor and material metadata;
5. a preregistered held-out-study comparison against parsimonious baselines;
6. `max_parameter_correlation` below the identifiability threshold when the 8-parameter
   model is fitted to that dataset — a low-RMSE fit with confounded parameters does not
   satisfy this gate.

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
