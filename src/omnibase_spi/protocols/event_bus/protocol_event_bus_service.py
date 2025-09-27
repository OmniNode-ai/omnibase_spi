"""
Protocol for Event Bus Service

Defines the required interface that all event bus service implementations must follow.
This ensures consistency and prevents runtime errors from missing methods.
"""

from typing import TYPE_CHECKING, Awaitable, Callable, Protocol, runtime_checkable

# Runtime imports needed for forward references in method signatures
from omnibase_spi.protocols.event_bus.protocol_event_bus import ProtocolEventBus
from omnibase_spi.protocols.types.protocol_event_bus_types import ProtocolEventMessage

if TYPE_CHECKING:
    # No types needed here currently
    pass


@runtime_checkable
class ProtocolEventBusService(Protocol):
    """
    Protocol defining the required interface for event bus service implementations.

    All event bus service classes must implement these methods to ensure:
    - Consistent lifecycle management
    - Proper shutdown handling
    - Standard event bus access
    - Service status monitoring

    This protocol prevents runtime errors like missing shutdown() methods.
    """

    async def get_event_bus(self) -> "ProtocolEventBus":
        """
        Get the event bus instance managed by this service.

        Returns:
            Event bus instance for publishing/subscribing to events

        Raises:
            RuntimeError: If service is not running or event bus unavailable
        """
        ...

    def shutdown(self) -> None:
        """
        Gracefully shutdown the event bus service.

        This method must:
        - Clean up all connections
        - Stop any running threads
        - Release resources
            ...
        - Handle shutdown errors gracefully
        """
        ...

    @property
    def is_running(self) -> bool:
        """
        Check if the event bus service is currently running.

        Returns:
            True if service is active, False otherwise
        """
        ...

    async def get_node_count(self) -> int:
        """
        Get the number of nodes connected to this event bus service.

        Returns:
            Count of connected nodes
                ...
        """
        ...

    async def list_nodes(self) -> list[str]:
        """
        List the names of all nodes connected to this event bus service.

        Returns:
            ...
        """
        ...


@runtime_checkable
class ProtocolHttpEventBusAdapter(Protocol):
    """
    Protocol for event bus adapters that wrap HTTP/network event bus services.

    This is for lightweight adapters that connect to external event bus services.
    """

    async def publish(self, event: "ProtocolEventMessage") -> bool:
        """
        Publish an event to the event bus.

        Args:
            ...
        Returns:
            True if successful, False otherwise
        """
        ...

    async def subscribe(
        self, handler: Callable[["ProtocolEventMessage"], Awaitable[bool]]
    ) -> bool:
        """
        Subscribe to events with a handler function.

        Args:
            handler: Async function to handle received events
                ...
        Returns:
            True if subscription successful, False otherwise
        """
        ...

    async def unsubscribe(
        self, handler: Callable[["ProtocolEventMessage"], Awaitable[bool]]
    ) -> bool:
        """
        Unsubscribe a handler from events.

        Args:
            handler: Async handler function to remove
                ...
        Returns:
            True if unsubscription successful, False otherwise
        """
        ...

    @property
    def is_healthy(self) -> bool:
        """
        Check if the adapter connection is healthy.

        Returns:
            True if connection is working, False otherwise
                ...
        """
        ...

    async def close(self) -> None:
        """
        Close the adapter connection and clean up resources.

        Performs async cleanup of network connections and other I/O resources.
        """
        ...


EventBusServiceType = ProtocolEventBusService
EventBusAdapterType = ProtocolHttpEventBusAdapter
