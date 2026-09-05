import numpy as np
import pandas as pd
import pytest

from biochar_ad_twin.effects import (
    build_within_study_effect_table,
    parameter_table_within_study_effects,
    reactor_within_study_effects,
)

REACTORS = "data/experimental/kozlowski_2025_bmp.csv"
PARAMETERS = "data/experimental/valentin_bialowiec_2024_parameters.csv"


def test_reactor_effects_fit_each_replicate_against_same_study_control() -> None:
    effects = reactor_within_study_effects(pd.read_csv(REACTORS))
    assert len(effects) == 6
    assert set(effects["response"]) == {"potential_ml_g_vs", "max_rate_ml_g_vs_day"}
    assert effects["n_control_reactors"].eq(3).all()
    assert set(effects["n_treatment_reactors"]) == {2, 3}
    assert effects["replicate_level_available"].all()
    assert effects[["treatment_sd", "control_sd"]].notna().all().all()

    potential = effects.query("response == 'potential_ml_g_vs'")
    rate = effects.query("response == 'max_rate_ml_g_vs_day'")
    assert (potential["percent_change"] > 0).all()
    assert (rate["percent_change"] < 0).all()
    assert np.isclose(potential["percent_change"].max(), 11.85162, atol=1e-4)
    assert np.isclose(rate["percent_change"].min(), -7.41140, atol=1e-4)


def test_reactor_effect_confidence_intervals_bracket_the_point_estimate() -> None:
    effects = reactor_within_study_effects(pd.read_csv(REACTORS))

    assert (effects["percent_change_ci95_low"] <= effects["percent_change"]).all()
    assert (effects["percent_change"] <= effects["percent_change_ci95_high"]).all()
    assert effects["log_response_ratio_se"].gt(0).all()

    # n=2 treatments must be flagged; the n=3 hydrochar treatment must not be.
    by_treatment = effects.groupby("treatment")["low_replication"]
    assert by_treatment.get_group("food_waste_pyrolysis_600c").all()
    assert by_treatment.get_group("food_waste_torrefaction_240c").all()
    assert not by_treatment.get_group("food_waste_hydrochar_240c").any()


def test_reactor_effects_reject_an_unreplicated_treatment() -> None:
    frame = pd.read_csv(REACTORS)
    unreplicated = frame.loc[
        ~(
            (frame["treatment"] == "food_waste_hydrochar_240c")
            & (frame["replicate"].isin([2, 3]))
        )
    ]

    with pytest.raises(ValueError, match="at least two reactors"):
        reactor_within_study_effects(unreplicated)


def test_parameter_effects_reject_a_non_positive_estimate() -> None:
    frame = pd.read_csv(PARAMETERS)
    frame.loc[frame["dose_g_l"] == 0, "potential_ml_g_vs"] = 0.0

    with pytest.raises(ValueError, match="non-positive estimate"):
        parameter_table_within_study_effects(frame)


def test_published_parameter_effects_preserve_missing_uncertainty() -> None:
    effects = parameter_table_within_study_effects(pd.read_csv(PARAMETERS))
    assert len(effects) == 8
    assert effects["dose_g_l"].nunique() == 4
    assert not effects["replicate_level_available"].any()
    assert effects[["treatment_sd", "control_sd"]].isna().all().all()
    assert effects[["percent_change_ci95_low", "percent_change_ci95_high"]].isna().all().all()
    assert effects["low_replication"].all()
    assert (effects["percent_change"] > 0).all()

    rate_at_eight = effects.query(
        "response == 'max_rate_ml_g_vs_day' and dose_g_l == 8"
    ).iloc[0]
    assert np.isclose(rate_at_eight["percent_change"], 100 * (90.97 / 26.32 - 1))


def test_combined_table_is_stratified_and_never_claims_pooling() -> None:
    effects = build_within_study_effect_table(
        pd.read_csv(REACTORS), pd.read_csv(PARAMETERS)
    )
    assert len(effects) == 14
    assert effects["study_id"].nunique() == 2
    assert not effects["supports_cross_study_pooling"].any()
