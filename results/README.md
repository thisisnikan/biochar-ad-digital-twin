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

## Independent dose-response result

`external-dose/dose_response_comparison.csv` is generated with:

```bash
biochar-ad benchmark-external-dose --output results/external-dose
```

Valentin & Białowiec (2024) provide five independent dose conditions but only
table-level kinetic estimates. Leave-one-dose-out testing ranks the log-linear
response ahead of the current log-quadratic form for both methane potential and
maximum production rate. With only five doses, this is a falsification-oriented
stress test rather than evidence for a universal response law. The current
dose-invariant lag assumption is also not supported descriptively: published lag
estimates span 0.10–0.76 days.

## Within-study treatment effects

`effects/within_study_effects.csv` puts the two public outcome datasets on a
common, dimensionless scale using `log(treatment / same-study control)` for
modified-Gompertz potential and maximum rate. The rows remain stratified: the
Kozłowski values come from reactor-level fits and retain between-reactor standard
deviations, whereas the Valentin values are published condition parameters
without reported parameter uncertainty. No pooled cross-study estimate is reported.

Within Kozłowski, fitted potential is 4.5–11.9% above the same-study control,
while fitted maximum rate is 1.6–7.4% lower. The Valentin table shows both
parameters increasing with dose. The contrast motivates context-aware modelling;
it does not identify whether material, substrate, dose or another study difference
caused the disagreement.

Every row now also carries a 95% confidence interval on `percent_change` (delta
method on the log response ratio) and a `low_replication` flag. Two of the six
Kozłowski rows — the hydrochar and torrefaction maximum-rate effects — have a CI
that crosses zero, so their point-estimate direction should not be read as a
settled effect; this holds even for hydrochar, which has 3 valid reactors, so
crossing zero is not only a low-replication artifact here. All eight
Valentin & Białowiec rows are flagged `low_replication` and carry no CI at all:
the published table reports point estimates only, with no per-replicate
standard deviation.

```bash
biochar-ad summarize-effects --output results/effects
```
