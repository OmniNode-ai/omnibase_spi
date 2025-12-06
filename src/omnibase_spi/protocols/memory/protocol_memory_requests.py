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
    ProtocolAgentCoordinationRequest,
    ProtocolAggregationRequest,
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
        ProtocolMemoryMetadata,
        ProtocolSearchFilters,
    )


@runtime_checkable
class ProtocolMemoryRequest(Protocol):
    """
    Base protocol for all memory operation requests.

    This is the root protocol that all memory request types inherit from.
    It defines the minimal required attributes for request correlation
    and timing. Concrete request protocols extend this with operation-specific
    attributes.

    Implementations should ensure that correlation IDs are propagated through
    all downstream operations for distributed tracing.

    Attributes:
        correlation_id: Optional UUID for request tracing across services.
        request_timestamp: When the request was created.
        request_source: Identifier of the requesting component/service.

    Example:
        ```python
        class BaseMemoryRequest:
            '''Concrete implementation of ProtocolMemoryRequest.'''

            def __init__(
                self,
                request_source: str,
                correlation_id: UUID | None = None,
            ) -> None:
                self.correlation_id = correlation_id or uuid4()
                self.request_timestamp = datetime.now(UTC)
                self.request_source = request_source

            @property
            def operation_type(self) -> str:
                return "base"

            @property
            def is_idempotent(self) -> bool:
                return False

        # Usage
        request = BaseMemoryRequest(request_source="agent-1")
        assert isinstance(request, ProtocolMemoryRequest)
        assert request.correlation_id is not None
        ```

    See Also:
        - ProtocolMemoryStoreRequest: For storage operations.
        - ProtocolMemoryRetrieveRequest: For retrieval operations.
    """

    correlation_id: UUID | None
    request_timestamp: datetime
    request_source: str

    @property
    def operation_type(self) -> str: ...

    @property
    def is_idempotent(self) -> bool: ...


