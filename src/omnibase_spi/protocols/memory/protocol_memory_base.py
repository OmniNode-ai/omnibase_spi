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
    """
    Base protocol for key-value storage structures with validation support.

    This protocol defines the foundational interface for all key-value based
    data structures in the memory domain. It provides a consistent API for
    accessing, querying, and validating stored key-value pairs.

    Implementations should ensure thread-safe access and support validation
    of stored data integrity.

    Example:
        ```python
        class SimpleKeyValueStore:
            '''Concrete implementation of ProtocolKeyValueStore.'''

            def __init__(self) -> None:
                self._data: dict[str, str] = {}

            @property
            def keys(self) -> list[str]:
                return list(self._data.keys())

            async def get_value(self, key: str) -> str | None:
                return self._data.get(key)

            def has_key(self, key: str) -> bool:
                return key in self._data

            async def validate_store(self) -> bool:
                return all(isinstance(v, str) for v in self._data.values())

        # Usage
        store = SimpleKeyValueStore()
        store._data["key1"] = "value1"
        assert isinstance(store, ProtocolKeyValueStore)
        assert store.has_key("key1")
        ```

    See Also:
        - ProtocolMemoryMetadata: Extends this for memory metadata.
        - ProtocolWorkflowConfiguration: Extends this for workflow config.
    """

    @property
    def keys(self) -> list[str]: ...

    async def get_value(self, key: str) -> str | None: ...

    def has_key(self, key: str) -> bool: ...

    async def validate_store(self) -> bool: ...


@runtime_checkable
class ProtocolMemoryMetadata(ProtocolKeyValueStore, Protocol):
    """
    Protocol for memory metadata structures extending key-value storage.

    This protocol defines the interface for storing and accessing metadata
    associated with memory records. Metadata includes custom attributes,
    tags, and operational information about memories.

    Implementations should provide efficient access to metadata and support
    the full key-value store interface for flexibility.

    Example:
        ```python
        class MemoryMetadata:
            '''Concrete implementation of ProtocolMemoryMetadata.'''

            def __init__(self) -> None:
                self._metadata: dict[str, str] = {}

            @property
            def keys(self) -> list[str]:
                return list(self._metadata.keys())

            @property
            def metadata_keys(self) -> list[str]:
                return list(self._metadata.keys())

            async def get_value(self, key: str) -> str | None:
                return self._metadata.get(key)

            async def get_metadata_value(self, key: str) -> str | None:
                return self._metadata.get(key)

            def has_key(self, key: str) -> bool:
                return key in self._metadata

            def has_metadata_key(self, key: str) -> bool:
                return key in self._metadata

            async def validate_store(self) -> bool:
                return True

        # Usage
        metadata = MemoryMetadata()
        metadata._metadata["author"] = "agent-1"
        metadata._metadata["version"] = "1.0"
        assert isinstance(metadata, ProtocolMemoryMetadata)
        ```

    See Also:
        - ProtocolMemoryRecord: Uses this for record metadata.
        - ProtocolKeyValueStore: Base protocol for key-value access.
    """

    @property
    def metadata_keys(self) -> list[str]: ...

    async def get_metadata_value(self, key: str) -> str | None: ...

    def has_metadata_key(self, key: str) -> bool: ...


@runtime_checkable
class ProtocolWorkflowConfiguration(ProtocolKeyValueStore, Protocol):
    """
    Protocol for workflow configuration structures in multi-agent operations.

    This protocol defines the interface for storing and accessing workflow
    configuration parameters. Configuration controls workflow behavior,
    agent selection, and execution settings.

    Implementations should validate configuration completeness and provide
    secure access to sensitive configuration values.

    Example:
        ```python
        class WorkflowConfiguration:
            '''Concrete implementation of ProtocolWorkflowConfiguration.'''

            def __init__(self) -> None:
                self._config: dict[str, str] = {}

            @property
            def keys(self) -> list[str]:
                return list(self._config.keys())

            @property
            def configuration_keys(self) -> list[str]:
                return list(self._config.keys())

            async def get_value(self, key: str) -> str | None:
                return self._config.get(key)

            async def get_configuration_value(self, key: str) -> str | None:
                return self._config.get(key)

            def has_key(self, key: str) -> bool:
                return key in self._config

            async def validate_store(self) -> bool:
                return await self.validate_configuration()

            async def validate_configuration(self) -> bool:
                required = ["workflow_type", "timeout"]
                return all(k in self._config for k in required)

        # Usage
        config = WorkflowConfiguration()
        config._config["workflow_type"] = "sync"
        config._config["timeout"] = "300"
        assert isinstance(config, ProtocolWorkflowConfiguration)
        ```

    See Also:
        - ProtocolWorkflowExecutionRequest: Uses this for workflow parameters.
    """

    @property
    def configuration_keys(self) -> list[str]: ...

    async def get_configuration_value(self, key: str) -> str | None: ...

    async def validate_configuration(self) -> bool: ...


