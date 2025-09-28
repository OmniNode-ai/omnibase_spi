"""
MCP (Model Context Protocol) types for ONEX SPI interfaces.

Domain: MCP tool registration and coordination protocols
"""

from typing import TYPE_CHECKING, Any, Literal, Optional, Protocol, runtime_checkable
from uuid import UUID

from omnibase_spi.protocols.types.protocol_core_types import (
    ContextValue,
    LiteralHealthStatus,
    LiteralOperationStatus,
    ProtocolDateTime,
    ProtocolSemVer,
)

if TYPE_CHECKING:
    pass
LiteralMCPToolType = Literal["function", "resource", "prompt", "sampling", "completion"]
LiteralMCPParameterType = Literal[
    "string", "number", "integer", "boolean", "array", "object"
]
LiteralMCPExecutionStatus = Literal[
    "pending", "running", "completed", "failed", "timeout", "cancelled"
]
LiteralMCPSubsystemType = Literal[
    "compute", "storage", "analytics", "integration", "workflow", "ui", "api"
]
LiteralMCPLifecycleState = Literal[
    "initializing", "active", "idle", "busy", "degraded", "shutting_down", "terminated"
]
LiteralMCPConnectionStatus = Literal["connected", "disconnected", "connecting", "error"]


@runtime_checkable
class ProtocolMCPToolParameter(Protocol):
    """Protocol for MCP tool parameter definition."""

    name: str
    parameter_type: LiteralMCPParameterType
    description: str
    required: bool
    default_value: ContextValue | None
    schema: dict[str, ContextValue] | None
    constraints: dict[str, ContextValue]
    examples: list[ContextValue]

    async def validate_parameter(self) -> bool: ...

    def is_required_parameter(self) -> bool: ...


@runtime_checkable
class ProtocolMCPToolDefinition(Protocol):
    """Protocol for MCP tool definition."""

    name: str
    tool_type: LiteralMCPToolType
    description: str
    version: ProtocolSemVer
    parameters: list[ProtocolMCPToolParameter]
    return_schema: dict[str, ContextValue] | None
    execution_endpoint: str
    timeout_seconds: int
    retry_count: int
    requires_auth: bool
    tags: list[str]
    metadata: dict[str, ContextValue]

    async def validate_tool_definition(self) -> bool: ...


@runtime_checkable
class ProtocolMCPSubsystemMetadata(Protocol):
    """Protocol for MCP subsystem metadata."""

    subsystem_id: str
    name: str
    subsystem_type: LiteralMCPSubsystemType
    version: ProtocolSemVer
    description: str
    base_url: str
    health_endpoint: str
    documentation_url: str | None
    repository_url: str | None
    maintainer: str | None
    tags: list[str]
    capabilities: list[str]
    dependencies: list[str]
    metadata: dict[str, ContextValue]

    async def validate_metadata(self) -> bool: ...


@runtime_checkable
class ProtocolMCPSubsystemRegistration(Protocol):
    """Protocol for MCP subsystem registration information."""

    registration_id: str
    subsystem_metadata: "ProtocolMCPSubsystemMetadata"
    tools: list["ProtocolMCPToolDefinition"]
    api_key: str
    registration_status: LiteralOperationStatus
    lifecycle_state: LiteralMCPLifecycleState
    connection_status: LiteralMCPConnectionStatus
    health_status: LiteralHealthStatus
    registered_at: ProtocolDateTime
    last_heartbeat: ProtocolDateTime | None
    heartbeat_interval_seconds: int
    ttl_seconds: int
    access_count: int
    error_count: int
    last_error: str | None
    configuration: dict[str, "ContextValue"]

    async def validate_registration(self) -> bool: ...


@runtime_checkable
class ProtocolMCPToolExecution(Protocol):
    """Protocol for MCP tool execution tracking."""

    execution_id: str
    tool_name: str
    subsystem_id: str
    parameters: dict[str, "ContextValue"]
    execution_status: LiteralMCPExecutionStatus
    started_at: ProtocolDateTime
    completed_at: ProtocolDateTime | None
    duration_ms: int | None
    result: dict[str, ContextValue] | None
    error_message: str | None
    retry_count: int
    correlation_id: UUID
    metadata: dict[str, ContextValue]

    async def validate_execution(self) -> bool: ...


