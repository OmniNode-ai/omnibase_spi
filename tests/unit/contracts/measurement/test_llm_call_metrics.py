"""Tests for LLM cost tracking contracts.

Covers:
- ContractEnumUsageSource enum stability
- ContractLlmUsageRaw frozen/forbid/extensions/round-trip
- ContractLlmUsageNormalized frozen/forbid/extensions/round-trip/validators
- ContractLlmCallMetrics frozen/forbid/extensions/round-trip/global invariants
"""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from omnibase_spi.contracts.measurement.contract_llm_call_metrics import (
    ContractLlmCallMetrics,
    ContractLlmUsageNormalized,
    ContractLlmUsageRaw,
)
from omnibase_spi.contracts.measurement.enum_usage_source import (
    ContractEnumUsageSource,
)

# ---------------------------------------------------------------------------
# ContractEnumUsageSource
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestContractEnumUsageSource:
    """Tests for ContractEnumUsageSource enum stability."""

    def test_has_three_members(self) -> None:
        """Enum must contain exactly three members."""
        assert len(ContractEnumUsageSource) == 3

    def test_member_values(self) -> None:
        """Each member must have the expected string value."""
        assert ContractEnumUsageSource.API == "api"
        assert ContractEnumUsageSource.ESTIMATED == "estimated"
        assert ContractEnumUsageSource.MISSING == "missing"

    def test_is_str_enum(self) -> None:
        """All members must be str instances."""
        for member in ContractEnumUsageSource:
            assert isinstance(member, str)


# ---------------------------------------------------------------------------
# ContractLlmUsageRaw
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestContractLlmUsageRaw:
    """Tests for ContractLlmUsageRaw."""

    def test_create_minimal(self) -> None:
        """Default construction must populate all fields with defaults."""
        raw = ContractLlmUsageRaw()
        assert raw.schema_version == "1.0"
        assert raw.provider == ""
        assert raw.raw_data == {}
        assert raw.extensions == {}

    def test_create_full(self) -> None:
        """Full construction must retain all provided values."""
        raw = ContractLlmUsageRaw(
            provider="openai",
            raw_data={
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150,
            },
            extensions={"region": "us-east-1"},
        )
        assert raw.provider == "openai"
        assert raw.raw_data["total_tokens"] == 150
        assert raw.extensions == {"region": "us-east-1"}

    def test_frozen(self) -> None:
        """Frozen model must reject attribute mutation."""
        raw = ContractLlmUsageRaw(provider="anthropic")
        with pytest.raises(ValidationError):
            raw.provider = "openai"  # type: ignore[misc]

    def test_extra_fields_rejected(self) -> None:
        """Extra fields must be rejected by extra='forbid'."""
        with pytest.raises(ValidationError, match="extra_forbidden"):
            ContractLlmUsageRaw(
                provider="openai",
                unknown="rejected",  # type: ignore[call-arg]
            )

    def test_json_round_trip(self) -> None:
        """JSON serialization must produce an equivalent instance."""
        raw = ContractLlmUsageRaw(
            provider="vllm",
            raw_data={"usage": {"prompt_tokens": 42}},
        )
        j = raw.model_dump_json()
        raw2 = ContractLlmUsageRaw.model_validate_json(j)
        assert raw == raw2

    def test_dict_round_trip(self) -> None:
        """Dict serialization must produce an equivalent instance."""
        raw = ContractLlmUsageRaw(provider="anthropic", raw_data={"input_tokens": 10})
        d = raw.model_dump()
        assert isinstance(d, dict)
        raw2 = ContractLlmUsageRaw.model_validate(d)
        assert raw == raw2


