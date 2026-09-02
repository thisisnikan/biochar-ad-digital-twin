# García Prats 2025 data-intake gate

Status reviewed: 2 September 2026

This directory is a public **metadata-only intake scaffold**. It contains no values,
tables, figures or files from the author-shared conference extended abstract.

## Current access boundary

- The full paper is under revision and is not public.
- The author shared an extended abstract, but did not grant permission to redistribute it.
- Reactor-level methane trajectories and their metadata have not been received.
- The PDF and any numeric values derived only from it must not be committed.
- A local source file, if later supplied for analysis, belongs under
  `data/private/garcia_prats_2025/`, which is excluded by `.gitignore`.

The public repository can record the intake contract and validation decisions, but it
cannot treat an unpublished summary as an open dataset.

## Required reactor-level delivery

One row per bottle and sampling time is preferred, with at least:

```text
study_id,batch_id,bottle_id,replicate_id,condition_id,time_days,
biochar_id,dose_pct_ts,dose_g_l,temperature_c,cumulative_methane_ml,
cumulative_methane_ml_g_vs,blank_corrected
```

A separate material table should preserve feedstock, pyrolysis conditions, pH,
electrical conductivity, elemental composition, surface-area and pore descriptors,
including their units and analytical method. Substrate, inoculum, reactor loading,
S/I ratio and blank-correction metadata are required at batch level.

## Checks before modelling

1. Preserve collection or experimental batch explicitly; never pool it into dose.
2. Compare every amended bottle only with the control from the same batch.
3. Retain biological/reactor replicates instead of reconstructing pseudo-replicates.
4. Verify mass-basis versus atomic-basis elemental ratios and all dose units.
5. Flag transcription anomalies for author confirmation; do not silently repair them.
6. Treat small-sample correlations and PCA as exploratory, with multiplicity and
   leave-one-material sensitivity checks.
7. Obtain explicit redistribution permission before moving source or derived numeric
   data out of the ignored private paths.

The planned response variables are control-normalized effects such as
`log(P_treatment / P_control_same_batch)` and the equivalent rate ratio, with lag
reported as a within-batch difference. This formulation is a preregistered direction,
not a result from the unavailable raw data.
