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
    def config(self) -> ProtocolMCPRegistryConfig: ...

    async def register_subsystem(
        self,
        subsystem_metadata: ProtocolMCPSubsystemMetadata,
        tools: list[ProtocolMCPToolDefinition],
        api_key: str,
        configuration: dict[str, "ContextValue"] | None,
    ) -> str: ...

    async def unregister_subsystem(self, registration_id: str) -> bool: ...

    async def update_subsystem_heartbeat(
        self,
        registration_id: str,
        health_status: str | None,
        metadata: dict[str, "ContextValue"] | None,
    ) -> bool: ...

    async def get_subsystem_registration(
        self, registration_id: str
    ) -> ProtocolMCPSubsystemRegistration | None: ...

    async def get_all_subsystems(
        self,
        subsystem_type: LiteralMCPSubsystemType | None,
        status_filter: LiteralOperationStatus | None,
    ) -> list[ProtocolMCPSubsystemRegistration]: ...

    async def discover_tools(
        self,
        tool_type: LiteralMCPToolType | None,
        tags: list[str] | None,
        subsystem_id: str | None,
    ) -> list[ProtocolMCPToolDefinition]: ...

    async def get_tool_definition(
        self, tool_name: str
    ) -> ProtocolMCPToolDefinition | None: ...

    async def get_all_tool_implementations(
        self, tool_name: str
    ) -> list[ProtocolMCPToolDefinition]: ...

    async def execute_tool(
        self,
        tool_name: str,
        parameters: dict[str, "ContextValue"],
        correlation_id: UUID,
        timeout_seconds: int | None,
        preferred_subsystem: str | None,
    ) -> dict[str, "ContextValue"]: ...

    async def get_tool_execution(
        self, execution_id: str
    ) -> ProtocolMCPToolExecution | None: ...

    async def get_tool_executions(
        self,
        tool_name: str | None,
        subsystem_id: str | None,
        correlation_id: UUID | None,
        limit: int,
    ) -> list[ProtocolMCPToolExecution]: ...

    async def cancel_tool_execution(self, execution_id: str) -> bool: ...

    async def validate_subsystem_registration(
        self,
        subsystem_metadata: ProtocolMCPSubsystemMetadata,
        tools: list[ProtocolMCPToolDefinition],
    ) -> ProtocolMCPValidationResult: ...

    async def validate_tool_parameters(
        self, tool_name: str, parameters: dict[str, "ContextValue"]
    ) -> ProtocolValidationResult: ...

    async def perform_health_check(
        self, registration_id: str
    ) -> ProtocolMCPHealthCheck: ...

    async def get_subsystem_health(
        self, registration_id: str
    ) -> ProtocolMCPHealthCheck | None: ...

    async def cleanup_expired_registrations(self) -> int: ...

    async def update_subsystem_configuration(
        self, registration_id: str, configuration: dict[str, "ContextValue"]
    ) -> bool: ...

    async def get_registry_status(self) -> ProtocolMCPRegistryStatus: ...

    async def get_registry_metrics(self) -> ProtocolMCPRegistryMetrics: ...


@runtime_checkable
class ProtocolMCPRegistryAdmin(Protocol):
    """
    Administrative protocol for MCP registry management.

    Provides privileged operations for registry administration,
    configuration management, and system maintenance.
    """

    async def set_maintenance_mode(self, enabled: bool) -> bool: ...

    async def force_subsystem_cleanup(self, registration_id: str) -> bool: ...

    async def update_registry_configuration(
        self, configuration: dict[str, "ContextValue"]
    ) -> bool: ...

    async def export_registry_state(self) -> dict[str, "ContextValue"]: ...

    async def import_registry_state(
        self, state_data: dict[str, "ContextValue"]
    ) -> bool: ...

    async def get_system_diagnostics(self) -> dict[str, "ContextValue"]: ...


@runtime_checkable
class ProtocolMCPRegistryMetricsOperations(Protocol):
    """
    Protocol for advanced MCP registry metrics and analytics.

    Provides detailed performance metrics, trend analysis,
    and operational insights for the registry system.
    """

    async def get_execution_metrics(
        self, time_range_hours: int, tool_name: str | None, subsystem_id: str | None
    ) -> dict[str, "ContextValue"]: ...

    async def get_performance_trends(
        self, metric_name: str, time_range_hours: int
    ) -> dict[str, "ContextValue"]: ...

    async def get_error_analysis(
        self, time_range_hours: int
    ) -> dict[str, "ContextValue"]: ...

    async def get_capacity_metrics(self) -> dict[str, "ContextValue"]: ...
