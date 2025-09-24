"""
Core protocol types for ONEX SPI interfaces.

Domain: Core system protocols (logging, serialization, validation)
"""

from datetime import datetime
from typing import Literal, Optional, Protocol, runtime_checkable
from uuid import UUID


# Semantic version protocol - for strong version typing
@runtime_checkable
class ProtocolSemVer(Protocol):
    """Protocol for semantic version objects."""

    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        """Return string representation (e.g., '1.2.3')."""
        ...


# Datetime protocol alias - ensures consistent datetime usage
ProtocolDateTime = datetime

# Log level types - using string literals instead of enums (includes FATAL for error severity)
LogLevel = Literal["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "FATAL"]

# Node-related types - using string literals for SPI purity
NodeType = Literal["COMPUTE", "EFFECT", "REDUCER", "ORCHESTRATOR"]
HealthStatus = Literal[
    "healthy",
    "degraded",
    "unhealthy",
    "critical",
    "unknown",
    "warning",
    "unreachable",
    "available",
    "unavailable",
    "initializing",
    "disposing",
    "error",
]

# Context value types - specific typed values for logging context
ContextValue = str | int | float | bool | list[str] | dict[str, str]


# Metadata types - for metadata storage protocols
@runtime_checkable
class ProtocolSupportedMetadataType(Protocol):
    """Protocol for types that can be stored in metadata."""

    def __str__(self) -> str:
        """Must be convertible to string."""
        ...


# Configuration value protocol - for type-safe configuration
class ProtocolConfigValue(Protocol):
    """Protocol for configuration values - attribute-based for data compatibility."""

    key: str
    value: ContextValue
    config_type: Literal["string", "int", "float", "bool", "list"]
    default_value: Optional[ContextValue]


# Core logging protocols
class ProtocolLogContext(Protocol):
    """Protocol for log context objects."""

    def to_dict(self) -> dict[str, ContextValue]:
        """Convert context to dictionary with typed values."""
        ...


@runtime_checkable
class ProtocolLogEntry(Protocol):
    """Protocol for log entry objects."""

    level: LogLevel
    message: str
    correlation_id: UUID
    timestamp: ProtocolDateTime
    context: dict[str, ContextValue]


# Core serialization protocols
class ProtocolSerializationResult(Protocol):
    """Protocol for serialization results."""

    success: bool
    data: str
    error_message: str | None


# Core node protocols
class ProtocolNodeMetadata(Protocol):
    """Protocol for node metadata objects."""

    node_id: str
    node_type: str
    metadata: dict[str, ContextValue]


# Core validation protocols
class ProtocolValidationResult(Protocol):
    """Protocol for validation results."""

    is_valid: bool
    errors: list[str]
    warnings: list[str]


# Cache service protocols
@runtime_checkable
class ProtocolCacheStatistics(Protocol):
    """Protocol for structured cache service statistics."""

    hit_count: int
    miss_count: int
    total_requests: int
    hit_ratio: float
    memory_usage_bytes: int
    entry_count: int
    eviction_count: int
    last_accessed: Optional[datetime]
    cache_size_limit: Optional[int]


# Base status types - consolidated from multiple duplicates
BaseStatus = Literal[
    "pending", "processing", "completed", "failed", "cancelled", "skipped"
]

# Domain-specific status types
NodeStatus = Literal["active", "inactive", "error", "pending"]

# Execution types - using string literals for SPI purity
ExecutionMode = Literal["direct", "inmemory", "kafka"]
OperationStatus = Literal["success", "failed", "in_progress", "cancelled", "pending"]

# Validation types - using string literals for SPI purity (ErrorSeverity consolidated into LogLevel)
# Use LogLevel for error severity instead of separate ErrorSeverity type
ValidationLevel = Literal["BASIC", "STANDARD", "COMPREHENSIVE", "PARANOID"]
ValidationMode = Literal["strict", "lenient", "smoke", "regression", "integration"]


# Metadata protocols for type safety
@runtime_checkable
class ProtocolMetadata(Protocol):
    """Protocol for structured metadata - attribute-based for data compatibility."""

    data: dict[str, ContextValue]
    version: ProtocolSemVer
    created_at: ProtocolDateTime
    updated_at: Optional[ProtocolDateTime]


# Behavior protocols for operations (method-based)
class ProtocolMetadataOperations(Protocol):
    """Protocol for metadata operations - method-based for services."""

    def get_value(self, key: str) -> ContextValue: ...

    def has_key(self, key: str) -> bool: ...

    def keys(self) -> list[str]: ...

    def update_value(self, key: str, value: ContextValue) -> None: ...


# Reducer protocol types with stronger typing
class ProtocolActionPayload(Protocol):
    """Protocol for action payload with specific data."""

    target_id: str
    operation: str
    parameters: dict[str, ContextValue]


class ProtocolAction(Protocol):
    """Protocol for reducer actions."""

    type: str
    payload: ProtocolActionPayload
    timestamp: ProtocolDateTime


class ProtocolState(Protocol):
    """Protocol for reducer state."""

    metadata: ProtocolMetadata
    version: int  # This is a sequence number, not semver
    last_updated: ProtocolDateTime


# Schema and node metadata protocols
class ProtocolNodeMetadataBlock(Protocol):
    """Protocol for node metadata block objects."""

    uuid: str
    name: str
    description: str
    version: ProtocolSemVer
    metadata_version: ProtocolSemVer
    namespace: str
    created_at: ProtocolDateTime
    last_modified_at: ProtocolDateTime
    lifecycle: str
    protocol_version: ProtocolSemVer


class ProtocolSchemaObject(Protocol):
    """Protocol for schema data objects."""

    schema_id: str
    schema_type: str
    schema_data: dict[str, ContextValue]
    version: ProtocolSemVer
    is_valid: bool


# Workflow result protocols for enhanced reducer support
class ProtocolErrorInfo(Protocol):
    """Protocol for error information in results."""

    error_type: str
    message: str
    trace: Optional[str]
    retryable: bool
    backoff_strategy: Optional[str]
    max_attempts: Optional[int]


class ProtocolSystemEvent(Protocol):
    """Protocol for system events."""

    type: str
    payload: dict[str, ContextValue]
    timestamp: float
    source: str


class ProtocolNodeResult(Protocol):
    """Protocol for node processing results with monadic composition."""

    value: Optional[ContextValue]
    is_success: bool
    is_failure: bool
    error: Optional[ProtocolErrorInfo]
    trust_score: float
    provenance: list[str]
    metadata: dict[str, ContextValue]
    events: list[ProtocolSystemEvent]
    state_delta: dict[str, ContextValue]


# Service Discovery Types
class ProtocolServiceMetadata(Protocol):
    """Protocol for service metadata."""

    data: dict[str, ContextValue]
    version: ProtocolSemVer
    capabilities: list[str]
    tags: list[str]


class ProtocolServiceInstance(Protocol):
    """Protocol for service instance information."""

    service_id: str
    service_name: str
    host: str
    port: int
    metadata: ProtocolServiceMetadata
    health_status: HealthStatus
    last_seen: ProtocolDateTime


class ProtocolServiceHealthStatus(Protocol):
    """Protocol for service health status."""

    service_id: str
    status: HealthStatus
    last_check: ProtocolDateTime
    details: dict[str, ContextValue]


# Node Configuration Types
class ProtocolNodeConfiguration(Protocol):
    """Protocol for node configuration information."""

    name: str
    version: ProtocolSemVer
    node_type: NodeType
    dependencies: list[str]
    capabilities: list[str]
    runtime_requirements: dict[str, ContextValue]
    metadata: dict[str, ContextValue]


# Storage Backend Types
class ProtocolCheckpointData(Protocol):
    """Protocol for checkpoint data."""

    checkpoint_id: str
    workflow_id: str
    data: dict[str, ContextValue]
    timestamp: ProtocolDateTime
    metadata: dict[str, ContextValue]


class ProtocolStorageCredentials(Protocol):
    """Protocol for storage credentials."""

    credential_type: str
    data: dict[str, str]


class ProtocolStorageConfiguration(Protocol):
    """Protocol for storage configuration."""

    backend_type: str
    connection_string: str
    options: dict[str, ContextValue]
    timeout_seconds: int


class ProtocolStorageResult(Protocol):
    """Protocol for storage operation results."""

    success: bool
    data: dict[str, ContextValue] | None
    error_message: str | None
    operation_id: str


class ProtocolStorageListResult(Protocol):
    """Protocol for storage list operation results."""

    success: bool
    items: list[dict[str, ContextValue]]
    total_count: int
    has_more: bool
    error_message: str | None


class ProtocolStorageHealthStatus(Protocol):
    """Protocol for storage health status."""

    is_healthy: bool
    status_details: dict[str, ContextValue]
    capacity_info: dict[str, int] | None
    last_check: ProtocolDateTime


# Standardized Error Handling Types
ErrorRecoveryStrategy = Literal[
    "retry", "fallback", "abort", "circuit_breaker", "compensation"
]
ErrorSeverity = Literal["low", "medium", "high", "critical"]


class ProtocolErrorContext(Protocol):
    """Protocol for error context information."""

    correlation_id: UUID
    operation_name: str
    timestamp: ProtocolDateTime
    context_data: dict[str, ContextValue]
    stack_trace: str | None


class ProtocolRecoveryAction(Protocol):
    """Protocol for error recovery action information."""

    action_type: ErrorRecoveryStrategy
    max_attempts: int
    backoff_multiplier: float
    timeout_seconds: int
    fallback_value: ContextValue | None


class ProtocolErrorResult(Protocol):
    """Protocol for standardized error results."""

    error_id: UUID
    error_type: str
    message: str
    severity: ErrorSeverity
    retryable: bool
    recovery_action: ProtocolRecoveryAction | None
    context: ProtocolErrorContext


# Protocol Versioning and Metadata Types
class ProtocolVersionInfo(Protocol):
    """Protocol for version metadata."""

    protocol_name: str
    version: ProtocolSemVer
    compatibility_version: ProtocolSemVer
    retirement_date: ProtocolDateTime | None
    migration_guide_url: str | None


class ProtocolCompatibilityCheck(Protocol):
    """Protocol for compatibility checking results."""

    is_compatible: bool
    required_version: ProtocolSemVer
    current_version: ProtocolSemVer
    breaking_changes: list[str]
    migration_required: bool


# Standardized Health Check Types
HealthCheckLevel = Literal["quick", "basic", "standard", "thorough", "comprehensive"]
HealthDimension = Literal[
    "availability", "performance", "functionality", "data_integrity", "security"
]


# Marker Interfaces for Type Compatibility
@runtime_checkable
class ProtocolNodeInfoLike(Protocol):
    """
    Protocol for objects that can provide node information.

    This protocol defines the minimal interface that objects
    must implement to be compatible with node metadata processing.
    Objects implementing this protocol can be converted to
    ModelNodeMetadataInfo instances.

    This is a marker interface - no methods required.
    """

    pass


@runtime_checkable
class ProtocolSupportedPropertyValue(Protocol):
    """
    Protocol for values that can be stored as property values.

    This protocol defines the minimal interface that property values
    must implement to be compatible with the ONEX property system.
    Any type implementing this protocol can be used as a property value.

    This is a marker interface - no methods required.
    """

    pass


class ProtocolHealthMetrics(Protocol):
    """Protocol for health check metrics."""

    response_time_ms: float
    cpu_usage_percent: float
    memory_usage_percent: float
    disk_usage_percent: float
    connection_count: int
    error_rate_percent: float
    throughput_per_second: float


class ProtocolHealthCheck(Protocol):
    """Protocol for standardized health checks."""

    service_name: str
    check_level: HealthCheckLevel
    dimensions_checked: list[HealthDimension]
    overall_status: HealthStatus
    individual_checks: dict[str, HealthStatus]
    metrics: ProtocolHealthMetrics
    check_duration_ms: float
    timestamp: ProtocolDateTime
    recommendations: list[str]


class ProtocolHealthMonitoring(Protocol):
    """Protocol for health monitoring configuration."""

    check_interval_seconds: int
    timeout_seconds: int
    failure_threshold: int
    recovery_threshold: int
    alert_on_status: list[HealthStatus]
    escalation_rules: dict[str, ContextValue]


# Observability and Monitoring Types
class ProtocolMetricsPoint(Protocol):
    """Protocol for individual metrics points."""

    metric_name: str
    value: float
    unit: str
    timestamp: ProtocolDateTime
    tags: dict[str, str]
    dimensions: dict[str, ContextValue]


class ProtocolTraceSpan(Protocol):
    """Protocol for distributed tracing spans."""

    span_id: UUID
    trace_id: UUID
    parent_span_id: UUID | None
    operation_name: str
    start_time: ProtocolDateTime
    end_time: ProtocolDateTime | None
    status: OperationStatus
    tags: dict[str, str]
    logs: list[dict[str, ContextValue]]


class ProtocolAuditEvent(Protocol):
    """Protocol for audit events."""

    event_id: UUID
    event_type: str
    actor: str
    resource: str
    action: str
    timestamp: ProtocolDateTime
    outcome: OperationStatus
    metadata: dict[str, ContextValue]
    sensitivity_level: Literal["public", "internal", "confidential", "restricted"]


# General Purpose Protocols for Type Constraints


@runtime_checkable
class ProtocolSerializable(Protocol):
    """Protocol for objects that can be serialized to dict."""

    def model_dump(
        self,
    ) -> dict[
        str,
        str
        | int
        | float
        | bool
        | list[str | int | float | bool]
        | dict[str, str | int | float | bool],
    ]:
        """Serialize to dictionary."""
        ...


@runtime_checkable
class ProtocolIdentifiable(Protocol):
    """Protocol for objects that have an ID."""

    @property
    def id(self) -> str:
        """Get the object ID."""
        ...


@runtime_checkable
class ProtocolNameable(Protocol):
    """Protocol for objects that have a name."""

    @property
    def name(self) -> str:
        """Get the object name."""
        ...


@runtime_checkable
class ProtocolValidatable(Protocol):
    """Protocol for objects that can be validated."""

    def is_valid(self) -> bool:
        """Check if the object is valid."""
        ...


@runtime_checkable
class ProtocolConfigurable(Protocol):
    """Protocol for objects that can be configured."""

    def configure(self, **kwargs: ContextValue) -> None:
        """Configure the object with parameters."""
        ...


@runtime_checkable
class ProtocolExecutable(Protocol):
    """Protocol for objects that can be executed."""

    def execute(self) -> object:
        """Execute the object."""
        ...


@runtime_checkable
class ProtocolMetadataProvider(Protocol):
    """Protocol for objects that provide metadata."""

    def get_metadata(self) -> dict[str, str | int | bool | float]:
        """Get metadata dictionary."""
        ...
