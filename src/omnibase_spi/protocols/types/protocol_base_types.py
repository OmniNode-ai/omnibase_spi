"""
Base protocol types for ONEX SPI interfaces.

Domain: Base types, context values, and literal type definitions.

This module contains foundational protocol definitions that other protocol
modules depend on. It includes:
- ProtocolSemVer for semantic versioning
- ProtocolDateTime type alias
- All Literal type aliases for constrained string values
- Context value protocols for typed context data
- Metadata and configuration value protocols
"""

from datetime import datetime
from typing import Literal, Protocol, runtime_checkable

# ==============================================================================
# Semantic Versioning Protocol
# ==============================================================================


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


# ==============================================================================
# DateTime Type Alias
# ==============================================================================

ProtocolDateTime = datetime

# ==============================================================================
# Literal Type Definitions
# ==============================================================================

# Logging
LiteralLogLevel = Literal[
    "TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "FATAL"
]

# Node Types
LiteralNodeType = Literal["COMPUTE", "EFFECT", "REDUCER", "ORCHESTRATOR"]

# Health Status
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

# Base and Node Status
LiteralBaseStatus = Literal[
    "pending", "processing", "completed", "failed", "cancelled", "skipped"
]
LiteralNodeStatus = Literal["active", "inactive", "error", "pending"]

# Execution and Operation
LiteralExecutionMode = Literal["direct", "inmemory", "kafka"]
LiteralOperationStatus = Literal[
    "success", "failed", "in_progress", "cancelled", "pending"
]

# Validation
LiteralValidationLevel = Literal["BASIC", "STANDARD", "COMPREHENSIVE", "PARANOID"]
LiteralValidationMode = Literal[
    "strict", "lenient", "smoke", "regression", "integration"
]
LiteralValidationSeverity = Literal["error", "warning", "info"]
LiteralValidationCategory = Literal[
    "syntax", "semantic", "style", "security", "performance"
]

# Health Check
LiteralHealthCheckLevel = Literal[
    "quick", "basic", "standard", "thorough", "comprehensive"
]
LiteralHealthDimension = Literal[
    "availability", "performance", "functionality", "data_integrity", "security"
]

# Error Handling
LiteralErrorRecoveryStrategy = Literal[
    "retry", "fallback", "abort", "circuit_breaker", "compensation"
]
LiteralErrorSeverity = Literal["low", "medium", "high", "critical"]

# Retry Strategies
LiteralRetryBackoffStrategy = Literal[
    "fixed", "linear", "exponential", "fibonacci", "jitter"
]
LiteralRetryCondition = Literal[
    "always", "never", "on_error", "on_timeout", "on_network", "on_transient"
]

# Time-Based Operations
LiteralTimeBasedType = Literal["duration", "timeout", "interval", "deadline"]

# Analytics
LiteralAnalyticsTimeWindow = Literal[
    "real_time", "hourly", "daily", "weekly", "monthly"
]
LiteralAnalyticsMetricType = Literal["counter", "gauge", "histogram", "summary"]

# Performance
LiteralPerformanceCategory = Literal[
    "latency", "throughput", "resource", "error", "availability"
]

# Connection
LiteralConnectionState = Literal[
    "disconnected", "connecting", "connected", "reconnecting", "failed", "closing"
]


# ==============================================================================
# Context Value Protocols
# ==============================================================================


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


# Type alias for any context value
ContextValue = ProtocolContextValue


# ==============================================================================
# Metadata Type Protocols
# ==============================================================================


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


# ==============================================================================
# Configuration Value Protocol
# ==============================================================================


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
