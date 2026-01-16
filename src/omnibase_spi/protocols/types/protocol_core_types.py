"""
Core protocol types re-exported for convenience.

This module re-exports commonly used types from domain-specific modules.
While new code should prefer importing directly from specific domain modules,
these re-exports are maintained for backward compatibility.

Domain modules for direct imports:
- protocol_analytics_types: Analytics and metrics protocols
- protocol_base_types: Base types, Literals, context values (canonical source)
- protocol_connection_types: Connection protocols
- protocol_error_types: Error handling protocols
- protocol_health_types: Health and monitoring protocols
- protocol_logging_types: Logging protocols
- protocol_marker_types: Marker and interface protocols
- protocol_node_types: Node metadata protocols
- protocol_retry_types: Retry and timeout protocols
- protocol_service_types: Service protocols
- protocol_state_types: State and action protocols
- protocol_storage_types: Storage and checkpoint protocols
- protocol_validation_types: Validation protocols
"""

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
    ProtocolInputState,
    ProtocolMetadata,
    ProtocolMetadataOperations,
    ProtocolOutputState,
    ProtocolState,
    ProtocolStateSystemEvent,
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
    "ProtocolExecutable",
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
    "ProtocolInputState",
    "ProtocolOutputState",
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
    "ProtocolStateSystemEvent",
    "ProtocolTimeBased",
    "ProtocolTimeout",
    "ProtocolTraceSpan",
    "ProtocolValidatable",
    "ProtocolVersionInfo",
]