@runtime_checkable
class ProtocolAnalysisParameters(ProtocolKeyValueStore, Protocol):
    """
    Protocol for analysis parameter structures in pattern analysis operations.

    This protocol defines the interface for storing and accessing parameters
    that control pattern analysis behavior. Parameters include sensitivity
    thresholds, scope definitions, and algorithm selections.

    Implementations should validate parameter ranges and compatibility
    to ensure valid analysis configurations.

    Example:
        ```python
        class AnalysisParameters:
            '''Concrete implementation of ProtocolAnalysisParameters.'''

            def __init__(self) -> None:
                self._params: dict[str, str] = {}

            @property
            def keys(self) -> list[str]:
                return list(self._params.keys())

            @property
            def parameter_keys(self) -> list[str]:
                return list(self._params.keys())

            async def get_value(self, key: str) -> str | None:
                return self._params.get(key)

            async def get_parameter_value(self, key: str) -> str | None:
                return self._params.get(key)

            def has_key(self, key: str) -> bool:
                return key in self._params

            async def validate_store(self) -> bool:
                return await self.validate_parameters()

            async def validate_parameters(self) -> bool:
                if "threshold" in self._params:
                    threshold = float(self._params["threshold"])
                    return 0.0 <= threshold <= 1.0
                return True

        # Usage
        params = AnalysisParameters()
        params._params["threshold"] = "0.75"
        params._params["algorithm"] = "semantic"
        assert isinstance(params, ProtocolAnalysisParameters)
        ```

    See Also:
        - ProtocolPatternAnalysisRequest: Uses this for analysis configuration.
    """

    @property
    def parameter_keys(self) -> list[str]: ...

    async def get_parameter_value(self, key: str) -> str | None: ...

    async def validate_parameters(self) -> bool: ...


@runtime_checkable
class ProtocolAggregationCriteria(ProtocolKeyValueStore, Protocol):
    """
    Protocol for aggregation criteria structures in memory aggregation.

    This protocol defines the interface for storing and accessing criteria
    that control aggregation operations. Criteria specify which memories
    to include, grouping dimensions, and aggregation functions to apply.

    Implementations should validate criteria completeness and logical
    consistency before aggregation execution.

    Example:
        ```python
        class AggregationCriteria:
            '''Concrete implementation of ProtocolAggregationCriteria.'''

            def __init__(self) -> None:
                self._criteria: dict[str, str] = {}

            @property
            def keys(self) -> list[str]:
                return list(self._criteria.keys())

            @property
            def criteria_keys(self) -> list[str]:
                return list(self._criteria.keys())

            async def get_value(self, key: str) -> str | None:
                return self._criteria.get(key)

            async def get_criteria_value(self, key: str) -> str | None:
                return self._criteria.get(key)

            def has_key(self, key: str) -> bool:
                return key in self._criteria

            async def validate_store(self) -> bool:
                return await self.validate_criteria()

            async def validate_criteria(self) -> bool:
                required = ["aggregation_function", "group_by"]
                return all(k in self._criteria for k in required)

        # Usage
        criteria = AggregationCriteria()
        criteria._criteria["aggregation_function"] = "sum"
        criteria._criteria["group_by"] = "content_type"
        assert isinstance(criteria, ProtocolAggregationCriteria)
        ```

    See Also:
        - ProtocolAggregationRequest: Uses this for aggregation specification.
    """

    @property
    def criteria_keys(self) -> list[str]: ...

    async def get_criteria_value(self, key: str) -> str | None: ...

    async def validate_criteria(self) -> bool: ...


