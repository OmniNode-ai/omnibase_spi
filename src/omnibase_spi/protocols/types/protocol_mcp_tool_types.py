"""
MCP Tool and Event Bus types for ONEX SPI interfaces.

Domain: MCP tool definitions, execution, CLI models, and event bus protocols.
"""

from typing import TYPE_CHECKING, Literal, Protocol, runtime_checkable
from uuid import UUID

from omnibase_spi.protocols.types.protocol_core_types import (
    ContextValue,
    ProtocolDateTime,
    ProtocolSemVer,
)

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_mcp_types import (
        ProtocolMCPValidationResult,
    )

LiteralMCPToolType = Literal["function", "resource", "prompt", "sampling", "completion"]
LiteralMCPParameterType = Literal[
    "string", "number", "integer", "boolean", "array", "object"
]
LiteralMCPExecutionStatus = Literal[
    "pending", "running", "completed", "failed", "timeout", "cancelled"
]


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
class ProtocolToolClass(Protocol):
    """Protocol for tool class objects in MCP systems."""

    __name__: str
    __module__: str

    async def __call__(
        self, *args: object, **kwargs: object
    ) -> "ProtocolToolInstance": ...


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
    ) -> "ProtocolMCPValidationResult": ...

    async def health_check(self) -> dict[str, ContextValue]: ...


# CLI Tool Types for ProtocolTool interface
@runtime_checkable
class ProtocolModelResultCLI(Protocol):
    """Protocol for CLI result models."""

    success: bool
    message: str
    data: dict[str, ContextValue] | None
    exit_code: int
    execution_time_ms: int | None
    warnings: list[str]
    errors: list[str]


@runtime_checkable
class ProtocolModelToolArguments(Protocol):
    """Protocol for tool arguments model."""

    tool_name: str
    apply: bool
    verbose: bool
    dry_run: bool
    force: bool
    interactive: bool
    config_path: str | None
    additional_args: dict[str, ContextValue]


@runtime_checkable
class ProtocolModelToolInputData(Protocol):
    """Protocol for tool input data model."""

    tool_name: str
    input_type: str
    data: dict[str, ContextValue]
    metadata: dict[str, ContextValue]
    timestamp: ProtocolDateTime
    correlation_id: UUID | None


@runtime_checkable
class ProtocolModelToolInfo(Protocol):
    """Protocol for tool information model."""

    tool_name: str
    tool_path: str
    contract_path: str
    description: str
    version: ProtocolSemVer
    author: str | None
    tags: list[str]
    capabilities: list[str]
    dependencies: list[str]
    entrypoint: str
    runtime_language: str
    metadata: dict[str, ContextValue]
    is_active: bool
    last_updated: ProtocolDateTime


@runtime_checkable
class ProtocolEventBusConfig(Protocol):
    """Protocol for event bus configuration."""

    bootstrap_servers: list[str]
    topic_prefix: str
    replication_factor: int
    partitions: int
    retention_ms: int
    compression_type: str
    security_protocol: str
    sasl_mechanism: str | None
    sasl_username: str | None
    sasl_password: str | None
    metadata: dict[str, ContextValue]


@runtime_checkable
class ProtocolEventBusBootstrapResult(Protocol):
    """Protocol for event bus bootstrap result."""

    success: bool
    cluster_id: str | None
    controller_id: int | None
    topics_created: list[str]
    errors: list[str]
    warnings: list[str]
    execution_time_ms: int
    bootstrap_config: ProtocolEventBusConfig
    metadata: dict[str, ContextValue]


@runtime_checkable
class ProtocolKafkaHealthCheckResult(Protocol):
    """Protocol for Kafka health check result."""

    cluster_healthy: bool
    cluster_id: str | None
    controller_id: int | None
    broker_count: int
    healthy_brokers: list[int]
    unhealthy_brokers: list[int]
    topic_count: int
    partition_count: int
    under_replicated_partitions: int
    offline_partitions: int
    response_time_ms: int
    errors: list[str]
    warnings: list[str]
    metadata: dict[str, ContextValue]


__all__ = [
    # Literal types
    "LiteralMCPToolType",
    "LiteralMCPParameterType",
    "LiteralMCPExecutionStatus",
    # Tool protocols
    "ProtocolMCPToolParameter",
    "ProtocolMCPToolDefinition",
    "ProtocolMCPToolExecution",
    "ProtocolToolClass",
    "ProtocolToolInstance",
    # CLI model protocols
    "ProtocolModelResultCLI",
    "ProtocolModelToolArguments",
    "ProtocolModelToolInputData",
    "ProtocolModelToolInfo",
    # Event bus protocols
    "ProtocolEventBusConfig",
    "ProtocolEventBusBootstrapResult",
    "ProtocolKafkaHealthCheckResult",
]
