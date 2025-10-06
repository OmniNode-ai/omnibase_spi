"""
Protocol for testable ONEX registry interfaces.

Provides a clean interface for testable registry operations without exposing
implementation-specific details. This protocol enables testing and cross-component
registry testing while maintaining proper architectural boundaries.
"""

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_core_types import ContextValue


@runtime_checkable
class ProtocolTestableRegistry(Protocol):
    """
    Protocol for testable ONEX registries (mock/real).

    Used for registry-driven tests and swappable registry fixtures.
    Provides methods for loading registries from disk or creating mock instances.
    """

    @classmethod
    async def load_from_disk(cls) -> "ProtocolTestableRegistry":
        """
        Load a testable registry from disk configuration.

        Returns:
            A testable registry instance loaded from disk
        """
        ...

    @classmethod
    async def load_mock(cls) -> "ProtocolTestableRegistry":
        """
        Load a mock testable registry for testing purposes.

        Returns:
            A mock testable registry instance
        """
        ...

    async def get_node(self, node_id: str) -> dict[str, Any]:
        """
        Get a node from the testable registry.

        Args:
            node_id: The identifier of the node to retrieve

        Returns:
            A dictionary containing the node information
        """
        ...
