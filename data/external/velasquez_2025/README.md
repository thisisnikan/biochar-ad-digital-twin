# Velasquez 2025 negative-control dataset

## Provenance

Author-shared raw OriginLab project received directly from Jean Agustin Velasquez Pinas on 2026-09-01 in response to a targeted request for reactor-level methane/biogas trajectories, controls, replicate information, blank corrections, substrate/inoculum metadata and biochar characterization data.

The author stated that the OriginLab project contains all raw experimental data and also includes DRX/XRD information not reported in the article.

## Redistribution status

The original `.opju` file is privately shared author data and **must not be committed or redistributed** without explicit permission from the author.

Only analysis code, provenance metadata, schema definitions, and derived outputs that are safe to share should be committed here.

## Immediate analysis target

The first analysis focuses on the two BMP workbooks identified in the Origin project:

- `BMPEN1`
- `BMPEN2`

The intended tidy schema is:

`experiment, treatment, biochar_type, pyrolysis_temperature_C, dose, replicate, time, cumulative_methane`

The control mapping must be verified before any mechanistic interpretation.

## Planned falsification test

1. Preserve reactor-level replicates.
2. Reproduce the published treatment-level methane result.
3. Quantify methane attributable to biodegradable carbon from biochar/negative-control reactors.
4. Estimate residual methane enhancement after that contribution is removed.
5. Compare a control kinetic model, a generic biochar dose-response model, a biochar-as-co-substrate model, and a co-substrate-plus-residual-material-effect model.
6. Only after the residual analysis, test whether material descriptors such as pyrolysis temperature, CHONS, conductivity, TGA, FTIR or XRD explain remaining variance.

## Required local files

For reproducible analysis, export the `BMPEN1` and `BMPEN2` worksheets from Origin/Origin Viewer as CSV files and place them locally as:

- `data/private/velasquez_2025/BMPEN1.csv`
- `data/private/velasquez_2025/BMPEN2.csv`

These private raw exports should remain untracked.
