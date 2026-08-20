# Scientific validation roadmap

This repository is an empirical kinetic-modelling framework, not yet a validated
process digital twin. The distinction is intentional: a digital twin normally
requires a persistent connection to a physical system, online state estimation,
or repeated calibration against incoming measurements.

## Evidence supporting the current design

- Modified Gompertz, logistic, first-order and Cone-type models are commonly
  compared when interpreting cumulative methane curves.
- A nonlinear biochar response is plausible. Published experiments report an
  optimum followed by reduced benefit or inhibition at larger dosages.
- A shared dose-response layer can be useful for hypothesis generation when all
  batches use the same substrate, inoculum and biochar.

## Claims the current software does not make

- Synthetic-data accuracy is not evidence of experimental validity.
- One fitted dose optimum cannot be transferred to another biochar or substrate.
- A Q10 relationship across mesophilic and thermophilic regimes does not prove a
  shared microbial mechanism.
- High R² alone does not establish that a kinetic model is preferable.

## Benchmarking protocol

Version 0.2 fits first-order, modified Gompertz, modified logistic and Cone
models independently to every batch. It reports RMSE, MAE, R², AICc, BIC and a
late-time holdout RMSE. Model selection should consider all metrics together,
residual structure and parameter plausibility.

## Required steps before publication-level use

1. Use inoculum-blank-corrected methane volumes normalized to added VS and dry
   gas at a declared reference temperature and pressure.
2. Include biological replicates and retain a `replicate_id` column.
3. Inspect residual autocorrelation and heteroscedasticity.
4. Replace point-wise residual resampling with replicate-level or time-blocked
   uncertainty estimation.
5. Treat mesophilic and thermophilic conditions as separate biological regimes,
   then test whether a shared temperature relationship is supported.
6. Add biochar pH, ash, BET surface area, feedstock and pyrolysis temperature
   before attempting transfer across biochars.
7. Validate the chosen model on independent experimental batches.

## Primary studies motivating the audit

- Senol et al. (2026), biochar and zeolite under three salinity levels; this is
  the closest published match to the repository's intended use and includes a
  previously contacted researcher:
  https://doi.org/10.1016/j.biortech.2026.134345
- da Borso et al. (2021), open-access aquaculture-sludge endpoints and published
  first-order/Gompertz parameters:
  https://doi.org/10.3390/app11020552
- Ngo et al. (2024), pristine/recovered biochar in high-solids chicken-manure AD:
  https://doi.org/10.1016/j.clwas.2023.100126
- Shi et al. (2022), dosage effects under oily-sludge inhibition:
  https://doi.org/10.1016/j.jhazmat.2021.126819
- Ma et al. (2021), response-surface optimization for chicken manure:
  https://doi.org/10.1016/j.biortech.2021.124697
- Hakimi et al. (2023), comparison of kinetic models in co-digestion:
  https://doi.org/10.1016/j.heliyon.2023.e17096
- Ulukardesler (2023), first-order, Gompertz and logistic comparison:
  https://doi.org/10.1038/s41598-023-33169-0
