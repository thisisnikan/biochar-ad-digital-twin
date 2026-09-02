# García Prats integration and evidence boundary

Status reviewed: 2 September 2026

## What is now public

The repository transcribes redistributable design and material data from García Prats
et al. (2024), *Characterization of biochars of different origin and application to the
anaerobic digestion of source-selected organic fraction of municipal solid waste under
batch conditions and at different dosages*, DOI
[`10.3389/fceng.2024.1384495`](https://doi.org/10.3389/fceng.2024.1384495).
The article is licensed CC BY 4.0.

The committed tables cover:

- three commercial biochars, including feedstock, source, pyrolysis temperature,
  manufacturer properties, BET area, pore size and CHNS values;
- two OFMSW collections and the inoculum, with density, TS, VS and pH;
- blank, cellulose, unamended and nine biochar-amended conditions at 1%, 5% and
  10% TS dose, including mass, working volume, triplicates and second-feeding selection.

The nominal g/L dose is recorded as the measured biochar mass divided by the 150 mL
working volume. It is not substituted for the paper's percentage-on-TS dose definition.

## Why outcomes are not transcribed

The main article exposes outcome curves and prose summaries, but the exact reactor-level
trajectories were not obtained. Relative-effect percentages also differ between the
abstract and the results narrative. Selecting one value or digitizing a plotted mean
would create false precision and still would not recover biological replicates.

Consequently, the open integration is limited to exact design/material tables. The
generated result is a coverage audit with `public_outcome_measurements_committed = 0`.
This is a deliberate quality decision, not a missing-data imputation.

## Unpublished 2025 study

Marta García Prats also shared a conference extended abstract for a full paper under
revision. No explicit redistribution permission accompanied it, and no raw reactor data
were supplied. The public repository therefore includes only the metadata-only intake
gate in `data/pending/garcia_prats_2025/`; it does not include the PDF, its tables, or
numeric derivatives.

The first modelling gate after raw delivery is batch-matched treatment effect estimation:

```text
delta_log_P = log(P_treatment / P_control_same_batch)
delta_log_R = log(R_treatment / R_control_same_batch)
delta_lag   = lag_treatment - lag_control_same_batch
```

Batch must remain explicit because a dose effect cannot be separated from a collection
or experimental batch when they move together. Material descriptors can then enter as
predictors with dose interactions, followed by leave-one-biochar-out and
leave-one-batch-or-study-out validation. Correlation screening and PCA remain exploratory,
especially with few materials and collinear descriptors.

## Claim boundary

This integration expands **descriptor and design coverage**. It does not validate the
current global dose–temperature equation, demonstrate a causal biochar mechanism, or
convert the repository into an operational digital twin. Those claims still require
exact reactor trajectories, same-batch controls, intact replicates and independent
held-out studies.
