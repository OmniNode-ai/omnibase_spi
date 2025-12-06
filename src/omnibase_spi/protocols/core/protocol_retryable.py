"""
Protocol for Standardized Retry Functionality.

Defines interfaces for retry logic, backoff strategies, and retry policy
management across all ONEX services with consistent patterns.
"""

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

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
        self, operation: Callable[..., Any], config: "ProtocolRetryConfig"
    ) -> "ProtocolRetryResult": ...

    def configure_retry_policy(self, policy: "ProtocolRetryPolicy") -> bool: ...

    async def get_retry_policy(self) -> "ProtocolRetryPolicy": ...

    def should_retry(
        self, error: Exception, attempt_number: int, config: "ProtocolRetryConfig"
    ) -> bool: ...

    def calculate_backoff_delay(
        self,
        attempt_number: int,
        strategy: "LiteralRetryBackoffStrategy",
        base_delay_ms: int,
        max_delay_ms: int,
    ) -> int: ...

    def record_retry_attempt(self, attempt: "ProtocolRetryAttempt") -> None: ...

    async def get_retry_metrics(self) -> dict[str, "ContextValue"]: ...

    async def reset_retry_budget(self) -> None: ...

    async def get_retry_budget_status(self) -> dict[str, int]: ...

    def add_retry_condition(
        self, condition: "LiteralRetryCondition", error_types: list[type[BaseException]]
    ) -> bool: ...

    def remove_retry_condition(self, condition: "LiteralRetryCondition") -> bool: ...

    async def get_retry_conditions(self) -> list["LiteralRetryCondition"]: ...
