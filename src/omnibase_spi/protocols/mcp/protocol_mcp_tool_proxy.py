#!/usr/bin/env python3
"""
MCP Tool Proxy Protocol - ONEX SPI Interface.

Protocol definition for MCP tool execution proxy and routing.
Handles tool execution routing, load balancing, and result aggregation.

Domain: MCP tool execution and proxy management
"""

from typing import Any, Optional, Protocol, runtime_checkable
from uuid import UUID

from omnibase_spi.protocols.types.protocol_core_types import ContextValue
from omnibase_spi.protocols.types.protocol_mcp_types import (
    LiteralMCPExecutionStatus,
    ProtocolMCPSubsystemRegistration,
    ProtocolMCPToolDefinition,
    ProtocolMCPToolExecution,
)


@runtime_checkable
class ProtocolMCPToolRouter(Protocol):
    """
    Protocol for MCP tool routing and selection.

    Handles intelligent routing of tool execution requests
    to appropriate subsystem implementations based on load,
    health, and routing policies.
    """

    async def select_tool_implementation(
        self,
        tool_name: str,
        parameters: dict[str, ContextValue],
        routing_policy: Optional[str],
    ) -> Optional[ProtocolMCPToolDefinition]:
        """
        Select the best tool implementation for execution.

        Args:
            tool_name: Name of the tool
            parameters: Tool execution parameters
            routing_policy: Optional routing policy (round_robin, least_loaded, etc.)

        Returns:
            Selected tool definition or None if no suitable implementation
        """
        ...

    async def get_available_implementations(
        self, tool_name: str
    ) -> list[ProtocolMCPToolDefinition]:
        """
        Get all available implementations of a tool.

        Args:
            tool_name: Name of the tool

        Returns:
            List of available tool implementations
        """
        ...

    async def check_implementation_health(
        self, tool_def: ProtocolMCPToolDefinition
    ) -> bool:
        """
        Check if a tool implementation is healthy and available.

        Args:
            tool_def: Tool definition to check

        Returns:
            True if implementation is healthy
        """
        ...

    async def get_routing_statistics(self) -> dict[str, Any]:
        """
        Get routing statistics and metrics.

        Returns:
            Routing statistics including selection counts and performance
        """
        ...


@runtime_checkable
class ProtocolMCPToolExecutor(Protocol):
    """
    Protocol for MCP tool execution management.

    Handles the actual execution of tools through HTTP proxying,
    including retry logic, timeout handling, and result processing.
    """

    async def execute_tool(
        self,
        tool_def: ProtocolMCPToolDefinition,
        subsystem: ProtocolMCPSubsystemRegistration,
        parameters: dict[str, ContextValue],
        execution_id: str,
        correlation_id: UUID,
        timeout_seconds: Optional[int],
    ) -> dict[str, Any]:
        """
        Execute a tool on a specific subsystem.

        Args:
            tool_def: Tool definition
            subsystem: Target subsystem registration
            parameters: Tool execution parameters
            execution_id: Unique execution identifier
            correlation_id: Request correlation ID
            timeout_seconds: Optional timeout override

        Returns:
            Tool execution result

        Raises:
            TimeoutError: If execution times out
            RuntimeError: If execution fails
        """
        ...

    async def execute_with_retry(
        self,
        tool_def: ProtocolMCPToolDefinition,
        subsystem: ProtocolMCPSubsystemRegistration,
        parameters: dict[str, ContextValue],
        execution_id: str,
        correlation_id: UUID,
        max_retries: Optional[int],
    ) -> dict[str, Any]:
        """
        Execute tool with retry logic on failure.

        Args:
            tool_def: Tool definition
            subsystem: Target subsystem registration
            parameters: Tool execution parameters
            execution_id: Unique execution identifier
            correlation_id: Request correlation ID
            max_retries: Optional retry count override

        Returns:
            Tool execution result
        """
        ...

    async def cancel_execution(self, execution_id: str) -> bool:
        """
        Cancel a running tool execution.

        Args:
            execution_id: Tool execution ID

        Returns:
            True if cancellation successful
        """
        ...

    async def get_execution_status(
        self, execution_id: str
    ) -> Optional[LiteralMCPExecutionStatus]:
        """
        Get current execution status.

        Args:
            execution_id: Tool execution ID

        Returns:
            Current execution status or None if not found
        """
        ...


