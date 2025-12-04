"""Health and metrics protocol types for ONEX SPI interfaces."""

from datetime import datetime
from typing import Literal, Protocol, runtime_checkable
from uuid import UUID

from omnibase_spi.protocols.types.protocol_base_types import (
    ContextValue,
    LiteralHealthCheckLevel,
    LiteralHealthDimension,
    LiteralHealthStatus,
    LiteralOperationStatus,
    ProtocolDateTime,
)


@runtime_checkable
class ProtocolCacheStatistics(Protocol):
    """
    Protocol for comprehensive cache service statistics.

    Provides detailed performance and usage metrics for cache services
    across ONEX systems. Used for monitoring, optimization, and capacity
    planning of distributed caching infrastructure.

    Key Features:
        - Performance metrics (hits, misses, ratios)
        - Resource usage tracking (memory, entry counts)
        - Operational statistics (evictions, access patterns)
        - Capacity management information

    Metrics Description:
        - hit_count: Number of successful cache retrievals
        - miss_count: Number of cache misses requiring data source access
        - hit_ratio: Efficiency ratio (hits / total_requests)
        - memory_usage_bytes: Current memory consumption
        - entry_count: Number of cached entries
        - eviction_count: Number of entries removed due to capacity limits
        - last_accessed: Timestamp of most recent cache access
        - cache_size_limit: Maximum cache capacity (if configured)

    Usage:
        stats = cache_service.get_statistics()
        if stats.hit_ratio < 0.8:
            logger.warning(f"Low cache hit ratio: {stats.hit_ratio:.2%}")
    """

    hit_count: int
    miss_count: int
    total_requests: int
    hit_ratio: float
    memory_usage_bytes: int
    entry_count: int
    eviction_count: int
    last_accessed: datetime | None
    cache_size_limit: int | None

    async def validate_statistics(self) -> bool: ...

    def is_current(self) -> bool: ...


@runtime_checkable
class ProtocolHealthMetrics(Protocol):
    """
    Protocol for comprehensive health check metrics and resource utilization.

    Provides standardized metrics for monitoring system health across ONEX
    services. Includes response timing, resource usage, connection tracking,
    and throughput measurements for operational visibility.

    Attributes:
        response_time_ms: Service response time in milliseconds.
        cpu_usage_percent: CPU utilization percentage (0-100).
        memory_usage_percent: Memory utilization percentage (0-100).
        disk_usage_percent: Disk utilization percentage (0-100).
        connection_count: Current number of active connections.
        error_rate_percent: Percentage of requests resulting in errors.
        throughput_per_second: Requests processed per second.

    Example:
        ```python
        class ServiceMetrics:
            response_time_ms: float = 45.5
            cpu_usage_percent: float = 35.0
            memory_usage_percent: float = 62.0
            disk_usage_percent: float = 48.0
            connection_count: int = 150
            error_rate_percent: float = 0.5
            throughput_per_second: float = 1250.0

            async def validate_metrics(self) -> bool:
                return self.cpu_usage_percent <= 100

            def is_within_thresholds(self) -> bool:
                return self.cpu_usage_percent < 80

        metrics = ServiceMetrics()
        assert isinstance(metrics, ProtocolHealthMetrics)
        ```
    """

    response_time_ms: float
    cpu_usage_percent: float
    memory_usage_percent: float
    disk_usage_percent: float
    connection_count: int
    error_rate_percent: float
    throughput_per_second: float

    async def validate_metrics(self) -> bool: ...

    def is_within_thresholds(self) -> bool: ...


