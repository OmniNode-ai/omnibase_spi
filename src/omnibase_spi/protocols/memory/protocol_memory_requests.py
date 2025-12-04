"""
Memory Request Protocols for OmniMemory ONEX Architecture

This module defines core request protocol interfaces for memory operations.
Separated from the main types module to prevent circular imports and
improve maintainability.

Contains:
    - Base request protocols
    - Single-record operation request protocols
    - Search request protocols
    - Pagination request protocol

Advanced request protocols (batch, streaming, workflow) have been moved to
protocol_memory_advanced_requests.py but are re-exported here for backward
compatibility.

All types are pure protocols with no implementation dependencies.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable
from uuid import UUID

# Re-export from protocol_memory_advanced_requests for backward compatibility
from omnibase_spi.protocols.memory.protocol_memory_advanced_requests import (
    ProtocolAggregationRequest,
    ProtocolAgentCoordinationRequest,
    ProtocolBatchMemoryRetrieveRequest,
    ProtocolBatchMemoryStoreRequest,
    ProtocolConsolidationRequest,
    ProtocolMemoryMetricsRequest,
    ProtocolPatternAnalysisRequest,
    ProtocolStreamingMemoryRequest,
    ProtocolStreamingRetrieveRequest,
    ProtocolWorkflowExecutionRequest,
)

if TYPE_CHECKING:
    from datetime import datetime

    from omnibase_spi.protocols.memory.protocol_memory_base import (
        LiteralAnalysisType,
        ProtocolAnalysisParameters,
        ProtocolMemoryMetadata,
        ProtocolSearchFilters,
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
    """
    Protocol for single memory retrieval requests.

    Retrieves one memory record by its unique identifier. For retrieving
    multiple memories in a single operation, use ProtocolBatchMemoryRetrieveRequest.

    Use Cases:
        - Direct memory lookup by known ID
        - Point queries in user interfaces
        - Individual memory inspection

    Attributes:
        memory_id: Single memory identifier (UUID)
        include_related: Whether to include related memory records
        timeout_seconds: Optional operation timeout

    Properties:
        related_depth: Depth of related memory graph traversal

    See Also:
        ProtocolBatchMemoryRetrieveRequest: For multi-memory retrieval
    """

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
class ProtocolEmbeddingRequest(ProtocolMemoryRequest, Protocol):
    """Protocol for embedding generation requests."""

    text: str
    algorithm: str | None
    timeout_seconds: float | None


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


# Backward compatibility exports
__all__ = [
    # Core protocols (defined here)
    "ProtocolMemoryRequest",
    "ProtocolMemoryStoreRequest",
    "ProtocolMemoryRetrieveRequest",
    "ProtocolMemoryListRequest",
    "ProtocolSemanticSearchRequest",
    "ProtocolEmbeddingRequest",
    "ProtocolPaginationRequest",
    # Re-exported from protocol_memory_advanced_requests
    "ProtocolBatchMemoryStoreRequest",
    "ProtocolBatchMemoryRetrieveRequest",
    "ProtocolPatternAnalysisRequest",
    "ProtocolConsolidationRequest",
    "ProtocolAggregationRequest",
    "ProtocolWorkflowExecutionRequest",
    "ProtocolAgentCoordinationRequest",
    "ProtocolMemoryMetricsRequest",
    "ProtocolStreamingMemoryRequest",
    "ProtocolStreamingRetrieveRequest",
]
