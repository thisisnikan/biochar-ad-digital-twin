import pandas as pd
import pytest

from biochar_ad_twin.data import generate_demo_dataset, validate_dataset
from biochar_ad_twin.fit import fit_global


def test_demo_global_fit(tmp_path) -> None:
    frame = generate_demo_dataset(tmp_path / "demo.csv")
    _, metrics = fit_global(frame)
    assert metrics["r_squared"] > 0.98
    assert metrics["rmse_ml_g_vs"] < 10


def test_missing_columns_are_reported() -> None:
    with pytest.raises(ValueError, match="Missing columns"):
        validate_dataset(pd.DataFrame({"time_days": [0, 1]}))

