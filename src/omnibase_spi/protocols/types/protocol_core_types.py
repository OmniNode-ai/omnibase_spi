"""
Core protocol types for ONEX SPI interfaces.

This module re-exports all core protocol types from domain-specific modules
for backward compatibility. New code should import directly from the
specific domain modules:

- protocol_base_types: Base types, context values, Literal definitions
- protocol_logging_types: Logging protocols
- protocol_error_types: Error handling protocols
- protocol_health_types: Health and metrics protocols
- protocol_service_types: Service protocols
- protocol_node_types: Node protocols
- protocol_state_types: State and action protocols
- protocol_retry_types: Retry and timeout protocols
- protocol_analytics_types: Analytics and performance protocols
- protocol_connection_types: Connection protocols
- protocol_marker_types: Marker and base protocols
- protocol_validation_types: Validation and compatibility protocols
"""

# Legacy storage types that may still be referenced
# (these duplicate protocols in protocol_storage_types.py but with "Generic" prefix)
# Keeping for backward compatibility - deprecated in favor of protocol_storage_types.py
from typing import Protocol, runtime_checkable
from uuid import UUID

# Re-export from event_bus module (canonical location for provider protocol)
from omnibase_spi.protocols.event_bus.protocol_event_bus_provider import (
    ProtocolEventBusProvider,
)

# Re-export from analytics types
from omnibase_spi.protocols.types.protocol_analytics_types import (
    ProtocolAnalyticsMetric,
    ProtocolAnalyticsProvider,
    ProtocolAnalyticsSummary,
    ProtocolPerformanceMetric,
    ProtocolPerformanceMetrics,
)

# Re-export all from base types (Literals, ProtocolSemVer, Context values)
from omnibase_spi.protocols.types.protocol_base_types import (
    ContextValue,
    LiteralAnalyticsMetricType,
    LiteralAnalyticsTimeWindow,
    LiteralBaseStatus,
    LiteralConnectionState,
    LiteralErrorRecoveryStrategy,
    LiteralErrorSeverity,
    LiteralExecutionMode,
    LiteralHealthCheckLevel,
    LiteralHealthDimension,
    LiteralHealthStatus,
    LiteralLogLevel,
    LiteralNodeStatus,
    LiteralNodeType,
    LiteralOperationStatus,
    LiteralPerformanceCategory,
    LiteralRetryBackoffStrategy,
    LiteralRetryCondition,
    LiteralTimeBasedType,
    LiteralValidationCategory,
    LiteralValidationLevel,
    LiteralValidationMode,
    LiteralValidationSeverity,
    ProtocolConfigValue,
    ProtocolContextBooleanValue,
    ProtocolContextNumericValue,
    ProtocolContextStringDictValue,
    ProtocolContextStringListValue,
    ProtocolContextStringValue,
    ProtocolContextValue,
    ProtocolDateTime,
    ProtocolSemVer,
    ProtocolSupportedMetadataType,
)

# Re-export from connection types
from omnibase_spi.protocols.types.protocol_connection_types import (
    ProtocolConnectionConfig,
    ProtocolConnectionStatus,
)

# Re-export from error types
from omnibase_spi.protocols.types.protocol_error_types import (
    ProtocolErrorContext,
    ProtocolErrorInfo,
    ProtocolErrorResult,
    ProtocolRecoveryAction,
)

# Re-export from health types
from omnibase_spi.protocols.types.protocol_health_types import (
    ProtocolAuditEvent,
    ProtocolCacheStatistics,
    ProtocolHealthCheck,
    ProtocolHealthMetrics,
    ProtocolHealthMonitoring,
    ProtocolMetricsPoint,
    ProtocolTraceSpan,
)

# Re-export from logging types
from omnibase_spi.protocols.types.protocol_logging_types import (
    ProtocolLogContext,
    ProtocolLogEmitter,
    ProtocolLogEntry,
)

# Re-export from marker types
from omnibase_spi.protocols.types.protocol_marker_types import (
    ProtocolConfigurable,
    ProtocolExecutable,
    ProtocolIdentifiable,
    ProtocolMetadataProvider,
    ProtocolNameable,
    ProtocolSchemaObject,
    ProtocolSerializable,
    ProtocolSerializationResult,
    ProtocolSupportedPropertyValue,
)

