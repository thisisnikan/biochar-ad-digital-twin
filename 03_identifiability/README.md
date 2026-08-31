# Cross-study identifiability audit

This stage asks a narrower question before adding a hierarchical model or new ML:
does the evidence currently in the repository contain enough overlap to distinguish
laboratory effects from inoculum effects, and if not, exactly what kind of overlap
is missing? It is a study-design diagnostic, computed from a source-linked metadata
manifest — it does not fit a dose-response model or estimate a biochar effect.

## Two different questions, kept separate on purpose

Reviewers of an earlier draft of this audit correctly pushed back on treating "the
graph has a cycle" as the one universal identifiability criterion. It is not. This
audit therefore reports two independent diagnostics per factor pair, because they
answer different questions and a design can pass one without the other:

1. **Is the additive main-effects model estimable at all, under the assumption that
   the two factors act additively (no interaction)?** This depends only on whether
   the deduplicated bipartite graph of the two factors is *connected*
   (`connected_components == 1`) — not on whether it has a cycle. We check this
   directly, by building the real one-hot additive design matrix (intercept + main
   effects) and computing its numeric rank with `numpy.linalg.matrix_rank`, rather
   than only trusting a graph-theory formula. A connected but acyclic (tree-shaped,
   "nested") design *is* fully rank — every additive contrast is estimable — it just
   depends entirely on the additivity assumption being correct, since the data give
   no way to check it. We call this **assumption-dependent estimability**.
2. **Is there crossed evidence to test that additivity assumption itself?** This
   needs a cycle in the graph (`cycle_rank = edges - vertices + components > 0`),
   i.e. a redundant cross-factor contrast: some level of each factor observed with
   more than one level of the other. Only a genuinely **crossed** design gives the
   data a way to flag an interaction or a lab-specific inoculum effect on its own,
   rather than assuming additivity by construction.

So: a cycle is sufficient but **not necessary** for additive estimability. A
connected acyclic graph can still support additive contrasts under that explicit
modelling assumption — this repository does not claim otherwise. What a connected
acyclic graph *cannot* do is validate the assumption it depends on; that requires
crossed evidence.

A **disconnected** design (more than one connected component) is different again,
and stronger than "assumption-dependent": it is **structurally confounded**. Some
main-effect contrasts cannot be estimated under *any* additive assumption, because
the levels involved never co-occur, directly or through a chain of shared levels —
no amount of modelling assumption recovers information that was never collected. A
design can also be a genuine mix — nested within one connected component while
disconnected from another — and is reported as its own category
(`partially_nested_partially_disconnected`) rather than forced into "nested" or
"disconnected".

| `evidence_category`                        | Connected? | Has a cycle? | Additive contrasts estimable? |
| ------------------------------------------- | :--------: | :-----------: | :----------------------------: |
| `crossed_evidence`                          | yes        | yes            | yes, and the additivity assumption is itself testable |
| `nested_single_component`                   | yes        | no             | yes, but only under the additivity assumption (assumption-dependent) |
| `partially_nested_partially_disconnected`   | no         | no             | no — some contrasts are structurally confounded |
| `disconnected_no_overlap`                   | no         | no             | no — every level pair is structurally confounded |

Practical identifiability and uncertainty (whether an estimable contrast is
*precisely* estimable given sample size and noise) is a separate question again,
downstream of this structural audit; a design can be structurally estimable and
still practically unidentifiable with too few studies per cell. This audit does not
attempt to quantify that — see "What this audit does not do" below.

## Current result

The three included studies represent two reported laboratory groups and three
study-specific inoculum collections. The Wroclaw group contributes two inoculum
sources (nested within that lab), but no inoculum batch is documented as used by
more than one laboratory, and the Fudan/Zhang study is never connected to the
Wroclaw component through any shared level. The lab-inoculum graph therefore has
**two connected components** — one nested (Wroclaw: 1 lab × 2 inocula), one a single
isolated edge (Fudan/Zhang) — and is classified
`partially_nested_partially_disconnected`, with one degree of additive rank
deficiency (`rank_deficiency = connected_components - 1 = 1`). Inoculum is also
completely disjoint from the current substrate and biochar-family choices
(`disconnected_no_overlap`, `rank_deficiency = 2`).

Consequently, with only the current manifest, an unrestricted laboratory effect and
an unrestricted inoculum effect are **not simultaneously estimable even under the
additivity assumption** — this is stronger than saying the design merely lacks
crossed evidence to *test* additivity; the design does not yet contain enough
overlap to *estimate* both effects at all, without an extra constraint (for example,
assuming zero laboratory effect). This does **not** reject an average biochar
effect, invalidate the existing kinetic benchmarks, or cancel the Digital Twin
roadmap. It limits the cross-study causal/mechanistic claims — specifically,
lab-vs-inoculum attribution — that these three datasets can support.

## What this audit does not do

- It does not estimate the sign, magnitude, or significance of a biochar effect.
- It does not evaluate the dose-response functional form, kinetic curve family, or
  predictive performance — those are separate evidence layers documented in
  [`../docs/PROJECT_STATUS.md`](../docs/PROJECT_STATUS.md) and
  [`../results/README.md`](../results/README.md).
- It does not quantify practical identifiability (how *precisely* an estimable
  contrast could be recovered given real noise and sample size) — only whether a
  contrast is estimable in principle from the reported study design.
- It does not infer that similarly described inoculum sources are the same
  physical batch, and it does not treat treatment means or reported standard
  deviations as reactor-level observations.

## Minimum useful next evidence

A targeted ring trial should reuse the same characterized inoculum across at least
two laboratories, while each participating laboratory also tests at least two
inocula under a harmonized substrate, biochar, dose, temperature, reactor, blank
correction, and reporting protocol. A complete 2-by-2 lab-inoculum crossing creates
one graph cycle (`crossed_evidence`); biological reactor replication is additionally
required for uncertainty, but replicate bottles do not replace cross-laboratory
crossing — replication and crossing answer different questions (uncertainty vs.
structural estimability).

Run the deterministic audit with:

```bash
biochar-ad audit-identifiability
```

The source-linked metadata are in `study_metadata.csv`; generated reference outputs
(CSV and JSON) are in `results/identifiability/`. Unknown shared identity is never
inferred from a similar plant description: inoculum IDs denote separately reported
collections.

## Metadata sources

- Kozłowski et al. (2025), Scientific Reports,
  <https://doi.org/10.1038/s41598-025-02564-0>: article methods and public publisher
  dataset; agricultural-biogas-plant digestate from Świdnica, Poland; reactor-level
  triplicate trajectories are the basis of `data/experimental/kozlowski_2025_bmp.csv`.
- Valentin & Białowiec (2024), Scientific Reports,
  <https://doi.org/10.1038/s41598-024-59313-y>: article methods and published kinetic
  table; digestate from a 1 MW agricultural biogas plant treating food and
  agricultural residues; only table-level triplicate summaries were obtained, not
  the raw reactor time series (available from the authors on request).
- Zhang et al. (2022), Biochar,
  <https://doi.org/10.1007/s42773-022-00187-6>: article methods; UASB inoculum
  treating cassava stillage, tested on food waste from a Shanghai treatment plant;
  the original triplicate reactor files are no longer available, so only
  author-shared treatment means and standard deviations exist.

`study_metadata.csv` records this evidence availability explicitly, as
`replicate_design_as_reported` and `raw_replicate_level_data_available`, separately
from experimental replication itself. A triplicate experiment reported only as
treatment-level kinetic values does not become reactor-level data in this
repository, and a lost original file is recorded as lost, not silently omitted.