@runtime_checkable
class ProtocolHealthCheck(Protocol):
    """
    Protocol for standardized health check results and diagnostics.

    Provides comprehensive health check information including multi-dimensional
    status tracking, metrics collection, and actionable recommendations.
    Used for service health monitoring and automated alerting.

    Attributes:
        service_name: Name of the service being checked.
        check_level: Depth of health check (basic, standard, deep).
        dimensions_checked: List of health dimensions evaluated.
        overall_status: Aggregated health status.
        individual_checks: Per-component health status mapping.
        metrics: Detailed health metrics from the check.
        check_duration_ms: Time taken to complete the check.
        timestamp: When the check was performed.
        recommendations: Suggested actions for improvement.

    Example:
        ```python
        class ApiHealthCheck:
            service_name: str = "api-gateway"
            check_level: LiteralHealthCheckLevel = "standard"
            dimensions_checked: list[LiteralHealthDimension] = ["cpu", "memory"]
            overall_status: LiteralHealthStatus = "healthy"
            individual_checks: dict[str, LiteralHealthStatus] = {
                "database": "healthy", "cache": "degraded"
            }
            metrics: ProtocolHealthMetrics = metrics_impl
            check_duration_ms: float = 125.5
            timestamp: ProtocolDateTime = datetime_impl
            recommendations: list[str] = ["Consider scaling cache nodes"]

            async def validate_health_check(self) -> bool:
                return self.check_duration_ms > 0

            def is_passing(self) -> bool:
                return self.overall_status == "healthy"

        check = ApiHealthCheck()
        assert isinstance(check, ProtocolHealthCheck)
        ```
    """

    service_name: str
    check_level: LiteralHealthCheckLevel
    dimensions_checked: list[LiteralHealthDimension]
    overall_status: "LiteralHealthStatus"
    individual_checks: dict[str, "LiteralHealthStatus"]
    metrics: "ProtocolHealthMetrics"
    check_duration_ms: float
    timestamp: "ProtocolDateTime"
    recommendations: list[str]

    async def validate_health_check(self) -> bool: ...

    def is_passing(self) -> bool: ...


@runtime_checkable
class ProtocolHealthMonitoring(Protocol):
    """
    Protocol for health monitoring configuration and alerting rules.

    Defines the configuration for continuous health monitoring including
    check intervals, thresholds for failure detection, and alerting
    rules. Used for configuring monitoring systems.

    Attributes:
        check_interval_seconds: Time between health checks.
        timeout_seconds: Maximum time to wait for check response.
        failure_threshold: Consecutive failures before marking unhealthy.
        recovery_threshold: Consecutive successes before marking healthy.
        alert_on_status: Status values that trigger alerts.
        escalation_rules: Rules for alert escalation.

    Example:
        ```python
        class MonitoringConfig:
            check_interval_seconds: int = 30
            timeout_seconds: int = 10
            failure_threshold: int = 3
            recovery_threshold: int = 2
            alert_on_status: list[LiteralHealthStatus] = ["unhealthy", "critical"]
            escalation_rules: dict[str, ContextValue] = {
                "critical": {"notify": "oncall", "delay_minutes": 0}
            }

            async def validate_monitoring_config(self) -> bool:
                return self.check_interval_seconds > self.timeout_seconds

            def is_reasonable(self) -> bool:
                return self.failure_threshold >= 1

        config = MonitoringConfig()
        assert isinstance(config, ProtocolHealthMonitoring)
        ```
    """

    check_interval_seconds: int
    timeout_seconds: int
    failure_threshold: int
    recovery_threshold: int
    alert_on_status: list["LiteralHealthStatus"]
    escalation_rules: dict[str, "ContextValue"]

    async def validate_monitoring_config(self) -> bool: ...

    def is_reasonable(self) -> bool: ...


@runtime_checkable
class ProtocolMetricsPoint(Protocol):
    """
    Protocol for individual metrics data points with dimensional metadata.

    Represents a single metric measurement with associated tags and
    dimensions for filtering and aggregation. Used for time-series
    metrics collection and observability.

    Attributes:
        metric_name: Name identifier for the metric.
        value: Numeric value of the measurement.
        unit: Unit of measurement (e.g., "ms", "bytes", "percent").
        timestamp: When the measurement was taken.
        tags: Key-value pairs for metric categorization.
        dimensions: Dimensional attributes for aggregation.

    Example:
        ```python
        class LatencyMetric:
            metric_name: str = "api.request.latency"
            value: float = 45.5
            unit: str = "ms"
            timestamp: ProtocolDateTime = datetime_impl
            tags: dict[str, ContextValue] = {"service": "gateway"}
            dimensions: dict[str, ContextValue] = {"endpoint": "/api/v1/users"}

            async def validate_metrics_point(self) -> bool:
                return self.value >= 0

            def is_valid_measurement(self) -> bool:
                return bool(self.metric_name)

        point = LatencyMetric()
        assert isinstance(point, ProtocolMetricsPoint)
        ```
    """

    metric_name: str
    value: float
    unit: str
    timestamp: "ProtocolDateTime"
    tags: dict[str, "ContextValue"]
    dimensions: dict[str, "ContextValue"]

    async def validate_metrics_point(self) -> bool: ...

    def is_valid_measurement(self) -> bool: ...


