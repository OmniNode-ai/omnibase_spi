"""
Discovery Client Protocol for ONEX Event-Driven Service Discovery

Defines the protocol interface for discovery client implementations.
"""

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    # Forward reference for discovery types to maintain namespace isolation
    class ModelDiscoveredTool:
        """Protocol for discovered tool information."""

        tool_name: str
        tool_type: str
        metadata: dict[str, Any]
        is_healthy: bool


@runtime_checkable
class ProtocolDiscoveryClient(Protocol):
    """
    Protocol interface for discovery client implementations.

    Defines the contract for event-driven service discovery with timeout
    handling, correlation tracking, and response aggregation.
    """

    async def discover_tools(
        self,
        filters: dict[str, Any] | None = None,
        timeout: float | None = None,
        max_results: int | None = None,
        include_metadata: bool = True,
        retry_count: int = 0,
        retry_delay: float = 1.0,
    ) -> list["ModelDiscoveredTool"]:
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
        **kwargs: Any,
    ) -> list["ModelDiscoveredTool"]:
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
        **kwargs: Any,
    ) -> list["ModelDiscoveredTool"]:
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
        **kwargs: Any,
    ) -> list["ModelDiscoveredTool"]:
        """
        Convenience method to discover only healthy tools.

        Args:
            timeout: Timeout in seconds
            **kwargs: Additional discovery options

        Returns:
            List of healthy tools
        """
        ...

    async def close(self) -> None:
        """
        Close the discovery client and clean up resources.

        Cancels any pending requests and unsubscribes from events.
        """
        ...

    async def get_pending_request_count(self) -> int:
        """Get the number of pending discovery requests"""
        ...

    async def get_client_stats(self) -> dict[str, Any]:
        """
        Get client statistics.

        Returns:
            Dictionary with client statistics
        """
        ...