# Re-export from node types
from omnibase_spi.protocols.types.protocol_node_types import (
    ProtocolNodeConfigurationData,
    ProtocolNodeInfoLike,
    ProtocolNodeMetadata,
    ProtocolNodeMetadataBlock,
    ProtocolNodeResult,
)

# Re-export from retry types
from omnibase_spi.protocols.types.protocol_retry_types import (
    ProtocolDuration,
    ProtocolRetryAttempt,
    ProtocolRetryConfig,
    ProtocolRetryPolicy,
    ProtocolRetryResult,
    ProtocolTimeBased,
    ProtocolTimeout,
)

# Re-export from service types
from omnibase_spi.protocols.types.protocol_service_types import (
    ProtocolServiceHealthStatus,
    ProtocolServiceInstance,
    ProtocolServiceMetadata,
)

# Re-export from state types
from omnibase_spi.protocols.types.protocol_state_types import (
    ProtocolAction,
    ProtocolActionPayload,
    ProtocolMetadata,
    ProtocolMetadataOperations,
    ProtocolOnexInputState,
    ProtocolOnexOutputState,
    ProtocolState,
    ProtocolSystemEvent,
)

# Re-export from validation types
from omnibase_spi.protocols.types.protocol_validation_types import (
    ProtocolCompatibilityCheck,
    ProtocolHasModelDump,
    ProtocolModelJsonSerializable,
    ProtocolModelValidatable,
    ProtocolPatternChecker,
    ProtocolValidatable,
    ProtocolVersionInfo,
)


@runtime_checkable
class ProtocolGenericCheckpointData(Protocol):
    """Protocol for generic checkpoint data. Deprecated: use ProtocolCheckpointData."""

    checkpoint_id: UUID
    workflow_id: UUID
    data: dict[str, "ContextValue"]
    timestamp: "ProtocolDateTime"
    metadata: dict[str, "ContextValue"]

    async def validate_checkpoint(self) -> bool: ...
    def is_restorable(self) -> bool: ...


@runtime_checkable
class ProtocolGenericStorageCredentials(Protocol):
    """Protocol for generic storage credentials. Deprecated: use ProtocolStorageCredentials."""

    credential_type: str
    data: dict[str, "ContextValue"]

    async def validate_credentials(self) -> bool: ...
    def is_secure(self) -> bool: ...


@runtime_checkable
class ProtocolGenericStorageConfiguration(Protocol):
    """Protocol for generic storage configuration. Deprecated: use ProtocolStorageConfiguration."""

    backend_type: str
    connection_string: str
    options: dict[str, "ContextValue"]
    timeout_seconds: int

    async def validate_configuration(self) -> bool: ...
    async def is_connectable(self) -> bool: ...


@runtime_checkable
class ProtocolGenericStorageResult(Protocol):
    """Protocol for generic storage results. Deprecated: use ProtocolStorageResult."""

    success: bool
    data: dict[str, "ContextValue"] | None
    error_message: str | None
    operation_id: UUID

    async def validate_storage_result(self) -> bool: ...
    def is_successful(self) -> bool: ...


@runtime_checkable
class ProtocolGenericStorageListResult(Protocol):
    """Protocol for generic storage list results. Deprecated: use ProtocolStorageListResult."""

    success: bool
    items: list[dict[str, "ContextValue"]]
    total_count: int
    has_more: bool
    error_message: str | None

    async def validate_list_result(self) -> bool: ...
    def has_items(self) -> bool: ...


@runtime_checkable
class ProtocolGenericStorageHealthStatus(Protocol):
    """Protocol for generic storage health. Deprecated: use ProtocolStorageHealthStatus."""

    is_healthy: bool
    status_details: dict[str, "ContextValue"]
    capacity_info: dict[str, int] | None
    last_check: "ProtocolDateTime"

    async def validate_health_status(self) -> bool: ...
    def is_available(self) -> bool: ...


