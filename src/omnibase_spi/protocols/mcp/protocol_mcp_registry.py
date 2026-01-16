"""
MCP Registry Protocol - ONEX SPI Interface.

Comprehensive protocol definition for Model Context Protocol registry management.
Supports distributed tool registration, execution routing, and subsystem coordination.

Domain: MCP infrastructure and service coordination
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable
from uuid import UUID

from omnibase_spi.protocols.types.protocol_core_types import LiteralOperationStatus

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_contract import ProtocolContract
    from omnibase_spi.protocols.types.protocol_core_types import ContextValue

from omnibase_spi.protocols.types.protocol_mcp_types import (
    LiteralMCPSubsystemType,
    LiteralMCPToolType,
    ProtocolMCPHealthCheck,
    ProtocolMCPRegistryConfig,
    ProtocolMCPRegistryMetrics,
    ProtocolMCPRegistryStatus,
    ProtocolMCPSubsystemMetadata,
    ProtocolMCPSubsystemRegistration,
    ProtocolMCPToolDefinition,
    ProtocolMCPToolExecution,
    ProtocolMCPValidationResult,
)
from omnibase_spi.protocols.validation.protocol_validation import (
    ProtocolValidationResult,
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
        """
        Get the registry configuration.

        Returns:
            The current registry configuration settings.
        """
        ...

    async def register_subsystem(
        self,
        subsystem_metadata: ProtocolMCPSubsystemMetadata,
        tools: list[ProtocolMCPToolDefinition],
        api_key: str,
        configuration: dict[str, "ContextValue"] | None,
    ) -> str:
        """
        Register a subsystem with its tools in the registry.

        Args:
            subsystem_metadata: Metadata describing the subsystem including
                name, type, version, and capabilities.
            tools: List of tool definitions provided by this subsystem.
            api_key: Authentication key for the subsystem.
            configuration: Optional configuration overrides for the subsystem.

        Returns:
            Registration ID for the newly registered subsystem.

        Raises:
            RegistrationError: If registration fails due to validation or system error.
            ValidationError: If subsystem metadata or tools are invalid.
        """
        ...

    async def unregister_subsystem(self, registration_id: str) -> bool:
        """
        Unregister a subsystem from the registry.

        Args:
            registration_id: The registration ID of the subsystem to remove.

        Returns:
            True if successfully unregistered, False if not found.

        Raises:
            RegistrationError: If unregistration fails due to system error.
        """
        ...

    async def update_subsystem_heartbeat(
        self,
        registration_id: str,
        health_status: str | None,
        metadata: dict[str, "ContextValue"] | None,
    ) -> bool:
        """
        Update the heartbeat for a registered subsystem.

        Args:
            registration_id: The registration ID of the subsystem.
            health_status: Optional updated health status string.
            metadata: Optional metadata updates to merge with existing metadata.

        Returns:
            True if heartbeat was updated, False if subsystem not found.

        Raises:
            RegistryError: If the heartbeat update fails due to system error.
        """
        ...

    async def get_subsystem_registration(
        self, registration_id: str
    ) -> ProtocolMCPSubsystemRegistration | None:
        """
        Get registration details for a subsystem.

        Args:
            registration_id: The registration ID to look up.

        Returns:
            The subsystem registration if found, None otherwise.

        Raises:
            RegistryError: If the lookup fails due to system error.
        """
        ...

    async def get_all_subsystems(
        self,
        subsystem_type: LiteralMCPSubsystemType | None,
        status_filter: LiteralOperationStatus | None,
    ) -> list[ProtocolMCPSubsystemRegistration]:
        """
        Get all registered subsystems with optional filtering.

        Args:
            subsystem_type: Optional filter by subsystem type.
            status_filter: Optional filter by operational status.

        Returns:
            List of matching subsystem registrations.

        Raises:
            RegistryError: If the query fails due to system error.
        """
        ...

    async def discover_tools(
        self,
        tool_type: LiteralMCPToolType | None,
        tags: list[str] | None,
        subsystem_id: str | None,
    ) -> list[ProtocolMCPToolDefinition]:
        """
        Discover available tools with optional filtering.

        Args:
            tool_type: Optional filter by tool type.
            tags: Optional filter by tags (matches any).
            subsystem_id: Optional filter by source subsystem.

        Returns:
            List of matching tool definitions.

        Raises:
            RegistryError: If the discovery query fails.
        """
        ...

    async def get_tool_definition(
        self, tool_name: str
    ) -> ProtocolMCPToolDefinition | None:
        """
        Get the definition for a specific tool.

        Args:
            tool_name: The name of the tool to look up.

        Returns:
            The tool definition if found, None otherwise.

        Raises:
            RegistryError: If the lookup fails due to system error.
        """
        ...

    async def get_all_tool_implementations(
        self, tool_name: str
    ) -> list[ProtocolMCPToolDefinition]:
        """
        Get all implementations of a tool across subsystems.

        Args:
            tool_name: The name of the tool.

        Returns:
            List of all tool implementations from different subsystems.

        Raises:
            RegistryError: If the query fails due to system error.
        """
        ...

    async def execute_tool(
        self,
        tool_name: str,
        parameters: dict[str, "ContextValue"],
        correlation_id: UUID,
        timeout_seconds: int | None,
        preferred_subsystem: str | None,
    ) -> dict[str, "ContextValue"]:
        """
        Execute a tool with the given parameters.

        Args:
            tool_name: The name of the tool to execute.
            parameters: Input parameters for the tool.
            correlation_id: UUID for tracking the execution across systems.
            timeout_seconds: Optional timeout override in seconds.
            preferred_subsystem: Optional preferred subsystem to route to.

        Returns:
            The tool execution result as a dictionary.

        Raises:
            ToolNotFoundError: If the specified tool is not registered.
            ExecutionError: If the tool execution fails.
            TimeoutError: If the execution exceeds the timeout.
        """
        ...

    async def get_tool_execution(
        self, execution_id: str
    ) -> ProtocolMCPToolExecution | None:
        """
        Get details of a specific tool execution.

        Args:
            execution_id: The execution ID to look up.

        Returns:
            The tool execution details if found, None otherwise.

        Raises:
            RegistryError: If the lookup fails due to system error.
        """
        ...

    async def get_tool_executions(
        self,
        tool_name: str | None,
        subsystem_id: str | None,
        correlation_id: UUID | None,
        limit: int,
    ) -> list[ProtocolMCPToolExecution]:
        """
        Get a list of tool executions with optional filtering.

        Args:
            tool_name: Optional filter by tool name.
            subsystem_id: Optional filter by executing subsystem.
            correlation_id: Optional filter by correlation ID.
            limit: Maximum number of executions to return.

        Returns:
            List of matching tool executions.

        Raises:
            RegistryError: If the query fails due to system error.
        """
        ...

    async def cancel_tool_execution(self, execution_id: str) -> bool:
        """
        Cancel a running tool execution.

        Args:
            execution_id: The execution ID to cancel.

        Returns:
            True if cancellation was initiated, False if execution not found
            or already completed.

        Raises:
            ExecutionError: If cancellation fails due to system error.
        """
        ...

    async def validate_subsystem_registration(
        self,
        subsystem_metadata: ProtocolMCPSubsystemMetadata,
        tools: list[ProtocolMCPToolDefinition],
    ) -> ProtocolMCPValidationResult:
        """
        Validate a subsystem registration before committing.

        Args:
            subsystem_metadata: The subsystem metadata to validate.
            tools: The tool definitions to validate.

        Returns:
            Validation result with any errors or warnings.
        """
        ...

    async def validate_tool_parameters(
        self, tool_name: str, parameters: dict[str, "ContextValue"]
    ) -> ProtocolValidationResult:
        """
        Validate parameters for a tool before execution.

        Args:
            tool_name: The name of the tool.
            parameters: The parameters to validate.

        Returns:
            Validation result indicating if parameters are valid.

        Raises:
            ToolNotFoundError: If the specified tool is not registered.
        """
        ...

    async def perform_health_check(
        self, registration_id: str
    ) -> ProtocolMCPHealthCheck:
        """
        Perform an active health check on a subsystem.

        Args:
            registration_id: The registration ID of the subsystem to check.

        Returns:
            Health check result with status and diagnostics.

        Raises:
            RegistryError: If the subsystem is not found.
            HealthCheckError: If the health check operation fails.
        """
        ...

    async def get_subsystem_health(
        self, registration_id: str
    ) -> ProtocolMCPHealthCheck | None:
        """
        Get the last known health status for a subsystem.

        Args:
            registration_id: The registration ID of the subsystem.

        Returns:
            The most recent health check result, or None if not found.

        Raises:
            RegistryError: If the lookup fails due to system error.
        """
        ...

    async def cleanup_expired_registrations(self) -> int:
        """
        Remove expired subsystem registrations.

        Returns:
            The number of registrations removed.

        Raises:
            RegistryError: If the cleanup operation fails.
        """
        ...

    async def update_subsystem_configuration(
        self, registration_id: str, configuration: dict[str, "ContextValue"]
    ) -> bool:
        """
        Update configuration for a registered subsystem.

        Args:
            registration_id: The registration ID of the subsystem.
            configuration: New configuration values to merge.

        Returns:
            True if configuration was updated, False if subsystem not found.

        Raises:
            RegistryError: If the update fails due to system error.
            ValidationError: If the configuration values are invalid.
        """
        ...

    async def get_registry_status(self) -> ProtocolMCPRegistryStatus:
        """
        Get the current status of the registry.

        Returns:
            Registry status including health and operational state.

        Raises:
            RegistryError: If status retrieval fails.
        """
        ...

    async def get_registry_metrics(self) -> ProtocolMCPRegistryMetrics:
        """
        Get metrics for the registry.

        Returns:
            Registry metrics including counts and performance data.

        Raises:
            RegistryError: If metrics retrieval fails.
        """
        ...

    # ONEX Node Registration Methods

    async def register_onex_node(
        self,
        contract: "ProtocolContract",
        tags: list[str] | None,
        configuration: dict[str, "ContextValue"] | None,
    ) -> str:
        """
        Register an ONEX node as an MCP tool.

        Converts an ONEX node contract into an MCP tool registration,
        enabling the node to be discovered and executed through the
        MCP protocol infrastructure.

        Args:
            contract: The ONEX node contract to register. Must satisfy
                ProtocolContract interface with valid contract_id and metadata.
            tags: Optional tags for tool discovery and categorization.
                Tags enable filtering during tool discovery operations.
            configuration: Optional configuration overrides for the
                registered tool. Merged with contract defaults.

        Returns:
            Registration ID for the registered tool. Use this ID for
            subsequent operations like unregistration or status queries.

        Raises:
            RegistrationError: If the contract is invalid or registration fails.
            ValidationError: If the contract does not meet MCP tool requirements.
        """
        ...

    async def unregister_onex_node(self, node_id: str) -> bool:
        """
        Unregister an ONEX node from the MCP registry.

        Removes the ONEX node tool registration, making it unavailable
        for discovery and execution through the MCP protocol.

        Args:
            node_id: The node/registration ID to unregister. This should
                be the ID returned from register_onex_node.

        Returns:
            True if successfully unregistered, False if the node was
            not found or could not be unregistered.

        Raises:
            RegistrationError: If unregistration fails due to system error.
        """
        ...

    async def get_onex_node_registration(
        self, node_id: str
    ) -> ProtocolMCPSubsystemRegistration | None:
        """
        Get registration details for an ONEX node.

        Retrieves the full registration information for an ONEX node
        that was registered as an MCP tool.

        Args:
            node_id: The node/registration ID to query. This should
                be the ID returned from register_onex_node.

        Returns:
            The subsystem registration details if found, None if the
            node is not registered or has been unregistered.

        Raises:
            RegistryError: If the registry lookup fails due to system error.
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
        """
        Enable or disable maintenance mode for the registry.

        Args:
            enabled: True to enable maintenance mode, False to disable.

        Returns:
            True if the mode was changed successfully.

        Raises:
            RegistryError: If the operation fails due to system error.
        """
        ...

    async def force_subsystem_cleanup(self, registration_id: str) -> bool:
        """
        Force cleanup of a subsystem registration.

        Args:
            registration_id: The registration ID of the subsystem to clean up.

        Returns:
            True if cleanup was successful, False if subsystem not found.

        Raises:
            RegistryError: If the cleanup operation fails.
        """
        ...

    async def update_registry_configuration(
        self, configuration: dict[str, "ContextValue"]
    ) -> bool:
        """
        Update the registry configuration.

        Args:
            configuration: New configuration values to apply.

        Returns:
            True if configuration was updated successfully.

        Raises:
            ValidationError: If the configuration values are invalid.
            RegistryError: If the update fails due to system error.
        """
        ...

    async def export_registry_state(self) -> dict[str, "ContextValue"]:
        """
        Export the current registry state for backup or migration.

        Returns:
            Dictionary containing the complete registry state.

        Raises:
            RegistryError: If the export operation fails.
        """
        ...

    async def import_registry_state(
        self, state_data: dict[str, "ContextValue"]
    ) -> bool:
        """
        Import registry state from a previous export.

        Args:
            state_data: The registry state data to import.

        Returns:
            True if import was successful.

        Raises:
            ValidationError: If the state data is invalid or corrupted.
            RegistryError: If the import operation fails.
        """
        ...

    async def get_system_diagnostics(self) -> dict[str, "ContextValue"]:
        """
        Get detailed system diagnostics for troubleshooting.

        Returns:
            Dictionary containing diagnostic information.

        Raises:
            RegistryError: If diagnostics retrieval fails.
        """
        ...


