# Biochar–AD Digital Twin

[![CI](https://github.com/thisisnikan/biochar-ad-digital-twin/actions/workflows/ci.yml/badge.svg)](https://github.com/thisisnikan/biochar-ad-digital-twin/actions)

A reproducible Python workflow for analysing batch biomethane potential (BMP)
experiments with biochar amendment. It fits all dose–temperature conditions
simultaneously, quantifies goodness of fit, and estimates parameter uncertainty
with a batch-aware residual bootstrap.

## Research question and falsifiable hypothesis

**Question.** Does explicitly modelling biochar dose and temperature explain and
predict cumulative methane production better than a condition-agnostic kinetic
baseline?

**Hypothesis.** A shared dose–temperature model will improve held-out-batch
prediction and AICc relative to a three-parameter modified Gompertz curve. The
hypothesis is rejected if that gain disappears on independent experimental data.

This project connects chemical-engineering kinetics, anaerobic digestion and
scientific Python. It was designed by **Nikan Haghighatjue**, building on his MSc
research on biochar characterization for anaerobic digestion.

> **Scientific status:** the included dose-response layer remains an exploratory,
> testable modelling hypothesis. A separate, openly licensed experimental dataset
> is now included for kinetic-baseline benchmarking, but it has one temperature and
> one carbon-material dose. It therefore does **not** validate the global
> dose-temperature hypothesis.

## Why this is useful

Most BMP curves are fitted one at a time. That makes it difficult to compare
operating conditions consistently. This tool uses a shared parameter set and
represents biochar dose and temperature explicitly:

- modified Gompertz methane-production kinetics;
- smooth, non-monotonic biochar dose response;
- Q10 temperature correction for production rate;
- robust global least-squares estimation;
- residual-bootstrap uncertainty that preserves batch structure;
- comparison with a parsimonious constant-Gompertz baseline using AIC, AICc and BIC;
- leave-one-batch-out validation to separate curve fitting from prediction;
- reproducible CSV, JSON and publication-ready PNG outputs.

## Model

For cumulative methane `M(t)`, the model uses:

```text
M(t) = P · exp{-exp[(e·R/P)(λ - t) + 1]}
```

`P` and `R` vary with `log(1 + dose)`, allowing both enhancement at moderate
dose and inhibition at excessive dose. Temperature changes `R` through a Q10
factor referenced to 37 °C. See `src/biochar_ad_twin/model.py` for the exact,
auditable implementation.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
biochar-ad demo --output outputs --bootstrap 100
```

The command creates:

- `synthetic_bmp_data.csv` — explicitly labelled demonstration data;
- `fit_summary.json` — fitted parameters and diagnostic metrics;
- `bootstrap_summary.csv` — uncertainty summary;
- `model_comparison.csv` — baseline comparison and ΔAICc;
- `leave_one_batch_out.csv` — prediction error for every held-out batch;
- `fitted_curves.png` — observed and fitted profiles.

## Real experimental benchmark

`data/experimental/kozlowski_2025_bmp.csv` contains reactor-level measurements
mechanically derived from the CC BY 4.0 publisher supplement to Kozłowski et al.
(2025), [Scientific Reports 15, 18728](https://doi.org/10.1038/s41598-025-02564-0).
It covers 12 food-waste reactor trajectories over 21 days at 37 °C: no carbon
material, torrefaction product, pyrolysis biochar, and hydrochar. Raw volumes,
blank correction, provenance, inclusion flags, and two source-data quality issues
are documented in `data/README.md`.

Run the experimental comparison with:

```bash
biochar-ad benchmark-experimental --output outputs/experimental
```

The benchmark compares first-order, modified Gompertz, and logistic cumulative
methane models separately within each treatment. The primary selection criterion
is leave-one-reactor-out RMSE. AIC/AICc/BIC are reported only as descriptive
secondary measures because points within a cumulative trajectory are
autocorrelated. The reproducible reference output and cautious interpretation are
stored in `results/experimental/`.

To fit an experimental dataset:

```bash
biochar-ad fit path/to/bmp_data.csv --output outputs
```

Required columns are `batch_id`, `time_days`, `dose_g_l`, `temperature_c`, and
`methane_ml_g_vs`.

## Quality controls

```bash
ruff check .
pytest -q
```

GitHub Actions runs both checks on Python 3.10 and 3.12.

## Responsible use and next validation step

Synthetic data tests software behaviour, not scientific validity. The real-data
benchmark tests kinetic curve families and reproducible data handling, not the
causal effect of biochar or the proposed dose-temperature response. A meaningful
next step is an independent multi-dose, multi-temperature dataset with reactor
replicates, preregistered comparison criteria, residual diagnostics, and practical
parameter-identifiability analysis.

## Interpretation rules

- `delta_aicc = 0` identifies the best-supported candidate within this limited set.
- Held-out error is the primary predictive check; training R² is descriptive only.
- Model selection cannot establish a causal biochar mechanism.
- Independent data and additional mechanistic baselines remain required before
  publication-level claims are appropriate.

## License

MIT
