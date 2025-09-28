from typing import TYPE_CHECKING, Callable, Optional, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types import ContextValue, ProtocolEvent
else:
    ContextValue = "ContextValue"
    ProtocolEvent = "ProtocolEvent"


@runtime_checkable
class ProtocolEventBusCredentials(Protocol):
    """
    Canonical credentials protocol for event bus authentication/authorization.
    Supports token, username/password, and TLS certs for future event bus support.
    """

    token: str | None
    username: str | None
    password: str | None
    cert: str | None
    key: str | None
    ca: str | None
    extra: dict[str, "ContextValue"] | None

    async def validate_credentials(self) -> bool: ...

    def is_secure(self) -> bool: ...


@runtime_checkable
class ProtocolEventPubSub(Protocol):
    """
    Canonical protocol for simple event pub/sub operations.
    Defines basic publish/subscribe interface for event emission and handling.
    Provides a simpler alternative to the full distributed ProtocolEventBus.
    Supports both synchronous and asynchronous methods for maximum flexibility.
    Implementations may provide either or both, as appropriate.
    Optionally supports clear() for test/lifecycle management.
    All event bus implementations must expose a unique, stable bus_id (str) for diagnostics, registry, and introspection.
    """

    @property
    def credentials(self) -> ProtocolEventBusCredentials | None: ...

    async def publish(self, event: "ProtocolEvent") -> None: ...

    async def publish_async(self, event: "ProtocolEvent") -> None: ...

    async def subscribe(self, callback: Callable[[ProtocolEvent], None]) -> None: ...

    async def subscribe_async(
        self, callback: Callable[[ProtocolEvent], None]
    ) -> None: ...

    async def unsubscribe(self, callback: Callable[[ProtocolEvent], None]) -> None: ...

    async def unsubscribe_async(
        self, callback: Callable[[ProtocolEvent], None]
    ) -> None: ...

    def clear(self) -> None: ...

    @property
    def bus_id(self) -> str: ...
