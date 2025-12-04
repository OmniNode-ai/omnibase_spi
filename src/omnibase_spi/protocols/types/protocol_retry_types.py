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
    """Protocol for retry configuration."""

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
    """Protocol for retry policy configuration."""

    default_config: "ProtocolRetryConfig"
    error_specific_configs: dict[str, "ProtocolRetryConfig"]
    retry_conditions: list[LiteralRetryCondition]
    retry_budget_limit: int
    budget_window_seconds: int

    async def validate_retry_policy(self) -> bool: ...

    def is_applicable(self) -> bool: ...


@runtime_checkable
class ProtocolRetryAttempt(Protocol):
    """Protocol for retry attempt records."""

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
    """Protocol for retry operation results."""

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
    """Protocol for time-based operations and measurements."""

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
    """Protocol for timeout configuration and tracking."""

    timeout_ms: int
    start_time: ProtocolDateTime
    warning_threshold_ms: int | None
    is_expired: bool
    time_remaining_ms: int

    async def validate_timeout(self) -> bool: ...

    def is_reasonable(self) -> bool: ...


@runtime_checkable
class ProtocolDuration(Protocol):
    """Protocol for duration measurement and tracking."""

    start_time: ProtocolDateTime
    end_time: ProtocolDateTime | None
    duration_ms: int
    is_completed: bool
    can_measure: bool

    async def validate_duration(self) -> bool: ...

    def is_measurable(self) -> bool: ...
