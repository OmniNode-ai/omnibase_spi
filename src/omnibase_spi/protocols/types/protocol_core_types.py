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
    """
    Protocol for semantic version objects following SemVer specification.

    Provides a structured approach to versioning with major, minor, and patch
    components. Used throughout ONEX for protocol versioning, dependency
    management, and compatibility checking.

    Key Features:
        - Major version: Breaking changes
        - Minor version: Backward-compatible additions
        - Patch version: Backward-compatible fixes
        - String representation: "major.minor.patch" format

    Usage:
        version = some_protocol_object.version
        if version.major >= 2:
            # Use new API features
        compatibility_string = str(version)  # "2.1.3"
    """

    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        """Return string representation in 'major.minor.patch' format (e.g., '1.2.3')."""
        ...


# Datetime protocol alias - ensures consistent datetime usage
ProtocolDateTime = datetime

# Log level types - comprehensive logging levels for observability
# TRACE: Finest-grained debug information
# DEBUG: Detailed diagnostic information
# INFO: General informational messages
# WARNING: Warning conditions that don't prevent operation
# ERROR: Error conditions that affect specific operations
# CRITICAL: Critical conditions that may affect system stability
# FATAL: Fatal errors that cause service termination
LiteralLogLevel = Literal[
    "TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "FATAL"
]

# Node-related types - ONEX 4-node architecture types
# COMPUTE: Data processing and business logic nodes
# EFFECT: External interaction and I/O operations
# REDUCER: State management and data consolidation
# ORCHESTRATOR: Workflow coordination and process management
LiteralNodeType = Literal["COMPUTE", "EFFECT", "REDUCER", "ORCHESTRATOR"]

