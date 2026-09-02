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

## Zhang et al. (2022)

`experimental/zhang_2022_biochar_characteristics.csv` contains the five
pyrolysis-temperature biochar descriptors reported in Table 1 and the Raman
`I_D/I_G` values reported in the article text:

> Zhang, C., Yang, R., Sun, M. et al. Wood waste biochar promoted anaerobic
> digestion of food waste: focusing on the characteristics of biochar and
> microbial community analysis. Biochar 4, 62 (2022).
> https://doi.org/10.1007/s42773-022-00187-6

- Article license: CC BY 4.0.
- Experiment: triplicate 37 °C food-waste batch digestion with 10 g/L wood-waste
  biochar prepared at several pyrolysis temperatures and residence times.
- The public table records surface O/C ratio, XPS-derived oxygen-containing bond
  percentages, and Raman `I_D/I_G`; it does not infer missing properties.

On 2026-08-26, Chao Zhang also shared a workbook containing post-processed
treatment means and standard deviations for cumulative methane, pH, and six VFAs.
The methane series are already inoculum-blank corrected. The original triplicate
files are no longer available, so the shared workbook cannot support
replicate-held-out validation or empirical replicate resampling.

The workbook is not redistributed while public-repository permission is pending.
`scripts/build_zhang_2022_dataset.py` verifies the private source hash and builds
ignored long-form methane and process-monitoring tables:

```bash
python scripts/build_zhang_2022_dataset.py --source /path/to/Data.xlsx
```

No pseudo-replicates are generated. Any model fitted to these summary curves must
identify its uncertainty and validation limits explicitly.

## García Prats et al. (2024)

The following files transcribe exact design and material tables from:

> García Prats, M., González, D. & Sánchez, A. *Characterization of biochars of
> different origin and application to the anaerobic digestion of source-selected
> organic fraction of municipal solid waste under batch conditions and at different
> dosages*. Frontiers in Chemical Engineering 6 (2024).
> https://doi.org/10.3389/fceng.2024.1384495

- `experimental/garcia_prats_2024_biochar_characteristics.csv` — manufacturer,
  feedstock, pyrolysis, bulk-density, TOC, pH, EC, BET/pore and CHNS descriptors for
  BC1–BC3. The missing BC2 EC remains missing; sulfur is represented as a censored
  upper bound rather than as a measured value.
- `experimental/garcia_prats_2024_material_context.csv` — density, TS, VS and pH for
  the two OFMSW collections and inoculum, preserving reported standard deviations.
- `experimental/garcia_prats_2024_treatment_design.csv` — 12 first-assay conditions,
  triplicates, three TS-based dose levels, measured biochar mass, 150 mL working
  volume, 37 °C, 22-day duration and explicit second-feeding selection.

The article and tables are CC BY 4.0. `nominal_dose_g_l` is a transparent unit
conversion (`mass_mg / working_volume_ml`), not a replacement for the reported
percentage-on-TS dose. Run the boundary and design checks with:

```bash
python scripts/summarize_garcia_prats_2024_design.py
```

No methane outcomes are included. Exact reactor-level values were not obtained, and
relative-effect percentages differ between the article's abstract and results prose.
The repository therefore preserves only unambiguous tables and does not digitize plots.

## García Prats 2025: pending, not public data

`pending/garcia_prats_2025/` is a metadata-only intake gate for an author-shared
conference abstract associated with a full paper under revision. Raw reactor data
have not been received and redistribution permission was not granted. The directory
contains no source document, table values or numeric derivatives. Its README defines
the required reactor-level schema, same-batch control rule and validation checks.

If a source file is later supplied, it must remain under
`private/garcia_prats_2025/` until explicit redistribution permission is documented.
That path is excluded from version control.
