"""
Protocol for Service-Specific Health Details.

Defines interface for service-specific health details that can assess
their own health status and provide summary information.
Complements existing health monitoring protocols with service-specific logic.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_core_types import LiteralHealthStatus


@runtime_checkable
class ProtocolHealthDetails(Protocol):
    """
    Protocol for service-specific health details with self-assessment capability.

    This protocol defines the interface for health detail models that can:
    - Assess their own health status based on service-specific metrics
    - Provide boolean health indicators
    - Generate human-readable health summaries

    Designed to work with the existing ProtocolHealthCheck and ProtocolHealthMonitor
    protocols, allowing service-specific models to contribute to overall health assessment.

    Key Features:
        - Service-specific health logic encapsulation
        - Consistent interface across all health detail models
        - Self-contained health assessment capability
        - Human-readable status reporting
        - Integration with existing health monitoring infrastructure

    Usage Example:
        ```python
        # Implementation example (not part of SPI)
        class ModelPostgresHealthDetails(BaseModel):
            postgres_connection_count: int | None
            postgres_last_error: str | None
            max_connections: int | None

            def get_health_status(self) -> LiteralHealthStatus:
                if self.postgres_last_error:
                    return "unhealthy"
                if self.postgres_connection_count and self.max_connections:
                    if self.postgres_connection_count > (self.max_connections * 0.9):
                        return "warning"
                return "healthy"

            def is_healthy(self) -> bool:
                return self.get_health_status() == "healthy"

            def get_health_summary(self) -> str:
                status = self.get_health_status()
                if status == "unhealthy":
                    return f"PostgreSQL Error: {self.postgres_last_error}"
                return "PostgreSQL connections healthy"
        ```

    Integration with Health Monitoring:
        ```python
        def create_health_check(details: ProtocolHealthDetails) -> ProtocolHealthCheck:
            return HealthCheckImpl(
                service_name=details.__class__.__name__,
                overall_status=details.get_health_status(),
                individual_checks={"service": details.get_health_status()},
                summary=details.get_health_summary()
            )
        ```
    """

    def get_health_status(self) -> "LiteralHealthStatus":
        """
        Assess and return the health status based on service-specific metrics.

        Returns:
            LiteralHealthStatus: Current health status of the service

        The implementation should analyze service-specific fields and return:
        - "healthy": Service is operating normally
        - "warning": Service has minor issues but is functional
        - "unhealthy": Service has significant issues
        - "critical": Service is non-functional
        - "unknown": Health status cannot be determined
        - "degraded": Service is functional but with reduced capabilities
        """
        ...

    def is_healthy(self) -> bool:
        """
        Return True if the service is considered healthy.

        Returns:
            bool: True if service is healthy, False otherwise

        This is a convenience method that typically returns True when
        get_health_status() returns "healthy".
        """
        ...

    def get_health_summary(self) -> str:
        """
        Generate a human-readable summary of the health status.

        Returns:
            str: Human-readable description of current health status

        Should provide actionable information about the service state,
        including any issues or warnings that operators should be aware of.
        Examples:
        - "PostgreSQL healthy - 45/100 connections"
        - "Kafka warning - high producer lag detected"
        - "Circuit breaker error - too many failures"
        """
        ...
