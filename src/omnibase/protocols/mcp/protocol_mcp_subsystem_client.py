#!/usr/bin/env python3
"""
MCP Subsystem Client Protocol - ONEX SPI Interface.

Protocol definition for MCP subsystem client integration.
Enables subsystems to register with and interact with the central MCP registry.

Domain: MCP subsystem integration and client-side operations
"""

from typing import Any, Callable, Optional, Protocol, runtime_checkable
from uuid import UUID

from omnibase.protocols.types.core_types import (
    ContextValue,
    ProtocolDateTime,
    ProtocolValidationResult,
)
from omnibase.protocols.types.mcp_types import (
    MCPConnectionStatus,
    MCPLifecycleState,
    ProtocolMCPHealthCheck,
    ProtocolMCPSubsystemMetadata,
    ProtocolMCPSubsystemRegistration,
    ProtocolMCPToolDefinition,
    ProtocolMCPToolExecution,
)


@runtime_checkable
class ProtocolMCPSubsystemConfig(Protocol):
    """Protocol for MCP subsystem configuration."""

    subsystem_metadata: ProtocolMCPSubsystemMetadata
    registry_url: str
    api_key: str
    heartbeat_interval: int
    tool_definitions: list[ProtocolMCPToolDefinition]
    auto_register: bool
    retry_count: int
    timeout_seconds: int
    health_check_endpoint: str
    configuration: dict[str, ContextValue]


