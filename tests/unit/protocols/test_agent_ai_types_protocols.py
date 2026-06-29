# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Unit tests for protocol_agent_ai_types.py.

Covers the 6 @runtime_checkable Protocol classes:
    ProtocolAgentAction, ProtocolAIExecutionMetrics,
    ProtocolAgentDebugIntelligence, ProtocolPRTicket,
    ProtocolVelocityLog, ProtocolIntelligenceResult.

Also covers ProtocolRetrievalOutputState.query async method
from protocol_semantic_types (cross-module async verification).

Ticket: OMN-13745
"""

from __future__ import annotations

import importlib
import inspect
from typing import Any, Protocol, get_type_hints
from uuid import UUID, uuid4

import pytest

from omnibase_spi.protocols.types.protocol_agent_ai_types import (
    LiteralActionType,
    ProtocolAgentAction,
    ProtocolAgentDebugIntelligence,
    ProtocolAIExecutionMetrics,
    ProtocolIntelligenceResult,
    ProtocolPRTicket,
    ProtocolVelocityLog,
)
from omnibase_spi.protocols.types.protocol_semantic_types import (
    ProtocolRetrievalOutputState,
)

MODULE_NAME = "omnibase_spi.protocols.types.protocol_agent_ai_types"
_agent_ai_mod = importlib.import_module(MODULE_NAME)

# ---------------------------------------------------------------------------
# Minimal conforming stubs
# ---------------------------------------------------------------------------


class _ConformingAgentAction:
    """Minimal stub satisfying ProtocolAgentAction."""

    @property
    def action_id(self) -> str:
        return "action-001"

    @property
    def action_type(self) -> str:
        return "query"

    @property
    def parameters(self) -> dict[str, Any]:
        return {"table": "users"}

    @property
    def timeout_ms(self) -> int:
        return 5000

    @property
    def retry_count(self) -> int:
        return 3

    @property
    def required_capabilities(self) -> list[str]:
        return ["database_read"]


class _ConformingAIMetrics:
    """Minimal stub satisfying ProtocolAIExecutionMetrics."""

    @property
    def execution_id(self) -> UUID:
        return uuid4()

    @property
    def model_name(self) -> str:
        return "test-model"

    async def input_tokens(self) -> int:
        return 100

    async def output_tokens(self) -> int:
        return 50

    @property
    def execution_time_ms(self) -> int:
        return 1200

    @property
    def cost_estimate_usd(self) -> float:
        return 0.002

    @property
    def success(self) -> bool:
        return True


class _ConformingDebugIntelligence:
    """Minimal stub satisfying ProtocolAgentDebugIntelligence."""

    def __init__(self) -> None:
        self._metrics = _ConformingAIMetrics()

    @property
    def session_id(self) -> UUID:
        return uuid4()

    @property
    def agent_name(self) -> str:
        return "coding-assistant"

    @property
    def debug_data(self) -> dict[str, Any]:
        return {"last_action": "code_review"}

    @property
    def performance_metrics(self) -> _ConformingAIMetrics:
        return self._metrics

    @property
    def error_logs(self) -> list[str]:
        return []

    @property
    def suggestions(self) -> list[str]:
        return ["batch requests"]


class _ConformingPRTicket:
    """Minimal stub satisfying ProtocolPRTicket."""

    @property
    def ticket_id(self) -> str:
        return "PR-001"

    @property
    def title(self) -> str:
        return "Fix null pointer"

    @property
    def description(self) -> str:
        return "Detailed description"

    @property
    def priority(self) -> str:
        return "high"

    @property
    def status(self) -> str:
        return "open"

    @property
    def assignee(self) -> str:
        return "alice"


class _ConformingVelocityLog:
    """Minimal stub satisfying ProtocolVelocityLog."""

    @property
    def log_id(self) -> UUID:
        return uuid4()

    @property
    def timestamp(self) -> str:
        return "2026-01-01T00:00:00Z"

    @property
    def metric_name(self) -> str:
        return "sprint_velocity"

    @property
    def value(self) -> float:
        return 42.0

    @property
    def unit(self) -> str:
        return "story_points"

    @property
    def tags(self) -> list[str]:
        return ["team-alpha"]


class _ConformingIntelligenceResult:
    """Minimal stub satisfying ProtocolIntelligenceResult."""

    @property
    def analysis_id(self) -> UUID:
        return uuid4()

    @property
    def confidence_score(self) -> float:
        return 0.92

    @property
    def entities(self) -> list[dict[str, Any]]:
        return [{"type": "PERSON", "text": "Alice"}]

    @property
    def sentiment_score(self) -> float | None:
        return 0.65

    @property
    def language_detected(self) -> str | None:
        return "en"

    @property
    def processing_metadata(self) -> dict[str, Any]:
        return {"model_version": "v1.0"}


class _ConformingRetrievalOutputState:
    """Minimal stub satisfying ProtocolRetrievalOutputState."""

    @property
    def results(self) -> list[Any]:
        return []

    @property
    def total_results(self) -> int:
        return 0

    async def query(self) -> str:
        return "test query"

    @property
    def metadata(self) -> dict[str, Any]:
        return {}

    @property
    def retrieval_time_ms(self) -> int:
        return 50

    @property
    def search_strategy(self) -> str:
        return "hybrid"


class _NonConforming:
    """Empty class — satisfies no Protocol."""


# ---------------------------------------------------------------------------
# Test: module import and __all__
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestModuleImport:
    """Verify module-level attributes are importable and correct."""

    def test_clean_import(self) -> None:
        """Module imports without error and exposes expected names."""
        mod = importlib.import_module(MODULE_NAME)

        assert mod is not None

    def test_all_contains_all_six_protocols(self) -> None:
        """__all__ includes all 6 Protocol class names."""
        expected = {
            "ProtocolAgentAction",
            "ProtocolAIExecutionMetrics",
            "ProtocolAgentDebugIntelligence",
            "ProtocolPRTicket",
            "ProtocolVelocityLog",
            "ProtocolIntelligenceResult",
        }
        module_all = getattr(_agent_ai_mod, "__all__", [])
        assert expected.issubset(set(module_all))

    def test_literal_action_type_alias_is_str(self) -> None:
        """LiteralActionType is an alias for str."""
        assert LiteralActionType is str


# ---------------------------------------------------------------------------
# Test: ProtocolAgentAction
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestProtocolAgentAction:
    """Tests for ProtocolAgentAction interface."""

    def test_is_protocol(self) -> None:
        assert issubclass(ProtocolAgentAction, Protocol)

    def test_is_runtime_checkable(self) -> None:
        # runtime_checkable protocols have _is_protocol = True and allow isinstance
        assert getattr(ProtocolAgentAction, "_is_protocol", False) is True

    def test_conforming_stub_passes_isinstance(self) -> None:
        stub = _ConformingAgentAction()
        assert isinstance(stub, ProtocolAgentAction)

    def test_non_conforming_fails_isinstance(self) -> None:
        obj = _NonConforming()
        assert not isinstance(obj, ProtocolAgentAction)

    def test_stub_action_id_returns_str(self) -> None:
        stub = _ConformingAgentAction()
        result = stub.action_id
        assert isinstance(result, str)
        assert result == "action-001"

    def test_stub_action_type_returns_str(self) -> None:
        stub = _ConformingAgentAction()
        assert isinstance(stub.action_type, str)

    def test_stub_timeout_ms_returns_int(self) -> None:
        stub = _ConformingAgentAction()
        assert isinstance(stub.timeout_ms, int)
        assert stub.timeout_ms > 0

    def test_stub_retry_count_returns_int(self) -> None:
        stub = _ConformingAgentAction()
        assert isinstance(stub.retry_count, int)
        assert stub.retry_count >= 0

    def test_stub_required_capabilities_is_list(self) -> None:
        stub = _ConformingAgentAction()
        caps = stub.required_capabilities
        assert isinstance(caps, list)
        assert all(isinstance(c, str) for c in caps)

    def test_parameters_is_dict(self) -> None:
        stub = _ConformingAgentAction()
        assert isinstance(stub.parameters, dict)

    def test_protocol_attrs_present(self) -> None:
        for attr in (
            "action_id",
            "action_type",
            "parameters",
            "timeout_ms",
            "retry_count",
            "required_capabilities",
        ):
            assert hasattr(ProtocolAgentAction, attr), f"missing protocol attr: {attr}"


# ---------------------------------------------------------------------------
# Test: ProtocolAIExecutionMetrics
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestProtocolAIExecutionMetrics:
    """Tests for ProtocolAIExecutionMetrics interface."""

    def test_is_protocol(self) -> None:
        assert issubclass(ProtocolAIExecutionMetrics, Protocol)

    def test_conforming_stub_passes_isinstance(self) -> None:
        stub = _ConformingAIMetrics()
        assert isinstance(stub, ProtocolAIExecutionMetrics)

    def test_non_conforming_fails_isinstance(self) -> None:
        assert not isinstance(_NonConforming(), ProtocolAIExecutionMetrics)

    def test_input_tokens_is_coroutinefunction(self) -> None:
        """input_tokens must be declared async on the Protocol."""
        assert inspect.iscoroutinefunction(ProtocolAIExecutionMetrics.input_tokens)

    def test_output_tokens_is_coroutinefunction(self) -> None:
        """output_tokens must be declared async on the Protocol."""
        assert inspect.iscoroutinefunction(ProtocolAIExecutionMetrics.output_tokens)

    def test_stub_input_tokens_is_coroutinefunction(self) -> None:
        stub = _ConformingAIMetrics()
        assert inspect.iscoroutinefunction(stub.input_tokens)

    def test_stub_output_tokens_is_coroutinefunction(self) -> None:
        stub = _ConformingAIMetrics()
        assert inspect.iscoroutinefunction(stub.output_tokens)

    def test_execution_id_return_type_hint_is_uuid(self) -> None:
        """execution_id property return type hint must be UUID.

        For Protocol @property members, the return annotation lives on the
        property's fget function, not on the class __annotations__ dict.
        """
        prop = ProtocolAIExecutionMetrics.execution_id  # type: ignore[attr-defined]
        assert isinstance(prop, property), "execution_id must be a property descriptor"
        hints = get_type_hints(prop.fget)  # type: ignore[arg-type]
        assert hints.get("return") is UUID

    def test_cost_estimate_usd_return_type_hint_is_float(self) -> None:
        """cost_estimate_usd property return type hint must be float."""
        prop = ProtocolAIExecutionMetrics.cost_estimate_usd  # type: ignore[attr-defined]
        assert isinstance(prop, property)
        hints = get_type_hints(prop.fget)  # type: ignore[arg-type]
        assert hints.get("return") is float

    def test_success_return_type_hint_is_bool(self) -> None:
        """success property return type hint must be bool."""
        prop = ProtocolAIExecutionMetrics.success  # type: ignore[attr-defined]
        assert isinstance(prop, property)
        hints = get_type_hints(prop.fget)  # type: ignore[arg-type]
        assert hints.get("return") is bool

    def test_stub_execution_id_returns_uuid(self) -> None:
        stub = _ConformingAIMetrics()
        assert isinstance(stub.execution_id, UUID)

    def test_stub_cost_estimate_usd_returns_float(self) -> None:
        stub = _ConformingAIMetrics()
        assert isinstance(stub.cost_estimate_usd, float)
        assert stub.cost_estimate_usd >= 0.0

    def test_stub_success_returns_bool(self) -> None:
        stub = _ConformingAIMetrics()
        assert isinstance(stub.success, bool)

    @pytest.mark.asyncio
    async def test_stub_input_tokens_awaitable_returns_int(self) -> None:
        stub = _ConformingAIMetrics()
        result = await stub.input_tokens()
        assert isinstance(result, int)
        assert result > 0

    @pytest.mark.asyncio
    async def test_stub_output_tokens_awaitable_returns_int(self) -> None:
        stub = _ConformingAIMetrics()
        result = await stub.output_tokens()
        assert isinstance(result, int)
        assert result >= 0


# ---------------------------------------------------------------------------
# Test: ProtocolAgentDebugIntelligence
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestProtocolAgentDebugIntelligence:
    """Tests for ProtocolAgentDebugIntelligence interface."""

    def test_is_protocol(self) -> None:
        assert issubclass(ProtocolAgentDebugIntelligence, Protocol)

    def test_conforming_stub_passes_isinstance(self) -> None:
        stub = _ConformingDebugIntelligence()
        assert isinstance(stub, ProtocolAgentDebugIntelligence)

    def test_non_conforming_fails_isinstance(self) -> None:
        assert not isinstance(_NonConforming(), ProtocolAgentDebugIntelligence)

    def test_performance_metrics_returns_ai_execution_metrics(self) -> None:
        """performance_metrics property must satisfy ProtocolAIExecutionMetrics."""
        stub = _ConformingDebugIntelligence()
        metrics = stub.performance_metrics
        assert isinstance(metrics, ProtocolAIExecutionMetrics)

    def test_stub_session_id_returns_uuid(self) -> None:
        stub = _ConformingDebugIntelligence()
        assert isinstance(stub.session_id, UUID)

    def test_stub_agent_name_returns_str(self) -> None:
        stub = _ConformingDebugIntelligence()
        assert isinstance(stub.agent_name, str)

    def test_stub_debug_data_is_dict(self) -> None:
        stub = _ConformingDebugIntelligence()
        assert isinstance(stub.debug_data, dict)

    def test_stub_error_logs_is_list(self) -> None:
        stub = _ConformingDebugIntelligence()
        assert isinstance(stub.error_logs, list)

    def test_stub_suggestions_is_list(self) -> None:
        stub = _ConformingDebugIntelligence()
        assert isinstance(stub.suggestions, list)

    def test_protocol_attrs_present(self) -> None:
        for attr in (
            "session_id",
            "agent_name",
            "debug_data",
            "performance_metrics",
            "error_logs",
            "suggestions",
        ):
            assert hasattr(ProtocolAgentDebugIntelligence, attr)


# ---------------------------------------------------------------------------
# Test: ProtocolPRTicket
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestProtocolPRTicket:
    """Tests for ProtocolPRTicket interface."""

    def test_is_protocol(self) -> None:
        assert issubclass(ProtocolPRTicket, Protocol)

    def test_conforming_stub_passes_isinstance(self) -> None:
        stub = _ConformingPRTicket()
        assert isinstance(stub, ProtocolPRTicket)

    def test_non_conforming_fails_isinstance(self) -> None:
        assert not isinstance(_NonConforming(), ProtocolPRTicket)

    def test_stub_ticket_id_returns_str(self) -> None:
        stub = _ConformingPRTicket()
        assert isinstance(stub.ticket_id, str)

    def test_stub_title_returns_str(self) -> None:
        stub = _ConformingPRTicket()
        assert isinstance(stub.title, str)

    def test_stub_description_returns_str(self) -> None:
        stub = _ConformingPRTicket()
        assert isinstance(stub.description, str)

    def test_stub_priority_returns_str(self) -> None:
        stub = _ConformingPRTicket()
        assert isinstance(stub.priority, str)

    def test_stub_status_returns_str(self) -> None:
        stub = _ConformingPRTicket()
        assert isinstance(stub.status, str)

    def test_stub_assignee_returns_str(self) -> None:
        stub = _ConformingPRTicket()
        assert isinstance(stub.assignee, str)

    def test_protocol_attrs_present(self) -> None:
        for attr in (
            "ticket_id",
            "title",
            "description",
            "priority",
            "status",
            "assignee",
        ):
            assert hasattr(ProtocolPRTicket, attr)


# ---------------------------------------------------------------------------
# Test: ProtocolVelocityLog
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestProtocolVelocityLog:
    """Tests for ProtocolVelocityLog interface."""

    def test_is_protocol(self) -> None:
        assert issubclass(ProtocolVelocityLog, Protocol)

    def test_conforming_stub_passes_isinstance(self) -> None:
        stub = _ConformingVelocityLog()
        assert isinstance(stub, ProtocolVelocityLog)

    def test_non_conforming_fails_isinstance(self) -> None:
        assert not isinstance(_NonConforming(), ProtocolVelocityLog)

    def test_stub_log_id_returns_uuid(self) -> None:
        stub = _ConformingVelocityLog()
        assert isinstance(stub.log_id, UUID)

    def test_stub_timestamp_returns_str(self) -> None:
        stub = _ConformingVelocityLog()
        assert isinstance(stub.timestamp, str)

    def test_stub_metric_name_returns_str(self) -> None:
        stub = _ConformingVelocityLog()
        assert isinstance(stub.metric_name, str)

    def test_stub_value_returns_float(self) -> None:
        stub = _ConformingVelocityLog()
        result = stub.value
        assert isinstance(result, float)
        assert result > 0.0

    def test_stub_unit_returns_str(self) -> None:
        stub = _ConformingVelocityLog()
        assert isinstance(stub.unit, str)

    def test_stub_tags_is_list_of_str(self) -> None:
        stub = _ConformingVelocityLog()
        tags = stub.tags
        assert isinstance(tags, list)
        assert all(isinstance(t, str) for t in tags)

    def test_protocol_attrs_present(self) -> None:
        for attr in ("log_id", "timestamp", "metric_name", "value", "unit", "tags"):
            assert hasattr(ProtocolVelocityLog, attr)


# ---------------------------------------------------------------------------
# Test: ProtocolIntelligenceResult
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestProtocolIntelligenceResult:
    """Tests for ProtocolIntelligenceResult interface."""

    def test_is_protocol(self) -> None:
        assert issubclass(ProtocolIntelligenceResult, Protocol)

    def test_conforming_stub_passes_isinstance(self) -> None:
        stub = _ConformingIntelligenceResult()
        assert isinstance(stub, ProtocolIntelligenceResult)

    def test_non_conforming_fails_isinstance(self) -> None:
        assert not isinstance(_NonConforming(), ProtocolIntelligenceResult)

    def test_stub_analysis_id_returns_uuid(self) -> None:
        stub = _ConformingIntelligenceResult()
        assert isinstance(stub.analysis_id, UUID)

    def test_stub_confidence_score_returns_float_in_range(self) -> None:
        stub = _ConformingIntelligenceResult()
        score = stub.confidence_score
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_stub_entities_is_list_of_dicts(self) -> None:
        stub = _ConformingIntelligenceResult()
        entities = stub.entities
        assert isinstance(entities, list)
        assert all(isinstance(e, dict) for e in entities)

    def test_stub_sentiment_score_optional_float(self) -> None:
        stub = _ConformingIntelligenceResult()
        score = stub.sentiment_score
        assert score is None or isinstance(score, float)

    def test_stub_language_detected_optional_str(self) -> None:
        stub = _ConformingIntelligenceResult()
        lang = stub.language_detected
        assert lang is None or isinstance(lang, str)

    def test_stub_processing_metadata_is_dict(self) -> None:
        stub = _ConformingIntelligenceResult()
        assert isinstance(stub.processing_metadata, dict)

    def test_protocol_attrs_present(self) -> None:
        for attr in (
            "analysis_id",
            "confidence_score",
            "entities",
            "sentiment_score",
            "language_detected",
            "processing_metadata",
        ):
            assert hasattr(ProtocolIntelligenceResult, attr)


# ---------------------------------------------------------------------------
# Test: ProtocolRetrievalOutputState — async query
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestProtocolRetrievalOutputStateQuery:
    """Verify async nature of ProtocolRetrievalOutputState.query."""

    def test_query_is_declared_async_on_protocol(self) -> None:
        """query must be declared as a coroutinefunction on the Protocol class."""
        assert inspect.iscoroutinefunction(ProtocolRetrievalOutputState.query)

    def test_conforming_stub_query_is_coroutinefunction(self) -> None:
        stub = _ConformingRetrievalOutputState()
        assert inspect.iscoroutinefunction(stub.query)

    @pytest.mark.asyncio
    async def test_stub_query_returns_str(self) -> None:
        stub = _ConformingRetrievalOutputState()
        result = await stub.query()
        assert isinstance(result, str)
