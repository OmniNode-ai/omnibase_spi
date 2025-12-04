"""
Memory Data Type Protocols for OmniMemory ONEX Architecture

This module defines data structure protocols that extend the base key-value
patterns. Split from protocol_memory_base.py to maintain the 15-protocol limit.

Contains:
    - Analysis and results protocols
    - Aggregation protocols
    - Agent mapping protocols
    - Error context protocols

All types are pure protocols with no implementation dependencies.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable
from uuid import UUID


@runtime_checkable
class ProtocolAnalysisResults(Protocol):
    """
    Protocol for analysis result data structures in memory pattern analysis.

    This protocol defines the interface for storing and accessing results
    from memory pattern analysis operations. Results are stored as key-value
    pairs where keys identify specific findings and values contain details.

    Implementations should support efficient key lookup and provide methods
    for querying available result categories.

    Example:
        ```python
        class AnalysisResults:
            '''Concrete implementation of ProtocolAnalysisResults.'''

            def __init__(self) -> None:
                self._results: dict[str, str] = {}

            @property
            def result_keys(self) -> list[str]:
                return list(self._results.keys())

            async def get_result_value(self, key: str) -> str | None:
                return self._results.get(key)

            def has_result_key(self, key: str) -> bool:
                return key in self._results

        # Usage
        results = AnalysisResults()
        results._results["pattern_count"] = "15"
        results._results["confidence"] = "0.92"
        assert isinstance(results, ProtocolAnalysisResults)
        assert results.has_result_key("pattern_count")
        ```

    See Also:
        - ProtocolPatternAnalysisResponse: Uses this for storing analysis findings.
    """

    @property
    def result_keys(self) -> list[str]: ...

    async def get_result_value(self, key: str) -> str | None: ...

    def has_result_key(self, key: str) -> bool: ...


@runtime_checkable
class ProtocolAggregatedData(Protocol):
    """
    Protocol for aggregated data structures in memory operations.

    This protocol defines the interface for storing aggregated data from
    memory aggregation operations. Data is stored as key-value pairs
    representing computed statistics or combined values.

    Implementations should support data validation to ensure integrity
    of aggregated values before they are used in downstream operations.

    Example:
        ```python
        class AggregatedData:
            '''Concrete implementation of ProtocolAggregatedData.'''

            def __init__(self) -> None:
                self._data: dict[str, str] = {}

            @property
            def data_keys(self) -> list[str]:
                return list(self._data.keys())

            async def get_data_value(self, key: str) -> str | None:
                return self._data.get(key)

            async def validate_data(self) -> bool:
                # Validate all required keys are present
                required = ["count", "total"]
                return all(k in self._data for k in required)

        # Usage
        data = AggregatedData()
        data._data["count"] = "100"
        data._data["total"] = "5000"
        assert isinstance(data, ProtocolAggregatedData)
        ```

    See Also:
        - ProtocolAggregationResponse: Uses this for storing aggregation results.
        - ProtocolBatchMemoryStoreRequest: Uses this for batch storage records.
    """

    @property
    def data_keys(self) -> list[str]: ...

    async def get_data_value(self, key: str) -> str | None: ...

    async def validate_data(self) -> bool: ...


@runtime_checkable
class ProtocolMemoryErrorContext(Protocol):
    """
    Protocol for error context structures in memory error handling.

    This protocol defines the interface for storing contextual information
    about memory operation errors. Context data helps with debugging and
    error recovery by preserving relevant state at error time.

    Implementations should support dynamic context addition during error
    propagation to capture all relevant debugging information.

    Example:
        ```python
        class MemoryErrorContext:
            '''Concrete implementation of ProtocolMemoryErrorContext.'''

            def __init__(self) -> None:
                self._context: dict[str, str] = {}

            @property
            def context_keys(self) -> list[str]:
                return list(self._context.keys())

            async def get_context_value(self, key: str) -> str | None:
                return self._context.get(key)

            def add_context(self, key: str, value: str) -> None:
                self._context[key] = value

        # Usage
        context = MemoryErrorContext()
        context.add_context("operation", "batch_store")
        context.add_context("memory_id", str(uuid4()))
        context.add_context("timestamp", datetime.now().isoformat())
        assert isinstance(context, ProtocolMemoryErrorContext)
        ```

    See Also:
        - ProtocolMemoryError: Uses this for error context storage.
    """

    @property
    def context_keys(self) -> list[str]: ...

    async def get_context_value(self, key: str) -> str | None: ...

    def add_context(self, key: str, value: str) -> None: ...


@runtime_checkable
class ProtocolPageInfo(Protocol):
    """
    Protocol for pagination information in memory list operations.

    This protocol defines the interface for storing detailed pagination
    metadata. It extends basic pagination information with additional
    details like page size, current position, and navigation availability.

    Implementations should support flexible key-value access for pagination
    parameters that may vary across different pagination strategies.

    Example:
        ```python
        class PageInfo:
            '''Concrete implementation of ProtocolPageInfo.'''

            def __init__(
                self,
                page_size: int,
                current_page: int,
                total_pages: int,
            ) -> None:
                self._info: dict[str, str] = {
                    "page_size": str(page_size),
                    "current_page": str(current_page),
                    "total_pages": str(total_pages),
                }
                self._has_next = current_page < total_pages

            @property
            def info_keys(self) -> list[str]:
                return list(self._info.keys())

            async def get_info_value(self, key: str) -> str | None:
                return self._info.get(key)

            def has_next_page(self) -> bool:
                return self._has_next

        # Usage
        page_info = PageInfo(page_size=20, current_page=2, total_pages=5)
        assert isinstance(page_info, ProtocolPageInfo)
        assert page_info.has_next_page()
        ```

    See Also:
        - ProtocolPaginationResponse: Uses this for detailed page information.
    """

    @property
    def info_keys(self) -> list[str]: ...

    async def get_info_value(self, key: str) -> str | None: ...

    def has_next_page(self) -> bool: ...


@runtime_checkable
class ProtocolCustomMetrics(Protocol):
    """
    Protocol for custom metrics structures in memory performance monitoring.

    This protocol defines the interface for storing domain-specific metrics
    that extend the standard memory metrics. Custom metrics enable monitoring
    of application-specific performance indicators.

    Implementations should support dynamic metric registration and provide
    numeric values for aggregation and alerting purposes.

    Example:
        ```python
        class CustomMetrics:
            '''Concrete implementation of ProtocolCustomMetrics.'''

            def __init__(self) -> None:
                self._metrics: dict[str, float] = {}

            @property
            def metric_names(self) -> list[str]:
                return list(self._metrics.keys())

            async def get_metric_value(self, name: str) -> float | None:
                return self._metrics.get(name)

            def has_metric(self, name: str) -> bool:
                return name in self._metrics

        # Usage
        metrics = CustomMetrics()
        metrics._metrics["cache_hit_ratio"] = 0.85
        metrics._metrics["compression_ratio"] = 0.45
        assert isinstance(metrics, ProtocolCustomMetrics)
        assert metrics.has_metric("cache_hit_ratio")
        ```

    See Also:
        - ProtocolMemoryMetrics: Uses this for custom metric extensions.
    """

    @property
    def metric_names(self) -> list[str]: ...

    async def get_metric_value(self, name: str) -> float | None: ...

    def has_metric(self, name: str) -> bool: ...


@runtime_checkable
class ProtocolAggregationSummary(Protocol):
    """
    Protocol for aggregation summary structures in metrics responses.

    This protocol defines the interface for storing summary statistics
    computed during metrics aggregation. Summaries provide quick insights
    into overall performance trends and key metrics.

    Implementations should support standard statistical summaries (min, max,
    avg, count) and validation of computed values.

    Example:
        ```python
        class AggregationSummary:
            '''Concrete implementation of ProtocolAggregationSummary.'''

            def __init__(self) -> None:
                self._summary: dict[str, float] = {}

            @property
            def summary_keys(self) -> list[str]:
                return list(self._summary.keys())

            async def get_summary_value(self, key: str) -> float | None:
                return self._summary.get(key)

            def calculate_total(self) -> float:
                return sum(self._summary.values())

            async def validate_record_data(self) -> bool:
                return len(self._summary) > 0

        # Usage
        summary = AggregationSummary()
        summary._summary["min"] = 10.0
        summary._summary["max"] = 100.0
        summary._summary["avg"] = 55.0
        assert isinstance(summary, ProtocolAggregationSummary)
        assert summary.calculate_total() == 165.0
        ```

    See Also:
        - ProtocolMemoryMetricsResponse: Uses this for aggregated statistics.
    """

    @property
    def summary_keys(self) -> list[str]: ...

    async def get_summary_value(self, key: str) -> float | None: ...

    def calculate_total(self) -> float: ...

    async def validate_record_data(self) -> bool: ...


@runtime_checkable
class ProtocolAgentStatusMap(Protocol):
    """
    Protocol for agent status mapping in multi-agent workflow operations.

    This protocol defines the interface for tracking agent statuses during
    workflow execution and coordination. It maintains a mapping from agent
    UUIDs to their current status values.

    Implementations should support concurrent status updates and provide
    efficient lookup of agent states for workflow orchestration.

    Example:
        ```python
        class AgentStatusMap:
            '''Concrete implementation of ProtocolAgentStatusMap.'''

            def __init__(self) -> None:
                self._statuses: dict[UUID, str] = {}
                self._responses: dict[UUID, str] = {}

            @property
            def agent_ids(self) -> list[UUID]:
                return list(self._statuses.keys())

            async def get_agent_status(self, agent_id: UUID) -> str | None:
                return self._statuses.get(agent_id)

            async def set_agent_status(self, agent_id: UUID, status: str) -> None:
                self._statuses[agent_id] = status

            @property
            def responding_agents(self) -> list[UUID]:
                return list(self._responses.keys())

            def add_agent_response(self, agent_id: UUID, response: str) -> None:
                self._responses[agent_id] = response

            async def get_all_statuses(self) -> dict[UUID, str]:
                return dict(self._statuses)

        # Usage
        status_map = AgentStatusMap()
        agent_id = uuid4()
        await status_map.set_agent_status(agent_id, "active")
        assert isinstance(status_map, ProtocolAgentStatusMap)
        ```

    See Also:
        - ProtocolWorkflowExecutionResponse: Uses this for agent status tracking.
    """

    @property
    def agent_ids(self) -> list[UUID]: ...

    async def get_agent_status(self, agent_id: UUID) -> str | None: ...

    async def set_agent_status(self, agent_id: UUID, status: str) -> None: ...

    @property
    def responding_agents(self) -> list[UUID]: ...

    def add_agent_response(self, agent_id: UUID, response: str) -> None: ...

    async def get_all_statuses(self) -> dict[UUID, str]: ...


@runtime_checkable
class ProtocolAgentResponseMap(Protocol):
    """
    Protocol for agent response mapping in coordination operations.

    This protocol defines the interface for collecting and accessing
    responses from multiple agents during coordination. It maintains
    a mapping from agent UUIDs to their response data.

    Implementations should support efficient response collection from
    multiple agents and provide bulk access to all collected responses.

    Example:
        ```python
        class AgentResponseMap:
            '''Concrete implementation of ProtocolAgentResponseMap.'''

            def __init__(self) -> None:
                self._responses: dict[UUID, str] = {}

            @property
            def responding_agents(self) -> list[UUID]:
                return list(self._responses.keys())

            async def get_agent_response(self, agent_id: UUID) -> str | None:
                return self._responses.get(agent_id)

            def add_agent_response(self, agent_id: UUID, response: str) -> None:
                self._responses[agent_id] = response

            async def get_all_responses(self) -> dict[UUID, str]:
                return dict(self._responses)

        # Usage
        response_map = AgentResponseMap()
        agent_id = uuid4()
        response_map.add_agent_response(agent_id, "task_completed")
        assert isinstance(response_map, ProtocolAgentResponseMap)
        assert agent_id in response_map.responding_agents
        ```

    See Also:
        - ProtocolAgentCoordinationResponse: Uses this for agent responses.
    """

    @property
    def responding_agents(self) -> list[UUID]: ...

    async def get_agent_response(self, agent_id: UUID) -> str | None: ...

    def add_agent_response(self, agent_id: UUID, response: str) -> None: ...

    async def get_all_responses(self) -> dict[UUID, str]: ...


@runtime_checkable
class ProtocolErrorCategoryMap(Protocol):
    """
    Protocol for error category counting in batch error summaries.

    This protocol defines the interface for counting errors by category
    during batch operations. It tracks occurrences of different error
    types to support error analysis and reporting.

    Implementations should support atomic increment operations and
    provide bulk access to all category counts for summary generation.

    Example:
        ```python
        class ErrorCategoryMap:
            '''Concrete implementation of ProtocolErrorCategoryMap.'''

            def __init__(self) -> None:
                self._counts: dict[str, int] = {}

            @property
            def category_names(self) -> list[str]:
                return list(self._counts.keys())

            async def get_category_count(self, category: str) -> int:
                return self._counts.get(category, 0)

            def increment_category(self, category: str) -> None:
                self._counts[category] = self._counts.get(category, 0) + 1

            async def get_all_counts(self) -> dict[str, int]:
                return dict(self._counts)

        # Usage
        error_map = ErrorCategoryMap()
        error_map.increment_category("validation")
        error_map.increment_category("validation")
        error_map.increment_category("timeout")
        assert isinstance(error_map, ProtocolErrorCategoryMap)
        assert await error_map.get_category_count("validation") == 2
        ```

    See Also:
        - ProtocolBatchErrorSummary: Uses this for categorized error counts.
    """

    @property
    def category_names(self) -> list[str]: ...

    async def get_category_count(self, category: str) -> int: ...

    def increment_category(self, category: str) -> None: ...

    async def get_all_counts(self) -> dict[str, int]: ...