# ---------------------------------------------------------------------------
# ContractLlmUsageNormalized
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestContractLlmUsageNormalized:
    """Tests for ContractLlmUsageNormalized."""

    def test_create_minimal(self) -> None:
        """Default construction must populate all fields with defaults."""
        norm = ContractLlmUsageNormalized()
        assert norm.schema_version == "1.0"
        assert norm.prompt_tokens == 0
        assert norm.completion_tokens == 0
        assert norm.total_tokens == 0
        assert norm.source == ContractEnumUsageSource.MISSING
        assert norm.usage_is_estimated is False
        assert norm.extensions == {}

    def test_create_api_source(self) -> None:
        """API source with usage_is_estimated=False must be accepted."""
        norm = ContractLlmUsageNormalized(
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            source=ContractEnumUsageSource.API,
            usage_is_estimated=False,
        )
        assert norm.prompt_tokens == 100
        assert norm.source == ContractEnumUsageSource.API
        assert norm.usage_is_estimated is False

    def test_create_estimated_source(self) -> None:
        """ESTIMATED source with usage_is_estimated=True must be accepted."""
        norm = ContractLlmUsageNormalized(
            prompt_tokens=95,
            completion_tokens=48,
            total_tokens=143,
            source=ContractEnumUsageSource.ESTIMATED,
            usage_is_estimated=True,
        )
        assert norm.source == ContractEnumUsageSource.ESTIMATED
        assert norm.usage_is_estimated is True

    def test_estimated_source_requires_usage_is_estimated_true(self) -> None:
        """ESTIMATED source with usage_is_estimated=False must be rejected."""
        with pytest.raises(ValidationError, match="usage_is_estimated must be True"):
            ContractLlmUsageNormalized(
                source=ContractEnumUsageSource.ESTIMATED,
                usage_is_estimated=False,
            )

    def test_api_source_requires_usage_is_estimated_false(self) -> None:
        """API source with usage_is_estimated=True must be rejected."""
        with pytest.raises(ValidationError, match="usage_is_estimated must be False"):
            ContractLlmUsageNormalized(
                source=ContractEnumUsageSource.API,
                usage_is_estimated=True,
            )

    def test_missing_source_allows_either_estimated_flag(self) -> None:
        """MISSING source must not constrain usage_is_estimated."""
        norm_false = ContractLlmUsageNormalized(
            source=ContractEnumUsageSource.MISSING,
            usage_is_estimated=False,
        )
        assert norm_false.usage_is_estimated is False

        norm_true = ContractLlmUsageNormalized(
            source=ContractEnumUsageSource.MISSING,
            usage_is_estimated=True,
        )
        assert norm_true.usage_is_estimated is True

    def test_inconsistent_total_tokens_rejected(self) -> None:
        """total_tokens must equal prompt_tokens + completion_tokens."""
        with pytest.raises(ValidationError, match="total_tokens"):
            ContractLlmUsageNormalized(
                prompt_tokens=100,
                completion_tokens=50,
                total_tokens=999,
            )

    def test_negative_tokens_rejected(self) -> None:
        """Negative token counts must be rejected by ge=0 constraint."""
        with pytest.raises(ValidationError):
            ContractLlmUsageNormalized(prompt_tokens=-1)

    def test_frozen(self) -> None:
        """Frozen model must reject attribute mutation."""
        norm = ContractLlmUsageNormalized()
        with pytest.raises(ValidationError):
            norm.prompt_tokens = 10  # type: ignore[misc]

    def test_extra_fields_rejected(self) -> None:
        """Extra fields must be rejected by extra='forbid'."""
        with pytest.raises(ValidationError, match="extra_forbidden"):
            ContractLlmUsageNormalized(
                nope="rejected",  # type: ignore[call-arg]
            )

    def test_json_round_trip(self) -> None:
        """JSON serialization must produce an equivalent instance."""
        norm = ContractLlmUsageNormalized(
            prompt_tokens=200,
            completion_tokens=100,
            total_tokens=300,
            source=ContractEnumUsageSource.API,
            usage_is_estimated=False,
        )
        j = norm.model_dump_json()
        norm2 = ContractLlmUsageNormalized.model_validate_json(j)
        assert norm == norm2

    def test_dict_round_trip(self) -> None:
        """Dict serialization must produce an equivalent instance."""
        norm = ContractLlmUsageNormalized(
            prompt_tokens=200,
            completion_tokens=100,
            total_tokens=300,
            source=ContractEnumUsageSource.API,
            usage_is_estimated=False,
        )
        d = norm.model_dump()
        assert isinstance(d, dict)
        norm2 = ContractLlmUsageNormalized.model_validate(d)
        assert norm == norm2


