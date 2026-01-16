"""
MCP Monitor Protocol - ONEX SPI Interface.

Protocol definition for MCP monitoring and health management.
Provides comprehensive monitoring, alerting, and health management for MCP systems.

Domain: MCP monitoring, health checks, and observability
"""

from collections.abc import Callable
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_core_types import ContextValue

if TYPE_CHECKING:
    from omnibase_core.types import JsonType
from omnibase_spi.protocols.types.protocol_mcp_types import (
    ProtocolMCPHealthCheck,
    ProtocolMCPSubsystemRegistration,
)


@runtime_checkable
class ProtocolMCPHealthMonitor(Protocol):
    """
    Protocol for MCP health monitoring operations.

    Handles health checks, status monitoring, and failure detection
    for MCP subsystems and registry components.
    """

    async def perform_health_check(
        self, subsystem: ProtocolMCPSubsystemRegistration, check_tools: bool
    ) -> ProtocolMCPHealthCheck: ...

    async def monitor_subsystem_health(
        self,
        subsystem_id: str,
        interval_seconds: int,
        callback: "Callable[[JsonType], JsonType] | None",
    ) -> bool: ...

    async def stop_health_monitoring(self, subsystem_id: str) -> bool: ...

    async def get_health_status(
        self, subsystem_id: str
    ) -> ProtocolMCPHealthCheck | None: ...

    async def get_health_history(
        self, subsystem_id: str, hours: int, limit: int
    ) -> list[ProtocolMCPHealthCheck]: ...

    async def detect_health_anomalies(
        self, subsystem_id: str | None, time_window_hours: int
    ) -> list[dict[str, ContextValue]]: ...


@runtime_checkable
class ProtocolMCPMonitor(Protocol):
    """
    Comprehensive MCP monitoring protocol for system observability.

    Provides complete monitoring capabilities including health monitoring,
    performance tracking, alerting, and operational dashboards.

    Key Features:
        - **Comprehensive Health Monitoring**: Monitor all subsystems and tools
        - **Performance Metrics**: Track execution times, success rates, and throughput
        - **Intelligent Alerting**: Generate alerts based on thresholds and anomalies
        - **Dashboard Generation**: Create operational dashboards and reports
        - **Historical Analysis**: Analyze trends and patterns over time
        - **Automated Recovery**: Trigger automated recovery actions
        - **Multi-Level Monitoring**: Registry, subsystem, and tool-level monitoring
    """

    @property
    def health_monitor(self) -> ProtocolMCPHealthMonitor: ...

    async def start_comprehensive_monitoring(
        self,
        registry_config: dict[str, ContextValue],
        monitoring_config: dict[str, ContextValue] | None,
    ) -> bool: ...

    async def stop_all_monitoring(self) -> bool: ...

    async def collect_system_metrics(
        self, time_range_minutes: int
    ) -> dict[str, ContextValue]: ...

    async def generate_alerts(
        self, alert_config: dict[str, ContextValue] | None = None
    ) -> list[dict[str, ContextValue]]: ...

    async def monitor_subsystem_performance(
        self,
        subsystem_id: str,
        interval_seconds: int,
        callback: "Callable[[JsonType], JsonType] | None",
    ) -> bool: ...

    async def analyze_performance_trends(
        self, subsystem_id: str | None, time_range_hours: int, metrics: list[str] | None
    ) -> dict[str, ContextValue]: ...

    async def generate_health_report(
        self, time_range_hours: int, include_recommendations: bool
    ) -> dict[str, ContextValue]: ...

    async def configure_alerting(
        self,
        alert_handlers: "list[Callable[[JsonType], JsonType]]",
        thresholds: dict[str, ContextValue],
        escalation_rules: dict[str, ContextValue] | None,
    ) -> bool: ...

    async def get_monitoring_status(self) -> dict[str, ContextValue]: ...

    async def generate_dashboard_data(
        self, dashboard_config: dict[str, ContextValue] | None = None
    ) -> dict[str, ContextValue]: ...

    async def export_monitoring_data(
        self, format_type: str, time_range_hours: int, include_raw_data: bool
    ) -> dict[str, ContextValue]: ...
