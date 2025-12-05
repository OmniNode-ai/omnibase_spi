from typing import TYPE_CHECKING, Callable, Protocol, runtime_checkable

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
    """Authentication token for token-based auth."""
    username: str | None
    """Username for username/password auth."""
    password: str | None
    """Password for username/password auth."""
    cert: str | None
    """Client certificate path for TLS auth."""
    key: str | None
    """Client private key path for TLS auth."""
    ca: str | None
    """Certificate authority path for TLS verification."""
    extra: dict[str, "ContextValue"] | None
    """Additional provider-specific credential fields."""

    async def validate_credentials(self) -> bool:
        """Validate the credentials are properly configured.

        Returns:
            True if credentials are valid and can be used for authentication.

        Raises:
            ValueError: If credentials are malformed.
        """
        ...

    def is_secure(self) -> bool:
        """Check if the credentials use secure authentication.

        Returns:
            True if using TLS or other secure authentication method.
        """
        ...


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
    def credentials(self) -> ProtocolEventBusCredentials | None:
        """Get credentials for this event bus.

        Returns:
            Credentials if authentication is configured, None otherwise.
        """
        ...

    async def publish(self, event: "ProtocolEvent") -> None:
        """Publish an event to the bus synchronously.

        Args:
            event: The event to publish.

        Raises:
            ConnectionError: If the bus is not connected.
        """
        ...

    async def publish_async(self, event: "ProtocolEvent") -> None:
        """Publish an event to the bus asynchronously.

        Args:
            event: The event to publish.

        Raises:
            ConnectionError: If the bus is not connected.
        """
        ...

    async def subscribe(self, callback: Callable[[ProtocolEvent], None]) -> None:
        """Subscribe to events with a callback.

        Args:
            callback: Function to call when events are received.

        Raises:
            ConnectionError: If the bus is not connected.
        """
        ...

    async def subscribe_async(self, callback: Callable[[ProtocolEvent], None]) -> None:
        """Subscribe to events with an async callback.

        Args:
            callback: Function to call when events are received.

        Raises:
            ConnectionError: If the bus is not connected.
        """
        ...

    async def unsubscribe(self, callback: Callable[[ProtocolEvent], None]) -> None:
        """Unsubscribe a callback from events.

        Args:
            callback: The callback to unsubscribe.

        Raises:
            ValueError: If the callback was not subscribed.
        """
        ...

    async def unsubscribe_async(
        self, callback: Callable[[ProtocolEvent], None]
    ) -> None:
        """Unsubscribe an async callback from events.

        Args:
            callback: The callback to unsubscribe.

        Raises:
            ValueError: If the callback was not subscribed.
        """
        ...

    def clear(self) -> None:
        """Clear all subscriptions.

        Useful for test cleanup and lifecycle management.
        """
        ...

    @property
    def bus_id(self) -> str:
        """Get the unique bus identifier.

        Returns:
            Unique, stable identifier for diagnostics and registry.
        """
        ...
