"""
Protocol for In-Memory Event Bus Implementation.

Defines the interface for in-memory event bus implementations with
additional introspection and debugging capabilities.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_event_bus_types import (
        ProtocolEventMessage,
    )


@runtime_checkable
class ProtocolEventBusInMemory(Protocol):
    """
    Protocol for in-memory event bus implementations.

    Extends basic event bus functionality with in-memory specific
    features for testing, debugging, and development environments.

    Key Features:
        - Event history tracking for debugging
        - Subscriber count monitoring
        - Memory-based event storage
        - Synchronous event processing
        - Development and testing support

    Usage Example:
        ```python
        # Implementation example (not part of SPI)
        class InMemoryEventBusImpl:
            def get_event_history(self) -> list:
                # Implementation returns copy of stored history
                return self._event_history.copy()

            def clear_event_history(self) -> None:
                # Implementation clears stored events
                self._event_history.clear()

            def get_subscriber_count(self) -> int:
                # Implementation returns active subscriber count
                return len(self._subscribers)

        # Usage in application code
        in_memory_bus: ProtocolEventBusInMemory = InMemoryEventBusImpl()

        # Check event processing history
        history = in_memory_bus.get_event_history()
        print(f"Processed {len(history)} events")

        # Monitor active subscribers
        subscriber_count = in_memory_bus.get_subscriber_count()
        print(f"Active subscribers: {subscriber_count}")

        # Clear history for testing
        in_memory_bus.clear_event_history()
        ```
    """

    def get_event_history(self) -> list["ProtocolEventMessage"]:
        """
        Get the history of events processed by this in-memory event bus.

        Returns:
            List of processed event messages in chronological order

        Note:
            History is maintained in-memory and may be limited by
            implementation-specific size constraints.
        """
        ...

    def clear_event_history(self) -> None:
        """
        Clear the event history.

        Removes all stored event history from memory. Useful for
        testing scenarios where clean state is required.
        """
        ...

    def get_subscriber_count(self) -> int:
        """
        Get the number of active subscribers.

        Returns:
            Current count of active event subscribers

        Note:
            Count includes all active subscriptions across all topics/patterns.
        """
        ...
