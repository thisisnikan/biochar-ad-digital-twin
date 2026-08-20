"""Command-line interface."""

import argparse
import json
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from .benchmarks import compare_models
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
    compare = commands.add_parser("compare", help="Benchmark four empirical kinetic models")
    compare.add_argument("csv", type=Path)
    compare.add_argument("--output", type=Path, default=Path("outputs"))
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "demo":
        csv_path = args.output / "synthetic_bmp_data.csv"
        frame = generate_demo_dataset(csv_path)
    elif args.command == "fit":
        frame = pd.read_csv(args.csv)
    else:
        frame = pd.read_csv(args.csv)
        args.output.mkdir(parents=True, exist_ok=True)
        comparison = compare_models(frame)
        comparison.to_csv(args.output / "model_comparison.csv", index=False)
        print(comparison.to_string(index=False))
        return

    parameters, metrics = fit_global(frame)
    save_report(frame, parameters, metrics, args.output)
    if args.command == "demo":
        bootstrap = bootstrap_parameters(frame, iterations=args.bootstrap)
        bootstrap.describe(percentiles=[0.025, 0.5, 0.975]).to_csv(
            args.output / "bootstrap_summary.csv"
        )
        compare_models(frame).to_csv(args.output / "model_comparison.csv", index=False)
    print(json.dumps({"parameters": asdict(parameters), "metrics": metrics}, indent=2))


if __name__ == "__main__":
    main()
