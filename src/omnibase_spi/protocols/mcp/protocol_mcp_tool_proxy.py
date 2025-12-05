"""
MCP Tool Proxy Protocol - ONEX SPI Interface.

Protocol definition for MCP tool execution proxy and routing.
Handles tool execution routing, load balancing, and result aggregation.

Domain: MCP tool execution and proxy management
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable
from uuid import UUID

if TYPE_CHECKING:
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
        parameters: dict[str, "ContextValue"],
        routing_policy: str | None,
    ) -> ProtocolMCPToolDefinition | None: ...

    async def get_available_implementations(
        self, tool_name: str
    ) -> list[ProtocolMCPToolDefinition]: ...

    async def check_implementation_health(
        self, tool_def: "ProtocolMCPToolDefinition"
    ) -> bool: ...

    async def get_routing_statistics(self) -> dict[str, "ContextValue"]: ...


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
        parameters: dict[str, "ContextValue"],
        execution_id: str,
        correlation_id: UUID,
        timeout_seconds: int | None,
    ) -> dict[str, "ContextValue"]: ...

    async def execute_with_retry(
        self,
        tool_def: ProtocolMCPToolDefinition,
        subsystem: ProtocolMCPSubsystemRegistration,
        parameters: dict[str, "ContextValue"],
        execution_id: str,
        correlation_id: UUID,
        max_retries: int | None,
    ) -> dict[str, "ContextValue"]: ...

    async def cancel_execution(self, execution_id: str) -> bool: ...

    async def get_execution_status(
        self, execution_id: str
    ) -> LiteralMCPExecutionStatus | None: ...


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
    def router(self) -> ProtocolMCPToolRouter: ...

    @property
    def executor(self) -> ProtocolMCPToolExecutor: ...

    async def proxy_tool_execution(
        self,
        tool_name: str,
        parameters: dict[str, "ContextValue"],
        correlation_id: UUID,
        timeout_seconds: int | None,
        routing_policy: str | None,
        preferred_subsystem: str | None,
    ) -> dict[str, "ContextValue"]: ...

    async def proxy_batch_execution(
        self,
        requests: list[dict[str, "ContextValue"]],
        correlation_id: UUID,
        max_parallel: int,
    ) -> list[dict[str, "ContextValue"]]: ...

    async def get_active_executions(
        self, tool_name: str | None = None
    ) -> list[ProtocolMCPToolExecution]: ...

    async def get_execution_history(
        self,
        tool_name: str | None,
        subsystem_id: str | None,
        correlation_id: UUID | None,
        limit: int,
    ) -> list[ProtocolMCPToolExecution]: ...

    async def cancel_execution(self, execution_id: str) -> bool: ...

    async def cancel_all_executions(
        self, tool_name: str | None, subsystem_id: str | None
    ) -> int: ...

    async def get_execution_metrics(
        self, time_range_hours: int, tool_name: str | None
    ) -> dict[str, "ContextValue"]: ...

    async def get_load_balancing_stats(self) -> dict[str, "ContextValue"]: ...

    async def configure_caching(
        self, tool_name: str, cache_ttl_seconds: int, cache_key_fields: list[str]
    ) -> bool: ...

    async def clear_cache(self, tool_name: str | None = None) -> int: ...

    async def validate_proxy_configuration(self) -> dict[str, "ContextValue"]: ...
