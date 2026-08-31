# Cross-study identifiability audit

This stage asks a narrower question before adding a hierarchical model or new ML:
does the evidence currently in the repository contain enough crossed experimental
overlap to distinguish laboratory effects from inoculum effects?

## Pre-specified decision rule

For each factor pair, studies are represented as a deduplicated bipartite graph.
We call the factors structurally crossed only when all three conditions hold:

1. at least one level of the first factor occurs with multiple levels of the second;
2. at least one level of the second factor occurs with multiple levels of the first;
3. the graph contains a cycle, with cycle rank `edges - vertices + components > 0`.

This is deliberately stricter than checking sample size or graph connectivity. An
additive model on a connected tree can estimate factor contrasts, but the absence of
a redundant cross-factor contrast makes that separation depend entirely on the
additivity assumption. The audit asks whether the literature design itself provides
crossed evidence; it is not a parameter-identifiability proof for a particular
nonlinear model.

## Current result

The three included studies represent two reported laboratory groups and three
study-specific inoculum collections. The Wroclaw group contributes two inoculum
sources, but no inoculum batch is documented as used by more than one laboratory.
The lab-inoculum graph is therefore nested/acyclic (cycle rank 0), not crossed.
Inoculum is also fully aliased with the current substrate and biochar-family choices.

Consequently, the current repository cannot empirically separate an unrestricted
laboratory effect from an unrestricted inoculum effect. This does **not** reject an
average biochar effect, invalidate the existing kinetic benchmarks, or cancel the
Digital Twin roadmap. It limits the cross-study causal/mechanistic claims that can
be supported by these three datasets.

## Minimum useful next evidence

A targeted ring trial should reuse the same characterized inoculum across at least
two laboratories, while each participating laboratory also tests at least two
inocula under a harmonized substrate, biochar, dose, temperature, reactor, blank
correction, and reporting protocol. A complete 2-by-2 lab-inoculum crossing creates
one graph cycle; biological reactor replication is additionally required for
uncertainty, but replicate bottles do not replace cross-laboratory crossing.

Run the deterministic audit with:

```bash
biochar-ad audit-identifiability
```

The source-linked metadata are in `study_metadata.csv`; generated reference outputs
are in `results/identifiability/`. Unknown shared identity is never inferred from a
similar plant description: inoculum IDs denote separately reported collections.

## Metadata sources

- Kozlowski et al. (2025), Scientific Reports,
  <https://doi.org/10.1038/s41598-025-02564-0>: article methods and public publisher
  dataset; agricultural-biogas-plant digestate from Swidnica, Poland.
- Valentin and Bialowiec (2024), Scientific Reports,
  <https://doi.org/10.1038/s41598-024-59313-y>: article methods and published kinetic
  table; digestate from a 1 MW agricultural biogas plant treating food and
  agricultural residues.
- Zhang et al. (2022), Biochar,
  <https://doi.org/10.1007/s42773-022-00187-6>: article methods; UASB inoculum treating
  cassava stillage and food waste from a Shanghai treatment plant.

The manifest records evidence availability separately from experimental replication.
For example, a triplicate experiment reported only as treatment-level kinetic values
does not become reactor-level data in this repository.
