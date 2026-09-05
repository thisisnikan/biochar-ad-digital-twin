import numpy as np
import pandas as pd
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
    assert set(comparison["model"]) == {
        "constant_gompertz", "global_dose_temperature", "log_linear_dose_temperature"
    }
    assert comparison["delta_aicc"].min() == 0
    assert len(validation) == 3 * frame["batch_id"].nunique()
    assert validation.groupby("held_out_batch")["model"].nunique().eq(3).all()
    assert validation.groupby("held_out_batch")["n_test"].nunique().eq(1).all()
    assert np.isfinite(validation["rmse_ml_g_vs"]).all()


def test_holdout_fits_never_see_test_batch(monkeypatch, tmp_path):
    from biochar_ad_twin import analysis
    from biochar_ad_twin.model import KineticParameters

    frame = generate_demo_dataset(tmp_path / "demo.csv")
    calls = []

    def spy(train, response):
        calls.append((set(train.batch_id), response))
        return KineticParameters(), {"n_parameters": 3}

    monkeypatch.setattr(analysis, "fit_global", spy)
    output = leave_one_batch_out(frame)
    for row, (seen, _) in zip(output.itertuples(), calls, strict=True):
        assert row.held_out_batch not in seen
        assert seen == set(frame.batch_id) - {row.held_out_batch}


def test_nested_models_and_single_temperature(tmp_path):
    from biochar_ad_twin.fit import fit_global

    frame = generate_demo_dataset(tmp_path / "demo.csv")
    frame = frame.loc[frame.temperature_c.eq(37)].reset_index(drop=True)
    parameters, metrics = fit_global(frame, response="log_linear")
    assert parameters.potential_quadratic == parameters.rate_quadratic == 0
    assert parameters.q10 == 1
    assert metrics["n_parameters"] == 5
    constant, metrics = fit_global(frame, response="constant")
    assert constant.potential_linear == constant.rate_linear == 0
    assert metrics["n_parameters"] == 3


def test_holdout_rejects_unidentifiable_temperature(tmp_path):
    frame = generate_demo_dataset(tmp_path / "demo.csv")
    subset = frame.loc[frame.batch_id.isin(["T37_D0", "T37_D2", "T55_D0"])]
    with pytest.raises(ValueError, match="temperature extrapolation"):
        leave_one_batch_out(subset)


def test_holdout_summary_weights_batches_equally():
    from biochar_ad_twin.analysis import summarize_holdouts

    frame = pd.DataFrame({
        "model": ["a", "a", "b", "b"], "held_out_batch": [1, 2, 1, 2],
        "rmse_ml_g_vs": [1, 9, 4, 4], "mae_ml_g_vs": [1, 9, 4, 4],
        "n_test": [100, 1, 100, 1],
    })
    summary = summarize_holdouts(frame)
    assert summary.model.tolist() == ["b", "a"]
    assert summary.mean_held_out_rmse_ml_g_vs.tolist() == [4, 5]
