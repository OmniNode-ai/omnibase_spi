"""
Core protocol types for ONEX SPI interfaces.

Domain: Core system protocols (logging, serialization, validation)
"""

from typing import Any, Dict, Literal, Protocol, Union
from uuid import UUID

# Log level types - using string literals instead of enums
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

# Context value types - more specific than Any
ContextValue = Union[str, int, float, bool, list[str], Dict[str, str]]


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
