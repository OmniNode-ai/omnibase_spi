"""
Protocol for In-Memory Event Bus Implementation.

Defines the interface for in-memory event bus implementations with
additional introspection and debugging capabilities.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_event_bus_types import ProtocolEventMessage

if TYPE_CHECKING:
    pass


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
    # Protocol usage example (SPI-compliant)
    in_memory_bus: "ProtocolEventBusInMemory" = get_in_memory_event_bus()

    # Check event processing history for debugging
    history = await in_memory_bus.get_event_history()
    print(f"Processed {len(history)} events")

    # Monitor active subscribers for system health
    subscriber_count = await in_memory_bus.get_subscriber_count()
    print(f"Active subscribers: {subscriber_count}")

    # Clear history for testing scenarios
    in_memory_bus.clear_event_history()

    # All methods operate on protocol interface without implementation details
    # Perfect for testing, debugging, and development environments
    ```
    """

    async def get_event_history(self) -> list[ProtocolEventMessage]: ...

    def clear_event_history(self) -> None: ...

    async def get_subscriber_count(self) -> int: ...
