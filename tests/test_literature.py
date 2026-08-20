from pathlib import Path

import numpy as np

from biochar_ad_twin.benchmarks import first_order, modified_gompertz
from biochar_ad_twin.literature import load_literature


def test_literature_tables_have_explicit_provenance_and_data_classes() -> None:
    root = Path(__file__).parents[1] / "data" / "literature"
    evidence = load_literature(root)

    assert len(evidence["endpoints"]) == 9
    assert len(evidence["kinetics"]) == 8
    assert len(evidence["effects"]) == 3
    assert set(evidence["endpoints"]["data_kind"]) == {"published_endpoint"}
    assert evidence["endpoints"]["source_url"].str.startswith("https://").all()
    assert evidence["kinetics"]["license"].eq("CC BY 4.0").all()


def test_contacted_researcher_is_represented_without_claiming_raw_data() -> None:
    root = Path(__file__).parents[1] / "data" / "literature"
    endpoints = load_literature(root)["endpoints"]
    contacted = endpoints[endpoints["source_id"] == "senol_2026"]

    assert len(contacted) == 3
    assert contacted["contact_relevance"].str.contains("previously contacted").all()
    assert not contacted["data_kind"].str.contains("raw").any()


def test_published_parameters_reproduce_near_terminal_curves() -> None:
    """Regression-check our equations against the paper's 36-day parameters."""

    root = Path(__file__).parents[1] / "data" / "literature"
    kinetics = load_literature(root)["kinetics"]
    for _, condition in kinetics.groupby("condition_id"):
        first = condition[condition["model"] == "first_order"].iloc[0]
        gompertz = condition[condition["model"] == "modified_gompertz"].iloc[0]
        potential = float(first["parameter_potential"])
        first_at_36 = first_order(
            np.array([36.0]), potential, float(first["hydrolysis_k_day"])
        )[0]
        gompertz_at_36 = modified_gompertz(
            np.array([36.0]),
            potential,
            float(gompertz["max_rate"]),
            float(gompertz["lag_days"]),
        )[0]

        assert first_at_36 / potential > 0.97
        assert gompertz_at_36 / potential > 0.99
