from typing import Callable, Dict, Optional, Protocol, runtime_checkable

from omnibase.protocols.types import ProtocolEvent


class ProtocolEventBusCredentials(Protocol):
    """
    Canonical credentials protocol for event bus authentication/authorization.
    Supports token, username/password, and TLS certs for future event bus support.
    """

    token: Optional[str]
    username: Optional[str]
    password: Optional[str]
    cert: Optional[str]
    key: Optional[str]
    ca: Optional[str]
    extra: Optional[dict[str, str]]


@runtime_checkable
class ProtocolEventBus(Protocol):
    """
    Canonical protocol for ONEX event bus (runtime/ placement).
    Defines publish/subscribe interface for event emission and handling.
    All event bus implementations must conform to this interface.
    Supports both synchronous and asynchronous methods for maximum flexibility.
    Implementations may provide either or both, as appropriate.
    Optionally supports clear() for test/lifecycle management.
    All event bus implementations must expose a unique, stable bus_id (str) for diagnostics, registry, and introspection.
    """

    @property
    def credentials(self) -> Optional[ProtocolEventBusCredentials]:
        """Get event bus credentials."""
        ...

    def publish(self, event: ProtocolEvent) -> None: ...

    async def publish_async(self, event: ProtocolEvent) -> None: ...

    def subscribe(self, callback: Callable[[ProtocolEvent], None]) -> None: ...

    async def subscribe_async(
        self, callback: Callable[[ProtocolEvent], None]
    ) -> None: ...

    def unsubscribe(self, callback: Callable[[ProtocolEvent], None]) -> None: ...

    async def unsubscribe_async(
        self, callback: Callable[[ProtocolEvent], None]
    ) -> None: ...

    def clear(self) -> None: ...

    @property
    def bus_id(self) -> str:
        """
        Unique, stable identifier for this event bus instance (MUST be unique per bus, stable for its lifetime).
        """
        ...
