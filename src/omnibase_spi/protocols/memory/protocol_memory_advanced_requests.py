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


@runtime_checkable
class ProtocolBatchMemoryStoreRequest(Protocol):
    """
    Protocol for batch memory storage requests.

    This protocol defines the interface for storing multiple memory records
    in a single atomic or semi-atomic operation. Batch storage provides
    performance benefits over individual storage operations and supports
    configurable transaction semantics.

    Implementations should support parallel execution for performance and
    configurable failure behavior (fail-fast vs. continue-on-error).

    Attributes:
        correlation_id: Request correlation ID for tracing and debugging.
        request_timestamp: When the request was created.
        memory_records: List of memory records to store.
        batch_size: Maximum records to process per internal batch.
        fail_on_first_error: Stop processing on first error if True.
        timeout_seconds: Optional timeout for the entire batch operation.

    Example:
        ```python
        class BatchMemoryStoreRequest:
            '''Concrete implementation of ProtocolBatchMemoryStoreRequest.'''

            def __init__(
                self,
                memory_records: list[ProtocolAggregatedData],
                batch_size: int = 100,
                fail_on_first_error: bool = False,
            ) -> None:
                self.correlation_id = uuid4()
                self.request_timestamp = datetime.now(UTC)
                self.memory_records = memory_records
                self.batch_size = batch_size
                self.fail_on_first_error = fail_on_first_error
                self.timeout_seconds = 60.0

            @property
            def operation_type(self) -> str:
                return "batch_store"

            @property
            def transaction_isolation(self) -> str:
                return "read_committed"

            @property
            def parallel_execution(self) -> bool:
                return True

        # Usage
        request = BatchMemoryStoreRequest(
            memory_records=[record1, record2, record3],
            batch_size=50,
        )
        assert isinstance(request, ProtocolBatchMemoryStoreRequest)
        ```

    See Also:
        - ProtocolBatchMemoryStoreResponse: For the corresponding response protocol.
        - ProtocolMemoryStoreRequest: For single memory storage.
    """

    correlation_id: UUID | None
    request_timestamp: datetime
    memory_records: list[ProtocolAggregatedData]
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
        correlation_id: Request correlation ID for tracing and debugging.
        request_timestamp: When the request was created.
        memory_ids: Multiple memory identifiers (list[UUID])
        include_related: Whether to include related memory records
        fail_on_missing: Whether to fail if ANY memory is missing
        timeout_seconds: Optional operation timeout

    Example:
        ```python
        class BatchMemoryRetrieveRequest:
            '''Concrete implementation of ProtocolBatchMemoryRetrieveRequest.'''

            def __init__(
                self,
                memory_ids: list[UUID],
                include_related: bool = False,
                fail_on_missing: bool = False,
            ) -> None:
                self.correlation_id = uuid4()
                self.request_timestamp = datetime.now(UTC)
                self.memory_ids = memory_ids
                self.include_related = include_related
                self.fail_on_missing = fail_on_missing
                self.timeout_seconds = 30.0

            @property
            def operation_type(self) -> str:
                return "batch_retrieve"

            @property
            def related_depth(self) -> int:
                return 2 if self.include_related else 0

        # Usage
        request = BatchMemoryRetrieveRequest(
            memory_ids=[uuid4(), uuid4(), uuid4()],
            include_related=True,
        )
        assert isinstance(request, ProtocolBatchMemoryRetrieveRequest)
        ```

    See Also:
        - ProtocolMemoryRetrieveRequest: For single memory retrieval
        - ProtocolBatchMemoryRetrieveResponse: For the corresponding response protocol.
    """

    correlation_id: UUID | None
    request_timestamp: datetime
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
    """
    Protocol for pattern analysis requests on memory data.

    This protocol defines the interface for requesting pattern analysis
    operations on memory content. Pattern analysis identifies recurring
    themes, relationships, and structures to support intelligent organization.

    Implementations should support multiple analysis types with configurable
    parameters for tuning detection sensitivity and scope.

    Attributes:
        correlation_id: Request correlation ID for tracing and debugging.
        request_timestamp: When the request was created.
        data_source: Source of data to analyze (e.g., memory store, agent logs).
        analysis_type: Type of analysis (standard, deep, quick, semantic).
        timeout_seconds: Optional timeout for the analysis operation.

    Example:
        ```python
        class PatternAnalysisRequest:
            '''Concrete implementation of ProtocolPatternAnalysisRequest.'''

            def __init__(
                self,
                data_source: str,
                analysis_type: LiteralAnalysisType = "semantic",
            ) -> None:
                self.correlation_id = uuid4()
                self.request_timestamp = datetime.now(UTC)
                self.data_source = data_source
                self.analysis_type = analysis_type
                self.timeout_seconds = 120.0
                self._parameters = AnalysisParameters()

            @property
            def operation_type(self) -> str:
                return "pattern_analysis"

            @property
            def analysis_parameters(self) -> ProtocolAnalysisParameters:
                return self._parameters

        # Usage
        request = PatternAnalysisRequest(
            data_source="memory_store_v1",
            analysis_type="semantic",
        )
        assert isinstance(request, ProtocolPatternAnalysisRequest)
        ```

    See Also:
        - ProtocolPatternAnalysisResponse: For the corresponding response protocol.
        - ProtocolAnalysisParameters: For analysis parameter configuration.
    """

    correlation_id: UUID | None
    request_timestamp: datetime
    data_source: str
    analysis_type: LiteralAnalysisType
    timeout_seconds: float | None

    @property
    def operation_type(self) -> str: ...

    @property
    def analysis_parameters(self) -> ProtocolAnalysisParameters: ...


@runtime_checkable
class ProtocolConsolidationRequest(Protocol):
    """
    Protocol for memory consolidation requests.

    Consolidation merges multiple memory records into a single unified record,
    applying a specific consolidation strategy to resolve conflicts and
    combine content. This is distinct from aggregation which computes
    summary statistics without merging records.

    Use Cases:
        - Merging duplicate or related memories
        - Combining fragmented memory records
        - Deduplication with content preservation

    Attributes:
        correlation_id: Request correlation ID for tracing and debugging.
        request_timestamp: When the request was created.
        memory_ids: Memory records to consolidate (will be merged)
        consolidation_strategy: Strategy for merging (e.g., 'latest_wins', 'merge_all')
        timeout_seconds: Optional timeout for the consolidation operation.
        preserve_source_links: Whether to maintain references to source memories

    Example:
        ```python
        class ConsolidationRequest:
            '''Concrete implementation of ProtocolConsolidationRequest.'''

            def __init__(
                self,
                memory_ids: list[UUID],
                consolidation_strategy: str = "merge_all",
                preserve_source_links: bool = True,
            ) -> None:
                self.correlation_id = uuid4()
                self.request_timestamp = datetime.now(UTC)
                self.memory_ids = memory_ids
                self.consolidation_strategy = consolidation_strategy
                self.preserve_source_links = preserve_source_links
                self.timeout_seconds = 60.0

            @property
            def operation_type(self) -> str:
                return "consolidation"

            @property
            def conflict_resolution_mode(self) -> str:
                return "latest_wins"

        # Usage
        request = ConsolidationRequest(
            memory_ids=[uuid4(), uuid4(), uuid4()],
            consolidation_strategy="merge_all",
        )
        assert isinstance(request, ProtocolConsolidationRequest)
        ```

    See Also:
        - ProtocolConsolidationResponse: For the corresponding response protocol.
        - ProtocolAggregationRequest: For computing statistics without merging.
    """

    correlation_id: UUID | None
    request_timestamp: datetime
    memory_ids: list[UUID]
    consolidation_strategy: str
    timeout_seconds: float | None
    preserve_source_links: bool

    @property
    def operation_type(self) -> str: ...

    @property
    def conflict_resolution_mode(self) -> str: ...


@runtime_checkable
class ProtocolAggregationRequest(Protocol):
    """
    Protocol for memory aggregation requests.

    Aggregation computes summary statistics and metrics across memory records
    without modifying or merging the underlying data. This is distinct from
    consolidation which merges records into a new unified record.

    Use Cases:
        - Computing usage statistics over time windows
        - Generating summary reports across memory types
        - Analytics and trend analysis

    Attributes:
        correlation_id: Request correlation ID for tracing and debugging.
        request_timestamp: When the request was created.
        aggregation_criteria: Criteria defining what to aggregate.
        time_window_start: Start of the aggregation time window.
        time_window_end: End of the aggregation time window.
        timeout_seconds: Optional timeout for the aggregation operation.
        group_by_fields: Fields to group results by.

    Example:
        ```python
        class AggregationRequest:
            '''Concrete implementation of ProtocolAggregationRequest.'''

            def __init__(
                self,
                aggregation_criteria: ProtocolAggregationCriteria,
                time_window_start: datetime | None = None,
                time_window_end: datetime | None = None,
            ) -> None:
                self.correlation_id = uuid4()
                self.request_timestamp = datetime.now(UTC)
                self.aggregation_criteria = aggregation_criteria
                self.time_window_start = time_window_start
                self.time_window_end = time_window_end
                self.timeout_seconds = 60.0
                self.group_by_fields = ["content_type", "source_agent"]

            @property
            def operation_type(self) -> str:
                return "aggregation"

            @property
            def include_percentiles(self) -> bool:
                return True

        # Usage
        request = AggregationRequest(
            aggregation_criteria=criteria,
            time_window_start=datetime(2024, 1, 1, tzinfo=UTC),
            time_window_end=datetime(2024, 12, 31, tzinfo=UTC),
        )
        assert isinstance(request, ProtocolAggregationRequest)
        ```

    See Also:
        - ProtocolAggregationResponse: For the corresponding response protocol.
        - ProtocolConsolidationRequest: For merging records into one.
    """

    correlation_id: UUID | None
    request_timestamp: datetime
    aggregation_criteria: ProtocolAggregationCriteria
    time_window_start: datetime | None
    time_window_end: datetime | None
    timeout_seconds: float | None
    group_by_fields: list[str]

    @property
    def operation_type(self) -> str: ...

    @property
    def include_percentiles(self) -> bool: ...


@runtime_checkable
class ProtocolWorkflowExecutionRequest(Protocol):
    """
    Protocol for workflow execution requests in multi-agent memory operations.

    This protocol defines the interface for initiating workflow executions
    that coordinate memory operations across multiple agents. Workflows
    enable complex multi-step memory processing with agent coordination.

    Implementations should support various workflow types and provide
    methods to retrieve the list of participating agents.

    Attributes:
        correlation_id: Request correlation ID for tracing and debugging.
        request_timestamp: When the request was created.
        workflow_type: Type of workflow to execute (e.g., 'synchronization', 'cleanup').
        workflow_configuration: Configuration parameters for the workflow.
        timeout_seconds: Optional timeout for the entire workflow.

    Example:
        ```python
        class WorkflowExecutionRequest:
            '''Concrete implementation of ProtocolWorkflowExecutionRequest.'''

            def __init__(
                self,
                workflow_type: str,
                workflow_configuration: ProtocolWorkflowConfiguration,
                target_agents: list[UUID],
            ) -> None:
                self.correlation_id = uuid4()
                self.request_timestamp = datetime.now(UTC)
                self.workflow_type = workflow_type
                self.workflow_configuration = workflow_configuration
                self.timeout_seconds = 300.0
                self._target_agents = target_agents

            @property
            def operation_type(self) -> str:
                return "workflow_execution"

            async def get_target_agents(self) -> list[UUID]:
                return self._target_agents

        # Usage
        request = WorkflowExecutionRequest(
            workflow_type="memory_synchronization",
            workflow_configuration=config,
            target_agents=[uuid4(), uuid4()],
        )
        assert isinstance(request, ProtocolWorkflowExecutionRequest)
        ```

    See Also:
        - ProtocolWorkflowExecutionResponse: For the corresponding response protocol.
        - ProtocolWorkflowConfiguration: For workflow configuration structure.
    """

    correlation_id: UUID | None
    request_timestamp: datetime
    workflow_type: str
    workflow_configuration: ProtocolWorkflowConfiguration
    timeout_seconds: float | None

    @property
    def operation_type(self) -> str: ...

    async def get_target_agents(self) -> list[UUID]: ...


@runtime_checkable
class ProtocolAgentCoordinationRequest(Protocol):
    """
    Protocol for agent coordination requests in distributed memory operations.

    This protocol defines the interface for coordinating tasks across multiple
    agents. Coordination enables synchronized memory operations, distributed
    consensus, and collaborative processing among agent instances.

    Implementations should support various coordination tasks and provide
    metadata for managing the coordination lifecycle.

    Attributes:
        correlation_id: Request correlation ID for tracing and debugging.
        request_timestamp: When the request was created.
        agent_ids: List of agent UUIDs to coordinate.
        coordination_task: Type of coordination (e.g., 'sync', 'distribute', 'collect').
        timeout_seconds: Optional timeout for the coordination operation.

    Example:
        ```python
        class AgentCoordinationRequest:
            '''Concrete implementation of ProtocolAgentCoordinationRequest.'''

            def __init__(
                self,
                agent_ids: list[UUID],
                coordination_task: str,
            ) -> None:
                self.correlation_id = uuid4()
                self.request_timestamp = datetime.now(UTC)
                self.agent_ids = agent_ids
                self.coordination_task = coordination_task
                self.timeout_seconds = 120.0
                self._metadata = CoordinationMetadata()

            @property
            def operation_type(self) -> str:
                return "agent_coordination"

            async def coordination_metadata(self) -> ProtocolCoordinationMetadata:
                return self._metadata

        # Usage
        request = AgentCoordinationRequest(
            agent_ids=[uuid4(), uuid4(), uuid4()],
            coordination_task="memory_sync",
        )
        assert isinstance(request, ProtocolAgentCoordinationRequest)
        ```

    See Also:
        - ProtocolAgentCoordinationResponse: For the corresponding response protocol.
        - ProtocolCoordinationMetadata: For coordination metadata structure.
    """

    correlation_id: UUID | None
    request_timestamp: datetime
    agent_ids: list[UUID]
    coordination_task: str
    timeout_seconds: float | None

    @property
    def operation_type(self) -> str: ...

    async def coordination_metadata(self) -> ProtocolCoordinationMetadata: ...


@runtime_checkable
class ProtocolMemoryMetricsRequest(Protocol):
    """
    Protocol for metrics collection requests from memory operations.

    This protocol defines the interface for requesting performance and usage
    metrics from the memory system. Metrics support monitoring, alerting,
    and capacity planning for memory operations.

    Implementations should support various aggregation levels and filtering
    by metric type and time window.

    Attributes:
        correlation_id: Request correlation ID for tracing and debugging.
        request_timestamp: When the request was created.
        metric_types: List of metric types to collect (e.g., 'latency', 'throughput').
        time_window_start: Start of the metrics time window.
        time_window_end: End of the metrics time window.
        aggregation_level: Aggregation granularity ('minute', 'hour', 'day').
        timeout_seconds: Optional timeout for the metrics collection.

    Example:
        ```python
        class MemoryMetricsRequest:
            '''Concrete implementation of ProtocolMemoryMetricsRequest.'''

            def __init__(
                self,
                metric_types: list[str],
                aggregation_level: str = "hour",
            ) -> None:
                self.correlation_id = uuid4()
                self.request_timestamp = datetime.now(UTC)
                self.metric_types = metric_types
                self.aggregation_level = aggregation_level
                self.time_window_start = datetime.now(UTC) - timedelta(hours=24)
                self.time_window_end = datetime.now(UTC)
                self.timeout_seconds = 30.0

            @property
            def operation_type(self) -> str:
                return "metrics_collection"

            @property
            def include_detailed_breakdown(self) -> bool:
                return True

        # Usage
        request = MemoryMetricsRequest(
            metric_types=["latency", "throughput", "error_rate"],
            aggregation_level="hour",
        )
        assert isinstance(request, ProtocolMemoryMetricsRequest)
        ```

    See Also:
        - ProtocolMemoryMetricsResponse: For the corresponding response protocol.
        - ProtocolMemoryMetrics: For individual metric data points.
    """

    correlation_id: UUID | None
    request_timestamp: datetime
    metric_types: list[str]
    time_window_start: datetime | None
    time_window_end: datetime | None
    aggregation_level: str
    timeout_seconds: float | None

    @property
    def operation_type(self) -> str: ...

    @property
    def include_detailed_breakdown(self) -> bool: ...


@runtime_checkable
class ProtocolStreamingMemoryRequest(Protocol):
    """
    Protocol for streaming memory operation requests.

    This protocol defines the interface for initiating streaming memory
    operations. Streaming enables efficient transfer of large memory content
    in chunks, reducing memory overhead and enabling progressive processing.

    Implementations should support configurable chunk sizes and optional
    compression for bandwidth optimization.

    Attributes:
        correlation_id: Request correlation ID for tracing and debugging.
        request_timestamp: When the request was created.
        stream_type: Type of streaming operation ('upload', 'download', 'sync').
        chunk_size: Size of each data chunk in bytes.
        timeout_seconds: Optional timeout for the streaming operation.

    Example:
        ```python
        class StreamingMemoryRequest:
            '''Concrete implementation of ProtocolStreamingMemoryRequest.'''

            def __init__(
                self,
                stream_type: str,
                chunk_size: int = 8192,
                compression_enabled: bool = True,
            ) -> None:
                self.correlation_id = uuid4()
                self.request_timestamp = datetime.now(UTC)
                self.stream_type = stream_type
                self.chunk_size = chunk_size
                self.timeout_seconds = 300.0
                self._compression_enabled = compression_enabled

            @property
            def operation_type(self) -> str:
                return "streaming"

            @property
            def compression_enabled(self) -> bool:
                return self._compression_enabled

        # Usage
        request = StreamingMemoryRequest(
            stream_type="upload",
            chunk_size=16384,
            compression_enabled=True,
        )
        assert isinstance(request, ProtocolStreamingMemoryRequest)
        ```

    See Also:
        - ProtocolStreamingMemoryResponse: For the corresponding response protocol.
        - ProtocolStreamingRetrieveRequest: For streaming retrieval requests.
    """

    correlation_id: UUID | None
    request_timestamp: datetime
    stream_type: str
    chunk_size: int
    timeout_seconds: float | None

    @property
    def operation_type(self) -> str: ...

    @property
    def compression_enabled(self) -> bool: ...


@runtime_checkable
class ProtocolStreamingRetrieveRequest(Protocol):
    """
    Protocol for streaming memory retrieval requests.

    This protocol defines the interface for retrieving memory content via
    streaming. It extends the basic streaming protocol with memory-specific
    features like selective memory retrieval and metadata inclusion.

    Implementations should support streaming multiple memories and allow
    clients to control content size limits for bandwidth management.

    Attributes:
        correlation_id: Request correlation ID for tracing and debugging.
        request_timestamp: When the request was created.
        stream_type: Type of streaming operation.
        chunk_size: Size of each data chunk in bytes.
        timeout_seconds: Optional timeout for the streaming operation.
        memory_ids: List of memory UUIDs to stream.
        include_metadata: Whether to include memory metadata in response.

    Example:
        ```python
        class StreamingRetrieveRequest:
            '''Concrete implementation of ProtocolStreamingRetrieveRequest.'''

            def __init__(
                self,
                memory_ids: list[UUID],
                chunk_size: int = 8192,
                include_metadata: bool = True,
            ) -> None:
                self.correlation_id = uuid4()
                self.request_timestamp = datetime.now(UTC)
                self.stream_type = "download"
                self.chunk_size = chunk_size
                self.timeout_seconds = 300.0
                self.memory_ids = memory_ids
                self.include_metadata = include_metadata

            @property
            def operation_type(self) -> str:
                return "streaming_retrieve"

            @property
            def compression_enabled(self) -> bool:
                return True

            @property
            def max_content_size(self) -> int | None:
                return 100 * 1024 * 1024  # 100 MB limit

        # Usage
        request = StreamingRetrieveRequest(
            memory_ids=[uuid4(), uuid4()],
            chunk_size=16384,
            include_metadata=True,
        )
        assert isinstance(request, ProtocolStreamingRetrieveRequest)
        ```

    See Also:
        - ProtocolStreamingRetrieveResponse: For the corresponding response protocol.
        - ProtocolStreamingMemoryRequest: For general streaming requests.
    """

    correlation_id: UUID | None
    request_timestamp: datetime
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
