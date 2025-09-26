"""
Protocol for Standardized Retry Functionality.

Defines interfaces for retry logic, backoff strategies, and retry policy
management across all ONEX services with consistent patterns.
"""

from typing import TYPE_CHECKING, Any, Callable, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_core_types import (
        ContextValue,
        LiteralRetryBackoffStrategy,
        LiteralRetryCondition,
        ProtocolRetryAttempt,
        ProtocolRetryConfig,
        ProtocolRetryPolicy,
        ProtocolRetryResult,
    )


@runtime_checkable
class ProtocolRetryable(Protocol):
    """
    Protocol for standardized retry functionality across ONEX services.

    Provides consistent retry patterns, backoff strategies, and policy
    management for resilient distributed system operations.

    Key Features:
        - Configurable retry policies with multiple backoff strategies
        - Conditional retry logic based on error types and contexts
        - Retry attempt tracking with success/failure metrics
        - Backoff strategies: linear, exponential, fixed, jitter
        - Circuit breaker integration for fail-fast scenarios
        - Retry budget management to prevent resource exhaustion

    Usage Example:
        ```python
        # Implementation example (not part of SPI)
        class RetryableServiceImpl:
            def execute_with_retry(self, operation, config):
                for attempt in range(config.max_attempts):
                    try:
                        result = operation()
                        self._record_success(attempt)
                        return ProtocolRetryResult(success=True, result=result)
                    except Exception as e:
                        if not self._should_retry(e, attempt, config):
                            break
                        self._apply_backoff(attempt, config.backoff_strategy)

                return ProtocolRetryResult(success=False, final_error=e)

        # Usage in application code
        retryable: ProtocolRetryable = RetryableServiceImpl()

        retry_config = ProtocolRetryConfig(
            max_attempts=3,
            backoff_strategy="exponential",
            base_delay_ms=1000,
            max_delay_ms=10000
        )

        result = retryable.execute_with_retry(
            operation=lambda: external_api_call(),
            config=retry_config
        )
        ```
    """

    def execute_with_retry(
        self,
        operation: Callable[..., Any],
        config: "ProtocolRetryConfig",
    ) -> "ProtocolRetryResult":
        """
        Execute operation with retry logic according to configuration.

        Args:
            operation: Function or callable to execute with retry logic
            config: Retry configuration with policies and limits

        Returns:
            Result containing success status, final result, or error details

        Note:
            Applies configured backoff strategy and retry conditions.
            Records retry metrics for monitoring and analysis.
        """
        ...

    def configure_retry_policy(
        self,
        policy: "ProtocolRetryPolicy",
    ) -> bool:
        """
        Configure retry policy for this retryable instance.

        Args:
            policy: Retry policy configuration with conditions and limits

        Returns:
            True if policy was configured successfully

        Note:
            Sets default retry behavior for all operations unless
            overridden by specific operation configurations.
        """
        ...

    def get_retry_policy(self) -> "ProtocolRetryPolicy":
        """
        Get current retry policy configuration.

        Returns:
            Current retry policy settings

        Note:
            Returns active policy including backoff strategy,
            retry conditions, and resource limits.
        """
        ...

    def should_retry(
        self,
        error: Exception,
        attempt_number: int,
        config: "ProtocolRetryConfig",
    ) -> bool:
        """
        Determine if operation should be retried based on error and config.

        Args:
            error: Exception that occurred during operation
            attempt_number: Current attempt number (0-indexed)
            config: Retry configuration with conditions

        Returns:
            True if operation should be retried

        Note:
            Evaluates retry conditions including error types,
            attempt limits, and circuit breaker states.
        """
        ...

    def calculate_backoff_delay(
        self,
        attempt_number: int,
        strategy: "LiteralRetryBackoffStrategy",
        base_delay_ms: int,
        max_delay_ms: int,
    ) -> int:
        """
        Calculate delay before next retry attempt.

        Args:
            attempt_number: Current attempt number (0-indexed)
            strategy: Backoff strategy (linear, exponential, fixed, jitter)
            base_delay_ms: Base delay in milliseconds
            max_delay_ms: Maximum allowed delay in milliseconds

        Returns:
            Delay in milliseconds before next attempt

        Note:
            Applies specified backoff strategy with jitter for
            distributed system coordination and load balancing.
        """
        ...

    def record_retry_attempt(
        self,
        attempt: "ProtocolRetryAttempt",
    ) -> None:
        """
        Record retry attempt for metrics and monitoring.

        Args:
            attempt: Retry attempt details with timing and outcome

        Note:
            Tracks retry patterns for operational visibility
            and system health monitoring.
        """
        ...

    def get_retry_metrics(self) -> dict[str, "ContextValue"]:
        """
        Get retry metrics for monitoring and analysis.

        Returns:
            Dictionary with retry statistics and performance metrics

        Note:
            Provides insights into retry patterns, success rates,
            and system reliability for operational dashboards.
        """
        ...

    def reset_retry_budget(self) -> None:
        """
        Reset retry budget for resource management.

        Note:
            Resets retry attempt counters and budgets for
            fresh retry cycles or recovery scenarios.
        """
        ...

    def get_retry_budget_status(self) -> dict[str, int]:
        """
        Get current retry budget status.

        Returns:
            Dictionary with current retry budget and usage

        Note:
            Provides visibility into retry resource consumption
            and helps prevent retry storms in distributed systems.
        """
        ...

    def add_retry_condition(
        self,
        condition: "LiteralRetryCondition",
        error_types: list[type[BaseException]],
    ) -> bool:
        """
        Add retry condition for specific error types.

        Args:
            condition: When to apply this condition (always, never, on_error, etc.)
            error_types: List of exception types that trigger this condition

        Returns:
            True if condition was added successfully

        Note:
            Allows fine-grained control over retry behavior
            based on specific error patterns and contexts.
        """
        ...

    def remove_retry_condition(
        self,
        condition: "LiteralRetryCondition",
    ) -> bool:
        """
        Remove retry condition from policy.

        Args:
            condition: Condition to remove from retry policy

        Returns:
            True if condition was removed successfully

        Note:
            Removes specific retry conditions while preserving
            other configured retry behaviors.
        """
        ...

    def get_retry_conditions(self) -> list["LiteralRetryCondition"]:
        """
        Get all configured retry conditions.

        Returns:
            List of all retry conditions currently configured

        Note:
            Provides visibility into retry logic for
            troubleshooting and policy validation.
        """
        ...