@runtime_checkable
class ProtocolMCPToolProxy(Protocol):
    """
    Comprehensive MCP tool proxy protocol for distributed tool execution.

    Combines routing, execution, and result management to provide
    a complete tool proxy solution for the MCP registry system.

    Key Features:
        - **Intelligent Routing**: Route tools to optimal subsystem implementations
        - **Load Balancing**: Distribute load across multiple implementations
        - **Fault Tolerance**: Handle failures with retry and failover logic
        - **Execution Tracking**: Track all tool executions with detailed metrics
        - **Performance Monitoring**: Monitor execution performance and success rates
        - **Cancellation Support**: Cancel long-running executions
        - **Result Caching**: Optional result caching for expensive operations
    """

    @property
    def router(self) -> ProtocolMCPToolRouter:
        """Get the tool router implementation."""
        ...

    @property
    def executor(self) -> ProtocolMCPToolExecutor:
        """Get the tool executor implementation."""
        ...

    async def proxy_tool_execution(
        self,
        tool_name: str,
        parameters: dict[str, ContextValue],
        correlation_id: UUID,
        timeout_seconds: Optional[int],
        routing_policy: Optional[str],
        preferred_subsystem: Optional[str],
    ) -> dict[str, Any]:
        """
        Proxy tool execution with intelligent routing and error handling.

        Args:
            tool_name: Name of the tool to execute
            parameters: Tool execution parameters
            correlation_id: Request correlation ID
            timeout_seconds: Optional execution timeout
            routing_policy: Optional routing policy (round_robin, least_loaded, etc.)
            preferred_subsystem: Optional preferred subsystem ID

        Returns:
            Tool execution result

        Raises:
            ValueError: If tool not found or parameters invalid
            TimeoutError: If execution times out
            RuntimeError: If execution fails
        """
        ...

    async def proxy_batch_execution(
        self,
        requests: list[dict[str, Any]],
        correlation_id: UUID,
        max_parallel: int,
    ) -> list[dict[str, Any]]:
        """
        Execute multiple tools in parallel with batching.

        Args:
            requests: List of tool execution requests
            correlation_id: Request correlation ID
            max_parallel: Maximum parallel executions

        Returns:
            List of execution results in request order
        """
        ...

    async def get_active_executions(
        self, tool_name: Optional[str] = None
    ) -> list[ProtocolMCPToolExecution]:
        """
        Get currently active tool executions.

        Args:
            tool_name: Optional filter by tool name

        Returns:
            List of active executions
        """
        ...

    async def get_execution_history(
        self,
        tool_name: Optional[str],
        subsystem_id: Optional[str],
        correlation_id: Optional[UUID],
        limit: int,
    ) -> list[ProtocolMCPToolExecution]:
        """
        Get tool execution history with filtering.

        Args:
            tool_name: Optional filter by tool name
            subsystem_id: Optional filter by subsystem
            correlation_id: Optional filter by correlation ID
            limit: Maximum number of results

        Returns:
            List of execution history records
        """
        ...

    async def cancel_execution(self, execution_id: str) -> bool:
        """
        Cancel a running tool execution.

        Args:
            execution_id: Tool execution ID

        Returns:
            True if cancellation successful
        """
        ...

    async def cancel_all_executions(
        self,
        tool_name: Optional[str],
        subsystem_id: Optional[str],
    ) -> int:
        """
        Cancel multiple running executions.

        Args:
            tool_name: Optional filter by tool name
            subsystem_id: Optional filter by subsystem

        Returns:
            Number of executions cancelled
        """
        ...

    async def get_execution_metrics(
        self,
        time_range_hours: int,
        tool_name: Optional[str],
    ) -> dict[str, Any]:
        """
        Get execution metrics and statistics.

        Args:
            time_range_hours: Time range for metrics
            tool_name: Optional filter by tool name

        Returns:
            Execution metrics including success rates, durations, error counts
        """
        ...

    async def get_load_balancing_stats(self) -> dict[str, Any]:
        """
        Get load balancing statistics across subsystems.

        Returns:
            Load balancing statistics and distribution metrics
        """
        ...

    async def configure_caching(
        self,
        tool_name: str,
        cache_ttl_seconds: int,
        cache_key_fields: list[str],
    ) -> bool:
        """
        Configure result caching for a tool.

        Args:
            tool_name: Name of the tool
            cache_ttl_seconds: Cache time-to-live
            cache_key_fields: Parameter fields to use for cache key

        Returns:
            True if caching configured successfully
        """
        ...

    async def clear_cache(self, tool_name: Optional[str] = None) -> int:
        """
        Clear cached results.

        Args:
            tool_name: Optional filter by tool name

        Returns:
            Number of cache entries cleared
        """
        ...

    async def validate_proxy_configuration(self) -> dict[str, Any]:
        """
        Validate proxy configuration and connectivity.

        Returns:
            Validation results including connectivity tests and configuration checks
        """
        ...
