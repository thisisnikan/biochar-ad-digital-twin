import json

import pandas as pd
import pytest

from biochar_ad_twin import cli
from biochar_ad_twin.data import generate_demo_dataset, validate_dataset
from biochar_ad_twin.fit import fit_global


def test_demo_global_fit(tmp_path) -> None:
    frame = generate_demo_dataset(tmp_path / "demo.csv")
    _, metrics = fit_global(frame)
    assert metrics["r_squared"] > 0.98
    assert metrics["rmse_ml_g_vs"] < 10


def test_fit_global_reports_parameter_identifiability(tmp_path) -> None:
    frame = generate_demo_dataset(tmp_path / "demo.csv")
    _, metrics = fit_global(frame)

    assert 0.0 <= metrics["max_parameter_correlation"] <= 1.0
    assert metrics["parameter_gram_condition_number"] > 1.0


def test_cli_fit_warns_when_parameters_are_confounded(tmp_path, monkeypatch, capsys) -> None:
    frame = generate_demo_dataset(tmp_path / "demo.csv")
    csv_path = tmp_path / "demo_copy.csv"
    frame.to_csv(csv_path, index=False)
    output_dir = tmp_path / "out"

    monkeypatch.setattr(
        "sys.argv", ["biochar-ad", "fit", str(csv_path), "--output", str(output_dir)]
    )
    cli.main()

    payload = json.loads(capsys.readouterr().out)
    # The demo dataset's own 8-parameter fit is confounded (see PROJECT_STATUS.md);
    # the CLI must surface that instead of only reporting RMSE/R-squared.
    assert payload["identifiability_warning"] is not None
    assert "confounded" in payload["identifiability_warning"]


def test_missing_columns_are_reported() -> None:
    with pytest.raises(ValueError, match="Missing columns"):
        validate_dataset(pd.DataFrame({"time_days": [0, 1]}))


def test_missing_batch_id_is_rejected() -> None:
    frame = pd.DataFrame(
        {
            "batch_id": ["a", None],
            "time_days": [0, 1],
            "dose_g_l": [0, 0],
            "temperature_c": [37, 37],
            "methane_ml_g_vs": [0, 10],
        }
    )
    with pytest.raises(ValueError, match="batch_id"):
        validate_dataset(frame)


def test_cli_fit_skips_leave_one_batch_out_below_three_batches(
    tmp_path, monkeypatch, capsys
) -> None:
    frame = generate_demo_dataset(tmp_path / "demo.csv")
    two_batch = frame.loc[frame["batch_id"].isin(frame["batch_id"].unique()[:2])]
    csv_path = tmp_path / "two_batch.csv"
    two_batch.to_csv(csv_path, index=False)
    output_dir = tmp_path / "out"

    monkeypatch.setattr(
        "sys.argv", ["biochar-ad", "fit", str(csv_path), "--output", str(output_dir)]
    )
    cli.main()

    assert not (output_dir / "leave_one_batch_out.csv").exists()
    payload = json.loads(capsys.readouterr().out)
    assert payload["mean_held_out_rmse_interior_ml_g_vs"] is None
    assert payload["mean_held_out_rmse_boundary_ml_g_vs"] is None


def test_cli_fit_bootstrap_is_opt_in(tmp_path, monkeypatch) -> None:
    frame = generate_demo_dataset(tmp_path / "demo.csv")
    csv_path = tmp_path / "demo_copy.csv"
    frame.to_csv(csv_path, index=False)
    output_dir = tmp_path / "out"

    monkeypatch.setattr(
        "sys.argv", ["biochar-ad", "fit", str(csv_path), "--output", str(output_dir)]
    )
    cli.main()
    assert not (output_dir / "bootstrap_summary.csv").exists()

    monkeypatch.setattr(
        "sys.argv",
        ["biochar-ad", "fit", str(csv_path), "--output", str(output_dir), "--bootstrap", "5"],
    )
    cli.main()
    assert (output_dir / "bootstrap_summary.csv").exists()


def test_cli_summarize_effects_reports_uncertainty_gaps(tmp_path, monkeypatch, capsys) -> None:
    output_dir = tmp_path / "effects_out"
    monkeypatch.setattr(
        "sys.argv", ["biochar-ad", "summarize-effects", "--output", str(output_dir)]
    )
    cli.main()

    payload = json.loads(capsys.readouterr().out)
    assert payload["low_replication_effects"] > 0
    assert payload["effects_without_uncertainty"] > 0

