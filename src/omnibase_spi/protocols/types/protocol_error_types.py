"""
Error handling protocol types for ONEX SPI interfaces.

Domain: Error handling, recovery strategies, and error context management.
"""

from typing import Protocol, runtime_checkable
from uuid import UUID

from omnibase_spi.protocols.types.protocol_base_types import (
    ContextValue,
    LiteralErrorRecoveryStrategy,
    LiteralErrorSeverity,
    ProtocolDateTime,
)


@runtime_checkable
class ProtocolErrorInfo(Protocol):
    """
    Protocol for comprehensive error information in workflow results.

    Provides detailed error context for workflow operations, including
    recovery strategies and retry configuration. Essential for resilient
    distributed system operation and automated error recovery.

    Key Features:
        - Error type classification for automated handling
        - Human-readable error messages
        - Stack trace information for debugging
        - Retry configuration and backoff strategies

    Usage:
        error_info = ProtocolErrorInfo(
            error_type="TimeoutError",
            message="Operation timed out after 30 seconds",
            trace=traceback.format_exc(),
            retryable=True,
            backoff_strategy="exponential",
            max_attempts=3
        )

        if error_info.retryable:
            schedule_retry(operation, error_info.backoff_strategy)
    """

    error_type: str
    message: str
    trace: str | None
    retryable: bool
    backoff_strategy: str | None
    max_attempts: int | None

    async def validate_error_info(self) -> bool: ...

    def is_retryable(self) -> bool: ...


@runtime_checkable
class ProtocolErrorContext(Protocol):
    """Protocol for error context information."""

    correlation_id: UUID
    operation_name: str
    timestamp: "ProtocolDateTime"
    context_data: dict[str, "ContextValue"]
    stack_trace: str | None

    async def validate_error_context(self) -> bool: ...

    def has_trace(self) -> bool: ...


@runtime_checkable
class ProtocolRecoveryAction(Protocol):
    """Protocol for error recovery action information."""

    action_type: LiteralErrorRecoveryStrategy
    max_attempts: int
    backoff_multiplier: float
    timeout_seconds: int
    fallback_value: ContextValue | None

    async def validate_recovery_action(self) -> bool: ...

    def is_applicable(self) -> bool: ...


@runtime_checkable
class ProtocolErrorResult(Protocol):
    """Protocol for standardized error results."""

    error_id: UUID
    error_type: str
    message: str
    severity: LiteralErrorSeverity
    retryable: bool
    recovery_action: "ProtocolRecoveryAction | None"
    context: "ProtocolErrorContext"

    async def validate_error(self) -> bool: ...

    def is_retryable(self) -> bool: ...
