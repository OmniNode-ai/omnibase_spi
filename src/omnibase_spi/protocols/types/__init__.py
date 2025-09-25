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

# Core types
from omnibase_spi.protocols.types.protocol_core_types import (
    ContextValue,
    LiteralBaseStatus,
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
    LiteralValidationLevel,
    LiteralValidationMode,
    ProtocolAction,
    ProtocolActionPayload,
    ProtocolAuditEvent,
    ProtocolCacheStatistics,
    ProtocolCheckpointData,
    ProtocolCompatibilityCheck,
    ProtocolConfigurable,
    ProtocolConfigValue,
    ProtocolContextBooleanValue,
    ProtocolContextNumericValue,
    ProtocolContextStringDictValue,
    ProtocolContextStringListValue,
    ProtocolContextStringValue,
    ProtocolContextValue,
    ProtocolDateTime,
    ProtocolErrorContext,
    ProtocolErrorInfo,
    ProtocolErrorResult,
    ProtocolExecutable,
    ProtocolHealthCheck,
    ProtocolHealthMetrics,
    ProtocolHealthMonitoring,
    ProtocolIdentifiable,
    ProtocolLogContext,
    ProtocolLogEntry,
    ProtocolMetadata,
    ProtocolMetadataOperations,
    ProtocolMetadataProvider,
    ProtocolMetricsPoint,
    ProtocolNameable,
    ProtocolNodeInfoLike,
    ProtocolNodeMetadata,
    ProtocolNodeMetadataBlock,
    ProtocolNodeResult,
    ProtocolRecoveryAction,
    ProtocolSchemaObject,
    ProtocolSemVer,
    ProtocolSerializable,
    ProtocolSerializationResult,
    ProtocolServiceHealthStatus,
    ProtocolServiceInstance,
    ProtocolServiceMetadata,
    ProtocolState,
    ProtocolStorageConfiguration,
    ProtocolStorageCredentials,
    ProtocolStorageHealthStatus,
    ProtocolStorageListResult,
    ProtocolStorageResult,
    ProtocolSupportedMetadataType,
    ProtocolSupportedPropertyValue,
    ProtocolSystemEvent,
    ProtocolTraceSpan,
    ProtocolValidatable,
    ProtocolValidationResult,
    ProtocolVersionInfo,
)

# Disambiguation aliases for service types to avoid naming conflicts
# Core types are for service discovery, container types are for dependency injection
ProtocolDiscoveryServiceMetadata = ProtocolServiceMetadata
ProtocolDiscoveryServiceInstance = ProtocolServiceInstance

# Discovery types
from omnibase_spi.protocols.types.protocol_discovery_types import (
    CapabilityValue,
    LiteralDiscoveryStatus,
    LiteralHandlerStatus,
    ProtocolDiscoveryQuery,
    ProtocolDiscoveryResult,
    ProtocolHandlerCapability,
    ProtocolHandlerInfo,
    ProtocolHandlerRegistration,
)

