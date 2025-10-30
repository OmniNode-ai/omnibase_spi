"""
Core protocol types for ONEX SPI interfaces.

Domain: Core system protocols (logging, serialization, validation)
"""

from datetime import datetime
from typing import TYPE_CHECKING, Literal, Protocol, runtime_checkable
from uuid import UUID

if TYPE_CHECKING:
    pass


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

    def __str__(self) -> str: ...


ProtocolDateTime = datetime
LiteralLogLevel = Literal[
    "TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "FATAL"
]
LiteralNodeType = Literal["COMPUTE", "EFFECT", "REDUCER", "ORCHESTRATOR"]
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


@runtime_checkable
class ProtocolContextValue(Protocol):
    """Protocol for context data values supporting validation and serialization."""

    async def validate_for_context(self) -> bool: ...

    def serialize_for_context(self) -> dict[str, object]: ...

    async def get_context_type_hint(self) -> str: ...


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


ContextValue = ProtocolContextValue


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
        def store_metadata(key: str, value: "ProtocolSupportedMetadataType"):
            metadata_store[key] = str(value)
    """

    __omnibase_metadata_type_marker__: Literal[True]

    def __str__(self) -> str: ...

    async def validate_for_metadata(self) -> bool: ...


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
    default_value: ContextValue | None

    async def validate_config_value(self) -> bool: ...

    def has_valid_default(self) -> bool: ...


@runtime_checkable
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

    def to_dict(self) -> dict[str, "ContextValue"]: ...


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
    timestamp: "ProtocolDateTime"
    context: dict[str, "ContextValue"]

    async def validate_log_entry(self) -> bool: ...

    def is_complete(self) -> bool: ...


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

    async def validate_serialization(self) -> bool: ...

    def has_data(self) -> bool: ...


@runtime_checkable
class ProtocolNodeConfigurationData(Protocol):
    """
    Protocol for ONEX node configuration data objects.

    Defines the configuration structure for nodes in the ONEX distributed system,
    including execution parameters, resource limits, and behavioral settings.

    Key Features:
        - Execution parameters and settings
        - Resource limits and constraints
        - Behavioral configuration options
        - Node-specific configuration metadata

    Usage:
        config = await node.get_node_config()
        max_memory = config.resource_limits.get("max_memory_mb")
        timeout_seconds = config.execution_parameters.get("timeout_seconds")
    """

    @property
    def execution_parameters(self) -> dict[str, "ContextValue"]: ...
    @property
    def resource_limits(self) -> dict[str, "ContextValue"]:
        """Resource limits and constraints."""
        ...

    @property
    def behavioral_settings(self) -> dict[str, "ContextValue"]:
        """Behavioral configuration options."""
        ...

    @property
    def configuration_metadata(self) -> dict[str, "ContextValue"]:
        """Configuration-specific metadata."""
        ...


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
    metadata: dict[str, "ContextValue"]

    async def validate_node_metadata(self) -> bool: ...

    def is_complete(self) -> bool: ...


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
    last_accessed: datetime | None
    cache_size_limit: int | None

    async def validate_statistics(self) -> bool: ...

    def is_current(self) -> bool: ...


LiteralBaseStatus = Literal[
    "pending", "processing", "completed", "failed", "cancelled", "skipped"
]
LiteralNodeStatus = Literal["active", "inactive", "error", "pending"]
LiteralExecutionMode = Literal["direct", "inmemory", "kafka"]
LiteralOperationStatus = Literal[
    "success", "failed", "in_progress", "cancelled", "pending"
]
LiteralValidationLevel = Literal["BASIC", "STANDARD", "COMPREHENSIVE", "PARANOID"]
LiteralValidationMode = Literal[
    "strict", "lenient", "smoke", "regression", "integration"
]


@runtime_checkable
class ProtocolMetadata(Protocol):
    """Protocol for structured metadata - attribute-based for data compatibility."""

    data: dict[str, "ContextValue"]
    version: "ProtocolSemVer"
    created_at: "ProtocolDateTime"
    updated_at: "ProtocolDateTime | None"

    async def validate_metadata(self) -> bool: ...

    def is_up_to_date(self) -> bool: ...


@runtime_checkable
class ProtocolMetadataOperations(Protocol):
    """Protocol for metadata operations - method-based for services."""

    async def get_value(self, key: str) -> ContextValue: ...

    def has_key(self, key: str) -> bool: ...

    def keys(self) -> list[str]: ...

    async def update_value(self, key: str, value: ContextValue) -> None: ...


@runtime_checkable
class ProtocolActionPayload(Protocol):
    """Protocol for action payload with specific data."""

    target_id: UUID
    operation: str
    parameters: dict[str, "ContextValue"]

    async def validate_payload(self) -> bool: ...

    def has_valid_parameters(self) -> bool: ...


@runtime_checkable
class ProtocolAction(Protocol):
    """Protocol for reducer actions."""

    type: str
    payload: "ProtocolActionPayload"
    timestamp: "ProtocolDateTime"

    async def validate_action(self) -> bool: ...

    def is_executable(self) -> bool: ...


@runtime_checkable
class ProtocolState(Protocol):
    """Protocol for reducer state."""

    metadata: "ProtocolMetadata"
    version: int
    last_updated: "ProtocolDateTime"

    async def validate_state(self) -> bool: ...

    def is_consistent(self) -> bool: ...


@runtime_checkable
class ProtocolNodeMetadataBlock(Protocol):
    """Protocol for node metadata block objects."""

    uuid: str
    name: str
    description: str
    version: "ProtocolSemVer"
    metadata_version: "ProtocolSemVer"
    namespace: str
    created_at: "ProtocolDateTime"
    last_modified_at: "ProtocolDateTime"
    lifecycle: str
    protocol_version: "ProtocolSemVer"

    async def validate_metadata_block(self) -> bool: ...

    def is_complete(self) -> bool: ...


@runtime_checkable
class ProtocolSchemaObject(Protocol):
    """Protocol for schema data objects."""

    schema_id: str
    schema_type: str
    schema_data: dict[str, "ContextValue"]
    version: "ProtocolSemVer"
    is_valid: bool

    async def validate_schema(self) -> bool: ...

    def is_valid_schema(self) -> bool: ...


@runtime_checkable
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
    trace: str | None
    retryable: bool
    backoff_strategy: str | None
    max_attempts: int | None

    async def validate_error_info(self) -> bool: ...

    def is_retryable(self) -> bool: ...


@runtime_checkable
class ProtocolSystemEvent(Protocol):
    """Protocol for system events."""

    type: str
    payload: dict[str, "ContextValue"]
    timestamp: float
    source: str

    async def validate_system_event(self) -> bool: ...

    def is_well_formed(self) -> bool: ...


@runtime_checkable
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

    value: ContextValue | None
    is_success: bool
    is_failure: bool
    error: "ProtocolErrorInfo | None"
    trust_score: float
    provenance: list[str]
    metadata: dict[str, "ContextValue"]
    events: list["ProtocolSystemEvent"]
    state_delta: dict[str, "ContextValue"]

    async def validate_result(self) -> bool: ...

    def is_successful(self) -> bool: ...


@runtime_checkable
class ProtocolServiceMetadata(Protocol):
    """Protocol for service metadata."""

    data: dict[str, "ContextValue"]
    version: "ProtocolSemVer"
    capabilities: list[str]
    tags: list[str]

    async def validate_service_metadata(self) -> bool: ...

    def has_capabilities(self) -> bool: ...


@runtime_checkable
class ProtocolServiceInstance(Protocol):
    """Protocol for service instance information."""

    service_id: UUID
    service_name: str
    host: str
    port: int
    metadata: "ProtocolServiceMetadata"
    health_status: "LiteralHealthStatus"
    last_seen: "ProtocolDateTime"

    async def validate_service_instance(self) -> bool: ...

    def is_available(self) -> bool: ...


@runtime_checkable
class ProtocolServiceHealthStatus(Protocol):
    """Protocol for service health status."""

    service_id: UUID
    status: "LiteralHealthStatus"
    last_check: "ProtocolDateTime"
    details: dict[str, "ContextValue"]

    async def validate_health_status(self) -> bool: ...

    def is_healthy(self) -> bool: ...


@runtime_checkable
class ProtocolGenericCheckpointData(Protocol):
    """Protocol for generic checkpoint data."""

    checkpoint_id: UUID
    workflow_id: UUID
    data: dict[str, "ContextValue"]
    timestamp: "ProtocolDateTime"
    metadata: dict[str, "ContextValue"]

    async def validate_checkpoint(self) -> bool: ...

    def is_restorable(self) -> bool: ...


@runtime_checkable
class ProtocolGenericStorageCredentials(Protocol):
    """Protocol for generic storage credentials."""

    credential_type: str
    data: dict[str, "ContextValue"]

    async def validate_credentials(self) -> bool: ...

    def is_secure(self) -> bool: ...


@runtime_checkable
class ProtocolGenericStorageConfiguration(Protocol):
    """Protocol for generic storage configuration."""

    backend_type: str
    connection_string: str
    options: dict[str, "ContextValue"]
    timeout_seconds: int

    async def validate_configuration(self) -> bool: ...

    async def is_connectable(self) -> bool: ...


@runtime_checkable
class ProtocolGenericStorageResult(Protocol):
    """Protocol for generic storage operation results."""

    success: bool
    data: dict[str, "ContextValue"] | None
    error_message: str | None
    operation_id: UUID

    async def validate_storage_result(self) -> bool: ...

    def is_successful(self) -> bool: ...


@runtime_checkable
class ProtocolGenericStorageListResult(Protocol):
    """Protocol for generic storage list operation results."""

    success: bool
    items: list[dict[str, "ContextValue"]]
    total_count: int
    has_more: bool
    error_message: str | None

    async def validate_list_result(self) -> bool: ...

    def has_items(self) -> bool: ...


@runtime_checkable
class ProtocolGenericStorageHealthStatus(Protocol):
    """Protocol for generic storage health status."""

    is_healthy: bool
    status_details: dict[str, "ContextValue"]
    capacity_info: dict[str, int] | None
    last_check: "ProtocolDateTime"

    async def validate_health_status(self) -> bool: ...

    def is_available(self) -> bool: ...


LiteralErrorRecoveryStrategy = Literal[
    "retry", "fallback", "abort", "circuit_breaker", "compensation"
]
LiteralErrorSeverity = Literal["low", "medium", "high", "critical"]


@runtime_checkable
class ProtocolErrorContext(Protocol):
    """Protocol for error context information."""

    correlation_id: UUID
    operation_name: str
    timestamp: "ProtocolDateTime"
    context_data: dict[str, "ContextValue"]
    stack_trace: str | None

    async def validate_error_context(self) -> bool: ...

    def has_trace(self) -> bool: ...


@runtime_checkable
class ProtocolRecoveryAction(Protocol):
    """Protocol for error recovery action information."""

    action_type: LiteralErrorRecoveryStrategy
    max_attempts: int
    backoff_multiplier: float
    timeout_seconds: int
    fallback_value: ContextValue | None

    async def validate_recovery_action(self) -> bool: ...

    def is_applicable(self) -> bool: ...


@runtime_checkable
class ProtocolErrorResult(Protocol):
    """Protocol for standardized error results."""

    error_id: UUID
    error_type: str
    message: str
    severity: LiteralErrorSeverity
    retryable: bool
    recovery_action: "ProtocolRecoveryAction | None"
    context: "ProtocolErrorContext"

    async def validate_error(self) -> bool: ...

    def is_retryable(self) -> bool: ...


@runtime_checkable
class ProtocolVersionInfo(Protocol):
    """Protocol for version metadata."""

    protocol_name: str
    version: "ProtocolSemVer"
    compatibility_version: "ProtocolSemVer"
    retirement_date: "ProtocolDateTime | None"
    migration_guide_url: str | None

    async def validate_version_info(self) -> bool: ...

    def is_compatible(self) -> bool: ...


@runtime_checkable
class ProtocolCompatibilityCheck(Protocol):
    """Protocol for compatibility checking results."""

    is_compatible: bool
    required_version: "ProtocolSemVer"
    current_version: "ProtocolSemVer"
    breaking_changes: list[str]
    migration_required: bool

    async def validate_compatibility(self) -> bool: ...


LiteralHealthCheckLevel = Literal[
    "quick", "basic", "standard", "thorough", "comprehensive"
]
LiteralHealthDimension = Literal[
    "availability", "performance", "functionality", "data_integrity", "security"
]


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
        def process_node_info(info: "ProtocolNodeInfoLike"):
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
        def set_property(key: str, value: "ProtocolSupportedPropertyValue"):
            if isinstance(value, ProtocolSupportedPropertyValue):
                property_store[key] = value
            else:
                raise TypeError("Value not compatible with property system")

    This is a marker interface with a sentinel attribute for runtime checks.
    """

    __omnibase_property_value_marker__: Literal[True]

    async def validate_for_property(self) -> bool: ...


