"""
MCP (Model Context Protocol) types for ONEX SPI interfaces.

Domain: MCP registry, subsystem, health, and validation protocols.

Note: Tool-related protocols have been moved to protocol_mcp_tool_types.py
and are re-exported here for backward compatibility.
"""

from typing import Literal, Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_core_types import (
    ContextValue,
    LiteralHealthStatus,
    LiteralOperationStatus,
    ProtocolDateTime,
    ProtocolSemVer,
)

# Re-export tool-related protocols for backward compatibility
from omnibase_spi.protocols.types.protocol_mcp_tool_types import (
    LiteralMCPExecutionStatus,
    LiteralMCPParameterType,
    LiteralMCPToolType,
    ProtocolEventBusBootstrapResult,
    ProtocolEventBusConfig,
    ProtocolKafkaHealthCheckResult,
    ProtocolMCPToolDefinition,
    ProtocolMCPToolExecution,
    ProtocolMCPToolParameter,
    ProtocolModelResultCLI,
    ProtocolModelToolArguments,
    ProtocolModelToolInfo,
    ProtocolModelToolInputData,
    ProtocolToolClass,
    ProtocolToolInstance,
)

LiteralMCPSubsystemType = Literal[
    "compute", "storage", "analytics", "integration", "workflow", "ui", "api"
]
LiteralMCPLifecycleState = Literal[
    "initializing", "active", "idle", "busy", "degraded", "shutting_down", "terminated"
]
LiteralMCPConnectionStatus = Literal["connected", "disconnected", "connecting", "error"]


