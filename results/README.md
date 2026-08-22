# Reproducible experimental results

`experimental/kinetic_baseline_comparison.csv` is generated with:

```bash
biochar-ad benchmark-experimental --output results/experimental
```

Across this single 2025 experiment, modified Gompertz produced the lowest mean
leave-one-reactor-out RMSE for all four treatments. This is a dataset-specific
predictive result, not evidence that the model captures a biochar mechanism.
Information criteria are secondary because cumulative measurements from the same
reactor are temporally autocorrelated.

| Treatment | Valid reactors | Best model | Held-out RMSE (mL CH4/g VS) |
| --- | ---: | --- | ---: |
| Food waste | 3 | Modified Gompertz | 12.83 |
| Food waste + hydrochar (240 °C) | 3 | Modified Gompertz | 6.94 |
| Food waste + pyrolysis biochar (600 °C) | 2 | Modified Gompertz | 5.82 |
| Food waste + torrefaction product (240 °C) | 2 | Modified Gompertz | 7.94 |
