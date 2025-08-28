"""
Core protocol types for ONEX SPI interfaces.

Domain: Core system protocols (logging, serialization, validation)
"""

from typing import Dict, Literal, Protocol, Union
from uuid import UUID

# Log level types - using string literals instead of enums
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

# Context value types - specific typed values for logging context
ContextValue = Union[str, int, float, bool, list[str], Dict[str, str]]


# Configuration value protocol - for type-safe configuration
class ProtocolConfigValue(Protocol):
    """Protocol for configuration values with type safety."""

    def get_string(self) -> str:
        ...

    def get_int(self) -> int:
        ...

    def get_float(self) -> float:
        ...

    def get_bool(self) -> bool:
        ...

    def get_list(self) -> list[str]:
        ...


# Core logging protocols
class ProtocolLogContext(Protocol):
    """Protocol for log context objects."""

    def to_dict(self) -> Dict[str, ContextValue]:
        """Convert context to dictionary with typed values."""
        ...


class ProtocolLogEntry(Protocol):
    """Protocol for log entry objects."""

    level: LogLevel
    message: str
    correlation_id: UUID
    timestamp: float
    context: Dict[str, ContextValue]


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
    metadata: Dict[str, ContextValue]


# Core validation protocols
class ProtocolValidationResult(Protocol):
    """Protocol for validation results."""

    is_valid: bool
    errors: list[str]
    warnings: list[str]


# Status types
NodeStatus = Literal["active", "inactive", "error", "pending"]


# Metadata protocols for type safety
class ProtocolMetadata(Protocol):
    """Protocol for structured metadata."""

    def get_value(self, key: str) -> ContextValue:
        ...

    def has_key(self, key: str) -> bool:
        ...

    def keys(self) -> list[str]:
        ...


# Reducer protocol types with stronger typing
class ProtocolActionPayload(Protocol):
    """Protocol for action payload with specific data."""

    target_id: str
    operation: str
    parameters: Dict[str, ContextValue]


class ProtocolAction(Protocol):
    """Protocol for reducer actions."""

    type: str
    payload: ProtocolActionPayload
    timestamp: float


class ProtocolState(Protocol):
    """Protocol for reducer state."""

    metadata: ProtocolMetadata
    version: int
    last_updated: float
