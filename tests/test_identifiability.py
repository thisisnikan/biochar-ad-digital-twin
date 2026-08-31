import pandas as pd
import pytest

from biochar_ad_twin.identifiability import audit_manifest, audit_pair, validate_manifest


def _manifest(rows: list[tuple[str, str, str]]) -> pd.DataFrame:
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
            for index, (lab, inoculum, _) in enumerate(rows)
        ]
    )


def test_crossed_two_by_two_design_is_identifiable() -> None:
    frame = _manifest(
        [("a", "x", ""), ("a", "y", ""), ("b", "x", ""), ("b", "y", "")]
    )
    result = audit_pair(frame, "lab_id", "inoculum_id")
    assert result.crossed_overlap
    assert result.cycle_rank == 1


def test_nested_design_is_not_called_crossed() -> None:
    frame = _manifest([("a", "x", ""), ("a", "y", ""), ("b", "z", "")])
    result = audit_pair(frame, "lab_id", "inoculum_id")
    assert not result.crossed_overlap
    assert result.conclusion == "nested_or_acyclic_overlap_only"
    assert result.cycle_rank == 0


def test_manifest_rejects_unresolved_factor_ids() -> None:
    frame = _manifest([("a", "not_reported", "")])
    with pytest.raises(ValueError, match="Unresolved identifier"):
        validate_manifest(frame)


def test_full_audit_has_prespecified_pairs() -> None:
    frame = _manifest([("a", "x", ""), ("b", "y", "")])
    result = audit_manifest(frame)
    assert len(result) == 3
    assert not result["crossed_overlap"].any()
