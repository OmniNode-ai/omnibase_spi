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
    - protocol_core_types: System-wide types (logging, validation, health, metadata)
    - protocol_discovery_types: Node and service discovery contracts
    - protocol_event_bus_types: Event messaging and subscription types
    - protocol_file_handling_types: File processing and metadata types
    - protocol_mcp_types: Model Context Protocol integration types
    - protocol_workflow_orchestration_types: Event-driven workflow and FSM types
    - protocol_container_types: Dependency injection and service location types

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

# Contract protocol
from omnibase_spi.protocols.types.protocol_contract import ProtocolContract

# Core types
from omnibase_spi.protocols.types.protocol_core_types import (  # Migrated from omnibase_core
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
    ProtocolAction,
    ProtocolActionPayload,
    ProtocolAnalyticsMetric,
    ProtocolAnalyticsProvider,
    ProtocolAnalyticsSummary,
    ProtocolAuditEvent,
    ProtocolCacheStatistics,
    ProtocolCompatibilityCheck,
    ProtocolConfigurable,
    ProtocolConfigValue,
    ProtocolConnectionConfig,
    ProtocolConnectionStatus,
    ProtocolContextBooleanValue,
    ProtocolContextNumericValue,
    ProtocolContextStringDictValue,
    ProtocolContextStringListValue,
    ProtocolContextStringValue,
    ProtocolContextValue,
    ProtocolDateTime,
    ProtocolDuration,
    ProtocolErrorContext,
    ProtocolErrorInfo,
    ProtocolErrorResult,
    ProtocolExecutable,
    ProtocolHasModelDump,
    ProtocolHealthCheck,
    ProtocolHealthMetrics,
    ProtocolHealthMonitoring,
    ProtocolIdentifiable,
    ProtocolLogContext,
    ProtocolLogEmitter,
    ProtocolLogEntry,
    ProtocolMetadata,
    ProtocolMetadataOperations,
    ProtocolMetadataProvider,
    ProtocolMetricsPoint,
    ProtocolModelJsonSerializable,
    ProtocolModelValidatable,
    ProtocolNameable,
    ProtocolNodeInfoLike,
    ProtocolNodeMetadata,
    ProtocolNodeMetadataBlock,
    ProtocolNodeResult,
    ProtocolOnexInputState,
    ProtocolOnexOutputState,
    ProtocolPatternChecker,
    ProtocolPerformanceMetric,
    ProtocolPerformanceMetrics,
    ProtocolRecoveryAction,
    ProtocolRetryAttempt,
    ProtocolRetryConfig,
    ProtocolRetryPolicy,
    ProtocolRetryResult,
    ProtocolSchemaObject,
    ProtocolSemVer,
    ProtocolSerializable,
    ProtocolSerializationResult,
    ProtocolServiceHealthStatus,
    ProtocolServiceInstance,
    ProtocolServiceMetadata,
    ProtocolState,
    ProtocolSupportedMetadataType,
    ProtocolSupportedPropertyValue,
    ProtocolSystemEvent,
    ProtocolTimeBased,
    ProtocolTimeout,
    ProtocolTraceSpan,
    ProtocolValidatable,
    ProtocolVersionInfo,
)

# ONEX error protocol
from omnibase_spi.protocols.types.protocol_onex_error import ProtocolOnexError

# Schema value protocol
from omnibase_spi.protocols.types.protocol_schema_value import ProtocolSchemaValue

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
    ProtocolEventData,
    ProtocolEventHeaders,
    ProtocolEventMessage,
    ProtocolEventResult,
    ProtocolEventStringData,
    ProtocolEventStringDictData,
    ProtocolEventStringListData,
    ProtocolEventSubscription,
    ProtocolOnexEvent,
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
    ProtocolOnexResult,
    ProtocolProcessingResult,
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
    "ProtocolErrorContext",
    "ProtocolErrorInfo",
    "ProtocolErrorResult",
    "ProtocolEvent",
    "ProtocolEventBusAgentStatus",
    "ProtocolEventBusConnectionCredentials",
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
    # Migrated from omnibase_core
    "ProtocolHasModelDump",
    "ProtocolHealthCheck",
    "ProtocolHealthMetrics",
    "ProtocolHealthMonitoring",
    "ProtocolIdentifiable",
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
    "ProtocolNodeInfoLike",
    "ProtocolNodeMetadata",
    "ProtocolNodeMetadataBlock",
    "ProtocolNodeResult",
    "ProtocolOnexError",
    "ProtocolOnexEvent",
    "ProtocolOnexInputState",
    "ProtocolOnexOutputState",
    "ProtocolOnexResult",
    "ProtocolPatternChecker",
    "ProtocolPerformanceMetric",
    "ProtocolPerformanceMetrics",
    "ProtocolProcessingResult",
    "ProtocolProgressUpdate",
    "ProtocolRecoveryAction",
    "ProtocolRecoveryPoint",
    "ProtocolReplayStrategy",
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
    "ProtocolStorageConfiguration",
    "ProtocolStorageCredentials",
    "ProtocolStorageHealthStatus",
    "ProtocolStorageListResult",
    "ProtocolStorageResult",
    "ProtocolStringFileContent",
    "ProtocolSupportedMetadataType",
    "ProtocolSupportedPropertyValue",
    "ProtocolSystemEvent",
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