# Event bus types
from omnibase_spi.protocols.types.protocol_event_bus_types import (
    EventStatus,
    LiteralAuthStatus,
    LiteralEventPriority,
    ProtocolEvent,
    ProtocolEventData,
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
    ProtocolServiceDiscovery,
    ProtocolTaskConfiguration,
    ProtocolTaskDependency,
    ProtocolTaskResult,
    ProtocolTimeoutConfiguration,
    ProtocolWorkflowContext,
    ProtocolWorkflowDefinition,
    ProtocolWorkflowEvent,
    ProtocolWorkflowMetadata,
    ProtocolWorkflowNumericValue,
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
    "LiteralDiscoveryStatus",
    "LiteralAuthStatus",
    "LiteralBaseStatus",
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
    "ProcessingStatus",
    "ProtocolAction",
    "ProtocolActionPayload",
    "ProtocolAuditEvent",
    "ProtocolCacheStatistics",
    "ProtocolCanHandleResult",
    "ProtocolCheckpointData",
    "ProtocolCompatibilityCheck",
    "ProtocolCompensationAction",
    "ProtocolConfigurable",
    "ProtocolConfigValue",
    "ProtocolContextBooleanValue",
    "ProtocolContextNumericValue",
    "ProtocolContextStringDictValue",
    "ProtocolContextStringListValue",
    "ProtocolContextStringValue",
    "ProtocolContextValue",
    "ProtocolDateTime",
    "ProtocolDiscoveryQuery",
    "ProtocolDiscoveryResult",
    "ProtocolDiscoveryServiceInstance",
    "ProtocolDiscoveryServiceMetadata",
    "ProtocolErrorContext",
    "ProtocolErrorInfo",
    "ProtocolErrorResult",
    "ProtocolEvent",
    "ProtocolEventData",
    "ProtocolEventStringData",
    "ProtocolEventStringListData",
    "ProtocolEventStringDictData",
    "ProtocolEventProjection",
    "ProtocolEventResult",
    "ProtocolEventStream",
    "ProtocolEventSubscription",
    "ProtocolExecutable",
    "ProtocolExtractedBlock",
    "ProtocolBinaryFileContent",
    "ProtocolFileContent",
    "ProtocolFileContentObject",
    "ProtocolFileFilter",
    "ProtocolStringFileContent",
    "ProtocolFileInfo",
    "ProtocolFileMetadata",
    "ProtocolFileMetadataOperations",
    "ProtocolFileTypeResult",
    "ProtocolHandlerCapability",
    "ProtocolHandlerInfo",
    "ProtocolHandlerMatch",
    "ProtocolHandlerMetadata",
    "ProtocolHandlerRegistration",
    "ProtocolHealthCheck",
    "ProtocolHealthMetrics",
    "ProtocolHealthMonitoring",
    "ProtocolIdentifiable",
    "ProtocolLogContext",
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
    "ProtocolNameable",
    "ProtocolNodeCapability",
    "ProtocolNodeInfoLike",
    "ProtocolNodeMetadata",
    "ProtocolNodeMetadataBlock",
    "ProtocolNodeResult",
    "ProtocolOnexResult",
    "ProtocolProcessingResult",
    "ProtocolRecoveryAction",
    "ProtocolRecoveryPoint",
    "ProtocolReplayStrategy",
    "ProtocolResultData",
    "ProtocolResultOperations",
    "ProtocolRetryConfiguration",
    "ProtocolSchemaObject",
    "ProtocolSecurityContext",
    "ProtocolSemVer",
    "ProtocolSerializable",
    "ProtocolSerializationResult",
    "ProtocolSerializedBlock",
    "ProtocolServiceDiscovery",
    "ProtocolServiceHealthStatus",
    "ProtocolServiceInstance",
    "ProtocolServiceMetadata",
    "ProtocolState",
    "ProtocolStorageConfiguration",
    "ProtocolStorageCredentials",
    "ProtocolStorageHealthStatus",
    "ProtocolStorageListResult",
    "ProtocolStorageResult",
    "ProtocolSupportedMetadataType",
    "ProtocolSupportedPropertyValue",
    "ProtocolSystemEvent",
    "ProtocolTaskConfiguration",
    "ProtocolTaskDependency",
    "ProtocolTaskResult",
    "ProtocolTimeoutConfiguration",
    "ProtocolTraceSpan",
    "ProtocolValidatable",
    "ProtocolValidationResult",
    "ProtocolVersionInfo",
    "ProtocolWorkflowContext",
    "ProtocolWorkflowDefinition",
    "ProtocolWorkflowEvent",
    "ProtocolWorkflowMetadata",
    "ProtocolWorkflowSnapshot",
    "ProtocolWorkflowValue",
    "ProtocolWorkflowStringValue",
    "ProtocolWorkflowStringListValue",
    "ProtocolWorkflowStringDictValue",
    "ProtocolWorkflowNumericValue",
    "ProtocolWorkflowStructuredValue",
    "LiteralRetryPolicy",
    "LiteralTaskPriority",
    "LiteralTaskState",
    "LiteralTaskType",
    "LiteralTimeoutType",
    "LiteralValidationLevel",
    "LiteralValidationMode",
    "LiteralWorkflowEventType",
    "LiteralWorkflowState",
]
