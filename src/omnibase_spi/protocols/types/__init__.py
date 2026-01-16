"""
Protocol types for ONEX SPI interfaces.

This package contains comprehensive domain-specific protocol types that define
the contracts for data structures used across ONEX service interfaces. All types
follow the zero-dependency principle and use strong typing without Any.

Key Design Principles:
    - Zero-dependency architecture for SPI purity
    - Strong typing with no Any usage in public interfaces
    - JSON-serializable types for cross-service communication
    - Consistent naming conventions with Protocol prefix
    - Runtime checkable protocols for dynamic validation

Domain Organization:
    - protocol_base_types: Base types, Literals, context values (canonical source)
    - protocol_analytics_types: Analytics and performance protocols
    - protocol_connection_types: Connection protocols
    - protocol_container_types: Dependency injection and service location types
    - protocol_discovery_types: Node and service discovery contracts
    - protocol_error_types: Error handling protocols
    - protocol_event_bus_types: Event messaging and subscription types
    - protocol_file_handling_types: File processing and metadata types
    - protocol_health_types: Health and metrics protocols
    - protocol_logging_types: Logging protocols
    - protocol_marker_types: Marker and base protocols
    - protocol_mcp_types: Model Context Protocol integration types
    - protocol_node_types: Node protocols
    - protocol_retry_types: Retry and timeout protocols
    - protocol_service_types: Service protocols
    - protocol_state_types: State and action protocols
    - protocol_storage_types: Storage and checkpoint types
    - protocol_validation_types: Validation and compatibility protocols
    - protocol_workflow_orchestration_types: Event-driven workflow and FSM types

Usage Examples:
    # Basic type imports
from omnibase_spi.protocols.types import LiteralLogLevel, LiteralHealthStatus, LiteralNodeType

    # Complex protocol imports
from omnibase_spi.protocols.types import (
        ProtocolWorkflowEvent,
        ProtocolMCPToolDefinition,
        ProtocolLogEntry
)

    # Service types disambiguation (available as both generic and specific names)
from omnibase_spi.protocols.types import (
        ProtocolServiceMetadata,                # Generic service metadata
        ProtocolDiscoveryServiceMetadata,      # Service discovery metadata (alias)
        ProtocolServiceInstance,               # Generic service instance
        ProtocolDiscoveryServiceInstance       # Service discovery instance (alias)
)

    # Domain-specific imports
from omnibase_spi.protocols.types.protocol_workflow_orchestration_types import LiteralWorkflowState
from omnibase_spi.protocols.types.protocol_mcp_types import MCPToolType

    # Usage in service implementations
    def log_event(level: LogLevel, message: str) -> ProtocolLogEntry:
        return create_log_entry(level=level, message=message)

    def check_node_health(node_type: LiteralNodeType) -> HealthStatus:
        return get_health_for_node_type(node_type)

Type Safety Features:
    - All protocols use runtime_checkable for isinstance() support
    - Literal types for enumerated values prevent invalid states
    - Union types for polymorphic data while maintaining type safety
    - Optional types for nullable fields with explicit None handling
"""

# NOTE: Method-based protocols like ProtocolConfigurationError,
# ProtocolNodeConfiguration, and ProtocolNodeConfigurationProvider
# are not re-exported here to avoid circular imports.
# Import these directly from omnibase_spi.protocols.core as needed.

# Analytics types
from omnibase_spi.protocols.types.protocol_analytics_types import (
    ProtocolAnalyticsMetric,
    ProtocolAnalyticsProvider,
    ProtocolAnalyticsSummary,
    ProtocolPerformanceMetric,
    ProtocolPerformanceMetrics,
)

# Base types (canonical source) - import directly from protocol_base_types
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

# Connection types
from omnibase_spi.protocols.types.protocol_connection_types import (
    ProtocolConnectionConfig,
    ProtocolConnectionStatus,
)

# Contract protocol
from omnibase_spi.protocols.types.protocol_contract import ProtocolContract

