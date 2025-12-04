"""Event Bus Provider Protocol for ONEX SPI.

Defines the provider/factory interface for obtaining event bus instances.
The actual ProtocolEventBus interface is defined in omnibase_core.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_core.protocols.event_bus import ProtocolEventBus


@runtime_checkable
class ProtocolEventBusProvider(Protocol):
    """Provider interface for obtaining event bus instances.

    Implements the factory pattern for event bus creation and lifecycle
    management. Allows dependency injection of different event bus
    implementations (in-memory, Kafka, Redpanda) based on configuration.

    This is the SPI factory protocol for event bus instances. It is distinct
    from omnibase_core's ProtocolEventBus which defines the event bus interface
    itself. This protocol defines the factory/provider pattern for managing
    event bus instances.

    Usage:
        ```python
        provider: ProtocolEventBusProvider = get_event_bus_provider()
        bus = await provider.get_event_bus()

        # Use bus...

        await provider.close_all()
        ```

    Implementations:
        - InMemoryEventBusProvider: Local development and testing
        - KafkaEventBusProvider: Production Kafka/Redpanda clusters
    """

    async def get_event_bus(
        self,
        environment: str | None = None,
        group: str | None = None,
    ) -> "ProtocolEventBus":
        """Get or create an event bus instance.

        May return a cached instance if one exists for the given
        environment/group combination.

        Args:
            environment: Environment identifier (e.g., "local", "dev", "prod").
                        If None, uses provider default.
            group: Consumer group identifier.
                   If None, uses provider default.

        Returns:
            Event bus instance implementing ProtocolEventBus.
        """
        ...

    async def create_event_bus(
        self,
        environment: str,
        group: str,
        config: dict[str, object] | None = None,
    ) -> "ProtocolEventBus":
        """Create a new event bus instance (no caching).

        Always creates a new instance, useful when you need
        isolated event buses for testing.

        Args:
            environment: Environment identifier.
            group: Consumer group identifier.
            config: Optional configuration overrides.

        Returns:
            New event bus instance.
        """
        ...

    async def close_all(self) -> None:
        """Close all managed event bus instances.

        Gracefully shuts down all event buses created by this provider.
        Should be called during application shutdown.
        """
        ...

    @property
    def default_environment(self) -> str:
        """Get the default environment."""
        ...

    @property
    def default_group(self) -> str:
        """Get the default consumer group."""
        ...


__all__ = ["ProtocolEventBusProvider"]
