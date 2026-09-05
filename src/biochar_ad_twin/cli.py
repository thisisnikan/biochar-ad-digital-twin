"""Command-line interface."""

import argparse
import json
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from .analysis import compare_models, leave_one_batch_out
from .baselines import compare_experimental_baselines
from .data import generate_demo_dataset
from .effects import build_within_study_effect_table
from .external_validation import compare_external_dose_responses
from .fit import bootstrap_parameters, fit_global
from .intake import validate_reactor_observations
from .report import save_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    demo = commands.add_parser("demo", help="Generate synthetic data and run the full workflow")
    demo.add_argument("--output", type=Path, default=Path("outputs"))
    demo.add_argument("--bootstrap", type=int, default=30)
    fit = commands.add_parser("fit", help="Fit a CSV dataset")
    fit.add_argument("csv", type=Path)
    fit.add_argument("--output", type=Path, default=Path("outputs"))
    benchmark = commands.add_parser(
        "benchmark-experimental",
        help="Compare transparent kinetic baselines on replicate-level experimental BMP data",
    )
    benchmark.add_argument(
        "csv",
        type=Path,
        nargs="?",
        default=Path("data/experimental/kozlowski_2025_bmp.csv"),
    )
    benchmark.add_argument("--output", type=Path, default=Path("outputs/experimental"))
    external = commands.add_parser(
        "benchmark-external-dose",
        help="Challenge dose-response forms with independent published kinetic parameters",
    )
    external.add_argument(
        "csv",
        type=Path,
        nargs="?",
        default=Path("data/experimental/valentin_bialowiec_2024_parameters.csv"),
    )
    external.add_argument("--output", type=Path, default=Path("outputs/external-dose"))
    effects = commands.add_parser(
        "summarize-effects",
        help="Normalize public treatment estimates to controls within each study",
    )
    effects.add_argument(
        "--reactor-csv",
        type=Path,
        default=Path("data/experimental/kozlowski_2025_bmp.csv"),
    )
    effects.add_argument(
        "--parameter-csv",
        type=Path,
        default=Path("data/experimental/valentin_bialowiec_2024_parameters.csv"),
    )
    effects.add_argument("--output", type=Path, default=Path("outputs/effects"))
    intake = commands.add_parser(
        "validate-intake",
        help="Validate a reactor-level contribution before modelling or publication",
    )
    intake.add_argument("csv", type=Path)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "validate-intake":
        report = validate_reactor_observations(pd.read_csv(args.csv))
        print(json.dumps(report.to_dict(), indent=2))
        if not report.valid:
            raise SystemExit(2)
        return
    if args.command == "summarize-effects":
        effects = build_within_study_effect_table(
            pd.read_csv(args.reactor_csv), pd.read_csv(args.parameter_csv)
        )
        args.output.mkdir(parents=True, exist_ok=True)
        destination = args.output / "within_study_effects.csv"
        effects.to_csv(destination, index=False)
        print(
            json.dumps(
                {
                    "output": str(destination),
                    "studies": effects["study_id"].nunique(),
                    "effects": len(effects),
                    "cross_study_pooling_performed": False,
                },
                indent=2,
            )
        )
        return
    if args.command == "benchmark-external-dose":
        frame = pd.read_csv(args.csv)
        comparison = compare_external_dose_responses(frame)
        args.output.mkdir(parents=True, exist_ok=True)
        comparison.to_csv(args.output / "dose_response_comparison.csv", index=False)
        best = comparison.loc[comparison["rank_by_held_out_rmse"] == 1]
        print(
            json.dumps(
                {
                    "dataset": str(args.csv),
                    "selection_metric": "leave-one-dose-out RMSE",
                    "best_model_by_response": dict(zip(best["response"], best["model"])),
                },
                indent=2,
            )
        )
        return
    if args.command == "benchmark-experimental":
        frame = pd.read_csv(args.csv)
        comparison = compare_experimental_baselines(frame)
        args.output.mkdir(parents=True, exist_ok=True)
        comparison.to_csv(args.output / "kinetic_baseline_comparison.csv", index=False)
        best = comparison.loc[comparison["rank_by_holdout_rmse"] == 1]
        print(
            json.dumps(
                {
                    "dataset": str(args.csv),
                    "selection_metric": "replicate-held-out RMSE",
                    "best_model_by_treatment": dict(zip(best["treatment"], best["model"])),
                },
                indent=2,
            )
        )
        return
    if args.command == "demo":
        csv_path = args.output / "synthetic_bmp_data.csv"
        frame = generate_demo_dataset(csv_path)
    else:
        frame = pd.read_csv(args.csv)

    parameters, metrics = fit_global(frame)
    save_report(frame, parameters, metrics, args.output)
    comparison = compare_models(frame)
    comparison.to_csv(args.output / "model_comparison.csv", index=False)

    mean_held_out_rmse = None
    if frame["batch_id"].nunique() >= 3:
        validation = leave_one_batch_out(frame)
        validation.to_csv(args.output / "leave_one_batch_out.csv", index=False)
        mean_held_out_rmse = validation["rmse_ml_g_vs"].mean()
    if args.command == "demo":
        bootstrap = bootstrap_parameters(frame, iterations=args.bootstrap)
        bootstrap.describe(percentiles=[0.025, 0.5, 0.975]).to_csv(
            args.output / "bootstrap_summary.csv"
        )
    print(
        json.dumps(
            {
                "parameters": asdict(parameters),
                "metrics": metrics,
                "best_model_by_aicc": comparison.iloc[0]["model"],
                "mean_held_out_rmse_ml_g_vs": mean_held_out_rmse,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
