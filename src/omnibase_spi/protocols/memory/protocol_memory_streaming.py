"""
Streaming protocol definitions for OmniMemory operations.

Defines streaming protocols for large data operations, chunked processing,
and cursor-based pagination following ONEX performance optimization patterns.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, AsyncGenerator, Optional, Protocol, runtime_checkable
from uuid import UUID

if TYPE_CHECKING:
    from .protocol_memory_base import ProtocolMemoryMetadata
    from .protocol_memory_security import ProtocolSecurityContext


@runtime_checkable
class ProtocolStreamingChunk(Protocol):
    """
    Protocol for streaming data chunks.

    Represents individual chunks in a streaming operation with
    metadata for reconstruction and error handling.
    """

    @property
    def chunk_id(self) -> UUID:
        """Unique identifier for this chunk."""
        ...

    @property
    def stream_id(self) -> UUID:
        """Identifier for the overall stream."""
        ...

    @property
    def sequence_number(self) -> int:
        """Sequential number of this chunk."""
        ...

    @property
    def total_chunks(self) -> Optional[int]:
        """Total number of chunks (if known)."""
        ...

    @property
    def chunk_data(self) -> bytes:
        """Binary data for this chunk."""
        ...

    @property
    def chunk_size(self) -> int:
        """Size of this chunk in bytes."""
        ...

    @property
    def is_final_chunk(self) -> bool:
        """Whether this is the final chunk in the stream."""
        ...

    @property
    def checksum(self) -> str:
        """Checksum for chunk integrity verification."""
        ...

    @property
    def compression_type(self) -> Optional[str]:
        """Compression type used for this chunk."""
        ...

    @property
    def chunk_metadata(self) -> "ProtocolMemoryMetadata":
        """Additional metadata for this chunk."""
        ...


@runtime_checkable
class ProtocolStreamingConfig(Protocol):
    """
    Configuration for streaming operations.

    Defines parameters for chunking, compression, buffering,
    and streaming behavior optimization.
    """

    @property
    def chunk_size_bytes(self) -> int:
        """Size of each chunk in bytes."""
        ...

    @property
    def max_concurrent_chunks(self) -> int:
        """Maximum number of concurrent chunks to process."""
        ...

    @property
    def buffer_size_mb(self) -> float:
        """Buffer size for streaming operations in MB."""
        ...

    @property
    def compression_enabled(self) -> bool:
        """Whether compression is enabled for chunks."""
        ...

    @property
    def compression_level(self) -> int:
        """Compression level (0-9, 0=no compression)."""
        ...

    @property
    def timeout_per_chunk_seconds(self) -> float:
        """Timeout for individual chunk operations."""
        ...

    @property
    def retry_failed_chunks(self) -> bool:
        """Whether to retry failed chunk operations."""
        ...

    @property
    def max_retries_per_chunk(self) -> int:
        """Maximum retries for failed chunks."""
        ...

    @property
    def enable_checksum_validation(self) -> bool:
        """Whether to validate chunk checksums."""
        ...


@runtime_checkable
class ProtocolCursorPagination(Protocol):
    """
    Cursor-based pagination for large datasets.

    Provides efficient pagination for large memory collections
    with stable ordering and consistent performance.
    """

    @property
    def cursor(self) -> Optional[str]:
        """Opaque cursor for pagination position."""
        ...

    @property
    def limit(self) -> int:
        """Maximum number of items to return."""
        ...

    @property
    def sort_field(self) -> str:
        """Field to sort by for consistent ordering."""
        ...

    @property
    def sort_direction(self) -> str:
        """Sort direction (asc, desc)."""
        ...

    @property
    def filters(self) -> "ProtocolMemoryMetadata":
        """Additional filters for pagination."""
        ...

    @property
    def include_total_count(self) -> bool:
        """Whether to include total count in response."""
        ...


@runtime_checkable
class ProtocolStreamingMemoryNode(Protocol):
    """
    Streaming operations for memory content processing.

    Handles large content streaming, chunked uploads/downloads,
    and cursor-based pagination for memory operations.
    """

    async def stream_memory_content(
        self,
        memory_id: UUID,
        streaming_config: "ProtocolStreamingConfig",
        security_context: Optional["ProtocolSecurityContext"] = None,
        timeout_seconds: Optional[float] = None,
    ) -> AsyncGenerator["ProtocolStreamingChunk", None]:
        """
        Stream memory content in chunks for large data.

        Args:
            memory_id: ID of memory to stream
            streaming_config: Configuration for streaming operation
            security_context: Security context for authorization
            timeout_seconds: Optional timeout for streaming operation

        Yields:
            Streaming chunks with content data

        Raises:
            SecurityError: If user not authorized to stream content
            NotFoundError: If memory not found
            StreamingError: If streaming operation fails
            TimeoutError: If operation exceeds timeout
        """
        ...

    async def upload_memory_stream(
        self,
        content_stream: AsyncGenerator["ProtocolStreamingChunk", None],
        target_memory_id: UUID,
        streaming_config: "ProtocolStreamingConfig",
        security_context: Optional["ProtocolSecurityContext"] = None,
        timeout_seconds: Optional[float] = None,
    ) -> "ProtocolMemoryMetadata":
        """
        Upload memory content from streaming chunks.

        Args:
            content_stream: Stream of content chunks to upload
            target_memory_id: Target memory ID for upload
            streaming_config: Configuration for streaming operation
            security_context: Security context for authorization
            timeout_seconds: Optional timeout for upload operation

        Returns:
            Upload result with metadata

        Raises:
            SecurityError: If user not authorized to upload content
            ValidationError: If chunk validation fails
            StreamingError: If streaming upload fails
            TimeoutError: If operation exceeds timeout
        """
        ...

    async def paginate_memories_cursor(
        self,
        pagination_config: "ProtocolCursorPagination",
        security_context: Optional["ProtocolSecurityContext"] = None,
        timeout_seconds: Optional[float] = None,
    ) -> "ProtocolMemoryMetadata":
        """
        Paginate memory records using cursor-based pagination.

        Args:
            pagination_config: Cursor pagination configuration
            security_context: Security context for authorization
            timeout_seconds: Optional timeout for pagination operation

        Returns:
            Paginated results with next cursor and metadata

        Raises:
            SecurityError: If user not authorized to list memories
            ValidationError: If pagination config is invalid
            TimeoutError: If operation exceeds timeout
        """
        ...

    async def stream_search_results(
        self,
        search_query: str,
        streaming_config: "ProtocolStreamingConfig",
        security_context: Optional["ProtocolSecurityContext"] = None,
        timeout_seconds: Optional[float] = None,
    ) -> AsyncGenerator["ProtocolMemoryMetadata", None]:
        """
        Stream search results for large result sets.

        Args:
            search_query: Search query to execute
            streaming_config: Configuration for streaming operation
            security_context: Security context for authorization
            timeout_seconds: Optional timeout for search operation

        Yields:
            Search result records as they become available

        Raises:
            SecurityError: If user not authorized to search
            ValidationError: If search query is invalid
            SearchError: If search operation fails
            TimeoutError: If operation exceeds timeout
        """
        ...

    async def compress_memory_content(
        self,
        memory_id: UUID,
        compression_algorithm: str,
        compression_level: int = 6,
        security_context: Optional["ProtocolSecurityContext"] = None,
        timeout_seconds: Optional[float] = None,
    ) -> "ProtocolMemoryMetadata":
        """
        Compress memory content for storage optimization.

        Args:
            memory_id: ID of memory to compress
            compression_algorithm: Algorithm to use (gzip, lz4, zstd)
            compression_level: Compression level (0-9)
            security_context: Security context for authorization
            timeout_seconds: Optional timeout for compression operation

        Returns:
            Compression result with statistics

        Raises:
            SecurityError: If user not authorized to modify memory
            CompressionError: If compression operation fails
            TimeoutError: If operation exceeds timeout
        """
        ...

    async def decompress_memory_content(
        self,
        memory_id: UUID,
        security_context: Optional["ProtocolSecurityContext"] = None,
        timeout_seconds: Optional[float] = None,
    ) -> "ProtocolMemoryMetadata":
        """
        Decompress memory content for access.

        Args:
            memory_id: ID of compressed memory to decompress
            security_context: Security context for authorization
            timeout_seconds: Optional timeout for decompression operation

        Returns:
            Decompression result with statistics

        Raises:
            SecurityError: If user not authorized to access memory
            CompressionError: If decompression operation fails
            TimeoutError: If operation exceeds timeout
        """
        ...

    async def stream_embedding_vectors(
        self,
        memory_ids: list[UUID],
        vector_chunk_size: int = 1000,
        compression_enabled: bool = True,
        security_context: Optional["ProtocolSecurityContext"] = None,
        timeout_seconds: Optional[float] = None,
    ) -> AsyncGenerator["ProtocolStreamingChunk", None]:
        """
        Stream embedding vectors efficiently for large datasets.

        Args:
            memory_ids: List of memory IDs to stream vectors for
            vector_chunk_size: Number of vectors per chunk
            compression_enabled: Whether to compress vector data
            security_context: Security context for authorization
            timeout_seconds: Optional timeout for streaming operation

        Yields:
            Streaming chunks with compressed embedding vectors

        Raises:
            SecurityError: If user not authorized to stream embeddings
            NotFoundError: If memory embeddings not found
            StreamingError: If streaming operation fails
            TimeoutError: If operation exceeds timeout
        """
        ...

    async def batch_upload_embedding_vectors(
        self,
        vector_stream: AsyncGenerator["ProtocolStreamingChunk", None],
        target_memory_ids: list[UUID],
        vector_dimensions: int,
        streaming_config: "ProtocolStreamingConfig",
        security_context: Optional["ProtocolSecurityContext"] = None,
        timeout_seconds: Optional[float] = None,
    ) -> "ProtocolMemoryMetadata":
        """
        Batch upload embedding vectors from streaming chunks.

        Args:
            vector_stream: Stream of embedding vector chunks
            target_memory_ids: Target memory IDs for vectors
            vector_dimensions: Dimensions of embedding vectors
            streaming_config: Configuration for streaming operation
            security_context: Security context for authorization
            timeout_seconds: Optional timeout for upload operation

        Returns:
            Upload result with vector statistics

        Raises:
            SecurityError: If user not authorized to upload vectors
            ValidationError: If vector chunk validation fails
            StreamingError: If streaming upload fails
            TimeoutError: If operation exceeds timeout
        """
        ...


@runtime_checkable
class ProtocolMemoryCache(Protocol):
    """
    Caching protocol for memory operations performance optimization.

    Provides intelligent caching with TTL, invalidation patterns,
    and cache warming strategies for memory access optimization.
    """

    async def cache_memory(
        self,
        memory_id: UUID,
        cache_ttl_seconds: int = 3600,
        cache_level: str = "L1",
        security_context: Optional["ProtocolSecurityContext"] = None,
    ) -> "ProtocolMemoryMetadata":
        """
        Cache memory content for faster access.

        Args:
            memory_id: ID of memory to cache
            cache_ttl_seconds: Time-to-live for cache entry
            cache_level: Cache level (L1, L2, L3)
            security_context: Security context for authorization

        Returns:
            Cache operation result

        Raises:
            SecurityError: If user not authorized to cache memory
            CacheError: If caching operation fails
        """
        ...

    async def invalidate_cache(
        self,
        memory_id: UUID,
        invalidation_scope: str = "single",
        security_context: Optional["ProtocolSecurityContext"] = None,
    ) -> "ProtocolMemoryMetadata":
        """
        Invalidate cached memory content.

        Args:
            memory_id: ID of memory to invalidate
            invalidation_scope: Scope of invalidation (single, related, all)
            security_context: Security context for authorization

        Returns:
            Cache invalidation result

        Raises:
            SecurityError: If user not authorized to invalidate cache
            CacheError: If invalidation operation fails
        """
        ...

    async def warm_cache(
        self,
        memory_ids: list[UUID],
        warming_strategy: str = "predictive",
        security_context: Optional["ProtocolSecurityContext"] = None,
        timeout_seconds: Optional[float] = None,
    ) -> "ProtocolMemoryMetadata":
        """
        Warm cache with frequently accessed memories.

        Args:
            memory_ids: List of memory IDs to warm
            warming_strategy: Strategy for cache warming
            security_context: Security context for authorization
            timeout_seconds: Optional timeout for warming operation

        Returns:
            Cache warming result with statistics

        Raises:
            SecurityError: If user not authorized to warm cache
            CacheError: If warming operation fails
            TimeoutError: If operation exceeds timeout
        """
        ...

    async def get_cache_stats(
        self,
        cache_scope: str = "user",
        security_context: Optional["ProtocolSecurityContext"] = None,
    ) -> "ProtocolMemoryMetadata":
        """
        Get cache performance statistics.

        Args:
            cache_scope: Scope for statistics (user, global, memory_id)
            security_context: Security context for authorization

        Returns:
            Cache statistics and performance metrics

        Raises:
            SecurityError: If user not authorized to view cache stats
        """
        ...


@runtime_checkable
class ProtocolPerformanceOptimization(Protocol):
    """
    Performance optimization protocol for memory operations.

    Provides performance monitoring, optimization suggestions,
    and automated optimization for memory operations.
    """

    async def analyze_performance_patterns(
        self,
        operation_types: list[str],
        time_window_hours: int = 24,
        security_context: Optional["ProtocolSecurityContext"] = None,
        timeout_seconds: Optional[float] = None,
    ) -> "ProtocolMemoryMetadata":
        """
        Analyze performance patterns for optimization.

        Args:
            operation_types: Types of operations to analyze
            time_window_hours: Time window for analysis
            security_context: Security context for authorization
            timeout_seconds: Optional timeout for analysis operation

        Returns:
            Performance analysis results with optimization suggestions

        Raises:
            SecurityError: If user not authorized to view performance data
            AnalysisError: If performance analysis fails
            TimeoutError: If operation exceeds timeout
        """
        ...

    async def optimize_memory_access_patterns(
        self,
        memory_ids: list[UUID],
        optimization_strategy: str = "adaptive",
        security_context: Optional["ProtocolSecurityContext"] = None,
        timeout_seconds: Optional[float] = None,
    ) -> "ProtocolMemoryMetadata":
        """
        Optimize access patterns for specified memories.

        Args:
            memory_ids: Memory IDs to optimize access for
            optimization_strategy: Strategy for optimization
            security_context: Security context for authorization
            timeout_seconds: Optional timeout for optimization operation

        Returns:
            Optimization results with performance improvements

        Raises:
            SecurityError: If user not authorized to optimize memories
            OptimizationError: If optimization operation fails
            TimeoutError: If operation exceeds timeout
        """
        ...

    async def create_performance_baseline(
        self,
        operation_type: str,
        baseline_duration_hours: int = 168,  # 1 week
        security_context: Optional["ProtocolSecurityContext"] = None,
        timeout_seconds: Optional[float] = None,
    ) -> "ProtocolMemoryMetadata":
        """
        Create performance baseline for operation type.

        Args:
            operation_type: Type of operation for baseline
            baseline_duration_hours: Duration for baseline collection
            security_context: Security context for authorization
            timeout_seconds: Optional timeout for baseline creation

        Returns:
            Performance baseline data and metrics

        Raises:
            SecurityError: If user not authorized to create baselines
            BaselineError: If baseline creation fails
            TimeoutError: If operation exceeds timeout
        """
        ...
