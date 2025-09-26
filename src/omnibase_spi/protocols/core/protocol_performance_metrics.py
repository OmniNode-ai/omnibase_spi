"""
Protocol for Performance Metrics Collection and Monitoring.

Defines interfaces for performance measurement, threshold management,
and system health monitoring across ONEX services for comprehensive
performance observability and optimization.
"""

from typing import TYPE_CHECKING, Any, Callable, Optional, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_core_types import (
        LiteralPerformanceCategory,
        ProtocolContextValue,
        ProtocolDateTime,
        ProtocolPerformanceMetric,
        ProtocolPerformanceMetrics,
    )


@runtime_checkable
class ProtocolPerformanceMetricsCollector(Protocol):
    """
    Protocol for performance metrics collection and monitoring.

    Provides standardized performance measurement interface for tracking
    system health, identifying bottlenecks, and enabling proactive
    optimization across ONEX distributed services.

    Key Features:
        - Multi-category performance metrics (latency, throughput, resource, etc.)
        - Real-time and historical performance tracking
        - Configurable alerting thresholds and notifications
        - Performance trend analysis and baseline management
        - Cross-service performance correlation
        - Automated performance recommendations

    Usage Example:

        .. code-block:: python

            # Implementation example (not part of SPI)
            class PerformanceMetricsImpl:
                def collect_performance_metrics(self, service_name):
                    metrics = []

                    # Collect latency metrics
                    response_time = self._measure_response_time()
                    metrics.append(PerformanceMetric(
                        metric_name="response_time",
                        category="latency",
                        value=response_time,
                        unit="ms"
                    ))

                    # Collect throughput metrics
                    rps = self._calculate_requests_per_second()
                    metrics.append(PerformanceMetric(
                        metric_name="requests_per_second",
                        category="throughput",
                        value=rps,
                        unit="req/s"
                    ))

                    return PerformanceMetrics(
                        service_name=service_name,
                        metrics=metrics,
                        overall_health_score=self._calculate_health_score(metrics)
                    )

            # Usage in application code
            perf_collector: ProtocolPerformanceMetricsCollector = PerformanceMetricsImpl()

            # Collect current performance metrics
            current_metrics = perf_collector.collect_performance_metrics(
                service_name="user-service"
            )

            # Set performance thresholds
            perf_collector.set_performance_threshold(
                metric_name="response_time",
                warning_threshold=500.0,
                critical_threshold=1000.0
            )

            # Analyze performance trends
            trends = perf_collector.analyze_performance_trends(
                service_name="user-service",
                hours_back=24,
                categories=["latency", "throughput"]
            )
    """

    def collect_performance_metrics(
        self,
        service_name: str,
    ) -> "ProtocolPerformanceMetrics":
        """
        Collect comprehensive performance metrics for a service.

        Args:
            service_name: Name of service to collect metrics for

        Returns:
            Complete performance metrics collection with health score

        Raises:
            ValueError: If service_name is empty or invalid
            RuntimeError: If service is unreachable or metrics collection fails

        Note:
            Collects real-time metrics across all performance categories
            including latency, throughput, resource utilization, error rates,
            and availability metrics.
        """
        ...

    def collect_category_metrics(
        self,
        service_name: str,
        categories: list["LiteralPerformanceCategory"],
    ) -> list["ProtocolPerformanceMetric"]:
        """
        Collect performance metrics for specific categories.

        Args:
            service_name: Name of service to collect metrics for
            categories: List of performance categories to collect

        Returns:
            List of performance metrics for specified categories

        Note:
            Enables targeted metric collection for specific performance
            aspects, reducing overhead when only certain metrics are needed.
        """
        ...

    def record_performance_metric(
        self,
        metric: "ProtocolPerformanceMetric",
    ) -> bool:
        """
        Record a single performance metric.

        Args:
            metric: Performance metric to record

        Returns:
            True if metric was recorded successfully

        Raises:
            ValueError: If metric validation fails or contains invalid data
            RuntimeError: If metric recording fails due to system issues

        Note:
            Used for custom metric recording and integration with
            external monitoring systems or specialized measurements.
        """
        ...

    def record_performance_metrics_batch(
        self,
        metrics: list["ProtocolPerformanceMetric"],
    ) -> int:
        """
        Record multiple performance metrics efficiently.

        Args:
            metrics: List of performance metrics to record

        Returns:
            Number of metrics successfully recorded

        Note:
            Batch recording improves performance for high-frequency
            metrics collection and reduces monitoring system overhead.
        """
        ...

    def set_performance_threshold(
        self,
        metric_name: str,
        warning_threshold: Optional[float],
        critical_threshold: Optional[float],
    ) -> bool:
        """
        Set performance thresholds for metric alerting.

        Args:
            metric_name: Name of metric to configure
            warning_threshold: Optional warning level threshold
            critical_threshold: Optional critical level threshold

        Returns:
            True if thresholds were configured successfully

        Raises:
            ValueError: If metric_name is empty, thresholds are negative, or critical_threshold < warning_threshold
            RuntimeError: If threshold configuration fails

        Note:
            Thresholds enable automated alerting when performance
            degrades beyond acceptable levels for proactive response.
        """
        ...

    def get_performance_thresholds(
        self,
        metric_name: str,
    ) -> dict[str, Optional[float]]:
        """
        Get configured performance thresholds for a metric.

        Args:
            metric_name: Name of metric to get thresholds for

        Returns:
            Dictionary with warning and critical threshold values

        Note:
            Returns current threshold configuration for operational
            visibility and threshold management.
        """
        ...

    def check_performance_thresholds(
        self,
        metrics: "ProtocolPerformanceMetrics",
    ) -> list[dict[str, "ProtocolContextValue"]]:
        """
        Check metrics against configured thresholds.

        Args:
            metrics: Performance metrics to check

        Returns:
            List of threshold violations with severity and details

        Note:
            Evaluates current metrics against thresholds to identify
            performance issues requiring attention or intervention.
        """
        ...

    def analyze_performance_trends(
        self,
        service_name: str,
        hours_back: int,
        categories: Optional[list["LiteralPerformanceCategory"]],
    ) -> dict[str, dict[str, float]]:
        """
        Analyze performance trends over time.

        Args:
            service_name: Service to analyze trends for
            hours_back: Hours of historical data to analyze
            categories: Optional categories to focus analysis on

        Returns:
            Trend analysis with metric names and trend scores

        Note:
            Provides performance trend analysis for capacity planning,
            optimization opportunities, and performance regression detection.
        """
        ...

    def get_performance_baseline(
        self,
        service_name: str,
        metric_name: str,
    ) -> dict[str, float]:
        """
        Get performance baseline for a service metric.

        Args:
            service_name: Service to get baseline for
            metric_name: Metric to get baseline for

        Returns:
            Baseline statistics including mean, percentiles, and variance

        Note:
            Baselines provide reference points for performance comparison
            and anomaly detection in operational monitoring.
        """
        ...

    def establish_performance_baseline(
        self,
        service_name: str,
        metric_name: str,
        baseline_period_hours: int,
    ) -> bool:
        """
        Establish new performance baseline from historical data.

        Args:
            service_name: Service to establish baseline for
            metric_name: Metric to establish baseline for
            baseline_period_hours: Hours of data to use for baseline

        Returns:
            True if baseline was established successfully

        Note:
            Creates new performance baseline from stable operational periods
            for improved anomaly detection and performance comparison.
        """
        ...

    def compare_to_baseline(
        self,
        current_metrics: "ProtocolPerformanceMetrics",
        baseline_deviation_threshold: float,
    ) -> dict[str, dict[str, "ProtocolContextValue"]]:
        """
        Compare current metrics to established baselines.

        Args:
            current_metrics: Current performance metrics to compare
            baseline_deviation_threshold: Threshold for significant deviation (0.0-1.0)

        Returns:
            Comparison results with deviations and significance

        Raises:
            ValueError: If baseline_deviation_threshold is not between 0.0 and 1.0
            RuntimeError: If baseline data is not available or comparison fails

        Note:
            Identifies performance deviations from normal baseline behavior
            for anomaly detection and performance regression analysis.
        """
        ...

    def get_performance_recommendations(
        self,
        service_name: str,
        performance_issues: list[dict[str, "ProtocolContextValue"]],
    ) -> list[str]:
        """
        Get performance optimization recommendations.

        Args:
            service_name: Service to get recommendations for
            performance_issues: List of identified performance issues

        Returns:
            List of actionable performance optimization recommendations

        Note:
            Provides AI-driven recommendations for performance optimization
            based on identified issues and best practices.
        """
        ...

    def export_performance_report(
        self,
        service_name: str,
        start_time: "ProtocolDateTime",
        end_time: "ProtocolDateTime",
        categories: Optional[list["LiteralPerformanceCategory"]],
    ) -> dict[str, "ProtocolContextValue"]:
        """
        Export comprehensive performance report for time period.

        Args:
            service_name: Service to generate report for
            start_time: Start of reporting period
            end_time: End of reporting period
            categories: Optional categories to include in report

        Returns:
            Comprehensive performance report with metrics, trends, and analysis

        Note:
            Generates detailed performance reports for operational reviews,
            capacity planning, and performance optimization initiatives.
        """
        ...

    def start_real_time_monitoring(
        self,
        service_name: str,
        collection_interval_seconds: int,
        alert_callback: Optional[Callable[..., Any]],
    ) -> str:
        """
        Start real-time performance monitoring.

        Args:
            service_name: Service to monitor
            collection_interval_seconds: How often to collect metrics
            alert_callback: Optional callback for threshold violations

        Returns:
            Monitoring session ID for management

        Raises:
            ValueError: If service_name is empty or collection_interval_seconds is <= 0
            RuntimeError: If monitoring system is unavailable or session creation fails

        Note:
            Begins continuous performance monitoring with configurable
            intervals and real-time alerting for proactive issue detection.
        """
        ...

    def stop_real_time_monitoring(
        self,
        monitoring_session_id: str,
    ) -> bool:
        """
        Stop real-time performance monitoring.

        Args:
            monitoring_session_id: ID of monitoring session to stop

        Returns:
            True if monitoring was stopped successfully

        Note:
            Stops continuous monitoring session while preserving
            collected data and configuration for future use.
        """
        ...

    def get_monitoring_sessions(self) -> list[dict[str, "ProtocolContextValue"]]:
        """
        Get active performance monitoring sessions.

        Returns:
            List of active monitoring sessions with status

        Note:
            Provides visibility into active monitoring sessions
            for operational management and resource planning.
        """
        ...

    def correlate_cross_service_performance(
        self,
        service_names: list[str],
        correlation_window_minutes: int,
    ) -> dict[str, dict[str, float]]:
        """
        Correlate performance metrics across multiple services.

        Args:
            service_names: Services to correlate performance for
            correlation_window_minutes: Time window for correlation analysis

        Returns:
            Cross-service performance correlations and dependencies

        Note:
            Identifies performance dependencies and impacts across
            distributed services for holistic system optimization.
        """
        ...

    def identify_performance_bottlenecks(
        self,
        service_name: str,
        analysis_period_hours: int,
    ) -> list[dict[str, "ProtocolContextValue"]]:
        """
        Identify performance bottlenecks through analysis.

        Args:
            service_name: Service to analyze for bottlenecks
            analysis_period_hours: Hours of data to analyze

        Returns:
            List of identified bottlenecks with impact assessment

        Note:
            Uses advanced analytics to identify performance bottlenecks
            and their impact on overall system performance.
        """
        ...

    def predict_performance_issues(
        self,
        service_name: str,
        prediction_horizon_hours: int,
    ) -> list[dict[str, "ProtocolContextValue"]]:
        """
        Predict potential performance issues based on trends.

        Args:
            service_name: Service to predict issues for
            prediction_horizon_hours: Hours ahead to predict

        Returns:
            List of predicted performance issues with probability

        Note:
            Uses machine learning and trend analysis to predict
            potential performance issues for proactive mitigation.
        """
        ...

    def get_performance_summary(
        self,
        service_names: list[str],
        summary_period_hours: int,
    ) -> dict[str, "ProtocolContextValue"]:
        """
        Get performance summary across multiple services.

        Args:
            service_names: Services to include in summary
            summary_period_hours: Hours of data to summarize

        Returns:
            Performance summary with key metrics and health indicators

        Note:
            Provides high-level performance overview for operational
            dashboards and executive reporting.
        """
        ...