# ---------------------------------------------------------------------------
# ContractLlmCallMetrics
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestContractLlmCallMetrics:
    """Tests for ContractLlmCallMetrics."""

    def test_create_minimal(self) -> None:
        """Minimal construction with only model_id must populate defaults."""
        m = ContractLlmCallMetrics(model_id="gpt-4o")
        assert m.model_id == "gpt-4o"
        assert m.schema_version == "1.0"
        assert m.prompt_tokens == 0
        assert m.completion_tokens == 0
        assert m.total_tokens == 0
        assert m.estimated_cost_usd is None
        assert m.latency_ms is None
        assert m.usage_raw is None
        assert m.usage_normalized is None
        assert m.usage_is_estimated is False
        assert m.input_hash == ""
        assert m.code_version == ""
        assert m.contract_version == "1.0"
        assert m.timestamp_iso == ""
        assert m.source == ""
        assert m.extensions == {}

    def test_create_full(self) -> None:
        """Full construction must retain all provided values including nested objects."""
        raw = ContractLlmUsageRaw(
            provider="openai",
            raw_data={"prompt_tokens": 500, "completion_tokens": 200},
        )
        norm = ContractLlmUsageNormalized(
            prompt_tokens=500,
            completion_tokens=200,
            total_tokens=700,
            source=ContractEnumUsageSource.API,
            usage_is_estimated=False,
        )
        m = ContractLlmCallMetrics(
            model_id="gpt-4o",
            prompt_tokens=500,
            completion_tokens=200,
            total_tokens=700,
            estimated_cost_usd=0.015,
            latency_ms=1250.5,
            usage_raw=raw,
            usage_normalized=norm,
            usage_is_estimated=False,
            input_hash="abc123def456",
            code_version="0.8.0",
            contract_version="1.0",
            timestamp_iso="2026-02-15T10:00:00Z",
            source="pipeline-agent",
            extensions={"request_id": "req-xyz"},
        )
        assert m.prompt_tokens == 500
        assert m.completion_tokens == 200
        assert m.total_tokens == 700
        assert m.estimated_cost_usd == 0.015
        assert m.latency_ms == 1250.5
        assert m.usage_raw is not None
        assert m.usage_raw.provider == "openai"
        assert m.usage_normalized is not None
        assert m.usage_normalized.total_tokens == 700
        assert m.input_hash == "abc123def456"
        assert m.code_version == "0.8.0"
        assert m.timestamp_iso == "2026-02-15T10:00:00Z"
        assert m.source == "pipeline-agent"
        assert m.extensions == {"request_id": "req-xyz"}

    def test_model_id_required(self) -> None:
        """Construction without model_id must raise ValidationError."""
        with pytest.raises(ValidationError):
            ContractLlmCallMetrics()  # type: ignore[call-arg]

    def test_negative_tokens_rejected(self) -> None:
        """Negative token counts must be rejected by ge=0 constraint."""
        with pytest.raises(ValidationError):
            ContractLlmCallMetrics(model_id="x", prompt_tokens=-1)

    def test_inconsistent_total_tokens_rejected(self) -> None:
        """total_tokens must equal prompt_tokens + completion_tokens."""
        with pytest.raises(ValidationError, match="total_tokens"):
            ContractLlmCallMetrics(
                model_id="x",
                prompt_tokens=100,
                completion_tokens=50,
                total_tokens=999,
            )

    def test_negative_cost_rejected(self) -> None:
        """Negative cost must be rejected by ge=0.0 constraint."""
        with pytest.raises(ValidationError):
            ContractLlmCallMetrics(model_id="x", estimated_cost_usd=-0.01)

    def test_negative_latency_rejected(self) -> None:
        """Negative latency must be rejected by ge=0.0 constraint."""
        with pytest.raises(ValidationError):
            ContractLlmCallMetrics(model_id="x", latency_ms=-1.0)

    def test_frozen(self) -> None:
        """Frozen model must reject attribute mutation."""
        m = ContractLlmCallMetrics(model_id="gpt-4o")
        with pytest.raises(ValidationError):
            m.model_id = "changed"  # type: ignore[misc]

    def test_extra_fields_rejected(self) -> None:
        """Extra fields must be rejected by extra='forbid'."""
        with pytest.raises(ValidationError, match="extra_forbidden"):
            ContractLlmCallMetrics(
                model_id="gpt-4o",
                nope="rejected",  # type: ignore[call-arg]
            )

    def test_json_round_trip(self) -> None:
        """JSON serialization must produce an equivalent instance."""
        m = ContractLlmCallMetrics(
            model_id="claude-opus-4-20250514",
            prompt_tokens=1000,
            completion_tokens=500,
            total_tokens=1500,
            estimated_cost_usd=0.045,
            latency_ms=3200.0,
            input_hash="sha256-abc",
            code_version="0.8.0",
            timestamp_iso="2026-02-15T12:00:00Z",
            source="test",
        )
        j = m.model_dump_json()
        m2 = ContractLlmCallMetrics.model_validate_json(j)
        assert m == m2

    def test_dict_round_trip_via_json_str(self) -> None:
        """JSON string parsed back to dict then validated must round-trip."""
        m = ContractLlmCallMetrics(
            model_id="gpt-4o",
            prompt_tokens=100,
            total_tokens=100,
            usage_normalized=ContractLlmUsageNormalized(
                prompt_tokens=100,
                total_tokens=100,
                source=ContractEnumUsageSource.API,
                usage_is_estimated=False,
            ),
        )
        j_str = m.model_dump_json()
        d = json.loads(j_str)
        m2 = ContractLlmCallMetrics.model_validate(d)
        assert m == m2

    def test_with_nested_usage_round_trip(self) -> None:
        """Full round-trip with both raw and normalized usage."""
        raw = ContractLlmUsageRaw(
            provider="anthropic",
            raw_data={"input_tokens": 300, "output_tokens": 150},
        )
        norm = ContractLlmUsageNormalized(
            prompt_tokens=300,
            completion_tokens=150,
            total_tokens=450,
            source=ContractEnumUsageSource.API,
            usage_is_estimated=False,
        )
        m = ContractLlmCallMetrics(
            model_id="claude-opus-4-20250514",
            prompt_tokens=300,
            completion_tokens=150,
            total_tokens=450,
            estimated_cost_usd=0.03,
            latency_ms=2500.0,
            usage_raw=raw,
            usage_normalized=norm,
            input_hash="sha256-xyz",
            code_version="1.0.0",
            contract_version="1.0",
            timestamp_iso="2026-02-15T14:00:00Z",
            source="integration-test",
        )
        j = m.model_dump_json()
        m2 = ContractLlmCallMetrics.model_validate_json(j)
        assert m == m2
        assert m2.usage_raw is not None
        assert m2.usage_raw.provider == "anthropic"
        assert m2.usage_normalized is not None
        assert m2.usage_normalized.source == ContractEnumUsageSource.API

    def test_global_invariant_fields_present(self) -> None:
        """All global invariant fields must exist on the contract."""
        m = ContractLlmCallMetrics(model_id="test-model")
        # Global invariants: input_hash, code_version, contract_version,
        # timestamp, source
        assert hasattr(m, "input_hash")
        assert hasattr(m, "code_version")
        assert hasattr(m, "contract_version")
        assert hasattr(m, "timestamp_iso")
        assert hasattr(m, "source")


# ---------------------------------------------------------------------------
# Module-level import tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestLlmCostTrackingImports:
    """Tests that all new contracts are importable from package __init__ modules."""

    def test_import_from_measurement_init(self) -> None:
        """All new types must be importable from the measurement package."""
        from omnibase_spi.contracts.measurement import (
            ContractEnumUsageSource,
            ContractLlmCallMetrics,
            ContractLlmUsageNormalized,
            ContractLlmUsageRaw,
        )

        assert ContractEnumUsageSource.API == "api"
        assert ContractLlmCallMetrics is not None
        assert ContractLlmUsageNormalized is not None
        assert ContractLlmUsageRaw is not None

    def test_import_from_contracts_init(self) -> None:
        """All new types must be importable from the contracts package."""
        from omnibase_spi.contracts import (
            ContractEnumUsageSource,
            ContractLlmCallMetrics,
            ContractLlmUsageNormalized,
            ContractLlmUsageRaw,
        )

        assert ContractEnumUsageSource.ESTIMATED == "estimated"
        assert ContractLlmCallMetrics is not None
        assert ContractLlmUsageNormalized is not None
        assert ContractLlmUsageRaw is not None
