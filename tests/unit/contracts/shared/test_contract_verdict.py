"""Tests for ContractVerdict."""

import pytest
from pydantic import ValidationError

from omnibase_spi.contracts.shared.contract_verdict import ContractVerdict


@pytest.mark.unit
class TestContractVerdict:
    """Tests for the ContractVerdict shared primitive."""

    def test_create_minimal(self) -> None:
        """Create with only required fields."""
        v = ContractVerdict(status="PASS")
        assert v.status == "PASS"
        assert v.schema_version == "1.0"
        assert v.score == 0
        assert v.block_reasons == []
        assert v.human_summary == ""
        assert v.promotion_recommendation is False

    def test_create_full(self) -> None:
        """Create with all fields populated."""
        v = ContractVerdict(
            status="FAIL",
            score=35,
            block_reasons=["Tests failed", "Coverage below 80%"],
            human_summary="Build is not ready for release.",
            promotion_recommendation=False,
        )
        assert v.status == "FAIL"
        assert v.score == 35
        assert len(v.block_reasons) == 2
        assert v.human_summary == "Build is not ready for release."

    def test_frozen(self) -> None:
        """Verify model is immutable."""
        v = ContractVerdict(status="PASS")
        with pytest.raises(ValidationError):
            v.status = "FAIL"  # type: ignore[misc]

    def test_score_bounds(self) -> None:
        """Score must be between 0 and 100."""
        ContractVerdict(status="PASS", score=0)
        ContractVerdict(status="PASS", score=100)
        with pytest.raises(ValidationError):
            ContractVerdict(status="PASS", score=-1)
        with pytest.raises(ValidationError):
            ContractVerdict(status="PASS", score=101)

    def test_forward_compat_extra_fields(self) -> None:
        """Unknown fields are tolerated."""
        v = ContractVerdict.model_validate(
            {
                "status": "QUARANTINE",
                "future_key": [1, 2, 3],
            }
        )
        assert v.status == "QUARANTINE"
        assert v.model_extra is not None
        assert v.model_extra.get("future_key") == [1, 2, 3]

    def test_json_round_trip(self) -> None:
        """Serialize to JSON and back."""
        v = ContractVerdict(
            status="PASS",
            score=95,
            block_reasons=[],
            human_summary="All checks passed.",
            promotion_recommendation=True,
        )
        j = v.model_dump_json()
        v2 = ContractVerdict.model_validate_json(j)
        assert v == v2
