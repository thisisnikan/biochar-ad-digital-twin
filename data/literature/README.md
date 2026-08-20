# Literature-derived evidence

These files deliberately separate published endpoints, aggregate treatment
effects and fitted kinetic parameters from raw experimental time series.

## Evidence classes

- `published_endpoint`: a numerical endpoint printed in an article or its
  publisher-indexed abstract.
- `published_aggregate_effect`: a range that applies across several conditions;
  its bounds must not be assigned to individual treatments.
- `published_fitted_parameters`: model parameters reported by the authors.

None of these records is labelled as raw experimental data. They therefore must
not be passed to the time-series fitting command. The values are suitable for
external-range checks, model-regression tests and planning an independent
validation experiment.

The da Borso et al. article is distributed under CC BY 4.0. The Senol et al. and
Ngo et al. records contain only cited numerical facts transcribed from official
publisher/indexing pages; the repository does not redistribute article text,
figures or supplementary files.

## Important limitation

The 2026 Senol et al. study is the closest match to this repository and includes
a previously contacted researcher, Nazli Pelin Kocatürk Schumacher. Its public
abstract reports endpoints and aggregate effects, but the raw time-course
measurements were not available through the inspected official endpoints. A
full kinetic re-fit requires the authors' supplementary/raw table. Until then,
the repository uses those numbers only as endpoint constraints.
