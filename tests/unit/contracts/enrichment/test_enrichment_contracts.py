"""Tests for enrichment contracts.

Covers:
- ContractEnrichmentResult: frozen, extra=forbid, required fields, bounds,
  enrichment_type literal, JSON round-trip
"""

from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from omnibase_spi.contracts.enrichment.contract_enrichment_result import (
    ContractEnrichmentResult,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_result(**overrides: Any) -> ContractEnrichmentResult:
    """Build a minimal valid ContractEnrichmentResult."""
    defaults: dict[str, object] = {
        "summary_markdown": "## Summary\n\nRelevant context extracted.",
        "token_count": 150,
        "relevance_score": 0.85,
        "enrichment_type": "code_analysis",
        "latency_ms": 42.5,
        "model_used": "qwen2.5-72b",
        "prompt_version": "v1.0",
    }
    defaults.update(overrides)
    return ContractEnrichmentResult(**defaults)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# ContractEnrichmentResult
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestContractEnrichmentResult:
    """Tests for ContractEnrichmentResult."""

    def test_create_minimal(self) -> None:
        result = _make_result()
        assert result.summary_markdown == "## Summary\n\nRelevant context extracted."
        assert result.token_count == 150
        assert result.relevance_score == 0.85
        assert result.enrichment_type == "code_analysis"
        assert result.latency_ms == 42.5
        assert result.model_used == "qwen2.5-72b"
        assert result.prompt_version == "v1.0"
        assert result.schema_version == "1.0"
        assert result.extensions == {}

    def test_create_full(self) -> None:
        result = _make_result(
            enrichment_type="similarity",
            extensions={"source": "qdrant", "collection": "code-patterns"},
        )
        assert result.enrichment_type == "similarity"
        assert result.extensions == {
            "source": "qdrant",
            "collection": "code-patterns",
        }

    def test_frozen(self) -> None:
        result = _make_result()
        with pytest.raises(ValidationError):
            result.summary_markdown = "changed"  # type: ignore[misc]

    def test_extra_fields_rejected(self) -> None:
        with pytest.raises(ValidationError, match="extra_forbidden"):
            ContractEnrichmentResult(
                summary_markdown="text",
                token_count=100,
                relevance_score=0.5,
                enrichment_type="code_analysis",
                latency_ms=10.0,
                model_used="model",
                prompt_version="v1",
                unknown_field="rejected",  # type: ignore[call-arg]
            )

    def test_summary_markdown_required(self) -> None:
        with pytest.raises(ValidationError):
            ContractEnrichmentResult(
                token_count=100,
                relevance_score=0.5,
                enrichment_type="code_analysis",
                latency_ms=10.0,
                model_used="model",
                prompt_version="v1",
            )  # type: ignore[call-arg]

    def test_summary_markdown_nonempty(self) -> None:
        with pytest.raises(ValidationError):
            _make_result(summary_markdown="")

    def test_token_count_required(self) -> None:
        with pytest.raises(ValidationError):
            ContractEnrichmentResult(
                summary_markdown="text",
                relevance_score=0.5,
                enrichment_type="code_analysis",
                latency_ms=10.0,
                model_used="model",
                prompt_version="v1",
            )  # type: ignore[call-arg]

    def test_token_count_nonnegative(self) -> None:
        with pytest.raises(ValidationError):
            _make_result(token_count=-1)

    def test_token_count_zero_allowed(self) -> None:
        result = _make_result(token_count=0)
        assert result.token_count == 0

    def test_relevance_score_required(self) -> None:
        with pytest.raises(ValidationError):
            ContractEnrichmentResult(
                summary_markdown="text",
                token_count=100,
                enrichment_type="code_analysis",
                latency_ms=10.0,
                model_used="model",
                prompt_version="v1",
            )  # type: ignore[call-arg]

    def test_relevance_score_bounds(self) -> None:
        with pytest.raises(ValidationError):
            _make_result(relevance_score=-0.1)
        with pytest.raises(ValidationError):
            _make_result(relevance_score=1.1)

    def test_relevance_score_edge_values(self) -> None:
        low = _make_result(relevance_score=0.0)
        assert low.relevance_score == 0.0
        high = _make_result(relevance_score=1.0)
        assert high.relevance_score == 1.0

    def test_enrichment_type_literal(self) -> None:
        for et in ("code_analysis", "similarity", "summarization"):
            result = _make_result(enrichment_type=et)
            assert result.enrichment_type == et

    def test_enrichment_type_invalid(self) -> None:
        with pytest.raises(ValidationError):
            _make_result(enrichment_type="invalid_type")

    def test_latency_ms_required(self) -> None:
        with pytest.raises(ValidationError):
            ContractEnrichmentResult(
                summary_markdown="text",
                token_count=100,
                relevance_score=0.5,
                enrichment_type="code_analysis",
                model_used="model",
                prompt_version="v1",
            )  # type: ignore[call-arg]

    def test_latency_ms_nonnegative(self) -> None:
        with pytest.raises(ValidationError):
            _make_result(latency_ms=-1.0)

    def test_latency_ms_zero_allowed(self) -> None:
        result = _make_result(latency_ms=0.0)
        assert result.latency_ms == 0.0

    def test_model_used_required(self) -> None:
        with pytest.raises(ValidationError):
            ContractEnrichmentResult(
                summary_markdown="text",
                token_count=100,
                relevance_score=0.5,
                enrichment_type="code_analysis",
                latency_ms=10.0,
                prompt_version="v1",
            )  # type: ignore[call-arg]

    def test_model_used_nonempty(self) -> None:
        with pytest.raises(ValidationError):
            _make_result(model_used="")

    def test_prompt_version_required(self) -> None:
        with pytest.raises(ValidationError):
            ContractEnrichmentResult(
                summary_markdown="text",
                token_count=100,
                relevance_score=0.5,
                enrichment_type="code_analysis",
                latency_ms=10.0,
                model_used="model",
            )  # type: ignore[call-arg]

    def test_prompt_version_nonempty(self) -> None:
        with pytest.raises(ValidationError):
            _make_result(prompt_version="")

    def test_json_round_trip(self) -> None:
        result = _make_result(
            enrichment_type="summarization",
            extensions={"trace_id": "abc-123"},
        )
        j = result.model_dump_json()
        result2 = ContractEnrichmentResult.model_validate_json(j)
        assert result == result2

    def test_schema_version_default(self) -> None:
        result = _make_result()
        assert result.schema_version == "1.0"

    def test_schema_version_custom(self) -> None:
        result = _make_result(schema_version="2.0")
        assert result.schema_version == "2.0"

    def test_extensions_default_empty(self) -> None:
        result = _make_result()
        assert result.extensions == {}

    def test_extensions_with_data(self) -> None:
        result = _make_result(extensions={"nested": {"key": "value"}, "count": 42})
        assert result.extensions["nested"] == {"key": "value"}
        assert result.extensions["count"] == 42


# ---------------------------------------------------------------------------
# Protocol compliance
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestProtocolContextEnrichment:
    """Tests for ProtocolContextEnrichment protocol compliance."""

    def test_protocol_is_runtime_checkable(self) -> None:
        from omnibase_spi.protocols.intelligence.protocol_context_enrichment import (
            ProtocolContextEnrichment,
        )

        class _ConformingEnricher:
            async def enrich(
                self, prompt: str, context: str
            ) -> ContractEnrichmentResult:
                return ContractEnrichmentResult(
                    summary_markdown="test",
                    token_count=0,
                    relevance_score=0.5,
                    enrichment_type="code_analysis",
                    latency_ms=1.0,
                    model_used="test-model",
                    prompt_version="1.0",
                )

        assert isinstance(_ConformingEnricher(), ProtocolContextEnrichment)

    def test_protocol_has_enrich_method(self) -> None:
        from omnibase_spi.protocols.intelligence.protocol_context_enrichment import (
            ProtocolContextEnrichment,
        )

        # Verify the protocol defines the enrich method and it is callable
        assert callable(getattr(ProtocolContextEnrichment, "enrich", None))


# ---------------------------------------------------------------------------
# Package-level imports
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestPackageExports:
    """Verify enrichment contracts are importable from the contracts package."""

    def test_import_from_contracts_package(self) -> None:
        from omnibase_spi.contracts import ContractEnrichmentResult

        assert ContractEnrichmentResult is not None

    def test_import_from_enrichment_subpackage(self) -> None:
        from omnibase_spi.contracts.enrichment import ContractEnrichmentResult

        assert ContractEnrichmentResult is not None

    def test_import_protocol_from_intelligence_package(self) -> None:
        from omnibase_spi.protocols.intelligence import ProtocolContextEnrichment

        assert ProtocolContextEnrichment is not None

    def test_import_protocol_from_protocols_package(self) -> None:
        from omnibase_spi.protocols import ProtocolContextEnrichment

        assert ProtocolContextEnrichment is not None
