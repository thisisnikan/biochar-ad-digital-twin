# Literature-derived benchmark data

This directory contains literature-derived benchmark values used to test the Biochar–AD Digital Twin against published experimental studies.

## Qiu et al. (2026), Imperial College London

**Paper:** Mengru Qiu, Maria E. Koulouri, Laure Sioné, Michael R. Templeton, *The impact of faecal sludge-derived biochar as an additive on anaerobic degradation of synthetic human excreta*, Environmental Science: Water Research & Technology (2026), 12, 1794–1809.

**DOI:** 10.1039/D6EW00095A

**License:** CC BY 3.0. Values in `qiu_2026_imperial_kinetic_parameters.csv` were transcribed from Table 3 of the open-access article with attribution.

### Experimental context

- Substrate: synthetic human excreta
- Biochar: faecal-sludge-derived biochar (FSB)
- FSB production: slow pyrolysis/carbonisation, maximum recorded temperature approximately 400 °C
- Biochar doses: 0, 3, 6, 9, 12 g/L
- Digestion temperature: 35 °C
- Reactor: 500 mL serum bottle, 400 mL working volume
- Inoculum-to-substrate ratio: 4:1 on a VS basis
- Duration: 18 days
- Three independent AD batches; each treatment was run in triplicate

### What this file contains

The CSV contains the **published fitted kinetic parameters**, not raw reactor time-series observations:

- first-order methane potential `Bmax`
- first-order hydrolysis constant `k`
- first-order R²
- modified-Gompertz methane potential `P`
- maximum methane-production rate `Rm`
- lag phase `lambda`
- modified-Gompertz R²

This distinction is important. These values are appropriate for parameter-level benchmarking and for testing dose/batch trends, but should not be represented as raw experimental observations.

### Scientific use in this repository

This dataset is useful because it contains three independent batches and shows strong batch-to-batch variation. It therefore provides a real test of whether a single deterministic dose-response relationship is adequate. In the paper, FSB generally accelerated early-stage kinetics and shortened lag phases while having only minor effects on final cumulative methane production. This makes the study particularly useful for separating **kinetic acceleration** from **ultimate methane-yield enhancement**.

### Next data target

The article states that supporting data, including batch methane and gas data, are provided in the supplementary information. If a machine-readable version of those raw/near-raw values is obtained, it should be stored separately and never silently substituted for this published-parameter benchmark.
