"""
Advanced Memory Response Protocols for OmniMemory ONEX Architecture

This module defines advanced response protocols including batch operations,
streaming responses, and workflow coordination. Split from protocol_memory_responses.py
to maintain the 15-protocol limit.

Contains:
    - Batch operation response protocols
    - Streaming response protocols
    - Workflow and coordination response protocols
    - Metrics response protocols

All types are pure protocols with no implementation dependencies.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Protocol, runtime_checkable
from uuid import UUID

if TYPE_CHECKING:
    from datetime import datetime

    from omnibase_spi.protocols.memory.protocol_memory_base import (
        ProtocolMemoryRecord,
    )
    from omnibase_spi.protocols.memory.protocol_memory_data_types import (
        ProtocolAgentResponseMap,
        ProtocolAgentStatusMap,
        ProtocolAggregatedData,
        ProtocolAggregationSummary,
        ProtocolAnalysisResults,
        ProtocolCustomMetrics,
        ProtocolPageInfo,
    )
    from omnibase_spi.protocols.memory.protocol_memory_responses import (
        ProtocolMemoryMetadata,
    )

from omnibase_spi.protocols.memory.protocol_memory_errors import ProtocolMemoryError


@runtime_checkable
class ProtocolBatchOperationResult(Protocol):
    """
    Protocol for individual batch operation results within a batch memory operation.

    This protocol defines the interface for representing the outcome of a single
    operation within a batch of memory operations. Each result tracks success status,
    timing, and any errors encountered during execution.

    Implementations should provide detailed error information when operations fail
    and accurate timing metrics for performance monitoring.

    Attributes:
        operation_index: Zero-based index of this operation within the batch.
        success: Whether this individual operation completed successfully.
        result_id: UUID of the created/retrieved memory record, if successful.
        error: Error details if the operation failed, None otherwise.

    Example:
        ```python
        class BatchOperationResult:
            '''Concrete implementation of ProtocolBatchOperationResult.'''

            def __init__(
                self,
                operation_index: int,
                success: bool,
                result_id: UUID | None = None,
                error: ProtocolMemoryError | None = None,
                execution_time_ms: int = 0,
            ) -> None:
                self.operation_index = operation_index
                self.success = success
                self.result_id = result_id
                self.error = error
                self._execution_time_ms = execution_time_ms

            @property
            def execution_time_ms(self) -> int:
                return self._execution_time_ms

        # Usage
        result = BatchOperationResult(
            operation_index=0,
            success=True,
            result_id=uuid4(),
            execution_time_ms=45,
        )
        assert isinstance(result, ProtocolBatchOperationResult)
        ```

    See Also:
        - ProtocolBatchMemoryStoreResponse: For batch storage operation responses.
        - ProtocolBatchMemoryRetrieveResponse: For batch retrieval operation responses.
    """

    operation_index: int
    success: bool
    result_id: UUID | None
    error: ProtocolMemoryError | None

    @property
    def execution_time_ms(self) -> int: ...


@runtime_checkable
class ProtocolBatchMemoryStoreResponse(Protocol):
    """
    Protocol for batch memory storage operation responses.

    This protocol defines the interface for responses from batch memory storage
    operations. It provides comprehensive status information including individual
    operation results, success/failure counts, and timing metrics.

    Implementations should support partial success scenarios where some operations
    succeed while others fail, enabling robust error handling and recovery.

    Attributes:
        correlation_id: Request correlation ID for tracing and debugging.
        response_timestamp: When the response was generated.
        success: True if all operations succeeded, False if any failed.
        results: List of individual operation results.
        total_processed: Total number of operations attempted.
        successful_count: Number of operations that succeeded.
        failed_count: Number of operations that failed.
        batch_execution_time_ms: Total execution time for the batch.

    Example:
        ```python
        class BatchMemoryStoreResponse:
            '''Concrete implementation of ProtocolBatchMemoryStoreResponse.'''

            def __init__(
                self,
                correlation_id: UUID | None,
                results: list[ProtocolBatchOperationResult],
                batch_execution_time_ms: int,
            ) -> None:
                self.correlation_id = correlation_id
                self.response_timestamp = datetime.now(UTC)
                self.results = results
                self.batch_execution_time_ms = batch_execution_time_ms
                self.total_processed = len(results)
                self.successful_count = sum(1 for r in results if r.success)
                self.failed_count = self.total_processed - self.successful_count
                self.success = self.failed_count == 0

            @property
            def error_message(self) -> str | None:
                if self.failed_count > 0:
                    return f"{self.failed_count} operations failed"
                return None

            @property
            def partial_success(self) -> bool:
                return self.successful_count > 0 and self.failed_count > 0

        # Usage
        response = BatchMemoryStoreResponse(
            correlation_id=uuid4(),
            results=[result1, result2],
            batch_execution_time_ms=150,
        )
        assert isinstance(response, ProtocolBatchMemoryStoreResponse)
        ```

    See Also:
        - ProtocolBatchOperationResult: For individual operation results.
        - ProtocolBatchMemoryStoreRequest: For the corresponding request protocol.
    """

    correlation_id: UUID | None
    response_timestamp: datetime
    success: bool
    results: list[ProtocolBatchOperationResult]
    total_processed: int
    successful_count: int
    failed_count: int
    batch_execution_time_ms: int

    @property
    def error_message(self) -> str | None: ...

    @property
    def partial_success(self) -> bool: ...


@runtime_checkable
class ProtocolBatchMemoryRetrieveResponse(Protocol):
    """
    Protocol for batch memory retrieval operation responses.

    This protocol defines the interface for responses from batch memory retrieval
    operations. It provides retrieved memory records, identifies missing records,
    and includes detailed status for each operation in the batch.

    Implementations should handle partial retrieval gracefully, returning
    all successfully retrieved memories while reporting which IDs could not be found.

    Attributes:
        correlation_id: Request correlation ID for tracing and debugging.
        response_timestamp: When the response was generated.
        success: True if all requested memories were found, False otherwise.
        results: List of individual operation results with timing data.
        memories: List of successfully retrieved memory records.
        missing_ids: List of UUIDs for memories that could not be found.
        batch_execution_time_ms: Total execution time for the batch retrieval.

    Example:
        ```python
        class BatchMemoryRetrieveResponse:
            '''Concrete implementation of ProtocolBatchMemoryRetrieveResponse.'''

            def __init__(
                self,
                correlation_id: UUID | None,
                memories: list[ProtocolMemoryRecord],
                missing_ids: list[UUID],
            ) -> None:
                self.correlation_id = correlation_id
                self.response_timestamp = datetime.now(UTC)
                self.memories = memories
                self.missing_ids = missing_ids
                self.success = len(missing_ids) == 0
                self.results = []  # Populated during processing
                self.batch_execution_time_ms = 0

            @property
            def error_message(self) -> str | None:
                if self.missing_ids:
                    return f"{len(self.missing_ids)} memories not found"
                return None

        # Usage
        response = BatchMemoryRetrieveResponse(
            correlation_id=uuid4(),
            memories=[memory1, memory2],
            missing_ids=[missing_uuid],
        )
        assert isinstance(response, ProtocolBatchMemoryRetrieveResponse)
        ```

    See Also:
        - ProtocolBatchMemoryRetrieveRequest: For the corresponding request protocol.
        - ProtocolMemoryRecord: For the structure of retrieved memory records.
    """

    correlation_id: UUID | None
    response_timestamp: datetime
    success: bool
    results: list[ProtocolBatchOperationResult]
    memories: list[ProtocolMemoryRecord]
    missing_ids: list[UUID]
    batch_execution_time_ms: int

    @property
    def error_message(self) -> str | None: ...


@runtime_checkable
class ProtocolPatternAnalysisResponse(Protocol):
    """
    Protocol for pattern analysis operation responses.

    This protocol defines the interface for responses from memory pattern analysis
    operations. Pattern analysis identifies recurring themes, relationships, and
    structures within memory data to support intelligent memory organization.

    Implementations should provide confidence scores for detected patterns and
    structured analysis results that can be used for memory consolidation.

    Attributes:
        correlation_id: Request correlation ID for tracing and debugging.
        response_timestamp: When the response was generated.
        success: Whether the analysis completed successfully.
        patterns_found: Number of distinct patterns identified.
        analysis_results: Structured results containing pattern details.

    Example:
        ```python
        class PatternAnalysisResponse:
            '''Concrete implementation of ProtocolPatternAnalysisResponse.'''

            def __init__(
                self,
                correlation_id: UUID | None,
                patterns_found: int,
                analysis_results: ProtocolAnalysisResults,
                confidence_scores: list[float],
            ) -> None:
                self.correlation_id = correlation_id
                self.response_timestamp = datetime.now(UTC)
                self.success = True
                self.patterns_found = patterns_found
                self.analysis_results = analysis_results
                self._confidence_scores = confidence_scores

            @property
            def error_message(self) -> str | None:
                return None

            @property
            def confidence_scores(self) -> list[float]:
                return self._confidence_scores

        # Usage
        response = PatternAnalysisResponse(
            correlation_id=uuid4(),
            patterns_found=5,
            analysis_results=results,
            confidence_scores=[0.95, 0.87, 0.82, 0.75, 0.68],
        )
        assert isinstance(response, ProtocolPatternAnalysisResponse)
        ```

    See Also:
        - ProtocolPatternAnalysisRequest: For the corresponding request protocol.
        - ProtocolAnalysisResults: For the structure of analysis results.
    """

    correlation_id: UUID | None
    response_timestamp: datetime
    success: bool
    patterns_found: int
    analysis_results: ProtocolAnalysisResults

    @property
    def error_message(self) -> str | None: ...

    @property
    def confidence_scores(self) -> list[float]: ...


@runtime_checkable
class ProtocolConsolidationResponse(Protocol):
    """
    Protocol for memory consolidation operation responses.

    This protocol defines the interface for responses from memory consolidation
    operations. Consolidation merges multiple related memories into a single
    coherent memory record while preserving source information.

    Implementations should track source memory IDs to maintain provenance and
    enable audit trails for consolidated memories.

    Attributes:
        correlation_id: Request correlation ID for tracing and debugging.
        response_timestamp: When the response was generated.
        success: Whether the consolidation completed successfully.
        consolidated_memory_id: UUID of the newly created consolidated memory.
        source_memory_ids: List of UUIDs of memories that were consolidated.
        consolidation_strategy_applied: Name of the consolidation strategy used.
        content_merge_summary: Summary describing how content was merged.
        error_message: Error details if the operation failed, None otherwise.
        source_records_archived: Whether the source records were archived after consolidation.

    Example:
        ```python
        class ConsolidationResponse:
            '''Concrete implementation of ProtocolConsolidationResponse.'''

            def __init__(
                self,
                correlation_id: UUID | None,
                consolidated_memory_id: UUID,
                source_memory_ids: list[UUID],
            ) -> None:
                self.correlation_id = correlation_id
                self.response_timestamp = datetime.now(UTC)
                self.success = True
                self.consolidated_memory_id = consolidated_memory_id
                self.source_memory_ids = source_memory_ids

            @property
            def error_message(self) -> str | None:
                return None

        # Usage
        response = ConsolidationResponse(
            correlation_id=uuid4(),
            consolidated_memory_id=uuid4(),
            source_memory_ids=[uuid4(), uuid4(), uuid4()],
        )
        assert isinstance(response, ProtocolConsolidationResponse)
        assert len(response.source_memory_ids) == 3
        ```

    See Also:
        - ProtocolConsolidationRequest: For the corresponding request protocol.
        - ProtocolPatternAnalysisResponse: For pattern detection before consolidation.
    """

    correlation_id: UUID | None
    response_timestamp: datetime
    success: bool
    consolidated_memory_id: UUID
    source_memory_ids: list[UUID]
    consolidation_strategy_applied: str
    content_merge_summary: str

    @property
    def error_message(self) -> str | None: ...

    @property
    def source_records_archived(self) -> bool: ...


@runtime_checkable
class ProtocolAggregationResponse(Protocol):
    """
    Protocol for memory aggregation operation responses.

    This protocol defines the interface for responses from memory aggregation
    operations. Aggregation combines data from multiple memories based on
    specified criteria, producing summary statistics or combined datasets.

    Implementations should provide both the aggregated data and metadata
    describing the aggregation parameters and source memory characteristics.

    Attributes:
        correlation_id: Request correlation ID for tracing and debugging.
        response_timestamp: When the response was generated.
        success: Whether the aggregation completed successfully.
        aggregated_data: The combined/aggregated data result.
        aggregation_metadata: Metadata about the aggregation operation.
        records_processed: Number of records processed during aggregation.
        time_window_applied: Time window used for the aggregation operation.
        error_message: Error details if the operation failed, None otherwise.
        percentiles_included: Whether percentile calculations are included in the results.

    Example:
        ```python
        class AggregationResponse:
            '''Concrete implementation of ProtocolAggregationResponse.'''

            def __init__(
                self,
                correlation_id: UUID | None,
                aggregated_data: ProtocolAggregatedData,
                aggregation_metadata: ProtocolMemoryMetadata,
            ) -> None:
                self.correlation_id = correlation_id
                self.response_timestamp = datetime.now(UTC)
                self.success = True
                self.aggregated_data = aggregated_data
                self.aggregation_metadata = aggregation_metadata

            @property
            def error_message(self) -> str | None:
                return None

        # Usage
        response = AggregationResponse(
            correlation_id=uuid4(),
            aggregated_data=data,
            aggregation_metadata=metadata,
        )
        assert isinstance(response, ProtocolAggregationResponse)
        ```

    See Also:
        - ProtocolAggregationRequest: For the corresponding request protocol.
        - ProtocolAggregatedData: For the structure of aggregated data.
    """

    correlation_id: UUID | None
    response_timestamp: datetime
    success: bool
    aggregated_data: ProtocolAggregatedData
    aggregation_metadata: ProtocolMemoryMetadata
    records_processed: int
    time_window_applied: str

    @property
    def error_message(self) -> str | None: ...

    @property
    def percentiles_included(self) -> bool: ...


@runtime_checkable
class ProtocolWorkflowExecutionResponse(Protocol):
    """
    Protocol for workflow execution operation responses.

    This protocol defines the interface for responses from multi-agent workflow
    execution operations. Workflows coordinate multiple memory operations across
    agents, tracking individual agent statuses and overall execution progress.

    Implementations should provide real-time status updates and aggregate
    status information for monitoring distributed workflow execution.

    Attributes:
        correlation_id: Request correlation ID for tracing and debugging.
        response_timestamp: When the response was generated.
        success: Whether the workflow completed successfully.
        workflow_id: Unique identifier for this workflow execution.
        execution_status: Current status (pending, running, completed, failed).

    Example:
        ```python
        class WorkflowExecutionResponse:
            '''Concrete implementation of ProtocolWorkflowExecutionResponse.'''

            def __init__(
                self,
                correlation_id: UUID | None,
                workflow_id: UUID,
                execution_status: str,
                agent_statuses: ProtocolAgentStatusMap,
            ) -> None:
                self.correlation_id = correlation_id
                self.response_timestamp = datetime.now(UTC)
                self.workflow_id = workflow_id
                self.execution_status = execution_status
                self._agent_statuses = agent_statuses
                self.success = execution_status == "completed"

            @property
            def error_message(self) -> str | None:
                if self.execution_status == "failed":
                    return "Workflow execution failed"
                return None

            @property
            def agent_statuses(self) -> ProtocolAgentStatusMap:
                return self._agent_statuses

        # Usage
        response = WorkflowExecutionResponse(
            correlation_id=uuid4(),
            workflow_id=uuid4(),
            execution_status="completed",
            agent_statuses=status_map,
        )
        assert isinstance(response, ProtocolWorkflowExecutionResponse)
        ```

    See Also:
        - ProtocolWorkflowExecutionRequest: For the corresponding request protocol.
        - ProtocolAgentStatusMap: For the structure of agent status information.
    """

    correlation_id: UUID | None
    response_timestamp: datetime
    success: bool
    workflow_id: UUID
    execution_status: str

    @property
    def error_message(self) -> str | None: ...

    @property
    def agent_statuses(self) -> ProtocolAgentStatusMap: ...


@runtime_checkable
class ProtocolAgentCoordinationResponse(Protocol):
    """
    Protocol for agent coordination operation responses.

    This protocol defines the interface for responses from agent coordination
    operations. Coordination manages communication and task distribution among
    multiple agents working on related memory operations.

    Implementations should collect and aggregate responses from all participating
    agents, providing a unified view of the coordinated operation results.

    Attributes:
        correlation_id: Request correlation ID for tracing and debugging.
        response_timestamp: When the response was generated.
        success: Whether the coordination completed successfully.
        coordination_id: Unique identifier for this coordination session.
        coordination_status: Current status of the coordination effort.

    Example:
        ```python
        class AgentCoordinationResponse:
            '''Concrete implementation of ProtocolAgentCoordinationResponse.'''

            def __init__(
                self,
                correlation_id: UUID | None,
                coordination_id: UUID,
                coordination_status: str,
                responses: ProtocolAgentResponseMap,
            ) -> None:
                self.correlation_id = correlation_id
                self.response_timestamp = datetime.now(UTC)
                self.coordination_id = coordination_id
                self.coordination_status = coordination_status
                self._responses = responses
                self.success = coordination_status == "completed"

            @property
            def error_message(self) -> str | None:
                if self.coordination_status == "failed":
                    return "Agent coordination failed"
                return None

            async def agent_responses(self) -> ProtocolAgentResponseMap:
                return self._responses

        # Usage
        response = AgentCoordinationResponse(
            correlation_id=uuid4(),
            coordination_id=uuid4(),
            coordination_status="completed",
            responses=response_map,
        )
        assert isinstance(response, ProtocolAgentCoordinationResponse)
        ```

    See Also:
        - ProtocolAgentCoordinationRequest: For the corresponding request protocol.
        - ProtocolAgentResponseMap: For the structure of agent responses.
    """

    correlation_id: UUID | None
    response_timestamp: datetime
    success: bool
    coordination_id: UUID
    coordination_status: str

    @property
    def error_message(self) -> str | None: ...

    async def agent_responses(self) -> ProtocolAgentResponseMap: ...


@runtime_checkable
class ProtocolPaginationResponse(Protocol):
    """
    Protocol for paginated response metadata in memory list operations.

    This protocol defines the interface for pagination information returned
    with paginated memory list responses. It provides cursor-based navigation
    and count information for efficient traversal of large result sets.

    Implementations should support both cursor-based and offset-based pagination
    strategies, with cursors preferred for consistency in distributed systems.

    Attributes:
        total_count: Total number of items matching the query.
        has_next_page: Whether more items exist after current page.
        has_previous_page: Whether items exist before current page.
        next_cursor: Opaque cursor for fetching the next page.
        previous_cursor: Opaque cursor for fetching the previous page.

    Example:
        ```python
        class PaginationResponse:
            '''Concrete implementation of ProtocolPaginationResponse.'''

            def __init__(
                self,
                total_count: int,
                page_size: int,
                current_offset: int,
            ) -> None:
                self.total_count = total_count
                self.has_next_page = current_offset + page_size < total_count
                self.has_previous_page = current_offset > 0
                self.next_cursor = str(current_offset + page_size) if self.has_next_page else None
                self.previous_cursor = str(max(0, current_offset - page_size)) if self.has_previous_page else None
                self._page_info = PageInfo(page_size=page_size, current_offset=current_offset)

            @property
            def page_info(self) -> ProtocolPageInfo:
                return self._page_info

        # Usage
        pagination = PaginationResponse(
            total_count=150,
            page_size=20,
            current_offset=40,
        )
        assert isinstance(pagination, ProtocolPaginationResponse)
        assert pagination.has_next_page
        assert pagination.has_previous_page
        ```

    See Also:
        - ProtocolPaginationRequest: For the corresponding request parameters.
        - ProtocolPageInfo: For detailed page information structure.
    """

    total_count: int
    has_next_page: bool
    has_previous_page: bool
    next_cursor: str | None
    previous_cursor: str | None

    @property
    def page_info(self) -> ProtocolPageInfo: ...


@runtime_checkable
class ProtocolMemoryMetrics(Protocol):
    """
    Protocol for memory system performance metrics collection.

    This protocol defines the interface for performance metrics data from
    memory operations. Metrics include timing, resource usage, throughput,
    and error rates for comprehensive system monitoring.

    Implementations should provide accurate timing measurements and support
    custom metric extensions for domain-specific monitoring needs.

    Attributes:
        operation_type: Type of operation measured (store, retrieve, search, etc.).
        execution_time_ms: Time taken for the operation in milliseconds.
        memory_usage_mb: Memory consumed by the operation in megabytes.
        timestamp: When the metrics were captured.

    Example:
        ```python
        class MemoryMetrics:
            '''Concrete implementation of ProtocolMemoryMetrics.'''

            def __init__(
                self,
                operation_type: str,
                execution_time_ms: int,
                memory_usage_mb: float,
                ops_count: int,
                error_count: int,
            ) -> None:
                self.operation_type = operation_type
                self.execution_time_ms = execution_time_ms
                self.memory_usage_mb = memory_usage_mb
                self.timestamp = datetime.now(UTC)
                self._ops_count = ops_count
                self._error_count = error_count
                self._custom_metrics = CustomMetrics()

            async def throughput_ops_per_second(self) -> float:
                if self.execution_time_ms == 0:
                    return 0.0
                return (self._ops_count / self.execution_time_ms) * 1000

            @property
            def error_rate_percent(self) -> float:
                if self._ops_count == 0:
                    return 0.0
                return (self._error_count / self._ops_count) * 100

            @property
            def custom_metrics(self) -> ProtocolCustomMetrics:
                return self._custom_metrics

        # Usage
        metrics = MemoryMetrics(
            operation_type="batch_store",
            execution_time_ms=250,
            memory_usage_mb=64.5,
            ops_count=100,
            error_count=2,
        )
        assert isinstance(metrics, ProtocolMemoryMetrics)
        ```

    See Also:
        - ProtocolMemoryMetricsResponse: For metrics collection responses.
        - ProtocolCustomMetrics: For custom metric structures.
    """

    operation_type: str
    execution_time_ms: int
    memory_usage_mb: float
    timestamp: datetime

    async def throughput_ops_per_second(self) -> float: ...

    @property
    def error_rate_percent(self) -> float: ...

    @property
    def custom_metrics(self) -> ProtocolCustomMetrics: ...


@runtime_checkable
class ProtocolMemoryMetricsResponse(Protocol):
    """
    Protocol for metrics collection operation responses.

    This protocol defines the interface for responses from metrics collection
    requests. It provides a list of individual metrics along with aggregated
    summary statistics for the requested time window.

    Implementations should support configurable aggregation levels (minute,
    hour, day) and filtering by metric types and operation categories.

    Attributes:
        correlation_id: Request correlation ID for tracing and debugging.
        response_timestamp: When the response was generated.
        success: Whether metrics collection completed successfully.
        metrics: List of individual metric data points.
        aggregation_summary: Aggregated statistics across all metrics.
        collection_timestamp: When the metrics were collected.
        collection_duration_ms: Duration of metrics collection in milliseconds.
        metrics_source_nodes: List of node identifiers that provided metrics data.
        error_message: Error details if the operation failed, None otherwise.
        has_anomalies: Whether any anomalies were detected in the collected metrics.

    Example:
        ```python
        class MemoryMetricsResponse:
            '''Concrete implementation of ProtocolMemoryMetricsResponse.'''

            def __init__(
                self,
                correlation_id: UUID | None,
                metrics: list[ProtocolMemoryMetrics],
                aggregation_summary: ProtocolAggregationSummary,
            ) -> None:
                self.correlation_id = correlation_id
                self.response_timestamp = datetime.now(UTC)
                self.success = True
                self.metrics = metrics
                self.aggregation_summary = aggregation_summary
                self.collection_timestamp = datetime.now(UTC)

            @property
            def error_message(self) -> str | None:
                return None

        # Usage
        response = MemoryMetricsResponse(
            correlation_id=uuid4(),
            metrics=[metric1, metric2, metric3],
            aggregation_summary=summary,
        )
        assert isinstance(response, ProtocolMemoryMetricsResponse)
        assert len(response.metrics) == 3
        ```

    See Also:
        - ProtocolMemoryMetricsRequest: For the corresponding request protocol.
        - ProtocolMemoryMetrics: For individual metric data points.
        - ProtocolAggregationSummary: For aggregated statistics structure.
    """

    correlation_id: UUID | None
    response_timestamp: datetime
    success: bool
    metrics: list[ProtocolMemoryMetrics]
    aggregation_summary: ProtocolAggregationSummary
    collection_timestamp: datetime
    collection_duration_ms: int
    metrics_source_nodes: list[str]

    @property
    def error_message(self) -> str | None: ...

    @property
    def has_anomalies(self) -> bool: ...


@runtime_checkable
class ProtocolStreamingMemoryResponse(Protocol):
    """
    Protocol for streaming memory operation responses.

    This protocol defines the interface for responses from streaming memory
    operations. Streaming enables efficient transfer of large memory content
    in chunks, reducing memory overhead and enabling early processing.

    Implementations should provide async iterators for content streaming and
    support optional compression for bandwidth optimization.

    Attributes:
        correlation_id: Request correlation ID for tracing and debugging.
        response_timestamp: When the response was generated.
        success: Whether the stream was initialized successfully.
        stream_id: Unique identifier for this streaming session.
        chunk_count: Number of chunks in the stream.
        total_size_bytes: Total uncompressed size of streamed content.

    Example:
        ```python
        class StreamingMemoryResponse:
            '''Concrete implementation of ProtocolStreamingMemoryResponse.'''

            def __init__(
                self,
                correlation_id: UUID | None,
                stream_id: UUID,
                content: bytes,
                chunk_size: int = 8192,
            ) -> None:
                self.correlation_id = correlation_id
                self.response_timestamp = datetime.now(UTC)
                self.success = True
                self.stream_id = stream_id
                self._content = content
                self._chunk_size = chunk_size
                self.total_size_bytes = len(content)
                self.chunk_count = (len(content) + chunk_size - 1) // chunk_size

            @property
            def error_message(self) -> str | None:
                return None

            async def stream_content(self) -> AsyncIterator[bytes]:
                for i in range(0, len(self._content), self._chunk_size):
                    yield self._content[i:i + self._chunk_size]

            @property
            def compression_ratio(self) -> float | None:
                return None  # No compression in this example

        # Usage
        response = StreamingMemoryResponse(
            correlation_id=uuid4(),
            stream_id=uuid4(),
            content=b"Large memory content...",
        )
        assert isinstance(response, ProtocolStreamingMemoryResponse)
        ```

    See Also:
        - ProtocolStreamingMemoryRequest: For the corresponding request protocol.
        - ProtocolStreamingRetrieveResponse: For streaming retrieval responses.
    """

    correlation_id: UUID | None
    response_timestamp: datetime
    success: bool
    stream_id: UUID
    chunk_count: int
    total_size_bytes: int

    @property
    def error_message(self) -> str | None: ...

    async def stream_content(self) -> AsyncIterator[bytes]: ...

    @property
    def compression_ratio(self) -> float | None: ...


@runtime_checkable
class ProtocolStreamingRetrieveResponse(Protocol):
    """
    Protocol for streaming memory retrieval operation responses.

    This protocol defines the interface for responses from streaming memory
    retrieval operations. It extends streaming capabilities with memory-specific
    features like per-memory content streaming and metadata access.

    Implementations should support selective streaming of individual memories
    within a batch and provide metadata without requiring full content download.

    Attributes:
        correlation_id: Request correlation ID for tracing and debugging.
        response_timestamp: When the response was generated.
        success: Whether the retrieval stream was initialized successfully.
        stream_id: Unique identifier for this streaming session.
        chunk_count: Total number of chunks across all memories.
        total_size_bytes: Total uncompressed size of all memory content.
        memory_metadata: Metadata for each memory in the stream.

    Example:
        ```python
        class StreamingRetrieveResponse:
            '''Concrete implementation of ProtocolStreamingRetrieveResponse.'''

            def __init__(
                self,
                correlation_id: UUID | None,
                stream_id: UUID,
                memories: dict[UUID, bytes],
                metadata: list[ProtocolMemoryRecord],
            ) -> None:
                self.correlation_id = correlation_id
                self.response_timestamp = datetime.now(UTC)
                self.success = True
                self.stream_id = stream_id
                self._memories = memories
                self.memory_metadata = metadata
                self.total_size_bytes = sum(len(c) for c in memories.values())
                self.chunk_count = len(memories)

            @property
            def error_message(self) -> str | None:
                return None

            @property
            def compression_ratio(self) -> float | None:
                return None

            async def stream_content(self) -> AsyncIterator[bytes]:
                for content in self._memories.values():
                    yield content

            async def stream_memory_content(self, memory_id: UUID) -> AsyncIterator[bytes]:
                if memory_id in self._memories:
                    yield self._memories[memory_id]

        # Usage
        response = StreamingRetrieveResponse(
            correlation_id=uuid4(),
            stream_id=uuid4(),
            memories={uuid4(): b"content1", uuid4(): b"content2"},
            metadata=[record1, record2],
        )
        assert isinstance(response, ProtocolStreamingRetrieveResponse)
        ```

    See Also:
        - ProtocolStreamingRetrieveRequest: For the corresponding request protocol.
        - ProtocolStreamingMemoryResponse: For general streaming responses.
        - ProtocolMemoryRecord: For memory metadata structure.
    """

    correlation_id: UUID | None
    response_timestamp: datetime
    success: bool
    stream_id: UUID
    chunk_count: int
    total_size_bytes: int
    memory_metadata: list[ProtocolMemoryRecord]

    @property
    def error_message(self) -> str | None: ...

    @property
    def compression_ratio(self) -> float | None: ...

    async def stream_content(self) -> AsyncIterator[bytes]: ...

    async def stream_memory_content(self, memory_id: UUID) -> AsyncIterator[bytes]: ...
