"""Tests for ContractCheckResult."""

import pytest
from pydantic import ValidationError

from omnibase_spi.contracts.shared.contract_check_result import ContractCheckResult


@pytest.mark.unit
class TestContractCheckResult:
    """Tests for the ContractCheckResult shared primitive."""

    def test_create_minimal(self) -> None:
        """Create with only required fields."""
        cr = ContractCheckResult(
            check_id="RRH-1001",
            domain="rrh",
            status="pass",
        )
        assert cr.check_id == "RRH-1001"
        assert cr.domain == "rrh"
        assert cr.status == "pass"
        assert cr.schema_version == "1.0"
        assert cr.severity == "minor"
        assert cr.value is None
        assert cr.duration_ms is None
        assert cr.message == ""

    def test_create_full(self) -> None:
        """Create with all fields populated."""
        cr = ContractCheckResult(
            schema_version="1.1",
            check_id="CHECK-PY-001",
            domain="validation",
            status="fail",
            severity="critical",
            value=42,
            duration_ms=150.5,
            message="Python version too old",
        )
        assert cr.schema_version == "1.1"
        assert cr.check_id == "CHECK-PY-001"
        assert cr.domain == "validation"
        assert cr.status == "fail"
        assert cr.severity == "critical"
        assert cr.value == 42
        assert cr.duration_ms == 150.5
        assert cr.message == "Python version too old"

    def test_frozen(self) -> None:
        """Verify model is immutable."""
        cr = ContractCheckResult(check_id="RRH-1001", domain="rrh", status="pass")
        with pytest.raises(ValidationError):
            cr.check_id = "changed"  # type: ignore[misc]

    def test_forward_compat_extra_fields(self) -> None:
        """Unknown fields are tolerated (forward compatibility)."""
        cr = ContractCheckResult.model_validate(
            {
                "check_id": "RRH-1001",
                "domain": "rrh",
                "status": "pass",
                "future_field": "hello",
                "another_future": 99,
            }
        )
        assert cr.check_id == "RRH-1001"
        assert cr.model_extra is not None
        assert cr.model_extra.get("future_field") == "hello"
        assert cr.model_extra.get("another_future") == 99

    def test_value_types(self) -> None:
        """Value field accepts str, int, float, bool, and None."""
        for val in ["text", 42, 3.14, True, None]:
            cr = ContractCheckResult(
                check_id="X", domain="rrh", status="pass", value=val
            )
            assert cr.value == val

    def test_json_round_trip(self) -> None:
        """Serialize to JSON and back."""
        cr = ContractCheckResult(
            check_id="RRH-1201",
            domain="rrh",
            status="fail",
            severity="major",
            value=85,
            duration_ms=200.0,
            message="Tests failed",
        )
        j = cr.model_dump_json()
        cr2 = ContractCheckResult.model_validate_json(j)
        assert cr == cr2
