"""Handler registry protocol for protocol handler management."""
from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, Type, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.handlers.protocol_handler import ProtocolHandler


@runtime_checkable
class ProtocolHandlerRegistry(Protocol):
    """
    Protocol for registering and resolving ProtocolHandler implementations.

    Manages the mapping between protocol types (http_rest, bolt, postgres, kafka)
    and their handler implementations for dependency injection.
    """

    def register(
        self,
        protocol_type: str,
        handler_cls: Type["ProtocolHandler"],
    ) -> None:
        """
        Register a protocol handler.

        Args:
            protocol_type: Protocol type identifier (e.g., 'http_rest', 'bolt').
            handler_cls: Handler class implementing ProtocolHandler.

        Raises:
            RegistryError: If registration fails.
        """
        ...

    def get(
        self,
        protocol_type: str,
    ) -> Type["ProtocolHandler"]:
        """
        Get handler class for protocol type.

        Args:
            protocol_type: Protocol type identifier.

        Returns:
            Handler class for the protocol type.

        Raises:
            RegistryError: If protocol type not registered.
        """
        ...

    def list_protocols(self) -> list[str]:
        """
        List registered protocol types.

        Returns:
            List of registered protocol type identifiers.
        """
        ...

    def is_registered(self, protocol_type: str) -> bool:
        """
        Check if protocol type is registered.

        Args:
            protocol_type: Protocol type identifier.

        Returns:
            True if protocol type is registered.
        """
        ...
