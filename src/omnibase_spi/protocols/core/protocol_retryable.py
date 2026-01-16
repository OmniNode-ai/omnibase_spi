"""
Protocol for Standardized Retry Functionality.

Defines interfaces for retry logic, backoff strategies, and retry policy
management across all ONEX services with consistent patterns.
"""

from collections.abc import Callable
from typing import TYPE_CHECKING, Protocol, runtime_checkable

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
        - Backoff strategies: linear, exponential, fibonacci, fixed, jitter
        - Circuit breaker integration for fail-fast scenarios
        - Retry budget management to prevent resource exhaustion

    Usage Example:
        ```python
        # Protocol usage example (SPI-compliant)
        service: "Retryable" = get_retryable()

        # Usage demonstrates protocol interface without implementation details
        # All operations work through the protocol contract
        # Implementation details are abstracted away from the interface

        retryable: "ProtocolRetryable" = RetryableServiceImpl()

        retry_config = "ProtocolRetryConfig"(
            max_attempts=5,
            backoff_strategy="fibonacci",
            base_delay_ms=1000,
            max_delay_ms=30000
        )

        result = retryable.execute_with_retry(
            operation=lambda: external_api_call(),
            config=retry_config
        )
        ```
    """

    async def execute_with_retry(
        self, operation: Callable[..., object], config: "ProtocolRetryConfig"
    ) -> "ProtocolRetryResult":
        """Execute an operation with retry logic based on the provided configuration.

        Executes the given operation and automatically retries on failure according
        to the retry configuration. Applies backoff delays between attempts and
        tracks retry metrics.

        Args:
            operation: The callable operation to execute with retry logic.
            config: Retry configuration specifying max attempts, backoff strategy,
                and delay parameters.

        Returns:
            Result containing the operation outcome, retry attempts made,
            and success/failure status.

        Raises:
            RetryExhaustedError: When all retry attempts have been exhausted.
            RetryBudgetExceededError: When the retry budget has been exceeded.
        """
        ...

    def configure_retry_policy(self, policy: "ProtocolRetryPolicy") -> bool:
        """Configure the retry policy for this retryable instance.

        Sets the retry policy that will be used as the default for retry operations.
        The policy defines conditions, backoff strategies, and budget constraints.

        Args:
            policy: The retry policy to configure.

        Returns:
            True if the policy was successfully configured, False otherwise.

        Raises:
            InvalidPolicyError: When the policy configuration is invalid.
        """
        ...

    async def get_retry_policy(self) -> "ProtocolRetryPolicy":
        """Retrieve the current retry policy configuration.

        Returns:
            The currently configured retry policy.

        Raises:
            PolicyNotConfiguredError: When no retry policy has been configured.
        """
        ...

    def should_retry(
        self, error: Exception, attempt_number: int, config: "ProtocolRetryConfig"
    ) -> bool:
        """Determine whether a retry should be attempted for the given error.

        Evaluates the error type, attempt number, and configuration to decide
        if another retry attempt should be made.

        Args:
            error: The exception that caused the operation to fail.
            attempt_number: The current attempt number (1-indexed).
            config: The retry configuration with max attempts and conditions.

        Returns:
            True if a retry should be attempted, False otherwise.
        """
        ...

    def calculate_backoff_delay(
        self,
        attempt_number: int,
        strategy: "LiteralRetryBackoffStrategy",
        base_delay_ms: int,
        max_delay_ms: int,
    ) -> int:
        """Calculate the backoff delay for the next retry attempt.

        Computes the delay in milliseconds based on the backoff strategy,
        attempt number, and delay bounds.

        Args:
            attempt_number: The current attempt number (1-indexed).
            strategy: The backoff strategy (linear, exponential, fibonacci,
                fixed, or jitter).
            base_delay_ms: The base delay in milliseconds.
            max_delay_ms: The maximum delay cap in milliseconds.

        Returns:
            The calculated delay in milliseconds for the next retry.

        Raises:
            ValueError: When attempt_number is less than 1 or delay parameters
                are negative.
        """
        ...

    def record_retry_attempt(self, attempt: "ProtocolRetryAttempt") -> None:
        """Record a retry attempt for metrics and tracking purposes.

        Stores information about the retry attempt including timing,
        success/failure status, and error details if applicable.

        Args:
            attempt: The retry attempt details to record.

        Raises:
            SPIError: When the attempt data cannot be recorded due to
                storage or validation errors.
        """
        ...

    async def get_retry_metrics(self) -> dict[str, "ContextValue"]:
        """Retrieve retry metrics and statistics.

        Returns aggregated metrics about retry operations including
        success rates, average attempts, and failure distributions.

        Returns:
            Dictionary containing retry metrics with string keys and
            context-appropriate values.

        Raises:
            SPIError: When metrics cannot be retrieved due to storage
                or connection errors.
        """
        ...

    async def reset_retry_budget(self) -> None:
        """Reset the retry budget to its initial state.

        Clears all consumed budget and resets counters, allowing
        fresh retry attempts after budget exhaustion.

        Raises:
            SPIError: When the budget cannot be reset due to storage
                or state management errors.
        """
        ...

    async def get_retry_budget_status(self) -> dict[str, int]:
        """Get the current retry budget status.

        Returns:
            Dictionary with budget information including remaining attempts,
            consumed budget, and total budget capacity.

        Raises:
            SPIError: When the budget status cannot be retrieved due to
                storage or state management errors.
        """
        ...

    def add_retry_condition(
        self, condition: "LiteralRetryCondition", error_types: list[type[BaseException]]
    ) -> bool:
        """Add a retry condition for specific error types.

        Configures the retryable to apply the given condition when
        encountering the specified error types.

        Args:
            condition: The retry condition to apply (e.g., always, never,
                on_timeout, on_connection_error).
            error_types: List of exception types that trigger this condition.

        Returns:
            True if the condition was successfully added, False otherwise.
        """
        ...

    def remove_retry_condition(self, condition: "LiteralRetryCondition") -> bool:
        """Remove a previously configured retry condition.

        Args:
            condition: The retry condition to remove.

        Returns:
            True if the condition was found and removed, False if not found.
        """
        ...

    async def get_retry_conditions(self) -> list["LiteralRetryCondition"]:
        """Retrieve all configured retry conditions.

        Returns:
            List of currently configured retry conditions.

        Raises:
            SPIError: When the conditions cannot be retrieved due to
                storage or state management errors.
        """
        ...
