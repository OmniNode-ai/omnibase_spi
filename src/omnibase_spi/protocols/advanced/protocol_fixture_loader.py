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

    async def discover_fixtures(self) -> list[str]:
        """Discover all available fixture names.

        Scans configured fixture directories (central and node-local) to
        find all available test fixtures.

        Returns:
            List of fixture names that can be loaded via load_fixture().
        """
        ...

    async def load_fixture(self, name: str) -> ProtocolFixtureData:
        """Load and return the fixture by name.

        Args:
            name: The name of the fixture to load (as returned by
                discover_fixtures).

        Returns:
            Parsed fixture data containing test inputs, expected outputs,
            and any associated metadata for the named fixture.

        Raises:
            FileNotFoundError: If the fixture is not found.
            ValueError: If the fixture cannot be parsed or is malformed.
        """
        ...
