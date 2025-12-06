"""
Protocol for CLI Directory Fixture Registry functionality.

Defines the interface for managing and accessing CLI directory test fixtures.
"""

from collections.abc import Callable
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.cli.protocol_cli_dir_fixture_case import (
        ProtocolCLIDirFixtureCase,
    )


@runtime_checkable
class ProtocolCLIDirFixtureRegistry(Protocol):
    """Protocol for CLI directory fixture registry management.

    This protocol defines the interface for managing CLI directory test fixtures,
    providing access to test cases and filtering capabilities.
    """

    def all_cases(self) -> list["ProtocolCLIDirFixtureCase"]:
        """Get all available CLI directory fixture cases.

        Returns:
            List of all available fixture cases
        """
        ...

    async def get_case(self, case_id: str) -> "ProtocolCLIDirFixtureCase":
        """Get a specific CLI directory fixture case by ID.

        Args:
            case_id: Unique identifier for the fixture case

        Returns:
            The requested fixture case

        Raises:
            KeyError: If case_id is not found
        """
        ...

    def filter_cases(
        self,
        predicate: Callable[["ProtocolCLIDirFixtureCase"], bool],
    ) -> list["ProtocolCLIDirFixtureCase"]:
        """Filter CLI directory fixture cases using a predicate function.

        Args:
            predicate: Function that returns True for cases to include

        Returns:
            List of fixture cases that match the predicate
        """
        ...
