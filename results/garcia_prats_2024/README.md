# García Prats et al. (2024): design coverage

`design_summary.csv` is generated from the three open design/provenance tables with:

```bash
python scripts/summarize_garcia_prats_2024_design.py
```

It confirms a three-biochar, three-dose amended matrix embedded in a 12-condition,
triplicate first assay at 37 °C. This is **design coverage**, not model validation.

No methane endpoint, fitted parameter or time series is committed. The article's main
text reports inconsistent relative-effect percentages between its abstract and results
section, while exact reactor-level observations were not obtained. The repository
therefore does not select one prose value, digitize plots, or fabricate trajectories.

The open descriptors are useful for schema development and future material-aware
modelling. Treatment effects can be estimated only after exact outcome data with batch,
control and replicate identities become available.