# Error protocol
from omnibase_spi.protocols.types.protocol_error import ProtocolError

# Error types
from omnibase_spi.protocols.types.protocol_error_types import (
    ProtocolErrorContext,
    ProtocolErrorInfo,
    ProtocolErrorResult,
    ProtocolRecoveryAction,
)

# Health types
from omnibase_spi.protocols.types.protocol_health_types import (
    ProtocolAuditEvent,
    ProtocolCacheStatistics,
    ProtocolHealthCheck,
    ProtocolHealthMetrics,
    ProtocolHealthMonitoring,
    ProtocolMetricsPoint,
    ProtocolTraceSpan,
)

# Logging types
from omnibase_spi.protocols.types.protocol_logging_types import (
    ProtocolLogContext,
    ProtocolLogEmitter,
    ProtocolLogEntry,
)

# Marker types
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

# Node types
from omnibase_spi.protocols.types.protocol_node_types import (
    ProtocolNodeConfigurationData,
    ProtocolNodeInfoLike,
    ProtocolNodeMetadata,
    ProtocolNodeMetadataBlock,
    ProtocolNodeResult,
)

# Retry types
from omnibase_spi.protocols.types.protocol_retry_types import (
    ProtocolDuration,
    ProtocolRetryAttempt,
    ProtocolRetryConfig,
    ProtocolRetryPolicy,
    ProtocolRetryResult,
    ProtocolTimeBased,
    ProtocolTimeout,
)

# Schema value protocol
from omnibase_spi.protocols.types.protocol_schema_value import ProtocolSchemaValue

# Service types
from omnibase_spi.protocols.types.protocol_service_types import (
    ProtocolServiceHealthStatus,
    ProtocolServiceInstance,
    ProtocolServiceMetadata,
)

# State types
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

# Storage types
from omnibase_spi.protocols.types.protocol_storage_types import (
    ProtocolCheckpointData,
    ProtocolStorageConfiguration,
    ProtocolStorageCredentials,
    ProtocolStorageHealthStatus,
    ProtocolStorageListResult,
    ProtocolStorageResult,
)

# Validation types
from omnibase_spi.protocols.types.protocol_validation_types import (
    ProtocolCompatibilityCheck,
    ProtocolHasModelDump,
    ProtocolModelJsonSerializable,
    ProtocolModelValidatable,
    ProtocolPatternChecker,
    ProtocolValidatable,
    ProtocolVersionInfo,
)

# Validation types (from validation domain)
from omnibase_spi.protocols.validation.protocol_validation import (
    ProtocolValidationResult,
)

# Disambiguation aliases for service types to avoid naming conflicts
# Core types are for service discovery, container types are for dependency injection
ProtocolDiscoveryServiceMetadata = ProtocolServiceMetadata
ProtocolDiscoveryServiceInstance = ProtocolServiceInstance

# Container types
from omnibase_spi.protocols.types.protocol_container_types import (
    LiteralContainerStatus,
    LiteralDependencyScope,
    LiteralServiceLifecycle,
)

# Discovery types
from omnibase_spi.protocols.types.protocol_discovery_types import (
    CapabilityValue,
    LiteralDiscoveryStatus,
    LiteralHandlerStatus,
    ProtocolDiscoveryNodeInfo,
    ProtocolDiscoveryQuery,
    ProtocolDiscoveryResult,
    ProtocolHandlerCapability,
    ProtocolHandlerRegistration,
)

# Event agent types (also re-exported from protocol_event_bus_types for backward compatibility)
from omnibase_spi.protocols.types.protocol_event_agent_types import (
    ProtocolAgentEvent,
    ProtocolEventBusAgentStatus,
    ProtocolProgressUpdate,
    ProtocolWorkResult,
)

