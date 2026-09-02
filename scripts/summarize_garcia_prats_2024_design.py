"""Validate and summarize the open García Prats et al. (2024) design tables.

The public article provides material characteristics and experimental-design data,
but the committed tables intentionally contain no methane endpoints or reconstructed
time series. This script checks that boundary and writes a compact design-coverage
summary; it does not fit a response model.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

DOI = "10.3389/fceng.2024.1384495"
LICENSE = "CC BY 4.0"
OUTCOME_TOKENS = ("methane", "biogas", "bmp", "yield", "potential", "rate", "lag")


def _require_columns(frame: pd.DataFrame, required: set[str], label: str) -> None:
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"{label} is missing columns: {', '.join(sorted(missing))}")


def _contains_outcome_token(column: str) -> bool:
    parts = column.lower().split("_")
    return bool(set(parts).intersection(OUTCOME_TOKENS))


def validate_public_tables(
    characteristics: pd.DataFrame,
    context: pd.DataFrame,
    design: pd.DataFrame,
) -> None:
    """Raise ``ValueError`` when provenance, design or publication boundaries fail."""
    _require_columns(
        characteristics,
        {
            "biochar_id",
            "pyrolysis_temperature_c",
            "bet_surface_area_m2_g",
            "source_doi",
            "license",
        },
        "characteristics",
    )
    _require_columns(
        context,
        {"sample_id", "sample_role", "total_solids_g_l", "source_doi", "license"},
        "material context",
    )
    _require_columns(
        design,
        {
            "condition_id",
            "condition_type",
            "biochar_id",
            "biochar_mass_mg",
            "working_volume_ml",
            "nominal_dose_g_l",
            "n_replicates",
            "source_doi",
            "license",
        },
        "treatment design",
    )

    if len(characteristics) != 3 or set(characteristics["biochar_id"]) != {"BC1", "BC2", "BC3"}:
        raise ValueError("Expected exactly the three published biochars BC1, BC2 and BC3")
    if len(context) != 3 or set(context["sample_role"]) != {"substrate", "inoculum"}:
        raise ValueError("Expected two substrate collections and one inoculum record")
    if design["condition_id"].duplicated().any() or len(design) != 12:
        raise ValueError("Expected 12 unique first-assay conditions")

    amended = design.loc[design["condition_type"] == "biochar_amended"].copy()
    if len(amended) != 9:
        raise ValueError("Expected a 3 biochar x 3 dose amended design")
    if set(amended["biochar_id"]) != set(characteristics["biochar_id"]):
        raise ValueError("Treatment and characteristic biochar identifiers do not match")
    if set(amended["dose_pct_ts"]) != {1, 5, 10}:
        raise ValueError("Expected published 1%, 5% and 10% TS dose levels")

    calculated_dose = amended["biochar_mass_mg"] / amended["working_volume_ml"]
    if not np.allclose(calculated_dose, amended["nominal_dose_g_l"], atol=1e-6):
        raise ValueError("nominal_dose_g_l does not equal mass_mg / volume_ml")
    if not design["n_replicates"].eq(3).all():
        raise ValueError("Every published condition must remain triplicate")
    if set(design["working_volume_ml"]) != {150}:
        raise ValueError("Expected one published 150 mL working volume")
    if set(design["temperature_c"]) != {37} or set(design["assay_1_duration_days"]) != {22}:
        raise ValueError("Expected one 37 degC, 22-day first-assay context")
    selected = set(design.loc[design["selected_for_second_feeding"], "condition_id"])
    expected_selected = {
        "control",
        "bc2_1pct",
        "bc2_5pct",
        "bc2_10pct",
        "bc3_1pct",
        "bc3_5pct",
        "bc3_10pct",
    }
    if selected != expected_selected:
        raise ValueError("Second-feeding selection does not match the published design")

    for label, frame in (
        ("characteristics", characteristics),
        ("material context", context),
        ("treatment design", design),
    ):
        if not frame["source_doi"].eq(DOI).all() or not frame["license"].eq(LICENSE).all():
            raise ValueError(f"{label} has inconsistent DOI or license provenance")
        prohibited = [column for column in frame.columns if _contains_outcome_token(column)]
        if prohibited:
            raise ValueError(f"{label} unexpectedly contains outcome columns: {prohibited}")


def summarize_design(
    characteristics: pd.DataFrame,
    context: pd.DataFrame,
    design: pd.DataFrame,
) -> pd.DataFrame:
    """Return auditable coverage counts after validating all source tables."""
    validate_public_tables(characteristics, context, design)
    amended = design.loc[design["condition_type"] == "biochar_amended"]
    second_feed = design.loc[design["selected_for_second_feeding"]]
    rows = [
        ("characterized_biochars", len(characteristics), "count"),
        ("material_context_records", len(context), "count"),
        ("first_assay_conditions", len(design), "count"),
        ("biochar_amended_conditions", len(amended), "count"),
        ("expected_first_assay_bottles", int(design["n_replicates"].sum()), "count"),
        ("biochar_dose_levels", amended["dose_pct_ts"].nunique(), "count"),
        ("minimum_amended_nominal_dose", amended["nominal_dose_g_l"].min(), "g/L"),
        ("maximum_amended_nominal_dose", amended["nominal_dose_g_l"].max(), "g/L"),
        ("digestion_temperature", design["temperature_c"].iloc[0], "degC"),
        ("first_assay_duration", design["assay_1_duration_days"].iloc[0], "days"),
        ("second_feeding_selected_conditions", len(second_feed), "count"),
        ("public_outcome_measurements_committed", 0, "count"),
        ("raw_reactor_trajectories_received", 0, "boolean"),
    ]
    return pd.DataFrame(rows, columns=["metric", "value", "unit"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("data/experimental"))
    parser.add_argument("--output", type=Path, default=Path("results/garcia_prats_2024"))
    args = parser.parse_args()

    characteristics = pd.read_csv(args.data / "garcia_prats_2024_biochar_characteristics.csv")
    context = pd.read_csv(args.data / "garcia_prats_2024_material_context.csv")
    design = pd.read_csv(args.data / "garcia_prats_2024_treatment_design.csv")
    summary = summarize_design(characteristics, context, design)
    args.output.mkdir(parents=True, exist_ok=True)
    destination = args.output / "design_summary.csv"
    summary.to_csv(destination, index=False)
    print(f"Wrote {destination}")


if __name__ == "__main__":
    main()
