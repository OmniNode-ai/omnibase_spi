"""
Pure Protocol Type Definitions for OmniMemory ONEX Architecture

This module defines type protocols for memory operations following ONEX
contract-driven development patterns. All types are pure protocols with
no implementation dependencies - no Pydantic, no BaseModel, just protocols.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional, Protocol, runtime_checkable
from uuid import UUID

if TYPE_CHECKING:
    pass  # All types are forward references to avoid circular imports


# === CORE MEMORY PROTOCOLS ===


@runtime_checkable
class ProtocolMemoryRecord(Protocol):
    """Protocol for memory record data structure."""

    memory_id: UUID
    content: str
    content_type: str
    created_at: datetime
    updated_at: datetime
    access_level: str
    source_agent: str
    expires_at: Optional[datetime]

    @property
    def embedding(self) -> Optional[list[float]]:
        """Vector embedding for semantic search."""
        ...

    @property
    def related_memories(self) -> list[UUID]:
        """Related memory identifiers."""
        ...


@runtime_checkable
class ProtocolSearchResult(Protocol):
    """Protocol for search result data structure."""

    memory_record: ProtocolMemoryRecord
    relevance_score: float
    match_type: str

    @property
    def highlighted_content(self) -> Optional[str]:
        """Content with search term highlights."""
        ...


@runtime_checkable
class ProtocolSearchFilters(Protocol):
    """Protocol for search filter specifications."""

    content_types: Optional[list[str]]
    access_levels: Optional[list[str]]
    source_agents: Optional[list[str]]
    date_range_start: Optional[datetime]
    date_range_end: Optional[datetime]

    @property
    def tags(self) -> Optional[list[str]]:
        """Filter tags for search."""
        ...


# === REQUEST/RESPONSE PROTOCOLS ===


@runtime_checkable
class ProtocolMemoryRequest(Protocol):
    """Base protocol for all memory operation requests."""

    correlation_id: Optional[UUID]
    request_timestamp: datetime

    @property
    def operation_type(self) -> str:
        """Type of memory operation being requested."""
        ...


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


@runtime_checkable
class ProtocolMemoryStoreRequest(ProtocolMemoryRequest, Protocol):
    """Protocol for memory storage requests."""

    content: str
    content_type: str
    access_level: str
    source_agent: str
    expires_at: Optional[datetime]

    @property
    def metadata(self) -> Optional[dict[str, str]]:
        """Additional metadata for the memory."""
        ...


@runtime_checkable
class ProtocolMemoryStoreResponse(ProtocolMemoryResponse, Protocol):
    """Protocol for memory storage responses."""

    memory_id: Optional[UUID]
    storage_location: Optional[str]


@runtime_checkable
class ProtocolMemoryRetrieveRequest(ProtocolMemoryRequest, Protocol):
    """Protocol for memory retrieval requests."""

    memory_id: UUID
    include_related: bool

    @property
    def related_depth(self) -> int:
        """Depth of related memory traversal."""
        ...


@runtime_checkable
class ProtocolMemoryRetrieveResponse(ProtocolMemoryResponse, Protocol):
    """Protocol for memory retrieval responses."""

    memory: Optional[ProtocolMemoryRecord]

    @property
    def related_memories(self) -> list[ProtocolMemoryRecord]:
        """Related memory records if requested."""
        ...


@runtime_checkable
class ProtocolSemanticSearchRequest(ProtocolMemoryRequest, Protocol):
    """Protocol for semantic search requests."""

    query: str
    limit: int
    similarity_threshold: float
    filters: Optional[ProtocolSearchFilters]

    @property
    def embedding_model(self) -> Optional[str]:
        """Specific embedding model for query."""
        ...


@runtime_checkable
class ProtocolSemanticSearchResponse(ProtocolMemoryResponse, Protocol):
    """Protocol for semantic search responses."""

    results: list[ProtocolSearchResult]
    total_matches: int
    search_time_ms: int

    @property
    def query_embedding(self) -> Optional[list[float]]:
        """Query embedding used for search."""
        ...


# === ORCHESTRATOR PROTOCOLS ===


@runtime_checkable
class ProtocolWorkflowExecutionRequest(ProtocolMemoryRequest, Protocol):
    """Protocol for workflow execution requests."""

    workflow_type: str
    workflow_configuration: dict[str, str]

    @property
    def target_agents(self) -> list[UUID]:
        """Agents to coordinate in workflow."""
        ...


@runtime_checkable
class ProtocolWorkflowExecutionResponse(ProtocolMemoryResponse, Protocol):
    """Protocol for workflow execution responses."""

    workflow_id: UUID
    execution_status: str

    @property
    def agent_statuses(self) -> dict[UUID, str]:
        """Status of each agent in workflow."""
        ...


@runtime_checkable
class ProtocolAgentCoordinationRequest(ProtocolMemoryRequest, Protocol):
    """Protocol for agent coordination requests."""

    agent_ids: list[UUID]
    coordination_task: str

    @property
    def coordination_metadata(self) -> dict[str, str]:
        """Coordination task metadata."""
        ...


@runtime_checkable
class ProtocolAgentCoordinationResponse(ProtocolMemoryResponse, Protocol):
    """Protocol for agent coordination responses."""

    coordination_id: UUID
    coordination_status: str

    @property
    def agent_responses(self) -> dict[UUID, str]:
        """Response from each coordinated agent."""
        ...


# === COMPUTE PROTOCOLS ===


@runtime_checkable
class ProtocolPatternAnalysisRequest(ProtocolMemoryRequest, Protocol):
    """Protocol for pattern analysis requests."""

    data_source: str
    analysis_type: str

    @property
    def analysis_parameters(self) -> dict[str, str]:
        """Parameters for pattern analysis."""
        ...


@runtime_checkable
class ProtocolPatternAnalysisResponse(ProtocolMemoryResponse, Protocol):
    """Protocol for pattern analysis responses."""

    patterns_found: int
    analysis_results: dict[str, str]

    @property
    def confidence_scores(self) -> list[float]:
        """Confidence scores for discovered patterns."""
        ...


@runtime_checkable
class ProtocolEmbeddingRequest(ProtocolMemoryRequest, Protocol):
    """Protocol for embedding generation requests."""

    text: str
    algorithm: Optional[str]


@runtime_checkable
class ProtocolEmbeddingResponse(ProtocolMemoryResponse, Protocol):
    """Protocol for embedding generation responses."""

    embedding: list[float]
    algorithm_used: str
    dimensions: int


# === REDUCER PROTOCOLS ===


@runtime_checkable
class ProtocolConsolidationRequest(ProtocolMemoryRequest, Protocol):
    """Protocol for memory consolidation requests."""

    memory_ids: list[UUID]
    consolidation_strategy: str


@runtime_checkable
class ProtocolConsolidationResponse(ProtocolMemoryResponse, Protocol):
    """Protocol for memory consolidation responses."""

    consolidated_memory_id: UUID
    source_memory_ids: list[UUID]


@runtime_checkable
class ProtocolAggregationRequest(ProtocolMemoryRequest, Protocol):
    """Protocol for memory aggregation requests."""

    aggregation_criteria: dict[str, str]
    time_window_start: Optional[datetime]
    time_window_end: Optional[datetime]


@runtime_checkable
class ProtocolAggregationResponse(ProtocolMemoryResponse, Protocol):
    """Protocol for memory aggregation responses."""

    aggregated_data: dict[str, str]
    aggregation_metadata: dict[str, str]


# === ERROR HANDLING PROTOCOLS ===


@runtime_checkable
class ProtocolMemoryError(Protocol):
    """Protocol for standardized memory operation errors."""

    error_code: str
    error_message: str
    error_timestamp: datetime
    correlation_id: Optional[UUID]

    @property
    def error_context(self) -> dict[str, str]:
        """Additional error context and debugging information."""
        ...

    @property
    def recoverable(self) -> bool:
        """Whether this error condition is recoverable."""
        ...


@runtime_checkable
class ProtocolMemoryErrorResponse(ProtocolMemoryResponse, Protocol):
    """Protocol for error responses from memory operations."""

    error: ProtocolMemoryError
    suggested_action: str

    @property
    def retry_after_seconds(self) -> Optional[int]:
        """Suggested retry delay for transient errors."""
        ...


# === PAGINATION PROTOCOLS ===


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


@runtime_checkable
class ProtocolPaginationResponse(Protocol):
    """Protocol for paginated response metadata."""

    total_count: int
    has_next_page: bool
    has_previous_page: bool
    next_cursor: Optional[str]
    previous_cursor: Optional[str]

    @property
    def page_info(self) -> dict[str, str]:
        """Additional pagination metadata."""
        ...


@runtime_checkable
class ProtocolMemoryListRequest(ProtocolMemoryRequest, Protocol):
    """Protocol for paginated memory list requests."""

    pagination: ProtocolPaginationRequest
    filters: Optional[ProtocolSearchFilters]

    @property
    def include_content(self) -> bool:
        """Whether to include full memory content in results."""
        ...


@runtime_checkable
class ProtocolMemoryListResponse(ProtocolMemoryResponse, Protocol):
    """Protocol for paginated memory list responses."""

    memories: list[ProtocolMemoryRecord]
    pagination: ProtocolPaginationResponse


# === METRICS PROTOCOLS ===


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
    def custom_metrics(self) -> dict[str, float]:
        """Additional operation-specific metrics."""
        ...


@runtime_checkable
class ProtocolMemoryMetricsRequest(ProtocolMemoryRequest, Protocol):
    """Protocol for metrics collection requests."""

    metric_types: list[str]
    time_window_start: Optional[datetime]
    time_window_end: Optional[datetime]
    aggregation_level: str

    @property
    def include_detailed_breakdown(self) -> bool:
        """Whether to include detailed metric breakdowns."""
        ...


@runtime_checkable
class ProtocolMemoryMetricsResponse(ProtocolMemoryResponse, Protocol):
    """Protocol for metrics collection responses."""

    metrics: list[ProtocolMemoryMetrics]
    aggregation_summary: dict[str, float]
    collection_timestamp: datetime


# === BATCH OPERATION PROTOCOLS ===


@runtime_checkable
class ProtocolBatchMemoryStoreRequest(ProtocolMemoryRequest, Protocol):
    """Protocol for batch memory storage requests."""

    memory_records: list[dict[str, str]]
    batch_size: int
    fail_on_first_error: bool

    @property
    def transaction_isolation(self) -> str:
        """Transaction isolation level for batch operation."""
        ...

    @property
    def parallel_execution(self) -> bool:
        """Whether to execute batch operations in parallel."""
        ...


@runtime_checkable
class ProtocolBatchOperationResult(Protocol):
    """Protocol for individual batch operation results."""

    operation_index: int
    success: bool
    result_id: Optional[UUID]
    error: Optional[ProtocolMemoryError]

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
class ProtocolBatchMemoryRetrieveRequest(ProtocolMemoryRequest, Protocol):
    """Protocol for batch memory retrieval requests."""

    memory_ids: list[UUID]
    include_related: bool
    fail_on_missing: bool

    @property
    def related_depth(self) -> int:
        """Depth of related memory traversal for each record."""
        ...


@runtime_checkable
class ProtocolBatchMemoryRetrieveResponse(ProtocolMemoryResponse, Protocol):
    """Protocol for batch memory retrieval responses."""

    results: list[ProtocolBatchOperationResult]
    memories: list[ProtocolMemoryRecord]
    missing_ids: list[UUID]
    batch_execution_time_ms: int