@runtime_checkable
class ProtocolMCPSubsystemMetadata(Protocol):
    """
    Protocol for MCP subsystem metadata defining subsystem identity and capabilities.

    Provides comprehensive metadata about an MCP (Model Context Protocol) subsystem
    including identification, versioning, endpoints, and capability declarations.
    Used for service discovery, registration, and dependency management.

    Attributes:
        subsystem_id: Unique identifier for the subsystem.
        name: Human-readable name of the subsystem.
        subsystem_type: Category of subsystem (compute, storage, etc.).
        version: Semantic version of the subsystem.
        description: Detailed description of subsystem purpose.
        base_url: Base URL for subsystem API endpoints.
        health_endpoint: URL path for health check endpoint.
        documentation_url: Optional URL to subsystem documentation.
        repository_url: Optional URL to source code repository.
        maintainer: Optional name or email of subsystem maintainer.
        tags: List of categorization tags.
        capabilities: List of capabilities this subsystem provides.
        dependencies: List of required dependency subsystem IDs.
        metadata: Additional key-value metadata.

    Example:
        ```python
        class MCPComputeSubsystem:
            '''Compute subsystem for ML inference.'''
            subsystem_id: str = "mcp-compute-v1"
            name: str = "ML Inference Engine"
            subsystem_type: LiteralMCPSubsystemType = "compute"
            version: ProtocolSemVer = SemVer(1, 0, 0)
            description: str = "High-performance ML model inference"
            base_url: str = "https://compute.example.com"
            health_endpoint: str = "/health"
            documentation_url: str | None = "https://docs.example.com"
            repository_url: str | None = None
            maintainer: str | None = "platform-team@example.com"
            tags: list[str] = ["ml", "inference", "gpu"]
            capabilities: list[str] = ["batch_inference", "streaming"]
            dependencies: list[str] = ["mcp-storage-v1"]
            metadata: dict[str, ContextValue] = {}

            async def validate_metadata(self) -> bool:
                return bool(self.subsystem_id and self.name)

        obj = MCPComputeSubsystem()
        assert isinstance(obj, ProtocolMCPSubsystemMetadata)
        ```
    """

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
    """
    Protocol for MCP subsystem registration tracking lifecycle and health status.

    Tracks the complete registration state of an MCP subsystem including
    its metadata, available tools, connection status, health monitoring,
    and operational metrics. Used by the MCP registry for subsystem management.

    Attributes:
        registration_id: Unique identifier for this registration.
        subsystem_metadata: Complete metadata about the registered subsystem.
        tools: List of tools provided by this subsystem.
        api_key: API key for authenticating subsystem requests.
        registration_status: Current status of the registration operation.
        lifecycle_state: Current lifecycle state of the subsystem.
        connection_status: Current connection status to the subsystem.
        health_status: Current health status from health checks.
        registered_at: Timestamp when subsystem was registered.
        last_heartbeat: Timestamp of last received heartbeat.
        heartbeat_interval_seconds: Expected interval between heartbeats.
        ttl_seconds: Time-to-live before registration expires.
        access_count: Number of times subsystem has been accessed.
        error_count: Number of errors encountered.
        last_error: Description of most recent error.
        configuration: Additional configuration key-value pairs.

    Example:
        ```python
        class SubsystemRegistration:
            '''Registration for compute subsystem.'''
            registration_id: str = "reg-12345"
            subsystem_metadata: ProtocolMCPSubsystemMetadata = metadata
            tools: list[ProtocolMCPToolDefinition] = []
            api_key: str = "sk-xxx"
            registration_status: LiteralOperationStatus = "success"
            lifecycle_state: LiteralMCPLifecycleState = "active"
            connection_status: LiteralMCPConnectionStatus = "connected"
            health_status: LiteralHealthStatus = "healthy"
            registered_at: ProtocolDateTime = datetime.now()
            last_heartbeat: ProtocolDateTime | None = datetime.now()
            heartbeat_interval_seconds: int = 30
            ttl_seconds: int = 300
            access_count: int = 0
            error_count: int = 0
            last_error: str | None = None
            configuration: dict[str, ContextValue] = {}

            async def validate_registration(self) -> bool:
                return self.registration_status == "success"

        obj = SubsystemRegistration()
        assert isinstance(obj, ProtocolMCPSubsystemRegistration)
        ```
    """

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
class ProtocolMCPRegistryMetrics(Protocol):
    """
    Protocol for MCP registry metrics providing operational statistics and insights.

    Aggregates comprehensive metrics about the MCP registry including subsystem
    counts, tool statistics, execution metrics, and distribution breakdowns.
    Essential for monitoring, alerting, and capacity planning.

    Attributes:
        total_subsystems: Total number of registered subsystems.
        active_subsystems: Number of currently active subsystems.
        failed_subsystems: Number of subsystems in failed state.
        total_tools: Total number of registered tools across all subsystems.
        active_tools: Number of currently available tools.
        total_executions: Cumulative count of tool executions.
        successful_executions: Number of successful tool executions.
        failed_executions: Number of failed tool executions.
        average_execution_time_ms: Average execution time in milliseconds.
        peak_concurrent_executions: Maximum concurrent executions observed.
        registry_uptime_seconds: Registry uptime in seconds.
        last_cleanup_at: Timestamp of last cleanup operation.
        subsystem_type_distribution: Count of subsystems by type.
        tool_type_distribution: Count of tools by type.
        health_status_distribution: Count of subsystems by health status.
        metadata: Additional metrics metadata.

    Example:
        ```python
        class RegistryMetrics:
            '''Metrics for MCP registry.'''
            total_subsystems: int = 10
            active_subsystems: int = 8
            failed_subsystems: int = 2
            total_tools: int = 50
            active_tools: int = 45
            total_executions: int = 10000
            successful_executions: int = 9800
            failed_executions: int = 200
            average_execution_time_ms: float = 150.5
            peak_concurrent_executions: int = 25
            registry_uptime_seconds: int = 86400
            last_cleanup_at: ProtocolDateTime | None = datetime.now()
            subsystem_type_distribution: dict = {"compute": 5}
            tool_type_distribution: dict = {"query": 30}
            health_status_distribution: dict = {"healthy": 8}
            metadata: dict[str, ContextValue] = {}

            async def validate_metrics(self) -> bool:
                return self.total_subsystems >= 0

        obj = RegistryMetrics()
        assert isinstance(obj, ProtocolMCPRegistryMetrics)
        ```
    """

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
    """
    Protocol for overall MCP registry status and operational state information.

    Provides a complete snapshot of the MCP registry state including its
    operational status, configuration, metrics, and enabled features.
    Used for health monitoring, dashboards, and operational visibility.

    Attributes:
        registry_id: Unique identifier for this registry instance.
        status: Current operational status of the registry.
        message: Human-readable status message.
        version: Semantic version of the registry.
        started_at: Timestamp when registry was started.
        last_updated: Timestamp of last status update.
        metrics: Aggregated registry metrics.
        active_connections: Number of currently active connections.
        configuration: Registry configuration key-value pairs.
        features_enabled: List of enabled feature flags.
        maintenance_mode: Whether registry is in maintenance mode.

    Example:
        ```python
        class RegistryStatus:
            '''Status for MCP registry instance.'''
            registry_id: str = "mcp-registry-prod-1"
            status: LiteralOperationStatus = "success"
            message: str = "Registry operational"
            version: ProtocolSemVer = SemVer(2, 0, 0)
            started_at: ProtocolDateTime = datetime.now()
            last_updated: ProtocolDateTime = datetime.now()
            metrics: ProtocolMCPRegistryMetrics = metrics
            active_connections: int = 15
            configuration: dict[str, ContextValue] = {}
            features_enabled: list[str] = ["caching", "tracing"]
            maintenance_mode: bool = False

            async def validate_status(self) -> bool:
                return self.status in ("success", "pending")

        obj = RegistryStatus()
        assert isinstance(obj, ProtocolMCPRegistryStatus)
        ```
    """

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
    """
    Protocol for MCP registry configuration defining operational parameters.

    Defines all configurable aspects of an MCP registry including capacity
    limits, timing parameters, security settings, and operational modes.
    Used to initialize and reconfigure registry instances.

    Attributes:
        registry_name: Human-readable name for the registry.
        max_subsystems: Maximum number of subsystems allowed.
        max_tools_per_subsystem: Maximum tools per subsystem.
        default_heartbeat_interval: Default heartbeat interval in seconds.
        default_ttl_seconds: Default time-to-live for registrations.
        cleanup_interval_seconds: Interval between cleanup operations.
        max_concurrent_executions: Maximum concurrent tool executions.
        tool_execution_timeout: Timeout for tool execution in seconds.
        health_check_timeout: Timeout for health checks in seconds.
        require_api_key: Whether API key authentication is required.
        enable_metrics: Whether to collect and expose metrics.
        enable_tracing: Whether distributed tracing is enabled.
        log_level: Logging level (debug, info, warn, error).
        maintenance_mode: Whether to start in maintenance mode.
        configuration: Additional configuration key-value pairs.

    Example:
        ```python
        class RegistryConfig:
            '''Configuration for production registry.'''
            registry_name: str = "mcp-registry-prod"
            max_subsystems: int = 100
            max_tools_per_subsystem: int = 50
            default_heartbeat_interval: int = 30
            default_ttl_seconds: int = 300
            cleanup_interval_seconds: int = 60
            max_concurrent_executions: int = 1000
            tool_execution_timeout: int = 30
            health_check_timeout: int = 10
            require_api_key: bool = True
            enable_metrics: bool = True
            enable_tracing: bool = True
            log_level: str = "info"
            maintenance_mode: bool = False
            configuration: dict[str, ContextValue] = {}

            async def validate_config(self) -> bool:
                return self.max_subsystems > 0

        obj = RegistryConfig()
        assert isinstance(obj, ProtocolMCPRegistryConfig)
        ```
    """

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
    """
    Protocol for MCP subsystem health check results with detailed diagnostics.

    Captures the complete result of a health check operation against an
    MCP subsystem including timing, status, individual check results,
    and diagnostic metadata. Used for monitoring and alerting.

    Attributes:
        subsystem_id: ID of the subsystem that was checked.
        check_time: Timestamp when the check was performed.
        health_status: Overall health status (healthy, degraded, unhealthy).
        response_time_ms: Response time of health check in milliseconds.
        status_code: HTTP status code from health endpoint (if applicable).
        status_message: Human-readable status message.
        checks: Individual check results by check name.
        metadata: Additional diagnostic metadata.

    Example:
        ```python
        class HealthCheckResult:
            '''Health check result for compute subsystem.'''
            subsystem_id: str = "mcp-compute-v1"
            check_time: ProtocolDateTime = datetime.now()
            health_status: LiteralHealthStatus = "healthy"
            response_time_ms: int = 45
            status_code: int | None = 200
            status_message: str = "All checks passed"
            checks: dict[str, bool] = {
                "database": True,
                "cache": True,
                "external_api": True
            }
            metadata: dict[str, ContextValue] = {}

            async def validate_health_check(self) -> bool:
                return self.health_status in ("healthy", "degraded")

        obj = HealthCheckResult()
        assert isinstance(obj, ProtocolMCPHealthCheck)
        ```
    """

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
    """
    Protocol for MCP service discovery information enabling dynamic service lookup.

    Provides the essential information needed for service discovery including
    service location, type, available capabilities, and current health status.
    Used by clients to discover and connect to available MCP services.

    Attributes:
        service_name: Human-readable name of the service.
        service_url: URL where the service can be accessed.
        service_type: Type category of the service.
        available_tools: List of tool names available from this service.
        health_status: Current health status of the service.
        last_seen: Timestamp when service was last seen/verified.
        metadata: Additional discovery metadata.

    Example:
        ```python
        class DiscoveryInfo:
            '''Discovery info for analytics service.'''
            service_name: str = "Analytics Engine"
            service_url: str = "https://analytics.example.com"
            service_type: LiteralMCPSubsystemType = "analytics"
            available_tools: list[str] = ["query", "aggregate", "export"]
            health_status: LiteralHealthStatus = "healthy"
            last_seen: ProtocolDateTime = datetime.now()
            metadata: dict[str, ContextValue] = {
                "region": "us-west-2",
                "tier": "premium"
            }

            async def validate_discovery_info(self) -> bool:
                return bool(self.service_url and self.service_name)

        obj = DiscoveryInfo()
        assert isinstance(obj, ProtocolMCPDiscoveryInfo)
        ```
    """

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
    """
    Protocol for MCP validation errors providing detailed error information.

    Captures comprehensive information about a validation error including
    the error type, affected field, detailed message, and suggested fixes.
    Used for input validation and configuration verification.

    Attributes:
        error_type: Category of the validation error.
        field_name: Name of the field that failed validation.
        error_message: Human-readable description of the error.
        invalid_value: The value that failed validation (if safe to expose).
        suggested_fix: Optional suggestion for fixing the error.
        severity: Severity level of the error (error, warning, info).

    Example:
        ```python
        class ValidationError:
            '''Validation error for invalid tool configuration.'''
            error_type: str = "invalid_parameter"
            field_name: str = "timeout_ms"
            error_message: str = "Timeout must be positive"
            invalid_value: ContextValue | None = -100
            suggested_fix: str | None = "Set timeout_ms to a positive integer"
            severity: str = "error"

            async def validate_error(self) -> bool:
                return bool(self.error_type and self.error_message)

        obj = ValidationError()
        assert isinstance(obj, ProtocolMCPValidationError)
        ```
    """

    error_type: str
    field_name: str
    error_message: str
    invalid_value: ContextValue | None
    suggested_fix: str | None
    severity: str

    async def validate_error(self) -> bool: ...


