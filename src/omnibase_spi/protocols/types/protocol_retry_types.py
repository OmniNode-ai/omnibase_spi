"""
Retry and timeout protocol types for ONEX SPI interfaces.

Domain: Retry configuration, policies, attempts, results, and time-based operations.

This module contains protocol definitions for:
- ProtocolRetryConfig: Retry configuration with backoff strategies
- ProtocolRetryPolicy: Policy-based retry configuration
- ProtocolRetryAttempt: Individual retry attempt records
- ProtocolRetryResult: Aggregated retry operation results
- ProtocolTimeBased: Time-based operation measurements
- ProtocolTimeout: Timeout configuration and tracking
- ProtocolDuration: Duration measurement and tracking
"""

from typing import Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_base_types import (
    ContextValue,
    LiteralRetryBackoffStrategy,
    LiteralRetryCondition,
    LiteralTimeBasedType,
    ProtocolDateTime,
)

# ==============================================================================
# Retry Configuration Protocols
# ==============================================================================


@runtime_checkable
class ProtocolRetryConfig(Protocol):
    """
    Protocol for retry configuration with backoff strategies.

    Defines comprehensive retry behavior including maximum attempts,
    backoff strategy, delay parameters, and jitter configuration.
    Used for resilient operation execution across ONEX services.

    Attributes:
        max_attempts: Maximum number of retry attempts.
        backoff_strategy: Strategy for delay calculation (linear, exponential).
        base_delay_ms: Initial delay between retries in milliseconds.
        max_delay_ms: Maximum delay cap in milliseconds.
        timeout_ms: Overall timeout for retry operation.
        jitter_factor: Random jitter factor (0.0 to 1.0) to prevent thundering herd.

    Example:
        ```python
        class ExponentialRetryConfig:
            max_attempts: int = 5
            backoff_strategy: LiteralRetryBackoffStrategy = "exponential"
            base_delay_ms: int = 100
            max_delay_ms: int = 30000
            timeout_ms: int = 60000
            jitter_factor: float = 0.1

            async def validate_retry_config(self) -> bool:
                return self.max_attempts > 0

            def is_reasonable(self) -> bool:
                return self.base_delay_ms < self.max_delay_ms

        config = ExponentialRetryConfig()
        assert isinstance(config, ProtocolRetryConfig)
        ```
    """

    max_attempts: int
    backoff_strategy: LiteralRetryBackoffStrategy
    base_delay_ms: int
    max_delay_ms: int
    timeout_ms: int
    jitter_factor: float

    async def validate_retry_config(self) -> bool: ...

    def is_reasonable(self) -> bool: ...


@runtime_checkable
class ProtocolRetryPolicy(Protocol):
    """
    Protocol for comprehensive retry policy with error-specific configurations.

    Defines a complete retry policy including default configuration,
    error-specific overrides, and budget management. Used for advanced
    retry scenarios with conditional retry logic.

    Attributes:
        default_config: Default retry configuration for all errors.
        error_specific_configs: Overrides keyed by error type.
        retry_conditions: Conditions that trigger retries.
        retry_budget_limit: Maximum retries within budget window.
        budget_window_seconds: Time window for budget calculation.

    Example:
        ```python
        class ServiceRetryPolicy:
            default_config: ProtocolRetryConfig = default_config_impl
            error_specific_configs: dict[str, ProtocolRetryConfig] = {
                "TimeoutError": timeout_config_impl,
                "ConnectionError": connection_config_impl
            }
            retry_conditions: list[LiteralRetryCondition] = [
                "transient", "timeout", "rate_limited"
            ]
            retry_budget_limit: int = 100
            budget_window_seconds: int = 60

            async def validate_retry_policy(self) -> bool:
                return self.retry_budget_limit > 0

            def is_applicable(self) -> bool:
                return len(self.retry_conditions) > 0

        policy = ServiceRetryPolicy()
        assert isinstance(policy, ProtocolRetryPolicy)
        ```
    """

    default_config: "ProtocolRetryConfig"
    error_specific_configs: dict[str, "ProtocolRetryConfig"]
    retry_conditions: list[LiteralRetryCondition]
    retry_budget_limit: int
    budget_window_seconds: int

    async def validate_retry_policy(self) -> bool: ...

    def is_applicable(self) -> bool: ...


@runtime_checkable
class ProtocolRetryAttempt(Protocol):
    """
    Protocol for individual retry attempt records and metrics.

    Captures details of a single retry attempt including timing,
    outcome, and applied backoff. Used for retry observability
    and debugging.

    Attributes:
        attempt_number: Sequential number of this attempt (1-indexed).
        timestamp: When the attempt started.
        duration_ms: How long the attempt took in milliseconds.
        error_type: Error type if failed, None on success.
        success: Whether this attempt succeeded.
        backoff_applied_ms: Backoff delay before this attempt.

    Example:
        ```python
        class FailedAttempt:
            attempt_number: int = 2
            timestamp: ProtocolDateTime = datetime_impl
            duration_ms: int = 5000
            error_type: str | None = "TimeoutError"
            success: bool = False
            backoff_applied_ms: int = 200

            async def validate_retry_attempt(self) -> bool:
                return self.attempt_number > 0

            def is_valid_attempt(self) -> bool:
                return self.duration_ms >= 0

        attempt = FailedAttempt()
        assert isinstance(attempt, ProtocolRetryAttempt)
        ```
    """

    attempt_number: int
    timestamp: ProtocolDateTime
    duration_ms: int
    error_type: str | None
    success: bool
    backoff_applied_ms: int

    async def validate_retry_attempt(self) -> bool: ...

    def is_valid_attempt(self) -> bool: ...


