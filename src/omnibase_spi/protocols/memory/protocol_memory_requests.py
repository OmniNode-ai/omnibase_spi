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

from typing import TYPE_CHECKING, Protocol, runtime_checkable
from uuid import UUID

if TYPE_CHECKING:
    from datetime import datetime

    from omnibase_spi.protocols.memory.protocol_memory_base import (
        LiteralAnalysisType,
        ProtocolAggregatedData,
        ProtocolAggregationCriteria,
        ProtocolAnalysisParameters,
        ProtocolCoordinationMetadata,
        ProtocolMemoryMetadata,
        ProtocolSearchFilters,
        ProtocolWorkflowConfiguration,
    )


@runtime_checkable
class ProtocolMemoryRequest(Protocol):
    """Base protocol for all memory operation requests."""

    correlation_id: UUID | None
    request_timestamp: "datetime"

    @property
    def operation_type(self) -> str: ...


@runtime_checkable
class ProtocolMemoryStoreRequest(ProtocolMemoryRequest, Protocol):
    """Protocol for memory storage requests."""

    content: str
    content_type: str
    access_level: str
    source_agent: str
    expires_at: "datetime | None"

    async def metadata(self) -> "ProtocolMemoryMetadata | None": ...


@runtime_checkable
class ProtocolMemoryRetrieveRequest(ProtocolMemoryRequest, Protocol):
    """Protocol for memory retrieval requests."""

    memory_id: UUID
    include_related: bool
    timeout_seconds: float | None

    @property
    def related_depth(self) -> int: ...


@runtime_checkable
class ProtocolMemoryListRequest(ProtocolMemoryRequest, Protocol):
    """Protocol for paginated memory list requests."""

    pagination: "ProtocolPaginationRequest"
    filters: "ProtocolSearchFilters | None"
    timeout_seconds: float | None

    @property
    def include_content(self) -> bool: ...


@runtime_checkable
class ProtocolBatchMemoryStoreRequest(ProtocolMemoryRequest, Protocol):
    """Protocol for batch memory storage requests."""

    memory_records: list["ProtocolAggregatedData"]
    batch_size: int
    fail_on_first_error: bool
    timeout_seconds: float | None

    @property
    def transaction_isolation(self) -> str: ...

    @property
    def parallel_execution(self) -> bool: ...


@runtime_checkable
class ProtocolBatchMemoryRetrieveRequest(ProtocolMemoryRequest, Protocol):
    """Protocol for batch memory retrieval requests."""

    memory_ids: list[UUID]
    include_related: bool
    fail_on_missing: bool
    timeout_seconds: float | None

    @property
    def related_depth(self) -> int: ...


@runtime_checkable
class ProtocolSemanticSearchRequest(ProtocolMemoryRequest, Protocol):
    """Protocol for semantic search requests."""

    query: str
    limit: int
    similarity_threshold: float
    filters: "ProtocolSearchFilters | None"
    timeout_seconds: float | None

    @property
    def embedding_model(self) -> str | None: ...


@runtime_checkable
class ProtocolPatternAnalysisRequest(ProtocolMemoryRequest, Protocol):
    """Protocol for pattern analysis requests."""

    data_source: str
    analysis_type: "LiteralAnalysisType"
    timeout_seconds: float | None

    @property
    def analysis_parameters(self) -> "ProtocolAnalysisParameters": ...


@runtime_checkable
class ProtocolEmbeddingRequest(ProtocolMemoryRequest, Protocol):
    """Protocol for embedding generation requests."""

    text: str
    algorithm: str | None
    timeout_seconds: float | None


@runtime_checkable
class ProtocolConsolidationRequest(ProtocolMemoryRequest, Protocol):
    """Protocol for memory consolidation requests."""

    memory_ids: list[UUID]
    consolidation_strategy: str
    timeout_seconds: float | None


@runtime_checkable
class ProtocolAggregationRequest(ProtocolMemoryRequest, Protocol):
    """Protocol for memory aggregation requests."""

    aggregation_criteria: "ProtocolAggregationCriteria"
    time_window_start: "datetime | None"
    time_window_end: "datetime | None"
    timeout_seconds: float | None


@runtime_checkable
class ProtocolWorkflowExecutionRequest(ProtocolMemoryRequest, Protocol):
    """Protocol for workflow execution requests."""

    workflow_type: str
    workflow_configuration: "ProtocolWorkflowConfiguration"
    timeout_seconds: float | None

    async def get_target_agents(self) -> list[UUID]: ...


@runtime_checkable
class ProtocolAgentCoordinationRequest(ProtocolMemoryRequest, Protocol):
    """Protocol for agent coordination requests."""

    agent_ids: list[UUID]
    coordination_task: str
    timeout_seconds: float | None

    async def coordination_metadata(self) -> "ProtocolCoordinationMetadata": ...


@runtime_checkable
class ProtocolPaginationRequest(Protocol):
    """Protocol for paginated request parameters."""

    limit: int
    offset: int
    cursor: str | None

    @property
    def sort_by(self) -> str | None: ...

    @property
    def sort_order(self) -> str: ...


@runtime_checkable
class ProtocolMemoryMetricsRequest(ProtocolMemoryRequest, Protocol):
    """Protocol for metrics collection requests."""

    metric_types: list[str]
    time_window_start: "datetime | None"
    time_window_end: "datetime | None"
    aggregation_level: str
    timeout_seconds: float | None

    @property
    def include_detailed_breakdown(self) -> bool: ...


@runtime_checkable
class ProtocolStreamingMemoryRequest(ProtocolMemoryRequest, Protocol):
    """Protocol for streaming memory operations."""

    stream_type: str
    chunk_size: int
    timeout_seconds: float | None

    @property
    def compression_enabled(self) -> bool: ...


@runtime_checkable
class ProtocolStreamingRetrieveRequest(ProtocolStreamingMemoryRequest, Protocol):
    """Protocol for streaming memory retrieval requests."""

    memory_ids: list[UUID]
    include_metadata: bool

    @property
    def max_content_size(self) -> int | None: ...