@runtime_checkable
class ProtocolMCPSubsystemClient(Protocol):
    """
    MCP subsystem client protocol for registry integration.

    Provides the client-side interface for subsystems to register with
    and interact with the central MCP registry infrastructure.

    Usage Example:
        ```python
        # Client implementation (not part of SPI)
        class MCPSubsystemClientImpl:
            def __init__(self, config: ProtocolMCPSubsystemConfig):
                self.config = config
                self.registration_id: Optional[str] = None
                self.lifecycle_state = "initializing"
                self.heartbeat_task: Optional[asyncio.Task] = None
                self.tool_handlers: dict[str, Callable] = {}

            async def register_subsystem(self) -> str:
                # Validate configuration
                validation = await self.validate_configuration()
                if not validation.is_valid:
                    raise ValueError(f"Invalid configuration: {validation.errors}")

                # Register with central registry
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.config.registry_url}/api/v1/registry/register",
                        json={
                            "subsystem_metadata": self.config.subsystem_metadata.__dict__,
                            "tools": [tool.__dict__ for tool in self.config.tool_definitions],
                            "api_key": self.config.api_key,
                            "configuration": self.config.configuration
                        },
                        timeout=self.config.timeout_seconds
                    )

                if response.status_code == 201:
                    result = response.json()
                    self.registration_id = result["registration_id"]
                    self.lifecycle_state = "active"

                    # Start heartbeat
                    if self.config.heartbeat_interval > 0:
                        await self.start_heartbeat()

                    return self.registration_id
                else:
                    raise RuntimeError(f"Registration failed: {response.text}")

            async def start_heartbeat(self) -> bool:
                if not self.registration_id:
                    raise ValueError("Must register subsystem before starting heartbeat")

                async def heartbeat_loop():
                    while self.lifecycle_state == "active":
                        try:
                            await self.send_heartbeat()
                            await asyncio.sleep(self.config.heartbeat_interval)
                        except Exception as e:
                            print(f"Heartbeat error: {e}")
                            await asyncio.sleep(self.config.heartbeat_interval * 2)

                self.heartbeat_task = asyncio.create_task(heartbeat_loop())
                return True

            async def send_heartbeat(self) -> bool:
                if not self.registration_id:
                    return False

                # Perform local health check
                health_status = await self.perform_local_health_check()

                async with httpx.AsyncClient() as client:
                    response = await client.put(
                        f"{self.config.registry_url}/api/v1/registry/{self.registration_id}/heartbeat",
                        json={
                            "health_status": health_status.health_status,
                            "metadata": {
                                "lifecycle_state": self.lifecycle_state,
                                "active_tools": len(self.tool_handlers),
                                "uptime_seconds": (datetime.now() - self.start_time).total_seconds()
                            }
                        },
                        headers={"Authorization": f"Bearer {self.config.api_key}"},
                        timeout=self.config.timeout_seconds
                    )

                return response.status_code == 200

            async def register_tool_handler(
                self,
                tool_name: str,
                handler: Callable[[dict[str, ContextValue]], dict[str, Any]]
            ) -> bool:
                # Validate tool is in our definitions
                tool_def = next(
                    (t for t in self.config.tool_definitions if t.name == tool_name),
                    None
                )
                if not tool_def:
                    raise ValueError(f"Tool not found in definitions: {tool_name}")

                self.tool_handlers[tool_name] = handler
                return True

        # Usage in subsystem
        config = SubsystemConfig(
            subsystem_metadata=SubsystemMetadata(
                subsystem_id="data-processor",
                name="Data Processing Service",
                subsystem_type="compute",
                version=SemVer(1, 0, 0),
                description="High-performance data processing tools",
                base_url="http://data-processor:8080",
                health_endpoint="/health",
                documentation_url="http://docs.example.com/data-processor",
                repository_url="http://github.com/org/data-processor",
                maintainer="data-team@example.com",
                tags=["data", "processing", "compute"],
                capabilities=["batch_processing", "stream_processing"],
                dependencies=["database", "message_queue"],
                metadata={"region": "us-east-1", "tier": "production"}
            ),
            registry_url="http://omnimcp:8100",
            api_key="data-processor-key-67890",
            heartbeat_interval=30,
            tool_definitions=[
                ToolDefinition(
                    name="process_batch",
                    tool_type="function",
                    description="Process data batch with specified algorithm",
                    version=SemVer(1, 0, 0),
                    parameters=[
                        ToolParameter(
                            name="batch_id",
                            parameter_type="string",
                            description="ID of batch to process",
                            required=True,
                            default_value=None,
                            schema={"type": "string", "minLength": 1},
                            constraints={"format": "uuid"},
                            examples=["batch-12345"]
                        )
                    ],
                    return_schema={"type": "object", "properties": {"status": {"type": "string"}}},
                    execution_endpoint="/api/v1/process",
                    timeout_seconds=600,
                    retry_count=3,
                    requires_auth=True,
                    tags=["batch", "processing"],
                    metadata={"cpu_intensive": "true"}
                )
            ],
            auto_register=True,
            retry_count=3,
            timeout_seconds=30,
            health_check_endpoint="/health",
            configuration={"max_batch_size": "1000", "parallel_workers": "4"}
        )

        client: ProtocolMCPSubsystemClient = MCPSubsystemClientImpl(config)

        # Register tool handler
        async def handle_process_batch(parameters: dict[str, ContextValue]) -> dict[str, Any]:
            batch_id = parameters["batch_id"]
            # Process batch logic here
            return {"status": "completed", "batch_id": batch_id, "records_processed": 1000}

        await client.register_tool_handler("process_batch", handle_process_batch)

        # Register with registry
        registration_id = await client.register_subsystem()
        print(f"Registered with ID: {registration_id}")

        # Client will automatically send heartbeats
        ```

    Key Features:
        - **Automatic Registration**: Register subsystem and tools with central registry
        - **Heartbeat Management**: Maintain connection with periodic health updates
        - **Tool Handler Registration**: Register local handlers for tool execution
        - **Health Monitoring**: Perform local health checks and report status
        - **Configuration Validation**: Validate subsystem configuration before registration
        - **Error Recovery**: Handle connection failures and retry logic
        - **Lifecycle Management**: Manage subsystem lifecycle states
    """

    @property
    def config(self) -> ProtocolMCPSubsystemConfig:
        """Get subsystem configuration."""
        ...

    @property
    def registration_id(self) -> Optional[str]:
        """Get current registration ID with the registry."""
        ...

    @property
    def lifecycle_state(self) -> MCPLifecycleState:
        """Get current subsystem lifecycle state."""
        ...

    @property
    def connection_status(self) -> MCPConnectionStatus:
        """Get current connection status to registry."""
        ...

    async def register_subsystem(self) -> str:
        """
        Register this subsystem with the central MCP registry.

        Returns:
            Registration ID assigned by the registry

        Raises:
            ValueError: If configuration is invalid
            RuntimeError: If registration fails
        """
        ...

    async def unregister_subsystem(self) -> bool:
        """
        Unregister this subsystem from the registry.

        Returns:
            True if unregistration successful
        """
        ...

    async def start_heartbeat(self, interval: Optional[int] = None) -> bool:
        """
        Start periodic heartbeat to maintain registration.

        Args:
            interval: Optional heartbeat interval override

        Returns:
            True if heartbeat started successfully
        """
        ...

    async def stop_heartbeat(self) -> bool:
        """
        Stop periodic heartbeat.

        Returns:
            True if heartbeat stopped successfully
        """
        ...

    async def send_heartbeat(
        self,
        health_status: Optional[str] = None,
        metadata: Optional[dict[str, ContextValue]] = None,
    ) -> bool:
        """
        Send immediate heartbeat to registry.

        Args:
            health_status: Optional health status override
            metadata: Optional metadata to include

        Returns:
            True if heartbeat sent successfully
        """
        ...

    async def register_tool_handler(
        self,
        tool_name: str,
        handler: Callable[[dict[str, ContextValue]], dict[str, Any]],
    ) -> bool:
        """
        Register a handler function for a tool.

        Args:
            tool_name: Name of the tool
            handler: Async function to handle tool execution

        Returns:
            True if handler registered successfully

        Raises:
            ValueError: If tool not found in configuration
        """
        ...

    async def unregister_tool_handler(self, tool_name: str) -> bool:
        """
        Unregister a tool handler.

        Args:
            tool_name: Name of the tool

        Returns:
            True if handler unregistered successfully
        """
        ...

    async def get_registered_tools(self) -> list[str]:
        """
        Get list of tools with registered handlers.

        Returns:
            List of tool names with active handlers
        """
        ...

    async def execute_tool_locally(
        self,
        tool_name: str,
        parameters: dict[str, ContextValue],
        execution_id: str,
        correlation_id: UUID,
    ) -> dict[str, Any]:
        """
        Execute a tool using local handler.

        Args:
            tool_name: Name of the tool to execute
            parameters: Tool execution parameters
            execution_id: Unique execution identifier
            correlation_id: Request correlation ID

        Returns:
            Tool execution result

        Raises:
            ValueError: If tool handler not found or parameters invalid
            RuntimeError: If execution fails
        """
        ...

    async def validate_configuration(self) -> ProtocolValidationResult:
        """
        Validate subsystem configuration.

        Returns:
            Validation result with any errors or warnings
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

    async def perform_local_health_check(self) -> ProtocolMCPHealthCheck:
        """
        Perform local health check of the subsystem.

        Returns:
            Health check result
        """
        ...

    async def get_subsystem_status(self) -> dict[str, Any]:
        """
        Get current subsystem status and metrics.

        Returns:
            Status information including health, performance, and statistics
        """
        ...

    async def update_configuration(
        self, configuration: dict[str, ContextValue]
    ) -> bool:
        """
        Update subsystem configuration dynamically.

        Args:
            configuration: New configuration values

        Returns:
            True if configuration updated successfully
        """
        ...

    async def get_registration_info(self) -> Optional[ProtocolMCPSubsystemRegistration]:
        """
        Get current registration information from registry.

        Returns:
            Registration information or None if not registered
        """
        ...

    async def test_registry_connection(self) -> bool:
        """
        Test connectivity to the MCP registry.

        Returns:
            True if registry is reachable and responding
        """
        ...

    async def get_tool_execution_history(
        self, tool_name: Optional[str] = None, limit: int = 50
    ) -> list[ProtocolMCPToolExecution]:
        """
        Get local tool execution history.

        Args:
            tool_name: Optional filter by tool name
            limit: Maximum number of results

        Returns:
            List of tool executions handled by this subsystem
        """
        ...

    async def shutdown_gracefully(self, timeout_seconds: int = 30) -> bool:
        """
        Perform graceful shutdown of the subsystem.

        Args:
            timeout_seconds: Maximum time to wait for clean shutdown

        Returns:
            True if shutdown completed successfully
        """
        ...