@runtime_checkable
class ProtocolTraceSpan(Protocol):
    """
    Protocol for distributed tracing spans in observability systems.

    Represents a single span in a distributed trace, capturing timing,
    hierarchy, and contextual information. Used for request tracing
    and debugging across ONEX services.

    Attributes:
        span_id: Unique identifier for this span.
        trace_id: Identifier for the overall trace.
        parent_span_id: Parent span ID for hierarchy, None if root.
        operation_name: Name of the traced operation.
        start_time: When the span started.
        end_time: When the span ended, None if still active.
        status: Operation outcome status.
        tags: Key-value metadata for the span.
        logs: Time-stamped log entries within the span.

    Example:
        ```python
        from uuid import uuid4

        class HttpRequestSpan:
            span_id: UUID = uuid4()
            trace_id: UUID = uuid4()
            parent_span_id: UUID | None = None
            operation_name: str = "HTTP GET /api/users"
            start_time: ProtocolDateTime = datetime_impl
            end_time: ProtocolDateTime | None = datetime_impl
            status: LiteralOperationStatus = "completed"
            tags: dict[str, ContextValue] = {"http.method": "GET"}
            logs: list[dict[str, ContextValue]] = []

            async def validate_trace_span(self) -> bool:
                return self.span_id != self.parent_span_id

            def is_complete(self) -> bool:
                return self.end_time is not None

        span = HttpRequestSpan()
        assert isinstance(span, ProtocolTraceSpan)
        ```
    """

    span_id: UUID
    trace_id: UUID
    parent_span_id: UUID | None
    operation_name: str
    start_time: "ProtocolDateTime"
    end_time: "ProtocolDateTime | None"
    status: LiteralOperationStatus
    tags: dict[str, "ContextValue"]
    logs: list[dict[str, "ContextValue"]]

    async def validate_trace_span(self) -> bool: ...

    def is_complete(self) -> bool: ...


@runtime_checkable
class ProtocolAuditEvent(Protocol):
    """
    Protocol for security and compliance audit events.

    Captures detailed audit information for security monitoring,
    compliance reporting, and forensic analysis. Includes actor
    identification, resource access, and sensitivity classification.

    Attributes:
        event_id: Unique identifier for the audit event.
        event_type: Category of the event (e.g., "access", "modification").
        actor: Identity of who performed the action.
        resource: Resource that was accessed or modified.
        action: Specific action performed.
        timestamp: When the event occurred.
        outcome: Result of the action.
        metadata: Additional context and details.
        sensitivity_level: Data classification level.

    Example:
        ```python
        from uuid import uuid4

        class DataAccessEvent:
            event_id: UUID = uuid4()
            event_type: str = "data_access"
            actor: str = "user@example.com"
            resource: str = "/api/v1/users/123"
            action: str = "read"
            timestamp: ProtocolDateTime = datetime_impl
            outcome: LiteralOperationStatus = "completed"
            metadata: dict[str, ContextValue] = {"ip": "192.168.1.1"}
            sensitivity_level: Literal[...] = "internal"

            async def validate_audit_event(self) -> bool:
                return bool(self.actor and self.resource)

            def is_complete(self) -> bool:
                return self.outcome is not None

        event = DataAccessEvent()
        assert isinstance(event, ProtocolAuditEvent)
        ```
    """

    event_id: UUID
    event_type: str
    actor: str
    resource: str
    action: str
    timestamp: "ProtocolDateTime"
    outcome: LiteralOperationStatus
    metadata: dict[str, "ContextValue"]
    sensitivity_level: Literal["public", "internal", "confidential", "restricted"]

    async def validate_audit_event(self) -> bool: ...

    def is_complete(self) -> bool: ...