@runtime_checkable
class ProtocolHealthMetrics(Protocol):
    """Protocol for health check metrics."""

    response_time_ms: float
    cpu_usage_percent: float
    memory_usage_percent: float
    disk_usage_percent: float
    connection_count: int
    error_rate_percent: float
    throughput_per_second: float

    async def validate_metrics(self) -> bool: ...

    def is_within_thresholds(self) -> bool: ...


@runtime_checkable
class ProtocolHealthCheck(Protocol):
    """Protocol for standardized health checks."""

    service_name: str
    check_level: LiteralHealthCheckLevel
    dimensions_checked: list[LiteralHealthDimension]
    overall_status: "LiteralHealthStatus"
    individual_checks: dict[str, "LiteralHealthStatus"]
    metrics: "ProtocolHealthMetrics"
    check_duration_ms: float
    timestamp: "ProtocolDateTime"
    recommendations: list[str]

    async def validate_health_check(self) -> bool: ...

    def is_passing(self) -> bool: ...


@runtime_checkable
class ProtocolHealthMonitoring(Protocol):
    """Protocol for health monitoring configuration."""

    check_interval_seconds: int
    timeout_seconds: int
    failure_threshold: int
    recovery_threshold: int
    alert_on_status: list["LiteralHealthStatus"]
    escalation_rules: dict[str, "ContextValue"]

    async def validate_monitoring_config(self) -> bool: ...

    def is_reasonable(self) -> bool: ...


