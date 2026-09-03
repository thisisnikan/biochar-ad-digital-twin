# Minimum Experimental Record

This contract defines the smallest reactor-level contribution that can support an
auditable Biochar–AD analysis. It is an intake gate, not a claim that every valid
file can answer the project's global dose–temperature hypothesis.

## Grain and identity

Each row is **one observation from one physical reactor at one time point**. Never
expand a treatment mean into pseudo-replicates. The combination
`study_id + experiment_id + reactor_id + time_days` must be unique.

Start from `data/templates/reactor_observations.csv` and validate the completed file:

```bash
biochar-ad validate-intake path/to/reactor_observations.csv
```

The command prints a machine-readable JSON report and exits with status 2 when an
error makes ingestion unsafe. Warnings preserve limited datasets while making their
evidence boundary explicit.

## Required fields

| Group | Fields | Purpose |
| --- | --- | --- |
| Identity | `study_id`, `experiment_id`, `reactor_id`, `treatment_id`, `replicate_id` | Preserve independent experimental units |
| Time/process | `time_days`, `temperature_c` | Locate every measurement in the process |
| Design | `is_control`, `is_inoculum_blank`, `substrate_id`, `inoculum_id`, `material_id` | Separate material, substrate and inoculum effects |
| Dose | `dose_value`, `dose_unit` | Preserve the reported dose without silent conversion |
| Response | `raw_cumulative_methane_ml`, `blank_corrected_methane_ml_g_vs` | Keep source measurement and processed outcome together |
| QC | `qc_include`, `qc_flags` | Exclude transparently without deleting observations |
| Provenance | `data_origin`, `source_record_id` | Trace each row back to a sheet, cell, table or instrument record |

Allowed `dose_unit` values are `g_l`, `g_g_vs`, `pct_ts`, `mg_reactor`, and `none`.
Use `material_id = none` and a zero dose for no-additive controls. Inoculum-only
blanks may leave `blank_corrected_methane_ml_g_vs` empty because they contain no
substrate VS denominator.

## Validation rules and evidence limits

The automated gate rejects missing identifiers, invalid numbers or booleans,
negative time/dose, duplicate observation keys, unsupported dose units, changing
reactor metadata, and included rows without a raw methane measurement.

It warns about missing processed yields, missing controls, missing inoculum blanks,
unreplicated treatments and decreasing cumulative raw trajectories. A warning is a
scientific limitation to report, not permission to manufacture missing information.

Passing this gate establishes structural integrity only. Causal mechanism claims,
global dose response, temperature extrapolation and plant-level control still require
appropriate factorial designs and genuinely held-out reactors or studies.