@runtime_checkable
class ProtocolCoordinationMetadata(Protocol):
    """
    Protocol for coordination metadata structures in agent coordination.

    This protocol defines the interface for storing and accessing metadata
    about coordination operations. Metadata includes coordination parameters,
    agent identifiers, and synchronization information.

    Implementations should support validation of metadata consistency and
    provide secure access to coordination details.

    Example:
        ```python
        class CoordinationMetadata:
            '''Concrete implementation of ProtocolCoordinationMetadata.'''

            def __init__(self) -> None:
                self._metadata: dict[str, str] = {}

            @property
            def metadata_keys(self) -> list[str]:
                return list(self._metadata.keys())

            async def get_metadata_value(self, key: str) -> str | None:
                return self._metadata.get(key)

            async def validate_metadata(self) -> bool:
                required = ["coordination_type", "agent_count"]
                return all(k in self._metadata for k in required)

        # Usage
        metadata = CoordinationMetadata()
        metadata._metadata["coordination_type"] = "synchronous"
        metadata._metadata["agent_count"] = "3"
        assert isinstance(metadata, ProtocolCoordinationMetadata)
        ```

    See Also:
        - ProtocolAgentCoordinationRequest: Uses this for coordination metadata.
    """

    @property
    def metadata_keys(self) -> list[str]: ...

    async def get_metadata_value(self, key: str) -> str | None: ...

    async def validate_metadata(self) -> bool: ...


@runtime_checkable
class ProtocolMemoryRecord(Protocol):
    """
    Protocol for memory record data structure representing stored memories.

    This protocol defines the interface for individual memory records in
    the memory system. Each record contains content, metadata, access control,
    and relationship information for memory retrieval and management.

    Implementations should support efficient serialization and provide
    secure access based on the defined access level.

    Attributes:
        memory_id: Unique identifier for this memory record.
        content: The actual memory content as a string.
        content_type: MIME type or content classification.
        created_at: When the memory was first created.
        updated_at: When the memory was last modified.
        access_level: Access control level for this memory.
        source_agent: Identifier of the agent that created this memory.
        expires_at: Optional expiration timestamp.

    Example:
        ```python
        class MemoryRecord:
            '''Concrete implementation of ProtocolMemoryRecord.'''

            def __init__(
                self,
                memory_id: UUID,
                content: str,
                content_type: str,
                source_agent: str,
            ) -> None:
                self.memory_id = memory_id
                self.content = content
                self.content_type = content_type
                self.created_at = datetime.now(UTC)
                self.updated_at = datetime.now(UTC)
                self.access_level: LiteralMemoryAccessLevel = "internal"
                self.source_agent = source_agent
                self.expires_at = None
                self._embedding: list[float] | None = None
                self._related: list[UUID] = []

            @property
            def embedding(self) -> list[float] | None:
                return self._embedding

            @property
            def related_memories(self) -> list[UUID]:
                return self._related

        # Usage
        record = MemoryRecord(
            memory_id=uuid4(),
            content="Important memory content",
            content_type="text/plain",
            source_agent="agent-1",
        )
        assert isinstance(record, ProtocolMemoryRecord)
        ```

    See Also:
        - ProtocolMemoryRetrieveResponse: Returns memory records.
        - ProtocolSearchResult: Wraps records with relevance information.
    """

    memory_id: UUID
    content: str
    content_type: str
    created_at: datetime
    updated_at: datetime
    access_level: LiteralMemoryAccessLevel
    source_agent: str
    expires_at: datetime | None

    @property
    def embedding(self) -> list[float] | None: ...

    @property
    def related_memories(self) -> list[UUID]: ...


