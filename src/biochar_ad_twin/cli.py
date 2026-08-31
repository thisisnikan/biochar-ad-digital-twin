"""Command-line interface."""

import argparse
import json
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from .analysis import compare_models, leave_one_batch_out
from .baselines import compare_experimental_baselines
from .data import generate_demo_dataset
from .external_validation import compare_external_dose_responses
from .fit import bootstrap_parameters, fit_global
from .identifiability import write_audit
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
    identifiability = commands.add_parser(
        "audit-identifiability",
        help="Audit cross-study factor overlap and additive-model estimability",
    )
    identifiability.add_argument(
        "csv", type=Path, nargs="?", default=Path("03_identifiability/study_metadata.csv")
    )
    identifiability.add_argument("--output", type=Path, default=Path("results/identifiability"))
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "audit-identifiability":
        summary = write_audit(args.csv, args.output)
        lab_inoculum = summary.loc[
            (summary["left_factor"] == "lab_id") & (summary["right_factor"] == "inoculum_id")
        ].iloc[0]
        print(
            json.dumps(
                {
                    "manifest": str(args.csv),
                    "lab_inoculum_evidence_category": lab_inoculum["evidence_category"],
                    "lab_inoculum_estimable_under_additive_assumption": bool(
                        lab_inoculum["estimable_under_additive_assumption"]
                    ),
                    "lab_inoculum_crossed_evidence": bool(lab_inoculum["crossed_overlap"]),
                    "conclusion": lab_inoculum["conclusion"],
                    "next_gate": (
                        "hierarchical_model_candidate"
                        if lab_inoculum["crossed_overlap"]
                        else "targeted_cross_lab_data_needed"
                    ),
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
