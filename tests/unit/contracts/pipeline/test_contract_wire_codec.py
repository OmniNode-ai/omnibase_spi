"""Tests for pipeline wire codec helpers."""

import json

import pytest

from omnibase_spi.contracts.pipeline.contract_wire_codec import (
    from_json,
    from_yaml,
    to_json,
    to_yaml,
)
from omnibase_spi.contracts.shared.contract_check_result import ContractCheckResult
from omnibase_spi.contracts.shared.contract_verdict import ContractVerdict


@pytest.mark.unit
class TestToJson:
    """Tests for to_json serialization."""

    def test_deterministic_output(self) -> None:
        """Same input always produces same JSON (sorted keys)."""
        cr = ContractCheckResult(check_id="RRH-1001", domain="rrh", status="pass")
        j1 = to_json(cr)
        j2 = to_json(cr)
        assert j1 == j2

    def test_sorted_keys(self) -> None:
        """Keys are sorted alphabetically."""
        cr = ContractCheckResult(check_id="RRH-1001", domain="rrh", status="pass")
        j = to_json(cr)
        data = json.loads(j)
        keys = list(data.keys())
        assert keys == sorted(keys)

    def test_round_trip(self) -> None:
        """JSON round-trip preserves all data."""
        cr = ContractCheckResult(
            check_id="CHECK-PY-001",
            domain="validation",
            status="fail",
            severity="critical",
            value=42,
            duration_ms=100.5,
            message="Failed",
        )
        j = to_json(cr)
        cr2 = from_json(j, ContractCheckResult)
        assert cr == cr2


@pytest.mark.unit
class TestFromJson:
    """Tests for from_json deserialization."""

    def test_extra_fields_tolerated(self) -> None:
        """Unknown fields do not cause errors."""
        raw = json.dumps(
            {
                "check_id": "X",
                "domain": "rrh",
                "status": "pass",
                "unknown_field": "ok",
            }
        )
        cr = from_json(raw, ContractCheckResult)
        assert cr.check_id == "X"
        assert cr.model_extra is not None


@pytest.mark.unit
class TestYamlSerialization:
    """Tests for YAML serialization."""

    def test_round_trip(self) -> None:
        """YAML round-trip preserves data."""
        v = ContractVerdict(
            status="PASS",
            score=90,
            human_summary="All good",
            promotion_recommendation=True,
        )
        y = to_yaml(v)
        v2 = from_yaml(y, ContractVerdict)
        assert v == v2

    def test_yaml_is_string(self) -> None:
        """to_yaml returns a string."""
        cr = ContractCheckResult(check_id="X", domain="rrh", status="pass")
        y = to_yaml(cr)
        assert isinstance(y, str)
        assert "check_id" in y
