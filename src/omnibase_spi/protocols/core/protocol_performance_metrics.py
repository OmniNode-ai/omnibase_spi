"""
Protocol for Performance Metrics Collection and Monitoring.

Defines interfaces for performance measurement, threshold management,
and system health monitoring across ONEX services for comprehensive
performance observability and optimization.
"""

from collections.abc import Callable
from typing import TYPE_CHECKING, Protocol, runtime_checkable

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
            # PerformanceMetricsImpl would implement the protocol interface
        # All methods defined in the protocol contract
    """

    async def collect_performance_metrics(
        self, service_name: str
    ) -> "ProtocolPerformanceMetrics": ...

    async def collect_category_metrics(
        self, service_name: str, categories: list["LiteralPerformanceCategory"]
    ) -> list["ProtocolPerformanceMetric"]: ...

    async def record_performance_metric(
        self, metric: "ProtocolPerformanceMetric"
    ) -> bool: ...

    async def record_performance_metrics_batch(
        self, metrics: list["ProtocolPerformanceMetric"]
    ) -> int: ...

    async def set_performance_threshold(
        self,
        metric_name: str,
        warning_threshold: float | None,
        critical_threshold: float | None,
    ) -> bool: ...

    async def get_performance_thresholds(
        self, metric_name: str
    ) -> dict[str, float | None]: ...

    async def check_performance_thresholds(
        self, metrics: "ProtocolPerformanceMetrics"
    ) -> list[dict[str, "ProtocolContextValue"]]: ...

    async def analyze_performance_trends(
        self,
        service_name: str,
        hours_back: int,
        categories: list["LiteralPerformanceCategory"] | None,
    ) -> dict[str, dict[str, float]]: ...

    async def get_performance_baseline(
        self, service_name: str, metric_name: str
    ) -> dict[str, float]: ...

    async def establish_performance_baseline(
        self, service_name: str, metric_name: str, baseline_period_hours: int
    ) -> bool: ...

    async def compare_to_baseline(
        self,
        current_metrics: "ProtocolPerformanceMetrics",
        baseline_deviation_threshold: float,
    ) -> dict[str, dict[str, "ProtocolContextValue"]]: ...

    async def get_performance_recommendations(
        self,
        service_name: str,
        performance_issues: list[dict[str, "ProtocolContextValue"]],
    ) -> list[str]: ...

    async def export_performance_report(
        self,
        service_name: str,
        start_time: "ProtocolDateTime",
        end_time: "ProtocolDateTime",
        categories: list["LiteralPerformanceCategory"] | None,
    ) -> dict[str, "ProtocolContextValue"]: ...

    async def start_real_time_monitoring(
        self,
        service_name: str,
        collection_interval_seconds: int,
        alert_callback: Callable[..., object] | None,
    ) -> str: ...

    async def stop_real_time_monitoring(self, monitoring_session_id: str) -> bool: ...

    async def get_monitoring_sessions(
        self,
    ) -> list[dict[str, "ProtocolContextValue"]]: ...

    async def correlate_cross_service_performance(
        self, service_names: list[str], correlation_window_minutes: int
    ) -> dict[str, dict[str, float]]: ...

    async def identify_performance_bottlenecks(
        self, service_name: str, analysis_period_hours: int
    ) -> list[dict[str, "ProtocolContextValue"]]: ...

    async def predict_performance_issues(
        self, service_name: str, prediction_horizon_hours: int
    ) -> list[dict[str, "ProtocolContextValue"]]: ...

    async def get_performance_summary(
        self, service_names: list[str], summary_period_hours: int
    ) -> dict[str, "ProtocolContextValue"]: ...
