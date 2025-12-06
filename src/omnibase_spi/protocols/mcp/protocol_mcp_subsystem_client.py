"""
MCP Subsystem Client Protocol - ONEX SPI Interface.

Protocol definition for MCP subsystem client integration.
Enables subsystems to register with and interact with the central MCP registry.

Domain: MCP subsystem integration and client-side operations
"""

from collections.abc import Callable
from typing import Protocol, runtime_checkable
from uuid import UUID

from omnibase_spi.protocols.types.protocol_core_types import ContextValue
from omnibase_spi.protocols.types.protocol_mcp_types import (
    LiteralMCPConnectionStatus,
    LiteralMCPLifecycleState,
    ProtocolMCPHealthCheck,
    ProtocolMCPSubsystemMetadata,
    ProtocolMCPSubsystemRegistration,
    ProtocolMCPToolDefinition,
    ProtocolMCPToolExecution,
)
from omnibase_spi.protocols.validation.protocol_validation import (
    ProtocolValidationResult,
)


@runtime_checkable
class ProtocolMCPSubsystemConfig(Protocol):
    """
    Protocol for MCP subsystem configuration.

    Defines the interface for MCP subsystem configuration including registry connection,
    authentication, tool definitions, and operational parameters for subsystem integration.

    Example:
        @runtime_checkable
        class MCPSubsystemConfig(Protocol):
            @property
            def subsystem_metadata(self) -> ProtocolMCPSubsystemMetadata: ...
            @property
            def registry_url(self) -> str: ...
            @property
            def api_key(self) -> str: ...
            @property
            def heartbeat_interval(self) -> int: ...
            @property
            def tool_definitions(self) -> list[ProtocolMCPToolDefinition]: ...
            @property
            def auto_register(self) -> bool: ...
            @property
            def retry_count(self) -> int: ...
            @property
            def timeout_seconds(self) -> int: ...
            @property
            def health_check_endpoint(self) -> str: ...
            @property
            def configuration(self) -> dict[str, ContextValue]: ...

            async def validate_configuration(self) -> bool: ...
            def get_connection_params(self) -> dict[str, ContextValue]: ...
    """

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
    def config(self) -> ProtocolMCPSubsystemConfig: ...

    @property
    def registration_id(self) -> str | None: ...

    @property
    def lifecycle_state(self) -> LiteralMCPLifecycleState: ...

    async def connection_status(self) -> LiteralMCPConnectionStatus: ...

    async def register_subsystem(self) -> str: ...

    async def unregister_subsystem(self) -> bool: ...

    async def start_heartbeat(self, interval: int | None) -> bool: ...

    async def stop_heartbeat(self) -> bool: ...

    async def send_heartbeat(
        self, health_status: str | None, metadata: dict[str, ContextValue] | None
    ) -> bool: ...

    async def register_tool_handler(
        self,
        tool_name: str,
        handler: Callable[[dict[str, ContextValue]], dict[str, ContextValue]],
    ) -> bool: ...

    async def unregister_tool_handler(self, tool_name: str) -> bool: ...

    async def get_registered_tools(self) -> list[str]: ...

    async def execute_tool_locally(
        self,
        tool_name: str,
        parameters: dict[str, ContextValue],
        execution_id: str,
        correlation_id: UUID,
    ) -> dict[str, ContextValue]: ...

    async def validate_configuration(self) -> ProtocolValidationResult: ...

    async def validate_tool_parameters(
        self, tool_name: str, parameters: dict[str, ContextValue]
    ) -> ProtocolValidationResult: ...

    async def perform_local_health_check(self) -> ProtocolMCPHealthCheck: ...

    async def get_subsystem_status(self) -> dict[str, ContextValue]: ...

    async def update_configuration(
        self, configuration: dict[str, "ContextValue"]
    ) -> bool: ...

    async def get_registration_info(
        self,
    ) -> ProtocolMCPSubsystemRegistration | None: ...

    async def test_registry_connection(self) -> bool: ...

    async def get_tool_execution_history(
        self, tool_name: str | None, limit: int
    ) -> list[ProtocolMCPToolExecution]: ...

    async def shutdown_gracefully(self, timeout_seconds: int) -> bool: ...