@runtime_checkable
class ProtocolMCPRegistryMetrics(Protocol):
    """Protocol for MCP registry metrics and statistics."""

    total_subsystems: int
    active_subsystems: int
    failed_subsystems: int
    total_tools: int
    active_tools: int
    total_executions: int
    successful_executions: int
    failed_executions: int
    average_execution_time_ms: float
    peak_concurrent_executions: int
    registry_uptime_seconds: int
    last_cleanup_at: ProtocolDateTime | None
    subsystem_type_distribution: dict[LiteralMCPSubsystemType, int]
    tool_type_distribution: dict[LiteralMCPToolType, int]
    health_status_distribution: dict[LiteralHealthStatus, int]
    metadata: dict[str, ContextValue]

    async def validate_metrics(self) -> bool: ...


@runtime_checkable
class ProtocolMCPRegistryStatus(Protocol):
    """Protocol for overall MCP registry status."""

    registry_id: str
    status: LiteralOperationStatus
    message: str
    version: ProtocolSemVer
    started_at: ProtocolDateTime
    last_updated: ProtocolDateTime
    metrics: "ProtocolMCPRegistryMetrics"
    active_connections: int
    configuration: dict[str, "ContextValue"]
    features_enabled: list[str]
    maintenance_mode: bool

    async def validate_status(self) -> bool: ...


@runtime_checkable
class ProtocolMCPRegistryConfig(Protocol):
    """Protocol for MCP registry configuration."""

    registry_name: str
    max_subsystems: int
    max_tools_per_subsystem: int
    default_heartbeat_interval: int
    default_ttl_seconds: int
    cleanup_interval_seconds: int
    max_concurrent_executions: int
    tool_execution_timeout: int
    health_check_timeout: int
    require_api_key: bool
    enable_metrics: bool
    enable_tracing: bool
    log_level: str
    maintenance_mode: bool
    configuration: dict[str, "ContextValue"]

    async def validate_config(self) -> bool: ...


@runtime_checkable
class ProtocolMCPHealthCheck(Protocol):
    """Protocol for MCP subsystem health check result."""

    subsystem_id: str
    check_time: ProtocolDateTime
    health_status: LiteralHealthStatus
    response_time_ms: int
    status_code: int | None
    status_message: str
    checks: dict[str, bool]
    metadata: dict[str, ContextValue]

    async def validate_health_check(self) -> bool: ...


@runtime_checkable
class ProtocolMCPDiscoveryInfo(Protocol):
    """Protocol for MCP service discovery information."""

    service_name: str
    service_url: str
    service_type: LiteralMCPSubsystemType
    available_tools: list[str]
    health_status: LiteralHealthStatus
    last_seen: ProtocolDateTime
    metadata: dict[str, ContextValue]

    async def validate_discovery_info(self) -> bool: ...


@runtime_checkable
class ProtocolMCPValidationError(Protocol):
    """Protocol for MCP validation errors."""

    error_type: str
    field_name: str
    error_message: str
    invalid_value: ContextValue | None
    suggested_fix: str | None
    severity: str

    async def validate_error(self) -> bool: ...


@runtime_checkable
class ProtocolMCPValidationResult(Protocol):
    """Protocol for MCP validation results."""

    is_valid: bool
    errors: list[ProtocolMCPValidationError]
    warnings: list[ProtocolMCPValidationError]
    validation_time: ProtocolDateTime
    validation_version: ProtocolSemVer

    async def validate_validation_result(self) -> bool: ...


@runtime_checkable
class ProtocolToolClass(Protocol):
    """Protocol for tool class objects in MCP systems."""

    __name__: str
    __module__: str

    def __call__(self, *args: object, **kwargs: object) -> "ProtocolToolInstance": ...


@runtime_checkable
class ProtocolToolInstance(Protocol):
    """Protocol for tool instance objects in MCP systems."""

    tool_name: str
    tool_version: ProtocolSemVer
    tool_type: LiteralMCPToolType
    is_initialized: bool

    async def execute(
        self, parameters: dict[str, ContextValue]
    ) -> dict[str, ContextValue]: ...

    async def validate_parameters(
        self, parameters: dict[str, ContextValue]
    ) -> ProtocolMCPValidationResult: ...

    async def health_check(self) -> dict[str, ContextValue]: ...