@runtime_checkable
class ProtocolRetryResult(Protocol):
    """
    Protocol for aggregated retry operation results.

    Contains the complete outcome of a retry operation including
    final status, attempt history, and the result or final error.
    Used for retry result handling and analytics.

    Attributes:
        success: Whether the operation eventually succeeded.
        final_attempt_number: Number of the last attempt made.
        total_duration_ms: Total time across all attempts.
        result: Operation result if successful, None otherwise.
        final_error: Last error if failed, None on success.
        attempts: Complete history of all attempts.

    Example:
        ```python
        class SuccessfulRetryResult:
            success: bool = True
            final_attempt_number: int = 3
            total_duration_ms: int = 15500
            result: ContextValue | None = {"data": "response"}
            final_error: Exception | None = None
            attempts: list[ProtocolRetryAttempt] = [
                attempt1, attempt2, attempt3
            ]

            async def validate_retry_result(self) -> bool:
                return self.final_attempt_number == len(self.attempts)

            def is_final(self) -> bool:
                return self.success or self.final_error is not None

        result = SuccessfulRetryResult()
        assert isinstance(result, ProtocolRetryResult)
        ```
    """

    success: bool
    final_attempt_number: int
    total_duration_ms: int
    result: ContextValue | None
    final_error: Exception | None
    attempts: list["ProtocolRetryAttempt"]

    async def validate_retry_result(self) -> bool: ...

    def is_final(self) -> bool: ...


# ==============================================================================
# Time-Based Operation Protocols
# ==============================================================================


@runtime_checkable
class ProtocolTimeBased(Protocol):
    """
    Protocol for time-based operations and duration measurements.

    Provides timing information for operations including start/end
    times, duration, and expiration status. Used for operation
    timing and time-boxed execution patterns.

    Attributes:
        type: Type of time-based operation (timer, timeout, schedule).
        start_time: When the operation started, None if not started.
        end_time: When the operation ended, None if still active.
        duration_ms: Elapsed duration in milliseconds, None if unknown.
        is_active: Whether the operation is currently running.
        has_expired: Whether the time limit has been exceeded.

    Example:
        ```python
        class ActiveTimer:
            type: LiteralTimeBasedType = "timer"
            start_time: ProtocolDateTime | None = datetime_impl
            end_time: ProtocolDateTime | None = None
            duration_ms: int | None = 5000
            is_active: bool = True
            has_expired: bool = False

            async def validate_time_based(self) -> bool:
                return self.start_time is not None if self.is_active else True

            def is_valid_timing(self) -> bool:
                return self.duration_ms is None or self.duration_ms >= 0

        timer = ActiveTimer()
        assert isinstance(timer, ProtocolTimeBased)
        ```
    """

    type: LiteralTimeBasedType
    start_time: ProtocolDateTime | None
    end_time: ProtocolDateTime | None
    duration_ms: int | None
    is_active: bool
    has_expired: bool

    async def validate_time_based(self) -> bool: ...

    def is_valid_timing(self) -> bool: ...


@runtime_checkable
class ProtocolTimeout(Protocol):
    """
    Protocol for timeout configuration and real-time tracking.

    Tracks timeout state including remaining time, expiration status,
    and optional warning thresholds. Used for operation timeouts
    and deadline enforcement.

    Attributes:
        timeout_ms: Total timeout duration in milliseconds.
        start_time: When the timeout period started.
        warning_threshold_ms: Time before expiry to issue warning, None to skip.
        is_expired: Whether the timeout has been exceeded.
        time_remaining_ms: Milliseconds until timeout.

    Example:
        ```python
        class OperationTimeout:
            timeout_ms: int = 30000
            start_time: ProtocolDateTime = datetime_impl
            warning_threshold_ms: int | None = 5000
            is_expired: bool = False
            time_remaining_ms: int = 25000

            async def validate_timeout(self) -> bool:
                return self.timeout_ms > 0

            def is_reasonable(self) -> bool:
                return (
                    self.warning_threshold_ms is None
                    or self.warning_threshold_ms < self.timeout_ms
                )

        timeout = OperationTimeout()
        assert isinstance(timeout, ProtocolTimeout)
        ```
    """

    timeout_ms: int
    start_time: ProtocolDateTime
    warning_threshold_ms: int | None
    is_expired: bool
    time_remaining_ms: int

    async def validate_timeout(self) -> bool: ...

    def is_reasonable(self) -> bool: ...


@runtime_checkable
class ProtocolDuration(Protocol):
    """
    Protocol for duration measurement and lifecycle tracking.

    Captures elapsed time for operations with start/end timestamps
    and computed duration. Used for performance measurement and
    operation lifecycle tracking.

    Attributes:
        start_time: When the measurement began.
        end_time: When the measurement ended, None if ongoing.
        duration_ms: Computed duration in milliseconds.
        is_completed: Whether the operation has finished.
        can_measure: Whether duration can be computed.

    Example:
        ```python
        class CompletedDuration:
            start_time: ProtocolDateTime = start_datetime_impl
            end_time: ProtocolDateTime | None = end_datetime_impl
            duration_ms: int = 1250
            is_completed: bool = True
            can_measure: bool = True

            async def validate_duration(self) -> bool:
                return self.duration_ms >= 0

            def is_measurable(self) -> bool:
                return self.can_measure and self.is_completed

        duration = CompletedDuration()
        assert isinstance(duration, ProtocolDuration)
        ```
    """

    start_time: ProtocolDateTime
    end_time: ProtocolDateTime | None
    duration_ms: int
    is_completed: bool
    can_measure: bool

    async def validate_duration(self) -> bool: ...

    def is_measurable(self) -> bool: ...
