"""
Enhanced error handling protocol definitions for OmniMemory operations.

Defines error categorization, retry policies, compensation/rollback patterns,
and comprehensive error recovery for memory operations.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Protocol, runtime_checkable
from uuid import UUID

if TYPE_CHECKING:
    from datetime import datetime

    from omnibase_spi.protocols.memory.protocol_memory_base import (
        ProtocolMemoryMetadata,
    )


@runtime_checkable
class ProtocolErrorCategory(Protocol):
    """
    Error category classification for memory operations.

    Categorizes errors as transient, permanent, security, validation,
    or infrastructure to enable appropriate error handling strategies.
    """

    @property
    def error_type(self) -> str: ...

    @property
    def error_severity(self) -> str: ...

    @property
    def is_retryable(self) -> bool: ...

    @property
    def default_retry_count(self) -> int: ...

    async def classify_error(self, error: Exception) -> str: ...

    async def get_recovery_strategy(self) -> str: ...


@runtime_checkable
class ProtocolMemoryRetryPolicy(Protocol):
    """
    Retry policy configuration for memory operations.

    Defines retry behavior including attempt limits, backoff strategies,
    and condition-based retry logic for memory operations.
    """

    @property
    def max_attempts(self) -> int: ...

    @property
    def base_delay_ms(self) -> int: ...

    @property
    def max_delay_ms(self) -> int: ...

    @property
    def backoff_multiplier(self) -> float: ...

    @property
    def jitter_enabled(self) -> bool: ...

    async def should_retry(self, error: Exception, attempt: int) -> bool: ...

    async def calculate_delay(self, attempt: int) -> int: ...

    async def reset_policy(self) -> None: ...


@runtime_checkable
class ProtocolMemoryCompensationAction(Protocol):
    """
    Compensation action for failed memory operations.

    Defines compensating actions to undo or mitigate the effects
    of failed operations in distributed memory systems.
    """

    @property
    def action_id(self) -> UUID: ...

    @property
    def operation_id(self) -> UUID: ...

    @property
    def compensation_type(self) -> str: ...

    @property
    def is_idempotent(self) -> bool: ...

    async def execute_compensation(self) -> bool: ...

    async def validate_compensation(self) -> bool: ...

    async def get_compensation_metadata(self) -> ProtocolMemoryMetadata: ...


@runtime_checkable
class ProtocolOperationContext(Protocol):
    """
    Context information for memory operations.

    Provides operation metadata, timing information, and environment
    details necessary for error handling and recovery decisions.
    """

    @property
    def operation_id(self) -> UUID: ...

    @property
    def operation_type(self) -> str: ...

    @property
    def start_time(self) -> datetime: ...

    @property
    def timeout_ms(self) -> int: ...

    @property
    def correlation_id(self) -> UUID | None: ...

    @property
    def user_context(self) -> dict[str, str] | None: ...

    @property
    def retry_count(self) -> int: ...

    def has_timed_out(self) -> bool: ...

    async def get_elapsed_time_ms(self) -> int: ...

    def increment_retry_count(self) -> None: ...

    def add_context_data(self, key: str, value: str) -> None: ...


@runtime_checkable
class ProtocolMemoryErrorHandler(Protocol):
    """
    Comprehensive error handler for memory operations.

    Orchestrates error classification, retry logic, compensation actions,
    and recovery strategies for memory operation failures.
    """

    @property
    def error_categories(self) -> list[ProtocolErrorCategory]: ...

    @property
    def retry_policies(self) -> dict[str, ProtocolMemoryRetryPolicy]: ...

    @property
    def compensation_actions(self) -> list[ProtocolMemoryCompensationAction]: ...

    async def handle_error(
        self, error: Exception, context: ProtocolOperationContext
    ) -> bool: ...

    async def classify_error(self, error: Exception) -> ProtocolErrorCategory: ...

    async def should_retry_operation(
        self, error: Exception, context: ProtocolOperationContext
    ) -> bool: ...

    async def execute_retry(
        self,
        operation_func: Callable[..., object],
        context: ProtocolOperationContext,
        retry_policy: ProtocolMemoryRetryPolicy,
    ) -> object: ...

    async def execute_compensation(self, context: ProtocolOperationContext) -> bool: ...

    async def log_error(
        self,
        error: Exception,
        context: ProtocolOperationContext,
        recovery_action: str,
    ) -> None: ...

    async def get_error_statistics(self) -> dict[str, int]: ...

    async def reset_error_statistics(self) -> None: ...


@runtime_checkable
class ProtocolMemoryHealthMonitor(Protocol):
    """
    Health monitoring for memory system components.

    Tracks system health, performance metrics, and provides
    early warning capabilities for memory operation issues.
    """

    @property
    def health_status(self) -> str: ...

    @property
    def error_rate_threshold(self) -> float: ...

    @property
    def response_time_threshold_ms(self) -> int: ...

    @property
    def monitoring_window_minutes(self) -> int: ...

    async def record_operation(
        self, operation_type: str, duration_ms: int, success: bool
    ) -> None: ...

    async def record_error(self, error_category: str, error_severity: str) -> None: ...

    async def get_current_error_rate(self) -> float: ...

    async def get_average_response_time_ms(self) -> float: ...

    async def get_health_metrics(self) -> dict[str, float]: ...

    async def check_health_thresholds(self) -> bool: ...

    async def get_health_recommendations(self) -> list[str]: ...

    async def reset_health_metrics(self) -> None: ...
