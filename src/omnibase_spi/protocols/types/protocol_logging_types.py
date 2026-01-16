"""
Logging protocol types for ONEX SPI interfaces.

Domain: Logging protocols for structured logging, log entries, and log emission.
"""

from typing import Protocol, runtime_checkable
from uuid import UUID

from omnibase_spi.protocols.types.protocol_base_types import (
    ContextValue,
    LiteralLogLevel,
    ProtocolDateTime,
)


@runtime_checkable
class ProtocolLogContext(Protocol):
    """
    Protocol for structured logging context objects.

    Provides standardized context information for distributed logging
    across ONEX services. Context objects carry metadata, correlation
    IDs, and structured data for observability and debugging.

    Key Features:
        - Structured context data with type safety
        - Dictionary conversion for serialization
        - Compatible with typed ContextValue constraints
        - Supports distributed tracing and correlation

    Usage:
        context = create_log_context()
        logger.info("Operation completed", context=context.to_dict())
    """

    def to_dict(self) -> dict[str, "ContextValue"]:
        """Convert the log context to a dictionary representation.

        Serializes all context key-value pairs for use in log entries
        or transmission to logging backends.

        Returns:
            Dictionary mapping context keys to their typed values.
        """
        ...


@runtime_checkable
class ProtocolLogEntry(Protocol):
    """
    Protocol for structured log entry objects in ONEX systems.

    Standardizes log entries across all ONEX services with consistent
    structure for level, messaging, correlation tracking, and context.
    Essential for distributed system observability and debugging.

    Key Features:
        - Standardized log levels (TRACE through FATAL)
        - Correlation ID for distributed tracing
        - Structured context with type safety
        - Timestamp for chronological ordering

    Usage:
        entry = create_log_entry(
            level="INFO",
            message="User authenticated successfully",
            correlation_id=request.correlation_id,
            context={"user_id": user.id, "action": "login"}
        )
    """

    level: LiteralLogLevel
    message: str
    correlation_id: UUID
    timestamp: "ProtocolDateTime"
    context: dict[str, "ContextValue"]

    async def validate_log_entry(self) -> bool: ...

    def is_complete(self) -> bool: ...


@runtime_checkable
class ProtocolLogEmitter(Protocol):
    """
    Protocol for objects that can emit structured log events.

    Provides standardized logging interface for ONEX services with
    structured logging support. Enables consistent log emission across
    all system components.

    Key Features:
        - Structured logging with log levels
        - Consistent log data format
        - Integration with ONEX logging infrastructure
        - Type-safe log emission

    Usage:
        def log_operation(emitter: ProtocolLogEmitter, message: str):
            emitter.emit_log_event(
                level="INFO",
                message=message,
                data=log_data
            )
    """

    def emit_log_event(
        self,
        level: LiteralLogLevel,
        message: str,
        data: object,  # MixinLogData type from mixins
    ) -> None: ...
