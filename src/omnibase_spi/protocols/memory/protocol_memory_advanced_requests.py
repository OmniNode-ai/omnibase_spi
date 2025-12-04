"""
Advanced Memory Request Protocols for OmniMemory ONEX Architecture

This module defines advanced request protocols including batch operations,
streaming requests, and workflow coordination. Split from protocol_memory_requests.py
to maintain the 15-protocol limit.

Contains:
    - Batch operation request protocols
    - Streaming request protocols
    - Workflow and coordination request protocols
    - Metrics request protocols

All types are pure protocols with no implementation dependencies.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable
from uuid import UUID

if TYPE_CHECKING:
    from datetime import datetime

    from omnibase_spi.protocols.memory.protocol_memory_base import (
        LiteralAnalysisType,
        ProtocolAggregationCriteria,
        ProtocolAnalysisParameters,
        ProtocolCoordinationMetadata,
        ProtocolWorkflowConfiguration,
    )
    from omnibase_spi.protocols.memory.protocol_memory_data_types import (
        ProtocolAggregatedData,
    )
    from omnibase_spi.protocols.memory.protocol_memory_requests import (
        ProtocolMemoryRequest,
    )


@runtime_checkable
class ProtocolBatchMemoryStoreRequest(Protocol):
    """Protocol for batch memory storage requests."""

    correlation_id: UUID | None
    request_timestamp: "datetime"
    memory_records: list["ProtocolAggregatedData"]
    batch_size: int
    fail_on_first_error: bool
    timeout_seconds: float | None

    @property
    def operation_type(self) -> str: ...

    @property
    def transaction_isolation(self) -> str: ...

    @property
    def parallel_execution(self) -> bool: ...


@runtime_checkable
class ProtocolBatchMemoryRetrieveRequest(Protocol):
    """
    Protocol for batch memory retrieval requests.

    Retrieves multiple memory records in a single operation with configurable
    failure semantics. Optimized for bulk operations with rate limiting support.

    Use Cases:
        - Bulk memory export/synchronization
        - Related memory graph traversal
        - Memory consolidation operations

    Performance Considerations:
        - Supports rate limiting via ProtocolRateLimitConfig
        - Can return partial results (fail_on_missing=False)
        - Optimized for multi-record retrieval efficiency

    Attributes:
        memory_ids: Multiple memory identifiers (list[UUID])
        include_related: Whether to include related memory records
        fail_on_missing: Whether to fail if ANY memory is missing
        timeout_seconds: Optional operation timeout

    Properties:
        related_depth: Depth of related memory graph traversal

    See Also:
        ProtocolMemoryRetrieveRequest: For single memory retrieval
        ProtocolMemoryEffectNode.batch_retrieve_memories: Implementation contract
    """

    correlation_id: UUID | None
    request_timestamp: "datetime"
    memory_ids: list[UUID]
    include_related: bool
    fail_on_missing: bool
    timeout_seconds: float | None

    @property
    def operation_type(self) -> str: ...

    @property
    def related_depth(self) -> int: ...


@runtime_checkable
class ProtocolPatternAnalysisRequest(Protocol):
    """Protocol for pattern analysis requests."""

    correlation_id: UUID | None
    request_timestamp: "datetime"
    data_source: str
    analysis_type: "LiteralAnalysisType"
    timeout_seconds: float | None

    @property
    def operation_type(self) -> str: ...

    @property
    def analysis_parameters(self) -> "ProtocolAnalysisParameters": ...


@runtime_checkable
class ProtocolConsolidationRequest(Protocol):
    """Protocol for memory consolidation requests."""

    correlation_id: UUID | None
    request_timestamp: "datetime"
    memory_ids: list[UUID]
    consolidation_strategy: str
    timeout_seconds: float | None

    @property
    def operation_type(self) -> str: ...


@runtime_checkable
class ProtocolAggregationRequest(Protocol):
    """Protocol for memory aggregation requests."""

    correlation_id: UUID | None
    request_timestamp: "datetime"
    aggregation_criteria: "ProtocolAggregationCriteria"
    time_window_start: "datetime | None"
    time_window_end: "datetime | None"
    timeout_seconds: float | None

    @property
    def operation_type(self) -> str: ...


@runtime_checkable
class ProtocolWorkflowExecutionRequest(Protocol):
    """Protocol for workflow execution requests."""

    correlation_id: UUID | None
    request_timestamp: "datetime"
    workflow_type: str
    workflow_configuration: "ProtocolWorkflowConfiguration"
    timeout_seconds: float | None

    @property
    def operation_type(self) -> str: ...

    async def get_target_agents(self) -> list[UUID]: ...


@runtime_checkable
class ProtocolAgentCoordinationRequest(Protocol):
    """Protocol for agent coordination requests."""

    correlation_id: UUID | None
    request_timestamp: "datetime"
    agent_ids: list[UUID]
    coordination_task: str
    timeout_seconds: float | None

    @property
    def operation_type(self) -> str: ...

    async def coordination_metadata(self) -> "ProtocolCoordinationMetadata": ...


@runtime_checkable
class ProtocolMemoryMetricsRequest(Protocol):
    """Protocol for metrics collection requests."""

    correlation_id: UUID | None
    request_timestamp: "datetime"
    metric_types: list[str]
    time_window_start: "datetime | None"
    time_window_end: "datetime | None"
    aggregation_level: str
    timeout_seconds: float | None

    @property
    def operation_type(self) -> str: ...

    @property
    def include_detailed_breakdown(self) -> bool: ...


@runtime_checkable
class ProtocolStreamingMemoryRequest(Protocol):
    """Protocol for streaming memory operations."""

    correlation_id: UUID | None
    request_timestamp: "datetime"
    stream_type: str
    chunk_size: int
    timeout_seconds: float | None

    @property
    def operation_type(self) -> str: ...

    @property
    def compression_enabled(self) -> bool: ...


@runtime_checkable
class ProtocolStreamingRetrieveRequest(Protocol):
    """Protocol for streaming memory retrieval requests."""

    correlation_id: UUID | None
    request_timestamp: "datetime"
    stream_type: str
    chunk_size: int
    timeout_seconds: float | None
    memory_ids: list[UUID]
    include_metadata: bool

    @property
    def operation_type(self) -> str: ...

    @property
    def compression_enabled(self) -> bool: ...

    @property
    def max_content_size(self) -> int | None: ...
