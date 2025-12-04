"""
Memory Response Protocols for OmniMemory ONEX Architecture

This module defines core response protocol interfaces for memory operations.
Separated from the main types module to prevent circular imports and
improve maintainability.

Contains:
    - Base response protocols
    - Single-record operation response protocols
    - Search response protocols
    - Embedding response protocol

Advanced response protocols (batch, streaming, workflow, metrics) have been
moved to protocol_memory_advanced_responses.py but are re-exported here for
backward compatibility.

All types are pure protocols with no implementation dependencies.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable
from uuid import UUID

from omnibase_spi.protocols.memory.protocol_memory_errors import ProtocolMemoryError

# Re-export from protocol_memory_advanced_responses for backward compatibility
from omnibase_spi.protocols.memory.protocol_memory_advanced_responses import (
    ProtocolAgentCoordinationResponse,
    ProtocolAggregationResponse,
    ProtocolBatchMemoryRetrieveResponse,
    ProtocolBatchMemoryStoreResponse,
    ProtocolBatchOperationResult,
    ProtocolConsolidationResponse,
    ProtocolMemoryMetrics,
    ProtocolMemoryMetricsResponse,
    ProtocolPaginationResponse,
    ProtocolPatternAnalysisResponse,
    ProtocolStreamingMemoryResponse,
    ProtocolStreamingRetrieveResponse,
    ProtocolWorkflowExecutionResponse,
)

if TYPE_CHECKING:
    from datetime import datetime

    from omnibase_spi.protocols.memory.protocol_memory_base import (
        ProtocolMemoryMetadata,
        ProtocolMemoryRecord,
        ProtocolSearchResult,
    )


@runtime_checkable
class ProtocolMemoryResponse(Protocol):
    """Base protocol for all memory operation responses."""

    correlation_id: UUID | None
    response_timestamp: "datetime"
    success: bool

    @property
    def error_message(self) -> str | None: ...


@runtime_checkable
class ProtocolMemoryStoreResponse(ProtocolMemoryResponse, Protocol):
    """Protocol for memory storage responses."""

    memory_id: UUID | None
    storage_location: str | None


@runtime_checkable
class ProtocolMemoryRetrieveResponse(ProtocolMemoryResponse, Protocol):
    """Protocol for memory retrieval responses."""

    memory: "ProtocolMemoryRecord | None"

    @property
    def related_memories(self) -> list["ProtocolMemoryRecord"]: ...


@runtime_checkable
class ProtocolMemoryListResponse(ProtocolMemoryResponse, Protocol):
    """Protocol for paginated memory list responses."""

    memories: list["ProtocolMemoryRecord"]
    pagination: "ProtocolPaginationResponse"


@runtime_checkable
class ProtocolSemanticSearchResponse(ProtocolMemoryResponse, Protocol):
    """Protocol for semantic search responses."""

    results: list["ProtocolSearchResult"]
    total_matches: int
    search_time_ms: int

    async def get_query_embedding(self) -> list[float] | None: ...


@runtime_checkable
class ProtocolEmbeddingResponse(ProtocolMemoryResponse, Protocol):
    """Protocol for embedding generation responses."""

    embedding: list[float]
    algorithm_used: str
    dimensions: int


# Backward compatibility exports
__all__ = [
    # Core protocols (defined here)
    "ProtocolMemoryResponse",
    "ProtocolMemoryStoreResponse",
    "ProtocolMemoryRetrieveResponse",
    "ProtocolMemoryListResponse",
    "ProtocolSemanticSearchResponse",
    "ProtocolEmbeddingResponse",
    # Re-exported from protocol_memory_advanced_responses
    "ProtocolBatchOperationResult",
    "ProtocolBatchMemoryStoreResponse",
    "ProtocolBatchMemoryRetrieveResponse",
    "ProtocolPatternAnalysisResponse",
    "ProtocolConsolidationResponse",
    "ProtocolAggregationResponse",
    "ProtocolWorkflowExecutionResponse",
    "ProtocolAgentCoordinationResponse",
    "ProtocolPaginationResponse",
    "ProtocolMemoryMetrics",
    "ProtocolMemoryMetricsResponse",
    "ProtocolStreamingMemoryResponse",
    "ProtocolStreamingRetrieveResponse",
]
