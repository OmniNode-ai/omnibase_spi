"""
Discovery Client Protocol for ONEX Event-Driven Service Discovery

Defines the protocol interface for discovery client implementations.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_core.types import JsonType


@runtime_checkable
class ProtocolDiscoveredTool(Protocol):
    """
    Protocol for discovered tool metadata and health information.

    Represents a tool discovered through the event-driven service
    discovery system, providing identification, classification,
    metadata, and health status for runtime tool selection.

    Example:
        ```python
        client: ProtocolDiscoveryClient = get_discovery_client()
        tools = await client.discover_healthy_tools()

        for tool in tools:
            if tool.is_healthy:
                print(f"Tool: {tool.tool_name} ({tool.tool_type})")
                print(f"  Metadata: {tool.metadata}")
        ```

    See Also:
        - ProtocolDiscoveryClient: Discovery interface
        - ProtocolCliDiscoveredTool: CLI-specific tool info
    """

    @property
    def tool_name(self) -> str:
        """Name of the discovered tool."""
        ...

    @property
    def tool_type(self) -> str:
        """Type of the tool."""
        ...

    @property
    def metadata(self) -> "dict[str, JsonType]":
        """Tool metadata."""
        ...

    @property
    def is_healthy(self) -> bool:
        """Whether the tool is healthy."""
        ...


@runtime_checkable
class ProtocolDiscoveryClient(Protocol):
    """
    Protocol interface for event-driven service discovery client.

    Provides the contract for discovering tools and services in an ONEX
    ecosystem using event-driven patterns with timeout handling,
    correlation tracking, retry logic, and response aggregation.

    Example:
        ```python
        client: ProtocolDiscoveryClient = get_discovery_client()

        try:
            # Discover all tools with specific filters
            tools = await client.discover_tools(
                filters={"capabilities": ["code_generation"]},
                timeout=30.0,
                max_results=10,
                include_metadata=True
            )
            print(f"Discovered {len(tools)} tools")

            # Discover by protocol
            graphql_tools = await client.discover_tools_by_protocol(
                protocol="graphql",
                timeout=15.0
            )

            # Discover by tags
            validator_tools = await client.discover_tools_by_tags(
                tags=["validator", "onex"],
                timeout=15.0
            )

            # Get only healthy tools
            healthy_tools = await client.discover_healthy_tools()

            # Check client statistics
            stats = await client.get_client_stats()
            print(f"Pending requests: {await client.get_pending_request_count()}")

        finally:
            await client.close()
        ```

    See Also:
        - ProtocolDiscoveredTool: Discovered tool representation
        - ProtocolNodeRegistry: Node-based discovery
        - ProtocolEventBus: Event transport for discovery
    """

    async def discover_tools(
        self,
        filters: "dict[str, JsonType] | None" = None,
        timeout: float | None = None,
        max_results: int | None = None,
        include_metadata: bool | None = None,
        retry_count: int | None = None,
        retry_delay: float | None = None,
    ) -> list[ProtocolDiscoveredTool]:
        """
        Discover available tools/services based on filters.

        Args:
            filters: Discovery filters (tags, protocols, actions, etc.)
            timeout: Timeout in seconds (uses default if None)
            max_results: Maximum number of results to return
            include_metadata: Whether to include full metadata
            retry_count: Number of retries on timeout (0 = no retries)
            retry_delay: Delay between retries in seconds

        Returns:
            List of discovered tools matching the filters

        Raises:
            ModelDiscoveryTimeoutError: If request times out
            ModelDiscoveryError: If discovery fails
        """
        ...

    async def discover_tools_by_protocol(
        self,
        protocol: str,
        timeout: float | None = None,
        **kwargs: object,
    ) -> list[ProtocolDiscoveredTool]:
        """
        Convenience method to discover tools by protocol.

        Args:
            protocol: Protocol to filter by (e.g. 'mcp', 'graphql')
            timeout: Timeout in seconds
            **kwargs: Additional discovery options

        Returns:
            List of tools supporting the protocol
        """
        ...

    async def discover_tools_by_tags(
        self,
        tags: list[str],
        timeout: float | None = None,
        **kwargs: object,
    ) -> list[ProtocolDiscoveredTool]:
        """
        Convenience method to discover tools by tags.

        Args:
            tags: Tags to filter by (e.g. ['generator', 'validated'])
            timeout: Timeout in seconds
            **kwargs: Additional discovery options

        Returns:
            List of tools with the specified tags
        """
        ...

    async def discover_healthy_tools(
        self,
        timeout: float | None = None,
        **kwargs: object,
    ) -> list[ProtocolDiscoveredTool]:
        """
        Convenience method to discover only healthy tools.

        Args:
            timeout: Timeout in seconds
            **kwargs: Additional discovery options

        Returns:
            List of healthy tools
        """
        ...

    async def close(self, timeout_seconds: float = 30.0) -> None:
        """
        Close the discovery client and clean up resources.

        Cancels any pending requests and unsubscribes from events.

        Args:
            timeout_seconds: Maximum time to wait for cleanup to complete.
                Defaults to 30.0 seconds.

        Raises:
            TimeoutError: If cleanup does not complete within the specified timeout.
        """
        ...

    async def get_pending_request_count(self) -> int:
        """
        Get the number of pending discovery requests.

        Returns:
            Number of pending requests
        """
        ...

    async def get_client_stats(self) -> "dict[str, JsonType]":
        """
        Get client statistics.

        Returns:
            Dictionary with client statistics
        """
        ...
