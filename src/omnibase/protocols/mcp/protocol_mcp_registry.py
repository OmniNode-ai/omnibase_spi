#!/usr/bin/env python3
"""
MCP Registry Protocol - ONEX SPI Interface.

Comprehensive protocol definition for Model Context Protocol registry management.
Supports distributed tool registration, execution routing, and subsystem coordination.

Domain: MCP infrastructure and service coordination
"""

from typing import Any, Optional, Protocol, runtime_checkable
from uuid import UUID

from omnibase.protocols.types.core_types import (
    ContextValue,
    OperationStatus,
    ProtocolDateTime,
    ProtocolValidationResult,
)
from omnibase.protocols.types.mcp_types import (
    MCPLifecycleState,
    MCPSubsystemType,
    MCPToolType,
    ProtocolMCPHealthCheck,
    ProtocolMCPRegistryConfig,
    ProtocolMCPRegistryMetrics,
    ProtocolMCPRegistryStatus,
    ProtocolMCPSubsystemRegistration,
    ProtocolMCPToolDefinition,
    ProtocolMCPToolExecution,
    ProtocolMCPValidationResult,
)


@runtime_checkable
class ProtocolMCPRegistry(Protocol):
    """
    Core MCP registry protocol for distributed tool coordination.

    Manages subsystem registration, tool discovery, and execution routing
    across multiple MCP-enabled subsystems in the ONEX ecosystem.

    Key Features:
        - **Multi-Subsystem Coordination**: Register and coordinate multiple MCP subsystems
        - **Dynamic Tool Discovery**: Discover and route tools across registered subsystems
        - **Load Balancing**: Distribute tool execution across multiple implementations
        - **Health Monitoring**: Monitor subsystem health and handle failures gracefully
        - **Execution Tracking**: Track tool execution metrics and performance
        - **Security**: API key authentication and request validation
        - **TTL Management**: Automatic cleanup of expired registrations
    """

    @property
    def config(self) -> ProtocolMCPRegistryConfig:
        """Get registry configuration."""
        ...

    async def register_subsystem(
        self,
        subsystem_metadata: Any,  # ProtocolMCPSubsystemMetadata from types
        tools: list[ProtocolMCPToolDefinition],
        api_key: str,
        configuration: Optional[dict[str, ContextValue]],
    ) -> str:
        """
        Register a new subsystem and its tools with the registry.

        Args:
            subsystem_metadata: Subsystem identification and metadata
            tools: List of tool definitions provided by the subsystem
            api_key: Authentication key for the subsystem
            configuration: Optional subsystem-specific configuration

        Returns:
            Registration ID for the subsystem

        Raises:
            ValueError: If registration data is invalid or conflicts exist
        """
        ...

    async def unregister_subsystem(self, registration_id: str) -> bool:
        """
        Unregister a subsystem and remove all its tools.

        Args:
            registration_id: Subsystem registration ID

        Returns:
            True if unregistration successful
        """
        ...

    async def update_subsystem_heartbeat(
        self,
        registration_id: str,
        health_status: Optional[str],
        metadata: Optional[dict[str, ContextValue]],
    ) -> bool:
        """
        Update subsystem heartbeat and health status.

        Args:
            registration_id: Subsystem registration ID
            health_status: Optional health status update
            metadata: Optional metadata update

        Returns:
            True if heartbeat update successful
        """
        ...

    async def get_subsystem_registration(
        self, registration_id: str
    ) -> Optional[ProtocolMCPSubsystemRegistration]:
        """
        Get subsystem registration information.

        Args:
            registration_id: Subsystem registration ID

        Returns:
            Subsystem registration or None if not found
        """
        ...

    async def get_all_subsystems(
        self,
        subsystem_type: Optional[MCPSubsystemType],
        status_filter: Optional[OperationStatus],
    ) -> list[ProtocolMCPSubsystemRegistration]:
        """
        Get all registered subsystems with optional filtering.

        Args:
            subsystem_type: Optional filter by subsystem type
            status_filter: Optional filter by registration status

        Returns:
            List of matching subsystem registrations
        """
        ...

    async def discover_tools(
        self,
        tool_type: Optional[MCPToolType],
        tags: Optional[list[str]],
        subsystem_id: Optional[str],
    ) -> list[ProtocolMCPToolDefinition]:
        """
        Discover available tools with optional filtering.

        Args:
            tool_type: Optional filter by tool type
            tags: Optional filter by tool tags
            subsystem_id: Optional filter by subsystem

        Returns:
            List of matching tool definitions
        """
        ...

    async def get_tool_definition(
        self, tool_name: str
    ) -> Optional[ProtocolMCPToolDefinition]:
        """
        Get tool definition by name (returns first available implementation).

        Args:
            tool_name: Name of the tool

        Returns:
            Tool definition or None if not found
        """
        ...

    async def get_all_tool_implementations(
        self, tool_name: str
    ) -> list[ProtocolMCPToolDefinition]:
        """
        Get all implementations of a tool across subsystems.

        Args:
            tool_name: Name of the tool

        Returns:
            List of tool implementations
        """
        ...

    async def execute_tool(
        self,
        tool_name: str,
        parameters: dict[str, ContextValue],
        correlation_id: UUID,
        timeout_seconds: Optional[int],
        preferred_subsystem: Optional[str],
    ) -> dict[str, Any]:
        """
        Execute a tool with load balancing and error handling.

        Args:
            tool_name: Name of the tool to execute
            parameters: Tool execution parameters
            correlation_id: Request correlation ID for tracing
            timeout_seconds: Optional execution timeout override
            preferred_subsystem: Optional subsystem preference

        Returns:
            Tool execution result

        Raises:
            ValueError: If tool not found or parameters invalid
            TimeoutError: If execution times out
            RuntimeError: If execution fails
        """
        ...

    async def get_tool_execution(
        self, execution_id: str
    ) -> Optional[ProtocolMCPToolExecution]:
        """
        Get tool execution status and results.

        Args:
            execution_id: Tool execution ID

        Returns:
            Tool execution information or None if not found
        """
        ...

    async def get_tool_executions(
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
            List of matching tool executions
        """
        ...

    async def cancel_tool_execution(self, execution_id: str) -> bool:
        """
        Cancel a running tool execution.

        Args:
            execution_id: Tool execution ID

        Returns:
            True if cancellation successful
        """
        ...

    async def validate_subsystem_registration(
        self,
        subsystem_metadata: Any,  # ProtocolMCPSubsystemMetadata
        tools: list[ProtocolMCPToolDefinition],
    ) -> ProtocolMCPValidationResult:
        """
        Validate subsystem registration data.

        Args:
            subsystem_metadata: Subsystem metadata to validate
            tools: Tool definitions to validate

        Returns:
            Validation result with errors and warnings
        """
        ...

    async def validate_tool_parameters(
        self,
        tool_name: str,
        parameters: dict[str, ContextValue],
    ) -> ProtocolValidationResult:
        """
        Validate tool execution parameters.

        Args:
            tool_name: Name of the tool
            parameters: Parameters to validate

        Returns:
            Validation result
        """
        ...

    async def perform_health_check(
        self, registration_id: str
    ) -> ProtocolMCPHealthCheck:
        """
        Perform health check on a registered subsystem.

        Args:
            registration_id: Subsystem registration ID

        Returns:
            Health check result
        """
        ...

    async def get_subsystem_health(
        self, registration_id: str
    ) -> Optional[ProtocolMCPHealthCheck]:
        """
        Get latest health check result for a subsystem.

        Args:
            registration_id: Subsystem registration ID

        Returns:
            Latest health check result or None if not found
        """
        ...

    async def cleanup_expired_registrations(self) -> int:
        """
        Remove expired subsystem registrations based on TTL.

        Returns:
            Number of registrations removed
        """
        ...

    async def update_subsystem_configuration(
        self,
        registration_id: str,
        configuration: dict[str, ContextValue],
    ) -> bool:
        """
        Update subsystem configuration.

        Args:
            registration_id: Subsystem registration ID
            configuration: New configuration values

        Returns:
            True if update successful
        """
        ...

    async def get_registry_status(self) -> ProtocolMCPRegistryStatus:
        """
        Get comprehensive registry status and metrics.

        Returns:
            Registry status information
        """
        ...

    async def get_registry_metrics(self) -> ProtocolMCPRegistryMetrics:
        """
        Get detailed registry metrics and statistics.

        Returns:
            Registry metrics
        """
        ...


@runtime_checkable
class ProtocolMCPRegistryAdmin(Protocol):
    """
    Administrative protocol for MCP registry management.

    Provides privileged operations for registry administration,
    configuration management, and system maintenance.
    """

    async def set_maintenance_mode(self, enabled: bool) -> bool:
        """Enable or disable registry maintenance mode."""
        ...

    async def force_subsystem_cleanup(self, registration_id: str) -> bool:
        """Force cleanup of a specific subsystem registration."""
        ...

    async def update_registry_configuration(
        self, configuration: dict[str, ContextValue]
    ) -> bool:
        """Update registry configuration dynamically."""
        ...

    async def export_registry_state(self) -> dict[str, Any]:
        """Export complete registry state for backup/migration."""
        ...

    async def import_registry_state(self, state_data: dict[str, Any]) -> bool:
        """Import registry state from backup/migration data."""
        ...

    async def get_system_diagnostics(self) -> dict[str, Any]:
        """Get comprehensive system diagnostics information."""
        ...


@runtime_checkable
class ProtocolMCPRegistryMetricsOperations(Protocol):
    """
    Protocol for advanced MCP registry metrics and analytics.

    Provides detailed performance metrics, trend analysis,
    and operational insights for the registry system.
    """

    async def get_execution_metrics(
        self,
        time_range_hours: int,
        tool_name: Optional[str],
        subsystem_id: Optional[str],
    ) -> dict[str, Any]:
        """Get tool execution metrics for specified time range."""
        ...

    async def get_performance_trends(
        self, metric_name: str, time_range_hours: int
    ) -> dict[str, Any]:
        """Get performance trend data for specified metric."""
        ...

    async def get_error_analysis(self, time_range_hours: int) -> dict[str, Any]:
        """Get error analysis and patterns."""
        ...

    async def get_capacity_metrics(self) -> dict[str, Any]:
        """Get current capacity utilization metrics."""
        ...
