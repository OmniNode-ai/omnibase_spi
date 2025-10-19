"""
CLI Directory Fixture Case Protocol for ONEX CLI Interface

Defines the protocol interface for directory fixture case handling in CLI operations,
providing standardized structure for test fixture management.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types import ContextValue


@runtime_checkable
class ProtocolFileEntry(Protocol):
    """Protocol for file entries in directory fixtures."""

    relative_path: str
    content: str


@runtime_checkable
class ProtocolSubdirEntry(Protocol):
    """Protocol for subdirectory entries in directory fixtures."""

    subdir: str
    files: list["ProtocolFileEntry"]


@runtime_checkable
class ProtocolCLIDirFixtureCase(Protocol):
    """Protocol for CLI directory fixture case operations."""

    id: str
    files: list["ProtocolFileEntry"]
    subdirs: list["ProtocolSubdirEntry"] | None

    async def create_fixture(self, base_path: str) -> bool:
        """
        Create the directory fixture at the specified path.

        Args:
            base_path: Base path where fixture should be created

        Returns:
            True if fixture creation succeeded, False otherwise
        """
        ...

    async def validate_fixture(self, base_path: str) -> bool:
        """
        Validate that the directory fixture exists and is correct.

        Args:
            base_path: Base path to validate fixture against

        Returns:
            True if fixture is valid, False otherwise
        """
        ...

    async def cleanup_fixture(self, base_path: str) -> bool:
        """
        Clean up the directory fixture.

        Args:
            base_path: Base path where fixture should be cleaned up

        Returns:
            True if cleanup succeeded, False otherwise
        """
        ...
