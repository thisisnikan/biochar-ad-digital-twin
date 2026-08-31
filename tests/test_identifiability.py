import pandas as pd
import pytest

from biochar_ad_twin.identifiability import (
    AUDITED_PAIRS,
    audit_manifest,
    audit_pair,
    validate_manifest,
)


def _manifest(rows: list[tuple[str, str]]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "study_id": f"s{index}",
                "source_doi": f"doi:{index}",
                "lab_id": lab,
                "inoculum_id": inoculum,
                "substrate_id": f"substrate_{index}",
                "biochar_family_id": f"biochar_{index}",
            }
            for index, (lab, inoculum) in enumerate(rows)
        ]
    )


def test_crossed_two_by_two_design_is_identifiable() -> None:
    frame = _manifest([("a", "x"), ("a", "y"), ("b", "x"), ("b", "y")])
    result = audit_pair(frame, "lab_id", "inoculum_id")
    assert result.crossed_overlap
    assert result.cycle_rank == 1
    assert result.evidence_category == "crossed_evidence"
    assert result.estimable_under_additive_assumption
    assert result.rank_deficiency == 0


def test_connected_nested_tree_is_estimable_but_not_crossed() -> None:
    """A connected, acyclic (tree-shaped) design has no redundant cross-factor
    contrast, so it is not "crossed" — but its additive main effects are still
    fully estimable under the additivity assumption, because the graph is
    connected. A cycle is not universally required for additive estimability."""
    frame = _manifest([("a", "x"), ("a", "y"), ("b", "y")])
    result = audit_pair(frame, "lab_id", "inoculum_id")
    assert result.connected_components == 1
    assert result.cycle_rank == 0
    assert not result.crossed_overlap
    assert result.evidence_category == "nested_single_component"
    assert result.conclusion == "nested_but_estimable_under_additivity"
    assert result.estimable_under_additive_assumption
    assert result.rank_deficiency == 0


def test_fully_disconnected_pairs_are_not_estimable() -> None:
    """No level of either factor repeats: a perfect 1-1 matching with two
    separate components. Main effects are structurally confounded — not merely
    "untested" — because the two components never co-occur at all."""
    frame = _manifest([("a", "x"), ("b", "y")])
    result = audit_pair(frame, "lab_id", "inoculum_id")
    assert result.connected_components == 2
    assert not result.crossed_overlap
    assert result.evidence_category == "disconnected_no_overlap"
    assert result.conclusion == "fully_aliased_or_disconnected"
    assert not result.estimable_under_additive_assumption
    assert result.rank_deficiency == 1


def test_mixed_nested_and_disconnected_design_is_reported_as_its_own_category() -> None:
    """One lab contributes two inocula (nested within that component) while a
    second lab's single inoculum is never linked to the first component
    (disconnected). This mirrors the repository's real lab-inoculum manifest and
    must not be mislabelled as purely "nested" or purely "disconnected"."""
    frame = _manifest([("a", "x"), ("a", "y"), ("b", "z")])
    result = audit_pair(frame, "lab_id", "inoculum_id")
    assert result.connected_components == 2
    assert result.cycle_rank == 0
    assert not result.crossed_overlap
    assert result.evidence_category == "partially_nested_partially_disconnected"
    assert result.conclusion == "structurally_confounded_mixed_design"
    assert not result.estimable_under_additive_assumption
    assert result.rank_deficiency == 1


def test_design_matrix_rank_deficiency_matches_connectivity_theorem() -> None:
    """Cross-check the direct numeric design-matrix rank against the graph-theory
    prediction (deficiency == connected_components - 1) for every audited shape."""
    cases = [
        [("a", "x"), ("a", "y"), ("b", "x"), ("b", "y")],
        [("a", "x"), ("a", "y"), ("b", "y")],
        [("a", "x"), ("b", "y")],
        [("a", "x"), ("a", "y"), ("b", "z")],
    ]
    for rows in cases:
        frame = _manifest(rows)
        result = audit_pair(frame, "lab_id", "inoculum_id")
        assert result.rank_deficiency == result.connected_components - 1
        assert result.design_matrix_rank == result.design_matrix_params - result.rank_deficiency


def test_manifest_rejects_unresolved_factor_ids() -> None:
    frame = _manifest([("a", "not_reported")])
    with pytest.raises(ValueError, match="Unresolved identifier"):
        validate_manifest(frame)


def test_manifest_rejects_missing_values() -> None:
    frame = _manifest([("a", "x"), ("b", "y")])
    frame.loc[1, "inoculum_id"] = None
    with pytest.raises(ValueError, match="Unresolved identifier"):
        validate_manifest(frame)


def test_manifest_rejects_duplicate_study_id() -> None:
    frame = _manifest([("a", "x"), ("b", "y")])
    frame["study_id"] = "same_study"
    with pytest.raises(ValueError, match="Duplicate study_id"):
        validate_manifest(frame)


def test_full_audit_has_prespecified_pairs() -> None:
    frame = _manifest([("a", "x"), ("b", "y")])
    result = audit_manifest(frame)
    assert len(result) == len(AUDITED_PAIRS)
    assert not result["crossed_overlap"].any()
    assert not result["estimable_under_additive_assumption"].any()
