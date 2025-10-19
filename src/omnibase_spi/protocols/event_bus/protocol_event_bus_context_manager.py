"""
Protocol for Event Bus Context Managers.

Provides async context management protocols for event bus lifecycle management.
Abstracts lifecycle management for event bus resources (e.g., Kafka, RedPanda).
"""

from typing import TYPE_CHECKING, Protocol, TypeVar, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.event_bus.protocol_event_bus import ProtocolEventBus

TEventBus = TypeVar("TEventBus", bound="ProtocolEventBus", covariant=True)


@runtime_checkable
class ProtocolEventBusContextManager(Protocol):
    """
    Protocol for async context managers that yield a ProtocolEventBus-compatible object.

    Provides lifecycle management for event bus resources with proper cleanup.
    Implementations must support async context management and return a ProtocolEventBus on enter.

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
            # event_bus is guaranteed to implement ProtocolEventBus
            await event_bus.publish(topic="test", key=None, value=b"data", headers={...})

            # Context manager handles connection lifecycle automatically
            # - Establishes connection on enter
            # - Performs cleanup on exit (even if exception occurs)
        ```
    """

    async def __aenter__(self) -> "ProtocolEventBus": ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None: ...
