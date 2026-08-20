# Literature-derived benchmark data

This directory contains literature-derived benchmark values used to test the Biochar–AD Digital Twin against published experimental studies.

The datasets here are deliberately separated by evidence type. Published fitted parameters, endpoint methane yields, relative effects, and raw time-series observations are **not** treated as interchangeable.

## Qiu et al. (2026), Imperial College London

**Paper:** Mengru Qiu, Maria E. Koulouri, Laure Sioné, Michael R. Templeton, *The impact of faecal sludge-derived biochar as an additive on anaerobic degradation of synthetic human excreta*, Environmental Science: Water Research & Technology (2026), 12, 1794–1809.

**DOI:** 10.1039/D6EW00095A

**License:** CC BY 3.0. Values in `qiu_2026_imperial_kinetic_parameters.csv` were transcribed from Table 3 of the open-access article with attribution.

### Experimental context

- Substrate: synthetic human excreta
- Biochar: faecal-sludge-derived biochar
- Maximum biochar production temperature: approximately 400 °C
- Biochar doses: 0, 3, 6, 9, 12 g/L
- Digestion temperature: 35 °C
- Reactor: 500 mL serum bottle, 400 mL working volume
- Inoculum-to-substrate ratio: 4:1 on a VS basis
- Duration: 18 days
- Three independent AD batches; each treatment was run in triplicate

### Data type

Published first-order and modified-Gompertz fitted kinetic parameters, not raw reactor time-series observations.

This study is particularly useful for separating kinetic acceleration from ultimate methane-yield enhancement and for testing batch-to-batch variability.

---

## Valentin & Białowiec (2024), Scientific Reports

**Paper:** Marvin T. Valentin and Andrzej Białowiec, *Impact of using glucose as a sole carbon source to analyze the effect of biochar on the kinetics of biomethane production*, Scientific Reports 14, 8656 (2024).

**DOI:** 10.1038/s41598-024-59313-y

**License:** CC BY 4.0.

**File:** `valentin_2024_glucose_gompertz.csv`

### Experimental context

- Substrate: glucose
- Temperature: 37 °C
- Biochar doses: 0, 2, 4, 6 and 8 g/L
- ISR: 2 on a VS basis
- Batch BMP system: AMPTS II
- 15 reactors total, triplicate treatments
- Overall experiment: 60 days; the published Table 3 describes the fourth phase, intended to isolate glucose as the carbon source

### Data type

Published cumulative BMP and modified-Gompertz parameters from Table 3. The article reports that the underlying methane measurements were collected every 15 minutes, but this repository currently stores only the values directly reported in the table.

This is a strong positive-response benchmark: cumulative BMP increased from 135.06 mL CH4/g VS without biochar to 390.33 mL CH4/g VS at 8 g/L, while the fitted lag phase shortened substantially.

---

## García-Prats et al. (2024), Frontiers in Chemical Engineering

**Paper:** *Characterization of biochars of different origin and application to the anaerobic digestion of source-selected organic fraction of municipal solid waste under batch conditions and at different dosages*.

**DOI:** 10.3389/fceng.2024.1384495

**File:** `ofmsw_biochar_batch_benchmark_2024.csv`

### Experimental context

- Substrate: source-selected organic fraction of municipal solid waste (OFMSW)
- Control BMP: 248 ± 18 mL CH4/g VS
- ISR: 2:1 inoculum:substrate on a VS basis
- Biochar doses: 1, 5 and 10% w/w relative to total solids
- Three different lignocellulosic biochars
- Batch stage: 22 days before a second substrate addition

### Data type

This file combines directly reported biochar characterization values (surface area, pore size, elemental composition and production metadata) with the significant relative methane effects reported in the article text. It does **not** digitize Figure 3 to invent unreported absolute endpoint values.

The dataset is scientifically valuable because the same nominal dose produced opposite effects depending on biochar identity: at 1%, BC1 and BC2 were inhibitory while BC3 was beneficial. This directly tests a central digital-twin hypothesis: dose alone is insufficient and biochar physicochemical descriptors matter.

---

## Municipal organic-waste biochar kinetics benchmark (2025)

**Paper:** *Converting Organic Municipal Solid Waste Into Volatile Fatty Acids and Biogas: Experimental Pilot and Batch Studies With Statistical Analysis*.

**File:** `municipal_waste_biochar_kinetics_2025.csv`

### Data type

Published Table 6 values for control, 0.12 g biochar/g VS and 0.24 g biochar/g VS treatments, including specific methane production, gas production, first-order rate constant, maximum methane-production rate, lag phase, RMSE values and maximum methane content.

This is useful as a counterexample to simplistic enhancement assumptions: both tested biochar treatments had lower reported specific methane production than the control, despite changes in hydrolysis rate and methane concentration.

---

## Rules for using literature data in this repository

1. Every numerical literature file must identify the paper and evidence source.
2. Table-transcribed values remain labelled as published/derived parameters.
3. Raw observations are stored separately from fitted or summary parameters.
4. Figure digitization, if ever required, must be explicitly labelled as digitized and include an uncertainty note.
5. Unit conversions must preserve the original value and document the transformation.
6. Literature datasets are intended for external validation and model comparison, not for claiming new experimental measurements.

## Modelling implications emerging from the benchmark

The current evidence already shows at least four regimes that a robust model should be able to represent:

- strong positive dose response;
- kinetic acceleration with relatively modest change in final methane potential;
- weak/null response;
- inhibition or reversal depending on biochar properties and process conditions.

This means a universal dose-only relationship is unlikely to generalize. The next modelling iteration should test study/batch effects and biochar descriptors before adding unnecessary complexity.
