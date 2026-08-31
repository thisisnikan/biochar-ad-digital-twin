"""Structural overlap checks for the project's literature-derived datasets.

These checks diagnose the study design; they do not estimate biological effects.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = {
    "study_id",
    "source_doi",
    "lab_id",
    "inoculum_id",
    "substrate_id",
    "biochar_family_id",
}


@dataclass(frozen=True)
class PairAudit:
    left_factor: str
    right_factor: str
    studies: int
    unique_edges: int
    left_levels: int
    right_levels: int
    connected_components: int
    cycle_rank: int
    left_levels_shared_across_right: int
    right_levels_shared_across_left: int
    crossed_overlap: bool
    conclusion: str


def validate_manifest(frame: pd.DataFrame) -> None:
    """Reject incomplete identifiers rather than silently inventing metadata."""
    missing = sorted(REQUIRED_COLUMNS - set(frame.columns))
    if missing:
        raise ValueError(f"Missing columns: {', '.join(missing)}")
    if frame.empty:
        raise ValueError("The study manifest is empty")
    if frame["study_id"].duplicated().any():
        duplicates = sorted(frame.loc[frame["study_id"].duplicated(), "study_id"].unique())
        raise ValueError(f"Duplicate study_id values: {', '.join(duplicates)}")
    identifiers = sorted(REQUIRED_COLUMNS - {"source_doi"})
    for column in identifiers:
        values = frame[column].astype("string").str.strip()
        if values.isna().any() or values.eq("").any() or values.eq("not_reported").any():
            raise ValueError(f"Unresolved identifier in {column}")


def _component_count(edges: pd.DataFrame, left: str, right: str) -> int:
    adjacency: dict[str, set[str]] = {}
    for left_value, right_value in edges[[left, right]].itertuples(index=False, name=None):
        left_node = f"L:{left_value}"
        right_node = f"R:{right_value}"
        adjacency.setdefault(left_node, set()).add(right_node)
        adjacency.setdefault(right_node, set()).add(left_node)

    unseen = set(adjacency)
    components = 0
    while unseen:
        components += 1
        stack = [unseen.pop()]
        while stack:
            for neighbour in adjacency[stack.pop()]:
                if neighbour in unseen:
                    unseen.remove(neighbour)
                    stack.append(neighbour)
    return components


def audit_pair(frame: pd.DataFrame, left: str, right: str) -> PairAudit:
    """Test whether two categorical factors have genuinely crossed overlap.

    A positive result requires both directions of reuse and at least one cycle in
    the deduplicated bipartite graph. This deliberately asks for a redundant
    cross-factor contrast, rather than declaring success from an additive model
    imposed on a tree or nested design.
    """
    edges = frame[["study_id", left, right]].drop_duplicates([left, right])
    left_degree = edges.groupby(left)[right].nunique()
    right_degree = edges.groupby(right)[left].nunique()
    components = _component_count(edges, left, right)
    cycle_rank = len(edges) - left_degree.size - right_degree.size + components
    left_shared = int((left_degree > 1).sum())
    right_shared = int((right_degree > 1).sum())
    crossed = left_shared > 0 and right_shared > 0 and cycle_rank > 0
    if crossed:
        conclusion = "crossed_overlap_present"
    elif left_shared == 0 and right_shared == 0:
        conclusion = "fully_aliased_or_disconnected"
    else:
        conclusion = "nested_or_acyclic_overlap_only"
    return PairAudit(
        left_factor=left,
        right_factor=right,
        studies=int(frame["study_id"].nunique()),
        unique_edges=len(edges),
        left_levels=left_degree.size,
        right_levels=right_degree.size,
        connected_components=components,
        cycle_rank=cycle_rank,
        left_levels_shared_across_right=left_shared,
        right_levels_shared_across_left=right_shared,
        crossed_overlap=crossed,
        conclusion=conclusion,
    )


def audit_manifest(frame: pd.DataFrame) -> pd.DataFrame:
    """Run the pre-specified factor-pair audits."""
    validate_manifest(frame)
    pairs = [
        ("lab_id", "inoculum_id"),
        ("inoculum_id", "substrate_id"),
        ("inoculum_id", "biochar_family_id"),
    ]
    return pd.DataFrame(asdict(audit_pair(frame, left, right)) for left, right in pairs)


def write_audit(manifest_path: Path, output_dir: Path) -> pd.DataFrame:
    """Read a manifest and write deterministic graph edges and audit results."""
    frame = pd.read_csv(manifest_path)
    summary = audit_manifest(frame)
    output_dir.mkdir(parents=True, exist_ok=True)
    summary.to_csv(output_dir / "factor_pair_audit.csv", index=False)
    for left, right in (
        ("lab_id", "inoculum_id"),
        ("inoculum_id", "substrate_id"),
        ("inoculum_id", "biochar_family_id"),
    ):
        frame[["study_id", left, right]].drop_duplicates().sort_values(
            [left, right, "study_id"]
        ).to_csv(output_dir / f"{left}__{right}_edges.csv", index=False)
    return summary
