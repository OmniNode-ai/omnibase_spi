"""
Protocol for Analytics Data Providers and Collection.

Defines interfaces for analytics data collection, aggregation, and reporting
across all ONEX services with consistent patterns and metrics.
"""

from typing import Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_analytics_types import (
    ProtocolAnalyticsMetric,
    ProtocolAnalyticsProvider,
    ProtocolAnalyticsSummary,
)
from omnibase_spi.protocols.types.protocol_base_types import (
    ContextValue,
    LiteralAnalyticsMetricType,
    LiteralAnalyticsTimeWindow,
    ProtocolDateTime,
)


@runtime_checkable
class ProtocolAnalyticsDataProvider(Protocol):
    """
    Protocol for analytics data providers and collection systems.

    Provides consistent analytics patterns, metric collection, aggregation,
    and reporting for comprehensive system monitoring and business intelligence.

    Key Features:
        - Multi-source data collection and aggregation
        - Time-windowed analytics with multiple granularities
        - Metric type classification (counter, gauge, histogram, summary)
        - Real-time and batch analytics processing
        - Insight generation and recommendation systems
        - Analytics pipeline management and data quality

    Usage Example:
        ```python
        # Protocol usage example (SPI-compliant)
        service: "AnalyticsProvider" = get_analytics_provider()

        # Usage demonstrates protocol interface without implementation details
        # All operations work through the protocol contract
        # Implementation details are abstracted away from the interface

        analytics: "ProtocolAnalyticsDataProvider" = AnalyticsProviderImpl()

        # Configure analytics collection
        provider_config = analytics.configure_analytics_provider(
            provider_id="service_metrics",
            data_sources=["database", "api", "cache"],
            supported_metrics=["response_time", "error_rate", "throughput"]
        )

        # Collect and analyze metrics
        summary = analytics.generate_analytics_summary(
            time_window="hourly",
            data_sources=["database", "api"]
        )
        ```
    """

    async def configure_analytics_provider(
        self, provider_config: "ProtocolAnalyticsProvider"
    ) -> bool: ...

    async def get_analytics_provider_info(self) -> "ProtocolAnalyticsProvider": ...

    async def collect_metric(self, metric: "ProtocolAnalyticsMetric") -> bool: ...

    async def collect_metrics_batch(
        self, metrics: list["ProtocolAnalyticsMetric"]
    ) -> int: ...

    async def query_metrics(
        self,
        metric_names: list[str],
        time_window: "LiteralAnalyticsTimeWindow",
        start_time: "ProtocolDateTime",
        end_time: "ProtocolDateTime",
    ) -> list["ProtocolAnalyticsMetric"]: ...

    async def generate_analytics_summary(
        self,
        time_window: "LiteralAnalyticsTimeWindow",
        data_sources: list[str] | None = None,
        metric_types: list["LiteralAnalyticsMetricType"] | None = None,
    ) -> "ProtocolAnalyticsSummary": ...

    async def get_supported_metrics(self) -> list[str]: ...

    async def get_supported_time_windows(
        self,
    ) -> list["LiteralAnalyticsTimeWindow"]: ...

    async def add_data_source(
        self, source_name: str, source_config: dict[str, str | int | bool]
    ) -> bool: ...

    async def remove_data_source(self, source_name: str) -> bool: ...

    async def get_analytics_health(self) -> dict[str, "ContextValue"]: ...

    async def create_custom_metric(
        self,
        metric_name: str,
        metric_type: "LiteralAnalyticsMetricType",
        unit: str,
        description: str,
    ) -> bool: ...

    async def delete_custom_metric(self, metric_name: str) -> bool: ...

    async def set_metric_threshold(
        self, metric_name: str, warning_threshold: float, critical_threshold: float
    ) -> bool: ...

    async def get_metric_thresholds(
        self, metric_name: str
    ) -> dict[str, float] | None: ...

    async def generate_insights(
        self, summary: "ProtocolAnalyticsSummary"
    ) -> list[str]: ...

    async def generate_recommendations(
        self, summary: "ProtocolAnalyticsSummary"
    ) -> list[str]: ...

    async def export_analytics_data(
        self,
        format_type: str,
        time_range: tuple["ProtocolDateTime", "ProtocolDateTime"],
        metric_filter: list[str] | None = None,
    ) -> bytes | str: ...
