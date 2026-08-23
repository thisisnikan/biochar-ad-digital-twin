# Experimental data provenance

## Kozłowski et al. (2025)

`experimental/kozlowski_2025_bmp.csv` is a tidy, mechanically derived version of the
publisher's XLSX supplement to:

> Kozłowski, M., Papaj, B., Sobieraj, K., Świechowski, K., Kosiorowska, K. &
> Białowiec, A. *The effect of different carbon materials' addition on the
> biomethane production from food waste*. Scientific Reports 15, 18728 (2025).
> https://doi.org/10.1038/s41598-025-02564-0

- Article and supplement license: CC BY 4.0.
- Publisher supplement: `41598_2025_2564_MOESM1_ESM.xlsx`.
- Verified source SHA-256:
  `a5be0c25990acbdd0a6ac14dfa202398e61713fea8496884018e97f1cf87b983`.
- Experiment: triplicate mesophilic (37 °C) batch digestion for 21 days, with food
  waste alone or a 5 g/L carbon-material addition.
- Raw source columns retained: reactor-level cumulative methane volume and the
  corresponding inoculum-control mean.
- Processed response: blank-corrected cumulative methane divided by substrate VS,
  matching the source workbook's calculation.

### Explicit data-quality decisions

The source workbook's derived `Days` column ends at 5.25 while its hourly index and
day label end at 504 hours and day 21. The tidy dataset therefore defines
`time_days = time_hours / 24` and retains the inconsistent source value in
`source_reported_time_days` for auditability.

Torrefaction replicate 2 and pyrolysis replicate 3 are retained but marked
`included_in_benchmark = false`. The publisher workbook excludes these same reactor
signals from its displayed treatment averages, and their raw trajectories are
inconsistent with sibling reactors. No observations are deleted or silently clipped.

Rebuild the CSV from a local or downloaded source workbook:

```bash
python scripts/build_kozlowski_2025_dataset.py
```

The script verifies the source hash before parsing it.

## Valentin & Białowiec (2024)

`experimental/valentin_bialowiec_2024_parameters.csv` transcribes the five dose
conditions and published modified-Gompertz estimates from Table 3 of:

> Valentin, M. T. & Białowiec, A. *Impact of using glucose as a sole carbon
> source to analyze the effect of biochar on the kinetics of biomethane
> production*. Scientific Reports 14, 8656 (2024).
> https://doi.org/10.1038/s41598-024-59313-y

- Article license: CC BY 4.0.
- Experiment: triplicate 37 °C reactors with glucose, wheat-straw biochar
  produced at 900 °C, and doses of 0, 2, 4, 6, and 8 g/L.
- Scope: exact table-level cumulative BMP, fit statistics, potential, maximum
  rate, rate constant, and lag; these are published estimates, not raw reactor
  trajectories.
- The article reports 86,400 raw cases but states that those data are available
  from the corresponding author on reasonable request. They are not reconstructed
  or represented here as open raw data.
