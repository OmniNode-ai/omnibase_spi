"""
Protocol for Standardized Health Monitoring.

Defines interfaces for health checks, monitoring, and service availability
across all ONEX services with consistent patterns and observability.
"""

from collections.abc import Callable
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_core_types import (
        LiteralHealthCheckLevel,
        LiteralHealthDimension,
        LiteralHealthStatus,
        ProtocolHealthCheck,
        ProtocolHealthMetrics,
        ProtocolHealthMonitoring,
    )


@runtime_checkable
class ProtocolHealthMonitor(Protocol):
    """
    Protocol for standardized health monitoring across ONEX services.

    Provides consistent health check patterns, monitoring configuration,
    and availability tracking for distributed system reliability.

    Key Features:
        - Multi-level health checks (quick to comprehensive)
        - Dimensional health assessment (availability, performance, etc.)
        - Configurable monitoring intervals and thresholds
        - Health metrics collection and trending
        - Automated alerting and escalation
        - Service dependency health tracking

    Usage Example:
        ```python
        # Protocol usage example (SPI-compliant)
        service: "HealthMonitor" = get_health_monitor()

        # Usage demonstrates protocol interface without implementation details
        # All operations work through the protocol contract
        # Implementation details are abstracted away from the interface

        health_monitor: "ProtocolHealthMonitor" = HealthMonitorImpl()

        health_status = health_monitor.perform_health_check(
            level="standard",
            dimensions=["availability", "performance"]
        )
        ```
    """

    async def perform_health_check(
        self,
        level: "LiteralHealthCheckLevel",
        dimensions: list["LiteralHealthDimension"],
    ) -> "ProtocolHealthCheck": ...

    async def get_current_health_status(self) -> "LiteralHealthStatus": ...

    async def get_health_metrics(self) -> "ProtocolHealthMetrics": ...

    def configure_monitoring(self, config: "ProtocolHealthMonitoring") -> bool: ...

    async def get_monitoring_configuration(self) -> "ProtocolHealthMonitoring": ...

    async def start_monitoring(self) -> bool: ...

    async def stop_monitoring(self) -> bool: ...

    def is_monitoring_active(self) -> bool: ...

    async def get_health_history(
        self, hours_back: int
    ) -> list["ProtocolHealthCheck"]: ...

    async def register_health_dependency(
        self, dependency_name: str, dependency_monitor: "ProtocolHealthMonitor"
    ) -> bool: ...

    async def unregister_health_dependency(self, dependency_name: str) -> bool: ...

    async def get_dependency_health_status(
        self, dependency_name: str
    ) -> "LiteralHealthStatus": ...

    async def set_health_alert_callback(
        self,
        callback: Callable[[str, "LiteralHealthStatus", "LiteralHealthStatus"], None],
    ) -> bool: ...

    async def get_aggregated_health_status(
        self,
    ) -> dict[str, "LiteralHealthStatus"]: ...
