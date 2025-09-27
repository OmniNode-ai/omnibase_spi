from typing import Optional, Protocol, runtime_checkable
from uuid import UUID

from omnibase_spi.protocols.types import (
    LiteralLogLevel,
    ProtocolLogContext,
    ProtocolLogEntry,
)


@runtime_checkable
class ProtocolLogger(Protocol):
    """
    Protocol for ONEX logging services that can be resolved from the registry.

    This protocol defines the interface that all logging implementations must
    implement to be compatible with the ONEX logging system.

    Example:
        class MyLogger:
            def emit(self, level: LiteralLogLevel, message: str, correlation_id: UUID) -> None:
                ...

            def log(self, entry: "ProtocolLogEntry") -> None:
                ...
    """

    def emit(
        self,
        level: LiteralLogLevel,
        message: str,
        correlation_id: UUID,
        context: "ProtocolLogContext | None" = None,
    ) -> None:
        """
        Emit a log event with the specified level and message.

        Args:
            level: Log level for the message
            message: Log message to emit
            correlation_id: Correlation ID for request tracking
            context: Optional log context for additional metadata
        """
        ...

    def log(self, entry: "ProtocolLogEntry") -> None:
        """
        Log a structured log entry.

        Args:
            entry: Structured log entry to emit
        """
        ...

    def is_level_enabled(self, level: LiteralLogLevel) -> bool:
        """
        Check if the specified log level is enabled.

        Args:
            level: Log level to check

        Returns:
            True if the level should be logged, False otherwise
        """
        ...
