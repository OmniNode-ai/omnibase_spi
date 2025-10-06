"""
CLI Tool Discovery Protocol for ONEX CLI Interface

Defines the protocol interface for CLI tool discovery and resolution,
providing duck-typed tool execution without hardcoded import paths.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable
from uuid import UUID

if TYPE_CHECKING:
    from omnibase_spi.protocols.types import ContextValue


@runtime_checkable
class ProtocolCliDiscoveredTool(Protocol):
    """Protocol for discovered CLI tool information."""

    name: str
    description: str | None
    version: str | None
    category: str | None
    health_status: str
    capabilities: list[str]


@runtime_checkable
class ProtocolCLIToolDiscovery(Protocol):
    """Protocol for CLI tool discovery operations."""

    async def discover_cli_tools(
        self, search_path: str
    ) -> list["ProtocolCliDiscoveredTool"]:
        """
        Discover CLI tools in the specified search path.

        Args:
            search_path: Path to search for CLI tools

        Returns:
            List of discovered tools with metadata
        """
        ...

    async def validate_tool_health(self, tool_name: str, tool_path: str) -> bool:
        """
        Validate the health and availability of a CLI tool.

        Args:
            tool_name: Name of the tool to validate
            tool_path: Path to the tool executable

        Returns:
            True if tool is healthy and available, False otherwise
        """
        ...

    async def get_tool_metadata(self, tool_name: str, tool_path: str) -> dict[str, str]:
        """
        Get metadata information for a CLI tool.

        Args:
            tool_name: Name of the tool
            tool_path: Path to the tool executable

        Returns:
            Dictionary containing tool metadata
        """
        ...

    async def register_tool(self, tool_data: "ProtocolCliDiscoveredTool") -> str:
        """
        Register a discovered tool for tracking and management.

        Args:
            tool_data: Tool data to register

        Returns:
            Registration ID for the tool
        """
        ...
