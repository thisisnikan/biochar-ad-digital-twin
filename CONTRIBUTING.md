# Contributing

Contributions are welcome when they improve reproducibility, data provenance, model
validation or scientific interpretation.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
ruff check .
pytest -q
```

## Contribution rules

1. Create a focused branch and keep each pull request limited to one scientific or software
   question.
2. Add tests for new behaviour and run the complete quality suite.
3. Document dataset DOI, license, original source, source hash and every transformation.
4. Distinguish reactor-level observations, treatment summaries and synthetic data explicitly.
5. Do not create pseudo-replicates, silently remove observations or overstate causal evidence.
6. Do not commit private or author-shared data without written redistribution permission.

For a new reactor-level dataset, start from `data/templates/reactor_observations.csv`,
run `biochar-ad validate-intake <csv>`, and use the data-contribution issue form before
writing an ingestion script. The pull request should include the validation report,
generated reference result and a cautious interpretation.
