"""
Analytics and performance protocol types for ONEX SPI interfaces.

Domain: Analytics metrics, providers, summaries, and performance monitoring.

This module contains protocol definitions for analytics and performance
monitoring in the ONEX platform. It includes:
- ProtocolAnalyticsMetric for individual metric data points
- ProtocolAnalyticsProvider for analytics data sources
- ProtocolAnalyticsSummary for aggregated analytics reports
- ProtocolPerformanceMetric for performance measurement data points
- ProtocolPerformanceMetrics for performance metrics collections
"""

from typing import Protocol, runtime_checkable
from uuid import UUID

from omnibase_spi.protocols.types.protocol_base_types import (
    ContextValue,
    LiteralAnalyticsMetricType,
    LiteralAnalyticsTimeWindow,
    LiteralPerformanceCategory,
    ProtocolDateTime,
)


# ==============================================================================
# Analytics Protocols
# ==============================================================================


@runtime_checkable
class ProtocolAnalyticsMetric(Protocol):
    """Protocol for individual analytics metrics."""

    name: str
    type: LiteralAnalyticsMetricType
    value: float
    unit: str
    timestamp: "ProtocolDateTime"
    tags: dict[str, "ContextValue"]
    metadata: dict[str, "ContextValue"]

    async def validate_metric(self) -> bool: ...

    def is_valid_measurement(self) -> bool: ...


@runtime_checkable
class ProtocolAnalyticsProvider(Protocol):
    """Protocol for analytics data providers."""

    provider_id: UUID
    provider_type: str
    data_sources: list[str]
    supported_metrics: list[str]
    time_windows: list[LiteralAnalyticsTimeWindow]
    last_updated: "ProtocolDateTime"

    async def validate_provider(self) -> bool: ...

    def is_available(self) -> bool: ...


@runtime_checkable
class ProtocolAnalyticsSummary(Protocol):
    """Protocol for analytics summary reports."""

    time_window: LiteralAnalyticsTimeWindow
    start_time: "ProtocolDateTime"
    end_time: "ProtocolDateTime"
    metrics: list["ProtocolAnalyticsMetric"]
    insights: list[str]
    recommendations: list[str]
    confidence_score: float

    async def validate_summary(self) -> bool: ...

    def is_complete(self) -> bool: ...


# ==============================================================================
# Performance Protocols
# ==============================================================================


@runtime_checkable
class ProtocolPerformanceMetric(Protocol):
    """Protocol for performance metric data points."""

    metric_name: str
    category: LiteralPerformanceCategory
    value: float
    unit: str
    timestamp: "ProtocolDateTime"
    source: str
    threshold_warning: float | None
    threshold_critical: float | None

    async def validate_performance_metric(self) -> bool: ...

    def is_valid(self) -> bool: ...


@runtime_checkable
class ProtocolPerformanceMetrics(Protocol):
    """Protocol for performance metrics collection."""

    service_name: str
    collection_timestamp: "ProtocolDateTime"
    metrics: list["ProtocolPerformanceMetric"]
    overall_health_score: float
    performance_trends: dict[str, float]
    recommendations: list[str]

    async def validate_performance_metrics(self) -> bool: ...

    def is_healthy(self) -> bool: ...
