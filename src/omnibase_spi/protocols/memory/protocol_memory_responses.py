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
        ProtocolMemoryRecord,
        ProtocolSearchResult,
    )

# Re-export ProtocolMemoryMetadata for backward compatibility
from omnibase_spi.protocols.memory.protocol_memory_base import ProtocolMemoryMetadata


@runtime_checkable
class ProtocolMemoryResponse(Protocol):
    """
    Base protocol for all memory operation responses.

    This is the root protocol that all memory response types inherit from.
    It defines the minimal required attributes for response correlation,
    timing, and success indication. Concrete response protocols extend
    this with operation-specific result attributes.

    Implementations should ensure correlation IDs match the originating request
    and provide accurate timing information for performance monitoring.

    Attributes:
        correlation_id: UUID matching the originating request.
        response_timestamp: When the response was generated.
        success: Whether the operation completed successfully.
        response_source: Identifier of the responding service/node.

    Example:
        ```python
        class BaseMemoryResponse:
            '''Concrete implementation of ProtocolMemoryResponse.'''

            def __init__(
                self,
                correlation_id: UUID | None,
                success: bool,
                start_time: datetime,
            ) -> None:
                self.correlation_id = correlation_id
                self.response_timestamp = datetime.now(UTC)
                self.success = success
                self.response_source = "memory-service"
                self._start_time = start_time
                self._error_message: str | None = None

            @property
            def error_message(self) -> str | None:
                return self._error_message

            @property
            def processing_duration_ms(self) -> int:
                delta = self.response_timestamp - self._start_time
                return int(delta.total_seconds() * 1000)

        # Usage
        response = BaseMemoryResponse(
            correlation_id=uuid4(),
            success=True,
            start_time=datetime.now(UTC),
        )
        assert isinstance(response, ProtocolMemoryResponse)
        ```

    See Also:
        - ProtocolMemoryRequest: For the corresponding request protocol.
        - ProtocolMemoryStoreResponse: For storage operation responses.
    """

    correlation_id: UUID | None
    response_timestamp: datetime
    success: bool
    response_source: str

    @property
    def error_message(self) -> str | None: ...

    @property
    def processing_duration_ms(self) -> int: ...


@runtime_checkable
class ProtocolMemoryStoreResponse(ProtocolMemoryResponse, Protocol):
    """
    Protocol for memory storage operation responses.

    This protocol defines the interface for responses from memory storage
    operations. It extends the base response with the assigned memory ID
    and storage location information.

    Implementations should return the generated memory ID on success and
    provide storage location details for distributed storage systems.

    Attributes:
        memory_id: UUID assigned to the stored memory (None on failure).
        storage_location: Storage location identifier (e.g., node, partition).

    Example:
        ```python
        class MemoryStoreResponse:
            '''Concrete implementation of ProtocolMemoryStoreResponse.'''

            def __init__(
                self,
                correlation_id: UUID | None,
                memory_id: UUID,
                storage_location: str,
            ) -> None:
                self.correlation_id = correlation_id
                self.response_timestamp = datetime.now(UTC)
                self.success = True
                self.response_source = "memory-service"
                self.memory_id = memory_id
                self.storage_location = storage_location

            @property
            def error_message(self) -> str | None:
                return None

            @property
            def processing_duration_ms(self) -> int:
                return 25

        # Usage
        response = MemoryStoreResponse(
            correlation_id=uuid4(),
            memory_id=uuid4(),
            storage_location="partition-1",
        )
        assert isinstance(response, ProtocolMemoryStoreResponse)
        assert response.memory_id is not None
        ```

    See Also:
        - ProtocolMemoryStoreRequest: For the corresponding request protocol.
        - ProtocolBatchMemoryStoreResponse: For batch storage responses.
    """

    memory_id: UUID | None
    storage_location: str | None


