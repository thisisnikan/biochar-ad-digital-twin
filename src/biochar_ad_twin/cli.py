"""Command-line interface."""

import argparse
import json
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from .analysis import compare_models, leave_one_batch_out
from .data import generate_demo_dataset
from .fit import bootstrap_parameters, fit_global
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
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "demo":
        csv_path = args.output / "synthetic_bmp_data.csv"
        frame = generate_demo_dataset(csv_path)
    else:
        frame = pd.read_csv(args.csv)

    parameters, metrics = fit_global(frame)
    save_report(frame, parameters, metrics, args.output)
    comparison = compare_models(frame)
    validation = leave_one_batch_out(frame)
    comparison.to_csv(args.output / "model_comparison.csv", index=False)
    validation.to_csv(args.output / "leave_one_batch_out.csv", index=False)
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
                "mean_held_out_rmse_ml_g_vs": validation["rmse_ml_g_vs"].mean(),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
