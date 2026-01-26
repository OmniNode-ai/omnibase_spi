"""
MCP Handler Protocol - ONEX SPI Interface.

Protocol definition for MCP tool listing and execution handling.
Provides the core interface for components that manage MCP tool
lifecycle operations including discovery, retrieval, and invocation.

Domain: MCP tool handling and execution
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable
from uuid import UUID

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_core_types import ContextValue

from omnibase_spi.protocols.types.protocol_mcp_tool_types import (
    LiteralMCPToolType,
    ProtocolMCPToolDefinition,
)


@runtime_checkable
class ProtocolMCPHandler(Protocol):
    """
    Protocol for MCP tool handling and execution.

    Defines the core interface for components that manage MCP tool operations
    including listing available tools, retrieving tool definitions, and
    executing tool calls. Implementations handle the bridge between MCP
    clients and tool registries/subsystems.

    Key Features:
        - **Tool Discovery**: List all available tools with filtering by type
        - **Tool Retrieval**: Get individual tool definitions by name
        - **Tool Execution**: Execute tool calls with parameter passing
        - **Type Filtering**: Filter tools by supported types
        - **Existence Checking**: Quick check for tool availability

    Attributes:
        supported_tool_types: List of MCP tool types this handler supports.
            Typically includes "function", "resource", "prompt", etc.

    Example:
        ```python
        from uuid import uuid4

        class AgentMCPHandler:
            '''MCP handler for agent tool integration.'''

            @property
            def supported_tool_types(self) -> list[LiteralMCPToolType]:
                return ["function", "resource"]

            async def handle_list_tools(self) -> list[ProtocolMCPToolDefinition]:
                # Return all registered tools
                return [
                    SearchToolDefinition(),
                    FileReaderToolDefinition(),
                    DatabaseQueryToolDefinition(),
                ]

            async def handle_get_tool(
                self, tool_name: str
            ) -> ProtocolMCPToolDefinition | None:
                tools = await self.handle_list_tools()
                for tool in tools:
                    if tool.name == tool_name:
                        return tool
                return None

            async def handle_tool_exists(self, tool_name: str) -> bool:
                tool = await self.handle_get_tool(tool_name)
                return tool is not None

            async def handle_call_tool(
                self,
                tool_name: str,
                parameters: dict[str, ContextValue],
                correlation_id: UUID,
            ) -> dict[str, ContextValue]:
                tool = await self.handle_get_tool(tool_name)
                if tool is None:
                    raise ValueError(f"Tool not found: {tool_name}")
                # Execute the tool and return results
                return {"status": "success", "result": "..."}

        handler = AgentMCPHandler()
        assert isinstance(handler, ProtocolMCPHandler)

        # List available tools
        tools = await handler.handle_list_tools()
        print(f"Available tools: {[t.name for t in tools]}")

        # Execute a tool
        result = await handler.handle_call_tool(
            tool_name="web_search",
            parameters={"query": "python tutorials"},
            correlation_id=uuid4(),
        )
        ```

    See Also:
        - ProtocolMCPRegistry: Central registry for tool coordination
        - ProtocolMCPToolProxy: Proxy for distributed tool execution
        - ProtocolMCPToolDefinition: Tool definition structure
    """

    @property
    def supported_tool_types(self) -> list[LiteralMCPToolType]:
        """
        Get the list of MCP tool types supported by this handler.

        Returns the tool type categories that this handler can process.
        Implementations should return only types they can actually handle.

        Returns:
            List of supported tool types (e.g., ["function", "resource"]).

        Example:
            ```python
            handler: ProtocolMCPHandler = get_handler()
            types = handler.supported_tool_types
            if "function" in types:
                print("Handler supports function tools")
            ```
        """
        ...

    async def handle_list_tools(self) -> list[ProtocolMCPToolDefinition]:
        """
        List all available tools managed by this handler.

        Retrieves the complete list of tool definitions that this handler
        can provide. The returned tools should be filtered to only include
        those matching the handler's supported_tool_types.

        Returns:
            List of tool definitions available through this handler.
            Returns empty list if no tools are available.

        Raises:
            SPIError: If tool listing fails due to registry unavailability
                or other infrastructure issues.

        Example:
            ```python
            handler: ProtocolMCPHandler = get_handler()
            tools = await handler.handle_list_tools()
            for tool in tools:
                print(f"Tool: {tool.name} ({tool.tool_type})")
                print(f"  Description: {tool.description}")
                print(f"  Parameters: {len(tool.parameters)}")
            ```
        """
        ...

    async def handle_get_tool(self, tool_name: str) -> ProtocolMCPToolDefinition | None:
        """
        Get a specific tool definition by name.

        Retrieves the complete definition for a single tool identified
        by its unique name. Returns None if the tool is not found or
        not supported by this handler.

        Args:
            tool_name: Unique identifier of the tool to retrieve.

        Returns:
            Tool definition if found, None otherwise.

        Example:
            ```python
            handler: ProtocolMCPHandler = get_handler()
            tool = await handler.handle_get_tool("web_search")
            if tool:
                print(f"Found tool: {tool.name}")
                print(f"Version: {tool.version}")
                print(f"Endpoint: {tool.execution_endpoint}")
            else:
                print("Tool not found")
            ```
        """
        ...

    async def handle_tool_exists(self, tool_name: str) -> bool:
        """
        Check if a tool exists and is available.

        Performs a quick existence check for a tool without retrieving
        its full definition. More efficient than handle_get_tool when
        only existence information is needed.

        Args:
            tool_name: Unique identifier of the tool to check.

        Returns:
            True if the tool exists and is available, False otherwise.

        Example:
            ```python
            handler: ProtocolMCPHandler = get_handler()
            if await handler.handle_tool_exists("web_search"):
                result = await handler.handle_call_tool(
                    "web_search",
                    {"query": "example"},
                    uuid4(),
                )
            else:
                print("web_search tool is not available")
            ```
        """
        ...

    async def handle_call_tool(
        self,
        tool_name: str,
        parameters: dict[str, "ContextValue"],
        correlation_id: UUID,
    ) -> dict[str, "ContextValue"]:
        """
        Execute a tool call with the given parameters.

        Invokes the specified tool with provided parameters and returns
        the execution result. The correlation_id enables request tracing
        across distributed systems.

        Args:
            tool_name: Unique identifier of the tool to execute.
            parameters: Input parameters for the tool execution as
                key-value pairs matching the tool's parameter schema.
            correlation_id: UUID for request correlation and tracing
                across service boundaries.

        Returns:
            Execution result as a dictionary containing the tool's
            output data. Structure depends on the specific tool's
            return_schema definition.

        Raises:
            SPIError: If tool execution fails.
            ValueError: If the tool is not found or parameters are invalid.

        Example:
            ```python
            from uuid import uuid4

            handler: ProtocolMCPHandler = get_handler()
            correlation_id = uuid4()

            # Execute a search tool
            result = await handler.handle_call_tool(
                tool_name="web_search",
                parameters={
                    "query": "python async programming",
                    "max_results": 10,
                },
                correlation_id=correlation_id,
            )

            # Process results
            if result.get("status") == "success":
                for item in result.get("results", []):
                    print(f"- {item['title']}: {item['url']}")
            else:
                print(f"Search failed: {result.get('error')}")
            ```

        Note:
            The correlation_id should be propagated to any downstream
            service calls to enable end-to-end request tracing.
        """
        ...


__all__ = [
    "ProtocolMCPHandler",
]
