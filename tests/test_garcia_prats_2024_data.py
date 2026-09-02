import importlib.util
from pathlib import Path

import pandas as pd
import pytest

SCRIPT = Path("scripts/summarize_garcia_prats_2024_design.py")
SPEC = importlib.util.spec_from_file_location("summarize_garcia_prats_2024_design", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


DATA = Path("data/experimental")


def _tables() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    return (
        pd.read_csv(DATA / "garcia_prats_2024_biochar_characteristics.csv"),
        pd.read_csv(DATA / "garcia_prats_2024_material_context.csv"),
        pd.read_csv(DATA / "garcia_prats_2024_treatment_design.csv"),
    )


def test_public_tables_preserve_provenance_and_design_boundary() -> None:
    characteristics, context, design = _tables()
    MODULE.validate_public_tables(characteristics, context, design)
    assert characteristics.loc[
        characteristics["biochar_id"] == "BC2", "manufacturer_ec_us_cm"
    ].isna().item()
    assert design["n_replicates"].sum() == 36
    assert not any("methane" in column.lower() for column in design.columns)


def test_nominal_dose_is_measured_mass_over_working_volume() -> None:
    _, _, design = _tables()
    amended = design.query("condition_type == 'biochar_amended'")
    expected = amended["biochar_mass_mg"] / amended["working_volume_ml"]
    assert amended["nominal_dose_g_l"].tolist() == pytest.approx(expected.tolist(), abs=1e-6)


def test_second_feeding_selection_is_explicit() -> None:
    _, _, design = _tables()
    selected = set(design.loc[design["selected_for_second_feeding"], "condition_id"])
    assert selected == {
        "control",
        "bc2_1pct",
        "bc2_5pct",
        "bc2_10pct",
        "bc3_1pct",
        "bc3_5pct",
        "bc3_10pct",
    }


def test_summary_reports_coverage_without_inventing_outcomes() -> None:
    summary = MODULE.summarize_design(*_tables()).set_index("metric")
    assert summary.loc["characterized_biochars", "value"] == 3
    assert summary.loc["biochar_amended_conditions", "value"] == 9
    assert summary.loc["expected_first_assay_bottles", "value"] == 36
    assert summary.loc["public_outcome_measurements_committed", "value"] == 0
