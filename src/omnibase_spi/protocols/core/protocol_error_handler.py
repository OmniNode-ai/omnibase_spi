"""
Protocol for Standardized Error Handling.

Defines interfaces for error handling, recovery strategies, and observability
across all ONEX services following consistent patterns.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_core_types import (
        LiteralErrorSeverity,
        ProtocolErrorContext,
        ProtocolErrorResult,
        ProtocolRecoveryAction,
    )


@runtime_checkable
class ProtocolErrorHandler(Protocol):
    """
    Protocol for standardized error handling across ONEX services.

    Provides consistent error handling patterns, recovery strategies,
    and observability for distributed system reliability.

    Key Features:
        - Standardized error classification and severity
        - Automatic recovery strategy selection
        - Error context capture and correlation
        - Circuit breaker pattern support
        - Comprehensive error observability

    Usage Example:
        ```python
        # Protocol usage example (SPI-compliant)
        service: "ErrorHandler" = get_error_handler()

        # Usage demonstrates protocol interface without implementation details
        # All operations work through the protocol contract
        # Implementation details are abstracted away from the interface

        error_handler: "ProtocolErrorHandler" = ErrorHandlerImpl()

        try:
            result = risky_operation()
        except Exception as e:
            error_context = create_error_context(operation_name="risky_operation")
            return error_handler.handle_error(e, error_context)
        ```
    """

    async def handle_error(
        self, error: Exception, context: "ProtocolErrorContext"
    ) -> "ProtocolErrorResult": ...

    async def get_error_recovery_strategy(
        self, error_result: "ProtocolErrorResult"
    ) -> "ProtocolRecoveryAction": ...

    def classify_error_severity(
        self, error: Exception, context: "ProtocolErrorContext"
    ) -> "LiteralErrorSeverity": ...

    def should_retry_error(
        self, error_result: "ProtocolErrorResult", attempt_count: int
    ) -> bool: ...

    async def get_backoff_delay_seconds(
        self, error_result: "ProtocolErrorResult", attempt_count: int
    ) -> float: ...

    def record_error_metrics(
        self, error_result: "ProtocolErrorResult", recovery_outcome: str
    ) -> None: ...

    def activate_circuit_breaker(
        self, service_name: str, error_threshold: int
    ) -> bool: ...

    async def get_circuit_breaker_status(self, service_name: str) -> str: ...

    async def reset_circuit_breaker(self, service_name: str) -> bool: ...

    async def get_error_statistics(
        self, time_window_minutes: int
    ) -> dict[str, object]: ...
