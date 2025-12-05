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
    """
    Protocol for individual analytics metrics with dimensional metadata.

    Represents a single analytics measurement with type classification,
    tags for categorization, and metadata for additional context.
    Used for analytics data collection and reporting.

    Attributes:
        name: Metric name identifier (e.g., "user.signups", "order.value").
        type: Type of metric (counter, gauge, histogram, summary).
        value: Numeric value of the metric.
        unit: Unit of measurement (e.g., "count", "ms", "bytes").
        timestamp: When the metric was recorded.
        tags: Key-value pairs for metric categorization.
        metadata: Additional context information.

    Example:
        ```python
        class OrderValueMetric:
            name: str = "order.total_value"
            type: LiteralAnalyticsMetricType = "gauge"
            value: float = 129.99
            unit: str = "usd"
            timestamp: ProtocolDateTime = datetime_impl
            tags: dict[str, ContextValue] = {"region": "us-east"}
            metadata: dict[str, ContextValue] = {"customer_segment": "premium"}

            async def validate_metric(self) -> bool:
                return bool(self.name)

            def is_valid_measurement(self) -> bool:
                return self.value >= 0

        metric = OrderValueMetric()
        assert isinstance(metric, ProtocolAnalyticsMetric)
        ```
    """

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
    """
    Protocol for analytics data providers and sources.

    Represents an analytics provider with its capabilities including
    data sources, supported metrics, and time window configurations.
    Used for provider registration and discovery.

    Attributes:
        provider_id: Unique identifier for the provider.
        provider_type: Type of provider (e.g., "database", "stream", "api").
        data_sources: List of data sources this provider accesses.
        supported_metrics: List of metric names this provider can supply.
        time_windows: Supported time aggregation windows.
        last_updated: When provider configuration was last updated.

    Example:
        ```python
        from uuid import uuid4

        class OrderAnalyticsProvider:
            provider_id: UUID = uuid4()
            provider_type: str = "database"
            data_sources: list[str] = ["orders_db", "transactions_db"]
            supported_metrics: list[str] = ["order.count", "order.value"]
            time_windows: list[LiteralAnalyticsTimeWindow] = [
                "hourly", "daily", "weekly"
            ]
            last_updated: ProtocolDateTime = datetime_impl

            async def validate_provider(self) -> bool:
                return len(self.data_sources) > 0

            def is_available(self) -> bool:
                return len(self.supported_metrics) > 0

        provider = OrderAnalyticsProvider()
        assert isinstance(provider, ProtocolAnalyticsProvider)
        ```
    """

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
    """
    Protocol for aggregated analytics summary reports.

    Contains a complete analytics report for a time period including
    metrics, AI-generated insights, and actionable recommendations.
    Used for dashboard displays and executive reporting.

    Attributes:
        time_window: Aggregation window (hourly, daily, weekly, etc.).
        start_time: Beginning of the analysis period.
        end_time: End of the analysis period.
        metrics: List of aggregated metrics for the period.
        insights: AI-generated insights from the data.
        recommendations: Suggested actions based on analysis.
        confidence_score: Confidence in the analysis (0.0 to 1.0).

    Example:
        ```python
        class WeeklySalesSummary:
            time_window: LiteralAnalyticsTimeWindow = "weekly"
            start_time: ProtocolDateTime = start_datetime_impl
            end_time: ProtocolDateTime = end_datetime_impl
            metrics: list[ProtocolAnalyticsMetric] = [metric1, metric2]
            insights: list[str] = ["Sales increased 15% vs prior week"]
            recommendations: list[str] = ["Consider expanding inventory"]
            confidence_score: float = 0.92

            async def validate_summary(self) -> bool:
                return self.start_time < self.end_time

            def is_complete(self) -> bool:
                return len(self.metrics) > 0

        summary = WeeklySalesSummary()
        assert isinstance(summary, ProtocolAnalyticsSummary)
        ```
    """

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
    """
    Protocol for performance metric data points with thresholds.

    Represents a single performance measurement with category
    classification and configurable warning/critical thresholds.
    Used for performance monitoring and alerting.

    Attributes:
        metric_name: Name of the performance metric.
        category: Performance category (latency, throughput, resource).
        value: Current metric value.
        unit: Unit of measurement.
        timestamp: When the metric was recorded.
        source: Source service or component.
        threshold_warning: Warning threshold, None if not configured.
        threshold_critical: Critical threshold, None if not configured.

    Example:
        ```python
        class ApiLatencyMetric:
            metric_name: str = "api.response.latency"
            category: LiteralPerformanceCategory = "latency"
            value: float = 125.5
            unit: str = "ms"
            timestamp: ProtocolDateTime = datetime_impl
            source: str = "api-gateway"
            threshold_warning: float | None = 200.0
            threshold_critical: float | None = 500.0

            async def validate_performance_metric(self) -> bool:
                return self.value >= 0

            def is_valid(self) -> bool:
                return bool(self.metric_name and self.source)

        metric = ApiLatencyMetric()
        assert isinstance(metric, ProtocolPerformanceMetric)
        ```
    """

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
    """
    Protocol for aggregated performance metrics collection.

    Contains a complete set of performance metrics for a service
    including health scoring, trend analysis, and recommendations.
    Used for service performance dashboards and monitoring.

    Attributes:
        service_name: Name of the monitored service.
        collection_timestamp: When metrics were collected.
        metrics: List of individual performance metrics.
        overall_health_score: Computed health score (0.0 to 1.0).
        performance_trends: Trend indicators per metric category.
        recommendations: Performance improvement suggestions.

    Example:
        ```python
        class GatewayPerformance:
            service_name: str = "api-gateway"
            collection_timestamp: ProtocolDateTime = datetime_impl
            metrics: list[ProtocolPerformanceMetric] = [latency, throughput]
            overall_health_score: float = 0.85
            performance_trends: dict[str, float] = {
                "latency": -0.05,  # improving
                "throughput": 0.10  # increasing
            }
            recommendations: list[str] = [
                "Consider adding cache layer for high-frequency endpoints"
            ]

            async def validate_performance_metrics(self) -> bool:
                return 0.0 <= self.overall_health_score <= 1.0

            def is_healthy(self) -> bool:
                return self.overall_health_score >= 0.7

        metrics = GatewayPerformance()
        assert isinstance(metrics, ProtocolPerformanceMetrics)
        ```
    """

    service_name: str
    collection_timestamp: "ProtocolDateTime"
    metrics: list["ProtocolPerformanceMetric"]
    overall_health_score: float
    performance_trends: dict[str, float]
    recommendations: list[str]

    async def validate_performance_metrics(self) -> bool: ...

    def is_healthy(self) -> bool: ...
