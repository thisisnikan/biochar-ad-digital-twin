"""Build a tidy experimental BMP dataset from Kozłowski et al. (2025).

The source workbook is an openly licensed supplement to:
https://doi.org/10.1038/s41598-025-02564-0

Only Python's standard library is used so the transformation remains auditable
without adding an Excel-engine dependency to the research package.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import tempfile
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

SOURCE_URL = (
    "https://media.springernature.com/original/springer-static/esm/"
    "art%3A10.1038%2Fs41598-025-02564-0/MediaObjects/"
    "41598_2025_2564_MOESM1_ESM.xlsx"
)
SOURCE_SHA256 = "a5be0c25990acbdd0a6ac14dfa202398e61713fea8496884018e97f1cf87b983"
SOURCE_DOI = "10.1038/s41598-025-02564-0"
SHEET_NAME = "Godzinowe"
XML_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PACKAGE_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"

INOCULUM_VS_G = 8.851386739388484
SUBSTRATE_VS_G = 4.425592386264921


def _column_number(reference: str) -> int:
    letters = "".join(character for character in reference if character.isalpha())
    result = 0
    for character in letters:
        result = result * 26 + ord(character.upper()) - ord("A") + 1
    return result


def _shared_strings(archive: zipfile.ZipFile) -> list[str]:
    try:
        root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    except KeyError:
        return []
    return ["".join(node.text or "" for node in item.iter(f"{{{XML_NS}}}t")) for item in root]


def _sheet_path(archive: zipfile.ZipFile, sheet_name: str) -> str:
    workbook = ET.fromstring(archive.read("xl/workbook.xml"))
    relationship_id = None
    for sheet in workbook.iter(f"{{{XML_NS}}}sheet"):
        if sheet.attrib["name"] == sheet_name:
            relationship_id = sheet.attrib[f"{{{REL_NS}}}id"]
            break
    if relationship_id is None:
        raise ValueError(f"Worksheet not found: {sheet_name}")

    relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    for relationship in relationships.iter(f"{{{PACKAGE_REL_NS}}}Relationship"):
        if relationship.attrib["Id"] == relationship_id:
            target = relationship.attrib["Target"].lstrip("/")
            return target if target.startswith("xl/") else f"xl/{target}"
    raise ValueError(f"Worksheet relationship not found: {sheet_name}")


def _read_cells(path: Path) -> dict[tuple[int, int], float | str]:
    with zipfile.ZipFile(path) as archive:
        strings = _shared_strings(archive)
        root = ET.fromstring(archive.read(_sheet_path(archive, SHEET_NAME)))

    cells: dict[tuple[int, int], float | str] = {}
    for cell in root.iter(f"{{{XML_NS}}}c"):
        reference = cell.attrib["r"]
        row = int("".join(character for character in reference if character.isdigit()))
        column = _column_number(reference)
        value_node = cell.find(f"{{{XML_NS}}}v")
        if value_node is None or value_node.text is None:
            continue
        raw = value_node.text
        if cell.attrib.get("t") == "s":
            value: float | str = strings[int(raw)]
        else:
            try:
                value = float(raw)
            except ValueError:
                value = raw
        cells[(row, column)] = value
    return cells


def _obtain_source(source: Path | None) -> tuple[Path, tempfile.TemporaryDirectory[str] | None]:
    temporary = None
    if source is None:
        temporary = tempfile.TemporaryDirectory(prefix="biochar_ad_source_")
        source = Path(temporary.name) / "supplement.xlsx"
        urllib.request.urlretrieve(SOURCE_URL, source)
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if digest != SOURCE_SHA256:
        raise ValueError(f"Source SHA-256 mismatch: expected {SOURCE_SHA256}, received {digest}")
    return source, temporary


def build_dataset(source: Path, destination: Path) -> int:
    """Transform the publisher workbook into a long, traceable CSV."""

    cells = _read_cells(source)
    blank_columns = (5, 6, 7)  # E:G, inoculum-only controls
    treatments = (
        ("food_waste", "none", None, 0.0, ((8, 1, True), (9, 2, True), (10, 3, True))),
        (
            "food_waste_torrefaction_240c",
            "torrefaction_product",
            240.0,
            5.0,
            ((11, 1, True), (12, 2, False), (13, 3, True)),
        ),
        (
            "food_waste_pyrolysis_600c",
            "biochar",
            600.0,
            5.0,
            ((14, 1, True), (15, 2, True), (16, 3, False)),
        ),
        (
            "food_waste_hydrochar_240c",
            "hydrochar",
            240.0,
            5.0,
            ((17, 1, True), (18, 2, True), (19, 3, True)),
        ),
    )
    fieldnames = (
        "study_id",
        "treatment",
        "replicate",
        "time_hours",
        "time_days",
        "source_day_label",
        "source_reported_time_days",
        "temperature_c",
        "carbon_material",
        "process_temperature_c",
        "dose_g_l",
        "raw_cumulative_methane_ml",
        "blank_mean_cumulative_methane_ml",
        "methane_ml_g_vs",
        "included_in_benchmark",
        "exclusion_reason",
        "data_origin",
        "source_doi",
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    rows_written = 0
    with destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in range(18, 523):
            hour = float(cells[(row, 3)])
            blank_mean = sum(float(cells[(row, col)]) for col in blank_columns) / 3
            for treatment, material, process_temperature, dose, reactors in treatments:
                for column, replicate, included in reactors:
                    raw_methane = float(cells[(row, column)])
                    corrected = (raw_methane - blank_mean) / SUBSTRATE_VS_G
                    writer.writerow(
                        {
                            "study_id": "kozlowski_2025_scientific_reports",
                            "treatment": treatment,
                            "replicate": replicate,
                            "time_hours": f"{hour:.0f}",
                            # The workbook's derived time column divides by 96. The article,
                            # raw hourly index, and day label all support division by 24.
                            "time_days": f"{hour / 24:.8f}",
                            "source_day_label": f"{float(cells[(row, 4)]):.0f}",
                            "source_reported_time_days": f"{float(cells[(row, 21)]):.8f}",
                            "temperature_c": "37",
                            "carbon_material": material,
                            "process_temperature_c": (
                                "" if process_temperature is None else f"{process_temperature:.0f}"
                            ),
                            "dose_g_l": f"{dose:.1f}",
                            "raw_cumulative_methane_ml": f"{raw_methane:.8f}",
                            "blank_mean_cumulative_methane_ml": f"{blank_mean:.8f}",
                            "methane_ml_g_vs": f"{corrected:.8f}",
                            "included_in_benchmark": str(included).lower(),
                            "exclusion_reason": (
                                ""
                                if included
                                else "excluded_from_publisher_mean; inconsistent_raw_signal"
                            ),
                            "data_origin": "experimental_publisher_supplement",
                            "source_doi": SOURCE_DOI,
                        }
                    )
                    rows_written += 1
    return rows_written


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, help="Optional local copy of the verified XLSX")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/experimental/kozlowski_2025_bmp.csv"),
    )
    args = parser.parse_args()
    source, temporary = _obtain_source(args.source)
    try:
        rows = build_dataset(source, args.output)
    finally:
        if temporary is not None:
            temporary.cleanup()
    print(f"Wrote {rows} experimental observations to {args.output}")


if __name__ == "__main__":
    main()
