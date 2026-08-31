"""Structural overlap and additive-model estimability checks for the project's
literature-derived datasets.

These checks diagnose the study design; they do not estimate biological effects.

Two separate questions are answered for every factor pair, on purpose, because they
have different consequences and are easy to conflate:

- **Is the additive main-effects model estimable at all?** This depends only on
  graph connectivity (``connected_components == 1``), not on whether the graph has a
  cycle. A connected but acyclic (tree-shaped / nested) design can still estimate
  every additive contrast under the additivity assumption; it simply cannot test
  whether that assumption is reasonable, because it has no redundant cross-factor
  contrast to check it against. We call this *assumption-dependent estimability*.
- **Is there crossed evidence to test that additivity assumption?** This needs a
  cycle in the deduplicated bipartite graph (``cycle_rank > 0``), i.e. a redundant
  cross-factor contrast that lets the data itself flag an interaction, rather than
  relying entirely on modelling assumptions. We call this *crossed evidence*.

A disconnected design (more than one connected component) is *structurally
confounded*: some main-effect contrasts cannot be estimated under any additive
assumption, because the levels involved never co-occur, directly or through a chain
of shared levels. A design can also be a mix — nested within one component while
disconnected from another — which is neither cleanly "nested" nor cleanly
"disconnected", and is reported as its own category rather than forced into either.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd

REQUIRED_COLUMNS = {
    "study_id",
    "source_doi",
    "lab_id",
    "inoculum_id",
    "substrate_id",
    "biochar_family_id",
}

#: Pre-specified factor pairs the audit checks. Adding a pair here is a scientific
#: decision (it should be pre-specified before looking at results), not a mechanical
#: one, so it is kept as an explicit constant rather than inferred from the manifest.
AUDITED_PAIRS: tuple[tuple[str, str], ...] = (
    ("lab_id", "inoculum_id"),
    ("inoculum_id", "substrate_id"),
    ("inoculum_id", "biochar_family_id"),
)


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
    design_matrix_params: int
    design_matrix_rank: int
    rank_deficiency: int
    estimable_under_additive_assumption: bool
    evidence_category: str
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


def _additive_design_matrix_rank(edges: pd.DataFrame, left: str, right: str) -> tuple[int, int]:
    """Build the real one-hot additive design matrix (intercept + main effects).

    This is a direct linear-algebra estimability check, kept independent of the
    bipartite cycle-rank test above. Two-way connectedness theory predicts the two
    should agree that rank deficiency equals ``connected_components - 1``, but this
    computes it from the actual numeric matrix rather than trusting that theorem, so
    a mistake in the graph bookkeeping cannot silently hide a real estimability
    problem. `tests/test_identifiability.py` checks the two against each other.
    """
    left_dummies = pd.get_dummies(edges[left], prefix="L", drop_first=True, dtype=float)
    right_dummies = pd.get_dummies(edges[right], prefix="R", drop_first=True, dtype=float)
    intercept = pd.DataFrame({"intercept": np.ones(len(edges))})
    design = pd.concat([intercept, left_dummies, right_dummies], axis=1)
    params = design.shape[1]
    rank = int(np.linalg.matrix_rank(design.to_numpy()))
    return params, rank


def audit_pair(frame: pd.DataFrame, left: str, right: str) -> PairAudit:
    """Classify structural overlap and additive-model estimability for two factors."""
    edges = frame[[left, right]].drop_duplicates([left, right]).reset_index(drop=True)
    left_degree = edges.groupby(left)[right].nunique()
    right_degree = edges.groupby(right)[left].nunique()
    components = _component_count(edges, left, right)
    cycle_rank = len(edges) - left_degree.size - right_degree.size + components
    left_shared = int((left_degree > 1).sum())
    right_shared = int((right_degree > 1).sum())
    crossed = left_shared > 0 and right_shared > 0 and cycle_rank > 0

    params, rank = _additive_design_matrix_rank(edges, left, right)
    deficiency = params - rank
    estimable = deficiency == 0
    fully_disjoint = left_shared == 0 and right_shared == 0

    if crossed:
        evidence_category = "crossed_evidence"
        conclusion = "crossed_overlap_present"
    elif components == 1:
        evidence_category = "nested_single_component"
        conclusion = "nested_but_estimable_under_additivity"
    elif fully_disjoint:
        evidence_category = "disconnected_no_overlap"
        conclusion = "fully_aliased_or_disconnected"
    else:
        evidence_category = "partially_nested_partially_disconnected"
        conclusion = "structurally_confounded_mixed_design"

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
        design_matrix_params=params,
        design_matrix_rank=rank,
        rank_deficiency=deficiency,
        estimable_under_additive_assumption=estimable,
        evidence_category=evidence_category,
        conclusion=conclusion,
    )


def audit_manifest(frame: pd.DataFrame) -> pd.DataFrame:
    """Run the pre-specified factor-pair audits."""
    validate_manifest(frame)
    return pd.DataFrame(asdict(audit_pair(frame, left, right)) for left, right in AUDITED_PAIRS)


def write_audit(manifest_path: Path, output_dir: Path) -> pd.DataFrame:
    """Read a manifest and write deterministic graph edges and audit results."""
    frame = pd.read_csv(manifest_path)
    summary = audit_manifest(frame)
    output_dir.mkdir(parents=True, exist_ok=True)
    summary.to_csv(output_dir / "factor_pair_audit.csv", index=False)
    summary.to_json(output_dir / "factor_pair_audit.json", orient="records", indent=2)
    for left, right in AUDITED_PAIRS:
        frame[["study_id", left, right]].drop_duplicates().sort_values(
            [left, right, "study_id"]
        ).to_csv(output_dir / f"{left}__{right}_edges.csv", index=False)
    return summary