@runtime_checkable
class ProtocolMetricsPoint(Protocol):
    """Protocol for individual metrics points."""

    metric_name: str
    value: float
    unit: str
    timestamp: "ProtocolDateTime"
    tags: dict[str, "ContextValue"]
    dimensions: dict[str, "ContextValue"]

    async def validate_metrics_point(self) -> bool: ...

    def is_valid_measurement(self) -> bool: ...


@runtime_checkable
class ProtocolTraceSpan(Protocol):
    """Protocol for distributed tracing spans."""

    span_id: UUID
    trace_id: UUID
    parent_span_id: UUID | None
    operation_name: str
    start_time: "ProtocolDateTime"
    end_time: "ProtocolDateTime | None"
    status: LiteralOperationStatus
    tags: dict[str, "ContextValue"]
    logs: list[dict[str, "ContextValue"]]

    async def validate_trace_span(self) -> bool: ...

    def is_complete(self) -> bool: ...


@runtime_checkable
class ProtocolAuditEvent(Protocol):
    """Protocol for audit events."""

    event_id: UUID
    event_type: str
    actor: str
    resource: str
    action: str
    timestamp: "ProtocolDateTime"
    outcome: LiteralOperationStatus
    metadata: dict[str, "ContextValue"]
    sensitivity_level: Literal["public", "internal", "confidential", "restricted"]

    async def validate_audit_event(self) -> bool: ...

    def is_complete(self) -> bool: ...


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
            def model_dump(self) -> dict[str, ContextValue]:
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
    ]: ...