@runtime_checkable
class ProtocolMCPValidationResult(Protocol):
    """
    Protocol for MCP validation results aggregating all validation outcomes.

    Provides a complete validation result including overall validity status,
    lists of errors and warnings, and validation metadata. Used to report
    validation outcomes for configurations, inputs, and registrations.

    Attributes:
        is_valid: Whether validation passed (no errors).
        errors: List of validation errors encountered.
        warnings: List of validation warnings (non-blocking issues).
        validation_time: Timestamp when validation was performed.
        validation_version: Version of the validation schema used.

    Example:
        ```python
        class ValidationResult:
            '''Result of tool configuration validation.'''
            is_valid: bool = False
            errors: list[ProtocolMCPValidationError] = [timeout_error]
            warnings: list[ProtocolMCPValidationError] = []
            validation_time: ProtocolDateTime = datetime.now()
            validation_version: ProtocolSemVer = SemVer(1, 0, 0)

            async def validate_validation_result(self) -> bool:
                return not self.is_valid or len(self.errors) == 0

        obj = ValidationResult()
        assert isinstance(obj, ProtocolMCPValidationResult)
        ```
    """

    is_valid: bool
    errors: list[ProtocolMCPValidationError]
    warnings: list[ProtocolMCPValidationError]
    validation_time: ProtocolDateTime
    validation_version: ProtocolSemVer

    async def validate_validation_result(self) -> bool: ...


