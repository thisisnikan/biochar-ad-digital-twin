import importlib.util
from pathlib import Path

SCRIPT = Path("scripts/build_zhang_2022_dataset.py")
SPEC = importlib.util.spec_from_file_location("build_zhang_2022_dataset", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_methane_summary_preserves_means_and_standard_deviations() -> None:
    sheet = [
        [None, "C", "Standard deviation", "B750-60", "Standard deviation"],
        [0, 0, 0, 0, 0],
        [1, 10.0, 0.5, 14.0, 0.9],
    ]
    rows = MODULE.transform_methane(sheet, "pyrolysis_temperature")
    assert len(rows) == 4
    biochar = rows[-1]
    assert biochar["treatment"] == "biochar_750c_60min"
    assert biochar["cumulative_methane_ml"] == 14.0
    assert biochar["reported_standard_deviation_ml"] == 0.9
    assert biochar["replicate_level_available"] is False
    assert biochar["inoculum_blank_corrected"] is True


def test_vfa_summary_propagates_day_and_never_invents_missing_values() -> None:
    sheet = [
        [None, "--", "Acetate", "Standard deviation", "Propionate", "Standard deviation"],
        ["6 day", "C", 100.0, 10.0, 80.0, 8.0],
        [None, "B750-60", 50.0, 5.0, "--", "--"],
    ]
    rows = MODULE.transform_vfa(sheet, "pyrolysis_temperature")
    assert len(rows) == 3
    assert {row["time_days"] for row in rows} == {6.0}
    assert {row["analyte"] for row in rows} == {"acetate", "propionate"}
    biochar = [row for row in rows if row["treatment"] == "biochar_750c_60min"]
    assert len(biochar) == 1
    assert biochar[0]["value"] == 50.0


def test_public_characteristics_are_exactly_source_attributed() -> None:
    import pandas as pd

    frame = pd.read_csv("data/experimental/zhang_2022_biochar_characteristics.csv")
    assert len(frame) == 5
    assert frame["source_doi"].eq("10.1007/s42773-022-00187-6").all()
    assert frame["data_origin"].eq("published_article_table_and_text").all()
    assert frame.loc[
        frame["treatment"] == "biochar_750c_60min", "raman_id_ig_ratio"
    ].item() == 0.77
