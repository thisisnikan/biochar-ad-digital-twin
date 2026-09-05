"""Within-study treatment effects from exact public outcomes.

Effects are normalized to the control from the same study. The returned rows
remain stratified by study and response; missing uncertainty in a published
parameter table prevents pooled inference across studies.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .baselines import BASELINES, fit_baseline
from .baselines import include_mask as _include_mask

RESPONSES = ("potential_ml_g_vs", "max_rate_ml_g_vs_day")


def _reactor_kinetic_estimates(frame: pd.DataFrame) -> pd.DataFrame:
    required = {
        "study_id",
        "treatment",
        "replicate",
        "time_days",
        "methane_ml_g_vs",
        "included_in_benchmark",
        "carbon_material",
        "process_temperature_c",
        "dose_g_l",
        "temperature_c",
        "source_doi",
    }
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing reactor-effect columns: {', '.join(sorted(missing))}")

    rows = []
    valid = frame.loc[_include_mask(frame)]
    for (treatment, replicate), reactor in valid.groupby(
        ["treatment", "replicate"], sort=True
    ):
        parameters, _ = fit_baseline(reactor, BASELINES["modified_gompertz"])
        first = reactor.iloc[0]
        rows.append(
            {
                "study_id": first["study_id"],
                "source_doi": first["source_doi"],
                "treatment": treatment,
                "replicate": replicate,
                "material": first["carbon_material"],
                "material_process_temperature_c": first["process_temperature_c"],
                "dose_g_l": first["dose_g_l"],
                "temperature_c": first["temperature_c"],
                "potential_ml_g_vs": parameters[0],
                "max_rate_ml_g_vs_day": parameters[1],
            }
        )
    return pd.DataFrame(rows)


def reactor_within_study_effects(frame: pd.DataFrame) -> pd.DataFrame:
    """Estimate biochar effects from independently fitted reactor trajectories."""
    estimates = _reactor_kinetic_estimates(frame)
    control = estimates.loc[estimates["treatment"] == "food_waste"]
    if len(control) < 2:
        raise ValueError("Kozlowski reactor data need at least two food_waste control reactors")

    rows = []
    treatments = estimates.loc[estimates["treatment"] != "food_waste"]
    for treatment, group in treatments.groupby("treatment", sort=True):
        if len(group) < 2:
            raise ValueError(f"Treatment {treatment} needs at least two reactors")
        first = group.iloc[0]
        for response in RESPONSES:
            treatment_values = group[response].to_numpy(float)
            control_values = control[response].to_numpy(float)
            treatment_mean = float(treatment_values.mean())
            control_mean = float(control_values.mean())
            if treatment_mean <= 0 or control_mean <= 0:
                raise ValueError(
                    f"Treatment {treatment} response {response} has a non-positive mean; "
                    "cannot compute a log response ratio"
                )
            log_ratio = float(np.log(treatment_mean / control_mean))
            rows.append(
                {
                    "study_id": first["study_id"],
                    "source_doi": first["source_doi"],
                    "treatment": treatment,
                    "control": "food_waste",
                    "material": first["material"],
                    "material_process_temperature_c": first[
                        "material_process_temperature_c"
                    ],
                    "dose_g_l": first["dose_g_l"],
                    "temperature_c": first["temperature_c"],
                    "response": response,
                    "treatment_estimate": treatment_mean,
                    "control_estimate": control_mean,
                    "treatment_sd": float(treatment_values.std(ddof=1)),
                    "control_sd": float(control_values.std(ddof=1)),
                    "log_response_ratio": log_ratio,
                    "percent_change": float(100 * np.expm1(log_ratio)),
                    "n_treatment_reactors": len(treatment_values),
                    "n_control_reactors": len(control_values),
                    "estimate_level": "reactor_level_gompertz_fit_mean",
                    "replicate_level_available": True,
                    "supports_cross_study_pooling": False,
                }
            )
    return pd.DataFrame(rows)


def parameter_table_within_study_effects(frame: pd.DataFrame) -> pd.DataFrame:
    """Normalize published dose-condition parameters to the zero-dose control."""
    required = {
        "dose_g_l",
        "temperature_c",
        "biochar_feedstock",
        "biochar_pyrolysis_c",
        "source_doi",
        *RESPONSES,
    }
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing parameter-effect columns: {', '.join(sorted(missing))}")
    control_rows = frame.loc[frame["dose_g_l"] == 0]
    if len(control_rows) != 1:
        raise ValueError("Published parameter table needs exactly one zero-dose control")
    control = control_rows.iloc[0]

    rows = []
    for _, treatment in frame.loc[frame["dose_g_l"] > 0].sort_values("dose_g_l").iterrows():
        for response in RESPONSES:
            treatment_estimate = float(treatment[response])
            control_estimate = float(control[response])
            if treatment_estimate <= 0 or control_estimate <= 0:
                raise ValueError(
                    f"Dose {treatment['dose_g_l']:g} response {response} has a non-positive "
                    "estimate; cannot compute a log response ratio"
                )
            log_ratio = float(np.log(treatment_estimate / control_estimate))
            rows.append(
                {
                    "study_id": "valentin_bialowiec_2024_scientific_reports",
                    "source_doi": treatment["source_doi"],
                    "treatment": f"dose_{treatment['dose_g_l']:g}_g_l",
                    "control": "dose_0_g_l",
                    "material": treatment["biochar_feedstock"],
                    "material_process_temperature_c": treatment["biochar_pyrolysis_c"],
                    "dose_g_l": treatment["dose_g_l"],
                    "temperature_c": treatment["temperature_c"],
                    "response": response,
                    "treatment_estimate": treatment_estimate,
                    "control_estimate": control_estimate,
                    "treatment_sd": np.nan,
                    "control_sd": np.nan,
                    "log_response_ratio": log_ratio,
                    "percent_change": float(100 * np.expm1(log_ratio)),
                    "n_treatment_reactors": treatment.get("n_reactors", np.nan),
                    "n_control_reactors": control.get("n_reactors", np.nan),
                    "estimate_level": "published_condition_parameter",
                    "replicate_level_available": False,
                    "supports_cross_study_pooling": False,
                }
            )
    return pd.DataFrame(rows)


def build_within_study_effect_table(
    reactor_frame: pd.DataFrame, parameter_frame: pd.DataFrame
) -> pd.DataFrame:
    """Build one stratified effect table without pooling unlike evidence levels."""
    result = pd.concat(
        [
            reactor_within_study_effects(reactor_frame),
            parameter_table_within_study_effects(parameter_frame),
        ],
        ignore_index=True,
    )
    return result.sort_values(["study_id", "response", "dose_g_l", "treatment"]).reset_index(
        drop=True
    )
