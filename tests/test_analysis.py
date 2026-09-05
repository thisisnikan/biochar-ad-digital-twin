import numpy as np
import pandas as pd
import pytest

from biochar_ad_twin.analysis import compare_models, information_criteria, leave_one_batch_out
from biochar_ad_twin.data import generate_demo_dataset
from biochar_ad_twin.model import BatchCondition, KineticParameters, cumulative_methane


def test_information_criteria_reward_better_fit():
    observed = np.arange(20, dtype=float)
    perfect = information_criteria(observed, observed, 2)
    poor = information_criteria(observed, observed + 3, 2)
    assert perfect["aicc"] < poor["aicc"]


def test_comparison_and_batch_validation(tmp_path):
    frame = generate_demo_dataset(tmp_path / "demo.csv")
    comparison = compare_models(frame)
    validation = leave_one_batch_out(frame)
    assert set(comparison["model"]) == {"constant_gompertz", "global_dose_temperature"}
    assert comparison["delta_aicc"].min() == 0
    assert len(validation) == frame["batch_id"].nunique()
    assert np.isfinite(validation["rmse_ml_g_vs"]).all()


def test_leave_one_batch_out_requires_three_batches(tmp_path):
    frame = generate_demo_dataset(tmp_path / "demo.csv")
    two_batch = frame.loc[frame["batch_id"].isin(frame["batch_id"].unique()[:2])]

    with pytest.raises(ValueError, match="three batch conditions"):
        leave_one_batch_out(two_batch)


def test_leave_one_batch_out_flags_only_true_boundary_conditions():
    truth = KineticParameters()
    time = [0.0, 5.0, 10.0, 20.0, 30.0]
    rows = []
    for temperature in (20.0, 37.0, 55.0):
        for dose in (0.0, 2.0, 5.0):
            condition = BatchCondition(dose, temperature)
            clean = cumulative_methane(time, condition, truth)
            rows.extend(
                {
                    "batch_id": f"T{temperature:.0f}_D{dose:g}",
                    "time_days": day,
                    "dose_g_l": dose,
                    "temperature_c": temperature,
                    "methane_ml_g_vs": value,
                }
                for day, value in zip(time, clean)
            )
    frame = pd.DataFrame(rows)

    validation = leave_one_batch_out(frame)

    interior_batch = "T37_D2"
    boundary_batch = "T20_D0"
    assert not validation.set_index("held_out_batch").loc[interior_batch, "is_boundary_condition"]
    assert validation.set_index("held_out_batch").loc[boundary_batch, "is_boundary_condition"]
    assert validation["is_boundary_condition"].any()
    assert not validation["is_boundary_condition"].all()
