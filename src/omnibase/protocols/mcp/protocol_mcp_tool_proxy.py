#!/usr/bin/env python3
"""
MCP Tool Proxy Protocol - ONEX SPI Interface.

Protocol definition for MCP tool execution proxy and routing.
Handles tool execution routing, load balancing, and result aggregation.

Domain: MCP tool execution and proxy management
"""

from typing import Any, Optional, Protocol, runtime_checkable
from uuid import UUID

from omnibase.protocols.types.core_types import ContextValue, ProtocolDateTime
from omnibase.protocols.types.mcp_types import (
    MCPExecutionStatus,
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
        routing_policy: Optional[str] = None,
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
        timeout_seconds: Optional[int] = None,
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
        max_retries: Optional[int] = None,
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
    ) -> Optional[MCPExecutionStatus]:
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

    Usage Example:
        ```python
        # Proxy implementation (not part of SPI)
        class MCPToolProxyImpl:
            def __init__(
                self,
                router: ProtocolMCPToolRouter,
                executor: ProtocolMCPToolExecutor
            ):
                self.router = router
                self.executor = executor
                self.active_executions: dict[str, ProtocolMCPToolExecution] = {}
                self.execution_history: list[ProtocolMCPToolExecution] = []

            async def proxy_tool_execution(
                self,
                tool_name: str,
                parameters: dict[str, ContextValue],
                correlation_id: UUID,
                timeout_seconds: Optional[int] = None,
                routing_policy: Optional[str] = None,
                preferred_subsystem: Optional[str] = None
            ) -> dict[str, Any]:
                # Create execution tracking
                execution_id = str(uuid4())
                execution = MCPToolExecution(
                    execution_id=execution_id,
                    tool_name=tool_name,
                    subsystem_id="",  # Will be set after routing
                    parameters=parameters,
                    execution_status="pending",
                    started_at=datetime.now(),
                    completed_at=None,
                    duration_ms=None,
                    result=None,
                    error_message=None,
                    retry_count=0,
                    correlation_id=correlation_id,
                    metadata={"routing_policy": routing_policy or "default"}
                )

                self.active_executions[execution_id] = execution

                try:
                    # Route to appropriate implementation
                    if preferred_subsystem:
                        tool_def = await self._find_tool_in_subsystem(
                            tool_name, preferred_subsystem
                        )
                        if not tool_def:
                            raise ValueError(f"Tool {tool_name} not found in subsystem {preferred_subsystem}")
                    else:
                        tool_def = await self.router.select_tool_implementation(
                            tool_name, parameters, routing_policy
                        )
                        if not tool_def:
                            raise ValueError(f"No available implementation for tool: {tool_name}")

                    # Get subsystem for tool
                    subsystem = await self._get_subsystem_for_tool(tool_def)
                    execution.subsystem_id = subsystem.subsystem_metadata.subsystem_id
                    execution.execution_status = "running"

                    # Execute tool
                    result = await self.executor.execute_with_retry(
                        tool_def=tool_def,
                        subsystem=subsystem,
                        parameters=parameters,
                        execution_id=execution_id,
                        correlation_id=correlation_id,
                        max_retries=tool_def.retry_count
                    )

                    # Update execution tracking
                    execution.result = result
                    execution.execution_status = "completed"
                    execution.completed_at = datetime.now()
                    execution.duration_ms = int(
                        (execution.completed_at - execution.started_at).total_seconds() * 1000
                    )

                    return result

                except Exception as e:
                    # Handle execution failure
                    execution.execution_status = "failed"
                    execution.error_message = str(e)
                    execution.completed_at = datetime.now()
                    execution.duration_ms = int(
                        (execution.completed_at - execution.started_at).total_seconds() * 1000
                    )

                    raise

                finally:
                    # Move to history and cleanup
                    if execution_id in self.active_executions:
                        del self.active_executions[execution_id]
                    self.execution_history.append(execution)

                    # Keep history bounded
                    if len(self.execution_history) > 1000:
                        self.execution_history = self.execution_history[-500:]

        # Usage in registry
        proxy: ProtocolMCPToolProxy = MCPToolProxyImpl(router, executor)

        # Execute tool with automatic routing
        result = await proxy.proxy_tool_execution(
            tool_name="analyze_data",
            parameters={"dataset_id": "data-123", "analysis_type": "detailed"},
            correlation_id=uuid4(),
            routing_policy="least_loaded"
        )

        # Execute with preferred subsystem
        result = await proxy.proxy_tool_execution(
            tool_name="process_batch",
            parameters={"batch_id": "batch-456"},
            correlation_id=uuid4(),
            preferred_subsystem="data-processor-1"
        )

        # Monitor active executions
        active = await proxy.get_active_executions()
        print(f"Currently running: {len(active)} executions")

        # Get execution metrics
        metrics = await proxy.get_execution_metrics()
        print(f"Success rate: {metrics['success_rate']}%")
        print(f"Average duration: {metrics['average_duration_ms']}ms")
        ```

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
        timeout_seconds: Optional[int] = None,
        routing_policy: Optional[str] = None,
        preferred_subsystem: Optional[str] = None,
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
        max_parallel: int = 10,
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
        tool_name: Optional[str] = None,
        subsystem_id: Optional[str] = None,
        correlation_id: Optional[UUID] = None,
        limit: int = 100,
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
        tool_name: Optional[str] = None,
        subsystem_id: Optional[str] = None,
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
        time_range_hours: int = 24,
        tool_name: Optional[str] = None,
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