@runtime_checkable
class ProtocolMCPRegistryMetricsOperations(Protocol):
    """
    Protocol for advanced MCP registry metrics and analytics.

    Provides detailed performance metrics, trend analysis,
    and operational insights for the registry system.
    """

    async def get_execution_metrics(
        self, time_range_hours: int, tool_name: str | None, subsystem_id: str | None
    ) -> dict[str, "ContextValue"]:
        """
        Get tool execution metrics for a time range.

        Args:
            time_range_hours: Number of hours to look back.
            tool_name: Optional filter by tool name.
            subsystem_id: Optional filter by subsystem.

        Returns:
            Dictionary containing execution metrics including counts,
            latencies, and success rates.

        Raises:
            RegistryError: If metrics retrieval fails.
        """
        ...

    async def get_performance_trends(
        self, metric_name: str, time_range_hours: int
    ) -> dict[str, "ContextValue"]:
        """
        Get performance trends for a specific metric.

        Args:
            metric_name: The name of the metric to analyze.
            time_range_hours: Number of hours to look back.

        Returns:
            Dictionary containing trend data with time series values.

        Raises:
            RegistryError: If trend analysis fails.
            ValidationError: If the metric name is invalid.
        """
        ...

    async def get_error_analysis(
        self, time_range_hours: int
    ) -> dict[str, "ContextValue"]:
        """
        Get error analysis for the registry.

        Args:
            time_range_hours: Number of hours to look back.

        Returns:
            Dictionary containing error statistics, patterns,
            and categorization.

        Raises:
            RegistryError: If error analysis fails.
        """
        ...

    async def get_capacity_metrics(self) -> dict[str, "ContextValue"]:
        """
        Get current capacity metrics for the registry.

        Returns:
            Dictionary containing capacity information including
            current usage, limits, and projections.

        Raises:
            RegistryError: If capacity metrics retrieval fails.
        """
        ...
