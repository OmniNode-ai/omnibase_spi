"""Handler registry protocol for protocol handler management."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.handlers.protocol_handler import ProtocolHandler

__all__ = ["ProtocolHandlerRegistry"]


@runtime_checkable
class ProtocolHandlerRegistry(Protocol):
    """
    Protocol for registering and resolving ProtocolHandler implementations.

    Implements ProtocolRegistryBase[str, type[ProtocolHandler]] interface to provide
    specialized handler registration with protocol type keys (http_rest, bolt, postgres, kafka).

    Type Parameters (conceptual):
        K = str: Protocol type identifier (e.g., 'http_rest', 'bolt')
        V = type[ProtocolHandler]: Handler class implementing ProtocolHandler

    Thread Safety:
        Implementations MUST be thread-safe for concurrent read/write operations.

    See Also:
        - ProtocolRegistryBase: Generic base protocol for key-value registries
        - ProtocolHandler: Base protocol for handler implementations
    """

    def register(
        self,
        key: str,
        value: type[ProtocolHandler],
    ) -> None:
        """
        Register a protocol handler.

        Args:
            key: Protocol type identifier (e.g., 'http_rest', 'bolt').
            value: Handler class implementing ProtocolHandler.

        Raises:
            RegistryError: If registration fails.
            ValueError: If duplicate key and implementation forbids overwrites.
        """
        ...

    def get(
        self,
        key: str,
    ) -> type[ProtocolHandler]:
        """
        Get handler class for protocol type.

        Args:
            key: Protocol type identifier.

        Returns:
            Handler class for the protocol type.

        Raises:
            KeyError: If protocol type not registered.
            RegistryError: If retrieval fails due to internal error.
        """
        ...

    def list_keys(self) -> list[str]:
        """
        List registered protocol types.

        Returns:
            List of registered protocol type identifiers.
            Order is implementation-specific.

        Thread Safety:
            Must return a consistent snapshot.
        """
        ...

    def is_registered(self, key: str) -> bool:
        """
        Check if protocol type is registered.

        Args:
            key: Protocol type identifier.

        Returns:
            True if protocol type is registered, False otherwise.

        Thread Safety:
            Result is a point-in-time snapshot.
        """
        ...

    def unregister(self, key: str) -> bool:
        """
        Remove a protocol handler from the registry.

        Idempotent operation - safe to call multiple times with same key.

        Args:
            key: Protocol type identifier to remove.

        Returns:
            True if key was registered and removed.
            False if key was not registered (no-op).

        Thread Safety:
            Must be safe to call concurrently with other registry methods.
        """
        ...
