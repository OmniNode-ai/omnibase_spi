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
    """
    Protocol for error context information in distributed operations.

    Captures the full context of an error occurrence including correlation
    tracking, operation identification, timing, and debugging information.
    Essential for error tracing across distributed services and debugging.

    Attributes:
        correlation_id: UUID linking related operations across services.
        operation_name: Name of the operation that failed.
        timestamp: When the error occurred.
        context_data: Additional context as key-value pairs.
        stack_trace: Optional stack trace for debugging.

    Example:
        ```python
        from uuid import uuid4
        from datetime import datetime

        class ErrorContext:
            correlation_id: UUID = uuid4()
            operation_name: str = "process_workflow"
            timestamp: ProtocolDateTime
            context_data: dict[str, ContextValue] = {"step": 3, "total": 5}
            stack_trace: str | None = "Traceback (most recent call last)..."

            async def validate_error_context(self) -> bool:
                return self.operation_name and self.correlation_id

            def has_trace(self) -> bool:
                return self.stack_trace is not None

        ctx = ErrorContext()
        assert isinstance(ctx, ProtocolErrorContext)
        assert ctx.has_trace()
        ```
    """

    correlation_id: UUID
    operation_name: str
    timestamp: "ProtocolDateTime"
    context_data: dict[str, "ContextValue"]
    stack_trace: str | None

    async def validate_error_context(self) -> bool: ...

    def has_trace(self) -> bool: ...


@runtime_checkable
class ProtocolRecoveryAction(Protocol):
    """
    Protocol for error recovery action configuration and execution.

    Defines a recovery strategy for handling errors including retry behavior,
    timeout configuration, and fallback values. Enables automated error
    recovery in distributed workflows with configurable strategies.

    Attributes:
        action_type: Recovery strategy type (retry, skip, fail, fallback, escalate).
        max_attempts: Maximum number of recovery attempts.
        backoff_multiplier: Multiplier for exponential backoff delays.
        timeout_seconds: Maximum time for recovery operations.
        fallback_value: Optional fallback value if recovery fails.

    Example:
        ```python
        class RecoveryAction:
            action_type: LiteralErrorRecoveryStrategy = "retry"
            max_attempts: int = 3
            backoff_multiplier: float = 2.0
            timeout_seconds: int = 60
            fallback_value: ContextValue | None = {"default": True}

            async def validate_recovery_action(self) -> bool:
                return self.max_attempts > 0 and self.timeout_seconds > 0

            def is_applicable(self) -> bool:
                return self.action_type != "skip"

        action = RecoveryAction()
        assert isinstance(action, ProtocolRecoveryAction)
        assert action.action_type == "retry"
        assert action.is_applicable()
        ```
    """

    action_type: LiteralErrorRecoveryStrategy
    max_attempts: int
    backoff_multiplier: float
    timeout_seconds: int
    fallback_value: ContextValue | None

    async def validate_recovery_action(self) -> bool: ...

    def is_applicable(self) -> bool: ...


@runtime_checkable
class ProtocolErrorResult(Protocol):
    """
    Protocol for comprehensive standardized error results.

    Provides complete error information including identification, severity,
    retry configuration, and associated recovery actions. Used as the
    standard error representation across ONEX services and workflows.

    Attributes:
        error_id: Unique identifier for this error instance.
        error_type: Classification of the error type.
        message: Human-readable error description.
        severity: Error severity level (critical, warning, info, debug).
        retryable: Whether the operation can be retried.
        recovery_action: Optional configured recovery action.
        context: Full error context with correlation and trace info.

    Example:
        ```python
        from uuid import uuid4

        class ErrorResult:
            error_id: UUID = uuid4()
            error_type: str = "TimeoutError"
            message: str = "Operation timed out after 30 seconds"
            severity: LiteralErrorSeverity = "warning"
            retryable: bool = True
            recovery_action: ProtocolRecoveryAction | None = None
            context: ProtocolErrorContext

            async def validate_error(self) -> bool:
                return self.error_id and self.error_type and self.message

            def is_retryable(self) -> bool:
                return self.retryable

        result = ErrorResult()
        assert isinstance(result, ProtocolErrorResult)
        assert result.is_retryable()
        assert result.severity == "warning"
        ```
    """

    error_id: UUID
    error_type: str
    message: str
    severity: LiteralErrorSeverity
    retryable: bool
    recovery_action: "ProtocolRecoveryAction | None"
    context: "ProtocolErrorContext"

    async def validate_error(self) -> bool: ...

    def is_retryable(self) -> bool: ...