@runtime_checkable
class ProtocolIdentifiable(Protocol):
    """Protocol for objects that have an ID."""

    __omnibase_identifiable_marker__: Literal[True]

    @property
    def id(self) -> str: ...


@runtime_checkable
class ProtocolNameable(Protocol):
    """Protocol for objects that have a name."""

    __omnibase_nameable_marker__: Literal[True]

    @property
    def name(self) -> str: ...


@runtime_checkable
class ProtocolConfigurable(Protocol):
    """Protocol for objects that can be configured."""

    __omnibase_configurable_marker__: Literal[True]

    def configure(self, **kwargs: ContextValue) -> None: ...


@runtime_checkable
class ProtocolExecutable(Protocol):
    """Protocol for objects that can be executed."""

    __omnibase_executable_marker__: Literal[True]

    async def execute(self) -> object: ...


@runtime_checkable
class ProtocolMetadataProvider(Protocol):
    """Protocol for objects that provide metadata."""

    __omnibase_metadata_provider_marker__: Literal[True]

    async def get_metadata(self) -> dict[str, str | int | bool | float]: ...


LiteralRetryBackoffStrategy = Literal[
    "fixed", "linear", "exponential", "fibonacci", "jitter"
]
LiteralRetryCondition = Literal[
    "always", "never", "on_error", "on_timeout", "on_network", "on_transient"
]


