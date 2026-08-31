# Identifiability reference result

Generated deterministically from `03_identifiability/study_metadata.csv` with:

```bash
biochar-ad audit-identifiability --output results/identifiability
```

`factor_pair_audit.csv` (and the equivalent `factor_pair_audit.json`) is the
decision table. Each row reports two independent diagnostics, not one: whether the
factor pair is `crossed_overlap` (a redundant cross-factor contrast that can test
the additivity assumption) and whether it is
`estimable_under_additive_assumption` (whether the additive main effects are
estimable at all, which depends only on graph connectivity). `evidence_category`
summarises both into one of four labels — see
[`../../03_identifiability/README.md`](../../03_identifiability/README.md) for the
full definitions and the reasoning behind keeping the two diagnostics separate. The
edge CSVs make every graph input inspectable.

With the current three-study manifest, no audited pair has crossed evidence. The
lab-inoculum pair is `partially_nested_partially_disconnected` (one connected
nested component at Wroclaw, one disconnected edge at Fudan/Zhang), so even the
additive main effects for laboratory and inoculum are not jointly estimable yet.
The inoculum-substrate and inoculum-biochar pairs are `disconnected_no_overlap`.

These results diagnose missing experimental overlap in the study design. They do
not estimate the sign or magnitude of a biochar effect and should not be
interpreted as evidence against the broader project hypothesis.