# Event bus types
from omnibase_spi.protocols.types.protocol_event_bus_types import (
    EventStatus,
    LiteralAuthStatus,
    LiteralEventPriority,
    MessageKey,
    ProtocolCompletionData,
    ProtocolEvent,
    ProtocolEventBusConnectionCredentials,
    ProtocolEventBusSystemEvent,
    ProtocolEventData,
    ProtocolEventHeaders,
    ProtocolEventMessage,
    ProtocolEventResult,
    ProtocolEventStringData,
    ProtocolEventStringDictData,
    ProtocolEventStringListData,
    ProtocolEventSubscription,
    ProtocolSecurityContext,
)

# File handling types
from omnibase_spi.protocols.types.protocol_file_handling_types import (
    FileContent,
    LiteralFileOperation,
    LiteralFileStatus,
    ProcessingStatus,
    ProtocolBinaryFileContent,
    ProtocolCanHandleResult,
    ProtocolExtractedBlock,
    ProtocolFileContent,
    ProtocolFileContentObject,
    ProtocolFileFilter,
    ProtocolFileInfo,
    ProtocolFileMetadata,
    ProtocolFileMetadataOperations,
    ProtocolFileTypeResult,
    ProtocolHandlerMatch,
    ProtocolHandlerMetadata,
    ProtocolProcessingResult,
    ProtocolResult,
    ProtocolResultData,
    ProtocolResultOperations,
    ProtocolSerializedBlock,
    ProtocolStringFileContent,
)

# MCP types
from omnibase_spi.protocols.types.protocol_mcp_types import (
    LiteralMCPConnectionStatus,
    LiteralMCPExecutionStatus,
    LiteralMCPLifecycleState,
    LiteralMCPParameterType,
    LiteralMCPSubsystemType,
    LiteralMCPToolType,
    ProtocolMCPDiscoveryInfo,
    ProtocolMCPHealthCheck,
    ProtocolMCPRegistryConfig,
    ProtocolMCPRegistryMetrics,
    ProtocolMCPRegistryStatus,
    ProtocolMCPSubsystemMetadata,
    ProtocolMCPSubsystemRegistration,
    ProtocolMCPToolDefinition,
    ProtocolMCPToolExecution,
    ProtocolMCPToolParameter,
    ProtocolMCPValidationError,
    ProtocolMCPValidationResult,
)

# Workflow orchestration types
from omnibase_spi.protocols.types.protocol_workflow_orchestration_types import (
    LiteralExecutionSemantics,
    LiteralIsolationLevel,
    LiteralRetryPolicy,
    LiteralTaskPriority,
    LiteralTaskState,
    LiteralTaskType,
    LiteralTimeoutType,
    LiteralWorkflowEventType,
    LiteralWorkflowState,
    ProtocolCompensationAction,
    ProtocolEventProjection,
    ProtocolEventStream,
    ProtocolNodeCapability,
    ProtocolRecoveryPoint,
    ProtocolReplayStrategy,
    ProtocolRetryConfiguration,
    ProtocolTaskConfiguration,
    ProtocolTaskDependency,
    ProtocolTaskResult,
    ProtocolTimeoutConfiguration,
    ProtocolTypedWorkflowData,
    ProtocolWorkflowContext,
    ProtocolWorkflowDefinition,
    ProtocolWorkflowEvent,
    ProtocolWorkflowMetadata,
    ProtocolWorkflowNumericValue,
    ProtocolWorkflowServiceInstance,
    ProtocolWorkflowSnapshot,
    ProtocolWorkflowStringDictValue,
    ProtocolWorkflowStringListValue,
    ProtocolWorkflowStringValue,
    ProtocolWorkflowStructuredValue,
    ProtocolWorkflowValue,
)

