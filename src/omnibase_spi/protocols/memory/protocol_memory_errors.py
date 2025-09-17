"""
Memory Error Protocols for OmniMemory ONEX Architecture

This module defines comprehensive error handling protocol interfaces for
memory operations. Separated from the main types module to prevent circular
imports and improve maintainability.

Contains:
- Error categorization literals
- Base error protocols
- Specific error types for each operation category
- Error response protocols
- Error recovery protocols

All types are pure protocols with no implementation dependencies.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional, Protocol, runtime_checkable
from uuid import UUID

if TYPE_CHECKING:
    from .protocol_memory_base import (
        ErrorCategory,
        ProtocolErrorCategoryMap,
        ProtocolErrorContext,
    )


# === ERROR HANDLING PROTOCOLS ===


@runtime_checkable
class ProtocolMemoryError(Protocol):
    """Protocol for standardized memory operation errors."""

    error_code: str
    error_message: str
    error_timestamp: datetime
    correlation_id: Optional[UUID]
    error_category: "ErrorCategory"

    @property
    def error_context(self) -> "ProtocolErrorContext":
        """Additional error context and debugging information."""
        ...

    @property
    def recoverable(self) -> bool:
        """Whether this error condition is recoverable."""
        ...

    @property
    def retry_strategy(self) -> Optional[str]:
        """Suggested retry strategy for recoverable errors."""
        ...


@runtime_checkable
class ProtocolMemoryErrorResponse(Protocol):
    """Protocol for error responses from memory operations."""

    correlation_id: Optional[UUID]
    response_timestamp: datetime
    success: bool
    error: ProtocolMemoryError
    suggested_action: str

    @property
    def error_message(self) -> Optional[str]:
        """Error message if operation failed."""
        ...

    @property
    def retry_after_seconds(self) -> Optional[int]:
        """Suggested retry delay for transient errors."""
        ...


# === SPECIFIC ERROR PROTOCOLS ===


@runtime_checkable
class ProtocolMemoryValidationError(ProtocolMemoryError, Protocol):
    """Protocol for memory validation errors."""

    validation_failures: list[str]

    @property
    def invalid_fields(self) -> list[str]:
        """List of fields that failed validation."""
        ...


@runtime_checkable
class ProtocolMemoryAuthorizationError(ProtocolMemoryError, Protocol):
    """Protocol for memory authorization errors."""

    required_permissions: list[str]
    user_permissions: list[str]

    @property
    def missing_permissions(self) -> list[str]:
        """Permissions required but not possessed by user."""
        ...


@runtime_checkable
class ProtocolMemoryNotFoundError(ProtocolMemoryError, Protocol):
    """Protocol for memory not found errors."""

    requested_memory_id: UUID
    suggested_alternatives: list[UUID]

    @property
    def search_suggestions(self) -> list[str]:
        """Suggested search terms to find similar memories."""
        ...


@runtime_checkable
class ProtocolMemoryTimeoutError(ProtocolMemoryError, Protocol):
    """Protocol for memory operation timeout errors."""

    timeout_seconds: float
    operation_type: str
    partial_results: Optional[str]

    @property
    def progress_percentage(self) -> Optional[float]:
        """Progress made before timeout occurred."""
        ...


@runtime_checkable
class ProtocolMemoryCapacityError(ProtocolMemoryError, Protocol):
    """Protocol for memory capacity/resource errors."""

    resource_type: str
    current_usage: float
    maximum_capacity: float

    @property
    def usage_percentage(self) -> float:
        """Current resource usage as percentage of capacity."""
        ...


@runtime_checkable
class ProtocolMemoryCorruptionError(ProtocolMemoryError, Protocol):
    """Protocol for memory corruption/integrity errors."""

    corruption_type: str
    affected_memory_ids: list[UUID]
    recovery_possible: bool

    @property
    def backup_available(self) -> bool:
        """Whether backup copies are available for recovery."""
        ...


# === ERROR RECOVERY PROTOCOLS ===


@runtime_checkable
class ProtocolErrorRecoveryStrategy(Protocol):
    """Protocol for error recovery strategies."""

    strategy_type: str
    recovery_steps: list[str]
    estimated_recovery_time: int

    @property
    def success_probability(self) -> float:
        """Estimated probability of successful recovery."""
        ...

    async def execute_recovery(self) -> bool:
        """Execute the recovery strategy."""
        ...


@runtime_checkable
class ProtocolMemoryErrorRecoveryResponse(Protocol):
    """Protocol for error recovery operation responses."""

    correlation_id: Optional[UUID]
    response_timestamp: datetime
    success: bool
    recovery_attempted: bool
    recovery_successful: bool
    recovery_strategy: Optional[ProtocolErrorRecoveryStrategy]

    @property
    def error_message(self) -> Optional[str]:
        """Error message if operation failed."""
        ...

    @property
    def recovery_details(self) -> Optional[str]:
        """Details about the recovery attempt."""
        ...


# === BATCH ERROR PROTOCOLS ===


@runtime_checkable
class ProtocolBatchErrorSummary(Protocol):
    """Protocol for batch operation error summaries."""

    total_operations: int
    failed_operations: int
    error_categories: "ProtocolErrorCategoryMap"

    @property
    def failure_rate(self) -> float:
        """Percentage of operations that failed."""
        ...

    @property
    def most_common_error(self) -> Optional[str]:
        """Most frequently occurring error type."""
        ...


@runtime_checkable
class ProtocolBatchErrorResponse(Protocol):
    """Protocol for batch operation error responses."""

    correlation_id: Optional[UUID]
    response_timestamp: datetime
    success: bool
    error: ProtocolMemoryError
    suggested_action: str
    batch_summary: ProtocolBatchErrorSummary
    individual_errors: list[ProtocolMemoryError]

    @property
    def error_message(self) -> Optional[str]:
        """Error message if operation failed."""
        ...

    @property
    def retry_after_seconds(self) -> Optional[int]:
        """Suggested retry delay for transient errors."""
        ...

    @property
    def partial_success_recovery(self) -> Optional[ProtocolErrorRecoveryStrategy]:
        """Recovery strategy for partial batch failures."""
        ...
