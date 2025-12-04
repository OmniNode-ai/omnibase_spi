"""
CLI Tool Discovery Protocol for ONEX CLI Interface

Defines the protocol interface for CLI tool discovery and resolution,
providing duck-typed tool execution without hardcoded import paths.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class ProtocolCliDiscoveredTool(Protocol):
    """
    Protocol for discovered CLI tool metadata representation.

    Captures comprehensive information about a discovered CLI tool
    including identification, versioning, health status, and capability
    declarations for dynamic tool resolution and management.

    Attributes:
        name: Unique name identifier for the tool
        description: Human-readable description of tool purpose
        version: Semantic version of the tool
        category: Classification category (validator, generator, etc.)
        health_status: Current health status (healthy, degraded, unhealthy)
        capabilities: List of capability tags the tool provides

    Example:
        ```python
        discovery: ProtocolCLIToolDiscovery = get_tool_discovery()
        tools = await discovery.discover_cli_tools("/path/to/tools")

        for tool in tools:
            status_icon = "OK" if tool.health_status == "healthy" else "!!"
            print(f"[{status_icon}] {tool.name} v{tool.version}")
            print(f"    Category: {tool.category}")
            print(f"    Capabilities: {', '.join(tool.capabilities)}")
        ```

    See Also:
        - ProtocolCLIToolDiscovery: Tool discovery interface
        - ProtocolCLI: Discovered tool execution interface
    """

    name: str
    description: str | None
    version: str | None
    category: str | None
    health_status: str
    capabilities: list[str]


@runtime_checkable
class ProtocolCLIToolDiscovery(Protocol):
    """
    Protocol for CLI tool discovery and registration operations.

    Provides the interface for discovering CLI tools within specified
    search paths, validating tool health, extracting metadata, and
    registering tools for managed access without hardcoded imports.

    Example:
        ```python
        discovery: ProtocolCLIToolDiscovery = get_tool_discovery()

        # Discover all CLI tools in a directory
        tools = await discovery.discover_cli_tools("/opt/onex/tools")
        print(f"Found {len(tools)} CLI tools")

        # Validate and register each tool
        for tool in tools:
            is_healthy = await discovery.validate_tool_health(
                tool.name, f"/opt/onex/tools/{tool.name}"
            )
            if is_healthy:
                registration_id = await discovery.register_tool(tool)
                print(f"Registered {tool.name}: {registration_id}")

        # Get detailed metadata for specific tool
        metadata = await discovery.get_tool_metadata("validator", "/opt/onex/tools/validator")
        print(f"Validator metadata: {metadata}")
        ```

    See Also:
        - ProtocolCliDiscoveredTool: Discovered tool representation
        - ProtocolCLI: Tool execution interface
        - ProtocolCliWorkflow: Workflow-based tool execution
    """

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