__all__ = [
    "CapabilityValue",
    "ContextValue",
    "EventStatus",
    "FileContent",
    "LiteralAnalyticsMetricType",
    "LiteralAnalyticsTimeWindow",
    "LiteralAuthStatus",
    "LiteralBaseStatus",
    "LiteralConnectionState",
    "LiteralContainerStatus",
    "LiteralDependencyScope",
    "LiteralDiscoveryStatus",
    "LiteralErrorRecoveryStrategy",
    "LiteralErrorSeverity",
    "LiteralEventPriority",
    "LiteralExecutionMode",
    "LiteralExecutionSemantics",
    "LiteralFileOperation",
    "LiteralFileStatus",
    "LiteralHandlerStatus",
    "LiteralHealthCheckLevel",
    "LiteralHealthDimension",
    "LiteralHealthStatus",
    "LiteralIsolationLevel",
    "LiteralLogLevel",
    "LiteralMCPConnectionStatus",
    "LiteralMCPExecutionStatus",
    "LiteralMCPLifecycleState",
    "LiteralMCPParameterType",
    "LiteralMCPSubsystemType",
    "LiteralMCPToolType",
    "LiteralNodeStatus",
    "LiteralNodeType",
    "LiteralOperationStatus",
    "LiteralPerformanceCategory",
    "LiteralRetryBackoffStrategy",
    "LiteralRetryCondition",
    "LiteralRetryPolicy",
    "LiteralServiceLifecycle",
    "LiteralTaskPriority",
    "LiteralTaskState",
    "LiteralTaskType",
    "LiteralTimeBasedType",
    "LiteralTimeoutType",
    "LiteralValidationCategory",
    "LiteralValidationLevel",
    "LiteralValidationMode",
    "LiteralValidationSeverity",
    "LiteralWorkflowEventType",
    "LiteralWorkflowState",
    "MessageKey",
    "ProcessingStatus",
    "ProtocolAction",
    "ProtocolActionPayload",
    "ProtocolAgentEvent",
    "ProtocolAnalyticsMetric",
    "ProtocolAnalyticsProvider",
    "ProtocolAnalyticsSummary",
    "ProtocolAuditEvent",
    "ProtocolBinaryFileContent",
    "ProtocolCacheStatistics",
    "ProtocolCanHandleResult",
    "ProtocolCheckpointData",
    "ProtocolCompatibilityCheck",
    "ProtocolCompensationAction",
    "ProtocolCompletionData",
    "ProtocolConfigValue",
    "ProtocolConfigurable",
    "ProtocolConnectionConfig",
    "ProtocolConnectionStatus",
    "ProtocolContextBooleanValue",
    "ProtocolContextNumericValue",
    "ProtocolContextStringDictValue",
    "ProtocolContextStringListValue",
    "ProtocolContextStringValue",
    "ProtocolContextValue",
    "ProtocolContract",
    "ProtocolDateTime",
    "ProtocolDiscoveryNodeInfo",
    "ProtocolDiscoveryQuery",
    "ProtocolDiscoveryResult",
    "ProtocolDiscoveryServiceInstance",
    "ProtocolDiscoveryServiceMetadata",
    "ProtocolDuration",
    "ProtocolError",
    "ProtocolErrorContext",
    "ProtocolErrorInfo",
    "ProtocolErrorResult",
    "ProtocolEvent",
    "ProtocolEventBusAgentStatus",
    "ProtocolEventBusConnectionCredentials",
    "ProtocolEventBusSystemEvent",
    "ProtocolEventData",
    "ProtocolEventHeaders",
    "ProtocolEventMessage",
    "ProtocolEventProjection",
    "ProtocolEventResult",
    "ProtocolEventStream",
    "ProtocolEventStringData",
    "ProtocolEventStringDictData",
    "ProtocolEventStringListData",
    "ProtocolEventSubscription",
    "ProtocolExecutable",
    "ProtocolExtractedBlock",
    "ProtocolFileContent",
    "ProtocolFileContentObject",
    "ProtocolFileFilter",
    "ProtocolFileInfo",
    "ProtocolFileMetadata",
    "ProtocolFileMetadataOperations",
    "ProtocolFileTypeResult",
    "ProtocolHandlerCapability",
    "ProtocolHandlerMatch",
    "ProtocolHandlerMetadata",
    "ProtocolHandlerRegistration",
    "ProtocolHasModelDump",
    "ProtocolHealthCheck",
    "ProtocolHealthMetrics",
    "ProtocolHealthMonitoring",
    "ProtocolIdentifiable",
    "ProtocolInputState",
    "ProtocolLogContext",
    "ProtocolLogEmitter",
    "ProtocolLogEntry",
    "ProtocolMCPDiscoveryInfo",
    "ProtocolMCPHealthCheck",
    "ProtocolMCPRegistryConfig",
    "ProtocolMCPRegistryMetrics",
    "ProtocolMCPRegistryStatus",
    "ProtocolMCPSubsystemMetadata",
    "ProtocolMCPSubsystemRegistration",
    "ProtocolMCPToolDefinition",
    "ProtocolMCPToolExecution",
    "ProtocolMCPToolParameter",
    "ProtocolMCPValidationError",
    "ProtocolMCPValidationResult",
    "ProtocolMetadata",
    "ProtocolMetadataOperations",
    "ProtocolMetadataProvider",
    "ProtocolMetricsPoint",
    "ProtocolModelJsonSerializable",
    "ProtocolModelValidatable",
    "ProtocolNameable",
    "ProtocolNodeCapability",
    "ProtocolNodeConfigurationData",
    "ProtocolNodeInfoLike",
    "ProtocolNodeMetadata",
    "ProtocolNodeMetadataBlock",
    "ProtocolNodeResult",
    "ProtocolOutputState",
    "ProtocolPatternChecker",
    "ProtocolPerformanceMetric",
    "ProtocolPerformanceMetrics",
    "ProtocolProcessingResult",
    "ProtocolProgressUpdate",
    "ProtocolRecoveryAction",
    "ProtocolRecoveryPoint",
    "ProtocolReplayStrategy",
    "ProtocolResult",
    "ProtocolResultData",
    "ProtocolResultOperations",
    "ProtocolRetryAttempt",
    "ProtocolRetryConfig",
    "ProtocolRetryConfiguration",
    "ProtocolRetryPolicy",
    "ProtocolRetryResult",
    "ProtocolSchemaObject",
    "ProtocolSchemaValue",
    "ProtocolSecurityContext",
    "ProtocolSemVer",
    "ProtocolSerializable",
    "ProtocolSerializationResult",
    "ProtocolSerializedBlock",
    "ProtocolServiceHealthStatus",
    "ProtocolServiceInstance",
    "ProtocolServiceMetadata",
    "ProtocolState",
    "ProtocolStateSystemEvent",
    "ProtocolStorageConfiguration",
    "ProtocolStorageCredentials",
    "ProtocolStorageHealthStatus",
    "ProtocolStorageListResult",
    "ProtocolStorageResult",
    "ProtocolStringFileContent",
    "ProtocolSupportedMetadataType",
    "ProtocolSupportedPropertyValue",
    "ProtocolTaskConfiguration",
    "ProtocolTaskDependency",
    "ProtocolTaskResult",
    "ProtocolTimeBased",
    "ProtocolTimeout",
    "ProtocolTimeoutConfiguration",
    "ProtocolTraceSpan",
    "ProtocolTypedWorkflowData",
    "ProtocolValidatable",
    "ProtocolValidationResult",
    "ProtocolVersionInfo",
    "ProtocolWorkResult",
    "ProtocolWorkflowContext",
    "ProtocolWorkflowDefinition",
    "ProtocolWorkflowEvent",
    "ProtocolWorkflowMetadata",
    "ProtocolWorkflowNumericValue",
    "ProtocolWorkflowServiceInstance",
    "ProtocolWorkflowSnapshot",
    "ProtocolWorkflowStringDictValue",
    "ProtocolWorkflowStringListValue",
    "ProtocolWorkflowStringValue",
    "ProtocolWorkflowStructuredValue",
    "ProtocolWorkflowValue",
]
