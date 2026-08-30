# Project status

Last reviewed: 30 August 2026

## Readiness snapshot

| Area | Status | Evidence |
| --- | --- | --- |
| Package and CLI | Working | Installable package with `demo`, `fit`, and `benchmark-experimental` commands |
| Automated quality | Working | Ruff plus 15 tests on Python 3.10 and 3.12 in GitHub Actions |
| Synthetic workflow | Reproducible | Labelled synthetic input and deterministic reporting pipeline |
| Open experimental benchmark | Reproducible | Kozłowski et al. (2025) reactor-level trajectories and reference output |
| Zhang integration | Limited by source | Hash-verified private ingestion and summary analysis; original triplicates were lost |
| Global dose–temperature hypothesis | Not independently validated | Requires multi-dose, multi-temperature reactor trajectories |

## What can be claimed now

- The software executes an auditable end-to-end BMP modelling workflow.
- Modified Gompertz has the lowest mean reactor-held-out RMSE within each treatment of the
  included Kozłowski et al. (2025) experiment.
- Author-shared Zhang et al. (2022) summaries can be analysed without inventing
  pseudo-replicates or publishing the private workbook.

## What cannot be claimed now

- That biochar causally improves anaerobic digestion across studies.
- That the exploratory dose–temperature response generalises beyond the demonstration.
- That summary-curve residuals replace biological replicate uncertainty.
- That this research prototype is already an operational plant digital twin.

## Next validation gate

The next publication-level gate is an independent dataset containing:

1. reactor-level methane or biogas trajectories;
2. at least three biochar doses and more than one temperature;
3. biological or reactor replicates plus inoculum-only controls;
4. substrate, inoculum, S/I ratio, reactor and material metadata;
5. a preregistered held-out-study comparison against parsimonious baselines.

Until that gate is passed, the repository should be described as a **reproducible research
prototype for falsifiable kinetic modelling**, not as a validated predictive product.

## Maintenance checklist

- Keep `main` green on every merge.
- Regenerate committed reference results after model or data-processing changes.
- Record every public dataset's license, DOI, source hash and transformation decisions.
- Never commit author-shared files without explicit redistribution permission.
- Update this page whenever the scientific evidence boundary changes.
