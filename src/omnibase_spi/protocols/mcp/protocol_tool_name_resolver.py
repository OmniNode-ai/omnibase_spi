"""
Protocol for dynamic tool name resolution.

Defines the interface for contract-based tool name discovery and resolution,
replacing the monolithic enum approach.
"""

from typing import Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_mcp_types import ProtocolModelToolInfo


@runtime_checkable
class ProtocolToolNameResolver(Protocol):
    """
    Protocol for tool name resolution from contracts.

    Implementations should provide dynamic tool discovery by reading
    contract.yaml files instead of relying on central enums.
    """

    async def get_tool_name(self, tool_path: str) -> str | None:
        """
        Get tool name from its path by reading contract.yaml.

        Args:
            tool_path: Path to the tool directory

        Returns:
            Tool name from contract, or None if not found
        """
        ...

    def discover_all_tools(
        self,
        force_refresh: bool | None = None,
    ) -> dict[str, ProtocolModelToolInfo]:
        """
        Discover all tools by scanning for contract.yaml files.

        Args:
            force_refresh: Force cache refresh even if not expired

        Returns:
            Dictionary mapping tool names to ModelToolInfo objects
        """
        ...

    def validate_tool_name_uniqueness(self) -> list[str]:
        """
        Validate that all tool names are unique across the codebase.

        Returns:
            List of validation errors (empty if all unique)
        """
        ...

    async def get_tool_path(self, tool_name: str) -> str | None:
        """
        Get the path to a tool by its name.

        Args:
            tool_name: Name of the tool to find

        Returns:
            Path string to the tool directory, or None if not found
        """
        ...

    async def get_all_tool_names(self) -> set[str]:
        """
        Get all available tool names.

        Returns:
            Set of all tool names discovered from contracts
        """
        ...

    def tool_exists(self, tool_name: str) -> bool:
        """
        Check if a tool exists.

        Args:
            tool_name: Name of the tool to check

        Returns:
            True if tool exists, False otherwise
        """
        ...

    def clear_cache(self) -> None:
        """Clear the tool discovery cache."""
        ...
