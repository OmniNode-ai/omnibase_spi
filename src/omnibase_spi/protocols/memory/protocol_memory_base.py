"""
Pure Base Type Definitions for OmniMemory ONEX Architecture

This module defines foundational type literals and core memory protocols that
serve as the base layer for the memory domain. These types have no dependencies
on other memory protocol modules, preventing circular imports.

Contains:
- Type literals for constrained values (access levels, analysis types, etc.)
- Core memory protocols (metadata, records, search filters)
- Base data structure protocols

All types are pure protocols with no implementation dependencies.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Optional, Protocol, runtime_checkable
from uuid import UUID

if TYPE_CHECKING:
    from datetime import datetime


# === TYPE LITERALS ===

# Memory access levels for security and authorization
LiteralMemoryAccessLevel = Literal[
    "public", "private", "internal", "restricted", "confidential"
]

# Analysis types for memory processing
LiteralAnalysisType = Literal[
    "standard", "deep", "quick", "semantic", "pattern", "performance"
]

# Compression algorithms for memory optimization
LiteralCompressionAlgorithm = Literal["gzip", "lz4", "zstd", "brotli", "deflate"]

# Error categories for better error handling
LiteralErrorCategory = Literal["transient", "permanent", "validation", "authorization"]

# Agent status types for workflow coordination
LiteralAgentStatus = Literal[
    "active", "inactive", "processing", "completed", "failed", "timeout"
]

# Workflow execution status types
LiteralWorkflowStatus = Literal[
    "pending", "running", "completed", "failed", "cancelled", "timeout"
]


# === CORE MEMORY PROTOCOLS ===


@runtime_checkable
class ProtocolMemoryMetadata(Protocol):
    """Protocol for memory metadata structures."""

    @property
    def metadata_keys(self) -> list[str]:
        """Available metadata keys."""
        ...

    def get_metadata_value(self, key: str) -> Optional[str]:
        """Get metadata value by key."""
        ...

    def has_metadata_key(self, key: str) -> bool:
        """Check if metadata key exists."""
        ...


@runtime_checkable
class ProtocolWorkflowConfiguration(Protocol):
    """Protocol for workflow configuration structures."""

    @property
    def configuration_keys(self) -> list[str]:
        """Available configuration keys."""
        ...

    def get_configuration_value(self, key: str) -> Optional[str]:
        """Get configuration value by key."""
        ...

    def validate_configuration(self) -> bool:
        """Validate configuration completeness."""
        ...


@runtime_checkable
class ProtocolAnalysisParameters(Protocol):
    """Protocol for analysis parameter structures."""

    @property
    def parameter_keys(self) -> list[str]:
        """Available parameter keys."""
        ...

    def get_parameter_value(self, key: str) -> Optional[str]:
        """Get parameter value by key."""
        ...

    def validate_parameters(self) -> bool:
        """Validate parameter completeness."""
        ...


@runtime_checkable
class ProtocolAggregationCriteria(Protocol):
    """Protocol for aggregation criteria structures."""

    @property
    def criteria_keys(self) -> list[str]:
        """Available criteria keys."""
        ...

    def get_criteria_value(self, key: str) -> Optional[str]:
        """Get criteria value by key."""
        ...

    def validate_criteria(self) -> bool:
        """Validate criteria completeness."""
        ...


@runtime_checkable
class ProtocolCoordinationMetadata(Protocol):
    """Protocol for coordination metadata structures."""

    @property
    def metadata_keys(self) -> list[str]:
        """Available metadata keys."""
        ...

    def get_metadata_value(self, key: str) -> Optional[str]:
        """Get metadata value by key."""
        ...

    def validate_metadata(self) -> bool:
        """Validate metadata completeness."""
        ...


@runtime_checkable
class ProtocolAnalysisResults(Protocol):
    """Protocol for analysis result structures."""

    @property
    def result_keys(self) -> list[str]:
        """Available result keys."""
        ...

    def get_result_value(self, key: str) -> Optional[str]:
        """Get result value by key."""
        ...

    def has_result_key(self, key: str) -> bool:
        """Check if result key exists."""
        ...


@runtime_checkable
class ProtocolAggregatedData(Protocol):
    """Protocol for aggregated data structures."""

    @property
    def data_keys(self) -> list[str]:
        """Available data keys."""
        ...

    def get_data_value(self, key: str) -> Optional[str]:
        """Get data value by key."""
        ...

    def validate_data(self) -> bool:
        """Validate data completeness."""
        ...


@runtime_checkable
class ProtocolErrorContext(Protocol):
    """Protocol for error context structures."""

    @property
    def context_keys(self) -> list[str]:
        """Available context keys."""
        ...

    def get_context_value(self, key: str) -> Optional[str]:
        """Get context value by key."""
        ...

    def add_context(self, key: str, value: str) -> None:
        """Add context information."""
        ...


@runtime_checkable
class ProtocolPageInfo(Protocol):
    """Protocol for pagination information structures."""

    @property
    def info_keys(self) -> list[str]:
        """Available info keys."""
        ...

    def get_info_value(self, key: str) -> Optional[str]:
        """Get info value by key."""
        ...

    def has_next_page(self) -> bool:
        """Check if next page exists."""
        ...


@runtime_checkable
class ProtocolCustomMetrics(Protocol):
    """Protocol for custom metrics structures."""

    @property
    def metric_names(self) -> list[str]:
        """Available metric names."""
        ...

    def get_metric_value(self, name: str) -> Optional[float]:
        """Get metric value by name."""
        ...

    def has_metric(self, name: str) -> bool:
        """Check if metric exists."""
        ...


@runtime_checkable
class ProtocolAggregationSummary(Protocol):
    """Protocol for aggregation summary structures."""

    @property
    def summary_keys(self) -> list[str]:
        """Available summary keys."""
        ...

    def get_summary_value(self, key: str) -> Optional[float]:
        """Get summary value by key."""
        ...

    def calculate_total(self) -> float:
        """Calculate total aggregated value."""
        ...


@runtime_checkable
class ProtocolMemoryRecordData(Protocol):
    """Protocol for memory record data structures."""

    @property
    def data_keys(self) -> list[str]:
        """Available data keys."""
        ...

    def get_data_value(self, key: str) -> Optional[str]:
        """Get data value by key."""
        ...

    def validate_record_data(self) -> bool:
        """Validate record data completeness."""
        ...


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
    expires_at: Optional["datetime"]

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
    date_range_start: Optional["datetime"]
    date_range_end: Optional["datetime"]

    @property
    def tags(self) -> Optional[list[str]]:
        """Filter tags for search."""
        ...


@runtime_checkable
class ProtocolAgentStatusMap(Protocol):
    """Protocol for agent status mapping structures."""

    @property
    def agent_ids(self) -> list[UUID]:
        """List of agent IDs in the status map."""
        ...

    def get_agent_status(self, agent_id: UUID) -> Optional[str]:
        """Get status for a specific agent."""
        ...

    def set_agent_status(self, agent_id: UUID, status: str) -> None:
        """Set status for a specific agent."""
        ...

    def get_all_statuses(self) -> dict[UUID, str]:
        """Get all agent statuses as a dict."""
        ...


@runtime_checkable
class ProtocolAgentResponseMap(Protocol):
    """Protocol for agent response mapping structures."""

    @property
    def responding_agents(self) -> list[UUID]:
        """List of agents that have responded."""
        ...

    def get_agent_response(self, agent_id: UUID) -> Optional[str]:
        """Get response from a specific agent."""
        ...

    def add_agent_response(self, agent_id: UUID, response: str) -> None:
        """Add response from an agent."""
        ...

    def get_all_responses(self) -> dict[UUID, str]:
        """Get all agent responses as a dict."""
        ...


@runtime_checkable
class ProtocolErrorCategoryMap(Protocol):
    """Protocol for error category counting structures."""

    @property
    def category_names(self) -> list[str]:
        """List of error category names."""
        ...

    def get_category_count(self, category: str) -> int:
        """Get count for a specific error category."""
        ...

    def increment_category(self, category: str) -> None:
        """Increment count for an error category."""
        ...

    def get_all_counts(self) -> dict[str, int]:
        """Get all category counts as a dict."""
        ...
