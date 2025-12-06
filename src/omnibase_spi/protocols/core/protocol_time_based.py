"""
Protocol for Time-Based Operations and Measurements.

Defines interfaces for duration tracking, timeout management, and time-based
scheduling across all ONEX services with consistent patterns.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_core_types import (
        LiteralTimeBasedType,
        ProtocolDateTime,
        ProtocolDuration,
        ProtocolTimeBased,
        ProtocolTimeout,
    )


@runtime_checkable
class ProtocolTimeBasedOperations(Protocol):
    """
            Protocol for time-based operations and measurements across ONEX services.

            Provides consistent time tracking patterns, timeout management, and
            duration measurement for distributed system operations and monitoring.

        Key Features:
        - Duration measurement for operation timing
        - Timeout management with early warning thresholds
        - Time-based scheduling and interval management
        - Deadline tracking for time-sensitive operations
        - Active time window management
        - Expiration detection and handling

    Usage Example:
        ```python
        # Protocol usage example (SPI-compliant)
    service: "TimeBased" = get_time_based()

    # Usage demonstrates protocol interface without implementation details
    # All operations work through the protocol contract
    # Implementation details are abstracted away from the interface

    time_ops: "ProtocolTimeBasedOperations" = TimeBasedOperationImpl()

    # Start tracking an operation
        duration = time_ops.start_duration_tracking("data_processing")
        timeout = time_ops.set_timeout("data_processing", 30000)  # 30 seconds

    # Check status during operation
    if time_ops.is_timeout_warning("data_processing"):
        logger.warning("Operation approaching timeout")

    # Complete operation
        time_ops.complete_duration_tracking("data_processing")
        ```
    """

    async def start_duration_tracking(
        self, operation_id: str
    ) -> "ProtocolDuration": ...

    def complete_duration_tracking(self, operation_id: str) -> "ProtocolDuration": ...

    async def get_operation_duration(self, operation_id: str) -> "ProtocolDuration": ...

    async def set_timeout(
        self,
        operation_id: str,
        timeout_ms: int,
        warning_threshold_ms: int | None = None,
    ) -> "ProtocolTimeout": ...

    def is_timeout_expired(self, operation_id: str) -> bool: ...

    def is_timeout_warning(self, operation_id: str) -> bool: ...

    async def get_timeout_remaining(self, operation_id: str) -> int: ...

    def clear_timeout(self, operation_id: str) -> bool: ...

    async def create_time_based_operation(
        self, operation_type: "LiteralTimeBasedType", duration_ms: int
    ) -> "ProtocolTimeBased": ...

    def is_operation_active(self, operation_id: str) -> bool: ...

    def has_operation_expired(self, operation_id: str) -> bool: ...

    async def get_active_operations(self) -> list[str]: ...

    def cleanup_expired_operations(self) -> int: ...

    async def get_time_based_metrics(self) -> dict[str, int | float]: ...

    async def reset_time_tracking(self) -> None: ...

    def schedule_interval_operation(
        self, operation_id: str, interval_ms: int
    ) -> "ProtocolTimeBased": ...

    async def set_deadline(
        self, operation_id: str, deadline: "ProtocolDateTime"
    ) -> "ProtocolTimeBased": ...

    async def get_deadline_remaining(self, operation_id: str) -> int: ...
