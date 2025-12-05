"""Protocol for Event Bus Context Managers.

This module provides async context management protocols for event bus lifecycle
management in the ONEX SPI layer. It abstracts lifecycle management for event
bus resources (e.g., Kafka, RedPanda), enabling clean resource acquisition and
release patterns.

The protocol ensures that implementations properly handle connection establishment,
resource cleanup, and error recovery for event bus instances.

Example:
    ```python
    from omnibase_spi.protocols.event_bus import ProtocolEventBusContextManager

    # Usage with async context manager pattern
    context_manager: ProtocolEventBusContextManager = get_event_bus_context_manager()

    async with context_manager as event_bus:
        # event_bus is guaranteed to implement ProtocolEventBus
        await event_bus.publish(topic="events", key=None, value=b"data", headers={})
        # Resources automatically cleaned up on exit
    ```

See Also:
    - ProtocolEventBusBase: The event bus interface returned by context managers.
    - ProtocolEventBusProvider: Factory for obtaining event bus instances.
"""

from typing import TYPE_CHECKING, Protocol, TypeVar, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.event_bus.protocol_event_bus_mixin import (
        ProtocolEventBusBase,
    )

TEventBus = TypeVar("TEventBus", bound="ProtocolEventBusBase", covariant=True)


@runtime_checkable
class ProtocolEventBusContextManager(Protocol):
    """
    Protocol for async context managers that yield a ProtocolEventBusBase-compatible object.

    Provides lifecycle management for event bus resources with proper cleanup.
    Implementations must support async context management and return a ProtocolEventBusBase on enter.

    Key Features:
        - Async context manager support (__aenter__, __aexit__)
        - Configuration-based initialization
        - Resource lifecycle management
        - Proper cleanup and error handling

    Usage Example:
        ```python
        # Protocol usage example (SPI-compliant)
        context_manager: "ProtocolEventBusContextManager" = get_event_bus_context_manager()

        # Usage with async context manager pattern
        async with context_manager as event_bus:
            # event_bus is guaranteed to implement ProtocolEventBusBase
            await event_bus.publish(event)

            # Context manager handles connection lifecycle automatically
            # - Establishes connection on enter
            # - Performs cleanup on exit (even if exception occurs)
        ```
    """

    async def __aenter__(self) -> "ProtocolEventBusBase":
        """Enter the async context and return an event bus instance.

        Establishes connection to the event bus backend (Kafka, RedPanda, etc.)
        and returns a ready-to-use event bus instance.

        Returns:
            A ProtocolEventBusBase instance ready for publishing and subscribing.

        Raises:
            ConnectionError: If connection to the event bus backend fails.
            ConfigurationError: If event bus configuration is invalid.
            TimeoutError: If connection establishment times out.

        Example:
            ```python
            async with context_manager as event_bus:
                # event_bus is now connected and ready
                await event_bus.publish(topic="events", key=None, value=b"data")
            ```
        """
        ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        """Exit the async context and cleanup resources.

        Performs graceful cleanup of event bus resources including:
        - Flushing any pending messages
        - Closing producer and consumer connections
        - Releasing network resources

        Args:
            exc_type: Exception type if an exception was raised, None otherwise.
            exc_val: Exception instance if an exception was raised, None otherwise.
            exc_tb: Exception traceback if an exception was raised, None otherwise.

        Returns:
            None. Exceptions are not suppressed.

        Example:
            ```python
            async with context_manager as event_bus:
                await event_bus.publish(...)
            # Resources are cleaned up here, even if an exception occurred
            ```
        """
        ...