@runtime_checkable
class ProtocolRetryConfig(Protocol):
    """Protocol for retry configuration."""

    max_attempts: int
    backoff_strategy: LiteralRetryBackoffStrategy
    base_delay_ms: int
    max_delay_ms: int
    timeout_ms: int
    jitter_factor: float

    async def validate_retry_config(self) -> bool: ...

    def is_reasonable(self) -> bool: ...


@runtime_checkable
class ProtocolRetryPolicy(Protocol):
    """Protocol for retry policy configuration."""

    default_config: "ProtocolRetryConfig"
    error_specific_configs: dict[str, "ProtocolRetryConfig"]
    retry_conditions: list[LiteralRetryCondition]
    retry_budget_limit: int
    budget_window_seconds: int

    async def validate_retry_policy(self) -> bool: ...

    def is_applicable(self) -> bool: ...


@runtime_checkable
class ProtocolRetryAttempt(Protocol):
    """Protocol for retry attempt records."""

    attempt_number: int
    timestamp: "ProtocolDateTime"
    duration_ms: int
    error_type: str | None
    success: bool
    backoff_applied_ms: int

    async def validate_retry_attempt(self) -> bool: ...

    def is_valid_attempt(self) -> bool: ...


@runtime_checkable
class ProtocolRetryResult(Protocol):
    """Protocol for retry operation results."""

    success: bool
    final_attempt_number: int
    total_duration_ms: int
    result: ContextValue | None
    final_error: Exception | None
    attempts: list["ProtocolRetryAttempt"]

    async def validate_retry_result(self) -> bool: ...

    def is_final(self) -> bool: ...


LiteralTimeBasedType = Literal["duration", "timeout", "interval", "deadline"]


@runtime_checkable
class ProtocolTimeBased(Protocol):
    """Protocol for time-based operations and measurements."""

    type: LiteralTimeBasedType
    start_time: "ProtocolDateTime | None"
    end_time: "ProtocolDateTime | None"
    duration_ms: int | None
    is_active: bool
    has_expired: bool

    async def validate_time_based(self) -> bool: ...

    def is_valid_timing(self) -> bool: ...


@runtime_checkable
class ProtocolTimeout(Protocol):
    """Protocol for timeout configuration and tracking."""

    timeout_ms: int
    start_time: "ProtocolDateTime"
    warning_threshold_ms: int | None
    is_expired: bool
    time_remaining_ms: int

    async def validate_timeout(self) -> bool: ...

    def is_reasonable(self) -> bool: ...


@runtime_checkable
class ProtocolDuration(Protocol):
    """Protocol for duration measurement and tracking."""

    start_time: "ProtocolDateTime"
    end_time: "ProtocolDateTime | None"
    duration_ms: int
    is_completed: bool
    can_measure: bool

    async def validate_duration(self) -> bool: ...

    def is_measurable(self) -> bool: ...


LiteralAnalyticsTimeWindow = Literal[
    "real_time", "hourly", "daily", "weekly", "monthly"
]
LiteralAnalyticsMetricType = Literal["counter", "gauge", "histogram", "summary"]


@runtime_checkable
class ProtocolAnalyticsMetric(Protocol):
    """Protocol for individual analytics metrics."""

    name: str
    type: LiteralAnalyticsMetricType
    value: float
    unit: str
    timestamp: "ProtocolDateTime"
    tags: dict[str, "ContextValue"]
    metadata: dict[str, "ContextValue"]

    async def validate_metric(self) -> bool: ...

    def is_valid_measurement(self) -> bool: ...


@runtime_checkable
class ProtocolAnalyticsProvider(Protocol):
    """Protocol for analytics data providers."""

    provider_id: UUID
    provider_type: str
    data_sources: list[str]
    supported_metrics: list[str]
    time_windows: list[LiteralAnalyticsTimeWindow]
    last_updated: "ProtocolDateTime"

    async def validate_provider(self) -> bool: ...

    def is_available(self) -> bool: ...


