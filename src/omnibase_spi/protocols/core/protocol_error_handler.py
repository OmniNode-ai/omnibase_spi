"""
Protocol for Standardized Error Handling.

Defines interfaces for error handling, recovery strategies, and observability
across all ONEX services following consistent patterns.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.core_types import (
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
        # Implementation example (not part of SPI)
        class ErrorHandlerImpl:
            def handle_error(self, error, context):
                error_result = self._classify_error(error)
                recovery_action = self.get_error_recovery_strategy(error_result)
                if recovery_action.action_type == "retry":
                    return self._retry_with_backoff(error_result, recovery_action)
                elif recovery_action.action_type == "circuit_breaker":
                    return self._activate_circuit_breaker(error_result)
                else:
                    return self._handle_terminal_error(error_result)

        # Usage in application code
        error_handler: ProtocolErrorHandler = ErrorHandlerImpl()

        try:
            result = risky_operation()
        except Exception as e:
            error_context = create_error_context(operation_name="risky_operation")
            return error_handler.handle_error(e, error_context)
        ```
    """

    def handle_error(
        self,
        error: Exception,
        context: "ProtocolErrorContext",
    ) -> "ProtocolErrorResult":
        """
        Handle error with appropriate recovery strategy.

        Args:
            error: Exception that occurred
            context: Error context with correlation and operation info

        Returns:
            Standardized error result with recovery actions

        Note:
            This is the main entry point for error handling. It classifies
            the error, determines recovery strategy, and executes appropriate
            handling logic with full observability.
        """
        ...

    def get_error_recovery_strategy(
        self,
        error_result: "ProtocolErrorResult",
    ) -> "ProtocolRecoveryAction":
        """
        Determine appropriate recovery strategy for error.

        Args:
            error_result: Classified error information

        Returns:
            Recovery action with strategy and parameters

        Note:
            Recovery strategies include retry with exponential backoff,
            circuit breaker activation, fallback value selection,
            and compensation action triggering.
        """
        ...

    def classify_error_severity(
        self,
        error: Exception,
        context: "ProtocolErrorContext",
    ) -> "LiteralErrorSeverity":
        """
        Classify error severity for appropriate handling.

        Args:
            error: Exception to classify
            context: Context information for classification

        Returns:
            Error severity level (low, medium, high, critical)

        Note:
            Severity classification drives recovery strategy selection,
            alerting rules, and escalation procedures.
        """
        ...

    def should_retry_error(
        self,
        error_result: "ProtocolErrorResult",
        attempt_count: int,
    ) -> bool:
        """
        Determine if error should be retried.

        Args:
            error_result: Classified error information
            attempt_count: Current attempt number (1-based)

        Returns:
            True if error should be retried

        Note:
            Considers error type, severity, circuit breaker state,
            and exponential backoff limits for retry decisions.
        """
        ...

    def get_backoff_delay_seconds(
        self,
        error_result: "ProtocolErrorResult",
        attempt_count: int,
    ) -> float:
        """
        Calculate backoff delay for retry attempts.

        Args:
            error_result: Classified error information
            attempt_count: Current attempt number (1-based)

        Returns:
            Delay in seconds before next retry

        Note:
            Implements exponential backoff with jitter to prevent
            thundering herd problems in distributed systems.
        """
        ...

    def record_error_metrics(
        self,
        error_result: "ProtocolErrorResult",
        recovery_outcome: str,
    ) -> None:
        """
        Record error metrics for observability.

        Args:
            error_result: Error that occurred
            recovery_outcome: Result of recovery attempt

        Note:
            Records metrics for error rates, recovery success rates,
            circuit breaker state changes, and performance impact.
        """
        ...

    def activate_circuit_breaker(
        self,
        service_name: str,
        error_threshold: int,
    ) -> bool:
        """
        Activate circuit breaker for failing service.

        Args:
            service_name: Name of service to circuit break
            error_threshold: Error count threshold for activation

        Returns:
            True if circuit breaker was activated

        Note:
            Circuit breaker prevents cascading failures by failing
            fast when error threshold is exceeded.
        """
        ...

    def get_circuit_breaker_status(
        self,
        service_name: str,
    ) -> str:
        """
        Get current circuit breaker status.

        Args:
            service_name: Service to check status for

        Returns:
            Circuit breaker status (closed, open, half_open)

        Note:
            Status determines whether requests should be allowed,
            blocked, or probed for service recovery.
        """
        ...

    def reset_circuit_breaker(
        self,
        service_name: str,
    ) -> bool:
        """
        Reset circuit breaker to closed state.

        Args:
            service_name: Service to reset circuit breaker for

        Returns:
            True if circuit breaker was successfully reset

        Note:
            Used when service has recovered and is ready to
            accept traffic again after failure period.
        """
        ...

    def get_error_statistics(
        self,
        time_window_minutes: int,
    ) -> dict[str, object]:
        """
        Get error statistics for monitoring.

        Args:
            time_window_minutes: Time window for statistics

        Returns:
            Error statistics including rates, types, and recovery metrics

        Note:
            Provides comprehensive error observability for monitoring
            dashboards, alerting, and operational insights.
        """
        ...
