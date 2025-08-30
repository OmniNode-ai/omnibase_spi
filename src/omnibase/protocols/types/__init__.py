"""
Protocol types for ONEX SPI interfaces.

This package contains domain-specific protocol types that define the contracts
for data structures used across ONEX service interfaces. All types follow
the zero-dependency principle and use strong typing without Any.
"""

# Core types
from omnibase.protocols.types.core_types import (
    BaseStatus,
    ContextValue,
    HealthStatus,
    LogLevel,
    NodeStatus,
    ProtocolAction,
    ProtocolActionPayload,
    ProtocolConfigValue,
    ProtocolErrorInfo,
    ProtocolLogContext,
    ProtocolLogEntry,
    ProtocolMetadata,
    ProtocolMetadataOperations,
    ProtocolNodeMetadata,
    ProtocolNodeMetadataBlock,
    ProtocolNodeResult,
    ProtocolSchemaObject,
    ProtocolSerializationResult,
    ProtocolState,
    ProtocolSystemEvent,
    ProtocolValidationResult,
)

# Discovery types
from omnibase.protocols.types.discovery_types import (
    CapabilityValue,
    DiscoveryStatus,
    HandlerStatus,
    ProtocolDiscoveryQuery,
    ProtocolDiscoveryResult,
    ProtocolHandlerCapability,
    ProtocolHandlerInfo,
    ProtocolHandlerRegistration,
)

# Event bus types
from omnibase.protocols.types.event_bus_types import (
    AuthStatus,
    EventData,
    EventStatus,
    ProtocolEvent,
    ProtocolEventResult,
    ProtocolEventSubscription,
    ProtocolSecurityContext,
)

# File handling types
from omnibase.protocols.types.file_handling_types import (
    FileContent,
    FileOperation,
    FileStatus,
    ProcessingStatus,
    ProtocolCanHandleResult,
    ProtocolExtractedBlock,
    ProtocolFileContent,
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
)

__all__ = [
    # Core types
    "BaseStatus",
    "ContextValue",
    "HealthStatus",
    "LogLevel",
    "NodeStatus",
    "ProtocolAction",
    "ProtocolActionPayload",
    "ProtocolConfigValue",
    "ProtocolErrorInfo",
    "ProtocolLogContext",
    "ProtocolLogEntry",
    "ProtocolMetadata",
    "ProtocolMetadataOperations",
    "ProtocolNodeMetadata",
    "ProtocolNodeMetadataBlock",
    "ProtocolNodeResult",
    "ProtocolSchemaObject",
    "ProtocolSerializationResult",
    "ProtocolState",
    "ProtocolSystemEvent",
    "ProtocolValidationResult",
    # Event bus types
    "AuthStatus",
    "EventData",
    "EventStatus",
    "ProtocolEvent",
    "ProtocolEventResult",
    "ProtocolEventSubscription",
    "ProtocolSecurityContext",
    # Discovery types
    "CapabilityValue",
    "DiscoveryStatus",
    "HandlerStatus",
    "ProtocolDiscoveryQuery",
    "ProtocolDiscoveryResult",
    "ProtocolHandlerCapability",
    "ProtocolHandlerInfo",
    "ProtocolHandlerRegistration",
    # File handling types
    "FileContent",
    "FileOperation",
    "FileStatus",
    "ProcessingStatus",
    "ProtocolFileContent",
    "ProtocolFileFilter",
    "ProtocolFileInfo",
    "ProtocolFileTypeResult",
    "ProtocolHandlerMatch",
    "ProtocolProcessingResult",
]
