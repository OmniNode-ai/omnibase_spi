"""
Streaming protocol definitions for OmniMemory operations.

Defines streaming protocols for large data operations, chunked processing,
and cursor-based pagination following ONEX performance optimization patterns.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING, Protocol, runtime_checkable
from uuid import UUID

if TYPE_CHECKING:
    from omnibase_spi.protocols.memory.protocol_memory_base import (
        ProtocolMemoryMetadata,
    )
    from omnibase_spi.protocols.memory.protocol_memory_security import (
        ProtocolMemorySecurityContext,
    )


@runtime_checkable
class ProtocolStreamingChunk(Protocol):
    """
    Protocol for streaming data chunks.

    Represents individual chunks in a streaming operation with
    metadata for reconstruction and error handling.
    """

    @property
    def chunk_id(self) -> UUID: ...

    @property
    def stream_id(self) -> UUID: ...

    @property
    def sequence_number(self) -> int: ...

    @property
    def total_chunks(self) -> int | None: ...

    @property
    def chunk_data(self) -> bytes: ...

    @property
    def chunk_size(self) -> int: ...

    @property
    def is_final_chunk(self) -> bool: ...

    @property
    def checksum(self) -> str: ...

    @property
    def compression_type(self) -> str | None: ...

    async def chunk_metadata(self) -> ProtocolMemoryMetadata: ...


@runtime_checkable
class ProtocolStreamingConfig(Protocol):
    """
    Configuration for streaming operations.

    Defines parameters for chunking, compression, buffering,
    and streaming behavior optimization.
    """

    @property
    def chunk_size_bytes(self) -> int: ...

    @property
    def max_concurrent_chunks(self) -> int: ...

    @property
    def buffer_size_mb(self) -> float: ...

    @property
    def compression_enabled(self) -> bool: ...

    @property
    def compression_level(self) -> int: ...

    @property
    def timeout_per_chunk_seconds(self) -> float: ...

    @property
    def retry_failed_chunks(self) -> bool: ...

    @property
    def max_retries_per_chunk(self) -> int: ...

    @property
    def enable_checksum_validation(self) -> bool: ...


@runtime_checkable
class ProtocolCursorPagination(Protocol):
    """
    Cursor-based pagination for large datasets.

    Provides efficient pagination for large memory collections
    with stable ordering and consistent performance.
    """

    @property
    def cursor(self) -> str | None: ...

    @property
    def limit(self) -> int: ...

    @property
    def sort_field(self) -> str: ...

    @property
    def sort_direction(self) -> str: ...

    async def filters(self) -> ProtocolMemoryMetadata: ...

    @property
    def include_total_count(self) -> bool: ...


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
        streaming_config: ProtocolStreamingConfig,
        security_context: ProtocolMemorySecurityContext | None = None,
        timeout_seconds: float | None = None,
    ) -> AsyncGenerator[ProtocolStreamingChunk, None]: ...

    async def upload_memory_stream(
        self,
        content_stream: AsyncGenerator[ProtocolStreamingChunk, None],
        target_memory_id: UUID,
        streaming_config: ProtocolStreamingConfig,
        security_context: ProtocolMemorySecurityContext | None = None,
        timeout_seconds: float | None = None,
    ) -> ProtocolMemoryMetadata: ...

    async def paginate_memories_cursor(
        self,
        pagination_config: ProtocolCursorPagination,
        security_context: ProtocolMemorySecurityContext | None = None,
        timeout_seconds: float | None = None,
    ) -> ProtocolMemoryMetadata: ...

    async def stream_search_results(
        self,
        search_query: str,
        streaming_config: ProtocolStreamingConfig,
        security_context: ProtocolMemorySecurityContext | None = None,
        timeout_seconds: float | None = None,
    ) -> AsyncGenerator[ProtocolMemoryMetadata, None]: ...

    async def compress_memory_content(
        self,
        memory_id: UUID,
        compression_algorithm: str,
        compression_level: int,
        security_context: ProtocolMemorySecurityContext | None = None,
        timeout_seconds: float | None = None,
    ) -> ProtocolMemoryMetadata: ...

    async def decompress_memory_content(
        self,
        memory_id: UUID,
        security_context: ProtocolMemorySecurityContext | None = None,
        timeout_seconds: float | None = None,
    ) -> ProtocolMemoryMetadata: ...

    async def stream_embedding_vectors(
        self,
        memory_ids: list[UUID],
        vector_chunk_size: int,
        compression_enabled: bool,
        security_context: ProtocolMemorySecurityContext | None = None,
        timeout_seconds: float | None = None,
    ) -> AsyncGenerator[ProtocolStreamingChunk, None]: ...

    async def batch_upload_embedding_vectors(
        self,
        vector_stream: AsyncGenerator[ProtocolStreamingChunk, None],
        target_memory_ids: list[UUID],
        vector_dimensions: int,
        streaming_config: ProtocolStreamingConfig,
        security_context: ProtocolMemorySecurityContext | None = None,
        timeout_seconds: float | None = None,
    ) -> ProtocolMemoryMetadata: ...


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
        cache_ttl_seconds: int,
        cache_level: str,
        security_context: ProtocolMemorySecurityContext | None = None,
    ) -> ProtocolMemoryMetadata: ...

    async def invalidate_cache(
        self,
        memory_id: UUID,
        invalidation_scope: str,
        security_context: ProtocolMemorySecurityContext | None = None,
    ) -> ProtocolMemoryMetadata: ...

    async def warm_cache(
        self,
        memory_ids: list[UUID],
        warming_strategy: str,
        security_context: ProtocolMemorySecurityContext | None = None,
        timeout_seconds: float | None = None,
    ) -> ProtocolMemoryMetadata: ...

    async def get_cache_stats(
        self,
        cache_scope: str,
        security_context: ProtocolMemorySecurityContext | None = None,
    ) -> ProtocolMemoryMetadata: ...


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
        time_window_hours: int,
        security_context: ProtocolMemorySecurityContext | None = None,
        timeout_seconds: float | None = None,
    ) -> ProtocolMemoryMetadata: ...

    async def optimize_memory_access_patterns(
        self,
        memory_ids: list[UUID],
        optimization_strategy: str,
        security_context: ProtocolMemorySecurityContext | None = None,
        timeout_seconds: float | None = None,
    ) -> ProtocolMemoryMetadata: ...

    async def create_performance_baseline(
        self,
        operation_type: str,
        baseline_duration_hours: int,
        security_context: ProtocolMemorySecurityContext | None = None,
        timeout_seconds: float | None = None,
    ) -> ProtocolMemoryMetadata: ...
