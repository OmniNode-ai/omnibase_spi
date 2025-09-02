#!/usr/bin/env python3
"""
MCP Monitor Protocol - ONEX SPI Interface.

Protocol definition for MCP monitoring and health management.
Provides comprehensive monitoring, alerting, and health management for MCP systems.

Domain: MCP monitoring, health checks, and observability
"""

from typing import Any, Callable, Optional, Protocol, runtime_checkable

from omnibase.protocols.types.core_types import (
    ContextValue,
    HealthStatus,
    ProtocolDateTime,
)
from omnibase.protocols.types.mcp_types import (
    ProtocolMCPHealthCheck,
    ProtocolMCPRegistryMetrics,
    ProtocolMCPSubsystemRegistration,
    ProtocolMCPToolExecution,
)


@runtime_checkable
class ProtocolMCPHealthMonitor(Protocol):
    """
    Protocol for MCP health monitoring operations.

    Handles health checks, status monitoring, and failure detection
    for MCP subsystems and registry components.
    """

    async def perform_health_check(
        self,
        subsystem: ProtocolMCPSubsystemRegistration,
        check_tools: bool = False,
    ) -> ProtocolMCPHealthCheck:
        """
        Perform comprehensive health check on a subsystem.

        Args:
            subsystem: Subsystem to check
            check_tools: Whether to test individual tools

        Returns:
            Health check result
        """
        ...

    async def monitor_subsystem_health(
        self,
        subsystem_id: str,
        interval_seconds: int = 30,
        callback: Optional[Callable[[Any], Any]] = None,
    ) -> bool:
        """
        Start continuous health monitoring for a subsystem.

        Args:
            subsystem_id: Subsystem to monitor
            interval_seconds: Check interval
            callback: Optional callback for status changes

        Returns:
            True if monitoring started successfully
        """
        ...

    async def stop_health_monitoring(self, subsystem_id: str) -> bool:
        """
        Stop health monitoring for a subsystem.

        Args:
            subsystem_id: Subsystem to stop monitoring

        Returns:
            True if monitoring stopped successfully
        """
        ...

    async def get_health_status(
        self, subsystem_id: str
    ) -> Optional[ProtocolMCPHealthCheck]:
        """
        Get latest health status for a subsystem.

        Args:
            subsystem_id: Subsystem ID

        Returns:
            Latest health check result or None if not found
        """
        ...

    async def get_health_history(
        self,
        subsystem_id: str,
        hours: int = 24,
        limit: int = 100,
    ) -> list[ProtocolMCPHealthCheck]:
        """
        Get health check history for a subsystem.

        Args:
            subsystem_id: Subsystem ID
            hours: Time range in hours
            limit: Maximum results

        Returns:
            List of historical health checks
        """
        ...

    async def detect_health_anomalies(
        self,
        subsystem_id: Optional[str] = None,
        time_window_hours: int = 1,
    ) -> list[dict[str, Any]]:
        """
        Detect health anomalies and patterns.

        Args:
            subsystem_id: Optional filter by subsystem
            time_window_hours: Analysis time window

        Returns:
            List of detected anomalies
        """
        ...


