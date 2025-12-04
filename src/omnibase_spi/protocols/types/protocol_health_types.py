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
    """Protocol for health check metrics."""

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
    """Protocol for standardized health checks."""

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
    """Protocol for health monitoring configuration."""

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
    """Protocol for individual metrics points."""

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
    """Protocol for distributed tracing spans."""

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
    """Protocol for audit events."""

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