@runtime_checkable
class ProtocolMemoryRetrieveResponse(ProtocolMemoryResponse, Protocol):
    """
    Protocol for memory retrieval operation responses.

    This protocol defines the interface for responses from memory retrieval
    operations. It includes the retrieved memory record and optionally
    related memories if requested.

    Implementations should return None for the memory if not found and
    provide related memories based on the request's include_related flag.

    Attributes:
        memory: The retrieved memory record (None if not found).

    Example:
        ```python
        class MemoryRetrieveResponse:
            '''Concrete implementation of ProtocolMemoryRetrieveResponse.'''

            def __init__(
                self,
                correlation_id: UUID | None,
                memory: ProtocolMemoryRecord | None,
                related: list[ProtocolMemoryRecord] | None = None,
            ) -> None:
                self.correlation_id = correlation_id
                self.response_timestamp = datetime.now(UTC)
                self.success = memory is not None
                self.response_source = "memory-service"
                self.memory = memory
                self._related = related or []

            @property
            def error_message(self) -> str | None:
                if self.memory is None:
                    return "Memory not found"
                return None

            @property
            def processing_duration_ms(self) -> int:
                return 15

            @property
            def related_memories(self) -> list[ProtocolMemoryRecord]:
                return self._related

        # Usage
        response = MemoryRetrieveResponse(
            correlation_id=uuid4(),
            memory=record,
            related=[related_record1, related_record2],
        )
        assert isinstance(response, ProtocolMemoryRetrieveResponse)
        ```

    See Also:
        - ProtocolMemoryRetrieveRequest: For the corresponding request protocol.
        - ProtocolBatchMemoryRetrieveResponse: For batch retrieval responses.
    """

    memory: ProtocolMemoryRecord | None

    @property
    def related_memories(self) -> list[ProtocolMemoryRecord]: ...


@runtime_checkable
class ProtocolMemoryListResponse(ProtocolMemoryResponse, Protocol):
    """
    Protocol for paginated memory list operation responses.

    This protocol defines the interface for responses from memory list
    operations. It includes the list of memory records for the current
    page and pagination metadata for navigation.

    Implementations should provide accurate pagination information and
    respect the filters specified in the corresponding request.

    Attributes:
        memories: List of memory records for the current page.
        pagination: Pagination metadata for navigation.

    Example:
        ```python
        class MemoryListResponse:
            '''Concrete implementation of ProtocolMemoryListResponse.'''

            def __init__(
                self,
                correlation_id: UUID | None,
                memories: list[ProtocolMemoryRecord],
                pagination: ProtocolPaginationResponse,
            ) -> None:
                self.correlation_id = correlation_id
                self.response_timestamp = datetime.now(UTC)
                self.success = True
                self.response_source = "memory-service"
                self.memories = memories
                self.pagination = pagination

            @property
            def error_message(self) -> str | None:
                return None

            @property
            def processing_duration_ms(self) -> int:
                return 50

        # Usage
        response = MemoryListResponse(
            correlation_id=uuid4(),
            memories=[record1, record2, record3],
            pagination=pagination_info,
        )
        assert isinstance(response, ProtocolMemoryListResponse)
        assert len(response.memories) == 3
        ```

    See Also:
        - ProtocolMemoryListRequest: For the corresponding request protocol.
        - ProtocolPaginationResponse: For pagination metadata structure.
    """

    memories: list[ProtocolMemoryRecord]
    pagination: ProtocolPaginationResponse


