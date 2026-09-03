from pathlib import Path

import pandas as pd

from biochar_ad_twin.intake import validate_reactor_observations

TEMPLATE = Path("data/templates/reactor_observations.csv")


def test_reactor_observation_template_passes() -> None:
    report = validate_reactor_observations(pd.read_csv(TEMPLATE))

    assert report.valid
    assert report.row_count == 12
    assert report.reactor_count == 6
    assert report.experiment_count == 1
    assert not report.issues


def test_duplicate_reactor_time_is_rejected() -> None:
    frame = pd.read_csv(TEMPLATE)
    frame = pd.concat([frame, frame.iloc[[0]]], ignore_index=True)

    report = validate_reactor_observations(frame)

    assert not report.valid
    assert "duplicate_observation_key" in {issue.code for issue in report.issues}


def test_changed_reactor_metadata_is_rejected() -> None:
    frame = pd.read_csv(TEMPLATE)
    frame.loc[frame["reactor_id"].eq("biochar_r1") & frame["time_days"].eq(1), "dose_value"] = 8

    report = validate_reactor_observations(frame)

    assert not report.valid
    assert "inconsistent_reactor_metadata" in {issue.code for issue in report.issues}


def test_missing_blank_is_reported_without_inventing_one() -> None:
    frame = pd.read_csv(TEMPLATE)
    frame = frame.loc[~frame["is_inoculum_blank"]]

    report = validate_reactor_observations(frame)

    assert report.valid
    assert "missing_inoculum_blank" in {issue.code for issue in report.issues}


def test_reactor_identifiers_are_scoped_to_their_experiment() -> None:
    frame = pd.read_csv(TEMPLATE)
    second = frame.copy()
    second["experiment_id"] = "run_02"
    second["temperature_c"] = 55

    report = validate_reactor_observations(pd.concat([frame, second], ignore_index=True))

    assert report.valid
    assert report.experiment_count == 2
    assert report.reactor_count == 12