@runtime_checkable
class ProtocolSearchResult(Protocol):
    """
    Protocol for search result data structure in semantic search operations.

    This protocol defines the interface for individual search results
    returned from memory searches. Each result wraps a memory record
    with relevance scoring and match type information.

    Implementations should provide accurate relevance scores and support
    optional content highlighting for search result display.

    Attributes:
        memory_record: The matched memory record.
        relevance_score: Similarity score between 0.0 and 1.0.
        match_type: Type of match (e.g., 'exact', 'semantic', 'fuzzy').

    Example:
        ```python
        class SearchResult:
            '''Concrete implementation of ProtocolSearchResult.'''

            def __init__(
                self,
                memory_record: ProtocolMemoryRecord,
                relevance_score: float,
                match_type: str,
            ) -> None:
                self.memory_record = memory_record
                self.relevance_score = relevance_score
                self.match_type = match_type
                self._highlighted: str | None = None

            @property
            def highlighted_content(self) -> str | None:
                return self._highlighted

        # Usage
        result = SearchResult(
            memory_record=record,
            relevance_score=0.92,
            match_type="semantic",
        )
        assert isinstance(result, ProtocolSearchResult)
        assert result.relevance_score > 0.9
        ```

    See Also:
        - ProtocolSemanticSearchResponse: Returns lists of search results.
        - ProtocolMemoryRecord: The wrapped memory record type.
    """

    memory_record: ProtocolMemoryRecord
    relevance_score: float
    match_type: str

    @property
    def highlighted_content(self) -> str | None: ...


@runtime_checkable
class ProtocolSearchFilters(Protocol):
    """
    Protocol for search filter specifications in memory search operations.

    This protocol defines the interface for specifying filters that constrain
    memory search results. Filters can restrict by content type, access level,
    source agent, date range, and tags.

    Implementations should support combining multiple filter criteria with
    logical AND semantics and handle None values as "no restriction".

    Attributes:
        content_types: Filter by content types (None = all types).
        access_levels: Filter by access levels (None = all levels).
        source_agents: Filter by source agent IDs (None = all agents).
        date_range_start: Include only memories created after this time.
        date_range_end: Include only memories created before this time.

    Example:
        ```python
        class SearchFilters:
            '''Concrete implementation of ProtocolSearchFilters.'''

            def __init__(
                self,
                content_types: list[str] | None = None,
                access_levels: list[str] | None = None,
            ) -> None:
                self.content_types = content_types
                self.access_levels = access_levels
                self.source_agents = None
                self.date_range_start = None
                self.date_range_end = None
                self._tags: list[str] | None = None

            @property
            def tags(self) -> list[str] | None:
                return self._tags

        # Usage
        filters = SearchFilters(
            content_types=["text/plain", "application/json"],
            access_levels=["public", "internal"],
        )
        assert isinstance(filters, ProtocolSearchFilters)
        ```

    See Also:
        - ProtocolSemanticSearchRequest: Uses this for search filtering.
        - ProtocolMemoryListRequest: Uses this for list filtering.
    """

    content_types: list[str] | None
    access_levels: list[str] | None
    source_agents: list[str] | None
    date_range_start: datetime | None
    date_range_end: datetime | None

    @property
    def tags(self) -> list[str] | None: ...


# Backward compatibility exports
__all__ = [
    "LiteralAgentStatus",
    "LiteralAnalysisType",
    "LiteralCompressionAlgorithm",
    "LiteralErrorCategory",
    # Type literals
    "LiteralMemoryAccessLevel",
    "LiteralWorkflowStatus",
    "ProtocolAgentResponseMap",
    "ProtocolAgentStatusMap",
    "ProtocolAggregatedData",
    "ProtocolAggregationCriteria",
    "ProtocolAggregationSummary",
    "ProtocolAnalysisParameters",
    # Re-exported from protocol_memory_data_types
    "ProtocolAnalysisResults",
    "ProtocolCoordinationMetadata",
    "ProtocolCustomMetrics",
    "ProtocolErrorCategoryMap",
    # Core protocols (defined here)
    "ProtocolKeyValueStore",
    "ProtocolMemoryErrorContext",
    "ProtocolMemoryMetadata",
    "ProtocolMemoryRecord",
    "ProtocolPageInfo",
    "ProtocolSearchFilters",
    "ProtocolSearchResult",
    "ProtocolWorkflowConfiguration",
]
