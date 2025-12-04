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
    """Protocol for analysis result structures."""

    @property
    def result_keys(self) -> list[str]: ...

    async def get_result_value(self, key: str) -> str | None: ...

    def has_result_key(self, key: str) -> bool: ...


@runtime_checkable
class ProtocolAggregatedData(Protocol):
    """Protocol for aggregated data structures."""

    @property
    def data_keys(self) -> list[str]: ...

    async def get_data_value(self, key: str) -> str | None: ...

    async def validate_data(self) -> bool: ...


@runtime_checkable
class ProtocolMemoryErrorContext(Protocol):
    """Protocol for error context structures."""

    @property
    def context_keys(self) -> list[str]: ...

    async def get_context_value(self, key: str) -> str | None: ...

    def add_context(self, key: str, value: str) -> None: ...


@runtime_checkable
class ProtocolPageInfo(Protocol):
    """Protocol for pagination information structures."""

    @property
    def info_keys(self) -> list[str]: ...

    async def get_info_value(self, key: str) -> str | None: ...

    def has_next_page(self) -> bool: ...


@runtime_checkable
class ProtocolCustomMetrics(Protocol):
    """Protocol for custom metrics structures."""

    @property
    def metric_names(self) -> list[str]: ...

    async def get_metric_value(self, name: str) -> float | None: ...

    def has_metric(self, name: str) -> bool: ...


@runtime_checkable
class ProtocolAggregationSummary(Protocol):
    """Protocol for aggregation summary structures."""

    @property
    def summary_keys(self) -> list[str]: ...

    async def get_summary_value(self, key: str) -> float | None: ...

    def calculate_total(self) -> float: ...

    async def validate_record_data(self) -> bool: ...


@runtime_checkable
class ProtocolAgentStatusMap(Protocol):
    """Protocol for agent status mapping structures."""

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
    """Protocol for agent response mapping structures."""

    @property
    def responding_agents(self) -> list[UUID]: ...

    async def get_agent_response(self, agent_id: UUID) -> str | None: ...

    def add_agent_response(self, agent_id: UUID, response: str) -> None: ...

    async def get_all_responses(self) -> dict[UUID, str]: ...


@runtime_checkable
class ProtocolErrorCategoryMap(Protocol):
    """Protocol for error category counting structures."""

    @property
    def category_names(self) -> list[str]: ...

    async def get_category_count(self, category: str) -> int: ...

    def increment_category(self, category: str) -> None: ...

    async def get_all_counts(self) -> dict[str, int]: ...
