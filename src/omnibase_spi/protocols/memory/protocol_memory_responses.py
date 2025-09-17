"""
Memory Response Protocols for OmniMemory ONEX Architecture

This module defines all response protocol interfaces for memory operations.
Separated from the main types module to prevent circular imports and
improve maintainability.

Contains:
- Base response protocols
- Effect node response protocols
- Compute node response protocols
- Reducer node response protocols
- Orchestrator node response protocols
- Batch operation response protocols
- Streaming response protocols

All types are pure protocols with no implementation dependencies.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, AsyncIterator, Optional, Protocol, runtime_checkable
from uuid import UUID

if TYPE_CHECKING:
    from .protocol_memory_base import (
        ProtocolAgentResponseMap,
        ProtocolAgentStatusMap,
        ProtocolAggregatedData,
        ProtocolAggregationSummary,
        ProtocolAnalysisResults,
        ProtocolCustomMetrics,
        ProtocolMemoryMetadata,
        ProtocolMemoryRecord,
        ProtocolPageInfo,
        ProtocolSearchResult,
    )
    from .protocol_memory_errors import ProtocolMemoryError


# === BASE RESPONSE PROTOCOLS ===


@runtime_checkable
class ProtocolMemoryResponse(Protocol):
    """Base protocol for all memory operation responses."""

    correlation_id: Optional[UUID]
    response_timestamp: datetime
    success: bool

    @property
    def error_message(self) -> Optional[str]:
        """Error message if operation failed."""
        ...


# === EFFECT NODE RESPONSE PROTOCOLS ===


@runtime_checkable
class ProtocolMemoryStoreResponse(ProtocolMemoryResponse, Protocol):
    """Protocol for memory storage responses."""

    memory_id: Optional[UUID]
    storage_location: Optional[str]


@runtime_checkable
class ProtocolMemoryRetrieveResponse(ProtocolMemoryResponse, Protocol):
    """Protocol for memory retrieval responses."""

    memory: Optional["ProtocolMemoryRecord"]

    @property
    def related_memories(self) -> list["ProtocolMemoryRecord"]:
        """Related memory records if requested."""
        ...


@runtime_checkable
class ProtocolMemoryListResponse(ProtocolMemoryResponse, Protocol):
    """Protocol for paginated memory list responses."""

    memories: list["ProtocolMemoryRecord"]
    pagination: "ProtocolPaginationResponse"


@runtime_checkable
class ProtocolBatchOperationResult(Protocol):
    """Protocol for individual batch operation results."""

    operation_index: int
    success: bool
    result_id: Optional[UUID]
    error: Optional["ProtocolMemoryError"]

    @property
    def execution_time_ms(self) -> int:
        """Execution time for this individual operation."""
        ...


@runtime_checkable
class ProtocolBatchMemoryStoreResponse(ProtocolMemoryResponse, Protocol):
    """Protocol for batch memory storage responses."""

    results: list[ProtocolBatchOperationResult]
    total_processed: int
    successful_count: int
    failed_count: int
    batch_execution_time_ms: int

    @property
    def partial_success(self) -> bool:
        """Whether batch had partial success (some operations failed)."""
        ...


@runtime_checkable
class ProtocolBatchMemoryRetrieveResponse(ProtocolMemoryResponse, Protocol):
    """Protocol for batch memory retrieval responses."""

    results: list[ProtocolBatchOperationResult]
    memories: list["ProtocolMemoryRecord"]
    missing_ids: list[UUID]
    batch_execution_time_ms: int


# === COMPUTE NODE RESPONSE PROTOCOLS ===


@runtime_checkable
class ProtocolSemanticSearchResponse(ProtocolMemoryResponse, Protocol):
    """Protocol for semantic search responses."""

    results: list["ProtocolSearchResult"]
    total_matches: int
    search_time_ms: int

    @property
    def query_embedding(self) -> Optional[list[float]]:
        """Query embedding used for search."""
        ...


@runtime_checkable
class ProtocolPatternAnalysisResponse(ProtocolMemoryResponse, Protocol):
    """Protocol for pattern analysis responses."""

    patterns_found: int
    analysis_results: "ProtocolAnalysisResults"

    @property
    def confidence_scores(self) -> list[float]:
        """Confidence scores for discovered patterns."""
        ...


@runtime_checkable
class ProtocolEmbeddingResponse(ProtocolMemoryResponse, Protocol):
    """Protocol for embedding generation responses."""

    embedding: list[float]
    algorithm_used: str
    dimensions: int


# === REDUCER NODE RESPONSE PROTOCOLS ===


@runtime_checkable
class ProtocolConsolidationResponse(ProtocolMemoryResponse, Protocol):
    """Protocol for memory consolidation responses."""

    consolidated_memory_id: UUID
    source_memory_ids: list[UUID]


@runtime_checkable
class ProtocolAggregationResponse(ProtocolMemoryResponse, Protocol):
    """Protocol for memory aggregation responses."""

    aggregated_data: "ProtocolAggregatedData"
    aggregation_metadata: "ProtocolMemoryMetadata"


# === ORCHESTRATOR NODE RESPONSE PROTOCOLS ===


@runtime_checkable
class ProtocolWorkflowExecutionResponse(ProtocolMemoryResponse, Protocol):
    """Protocol for workflow execution responses."""

    workflow_id: UUID
    execution_status: str

    @property
    def agent_statuses(self) -> "ProtocolAgentStatusMap":
        """Status of each agent in workflow."""
        ...


@runtime_checkable
class ProtocolAgentCoordinationResponse(ProtocolMemoryResponse, Protocol):
    """Protocol for agent coordination responses."""

    coordination_id: UUID
    coordination_status: str

    @property
    def agent_responses(self) -> "ProtocolAgentResponseMap":
        """Response from each coordinated agent."""
        ...


# === PAGINATION RESPONSE PROTOCOLS ===


@runtime_checkable
class ProtocolPaginationResponse(Protocol):
    """Protocol for paginated response metadata."""

    total_count: int
    has_next_page: bool
    has_previous_page: bool
    next_cursor: Optional[str]
    previous_cursor: Optional[str]

    @property
    def page_info(self) -> "ProtocolPageInfo":
        """Additional pagination metadata."""
        ...


# === METRICS RESPONSE PROTOCOLS ===


@runtime_checkable
class ProtocolMemoryMetrics(Protocol):
    """Protocol for memory system performance metrics."""

    operation_type: str
    execution_time_ms: int
    memory_usage_mb: float
    timestamp: datetime

    @property
    def throughput_ops_per_second(self) -> float:
        """Operations per second for this metric period."""
        ...

    @property
    def error_rate_percent(self) -> float:
        """Error rate as percentage for this operation type."""
        ...

    @property
    def custom_metrics(self) -> "ProtocolCustomMetrics":
        """Additional operation-specific metrics."""
        ...


@runtime_checkable
class ProtocolMemoryMetricsResponse(ProtocolMemoryResponse, Protocol):
    """Protocol for metrics collection responses."""

    metrics: list[ProtocolMemoryMetrics]
    aggregation_summary: "ProtocolAggregationSummary"
    collection_timestamp: datetime


# === STREAMING RESPONSE PROTOCOLS ===


@runtime_checkable
class ProtocolStreamingMemoryResponse(ProtocolMemoryResponse, Protocol):
    """Protocol for streaming memory operation responses."""

    stream_id: UUID
    chunk_count: int
    total_size_bytes: int

    async def stream_content(self) -> AsyncIterator[bytes]:
        """Stream memory content in chunks."""
        ...

    @property
    def compression_ratio(self) -> Optional[float]:
        """Compression ratio if compression was used."""
        ...


@runtime_checkable
class ProtocolStreamingRetrieveResponse(ProtocolStreamingMemoryResponse, Protocol):
    """Protocol for streaming memory retrieval responses."""

    memory_metadata: list["ProtocolMemoryRecord"]

    async def stream_memory_content(self, memory_id: UUID) -> AsyncIterator[bytes]:
        """Stream content for a specific memory record."""
        ...
