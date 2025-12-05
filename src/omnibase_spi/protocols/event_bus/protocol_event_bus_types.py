from typing import TYPE_CHECKING, Awaitable, Callable, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types import ContextValue, ProtocolEvent


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
        """Publish an event to the bus.

        This is an async method that publishes an event and waits for
        confirmation that it was received by the bus infrastructure.

        Args:
            event: The event to publish.

        Returns:
            None when the event has been successfully published.

        Raises:
            ConnectionError: If the bus is not connected.
        """
        ...

    async def publish_async(self, event: "ProtocolEvent") -> None:
        """Publish an event to the bus with fire-and-forget semantics.

        This method queues the event for publication without waiting for
        confirmation. Use this for high-throughput scenarios where delivery
        guarantees are handled at a higher level.

        Args:
            event: The event to publish.

        Returns:
            None when the event has been queued for publication.

        Raises:
            ConnectionError: If the bus is not connected.
        """
        ...

    async def subscribe(self, callback: Callable[["ProtocolEvent"], None]) -> None:
        """Subscribe to events with a synchronous callback.

        The callback will be invoked synchronously when events are received.
        For async callbacks, use subscribe_async instead.

        Args:
            callback: Synchronous function to call when events are received.
                Must accept a ProtocolEvent and return None.

        Returns:
            None when the subscription is registered.

        Raises:
            ConnectionError: If the bus is not connected.
        """
        ...

    async def subscribe_async(
        self, callback: Callable[["ProtocolEvent"], Awaitable[None]]
    ) -> None:
        """Subscribe to events with an asynchronous callback.

        The callback will be awaited when events are received.
        For synchronous callbacks, use subscribe instead.

        Args:
            callback: Async function to call when events are received.
                Must accept a ProtocolEvent and return an Awaitable[None].

        Returns:
            None when the subscription is registered.

        Raises:
            ConnectionError: If the bus is not connected.
        """
        ...

    async def unsubscribe(self, callback: Callable[["ProtocolEvent"], None]) -> None:
        """Unsubscribe a synchronous callback from events.

        Args:
            callback: The synchronous callback to unsubscribe.

        Returns:
            None when the callback has been unsubscribed.

        Raises:
            ValueError: If the callback was not subscribed.
        """
        ...

    async def unsubscribe_async(
        self, callback: Callable[["ProtocolEvent"], Awaitable[None]]
    ) -> None:
        """Unsubscribe an asynchronous callback from events.

        Args:
            callback: The async callback to unsubscribe.

        Returns:
            None when the callback has been unsubscribed.

        Raises:
            ValueError: If the callback was not subscribed.
        """
        ...

    def clear(self) -> None:
        """Clear all subscriptions.

        Useful for test cleanup and lifecycle management.
        Removes both synchronous and asynchronous subscriptions.

        Returns:
            None when all subscriptions have been cleared.
        """
        ...

    @property
    def bus_id(self) -> str:
        """Get the unique bus identifier.

        Returns:
            Unique, stable identifier for diagnostics and registry.
        """
        ...
