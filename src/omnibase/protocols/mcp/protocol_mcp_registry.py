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

    Usage Example:
        ```python
        # Registry implementation (not part of SPI)
        class MCPRegistryImpl:
            def __init__(self, config: ProtocolMCPRegistryConfig):
                self.config = config
                self.subsystems: dict[str, ProtocolMCPSubsystemRegistration] = {}
                self.tools: dict[str, list[ProtocolMCPToolDefinition]] = {}
                self.executions: dict[str, ProtocolMCPToolExecution] = {}
                self.health_checks: dict[str, ProtocolMCPHealthCheck] = {}

            async def register_subsystem(
                self,
                subsystem_metadata: ProtocolMCPSubsystemMetadata,
                tools: list[ProtocolMCPToolDefinition],
                api_key: str
            ) -> str:
                # Validate subsystem metadata and tools
                validation = await self.validate_subsystem_registration(
                    subsystem_metadata, tools
                )
                if not validation.is_valid:
                    raise ValueError(f"Invalid registration: {validation.errors}")

                # Create registration
                registration = MCPSubsystemRegistration(
                    registration_id=f"{subsystem_metadata.subsystem_id}_{uuid4()}",
                    subsystem_metadata=subsystem_metadata,
                    tools=tools,
                    api_key=api_key,
                    registration_status="registered",
                    lifecycle_state="active",
                    connection_status="connected",
                    health_status="healthy",
                    registered_at=datetime.now(),
                    last_heartbeat=datetime.now(),
                    heartbeat_interval_seconds=self.config.default_heartbeat_interval,
                    ttl_seconds=self.config.default_ttl_seconds,
                    access_count=0,
                    error_count=0,
                    last_error=None,
                    configuration={}
                )

                # Store registration
                self.subsystems[registration.registration_id] = registration

                # Index tools
                for tool in tools:
                    if tool.name not in self.tools:
                        self.tools[tool.name] = []
                    self.tools[tool.name].append(tool)

                # Start health monitoring
                await self._schedule_health_check(registration.registration_id)

                return registration.registration_id

            async def execute_tool(
                self,
                tool_name: str,
                parameters: dict[str, ContextValue],
                correlation_id: UUID,
                timeout_seconds: Optional[int] = None
            ) -> dict[str, Any]:
                # Find tool registration
                if tool_name not in self.tools:
                    raise ValueError(f"Tool not found: {tool_name}")

                # Select best available implementation (load balancing)
                tool_def = await self._select_tool_implementation(tool_name)
                subsystem = await self._get_subsystem_for_tool(tool_def)

                # Create execution tracking
                execution = MCPToolExecution(
                    execution_id=str(uuid4()),
                    tool_name=tool_name,
                    subsystem_id=subsystem.subsystem_metadata.subsystem_id,
                    parameters=parameters,
                    execution_status="pending",
                    started_at=datetime.now(),
                    completed_at=None,
                    duration_ms=None,
                    result=None,
                    error_message=None,
                    retry_count=0,
                    correlation_id=correlation_id,
                    metadata={}
                )

                self.executions[execution.execution_id] = execution

                try:
                    # Execute tool via HTTP proxy
                    execution.execution_status = "running"

                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            f"{subsystem.subsystem_metadata.base_url}{tool_def.execution_endpoint}",
                            json={
                                "parameters": parameters,
                                "execution_id": execution.execution_id,
                                "correlation_id": str(correlation_id)
                            },
                            timeout=timeout_seconds or tool_def.timeout_seconds,
                            headers={"Authorization": f"Bearer {subsystem.api_key}"}
                        )

                    result = response.json()
                    execution.result = result
                    execution.execution_status = "completed"
                    execution.completed_at = datetime.now()
                    execution.duration_ms = int(
                        (execution.completed_at - execution.started_at).total_seconds() * 1000
                    )

                    # Update subsystem statistics
                    subsystem.access_count += 1

                    return result

                except Exception as e:
                    execution.execution_status = "failed"
                    execution.error_message = str(e)
                    execution.completed_at = datetime.now()

                    # Update error statistics
                    subsystem.error_count += 1
                    subsystem.last_error = str(e)

                    raise

        # Usage in MCP coordinator
        registry: ProtocolMCPRegistry = MCPRegistryImpl(config)

        # Subsystem registration
        await registry.register_subsystem(
            subsystem_metadata=SubsystemMetadata(
                subsystem_id="analytics-service",
                name="Analytics Service",
                subsystem_type="analytics",
                version=SemVer(1, 0, 0),
                description="Data analytics and processing tools",
                base_url="http://analytics:8080",
                health_endpoint="/health",
                documentation_url="http://docs.example.com/analytics",
                repository_url="http://github.com/org/analytics",
                maintainer="analytics-team@example.com",
                tags=["analytics", "data", "processing"],
                capabilities=["batch_processing", "real_time_analytics"],
                dependencies=["database", "redis"],
                metadata={"region": "us-west-2", "tier": "production"}
            ),
            tools=[
                ToolDefinition(
                    name="analyze_data",
                    tool_type="function",
                    description="Analyze dataset and return insights",
                    version=SemVer(1, 0, 0),
                    parameters=[
                        ToolParameter(
                            name="dataset_id",
                            parameter_type="string",
                            description="ID of dataset to analyze",
                            required=True,
                            default_value=None,
                            schema={"type": "string", "minLength": 1},
                            constraints={"format": "uuid"},
                            examples=["550e8400-e29b-41d4-a716-446655440000"]
                        ),
                        ToolParameter(
                            name="analysis_type",
                            parameter_type="string",
                            description="Type of analysis to perform",
                            required=True,
                            default_value="summary",
                            schema={"type": "string", "enum": ["summary", "detailed", "statistical"]},
                            constraints={"allowed_values": ["summary", "detailed", "statistical"]},
                            examples=["summary", "detailed"]
                        )
                    ],
                    return_schema={"type": "object", "properties": {"insights": {"type": "array"}}},
                    execution_endpoint="/api/v1/analyze",
                    timeout_seconds=300,
                    retry_count=3,
                    requires_auth=True,
                    tags=["analytics", "data-processing"],
                    metadata={"cost_per_execution": "0.05", "memory_intensive": "true"}
                )
            ],
            api_key="analytics-service-key-12345"
        )

        # Tool execution
        result = await registry.execute_tool(
            tool_name="analyze_data",
            parameters={
                "dataset_id": "550e8400-e29b-41d4-a716-446655440000",
                "analysis_type": "detailed"
            },
            correlation_id=uuid4()
        )

        # Registry monitoring
        status = await registry.get_registry_status()
        print(f"Active Subsystems: {status.metrics.active_subsystems}")
        print(f"Total Tools: {status.metrics.total_tools}")
        ```

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
        configuration: Optional[dict[str, ContextValue]] = None,
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
        health_status: Optional[str] = None,
        metadata: Optional[dict[str, ContextValue]] = None,
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
        subsystem_type: Optional[MCPSubsystemType] = None,
        status_filter: Optional[OperationStatus] = None,
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
        tool_type: Optional[MCPToolType] = None,
        tags: Optional[list[str]] = None,
        subsystem_id: Optional[str] = None,
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
        timeout_seconds: Optional[int] = None,
        preferred_subsystem: Optional[str] = None,
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
        time_range_hours: int = 24,
        tool_name: Optional[str] = None,
        subsystem_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Get tool execution metrics for specified time range."""
        ...

    async def get_performance_trends(
        self, metric_name: str, time_range_hours: int = 168
    ) -> dict[str, Any]:
        """Get performance trend data for specified metric."""
        ...

    async def get_error_analysis(self, time_range_hours: int = 24) -> dict[str, Any]:
        """Get error analysis and patterns."""
        ...

    async def get_capacity_metrics(self) -> dict[str, Any]:
        """Get current capacity utilization metrics."""
        ...