# Export all for wildcard imports
__all__ = [
    # Base types
    "ContextValue",
    "LiteralAnalyticsMetricType",
    "LiteralAnalyticsTimeWindow",
    "LiteralBaseStatus",
    "LiteralConnectionState",
    "LiteralErrorRecoveryStrategy",
    "LiteralErrorSeverity",
    "LiteralExecutionMode",
    "LiteralHealthCheckLevel",
    "LiteralHealthDimension",
    "LiteralHealthStatus",
    "LiteralLogLevel",
    "LiteralNodeStatus",
    "LiteralNodeType",
    "LiteralOperationStatus",
    "LiteralPerformanceCategory",
    "LiteralRetryBackoffStrategy",
    "LiteralRetryCondition",
    "LiteralTimeBasedType",
    "LiteralValidationCategory",
    "LiteralValidationLevel",
    "LiteralValidationMode",
    "LiteralValidationSeverity",
    # State
    "ProtocolAction",
    "ProtocolActionPayload",
    # Analytics
    "ProtocolAnalyticsMetric",
    "ProtocolAnalyticsProvider",
    "ProtocolAnalyticsSummary",
    # Health
    "ProtocolAuditEvent",
    "ProtocolCacheStatistics",
    # Validation
    "ProtocolCompatibilityCheck",
    "ProtocolConfigValue",
    # Marker
    "ProtocolConfigurable",
    # Connection
    "ProtocolConnectionConfig",
    "ProtocolConnectionStatus",
    "ProtocolContextBooleanValue",
    "ProtocolContextNumericValue",
    "ProtocolContextStringDictValue",
    "ProtocolContextStringListValue",
    "ProtocolContextStringValue",
    "ProtocolContextValue",
    "ProtocolDateTime",
    # Retry
    "ProtocolDuration",
    # Error
    "ProtocolErrorContext",
    "ProtocolErrorInfo",
    "ProtocolErrorResult",
    "ProtocolEventBusProvider",
    "ProtocolExecutable",
    # Legacy storage (deprecated)
    "ProtocolGenericCheckpointData",
    "ProtocolGenericStorageConfiguration",
    "ProtocolGenericStorageCredentials",
    "ProtocolGenericStorageHealthStatus",
    "ProtocolGenericStorageListResult",
    "ProtocolGenericStorageResult",
    "ProtocolHasModelDump",
    "ProtocolHealthCheck",
    "ProtocolHealthMetrics",
    "ProtocolHealthMonitoring",
    "ProtocolIdentifiable",
    # Logging
    "ProtocolLogContext",
    "ProtocolLogEmitter",
    "ProtocolLogEntry",
    "ProtocolMetadata",
    "ProtocolMetadataOperations",
    "ProtocolMetadataProvider",
    "ProtocolMetricsPoint",
    "ProtocolModelJsonSerializable",
    "ProtocolModelValidatable",
    "ProtocolNameable",
    # Node
    "ProtocolNodeConfigurationData",
    "ProtocolNodeInfoLike",
    "ProtocolNodeMetadata",
    "ProtocolNodeMetadataBlock",
    "ProtocolNodeResult",
    "ProtocolOnexInputState",
    "ProtocolOnexOutputState",
    "ProtocolPatternChecker",
    "ProtocolPerformanceMetric",
    "ProtocolPerformanceMetrics",
    "ProtocolRecoveryAction",
    "ProtocolRetryAttempt",
    "ProtocolRetryConfig",
    "ProtocolRetryPolicy",
    "ProtocolRetryResult",
    "ProtocolSchemaObject",
    "ProtocolSemVer",
    "ProtocolSerializable",
    "ProtocolSerializationResult",
    # Service
    "ProtocolServiceHealthStatus",
    "ProtocolServiceInstance",
    "ProtocolServiceMetadata",
    "ProtocolState",
    "ProtocolSupportedMetadataType",
    "ProtocolSupportedPropertyValue",
    "ProtocolSystemEvent",
    "ProtocolTimeBased",
    "ProtocolTimeout",
    "ProtocolTraceSpan",
    "ProtocolValidatable",
    "ProtocolVersionInfo",
]
