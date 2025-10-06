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
        # Protocol usage example (SPI-compliant)
        health_details: "ProtocolHealthDetails" = get_service_health_details()

        # Check service health status using protocol interface
        health_status = health_details.get_health_status()
        is_service_healthy = health_details.is_healthy()
        health_summary = health_details.get_health_summary()

        # All health assessment logic is encapsulated in the implementation
        # Protocol provides consistent interface across different service types
        ```

    Integration with Health Monitoring:
        ```python
        # Protocol integration example (SPI-compliant)
        async def create_health_check(details: "ProtocolHealthDetails") -> "ProtocolHealthCheck":
            # Protocol enables seamless integration with health monitoring
            # All health data accessed through protocol interface
            health_check = await build_health_check_from_details(details)
            return health_check
        ```
    """

    async def get_health_status(self) -> "LiteralHealthStatus": ...

    async def is_healthy(self) -> bool: ...

    async def get_health_summary(self) -> str: ...
