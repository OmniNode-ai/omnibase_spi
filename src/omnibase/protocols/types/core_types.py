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
