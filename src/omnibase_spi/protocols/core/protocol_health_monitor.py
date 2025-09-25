"""
Protocol for Standardized Health Monitoring.

Defines interfaces for health checks, monitoring, and service availability
across all ONEX services with consistent patterns and observability.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.core_types import (
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
        # Implementation example (not part of SPI)
        class HealthMonitorImpl:
            def perform_health_check(self, level, dimensions):
                checks = {}
                metrics = self._collect_metrics()

                for dimension in dimensions:
                    if dimension == "availability":
                        checks[dimension] = self._check_availability()
                    elif dimension == "performance":
                        checks[dimension] = self._check_performance(metrics)

                overall = self._aggregate_status(checks.values())
                return HealthCheck(overall_status=overall, individual_checks=checks)

        # Usage in application code
        health_monitor: ProtocolHealthMonitor = HealthMonitorImpl()

        health_status = health_monitor.perform_health_check(
            level="standard",
            dimensions=["availability", "performance"]
        )
        ```
    """

    def perform_health_check(
        self,
        level: "LiteralHealthCheckLevel",
        dimensions: list["LiteralHealthDimension"],
    ) -> "ProtocolHealthCheck":
        """
        Perform health check at specified level and dimensions.

        Args:
            level: Depth of health check (quick, basic, standard, thorough, comprehensive)
            dimensions: Aspects to check (availability, performance, functionality, etc.)

        Returns:
            Comprehensive health check results with metrics

        Note:
            Higher levels perform more thorough checks but take longer.
            Dimensions allow targeted health assessment for specific concerns.
        """
        ...

    def get_current_health_status(self) -> "LiteralHealthStatus":
        """
        Get current overall health status.

        Returns:
            Current health status without performing full check

        Note:
            Returns cached status from last health check for quick queries.
            Use perform_health_check() for up-to-date comprehensive status.
        """
        ...

    def get_health_metrics(self) -> "ProtocolHealthMetrics":
        """
        Get current health metrics.

        Returns:
            Current health metrics including performance indicators

        Note:
            Provides real-time metrics for monitoring dashboards
            and operational visibility into service health.
        """
        ...

    def configure_monitoring(
        self,
        config: "ProtocolHealthMonitoring",
    ) -> bool:
        """
        Configure health monitoring parameters.

        Args:
            config: Monitoring configuration with intervals and thresholds

        Returns:
            True if configuration was applied successfully

        Note:
            Configures automatic health check intervals, failure thresholds,
            and alerting rules for proactive monitoring.
        """
        ...

    def get_monitoring_configuration(self) -> "ProtocolHealthMonitoring":
        """
        Get current monitoring configuration.

        Returns:
            Current monitoring configuration settings

        Note:
            Returns active monitoring configuration including
            intervals, thresholds, and alerting rules.
        """
        ...

    def start_monitoring(self) -> bool:
        """
        Start automated health monitoring.

        Returns:
            True if monitoring was started successfully

        Note:
            Begins background health monitoring with configured intervals
            and automatic alerting based on configured thresholds.
        """
        ...

    def stop_monitoring(self) -> bool:
        """
        Stop automated health monitoring.

        Returns:
            True if monitoring was stopped successfully

        Note:
            Stops background monitoring but preserves configuration.
            Manual health checks can still be performed.
        """
        ...

    def is_monitoring_active(self) -> bool:
        """
        Check if automated monitoring is currently active.

        Returns:
            True if monitoring is running

        Note:
            Indicates whether background health monitoring is
            currently performing automated checks and alerting.
        """
        ...

    def get_health_history(
        self,
        hours_back: int,
    ) -> list["ProtocolHealthCheck"]:
        """
        Get historical health check results.

        Args:
            hours_back: Number of hours of history to retrieve

        Returns:
            Historical health check results ordered by timestamp

        Note:
            Provides health trends and patterns for operational
            analysis and capacity planning.
        """
        ...

    def register_health_dependency(
        self,
        dependency_name: str,
        dependency_monitor: "ProtocolHealthMonitor",
    ) -> bool:
        """
        Register dependency health monitor.

        Args:
            dependency_name: Name of the dependency service
            dependency_monitor: Health monitor for the dependency

        Returns:
            True if dependency was registered successfully

        Note:
            Enables composite health checks that consider dependency
            health in overall service health assessment.
        """
        ...

    def unregister_health_dependency(
        self,
        dependency_name: str,
    ) -> bool:
        """
        Unregister dependency health monitor.

        Args:
            dependency_name: Name of dependency to unregister

        Returns:
            True if dependency was unregistered successfully

        Note:
            Removes dependency from health assessment calculations.
        """
        ...

    def get_dependency_health_status(
        self,
        dependency_name: str,
    ) -> "LiteralHealthStatus":
        """
        Get health status of specific dependency.

        Args:
            dependency_name: Name of dependency to check

        Returns:
            Current health status of the dependency

        Raises:
            KeyError: If dependency is not registered

        Note:
            Provides visibility into dependency health for
            troubleshooting and impact analysis.
        """
        ...

    def set_health_alert_callback(
        self,
        callback: object,
    ) -> bool:
        """
        Set callback for health status changes.

        Args:
            callback: Function to call on health status changes

        Returns:
            True if callback was registered successfully

        Note:
            Enables integration with external alerting systems
            and custom notification mechanisms.
        """
        ...

    def get_aggregated_health_status(self) -> dict[str, "LiteralHealthStatus"]:
        """
        Get health status including all dependencies.

        Returns:
            Dictionary of service and dependency health statuses

        Note:
            Provides comprehensive view of service ecosystem health
            for operational dashboards and monitoring systems.
        """
        ...
