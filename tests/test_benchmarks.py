import numpy as np

from biochar_ad_twin.benchmarks import MODEL_SPECS, compare_models, modified_gompertz
from biochar_ad_twin.data import generate_demo_dataset


def test_all_benchmark_curves_are_bounded_and_monotonic() -> None:
    time = np.linspace(0, 40, 100)
    values = {
        "first_order": (300.0, 0.1),
        "modified_gompertz": (300.0, 18.0, 2.0),
        "modified_logistic": (300.0, 18.0, 2.0),
        "cone": (300.0, 0.1, 2.0),
    }
    for spec in MODEL_SPECS:
        curve = spec.curve(time, *values[spec.name])
        assert np.all(np.diff(curve) >= 0)
        assert curve.min() >= 0
        assert curve.max() <= 300


def test_gompertz_is_preferred_for_gompertz_data(tmp_path) -> None:
    time = np.linspace(0, 30, 31)
    observed = modified_gompertz(time, 300.0, 18.0, 2.0)
    frame = generate_demo_dataset(tmp_path / "unused.csv").iloc[:31].copy()
    frame["time_days"] = time
    frame["methane_ml_g_vs"] = observed
    comparison = compare_models(frame)
    winner = comparison.loc[comparison["aicc_rank"] == 1, "model"].iloc[0]
    assert winner == "modified_gompertz"
