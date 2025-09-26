"""
Protocol for Analytics Data Providers and Collection.

Defines interfaces for analytics data collection, aggregation, and reporting
across all ONEX services with consistent patterns and metrics.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_core_types import (
        LiteralAnalyticsMetricType,
        LiteralAnalyticsTimeWindow,
        ProtocolAnalyticsMetric,
        ProtocolAnalyticsProvider,
        ProtocolAnalyticsSummary,
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
        # Implementation example (not part of SPI)
        class AnalyticsProviderImpl:
            def collect_metrics(self, data_sources, time_window):
                metrics = []
                for source in data_sources:
                    raw_data = self._fetch_data(source, time_window)
                    processed_metrics = self._process_metrics(raw_data)
                    metrics.extend(processed_metrics)

                return self._aggregate_metrics(metrics, time_window)

            def generate_insights(self, summary):
                insights = []
                for metric in summary.metrics:
                    if metric.value > self._get_threshold(metric.name):
                        insights.append(f"High {metric.name} detected")

                return insights

        # Usage in application code
        analytics: ProtocolAnalyticsDataProvider = AnalyticsProviderImpl()

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

    def configure_analytics_provider(
        self,
        provider_config: "ProtocolAnalyticsProvider",
    ) -> bool:
        """
        Configure analytics provider with data sources and capabilities.

        Args:
            provider_config: Provider configuration with sources and metrics

        Returns:
            True if provider was configured successfully

        Note:
            Sets up data source connections, metric definitions,
            and collection intervals for analytics processing.
        """
        ...

    def get_analytics_provider_info(self) -> "ProtocolAnalyticsProvider":
        """
        Get current analytics provider configuration.

        Returns:
            Current provider configuration and capabilities

        Note:
            Returns active configuration including data sources,
            supported metrics, and time windows.
        """
        ...

    def collect_metric(
        self,
        metric: "ProtocolAnalyticsMetric",
    ) -> bool:
        """
        Collect individual analytics metric.

        Args:
            metric: Analytics metric with value, type, and metadata

        Returns:
            True if metric was collected successfully

        Note:
            Stores metric for aggregation and analysis.
            Metric timestamp determines which time window it belongs to.
        """
        ...

    def collect_metrics_batch(
        self,
        metrics: list["ProtocolAnalyticsMetric"],
    ) -> int:
        """
        Collect batch of analytics metrics.

        Args:
            metrics: List of analytics metrics to collect

        Returns:
            Number of metrics successfully collected

        Note:
            Efficient batch collection for high-volume metric ingestion.
            Failed metrics are logged but don't stop batch processing.
        """
        ...

    def query_metrics(
        self,
        metric_names: list[str],
        time_window: "LiteralAnalyticsTimeWindow",
        start_time: "ProtocolDateTime",
        end_time: "ProtocolDateTime",
    ) -> list["ProtocolAnalyticsMetric"]:
        """
        Query metrics for specific time range and names.

        Args:
            metric_names: List of metric names to retrieve
            time_window: Time window granularity for aggregation
            start_time: Start of time range
            end_time: End of time range

        Returns:
            List of metrics matching criteria

        Note:
            Aggregates metrics according to time window granularity.
            Empty list returned if no matching metrics found.
        """
        ...

    def generate_analytics_summary(
        self,
        time_window: "LiteralAnalyticsTimeWindow",
        data_sources: list[str] | None = None,
        metric_types: list["LiteralAnalyticsMetricType"] | None = None,
    ) -> "ProtocolAnalyticsSummary":
        """
        Generate analytics summary for specified criteria.

        Args:
            time_window: Time window for summary generation
            data_sources: Optional filter by data sources
            metric_types: Optional filter by metric types

        Returns:
            Comprehensive analytics summary with insights

        Note:
            Aggregates metrics, generates insights, and provides
            recommendations based on analytics patterns and thresholds.
        """
        ...

    def get_supported_metrics(self) -> list[str]:
        """
        Get list of supported metric names.

        Returns:
            List of metric names this provider can collect

        Note:
            Metrics depend on configured data sources and
            analytics provider capabilities.
        """
        ...

    def get_supported_time_windows(self) -> list["LiteralAnalyticsTimeWindow"]:
        """
        Get supported time window granularities.

        Returns:
            List of time windows supported by this provider

        Note:
            Time windows determine aggregation levels:
            real_time, hourly, daily, weekly, monthly.
        """
        ...

    def add_data_source(
        self,
        source_name: str,
        source_config: dict[str, str | int | bool],
    ) -> bool:
        """
        Add new data source for analytics collection.

        Args:
            source_name: Unique name for the data source
            source_config: Configuration for data source connection

        Returns:
            True if data source was added successfully

        Note:
            Dynamically adds data sources to existing analytics provider.
            New metrics from source become available after configuration.
        """
        ...

    def remove_data_source(
        self,
        source_name: str,
    ) -> bool:
        """
        Remove data source from analytics collection.

        Args:
            source_name: Name of data source to remove

        Returns:
            True if data source was removed successfully

        Note:
            Stops collecting metrics from specified data source.
            Historical data remains available in analytics store.
        """
        ...

    def get_analytics_health(self) -> dict[str, str | int | float]:
        """
        Get analytics system health status.

        Returns:
            Dictionary with analytics health indicators

        Note:
            Includes metrics collection rates, data source connectivity,
            processing latency, and storage utilization.
        """
        ...

    def create_custom_metric(
        self,
        metric_name: str,
        metric_type: "LiteralAnalyticsMetricType",
        unit: str,
        description: str,
    ) -> bool:
        """
        Create custom metric definition.

        Args:
            metric_name: Unique name for the custom metric
            metric_type: Type of metric (counter, gauge, histogram, summary)
            unit: Unit of measurement for metric values
            description: Human-readable description

        Returns:
            True if custom metric was created successfully

        Note:
            Custom metrics can be collected using standard metric collection methods.
            Metric definition persists across analytics provider restarts.
        """
        ...

    def delete_custom_metric(
        self,
        metric_name: str,
    ) -> bool:
        """
        Delete custom metric definition.

        Args:
            metric_name: Name of custom metric to delete

        Returns:
            True if custom metric was deleted successfully

        Note:
            Removes metric definition and stops future collection.
            Historical metric data is retained for analysis.
        """
        ...

    def set_metric_threshold(
        self,
        metric_name: str,
        warning_threshold: float,
        critical_threshold: float,
    ) -> bool:
        """
        Set alerting thresholds for metric.

        Args:
            metric_name: Name of metric to set thresholds for
            warning_threshold: Value that triggers warning alerts
            critical_threshold: Value that triggers critical alerts

        Returns:
            True if thresholds were set successfully

        Note:
            Thresholds are used for automated alerting and
            insight generation in analytics summaries.
        """
        ...

    def get_metric_thresholds(
        self,
        metric_name: str,
    ) -> dict[str, float] | None:
        """
        Get alerting thresholds for metric.

        Args:
            metric_name: Name of metric to get thresholds for

        Returns:
            Dictionary with warning and critical thresholds, or None

        Note:
            Returns None if no thresholds are configured for the metric.
        """
        ...

    def generate_insights(
        self,
        summary: "ProtocolAnalyticsSummary",
    ) -> list[str]:
        """
        Generate insights from analytics summary.

        Args:
            summary: Analytics summary to analyze for patterns

        Returns:
            List of generated insights and observations

        Note:
            Uses machine learning, statistical analysis, and threshold
            comparisons to identify significant patterns and anomalies.
        """
        ...

    def generate_recommendations(
        self,
        summary: "ProtocolAnalyticsSummary",
    ) -> list[str]:
        """
        Generate actionable recommendations from analytics.

        Args:
            summary: Analytics summary to analyze for optimization opportunities

        Returns:
            List of actionable recommendations

        Note:
            Provides specific actions to improve system performance,
            reduce errors, or optimize resource utilization.
        """
        ...

    def export_analytics_data(
        self,
        format_type: str,
        time_range: tuple["ProtocolDateTime", "ProtocolDateTime"],
        metric_filter: list[str] | None = None,
    ) -> bytes | str:
        """
        Export analytics data in specified format.

        Args:
            format_type: Export format (json, csv, parquet, etc.)
            time_range: Tuple of start and end times for export
            metric_filter: Optional list of metric names to include

        Returns:
            Exported data in specified format

        Note:
            Enables analytics data export for external analysis,
            reporting, or long-term archival storage.
        """
        ...
