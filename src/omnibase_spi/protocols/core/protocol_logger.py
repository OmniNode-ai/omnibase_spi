"""Protocol for structured logging with distributed tracing support."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable
from uuid import UUID

if TYPE_CHECKING:
    from omnibase_spi.protocols.types import ProtocolLogEntry

from omnibase_spi.protocols.types import LiteralLogLevel, ProtocolLogContext


@runtime_checkable
class ProtocolLogger(Protocol):
    """Protocol for structured logging with distributed tracing support.

    Defines the contract for all logging implementations in the ONEX ecosystem,
    ensuring consistent logging patterns, structured data capture, and correlation
    ID tracking for distributed system observability.

    The logger protocol provides both simple emission (emit) and structured entry
    logging (log) interfaces, supporting correlation tracking, contextual metadata,
    and level-based filtering for production observability.

    Example:
        ```python
        from uuid import uuid4
        from omnibase_spi.protocols.core import ProtocolLogger
        from omnibase_spi.protocols.types import LiteralLogLevel

        logger: ProtocolLogger = get_logger()

        # Simple structured logging with correlation
        correlation_id = uuid4()
        await logger.emit(
            level="info",
            message="User registration completed",
            correlation_id=correlation_id,
            context={"user_id": "user_123", "email": "user@example.com"}
        )

        # Structured log entry with full metadata
        log_entry = create_log_entry(
            level="error",
            message="Database connection failed",
            correlation_id=correlation_id,
            error_details={"host": "db.example.com", "port": 5432}
        )
        await logger.log(log_entry)

        # Check if level is enabled before expensive operations
        if await logger.is_level_enabled("debug"):
            debug_data = compute_expensive_debug_info()
            await logger.emit("debug", f"Debug info: {debug_data}", correlation_id)
        ```

    Key Features:
        - Structured logging with typed log levels
        - Distributed tracing via correlation IDs
        - Contextual metadata attachment
        - Level-based filtering for performance
        - Async-first design for non-blocking logging
        - Integration with ONEX observability stack

    Log Levels (from protocol_core_types):
        - "debug": Detailed diagnostic information
        - "info": General informational messages
        - "warning": Warning messages for potential issues
        - "error": Error messages for failures
        - "critical": Critical failures requiring immediate attention

    See Also:
        - ProtocolLogEntry: Structured log entry type definition
        - ProtocolLogContext: Contextual metadata for log entries
        - ProtocolObservability: Observability and monitoring protocols
        - ProtocolDistributedTracing: Distributed tracing integration
    """

    async def emit(
        self,
        level: LiteralLogLevel,
        message: str,
        correlation_id: UUID,
        context: ProtocolLogContext | None = None,
    ) -> None:
        """Emit a structured log message with correlation tracking.

        Performs structured logging with the specified level, message, and correlation
        ID for distributed tracing. Optional context provides additional metadata for
        enhanced observability.

        Args:
            level: Log level from LiteralLogLevel ("debug", "info", "warning", "error", "critical")
            message: Log message content
            correlation_id: UUID for distributed trace correlation
            context: Optional contextual metadata (user_id, request_id, etc.)

        Example:
            ```python
            await logger.emit(
                level="info",
                message="Processing workflow started",
                correlation_id=uuid4(),
                context={"workflow_type": "data_pipeline", "instance_id": "wp_123"}
            )
            ```
        """
        ...

    async def log(self, entry: ProtocolLogEntry) -> None:
        """Log a pre-structured log entry with full metadata.

        Performs structured logging using a complete log entry object that includes
        all metadata, timestamps, and contextual information. Use this method when
        you need full control over log entry structure.

        Args:
            entry: Complete log entry with level, message, correlation, and metadata

        Example:
            ```python
            from omnibase_spi.protocols.types import ProtocolLogEntry

            log_entry = create_log_entry(
                level="error",
                message="Failed to process event",
                correlation_id=correlation_id,
                metadata={
                    "event_type": "workflow.started",
                    "error_code": "E001",
                    "retry_count": 3
                }
            )
            await logger.log(log_entry)
            ```
        """
        ...

    async def is_level_enabled(self, level: LiteralLogLevel) -> bool:
        """Check if a log level is currently enabled.

        Determines whether logging at the specified level is currently enabled,
        allowing callers to skip expensive log message construction when the
        level is disabled for performance optimization.

        Args:
            level: Log level to check ("debug", "info", "warning", "error", "critical")

        Returns:
            True if the level is enabled, False otherwise

        Example:
            ```python
            # Avoid expensive computation if debug is disabled
            if await logger.is_level_enabled("debug"):
                detailed_state = serialize_complex_object(state)
                await logger.emit("debug", f"State: {detailed_state}", correlation_id)
            ```
        """
        ...
