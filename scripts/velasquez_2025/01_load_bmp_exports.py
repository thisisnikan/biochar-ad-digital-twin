from __future__ import annotations

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
PRIVATE_DIR = ROOT / "data" / "private" / "velasquez_2025"
OUTPUT_DIR = ROOT / "results" / "velasquez_negative_control"

EXPECTED = {
    "BMPEN1": PRIVATE_DIR / "BMPEN1.csv",
    "BMPEN2": PRIVATE_DIR / "BMPEN2.csv",
}


def read_export(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"Missing {path}. Export the worksheet from Origin/Origin Viewer as CSV; "
            "do not commit the privately shared raw file."
        )
    df = pd.read_csv(path)
    # Preserve original column names exactly at ingestion. Normalization happens only
    # after treatment/control mapping is verified against the experimental design.
    return df


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for experiment, path in EXPECTED.items():
        df = read_export(path)
        rows.append(
            {
                "experiment": experiment,
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": " | ".join(map(str, df.columns)),
                "missing_cells": int(df.isna().sum().sum()),
            }
        )
        # Local QC snapshot only. This file may contain author-shared raw values and
        # should not be committed unless redistribution permission is obtained.
        df.head(10).to_csv(OUTPUT_DIR / f"{experiment}_head_local.csv", index=False)

    pd.DataFrame(rows).to_csv(OUTPUT_DIR / "bmp_export_inventory.csv", index=False)
    print(pd.DataFrame(rows).to_string(index=False))


if __name__ == "__main__":
    main()