# Health status types - comprehensive health states for monitoring
# healthy: Normal operation, all systems functional
# degraded: Reduced functionality but still operational
# unhealthy: Significant issues affecting operation
# critical: Severe issues requiring immediate attention
# unknown: Health status cannot be determined
# warning: Minor issues that should be monitored
# unreachable: Service cannot be contacted
# available: Service is reachable and ready
# unavailable: Service is temporarily not available
# initializing: Service is starting up
# disposing: Service is shutting down
# error: Service is in an error state
LiteralHealthStatus = Literal[
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

# === Context Value Protocol Hierarchy (Eliminates Union anti-patterns) ===


@runtime_checkable
class ProtocolContextValue(Protocol):
    """Protocol for context data values supporting validation and serialization."""

    def validate_for_context(self) -> bool:
        """Validate value is safe for context storage."""
        ...

    def serialize_for_context(self) -> dict[str, object]:
        """Serialize value for context persistence."""
        ...

    def get_context_type_hint(self) -> str:
        """Get type hint for context schema validation."""
        ...


@runtime_checkable
class ProtocolContextStringValue(ProtocolContextValue, Protocol):
    """Protocol for string-based context values (text data, identifiers, messages)."""

    value: str


@runtime_checkable
class ProtocolContextNumericValue(ProtocolContextValue, Protocol):
    """Protocol for numeric context values (identifiers, counts, measurements, scores)."""

    value: int | float


@runtime_checkable
class ProtocolContextBooleanValue(ProtocolContextValue, Protocol):
    """Protocol for boolean context values (flags, status indicators)."""

    value: bool


@runtime_checkable
class ProtocolContextStringListValue(ProtocolContextValue, Protocol):
    """Protocol for string list context values (identifiers, tags, categories)."""

    value: list[str]


@runtime_checkable
class ProtocolContextStringDictValue(ProtocolContextValue, Protocol):
    """Protocol for string dictionary context values (key-value mappings, structured data)."""

    value: dict[str, str]


# Backward compatibility alias - use ProtocolContextValue for new code
ContextValue = ProtocolContextValue


# Metadata types - for metadata storage protocols
@runtime_checkable
class ProtocolSupportedMetadataType(Protocol):
    """
    Protocol for types that can be stored in ONEX metadata systems.

    This marker protocol defines the contract for objects that can be safely
    stored, serialized, and retrieved from metadata storage systems. Objects
    implementing this protocol guarantee string convertibility for persistence.

    Key Features:
        - Marker interface for metadata compatibility
        - String conversion guarantee
        - Runtime type checking support
        - Safe for serialization/deserialization

    Usage:
        def store_metadata(key: str, value: ProtocolSupportedMetadataType):
            metadata_store[key] = str(value)
    """

    __omnibase_metadata_type_marker__: Literal[True]

    def __str__(self) -> str:
        """Convert to string representation for persistence and display."""
        ...


# Configuration value protocol - for type-safe configuration
@runtime_checkable
class ProtocolConfigValue(Protocol):
    """
    Protocol for type-safe configuration values in ONEX systems.

    Provides structured configuration management with type enforcement,
    default value handling, and validation support. Used for service
    configuration, node parameters, and runtime settings.

    Key Features:
        - Typed configuration values (string, int, float, bool, list)
        - Default value support for fallback behavior
        - Key-value structure for configuration management
        - Type validation and conversion support

    Usage:
        config = ProtocolConfigValue(
            key="max_retries",
            value=3,
            config_type="int",
            default_value=1
        )
    """

    key: str
    value: ContextValue
    config_type: Literal["string", "int", "float", "bool", "list"]
    default_value: Optional[ContextValue]


# Core logging protocols
class ProtocolLogContext(Protocol):
    """
    Protocol for structured logging context objects.

    Provides standardized context information for distributed logging
    across ONEX services. Context objects carry metadata, correlation
    IDs, and structured data for observability and debugging.

    Key Features:
        - Structured context data with type safety
        - Dictionary conversion for serialization
        - Compatible with typed ContextValue constraints
        - Supports distributed tracing and correlation

    Usage:
        context = create_log_context()
        logger.info("Operation completed", context=context.to_dict())
    """

    def to_dict(self) -> dict[str, ContextValue]:
        """
        Convert context to dictionary with typed values.

        Returns:
            Dictionary containing context data with ContextValue types
            for safe serialization and structured logging.
        """
        ...


@runtime_checkable
class ProtocolLogEntry(Protocol):
    """
    Protocol for structured log entry objects in ONEX systems.

    Standardizes log entries across all ONEX services with consistent
    structure for level, messaging, correlation tracking, and context.
    Essential for distributed system observability and debugging.

    Key Features:
        - Standardized log levels (TRACE through FATAL)
        - Correlation ID for distributed tracing
        - Structured context with type safety
        - Timestamp for chronological ordering

    Usage:
        entry = create_log_entry(
            level="INFO",
            message="User authenticated successfully",
            correlation_id=request.correlation_id,
            context={"user_id": user.id, "action": "login"}
        )
    """

    level: LiteralLogLevel
    message: str
    correlation_id: UUID
    timestamp: ProtocolDateTime
    context: dict[str, ContextValue]


# Core serialization protocols
@runtime_checkable
class ProtocolSerializationResult(Protocol):
    """
    Protocol for serialization operation results.

    Provides standardized results for serialization operations across
    ONEX services, including success status, serialized data, and
    error handling information.

    Key Features:
        - Success/failure indication
        - Serialized data as string format
        - Detailed error messages for debugging
        - Consistent result structure across services

    Usage:
        result = serializer.serialize(data)
        if result.success:
            send_data(result.data)
        else:
            logger.error(f"Serialization failed: {result.error_message}")
    """

    success: bool
    data: str
    error_message: str | None


# Core node protocols
@runtime_checkable
class ProtocolNodeMetadata(Protocol):
    """
    Protocol for ONEX node metadata objects.

    Defines the essential metadata structure for nodes in the ONEX
    distributed system, including identification, type classification,
    and extensible metadata storage.

    Key Features:
        - Unique node identification
        - Node type classification (COMPUTE, EFFECT, REDUCER, ORCHESTRATOR)
        - Extensible metadata dictionary with type safety
        - Runtime node introspection support

    Usage:
        metadata = node.get_metadata()
        if metadata.node_type == "COMPUTE":
            schedule_computation_task(metadata.node_id)
    """

    node_id: str
    node_type: str
    metadata: dict[str, ContextValue]


# Core validation protocols
@runtime_checkable
class ProtocolValidationResult(Protocol):
    """
    Protocol for comprehensive validation results.

    Provides structured validation outcomes with success indication,
    detailed error reporting, and warning notifications. Used across
    ONEX for input validation, configuration checking, and data integrity.

    Key Features:
        - Boolean validation status
        - Detailed error messages for failures
        - Warning messages for non-critical issues
        - Consistent validation reporting across services

    Usage:
        result = validator.validate(input_data)
        if not result.is_valid:
            raise ValidationError("\n".join(result.errors))
        if result.warnings:
            logger.warning(f"Validation warnings: {result.warnings}")
    """

    is_valid: bool
    errors: list[str]
    warnings: list[str]


# Cache service protocols
@runtime_checkable
class ProtocolCacheStatistics(Protocol):
    """
    Protocol for comprehensive cache service statistics.

    Provides detailed performance and usage metrics for cache services
    across ONEX systems. Used for monitoring, optimization, and capacity
    planning of distributed caching infrastructure.

    Key Features:
        - Performance metrics (hits, misses, ratios)
        - Resource usage tracking (memory, entry counts)
        - Operational statistics (evictions, access patterns)
        - Capacity management information

    Metrics Description:
        - hit_count: Number of successful cache retrievals
        - miss_count: Number of cache misses requiring data source access
        - hit_ratio: Efficiency ratio (hits / total_requests)
        - memory_usage_bytes: Current memory consumption
        - entry_count: Number of cached entries
        - eviction_count: Number of entries removed due to capacity limits
        - last_accessed: Timestamp of most recent cache access
        - cache_size_limit: Maximum cache capacity (if configured)

    Usage:
        stats = cache_service.get_statistics()
        if stats.hit_ratio < 0.8:
            logger.warning(f"Low cache hit ratio: {stats.hit_ratio:.2%}")
    """

    hit_count: int
    miss_count: int
    total_requests: int
    hit_ratio: float
    memory_usage_bytes: int
    entry_count: int
    eviction_count: int
    last_accessed: Optional[datetime]
    cache_size_limit: Optional[int]


# Base status types - consolidated lifecycle states for operations and processes
# pending: Operation queued but not started
# processing: Operation currently in progress
# completed: Operation finished successfully
# failed: Operation encountered an error and stopped
# cancelled: Operation was stopped by user or system request
# skipped: Operation was bypassed due to conditions or filters
LiteralBaseStatus = Literal[
    "pending", "processing", "completed", "failed", "cancelled", "skipped"
]

# Domain-specific status types for node lifecycle management
# active: Node is operational and accepting work
# inactive: Node is stopped but can be reactivated
# error: Node is in error state requiring intervention
# pending: Node is starting up or waiting for resources
LiteralNodeStatus = Literal["active", "inactive", "error", "pending"]

# Execution types - workflow execution strategies
# direct: Synchronous execution in current process
# inmemory: Async execution using in-memory queues
# kafka: Distributed execution via Kafka messaging
LiteralExecutionMode = Literal["direct", "inmemory", "kafka"]

# Operation status for tracking distributed operation outcomes
# success: Operation completed without errors
# failed: Operation failed and cannot be retried
# in_progress: Operation is currently executing
# cancelled: Operation was cancelled before completion
# pending: Operation is queued for execution
LiteralOperationStatus = Literal[
    "success", "failed", "in_progress", "cancelled", "pending"
]

# Validation types - validation thoroughness and execution modes
# Use LogLevel for error severity instead of separate ErrorSeverity type

# Validation thoroughness levels
# BASIC: Essential validation only (fast)
# STANDARD: Normal validation with common checks
# COMPREHENSIVE: Thorough validation with detailed analysis
# PARANOID: Maximum validation with all possible checks
LiteralValidationLevel = Literal["BASIC", "STANDARD", "COMPREHENSIVE", "PARANOID"]

# Validation execution modes
# strict: Fail on any validation error
# lenient: Allow warnings but fail on errors
# smoke: Basic functionality validation
# regression: Validate against known good states
# integration: Cross-system validation testing
LiteralValidationMode = Literal[
    "strict", "lenient", "smoke", "regression", "integration"
]


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
@runtime_checkable
class ProtocolActionPayload(Protocol):
    """Protocol for action payload with specific data."""

    target_id: str
    operation: str
    parameters: dict[str, ContextValue]


@runtime_checkable
class ProtocolAction(Protocol):
    """Protocol for reducer actions."""

    type: str
    payload: ProtocolActionPayload
    timestamp: ProtocolDateTime


@runtime_checkable
class ProtocolState(Protocol):
    """Protocol for reducer state."""

    metadata: ProtocolMetadata
    version: int  # This is a sequence number, not semver
    last_updated: ProtocolDateTime


# Schema and node metadata protocols
@runtime_checkable
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


@runtime_checkable
class ProtocolSchemaObject(Protocol):
    """Protocol for schema data objects."""

    schema_id: str
    schema_type: str
    schema_data: dict[str, ContextValue]
    version: ProtocolSemVer
    is_valid: bool


# Workflow result protocols for enhanced reducer support
class ProtocolErrorInfo(Protocol):
    """
    Protocol for comprehensive error information in workflow results.

    Provides detailed error context for workflow operations, including
    recovery strategies and retry configuration. Essential for resilient
    distributed system operation and automated error recovery.

    Key Features:
        - Error type classification for automated handling
        - Human-readable error messages
        - Stack trace information for debugging
        - Retry configuration and backoff strategies

    Usage:
        error_info = ProtocolErrorInfo(
            error_type="TimeoutError",
            message="Operation timed out after 30 seconds",
            trace=traceback.format_exc(),
            retryable=True,
            backoff_strategy="exponential",
            max_attempts=3
        )

        if error_info.retryable:
            schedule_retry(operation, error_info.backoff_strategy)
    """

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
    """
    Protocol for comprehensive node processing results with monadic composition.

    Provides rich result information for ONEX node operations, including
    success/failure indication, error details, trust scores, provenance
    tracking, and state changes. Enables sophisticated result composition
    and error handling in distributed workflows.

    Key Features:
        - Monadic success/failure patterns
        - Trust scoring for result confidence
        - Provenance tracking for data lineage
        - Event emission for observability
        - State delta tracking for reducers

    Usage:
        result = node.process(input_data)

        # Monadic composition patterns
        if result.is_success:
            next_result = next_node.process(result.value)
        else:
            handle_error(result.error)

        # Trust evaluation
        if result.trust_score > 0.8:
            accept_result(result.value)

        # State management
        for key, value in result.state_delta.items():
            state_manager.update(key, value)
    """

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
    health_status: LiteralHealthStatus
    last_seen: ProtocolDateTime


class ProtocolServiceHealthStatus(Protocol):
    """Protocol for service health status."""

    service_id: str
    status: LiteralHealthStatus
    last_check: ProtocolDateTime
    details: dict[str, ContextValue]


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
# Error recovery strategies for fault tolerance
# retry: Attempt the operation again with backoff
# fallback: Use alternative implementation or default value
# abort: Stop operation and propagate error
# circuit_breaker: Temporarily disable failing service
# compensation: Execute compensating actions (saga pattern)
LiteralErrorRecoveryStrategy = Literal[
    "retry", "fallback", "abort", "circuit_breaker", "compensation"
]

# Error severity levels for prioritization and alerting
# low: Minor issues that don't affect operation
# medium: Moderate issues that may affect performance
# high: Significant issues that affect functionality
# critical: Severe issues requiring immediate attention
LiteralErrorSeverity = Literal["low", "medium", "high", "critical"]


class ProtocolErrorContext(Protocol):
    """Protocol for error context information."""

    correlation_id: UUID
    operation_name: str
    timestamp: ProtocolDateTime
    context_data: dict[str, ContextValue]
    stack_trace: str | None


class ProtocolRecoveryAction(Protocol):
    """Protocol for error recovery action information."""

    action_type: LiteralErrorRecoveryStrategy
    max_attempts: int
    backoff_multiplier: float
    timeout_seconds: int
    fallback_value: ContextValue | None


class ProtocolErrorResult(Protocol):
    """Protocol for standardized error results."""

    error_id: UUID
    error_type: str
    message: str
    severity: LiteralErrorSeverity
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
# Health check thoroughness levels - balancing speed vs completeness
# quick: Fast ping-style health check (<100ms)
# basic: Essential service health indicators (<500ms)
# standard: Normal operational health checks (<2s)
# thorough: Detailed health analysis including dependencies (<10s)
# comprehensive: Complete system health audit (variable time)
LiteralHealthCheckLevel = Literal[
    "quick", "basic", "standard", "thorough", "comprehensive"
]

# Health check dimensions - different aspects of system health
# availability: Service reachability and response
# performance: Response time and throughput metrics
# functionality: Core features working correctly
# data_integrity: Data consistency and validation
# security: Security posture and compliance
LiteralHealthDimension = Literal[
    "availability", "performance", "functionality", "data_integrity", "security"
]


# Marker Interfaces for Type Compatibility
@runtime_checkable
class ProtocolNodeInfoLike(Protocol):
    """
    Protocol for objects that can provide ONEX node information.

    This marker protocol defines the minimal interface that objects
    must implement to be compatible with node metadata processing
    and discovery systems. Objects implementing this protocol can be
    safely converted to ModelNodeMetadataInfo instances.

    Key Features:
        - Marker interface for node information compatibility
        - Runtime type checking with sentinel attribute
        - Safe conversion to node metadata structures
        - Compatibility with node discovery and registry systems

    Usage:
        def process_node_info(info: ProtocolNodeInfoLike):
            if isinstance(info, ProtocolNodeInfoLike):
                metadata = convert_to_node_metadata(info)
                register_node(metadata)

    This is a marker interface with a sentinel attribute for runtime checks.
    """

    __omnibase_node_info_marker__: Literal[True]


@runtime_checkable
class ProtocolSupportedPropertyValue(Protocol):
    """
    Protocol for values that can be stored as ONEX property values.

    This marker protocol defines the minimal interface that property values
    must implement to be compatible with the ONEX property system.
    Properties are used for node configuration, service parameters,
    and dynamic system settings.

    Key Features:
        - Marker interface for property value compatibility
        - Runtime type checking with sentinel attribute
        - Safe storage in property management systems
        - Compatible with configuration and parameter systems

    Usage:
        def set_property(key: str, value: ProtocolSupportedPropertyValue):
            if isinstance(value, ProtocolSupportedPropertyValue):
                property_store[key] = value
            else:
                raise TypeError("Value not compatible with property system")

    This is a marker interface with a sentinel attribute for runtime checks.
    """

    __omnibase_property_value_marker__: Literal[True]


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
    check_level: LiteralHealthCheckLevel
    dimensions_checked: list[LiteralHealthDimension]
    overall_status: LiteralHealthStatus
    individual_checks: dict[str, LiteralHealthStatus]
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
    alert_on_status: list[LiteralHealthStatus]
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
    status: LiteralOperationStatus
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
    outcome: LiteralOperationStatus
    metadata: dict[str, ContextValue]
    sensitivity_level: Literal["public", "internal", "confidential", "restricted"]


# General Purpose Protocols for Type Constraints


@runtime_checkable
class ProtocolSerializable(Protocol):
    """
    Protocol for objects that can be serialized to dictionary format.

    Provides standardized serialization contract for ONEX objects that need
    to be persisted, transmitted, or cached. The model_dump method ensures
    consistent serialization across all ONEX services.

    Key Features:
        - Standardized serialization interface
        - Type-safe dictionary output
        - Compatible with JSON serialization
        - Consistent across all ONEX services

    Usage:
        class MyDataObject(ProtocolSerializable):
            def model_dump(self) -> dict[str, Any]:
                return {
                    "id": self.id,
                    "name": self.name,
                    "active": self.is_active
                }

        # Serialize for storage
        obj = MyDataObject()
        serialized = obj.model_dump()
        json.dumps(serialized)  # Safe for JSON
    """

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
        """Serialize object to dictionary with type-safe values."""
        ...


@runtime_checkable
class ProtocolIdentifiable(Protocol):
    """Protocol for objects that have an ID."""

    __omnibase_identifiable_marker__: Literal[True]

    @property
    def id(self) -> str:
        """Get the object ID."""
        ...


@runtime_checkable
class ProtocolNameable(Protocol):
    """Protocol for objects that have a name."""

    __omnibase_nameable_marker__: Literal[True]

    @property
    def name(self) -> str:
        """Get the object name."""
        ...


@runtime_checkable
class ProtocolValidatable(Protocol):
    """Protocol for objects that can be validated."""

    __omnibase_validatable_marker__: Literal[True]

    def is_valid(self) -> bool:
        """Check if the object is valid."""
        ...


@runtime_checkable
class ProtocolConfigurable(Protocol):
    """Protocol for objects that can be configured."""

    __omnibase_configurable_marker__: Literal[True]

    def configure(self, **kwargs: ContextValue) -> None:
        """Configure the object with parameters."""
        ...


@runtime_checkable
class ProtocolExecutable(Protocol):
    """Protocol for objects that can be executed."""

    __omnibase_executable_marker__: Literal[True]

    def execute(self) -> object:
        """Execute the object."""
        ...


@runtime_checkable
class ProtocolMetadataProvider(Protocol):
    """Protocol for objects that provide metadata."""

    __omnibase_metadata_provider_marker__: Literal[True]

    def get_metadata(self) -> dict[str, str | int | bool | float]:
        """Get metadata dictionary."""
        ...