@runtime_checkable
class ProtocolSemanticSearchResponse(ProtocolMemoryResponse, Protocol):
    """
    Protocol for semantic search operation responses.

    This protocol defines the interface for responses from semantic search
    operations. It includes ranked search results with relevance scores
    and search performance metrics.

    Implementations should return results sorted by relevance score in
    descending order and provide accurate timing metrics.

    Attributes:
        results: List of search results ranked by relevance.
        total_matches: Total number of memories matching the query.
        search_time_ms: Time taken to execute the search in milliseconds.

    Example:
        ```python
        class SemanticSearchResponse:
            '''Concrete implementation of ProtocolSemanticSearchResponse.'''

            def __init__(
                self,
                correlation_id: UUID | None,
                results: list[ProtocolSearchResult],
                total_matches: int,
                search_time_ms: int,
            ) -> None:
                self.correlation_id = correlation_id
                self.response_timestamp = datetime.now(UTC)
                self.success = True
                self.response_source = "memory-service"
                self.results = results
                self.total_matches = total_matches
                self.search_time_ms = search_time_ms
                self._query_embedding: list[float] | None = None

            @property
            def error_message(self) -> str | None:
                return None

            @property
            def processing_duration_ms(self) -> int:
                return self.search_time_ms

            async def get_query_embedding(self) -> list[float] | None:
                return self._query_embedding

        # Usage
        response = SemanticSearchResponse(
            correlation_id=uuid4(),
            results=[result1, result2],
            total_matches=25,
            search_time_ms=150,
        )
        assert isinstance(response, ProtocolSemanticSearchResponse)
        ```

    See Also:
        - ProtocolSemanticSearchRequest: For the corresponding request protocol.
        - ProtocolSearchResult: For individual search result structure.
    """

    results: list[ProtocolSearchResult]
    total_matches: int
    search_time_ms: int

    async def get_query_embedding(self) -> list[float] | None: ...


@runtime_checkable
class ProtocolEmbeddingResponse(ProtocolMemoryResponse, Protocol):
    """
    Protocol for embedding vector generation responses.

    This protocol defines the interface for responses from embedding
    generation operations. It includes the generated embedding vector
    and information about the algorithm used.

    Implementations should return normalized vectors and accurate
    dimension information for vector database compatibility.

    Attributes:
        embedding: The generated embedding vector (list of floats).
        algorithm_used: Name of the algorithm/model used for generation.
        dimensions: Number of dimensions in the embedding vector.

    Example:
        ```python
        class EmbeddingResponse:
            '''Concrete implementation of ProtocolEmbeddingResponse.'''

            def __init__(
                self,
                correlation_id: UUID | None,
                embedding: list[float],
                algorithm_used: str,
            ) -> None:
                self.correlation_id = correlation_id
                self.response_timestamp = datetime.now(UTC)
                self.success = True
                self.response_source = "embedding-service"
                self.embedding = embedding
                self.algorithm_used = algorithm_used
                self.dimensions = len(embedding)

            @property
            def error_message(self) -> str | None:
                return None

            @property
            def processing_duration_ms(self) -> int:
                return 45

        # Usage
        response = EmbeddingResponse(
            correlation_id=uuid4(),
            embedding=[0.1, 0.2, 0.3, ...],  # 1536-dimensional vector
            algorithm_used="text-embedding-3-small",
        )
        assert isinstance(response, ProtocolEmbeddingResponse)
        assert response.dimensions == len(response.embedding)
        ```

    See Also:
        - ProtocolEmbeddingRequest: For the corresponding request protocol.
        - ProtocolSemanticSearchRequest: Uses embeddings for similarity search.
    """

    embedding: list[float]
    algorithm_used: str
    dimensions: int


# Backward compatibility exports
__all__ = [
    "ProtocolAgentCoordinationResponse",
    "ProtocolAggregationResponse",
    "ProtocolBatchMemoryRetrieveResponse",
    "ProtocolBatchMemoryStoreResponse",
    # Re-exported from protocol_memory_advanced_responses
    "ProtocolBatchOperationResult",
    "ProtocolConsolidationResponse",
    "ProtocolEmbeddingResponse",
    "ProtocolMemoryListResponse",
    # Re-exported from protocol_memory_base
    "ProtocolMemoryMetadata",
    "ProtocolMemoryMetrics",
    "ProtocolMemoryMetricsResponse",
    # Core protocols (defined here)
    "ProtocolMemoryResponse",
    "ProtocolMemoryRetrieveResponse",
    "ProtocolMemoryStoreResponse",
    "ProtocolPaginationResponse",
    "ProtocolPatternAnalysisResponse",
    "ProtocolSemanticSearchResponse",
    "ProtocolStreamingMemoryResponse",
    "ProtocolStreamingRetrieveResponse",
    "ProtocolWorkflowExecutionResponse",
]