@runtime_checkable
class ProtocolMemoryStoreRequest(ProtocolMemoryRequest, Protocol):
    """
    Protocol for single memory storage requests.

    This protocol defines the interface for storing a single memory record.
    It extends the base request protocol with content, access control, and
    expiration information for the memory to be stored.

    Implementations should validate content size limits and access level
    permissions before processing the storage request.

    Attributes:
        content: The memory content to store.
        content_type: MIME type or classification of the content.
        access_level: Access control level for the stored memory.
        source_agent: Identifier of the agent creating this memory.
        expires_at: Optional expiration timestamp for auto-deletion.

    Example:
        ```python
        class MemoryStoreRequest:
            '''Concrete implementation of ProtocolMemoryStoreRequest.'''

            def __init__(
                self,
                content: str,
                content_type: str,
                source_agent: str,
            ) -> None:
                self.correlation_id = uuid4()
                self.request_timestamp = datetime.now(UTC)
                self.request_source = source_agent
                self.content = content
                self.content_type = content_type
                self.access_level = "internal"
                self.source_agent = source_agent
                self.expires_at = None
                self._metadata: ProtocolMemoryMetadata | None = None

            @property
            def operation_type(self) -> str:
                return "store"

            @property
            def is_idempotent(self) -> bool:
                return False

            async def metadata(self) -> ProtocolMemoryMetadata | None:
                return self._metadata

        # Usage
        request = MemoryStoreRequest(
            content="Important information to remember",
            content_type="text/plain",
            source_agent="agent-1",
        )
        assert isinstance(request, ProtocolMemoryStoreRequest)
        ```

    See Also:
        - ProtocolMemoryStoreResponse: For the corresponding response protocol.
        - ProtocolBatchMemoryStoreRequest: For batch storage operations.
    """

    content: str
    content_type: str
    access_level: str
    source_agent: str
    expires_at: datetime | None

    async def metadata(self) -> ProtocolMemoryMetadata | None: ...


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
        memory_id: Single memory identifier (UUID).
        include_related: Whether to include related memory records.
        timeout_seconds: Optional operation timeout.

    Example:
        ```python
        class MemoryRetrieveRequest:
            '''Concrete implementation of ProtocolMemoryRetrieveRequest.'''

            def __init__(
                self,
                memory_id: UUID,
                include_related: bool = False,
            ) -> None:
                self.correlation_id = uuid4()
                self.request_timestamp = datetime.now(UTC)
                self.request_source = "client"
                self.memory_id = memory_id
                self.include_related = include_related
                self.timeout_seconds = 30.0

            @property
            def operation_type(self) -> str:
                return "retrieve"

            @property
            def is_idempotent(self) -> bool:
                return True

            @property
            def related_depth(self) -> int:
                return 2 if self.include_related else 0

        # Usage
        request = MemoryRetrieveRequest(
            memory_id=uuid4(),
            include_related=True,
        )
        assert isinstance(request, ProtocolMemoryRetrieveRequest)
        ```

    See Also:
        - ProtocolMemoryRetrieveResponse: For the corresponding response protocol.
        - ProtocolBatchMemoryRetrieveRequest: For multi-memory retrieval.
    """

    memory_id: UUID
    include_related: bool
    timeout_seconds: float | None

    @property
    def related_depth(self) -> int: ...


@runtime_checkable
class ProtocolMemoryListRequest(ProtocolMemoryRequest, Protocol):
    """
    Protocol for paginated memory list requests.

    This protocol defines the interface for listing memories with pagination
    and filtering. It supports cursor-based or offset-based pagination and
    optional content type, access level, and date range filters.

    Implementations should efficiently handle large result sets and support
    forward and backward pagination navigation.

    Attributes:
        pagination: Pagination parameters (limit, offset, cursor).
        filters: Optional search filters to constrain results.
        timeout_seconds: Optional operation timeout.

    Example:
        ```python
        class MemoryListRequest:
            '''Concrete implementation of ProtocolMemoryListRequest.'''

            def __init__(
                self,
                pagination: ProtocolPaginationRequest,
                filters: ProtocolSearchFilters | None = None,
            ) -> None:
                self.correlation_id = uuid4()
                self.request_timestamp = datetime.now(UTC)
                self.request_source = "client"
                self.pagination = pagination
                self.filters = filters
                self.timeout_seconds = 30.0

            @property
            def operation_type(self) -> str:
                return "list"

            @property
            def is_idempotent(self) -> bool:
                return True

            @property
            def include_content(self) -> bool:
                return True

        # Usage
        request = MemoryListRequest(
            pagination=pagination,
            filters=filters,
        )
        assert isinstance(request, ProtocolMemoryListRequest)
        ```

    See Also:
        - ProtocolMemoryListResponse: For the corresponding response protocol.
        - ProtocolPaginationRequest: For pagination parameters.
    """

    pagination: ProtocolPaginationRequest
    filters: ProtocolSearchFilters | None
    timeout_seconds: float | None

    @property
    def include_content(self) -> bool: ...


@runtime_checkable
class ProtocolSemanticSearchRequest(ProtocolMemoryRequest, Protocol):
    """
    Protocol for semantic search requests using vector similarity.

    This protocol defines the interface for semantic memory search using
    embeddings and vector similarity. It supports natural language queries
    with configurable similarity thresholds and result limits.

    Implementations should generate query embeddings and perform efficient
    vector similarity search using appropriate indexing strategies.

    Attributes:
        query: Natural language search query.
        limit: Maximum number of results to return.
        similarity_threshold: Minimum similarity score (0.0 to 1.0).
        filters: Optional filters to constrain search space.
        timeout_seconds: Optional operation timeout.

    Example:
        ```python
        class SemanticSearchRequest:
            '''Concrete implementation of ProtocolSemanticSearchRequest.'''

            def __init__(
                self,
                query: str,
                limit: int = 10,
                similarity_threshold: float = 0.7,
            ) -> None:
                self.correlation_id = uuid4()
                self.request_timestamp = datetime.now(UTC)
                self.request_source = "client"
                self.query = query
                self.limit = limit
                self.similarity_threshold = similarity_threshold
                self.filters = None
                self.timeout_seconds = 30.0

            @property
            def operation_type(self) -> str:
                return "semantic_search"

            @property
            def is_idempotent(self) -> bool:
                return True

            @property
            def embedding_model(self) -> str | None:
                return "text-embedding-3-small"

        # Usage
        request = SemanticSearchRequest(
            query="Find memories about project planning",
            limit=20,
            similarity_threshold=0.8,
        )
        assert isinstance(request, ProtocolSemanticSearchRequest)
        ```

    See Also:
        - ProtocolSemanticSearchResponse: For the corresponding response protocol.
        - ProtocolSearchResult: For individual search result structure.
    """

    query: str
    limit: int
    similarity_threshold: float
    filters: ProtocolSearchFilters | None
    timeout_seconds: float | None

    @property
    def embedding_model(self) -> str | None: ...


@runtime_checkable
class ProtocolEmbeddingRequest(ProtocolMemoryRequest, Protocol):
    """
    Protocol for embedding vector generation requests.

    This protocol defines the interface for generating embedding vectors
    from text content. Embeddings are used for semantic search and
    similarity comparison of memory content.

    Implementations should support multiple embedding algorithms and
    return normalized vectors suitable for cosine similarity comparison.

    Attributes:
        text: The text content to generate an embedding for.
        algorithm: Optional embedding algorithm/model to use.
        timeout_seconds: Optional operation timeout.

    Example:
        ```python
        class EmbeddingRequest:
            '''Concrete implementation of ProtocolEmbeddingRequest.'''

            def __init__(
                self,
                text: str,
                algorithm: str | None = None,
            ) -> None:
                self.correlation_id = uuid4()
                self.request_timestamp = datetime.now(UTC)
                self.request_source = "client"
                self.text = text
                self.algorithm = algorithm or "text-embedding-3-small"
                self.timeout_seconds = 10.0

            @property
            def operation_type(self) -> str:
                return "embedding"

            @property
            def is_idempotent(self) -> bool:
                return True

        # Usage
        request = EmbeddingRequest(
            text="Generate embedding for this text content",
            algorithm="text-embedding-3-large",
        )
        assert isinstance(request, ProtocolEmbeddingRequest)
        ```

    See Also:
        - ProtocolEmbeddingResponse: For the corresponding response protocol.
        - ProtocolSemanticSearchRequest: Uses embeddings for similarity search.
    """

    text: str
    algorithm: str | None
    timeout_seconds: float | None


@runtime_checkable
class ProtocolPaginationRequest(Protocol):
    """
    Protocol for paginated request parameters.

    This protocol defines the interface for specifying pagination parameters
    in list and search requests. It supports both offset-based and cursor-based
    pagination strategies with configurable sorting.

    Implementations should prefer cursor-based pagination for consistency
    in distributed systems and use offset-based for simple use cases.

    Attributes:
        limit: Maximum number of items to return per page.
        offset: Number of items to skip (for offset-based pagination).
        cursor: Opaque cursor string (for cursor-based pagination).

    Example:
        ```python
        class PaginationRequest:
            '''Concrete implementation of ProtocolPaginationRequest.'''

            def __init__(
                self,
                limit: int = 20,
                offset: int = 0,
                cursor: str | None = None,
            ) -> None:
                self.limit = limit
                self.offset = offset
                self.cursor = cursor
                self._sort_by: str | None = "created_at"
                self._sort_order = "desc"

            @property
            def sort_by(self) -> str | None:
                return self._sort_by

            @property
            def sort_order(self) -> str:
                return self._sort_order

        # Usage
        pagination = PaginationRequest(limit=50, offset=100)
        assert isinstance(pagination, ProtocolPaginationRequest)
        assert pagination.limit == 50
        ```

    See Also:
        - ProtocolPaginationResponse: For the corresponding response protocol.
        - ProtocolMemoryListRequest: Uses this for pagination parameters.
    """

    limit: int
    offset: int
    cursor: str | None

    @property
    def sort_by(self) -> str | None: ...

    @property
    def sort_order(self) -> str: ...


# Backward compatibility exports
__all__ = [
    "ProtocolAgentCoordinationRequest",
    "ProtocolAggregationRequest",
    "ProtocolBatchMemoryRetrieveRequest",
    # Re-exported from protocol_memory_advanced_requests
    "ProtocolBatchMemoryStoreRequest",
    "ProtocolConsolidationRequest",
    "ProtocolEmbeddingRequest",
    "ProtocolMemoryListRequest",
    "ProtocolMemoryMetricsRequest",
    # Core protocols (defined here)
    "ProtocolMemoryRequest",
    "ProtocolMemoryRetrieveRequest",
    "ProtocolMemoryStoreRequest",
    "ProtocolPaginationRequest",
    "ProtocolPatternAnalysisRequest",
    "ProtocolSemanticSearchRequest",
    "ProtocolStreamingMemoryRequest",
    "ProtocolStreamingRetrieveRequest",
    "ProtocolWorkflowExecutionRequest",
]
