# Zhang et al. (2022) private-summary analysis

This workflow analyses the author-shared, inoculum-blank-corrected treatment means
without publishing the workbook or reconstructing the lost triplicates.

## Scope

The script produces private treatment-level metrics for cumulative methane,
modified-Gompertz parameters, descriptive comparisons with logistic and
first-order curves, total VFA removal, pH stability, and small-sample exploratory
correlations with publicly reported biochar characteristics.

Run after private ingestion:

```bash
python scripts/analyze_zhang_2022_summary.py \
  --methane data/private/zhang_2022/methane_summary.csv \
  --process data/private/zhang_2022/process_summary.csv \
  --characteristics data/experimental/zhang_2022_biochar_characteristics.csv
```

Outputs default to `results/private/zhang_2022/`, which is excluded from Git.

## Interpretation boundary

- Model AICc and residual statistics are descriptive because time points within a
  cumulative mean trajectory are autocorrelated.
- The missing reactor-level triplicates prevent replicate-held-out validation,
  empirical uncertainty propagation, and new significance tests.
- Correlations across five pyrolysis-temperature biochars are exploratory and
  cannot establish DIET or another causal mechanism.
- Public results should cite DOI `10.1007/s42773-022-00187-6`; the private workbook
  must not be redistributed without permission.