@runtime_checkable
class ProtocolAnalyticsSummary(Protocol):
    """Protocol for analytics summary reports."""

    time_window: LiteralAnalyticsTimeWindow
    start_time: "ProtocolDateTime"
    end_time: "ProtocolDateTime"
    metrics: list["ProtocolAnalyticsMetric"]
    insights: list[str]
    recommendations: list[str]
    confidence_score: float

    async def validate_summary(self) -> bool: ...

    def is_complete(self) -> bool: ...


LiteralPerformanceCategory = Literal[
    "latency", "throughput", "resource", "error", "availability"
]


@runtime_checkable
class ProtocolPerformanceMetric(Protocol):
    """Protocol for performance metric data points."""

    metric_name: str
    category: LiteralPerformanceCategory
    value: float
    unit: str
    timestamp: "ProtocolDateTime"
    source: str
    threshold_warning: float | None
    threshold_critical: float | None

    async def validate_performance_metric(self) -> bool: ...

    def is_valid(self) -> bool: ...


@runtime_checkable
class ProtocolPerformanceMetrics(Protocol):
    """Protocol for performance metrics collection."""

    service_name: str
    collection_timestamp: "ProtocolDateTime"
    metrics: list["ProtocolPerformanceMetric"]
    overall_health_score: float
    performance_trends: dict[str, float]
    recommendations: list[str]

    async def validate_performance_metrics(self) -> bool: ...

    def is_healthy(self) -> bool: ...


LiteralConnectionState = Literal[
    "disconnected", "connecting", "connected", "reconnecting", "failed", "closing"
]


@runtime_checkable
class ProtocolConnectionConfig(Protocol):
    """Protocol for connection configuration."""

    host: str
    port: int
    timeout_ms: int
    max_retries: int
    ssl_enabled: bool
    connection_pool_size: int
    keep_alive_interval_ms: int

    async def validate_connection_config(self) -> bool: ...

    async def is_connectable(self) -> bool: ...


@runtime_checkable
class ProtocolConnectionStatus(Protocol):
    """Protocol for connection status tracking."""

    state: LiteralConnectionState
    connected_at: "ProtocolDateTime | None"
    last_activity: "ProtocolDateTime | None"
    error_count: int
    bytes_sent: int
    bytes_received: int

    async def validate_connection_status(self) -> bool: ...

    async def is_connected(self) -> bool: ...


LiteralValidationSeverity = Literal["error", "warning", "info"]
LiteralValidationCategory = Literal[
    "syntax", "semantic", "style", "security", "performance"
]


@runtime_checkable
class ProtocolValidatable(Protocol):
    """
    Base protocol for objects that can be validated.

    This protocol defines the minimal interface that validation targets
    should implement to provide context and metadata for validation
    operations. By implementing this protocol, objects become compatible
    with the ONEX validation framework while maintaining type safety.

    Key Features:
        - Validation context extraction for rule applicability
        - Object identification for validation reporting
        - Type safety for validation operations
        - Minimal interface requirements for broad compatibility

    Usage:
        class ConfigurationData(ProtocolValidatable):
            def get_validation_context(self) -> dict[str, "ContextValue"]:
                return {"type": "config", "version": self.version}

            def get_validation_id(self) -> str:
                return f"config_{self.name}"
    """

    async def get_validation_context(self) -> dict[str, "ContextValue"]: ...

    async def get_validation_id(self) -> str: ...

    ...


@runtime_checkable
class ProtocolOnexInputState(Protocol):
    """
    Protocol for ONEX input state objects.

    Used for format conversion and string transformation operations.
    Distinct from ProtocolWorkflowInputState which handles workflow orchestration.
    """

    input_string: str
    source_format: str
    metadata: dict[str, "ContextValue"]

    async def validate_onex_input(self) -> bool:
        """
        Validate ONEX input state for format conversion.

        Returns:
            True if input string and source format are valid
        """
        ...


@runtime_checkable
class ProtocolOnexOutputState(Protocol):
    """Protocol for ONEX output state objects."""

    output_string: str
    target_format: str
    conversion_success: bool
    metadata: dict[str, "ContextValue"]

    async def validate_output_state(self) -> bool: ...


