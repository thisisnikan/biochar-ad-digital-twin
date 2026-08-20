# Biochar–AD Digital Twin

[![CI](https://github.com/thisisnikan/biochar-ad-digital-twin/actions/workflows/ci.yml/badge.svg)](https://github.com/thisisnikan/biochar-ad-digital-twin/actions)

A reproducible Python workflow for analysing batch biomethane potential (BMP)
experiments with biochar amendment. It fits all dose–temperature conditions
simultaneously, quantifies goodness of fit, and estimates parameter uncertainty
with a batch-aware residual bootstrap.

This project connects chemical-engineering kinetics, anaerobic digestion and
scientific Python. It was designed by **Nikan Haghighatjue**, building on his MSc
research on biochar characterization for anaerobic digestion.

> **Scientific status:** the included dose-response layer is an exploratory,
> testable modelling hypothesis. The demo dataset is synthetic and clearly
> labelled. The repository does not claim experimental validation.

## Why this is useful

Most BMP curves are fitted one at a time. That makes it difficult to compare
operating conditions consistently. This tool uses a shared parameter set and
represents biochar dose and temperature explicitly:

- modified Gompertz methane-production kinetics;
- smooth, non-monotonic biochar dose response;
- Q10 temperature correction for production rate;
- robust global least-squares estimation;
- residual-bootstrap uncertainty that preserves batch structure;
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
- `fitted_curves.png` — observed and fitted profiles.

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

Synthetic data tests software behaviour, not scientific validity. A meaningful
next step is to fit independent experimental BMP data, inspect residuals, test
parameter identifiability, and compare the model against simpler Gompertz and
first-order baselines using information criteria or held-out prediction.

## License

MIT
