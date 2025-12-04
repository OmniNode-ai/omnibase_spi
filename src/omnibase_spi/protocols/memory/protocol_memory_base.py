"""
Pure Base Type Definitions for OmniMemory ONEX Architecture

This module defines foundational type literals and core memory protocols that
serve as the base layer for the memory domain. These types have no dependencies
on other memory protocol modules, preventing circular imports.

Contains:
    - Type literals for constrained values (access levels, analysis types, etc.)
    - Core memory protocols (metadata, records, search filters)
    - Base key-value store protocols

All types are pure protocols with no implementation dependencies.

Note: Data structure protocols (analysis results, aggregation, agent maps) have
been moved to protocol_memory_data_types.py but are re-exported here for
backward compatibility.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Protocol, runtime_checkable
from uuid import UUID

# Re-export from protocol_memory_data_types for backward compatibility
from omnibase_spi.protocols.memory.protocol_memory_data_types import (
    ProtocolAgentResponseMap,
    ProtocolAgentStatusMap,
    ProtocolAggregatedData,
    ProtocolAggregationSummary,
    ProtocolAnalysisResults,
    ProtocolCustomMetrics,
    ProtocolErrorCategoryMap,
    ProtocolMemoryErrorContext,
    ProtocolPageInfo,
)

if TYPE_CHECKING:
    from datetime import datetime

# Type literals for constrained values
LiteralMemoryAccessLevel = Literal[
    "public", "private", "internal", "restricted", "confidential"
]
LiteralAnalysisType = Literal[
    "standard", "deep", "quick", "semantic", "pattern", "performance"
]
LiteralCompressionAlgorithm = Literal["gzip", "lz4", "zstd", "brotli", "deflate"]
LiteralErrorCategory = Literal["transient", "permanent", "validation", "authorization"]
LiteralAgentStatus = Literal[
    "active", "inactive", "processing", "completed", "failed", "timeout"
]
LiteralWorkflowStatus = Literal[
    "pending", "running", "completed", "failed", "cancelled", "timeout"
]


@runtime_checkable
class ProtocolKeyValueStore(Protocol):
    """Base protocol for key-value storage structures with validation."""

    @property
    def keys(self) -> list[str]: ...

    async def get_value(self, key: str) -> str | None: ...

    def has_key(self, key: str) -> bool: ...

    async def validate_store(self) -> bool: ...


@runtime_checkable
class ProtocolMemoryMetadata(ProtocolKeyValueStore, Protocol):
    """Protocol for memory metadata structures."""

    @property
    def metadata_keys(self) -> list[str]: ...

    async def get_metadata_value(self, key: str) -> str | None: ...

    def has_metadata_key(self, key: str) -> bool: ...


@runtime_checkable
class ProtocolWorkflowConfiguration(ProtocolKeyValueStore, Protocol):
    """Protocol for workflow configuration structures."""

    @property
    def configuration_keys(self) -> list[str]: ...

    async def get_configuration_value(self, key: str) -> str | None: ...

    async def validate_configuration(self) -> bool: ...


@runtime_checkable
class ProtocolAnalysisParameters(ProtocolKeyValueStore, Protocol):
    """Protocol for analysis parameter structures."""

    @property
    def parameter_keys(self) -> list[str]: ...

    async def get_parameter_value(self, key: str) -> str | None: ...

    async def validate_parameters(self) -> bool: ...


@runtime_checkable
class ProtocolAggregationCriteria(ProtocolKeyValueStore, Protocol):
    """Protocol for aggregation criteria structures."""

    @property
    def criteria_keys(self) -> list[str]: ...

    async def get_criteria_value(self, key: str) -> str | None: ...

    async def validate_criteria(self) -> bool: ...


@runtime_checkable
class ProtocolCoordinationMetadata(Protocol):
    """Protocol for coordination metadata structures."""

    @property
    def metadata_keys(self) -> list[str]: ...

    async def get_metadata_value(self, key: str) -> str | None: ...

    async def validate_metadata(self) -> bool: ...


@runtime_checkable
class ProtocolMemoryRecord(Protocol):
    """Protocol for memory record data structure."""

    memory_id: UUID
    content: str
    content_type: str
    created_at: "datetime"
    updated_at: "datetime"
    access_level: LiteralMemoryAccessLevel
    source_agent: str
    expires_at: "datetime | None"

    @property
    def embedding(self) -> list[float] | None: ...

    @property
    def related_memories(self) -> list[UUID]: ...


@runtime_checkable
class ProtocolSearchResult(Protocol):
    """Protocol for search result data structure."""

    memory_record: "ProtocolMemoryRecord"
    relevance_score: float
    match_type: str

    @property
    def highlighted_content(self) -> str | None: ...


@runtime_checkable
class ProtocolSearchFilters(Protocol):
    """Protocol for search filter specifications."""

    content_types: list[str] | None
    access_levels: list[str] | None
    source_agents: list[str] | None
    date_range_start: "datetime | None"
    date_range_end: "datetime | None"

    @property
    def tags(self) -> list[str] | None: ...


# Backward compatibility exports
__all__ = [
    # Type literals
    "LiteralMemoryAccessLevel",
    "LiteralAnalysisType",
    "LiteralCompressionAlgorithm",
    "LiteralErrorCategory",
    "LiteralAgentStatus",
    "LiteralWorkflowStatus",
    # Core protocols (defined here)
    "ProtocolKeyValueStore",
    "ProtocolMemoryMetadata",
    "ProtocolWorkflowConfiguration",
    "ProtocolAnalysisParameters",
    "ProtocolAggregationCriteria",
    "ProtocolCoordinationMetadata",
    "ProtocolMemoryRecord",
    "ProtocolSearchResult",
    "ProtocolSearchFilters",
    # Re-exported from protocol_memory_data_types
    "ProtocolAnalysisResults",
    "ProtocolAggregatedData",
    "ProtocolMemoryErrorContext",
    "ProtocolPageInfo",
    "ProtocolCustomMetrics",
    "ProtocolAggregationSummary",
    "ProtocolAgentStatusMap",
    "ProtocolAgentResponseMap",
    "ProtocolErrorCategoryMap",
]
