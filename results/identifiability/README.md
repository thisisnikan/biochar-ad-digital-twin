# Identifiability reference result

Generated from `03_identifiability/study_metadata.csv` with:

```bash
biochar-ad audit-identifiability --output results/identifiability
```

`factor_pair_audit.csv` is the decision table. The edge files make every graph input
inspectable. With the current three-study manifest, no audited pair has crossed
overlap; in particular, the lab-inoculum graph is nested/acyclic with cycle rank 0.

These results diagnose missing experimental overlap. They do not estimate the sign
or magnitude of a biochar effect and should not be interpreted as evidence against
the broader project hypothesis.