# ==============================================================================
# Additional Core Protocols (Migrated from omnibase_core)
# ==============================================================================


@runtime_checkable
class ProtocolHasModelDump(Protocol):
    """
    Protocol for objects that support Pydantic model_dump method.

    This protocol ensures compatibility with Pydantic models and other
    objects that provide dictionary serialization via model_dump.
    Used for consistent serialization across ONEX services.

    Key Features:
        - Pydantic model compatibility
        - Mode-based serialization (json, python)
        - Consistent serialization interface
        - Type-safe dictionary output

    Usage:
        def serialize_object(obj: ProtocolHasModelDump) -> dict[str, "ContextValue"]:
            return obj.model_dump(mode="json")
    """

    def model_dump(self, mode: str | None = None) -> dict[str, ContextValue]: ...


@runtime_checkable
class ProtocolEventBusProvider(Protocol):
    """
    Protocol for objects that provide event bus integration.

    This protocol indicates that an object has event bus capabilities,
    regardless of whether it's a container, node, service, or other component.
    Used for coordinating events across distributed services and nodes.

    Key Features:
        - Optional event bus integration
        - Async event bus support
        - Component-level event coordination
        - Distributed messaging compatibility

    Usage:
        def get_event_bus(provider: ProtocolEventBusProvider):
            if provider.event_bus:
                await provider.event_bus.publish(event)
    """

    event_bus: object | None  # ProtocolAsyncEventBus type from event_bus module


@runtime_checkable
class ProtocolLogEmitter(Protocol):
    """
    Protocol for objects that can emit structured log events.

    Provides standardized logging interface for ONEX services with
    structured logging support. Enables consistent log emission across
    all system components.

    Key Features:
        - Structured logging with log levels
        - Consistent log data format
        - Integration with ONEX logging infrastructure
        - Type-safe log emission

    Usage:
        def log_operation(emitter: ProtocolLogEmitter, message: str):
            emitter.emit_log_event(
                level="INFO",
                message=message,
                data=log_data
            )
    """

    def emit_log_event(
        self,
        level: LiteralLogLevel,
        message: str,
        data: object,  # MixinLogData type from mixins
    ) -> None: ...


@runtime_checkable
class ProtocolPatternChecker(Protocol):
    """
    Protocol for AST pattern checker objects.

    Defines the interface for pattern checkers used in code validation
    and AST analysis. Pattern checkers traverse AST nodes to identify
    and validate code patterns.

    Key Features:
        - AST node traversal support
        - Issue collection and reporting
        - Pattern validation framework
        - Code quality checking

    Usage:
        checker = create_pattern_checker()
        checker.visit(ast_node)
        if checker.issues:
            report_violations(checker.issues)
    """

    issues: list[str]

    def visit(self, node: object) -> None: ...  # ast.AST type


@runtime_checkable
class ProtocolModelJsonSerializable(Protocol):
    """
    Protocol for values that can be JSON serialized.

    Marker protocol for objects that can be safely serialized to JSON.
    Used throughout ONEX for data interchange and persistence.
    Built-in types that implement this: str, int, float, bool,
    list[Any], dict[str, Any], None.

    Key Features:
        - JSON serialization guarantee
        - Marker interface pattern
        - Runtime type checking support
        - Safe for data interchange

    Usage:
        def store_json(value: ProtocolModelJsonSerializable):
            json_data = json.dumps(value)
            save_to_storage(json_data)
    """

    __omnibase_json_serializable_marker__: Literal[True]


@runtime_checkable
class ProtocolModelValidatable(Protocol):
    """
    Protocol for values that can validate themselves.

    Provides self-validation interface for objects with built-in
    validation logic. Used across ONEX for data validation before
    processing or persistence.

    Key Features:
        - Self-validation capability
        - Error collection and reporting
        - Boolean validation result
        - Detailed error messages

    Usage:
        def process_data(data: ProtocolModelValidatable):
            if data.is_valid():
                process(data)
            else:
                log_errors(data.get_errors())
    """

    def is_valid(self) -> bool:
        """Check if the value is valid."""
        ...

    async def get_errors(self) -> list[str]:
        """Get validation errors."""
        ...
