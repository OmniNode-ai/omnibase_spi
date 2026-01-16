"""Protocol for fixture loading and discovery.

This module defines the minimal interface for fixture loaders that can
discover and load test fixtures from various sources (central, node-local).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_advanced_types import ProtocolFixtureData


@runtime_checkable
class ProtocolFixtureLoader(Protocol):
    """
    Protocol for fixture loading and discovery.

    This minimal interface supports fixture discovery and loading for both
    central and node-scoped fixture directories, enabling extensibility
    and plugin scenarios.
    """

    async def discover_fixtures(self) -> list[str]: ...
    async def load_fixture(self, name: str) -> ProtocolFixtureData:
        """
        Load and return the fixture by name.

        Args:
            name: The name of the fixture to load.

        Returns:
            ...
        Raises:
            FileNotFoundError: If the fixture is not found.
            Exception: If the fixture cannot be loaded or parsed.
        """
        ...
