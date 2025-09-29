"""
Protocol for Event Bus Service

Defines the required interface that all event bus service implementations must follow.
This ensures consistency and prevents runtime errors from missing methods.
"""

from typing import TYPE_CHECKING, Awaitable, Callable, Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_event_bus_types import ProtocolEventMessage

if TYPE_CHECKING:
    from omnibase_spi.protocols.event_bus.protocol_event_bus import ProtocolEventBus


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

    async def get_event_bus(self) -> "ProtocolEventBus": ...

    def shutdown(self) -> None: ...

    @property
    def is_running(self) -> bool: ...

    async def get_node_count(self) -> int: ...

    async def list_nodes(self) -> list[str]: ...


@runtime_checkable
class ProtocolHttpEventBusAdapter(Protocol):
    """
    Protocol for event bus adapters that wrap HTTP/network event bus services.

    This is for lightweight adapters that connect to external event bus services.
    """

    async def publish(self, event: "ProtocolEventMessage") -> bool: ...

    async def subscribe(
        self, handler: Callable[["ProtocolEventMessage"], Awaitable[bool]]
    ) -> bool: ...

    async def unsubscribe(
        self, handler: Callable[["ProtocolEventMessage"], Awaitable[bool]]
    ) -> bool: ...

    @property
    def is_healthy(self) -> bool: ...

    async def close(self) -> None: ...
