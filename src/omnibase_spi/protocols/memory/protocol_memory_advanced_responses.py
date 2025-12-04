"""
Advanced Memory Response Protocols for OmniMemory ONEX Architecture

This module defines advanced response protocols including batch operations,
streaming responses, and workflow coordination. Split from protocol_memory_responses.py
to maintain the 15-protocol limit.

Contains:
    - Batch operation response protocols
    - Streaming response protocols
    - Workflow and coordination response protocols
    - Metrics response protocols

All types are pure protocols with no implementation dependencies.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, AsyncIterator, Protocol, runtime_checkable
from uuid import UUID

if TYPE_CHECKING:
    from datetime import datetime

    from omnibase_spi.protocols.memory.protocol_memory_base import (
        ProtocolMemoryRecord,
    )
    from omnibase_spi.protocols.memory.protocol_memory_data_types import (
        ProtocolAgentResponseMap,
        ProtocolAgentStatusMap,
        ProtocolAggregatedData,
        ProtocolAggregationSummary,
        ProtocolAnalysisResults,
        ProtocolCustomMetrics,
        ProtocolPageInfo,
    )
    from omnibase_spi.protocols.memory.protocol_memory_responses import (
        ProtocolMemoryMetadata,
    )

from omnibase_spi.protocols.memory.protocol_memory_errors import ProtocolMemoryError


@runtime_checkable
class ProtocolBatchOperationResult(Protocol):
    """Protocol for individual batch operation results."""

    operation_index: int
    success: bool
    result_id: UUID | None
    error: "ProtocolMemoryError | None"

    @property
    def execution_time_ms(self) -> int: ...


@runtime_checkable
class ProtocolBatchMemoryStoreResponse(Protocol):
    """Protocol for batch memory storage responses."""

    correlation_id: UUID | None
    response_timestamp: "datetime"
    success: bool
    results: list["ProtocolBatchOperationResult"]
    total_processed: int
    successful_count: int
    failed_count: int
    batch_execution_time_ms: int

    @property
    def error_message(self) -> str | None: ...

    @property
    def partial_success(self) -> bool: ...


@runtime_checkable
class ProtocolBatchMemoryRetrieveResponse(Protocol):
    """Protocol for batch memory retrieval responses."""

    correlation_id: UUID | None
    response_timestamp: "datetime"
    success: bool
    results: list["ProtocolBatchOperationResult"]
    memories: list["ProtocolMemoryRecord"]
    missing_ids: list[UUID]
    batch_execution_time_ms: int

    @property
    def error_message(self) -> str | None: ...


@runtime_checkable
class ProtocolPatternAnalysisResponse(Protocol):
    """Protocol for pattern analysis responses."""

    correlation_id: UUID | None
    response_timestamp: "datetime"
    success: bool
    patterns_found: int
    analysis_results: "ProtocolAnalysisResults"

    @property
    def error_message(self) -> str | None: ...

    @property
    def confidence_scores(self) -> list[float]: ...


@runtime_checkable
class ProtocolConsolidationResponse(Protocol):
    """Protocol for memory consolidation responses."""

    correlation_id: UUID | None
    response_timestamp: "datetime"
    success: bool
    consolidated_memory_id: UUID
    source_memory_ids: list[UUID]

    @property
    def error_message(self) -> str | None: ...


@runtime_checkable
class ProtocolAggregationResponse(Protocol):
    """Protocol for memory aggregation responses."""

    correlation_id: UUID | None
    response_timestamp: "datetime"
    success: bool
    aggregated_data: "ProtocolAggregatedData"
    aggregation_metadata: "ProtocolMemoryMetadata"

    @property
    def error_message(self) -> str | None: ...


@runtime_checkable
class ProtocolWorkflowExecutionResponse(Protocol):
    """Protocol for workflow execution responses."""

    correlation_id: UUID | None
    response_timestamp: "datetime"
    success: bool
    workflow_id: UUID
    execution_status: str

    @property
    def error_message(self) -> str | None: ...

    @property
    def agent_statuses(self) -> "ProtocolAgentStatusMap": ...


@runtime_checkable
class ProtocolAgentCoordinationResponse(Protocol):
    """Protocol for agent coordination responses."""

    correlation_id: UUID | None
    response_timestamp: "datetime"
    success: bool
    coordination_id: UUID
    coordination_status: str

    @property
    def error_message(self) -> str | None: ...

    async def agent_responses(self) -> "ProtocolAgentResponseMap": ...


@runtime_checkable
class ProtocolPaginationResponse(Protocol):
    """Protocol for paginated response metadata."""

    total_count: int
    has_next_page: bool
    has_previous_page: bool
    next_cursor: str | None
    previous_cursor: str | None

    @property
    def page_info(self) -> "ProtocolPageInfo": ...


@runtime_checkable
class ProtocolMemoryMetrics(Protocol):
    """Protocol for memory system performance metrics."""

    operation_type: str
    execution_time_ms: int
    memory_usage_mb: float
    timestamp: "datetime"

    async def throughput_ops_per_second(self) -> float: ...

    @property
    def error_rate_percent(self) -> float: ...

    @property
    def custom_metrics(self) -> "ProtocolCustomMetrics": ...


@runtime_checkable
class ProtocolMemoryMetricsResponse(Protocol):
    """Protocol for metrics collection responses."""

    correlation_id: UUID | None
    response_timestamp: "datetime"
    success: bool
    metrics: list["ProtocolMemoryMetrics"]
    aggregation_summary: "ProtocolAggregationSummary"
    collection_timestamp: "datetime"

    @property
    def error_message(self) -> str | None: ...


@runtime_checkable
class ProtocolStreamingMemoryResponse(Protocol):
    """Protocol for streaming memory operation responses."""

    correlation_id: UUID | None
    response_timestamp: "datetime"
    success: bool
    stream_id: UUID
    chunk_count: int
    total_size_bytes: int

    @property
    def error_message(self) -> str | None: ...

    async def stream_content(self) -> AsyncIterator[bytes]: ...

    @property
    def compression_ratio(self) -> float | None: ...


@runtime_checkable
class ProtocolStreamingRetrieveResponse(Protocol):
    """Protocol for streaming memory retrieval responses."""

    correlation_id: UUID | None
    response_timestamp: "datetime"
    success: bool
    stream_id: UUID
    chunk_count: int
    total_size_bytes: int
    memory_metadata: list["ProtocolMemoryRecord"]

    @property
    def error_message(self) -> str | None: ...

    @property
    def compression_ratio(self) -> float | None: ...

    async def stream_content(self) -> AsyncIterator[bytes]: ...

    async def stream_memory_content(self, memory_id: UUID) -> AsyncIterator[bytes]: ...