__all__ = [
    "LiteralMCPConnectionStatus",
    "LiteralMCPExecutionStatus",
    "LiteralMCPLifecycleState",
    "LiteralMCPParameterType",
    # Literal types (local)
    "LiteralMCPSubsystemType",
    # Re-exported from protocol_mcp_tool_types for backward compatibility
    "LiteralMCPToolType",
    "ProtocolEventBusBootstrapResult",
    "ProtocolEventBusConfig",
    "ProtocolKafkaHealthCheckResult",
    "ProtocolMCPDiscoveryInfo",
    # Health and discovery protocols
    "ProtocolMCPHealthCheck",
    "ProtocolMCPRegistryConfig",
    # Registry protocols
    "ProtocolMCPRegistryMetrics",
    "ProtocolMCPRegistryStatus",
    # Subsystem protocols
    "ProtocolMCPSubsystemMetadata",
    "ProtocolMCPSubsystemRegistration",
    "ProtocolMCPToolDefinition",
    "ProtocolMCPToolExecution",
    "ProtocolMCPToolParameter",
    # Validation protocols
    "ProtocolMCPValidationError",
    "ProtocolMCPValidationResult",
    "ProtocolModelResultCLI",
    "ProtocolModelToolArguments",
    "ProtocolModelToolInfo",
    "ProtocolModelToolInputData",
    "ProtocolToolClass",
    "ProtocolToolInstance",
]
