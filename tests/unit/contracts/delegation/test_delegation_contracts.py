"""Tests for delegation contracts.

Covers:
- ContractAttachment: frozen, extra=forbid, required fields, defaults
- ContractComplianceResult: frozen, extra=forbid, required fields, score bounds
- ContractDelegationAttribution: frozen, extra=forbid, required fields, confidence bounds
- ContractDelegatedResponse: frozen, extra=forbid, composition, JSON round-trip
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from omnibase_spi.contracts.delegation.contract_attachment import (
    ContractAttachment,
)
from omnibase_spi.contracts.delegation.contract_compliance_result import (
    ContractComplianceResult,
)
from omnibase_spi.contracts.delegation.contract_delegated_response import (
    ContractDelegatedResponse,
)
from omnibase_spi.contracts.delegation.contract_delegation_attribution import (
    ContractDelegationAttribution,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_attribution(**overrides: object) -> ContractDelegationAttribution:
    """Build a minimal valid ContractDelegationAttribution."""
    defaults: dict[str, object] = {
        "model_name": "qwen2.5-coder-14b",
        "endpoint_url": "http://192.168.86.201:8000",
        "latency_ms": 42.5,
        "delegation_confidence": 0.95,
    }
    defaults.update(overrides)
    return ContractDelegationAttribution(**defaults)  # type: ignore[arg-type]


def _make_response(**overrides: object) -> ContractDelegatedResponse:
    """Build a minimal valid ContractDelegatedResponse."""
    defaults: dict[str, object] = {
        "rendered_text": "# Hello\n\nWorld",
        "attribution": _make_attribution(),
    }
    defaults.update(overrides)
    return ContractDelegatedResponse(**defaults)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# ContractAttachment
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestContractAttachment:
    """Tests for ContractAttachment."""

    def test_create_minimal(self) -> None:
        att = ContractAttachment(filename="report.pdf")
        assert att.filename == "report.pdf"
        assert att.content_type == "application/octet-stream"
        assert att.content_base64 == ""
        assert att.size_bytes == 0
        assert att.description == ""
        assert att.schema_version == "1.0"
        assert att.extensions == {}

    def test_create_full(self) -> None:
        att = ContractAttachment(
            filename="image.png",
            content_type="image/png",
            content_base64="iVBORw0KGgo=",
            size_bytes=1024,
            description="Screenshot of the dashboard",
            extensions={"source": "capture"},
        )
        assert att.filename == "image.png"
        assert att.content_type == "image/png"
        assert att.content_base64 == "iVBORw0KGgo="
        assert att.size_bytes == 1024
        assert att.description == "Screenshot of the dashboard"
        assert att.extensions == {"source": "capture"}

    def test_frozen(self) -> None:
        att = ContractAttachment(filename="report.pdf")
        with pytest.raises(ValidationError):
            att.filename = "changed.pdf"  # type: ignore[misc]

    def test_extra_fields_rejected(self) -> None:
        with pytest.raises(ValidationError, match="extra_forbidden"):
            ContractAttachment(
                filename="report.pdf",
                unknown_field="rejected",  # type: ignore[call-arg]
            )

    def test_filename_required(self) -> None:
        with pytest.raises(ValidationError):
            ContractAttachment()  # type: ignore[call-arg]

    def test_filename_nonempty(self) -> None:
        with pytest.raises(ValidationError):
            ContractAttachment(filename="")

    def test_size_bytes_nonnegative(self) -> None:
        with pytest.raises(ValidationError):
            ContractAttachment(filename="f.txt", size_bytes=-1)

    def test_json_round_trip(self) -> None:
        att = ContractAttachment(
            filename="data.json",
            content_type="application/json",
            size_bytes=256,
        )
        j = att.model_dump_json()
        att2 = ContractAttachment.model_validate_json(j)
        assert att == att2


# ---------------------------------------------------------------------------
# ContractComplianceResult
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestContractComplianceResult:
    """Tests for ContractComplianceResult."""

    def test_create_minimal(self) -> None:
        cr = ContractComplianceResult(passed=True)
        assert cr.passed is True
        assert cr.gate_name == ""
        assert cr.score == 0.0
        assert cr.threshold == 0.0
        assert cr.verdict == "SKIP"
        assert cr.violations == []
        assert cr.evaluated_at_iso == ""
        assert cr.schema_version == "1.0"
        assert cr.extensions == {}

    def test_create_full(self) -> None:
        cr = ContractComplianceResult(
            passed=False,
            gate_name="syntax-check",
            score=0.6,
            threshold=0.8,
            verdict="FAIL",
            violations=["Missing docstring", "Invalid import"],
            evaluated_at_iso="2026-02-16T10:00:00Z",
            extensions={"gate_version": "2.0"},
        )
        assert cr.passed is False
        assert cr.gate_name == "syntax-check"
        assert cr.score == 0.6
        assert cr.threshold == 0.8
        assert cr.verdict == "FAIL"
        assert len(cr.violations) == 2
        assert cr.evaluated_at_iso == "2026-02-16T10:00:00Z"

    def test_frozen(self) -> None:
        cr = ContractComplianceResult(passed=True)
        with pytest.raises(ValidationError):
            cr.passed = False  # type: ignore[misc]

    def test_extra_fields_rejected(self) -> None:
        with pytest.raises(ValidationError, match="extra_forbidden"):
            ContractComplianceResult(
                passed=True,
                unknown_field="rejected",  # type: ignore[call-arg]
            )

    def test_passed_required(self) -> None:
        with pytest.raises(ValidationError):
            ContractComplianceResult()  # type: ignore[call-arg]

    def test_score_bounds(self) -> None:
        with pytest.raises(ValidationError):
            ContractComplianceResult(passed=True, score=-0.1)
        with pytest.raises(ValidationError):
            ContractComplianceResult(passed=True, score=1.1)

    def test_threshold_bounds(self) -> None:
        with pytest.raises(ValidationError):
            ContractComplianceResult(passed=True, threshold=-0.1)
        with pytest.raises(ValidationError):
            ContractComplianceResult(passed=True, threshold=1.1)

    def test_verdict_literal(self) -> None:
        for v in ("PASS", "FAIL", "WARN", "SKIP"):
            cr = ContractComplianceResult(passed=True, verdict=v)  # type: ignore[arg-type]
            assert cr.verdict == v
        with pytest.raises(ValidationError):
            ContractComplianceResult(passed=True, verdict="INVALID")  # type: ignore[arg-type]

    def test_json_round_trip(self) -> None:
        cr = ContractComplianceResult(
            passed=False,
            gate_name="quality",
            score=0.75,
            threshold=0.8,
            verdict="FAIL",
            violations=["Too many warnings"],
        )
        j = cr.model_dump_json()
        cr2 = ContractComplianceResult.model_validate_json(j)
        assert cr == cr2


# ---------------------------------------------------------------------------
# ContractDelegationAttribution
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestContractDelegationAttribution:
    """Tests for ContractDelegationAttribution."""

    def test_create_minimal(self) -> None:
        attr = _make_attribution()
        assert attr.model_name == "qwen2.5-coder-14b"
        assert attr.endpoint_url == "http://192.168.86.201:8000"
        assert attr.latency_ms == 42.5
        assert attr.delegation_confidence == 0.95
        assert attr.prompt_version == ""
        assert attr.schema_version == "1.0"
        assert attr.extensions == {}

    def test_create_full(self) -> None:
        attr = _make_attribution(
            prompt_version="v2.1",
            extensions={"routing_strategy": "cost-optimized"},
        )
        assert attr.prompt_version == "v2.1"
        assert attr.extensions == {"routing_strategy": "cost-optimized"}

    def test_frozen(self) -> None:
        attr = _make_attribution()
        with pytest.raises(ValidationError):
            attr.model_name = "changed"  # type: ignore[misc]

    def test_extra_fields_rejected(self) -> None:
        with pytest.raises(ValidationError, match="extra_forbidden"):
            ContractDelegationAttribution(
                model_name="m",
                endpoint_url="http://localhost",
                latency_ms=1.0,
                delegation_confidence=0.5,
                unknown_field="rejected",  # type: ignore[call-arg]
            )

    def test_model_name_required(self) -> None:
        with pytest.raises(ValidationError):
            ContractDelegationAttribution(
                endpoint_url="http://localhost",
                latency_ms=1.0,
                delegation_confidence=0.5,
            )  # type: ignore[call-arg]

    def test_model_name_nonempty(self) -> None:
        with pytest.raises(ValidationError):
            ContractDelegationAttribution(
                model_name="",
                endpoint_url="http://localhost",
                latency_ms=1.0,
                delegation_confidence=0.5,
            )

    def test_endpoint_url_required(self) -> None:
        with pytest.raises(ValidationError):
            ContractDelegationAttribution(
                model_name="m",
                latency_ms=1.0,
                delegation_confidence=0.5,
            )  # type: ignore[call-arg]

    def test_endpoint_url_nonempty(self) -> None:
        with pytest.raises(ValidationError):
            ContractDelegationAttribution(
                model_name="m",
                endpoint_url="",
                latency_ms=1.0,
                delegation_confidence=0.5,
            )

    def test_latency_ms_nonnegative(self) -> None:
        with pytest.raises(ValidationError):
            ContractDelegationAttribution(
                model_name="m",
                endpoint_url="http://localhost",
                latency_ms=-1.0,
                delegation_confidence=0.5,
            )

    def test_delegation_confidence_bounds(self) -> None:
        with pytest.raises(ValidationError):
            _make_attribution(delegation_confidence=-0.1)
        with pytest.raises(ValidationError):
            _make_attribution(delegation_confidence=1.1)

    def test_delegation_confidence_edge_values(self) -> None:
        attr_low = _make_attribution(delegation_confidence=0.0)
        assert attr_low.delegation_confidence == 0.0
        attr_high = _make_attribution(delegation_confidence=1.0)
        assert attr_high.delegation_confidence == 1.0

    def test_json_round_trip(self) -> None:
        attr = _make_attribution(prompt_version="v3.0")
        j = attr.model_dump_json()
        attr2 = ContractDelegationAttribution.model_validate_json(j)
        assert attr == attr2


# ---------------------------------------------------------------------------
# ContractDelegatedResponse
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestContractDelegatedResponse:
    """Tests for ContractDelegatedResponse."""

    def test_create_minimal(self) -> None:
        resp = _make_response()
        assert resp.rendered_text == "# Hello\n\nWorld"
        assert resp.attachments == []
        assert resp.structured_json is None
        assert resp.attribution.model_name == "qwen2.5-coder-14b"
        assert resp.quality_gate_result is None
        assert resp.schema_version == "1.0"
        assert resp.extensions == {}

    def test_create_full(self) -> None:
        att = ContractAttachment(
            filename="output.json", content_type="application/json"
        )
        cr = ContractComplianceResult(passed=True, score=0.99, verdict="PASS")
        resp = _make_response(
            attachments=[att],
            structured_json={"key": "value", "nested": {"a": 1}},
            quality_gate_result=cr,
            extensions={"trace_id": "abc-123"},
        )
        assert len(resp.attachments) == 1
        assert resp.attachments[0].filename == "output.json"
        assert resp.structured_json == {"key": "value", "nested": {"a": 1}}
        assert resp.quality_gate_result is not None
        assert resp.quality_gate_result.passed is True
        assert resp.extensions == {"trace_id": "abc-123"}

    def test_frozen(self) -> None:
        resp = _make_response()
        with pytest.raises(ValidationError):
            resp.rendered_text = "changed"  # type: ignore[misc]

    def test_extra_fields_rejected(self) -> None:
        with pytest.raises(ValidationError, match="extra_forbidden"):
            ContractDelegatedResponse(
                rendered_text="text",
                attribution=_make_attribution(),
                unknown_field="rejected",  # type: ignore[call-arg]
            )

    def test_rendered_text_required(self) -> None:
        with pytest.raises(ValidationError):
            ContractDelegatedResponse(
                attribution=_make_attribution(),
            )  # type: ignore[call-arg]

    def test_rendered_text_nonempty(self) -> None:
        with pytest.raises(ValidationError):
            ContractDelegatedResponse(
                rendered_text="",
                attribution=_make_attribution(),
            )

    def test_attribution_required(self) -> None:
        with pytest.raises(ValidationError):
            ContractDelegatedResponse(
                rendered_text="text",
            )  # type: ignore[call-arg]

    def test_json_round_trip(self) -> None:
        att = ContractAttachment(filename="f.txt", size_bytes=10)
        cr = ContractComplianceResult(passed=False, verdict="FAIL", violations=["v1"])
        resp = ContractDelegatedResponse(
            rendered_text="# Report\n\nDetails here.",
            attachments=[att],
            structured_json={"summary": "ok"},
            attribution=_make_attribution(prompt_version="v1.0"),
            quality_gate_result=cr,
            extensions={"run_id": "run-42"},
        )
        j = resp.model_dump_json()
        resp2 = ContractDelegatedResponse.model_validate_json(j)
        assert resp == resp2

    def test_multiple_attachments(self) -> None:
        atts = [
            ContractAttachment(filename="a.txt"),
            ContractAttachment(filename="b.png", content_type="image/png"),
            ContractAttachment(filename="c.json", content_type="application/json"),
        ]
        resp = _make_response(attachments=atts)
        assert len(resp.attachments) == 3
        assert resp.attachments[0].filename == "a.txt"
        assert resp.attachments[2].content_type == "application/json"

    def test_nested_frozen_attribution(self) -> None:
        """Verify that the nested attribution object is also frozen."""
        resp = _make_response()
        with pytest.raises(ValidationError):
            resp.attribution.model_name = "changed"  # type: ignore[misc]

    def test_nested_frozen_quality_gate(self) -> None:
        """Verify that the nested quality gate object is also frozen."""
        cr = ContractComplianceResult(passed=True)
        resp = _make_response(quality_gate_result=cr)
        assert resp.quality_gate_result is not None
        with pytest.raises(ValidationError):
            resp.quality_gate_result.passed = False  # type: ignore[misc]

    def test_nested_frozen_attachment(self) -> None:
        """Verify that nested attachment objects are also frozen."""
        att = ContractAttachment(filename="f.txt")
        resp = _make_response(attachments=[att])
        with pytest.raises(ValidationError):
            resp.attachments[0].filename = "changed"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Package-level imports
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestPackageExports:
    """Verify delegation contracts are importable from the contracts package."""

    def test_import_from_contracts_package(self) -> None:
        from omnibase_spi.contracts import (
            ContractAttachment,
            ContractComplianceResult,
            ContractDelegatedResponse,
            ContractDelegationAttribution,
        )

        assert ContractAttachment is not None
        assert ContractComplianceResult is not None
        assert ContractDelegatedResponse is not None
        assert ContractDelegationAttribution is not None

    def test_import_from_delegation_subpackage(self) -> None:
        from omnibase_spi.contracts.delegation import (
            ContractAttachment,
            ContractComplianceResult,
            ContractDelegatedResponse,
            ContractDelegationAttribution,
        )

        assert ContractAttachment is not None
        assert ContractComplianceResult is not None
        assert ContractDelegatedResponse is not None
        assert ContractDelegationAttribution is not None
