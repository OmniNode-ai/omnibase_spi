"""
Protocol for Time-Based Operations and Measurements.

Defines interfaces for duration tracking, timeout management, and time-based
scheduling across all ONEX services with consistent patterns.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

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
        # Implementation example (not part of SPI)
        class TimeBasedOperationImpl:
            async def start_duration_tracking(self, operation_id):
                duration = DurationRecord(  # implements ProtocolDuration
                    start_time=datetime.now(),
                    end_time=None,
                    is_completed=False
                )
                self._active_durations[operation_id] = duration
                return duration

            def set_timeout(self, operation_id, timeout_ms):
                timeout = TimeoutTracker(  # implements ProtocolTimeout
                    timeout_ms=timeout_ms,
                    start_time=datetime.now(),
                    warning_threshold_ms=timeout_ms * 0.8
                )
                self._active_timeouts[operation_id] = timeout
                return timeout

        # Usage in application code
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

    async def start_duration_tracking(self, operation_id: str) -> "ProtocolDuration":
        """
        Start duration tracking for an operation.

        Args:
            operation_id: Unique identifier for the operation

        Returns:
            Duration tracker for the operation

        Note:
            Creates a new duration measurement starting from current time.
            Operation can be completed later using complete_duration_tracking().
        """
        ...

    def complete_duration_tracking(self, operation_id: str) -> "ProtocolDuration":
        """
        Complete duration tracking for an operation.

        Args:
            operation_id: Unique identifier for the operation

        Returns:
            Completed duration measurement with total time

        Note:
            Sets end time and calculates total duration.
            Operation must have been started with start_duration_tracking().
        """
        ...

    def get_operation_duration(self, operation_id: str) -> "ProtocolDuration":
        """
        Get current duration for an active operation.

        Args:
            operation_id: Unique identifier for the operation

        Returns:
            Current duration measurement (may be incomplete)

        Note:
            Returns current duration even if operation is still active.
            For completed operations, returns final duration.
        """
        ...

    def set_timeout(
        self,
        operation_id: str,
        timeout_ms: int,
        warning_threshold_ms: int | None = None,
    ) -> "ProtocolTimeout":
        """
        Set timeout for an operation.

        Args:
            operation_id: Unique identifier for the operation
            timeout_ms: Timeout duration in milliseconds
            warning_threshold_ms: Optional early warning threshold

        Returns:
            Timeout tracker for the operation

        Note:
            Creates timeout monitoring for operation. Warning threshold
            allows proactive timeout handling before actual expiration.
        """
        ...

    def is_timeout_expired(self, operation_id: str) -> bool:
        """
        Check if operation has timed out.

        Args:
            operation_id: Unique identifier for the operation

        Returns:
            True if operation has exceeded its timeout

        Note:
            Returns False if no timeout is set for the operation.
        """
        ...

    def is_timeout_warning(self, operation_id: str) -> bool:
        """
        Check if operation is approaching timeout.

        Args:
            operation_id: Unique identifier for the operation

        Returns:
            True if operation is within warning threshold of timeout

        Note:
            Allows proactive handling before actual timeout occurs.
            Returns False if no warning threshold is configured.
        """
        ...

    def get_timeout_remaining(self, operation_id: str) -> int:
        """
        Get remaining time before timeout.

        Args:
            operation_id: Unique identifier for the operation

        Returns:
            Milliseconds remaining before timeout (0 if expired)

        Note:
            Returns 0 if timeout has already expired.
            Returns -1 if no timeout is set for the operation.
        """
        ...

    def clear_timeout(self, operation_id: str) -> bool:
        """
        Clear timeout for an operation.

        Args:
            operation_id: Unique identifier for the operation

        Returns:
            True if timeout was cleared successfully

        Note:
            Removes timeout monitoring for the operation.
            Operation will no longer be subject to timeout constraints.
        """
        ...

    async def create_time_based_operation(
        self, operation_type: "LiteralTimeBasedType", duration_ms: int
    ) -> "ProtocolTimeBased":
        """
        Create a time-based operation tracker.

        Args:
            operation_type: Type of time operation (duration, timeout, interval, deadline)
            duration_ms: Duration in milliseconds for the operation

        Returns:
            Time-based operation tracker

        Note:
            Creates generic time-based operation for various timing patterns.
            Type determines behavior: duration tracks elapsed time, timeout enforces limits.
        """
        ...

    def is_operation_active(self, operation_id: str) -> bool:
        """
        Check if time-based operation is currently active.

        Args:
            operation_id: Unique identifier for the operation

        Returns:
            True if operation is active (not completed or expired)

        Note:
            Active means operation is currently running and within time limits.
        """
        ...

    def has_operation_expired(self, operation_id: str) -> bool:
        """
        Check if time-based operation has expired.

        Args:
            operation_id: Unique identifier for the operation

        Returns:
            True if operation has exceeded its time limits

        Note:
            Expiration can occur due to timeout, deadline, or completion.
        """
        ...

    def get_active_operations(self) -> list[str]:
        """
        Get list of all active time-based operations.

        Returns:
            List of operation IDs that are currently active

        Note:
            Includes operations with active durations, timeouts, or intervals.
            Useful for monitoring and cleanup operations.
        """
        ...

    def cleanup_expired_operations(self) -> int:
        """
        Clean up expired time-based operations.

        Returns:
            Number of operations cleaned up

        Note:
            Removes tracking for operations that have expired or completed.
            Helps prevent memory leaks in long-running services.
        """
        ...

    def get_time_based_metrics(self) -> dict[str, int | float]:
        """
        Get time-based operation metrics.

        Returns:
            Dictionary with timing statistics and performance metrics

        Note:
            Provides insights into operation timing patterns, timeout rates,
            and system performance for monitoring dashboards.
        """
        ...

    def reset_time_tracking(self) -> None:
        """
        Reset all time tracking operations.

        Note:
            Clears all active durations, timeouts, and time-based operations.
            Used for testing or service restart scenarios.
        """
        ...

    def schedule_interval_operation(
        self, operation_id: str, interval_ms: int
    ) -> "ProtocolTimeBased":
        """
        Schedule recurring interval-based operation.

        Args:
            operation_id: Unique identifier for the recurring operation
            interval_ms: Interval between operations in milliseconds

        Returns:
            Interval tracker for the recurring operation

        Note:
            Creates recurring time-based operation that triggers at specified intervals.
            Useful for periodic tasks, health checks, and maintenance operations.
        """
        ...

    def set_deadline(
        self, operation_id: str, deadline: "ProtocolDateTime"
    ) -> "ProtocolTimeBased":
        """
        Set absolute deadline for an operation.

        Args:
            operation_id: Unique identifier for the operation
            deadline: Absolute datetime by which operation must complete

        Returns:
            Deadline tracker for the operation

        Note:
            Creates deadline-based time tracking with absolute end time.
            Different from timeout which uses relative duration.
        """
        ...

    def get_deadline_remaining(self, operation_id: str) -> int:
        """
        Get time remaining until deadline.

        Args:
            operation_id: Unique identifier for the operation

        Returns:
            Milliseconds remaining until deadline (0 if passed)

        Note:
            Returns 0 if deadline has already passed.
            Returns -1 if no deadline is set for the operation.
        """
        ...
