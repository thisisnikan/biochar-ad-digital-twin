"""Load and validate literature-derived evidence without treating it as raw data."""

from pathlib import Path

import pandas as pd


ENDPOINT_COLUMNS = {
    "source_id",
    "condition_id",
    "data_kind",
    "methane_yield",
    "methane_yield_unit",
    "doi",
    "source_url",
}
KINETIC_COLUMNS = {
    "source_id",
    "condition_id",
    "model",
    "data_kind",
    "doi",
    "source_url",
}
EFFECT_COLUMNS = {
    "source_id",
    "effect_id",
    "data_kind",
    "effect_min_pct",
    "effect_max_pct",
    "doi",
    "source_url",
}


def _load_validated(path: Path, required: set[str], allowed_kinds: set[str]) -> pd.DataFrame:
    frame = pd.read_csv(path)
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing literature columns in {path}: {sorted(missing)}")
    unexpected = set(frame["data_kind"].dropna()).difference(allowed_kinds)
    if unexpected:
        raise ValueError(f"Unexpected data_kind values in {path}: {sorted(unexpected)}")
    if frame["source_url"].isna().any() or frame["doi"].isna().any():
        raise ValueError(f"Every literature record must include DOI and source URL: {path}")
    return frame


def load_literature(directory: str | Path) -> dict[str, pd.DataFrame]:
    """Load the three evidence tables and enforce their provenance schema."""

    root = Path(directory)
    endpoints = _load_validated(
        root / "published_endpoints.csv", ENDPOINT_COLUMNS, {"published_endpoint"}
    )
    kinetics = _load_validated(
        root / "published_kinetic_parameters.csv",
        KINETIC_COLUMNS,
        {"published_fitted_parameters"},
    )
    effects = _load_validated(
        root / "published_effects.csv",
        EFFECT_COLUMNS,
        {"published_aggregate_effect", "published_condition_effect"},
    )
    if endpoints.duplicated(["source_id", "condition_id"]).any():
        raise ValueError("Duplicate source/condition rows in published endpoints")
    if kinetics.duplicated(["source_id", "condition_id", "model"]).any():
        raise ValueError("Duplicate source/condition/model rows in kinetic parameters")
    if effects.duplicated(["source_id", "effect_id"]).any():
        raise ValueError("Duplicate source/effect rows in published effects")
    if (effects["effect_min_pct"] > effects["effect_max_pct"]).any():
        raise ValueError("Literature effect minima cannot exceed maxima")
    return {"endpoints": endpoints, "kinetics": kinetics, "effects": effects}