@runtime_checkable
class ProtocolMCPMonitor(Protocol):
    """
    Comprehensive MCP monitoring protocol for system observability.

    Provides complete monitoring capabilities including health monitoring,
    performance tracking, alerting, and operational dashboards.

    Usage Example:
        ```python
        # Monitor implementation (not part of SPI)
        class MCPMonitorImpl:
            def __init__(self):
                self.health_monitor = MCPHealthMonitorImpl()
                self.metrics_collectors: dict[str, Any] = {}
                self.alert_handlers: list[Callable] = []
                self.monitoring_tasks: dict[str, asyncio.Task] = {}

            async def start_comprehensive_monitoring(
                self,
                registry_config: dict[str, Any],
                monitoring_config: dict[str, Any] = None
            ) -> bool:
                config = monitoring_config or {
                    "health_check_interval": 30,
                    "metrics_collection_interval": 60,
                    "alert_thresholds": {
                        "error_rate": 0.05,
                        "response_time_p95": 5000,
                        "cpu_usage": 0.8,
                        "memory_usage": 0.85
                    }
                }

                # Start health monitoring
                await self._start_health_monitoring(config)

                # Start metrics collection
                await self._start_metrics_collection(config)

                # Start alert monitoring
                await self._start_alert_monitoring(config)

                return True

            async def _start_health_monitoring(self, config: dict[str, Any]):
                async def health_monitoring_loop():
                    while True:
                        try:
                            # Get all registered subsystems
                            subsystems = await self.registry.get_all_subsystems()

                            # Perform health checks
                            for subsystem in subsystems:
                                health = await self.health_monitor.perform_health_check(
                                    subsystem, check_tools=True
                                )

                                # Store health data
                                await self._store_health_data(health)

                                # Check for alerts
                                await self._check_health_alerts(health)

                            await asyncio.sleep(config["health_check_interval"])

                        except Exception as e:
                            print(f"Health monitoring error: {e}")
                            await asyncio.sleep(config["health_check_interval"] * 2)

                task = asyncio.create_task(health_monitoring_loop())
                self.monitoring_tasks["health"] = task

            async def collect_system_metrics(
                self,
                time_range_minutes: int = 60
            ) -> dict[str, Any]:
                metrics = {
                    "timestamp": datetime.now().isoformat(),
                    "time_range_minutes": time_range_minutes,
                    "registry_metrics": {},
                    "subsystem_metrics": {},
                    "tool_metrics": {},
                    "performance_metrics": {}
                }

                # Collect registry metrics
                registry_metrics = await self.registry.get_registry_metrics()
                metrics["registry_metrics"] = {
                    "total_subsystems": registry_metrics.total_subsystems,
                    "active_subsystems": registry_metrics.active_subsystems,
                    "total_tools": registry_metrics.total_tools,
                    "total_executions": registry_metrics.total_executions,
                    "success_rate": (
                        registry_metrics.successful_executions /
                        max(registry_metrics.total_executions, 1)
                    ),
                    "average_execution_time": registry_metrics.average_execution_time_ms
                }

                # Collect subsystem metrics
                subsystems = await self.registry.get_all_subsystems()
                for subsystem in subsystems:
                    sub_id = subsystem.subsystem_metadata.subsystem_id

                    # Get recent executions
                    executions = await self.registry.get_tool_executions(
                        subsystem_id=sub_id,
                        limit=1000
                    )

                    recent_executions = [
                        e for e in executions
                        if (datetime.now() - e.started_at).total_seconds() < time_range_minutes * 60
                    ]

                    metrics["subsystem_metrics"][sub_id] = {
                        "total_executions": len(recent_executions),
                        "successful_executions": len([
                            e for e in recent_executions
                            if e.execution_status == "completed"
                        ]),
                        "failed_executions": len([
                            e for e in recent_executions
                            if e.execution_status == "failed"
                        ]),
                        "average_duration": sum(
                            e.duration_ms or 0 for e in recent_executions
                        ) / max(len(recent_executions), 1),
                        "health_status": subsystem.health_status,
                        "last_heartbeat": subsystem.last_heartbeat.isoformat() if subsystem.last_heartbeat else None
                    }

                return metrics

            async def generate_alerts(
                self,
                alert_config: dict[str, Any] = None
            ) -> list[dict[str, Any]]:
                config = alert_config or {
                    "error_rate_threshold": 0.05,
                    "response_time_threshold": 5000,
                    "health_check_failure_threshold": 3
                }

                alerts = []

                # Check error rates
                metrics = await self.collect_system_metrics()

                for sub_id, sub_metrics in metrics["subsystem_metrics"].items():
                    total_exec = sub_metrics["total_executions"]
                    failed_exec = sub_metrics["failed_executions"]

                    if total_exec > 0:
                        error_rate = failed_exec / total_exec
                        if error_rate > config["error_rate_threshold"]:
                            alerts.append({
                                "type": "high_error_rate",
                                "subsystem_id": sub_id,
                                "severity": "warning" if error_rate < 0.1 else "critical",
                                "message": f"High error rate: {error_rate:.2%}",
                                "metric_value": error_rate,
                                "threshold": config["error_rate_threshold"],
                                "timestamp": datetime.now().isoformat()
                            })

                    # Check response times
                    avg_duration = sub_metrics["average_duration"]
                    if avg_duration > config["response_time_threshold"]:
                        alerts.append({
                            "type": "slow_response",
                            "subsystem_id": sub_id,
                            "severity": "warning",
                            "message": f"Slow response time: {avg_duration:.0f}ms",
                            "metric_value": avg_duration,
                            "threshold": config["response_time_threshold"],
                            "timestamp": datetime.now().isoformat()
                        })

                return alerts

        # Usage in MCP system
        monitor: ProtocolMCPMonitor = MCPMonitorImpl()

        # Start comprehensive monitoring
        await monitor.start_comprehensive_monitoring({
            "registry_url": "http://omnimcp:8100",
            "health_check_interval": 30,
            "metrics_interval": 60
        })

        # Collect system metrics
        metrics = await monitor.collect_system_metrics(time_range_minutes=60)
        print(f"System Health: {metrics['registry_metrics']['success_rate']:.2%} success rate")

        # Generate alerts
        alerts = await monitor.generate_alerts()
        if alerts:
            print(f"Active Alerts: {len(alerts)}")
            for alert in alerts:
                print(f"- {alert['type']}: {alert['message']}")

        # Monitor specific subsystem
        await monitor.monitor_subsystem_performance(
            subsystem_id="analytics-service",
            callback=lambda metrics: print(f"Analytics performance: {metrics}")
        )

        # Generate dashboard data
        dashboard = await monitor.generate_dashboard_data()
        print(f"Dashboard: {len(dashboard['widgets'])} widgets")
        ```

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
    def health_monitor(self) -> ProtocolMCPHealthMonitor:
        """Get the health monitor implementation."""
        ...

    async def start_comprehensive_monitoring(
        self,
        registry_config: dict[str, Any],
        monitoring_config: Optional[dict[str, Any]] = None,
    ) -> bool:
        """
        Start comprehensive monitoring of the MCP system.

        Args:
            registry_config: Registry connection configuration
            monitoring_config: Monitoring-specific configuration

        Returns:
            True if monitoring started successfully
        """
        ...

    async def stop_all_monitoring(self) -> bool:
        """
        Stop all monitoring activities.

        Returns:
            True if all monitoring stopped successfully
        """
        ...

    async def collect_system_metrics(
        self, time_range_minutes: int = 60
    ) -> dict[str, Any]:
        """
        Collect comprehensive system metrics.

        Args:
            time_range_minutes: Time range for metric collection

        Returns:
            System metrics including registry, subsystem, and tool metrics
        """
        ...

    async def generate_alerts(
        self, alert_config: Optional[dict[str, Any]] = None
    ) -> list[dict[str, Any]]:
        """
        Generate alerts based on current system status.

        Args:
            alert_config: Alert configuration and thresholds

        Returns:
            List of active alerts
        """
        ...

    async def monitor_subsystem_performance(
        self,
        subsystem_id: str,
        interval_seconds: int = 60,
        callback: Optional[Callable[[Any], Any]] = None,
    ) -> bool:
        """
        Monitor performance metrics for a specific subsystem.

        Args:
            subsystem_id: Subsystem to monitor
            interval_seconds: Monitoring interval
            callback: Optional callback for metric updates

        Returns:
            True if monitoring started successfully
        """
        ...

    async def analyze_performance_trends(
        self,
        subsystem_id: Optional[str] = None,
        time_range_hours: int = 24,
        metrics: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """
        Analyze performance trends and patterns.

        Args:
            subsystem_id: Optional filter by subsystem
            time_range_hours: Analysis time range
            metrics: Optional specific metrics to analyze

        Returns:
            Trend analysis results
        """
        ...

    async def generate_health_report(
        self,
        time_range_hours: int = 24,
        include_recommendations: bool = True,
    ) -> dict[str, Any]:
        """
        Generate comprehensive health report.

        Args:
            time_range_hours: Report time range
            include_recommendations: Whether to include improvement recommendations

        Returns:
            Health report with status, metrics, and recommendations
        """
        ...

    async def configure_alerting(
        self,
        alert_handlers: list[Callable[[Any], Any]],
        thresholds: dict[str, Any],
        escalation_rules: Optional[dict[str, Any]] = None,
    ) -> bool:
        """
        Configure alerting system.

        Args:
            alert_handlers: List of alert handler functions
            thresholds: Alert thresholds and conditions
            escalation_rules: Optional escalation configuration

        Returns:
            True if alerting configured successfully
        """
        ...

    async def get_monitoring_status(self) -> dict[str, Any]:
        """
        Get current monitoring system status.

        Returns:
            Monitoring status including active monitors and health
        """
        ...

    async def generate_dashboard_data(
        self, dashboard_config: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """
        Generate data for operational dashboard.

        Args:
            dashboard_config: Dashboard configuration

        Returns:
            Dashboard data including widgets and metrics
        """
        ...

    async def export_monitoring_data(
        self,
        format_type: str = "json",
        time_range_hours: int = 24,
        include_raw_data: bool = False,
    ) -> dict[str, Any]:
        """
        Export monitoring data for external analysis.

        Args:
            format_type: Export format (json, csv, prometheus)
            time_range_hours: Data time range
            include_raw_data: Whether to include raw metric data

        Returns:
            Exported monitoring data
        """
        ...
