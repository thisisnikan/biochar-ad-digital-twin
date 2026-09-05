import numpy as np
import pytest

from biochar_ad_twin.analysis import compare_models, information_criteria, leave_one_batch_out
from biochar_ad_twin.data import generate_demo_dataset


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
