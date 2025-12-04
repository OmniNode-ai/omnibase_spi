"""Event Bus Provider Protocol for ONEX SPI.

This module defines the provider/factory interface for obtaining event bus instances.
The actual ProtocolEventBus interface is defined in omnibase_core, while this protocol
defines the factory pattern for creating and managing event bus instances.

The provider pattern enables dependency injection of different event bus implementations
(in-memory, Kafka, Redpanda) based on environment configuration, supporting both
development and production scenarios.

Example:
    ```python
    from omnibase_spi.protocols.event_bus import ProtocolEventBusProvider

    # Get provider from dependency injection
    provider: ProtocolEventBusProvider = get_event_bus_provider()

    # Get or create event bus for environment
    bus = await provider.get_event_bus(environment="prod", group="my-service")

    # Use bus for messaging
    await bus.publish(topic="events", key=None, value=b"data", headers={})

    # Cleanup on shutdown
    await provider.close_all()
    ```

See Also:
    - ProtocolEventBus: The event bus interface from omnibase_core.
    - ProtocolEventBusContextManager: Context manager for event bus lifecycle.
    - ProtocolEventBusService: Service layer for event bus operations.
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

        Raises:
            ConnectionError: If connection to the event bus backend fails.
            ConfigurationError: If event bus configuration is invalid.

        Example:
            ```python
            bus = await provider.get_event_bus(environment="prod", group="my-service")
            await bus.publish(topic="events", key=None, value=b"data", headers={})
            ```
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

        Raises:
            ConnectionError: If connection to the event bus backend fails.
            ConfigurationError: If configuration is invalid.
            ValueError: If environment or group is empty.

        Example:
            ```python
            # Create isolated bus for testing
            test_bus = await provider.create_event_bus(
                environment="test",
                group="test-consumer",
                config={"auto_offset_reset": "earliest"}
            )
            ```
        """
        ...

    async def close_all(self) -> None:
        """Close all managed event bus instances.

        Gracefully shuts down all event buses created by this provider.
        Should be called during application shutdown.

        Performs the following cleanup:
        - Flushes pending messages on all producers
        - Closes all consumer connections
        - Releases network resources
        - Clears internal instance cache

        Raises:
            TimeoutError: If shutdown does not complete within timeout.

        Example:
            ```python
            # During application shutdown
            await provider.close_all()
            ```
        """
        ...

    @property
    def default_environment(self) -> str:
        """Get the default environment.

        Returns:
            The default environment identifier (e.g., "local", "dev", "prod").

        Example:
            ```python
            env = provider.default_environment
            print(f"Default environment: {env}")
            ```
        """
        ...

    @property
    def default_group(self) -> str:
        """Get the default consumer group.

        Returns:
            The default consumer group identifier.

        Example:
            ```python
            group = provider.default_group
            print(f"Default consumer group: {group}")
            ```
        """
        ...


__all__ = ["ProtocolEventBusProvider"]
