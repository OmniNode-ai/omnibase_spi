"""
Memory Request Protocols for OmniMemory ONEX Architecture

This module defines all request protocol interfaces for memory operations.
Separated from the main types module to prevent circular imports and
improve maintainability.

Contains:
- Base request protocols
- Effect node request protocols
- Compute node request protocols
- Reducer node request protocols
- Orchestrator node request protocols
- Batch operation request protocols

All types are pure protocols with no implementation dependencies.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Protocol, runtime_checkable
from uuid import UUID

if TYPE_CHECKING:
    from datetime import datetime

    from .protocol_memory_base import (
        LiteralAnalysisType,
        ProtocolAggregationCriteria,
        ProtocolAnalysisParameters,
        ProtocolCoordinationMetadata,
        ProtocolMemoryMetadata,
        ProtocolMemoryRecordData,
        ProtocolSearchFilters,
        ProtocolWorkflowConfiguration,
    )


# === BASE REQUEST PROTOCOLS ===


@runtime_checkable
class ProtocolMemoryRequest(Protocol):
    """Base protocol for all memory operation requests."""

    correlation_id: Optional[UUID]
    request_timestamp: "datetime"

    @property
    def operation_type(self) -> str:
        """Type of memory operation being requested."""
        ...


# === EFFECT NODE REQUEST PROTOCOLS ===


@runtime_checkable
class ProtocolMemoryStoreRequest(ProtocolMemoryRequest, Protocol):
    """Protocol for memory storage requests."""

    content: str
    content_type: str
    access_level: str  # LiteralMemoryAccessLevel from base
    source_agent: str
    expires_at: Optional["datetime"]

    @property
    def metadata(self) -> Optional["ProtocolMemoryMetadata"]:
        """Additional metadata for the memory."""
        ...


@runtime_checkable
class ProtocolMemoryRetrieveRequest(ProtocolMemoryRequest, Protocol):
    """Protocol for memory retrieval requests."""

    memory_id: UUID
    include_related: bool
    timeout_seconds: Optional[float]

    @property
    def related_depth(self) -> int:
        """Depth of related memory traversal."""
        ...


@runtime_checkable
class ProtocolMemoryListRequest(ProtocolMemoryRequest, Protocol):
    """Protocol for paginated memory list requests."""

    pagination: "ProtocolPaginationRequest"
    filters: Optional["ProtocolSearchFilters"]
    timeout_seconds: Optional[float]

    @property
    def include_content(self) -> bool:
        """Whether to include full memory content in results."""
        ...


@runtime_checkable
class ProtocolBatchMemoryStoreRequest(ProtocolMemoryRequest, Protocol):
    """Protocol for batch memory storage requests."""

    memory_records: list["ProtocolMemoryRecordData"]
    batch_size: int
    fail_on_first_error: bool
    timeout_seconds: Optional[float]

    @property
    def transaction_isolation(self) -> str:
        """Transaction isolation level for batch operation."""
        ...

    @property
    def parallel_execution(self) -> bool:
        """Whether to execute batch operations in parallel."""
        ...


@runtime_checkable
class ProtocolBatchMemoryRetrieveRequest(ProtocolMemoryRequest, Protocol):
    """Protocol for batch memory retrieval requests."""

    memory_ids: list[UUID]
    include_related: bool
    fail_on_missing: bool
    timeout_seconds: Optional[float]

    @property
    def related_depth(self) -> int:
        """Depth of related memory traversal for each record."""
        ...


# === COMPUTE NODE REQUEST PROTOCOLS ===


@runtime_checkable
class ProtocolSemanticSearchRequest(ProtocolMemoryRequest, Protocol):
    """Protocol for semantic search requests."""

    query: str
    limit: int
    similarity_threshold: float
    filters: Optional["ProtocolSearchFilters"]
    timeout_seconds: Optional[float]

    @property
    def embedding_model(self) -> Optional[str]:
        """Specific embedding model for query."""
        ...


@runtime_checkable
class ProtocolPatternAnalysisRequest(ProtocolMemoryRequest, Protocol):
    """Protocol for pattern analysis requests."""

    data_source: str
    analysis_type: "LiteralAnalysisType"
    timeout_seconds: Optional[float]

    @property
    def analysis_parameters(self) -> "ProtocolAnalysisParameters":
        """Parameters for pattern analysis."""
        ...


@runtime_checkable
class ProtocolEmbeddingRequest(ProtocolMemoryRequest, Protocol):
    """Protocol for embedding generation requests."""

    text: str
    algorithm: Optional[str]
    timeout_seconds: Optional[float]


# === REDUCER NODE REQUEST PROTOCOLS ===


@runtime_checkable
class ProtocolConsolidationRequest(ProtocolMemoryRequest, Protocol):
    """Protocol for memory consolidation requests."""

    memory_ids: list[UUID]
    consolidation_strategy: str
    timeout_seconds: Optional[float]


@runtime_checkable
class ProtocolAggregationRequest(ProtocolMemoryRequest, Protocol):
    """Protocol for memory aggregation requests."""

    aggregation_criteria: "ProtocolAggregationCriteria"
    time_window_start: Optional["datetime"]
    time_window_end: Optional["datetime"]
    timeout_seconds: Optional[float]


# === ORCHESTRATOR NODE REQUEST PROTOCOLS ===


@runtime_checkable
class ProtocolWorkflowExecutionRequest(ProtocolMemoryRequest, Protocol):
    """Protocol for workflow execution requests."""

    workflow_type: str
    workflow_configuration: "ProtocolWorkflowConfiguration"
    timeout_seconds: Optional[float]

    @property
    def target_agents(self) -> list[UUID]:
        """Agents to coordinate in workflow."""
        ...


@runtime_checkable
class ProtocolAgentCoordinationRequest(ProtocolMemoryRequest, Protocol):
    """Protocol for agent coordination requests."""

    agent_ids: list[UUID]
    coordination_task: str
    timeout_seconds: Optional[float]

    @property
    def coordination_metadata(self) -> "ProtocolCoordinationMetadata":
        """Coordination task metadata."""
        ...


# === PAGINATION REQUEST PROTOCOLS ===


@runtime_checkable
class ProtocolPaginationRequest(Protocol):
    """Protocol for paginated request parameters."""

    limit: int
    offset: int
    cursor: Optional[str]

    @property
    def sort_by(self) -> Optional[str]:
        """Field to sort results by."""
        ...

    @property
    def sort_order(self) -> str:
        """Sort order: 'asc' or 'desc'."""
        ...


# === METRICS REQUEST PROTOCOLS ===


@runtime_checkable
class ProtocolMemoryMetricsRequest(ProtocolMemoryRequest, Protocol):
    """Protocol for metrics collection requests."""

    metric_types: list[str]
    time_window_start: Optional["datetime"]
    time_window_end: Optional["datetime"]
    aggregation_level: str
    timeout_seconds: Optional[float]

    @property
    def include_detailed_breakdown(self) -> bool:
        """Whether to include detailed metric breakdowns."""
        ...


# === STREAMING REQUEST PROTOCOLS ===


@runtime_checkable
class ProtocolStreamingMemoryRequest(ProtocolMemoryRequest, Protocol):
    """Protocol for streaming memory operations."""

    stream_type: str
    chunk_size: int
    timeout_seconds: Optional[float]

    @property
    def compression_enabled(self) -> bool:
        """Whether to enable streaming compression."""
        ...


@runtime_checkable
class ProtocolStreamingRetrieveRequest(ProtocolStreamingMemoryRequest, Protocol):
    """Protocol for streaming memory retrieval requests."""

    memory_ids: list[UUID]
    include_metadata: bool

    @property
    def max_content_size(self) -> Optional[int]:
        """Maximum content size per memory record."""
        ...
