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

from typing import TYPE_CHECKING, Protocol, runtime_checkable
from uuid import UUID

from .protocol_memory_base import LiteralErrorCategory

if TYPE_CHECKING:
    from datetime import datetime

    from .protocol_memory_base import (
        ProtocolErrorCategoryMap,
        ProtocolMemoryErrorContext,
    )


@runtime_checkable
class ProtocolMemoryError(Protocol):
    """Protocol for standardized memory operation errors."""

    error_code: str
    error_message: str
    error_timestamp: "datetime"
    correlation_id: UUID | None
    error_category: LiteralErrorCategory

    @property
    def error_context(self) -> "ProtocolMemoryErrorContext": ...

    @property
    def recoverable(self) -> bool: ...

    @property
    def retry_strategy(self) -> str | None: ...


@runtime_checkable
class ProtocolMemoryErrorResponse(Protocol):
    """Protocol for error responses from memory operations."""

    correlation_id: UUID | None
    response_timestamp: "datetime"
    success: bool
    error: "ProtocolMemoryError"
    suggested_action: str

    @property
    def error_message(self) -> str | None: ...

    @property
    def retry_after_seconds(self) -> int | None: ...


@runtime_checkable
class ProtocolMemoryValidationError(ProtocolMemoryError, Protocol):
    """Protocol for memory validation errors."""

    validation_failures: list[str]

    @property
    def invalid_fields(self) -> list[str]: ...


@runtime_checkable
class ProtocolMemoryAuthorizationError(ProtocolMemoryError, Protocol):
    """Protocol for memory authorization errors."""

    required_permissions: list[str]
    user_permissions: list[str]

    @property
    def missing_permissions(self) -> list[str]: ...


@runtime_checkable
class ProtocolMemoryNotFoundError(ProtocolMemoryError, Protocol):
    """Protocol for memory not found errors."""

    requested_memory_id: UUID
    suggested_alternatives: list[UUID]

    async def get_search_suggestions(self) -> list[str]: ...


@runtime_checkable
class ProtocolMemoryTimeoutError(ProtocolMemoryError, Protocol):
    """Protocol for memory operation timeout errors."""

    timeout_seconds: float
    operation_type: str
    partial_results: str | None

    @property
    def progress_percentage(self) -> float | None: ...


@runtime_checkable
class ProtocolMemoryCapacityError(ProtocolMemoryError, Protocol):
    """Protocol for memory capacity/resource errors."""

    resource_type: str
    current_usage: float
    maximum_capacity: float

    @property
    def usage_percentage(self) -> float: ...


@runtime_checkable
class ProtocolMemoryCorruptionError(ProtocolMemoryError, Protocol):
    """Protocol for memory corruption/integrity errors."""

    corruption_type: str
    affected_memory_ids: list[UUID]
    recovery_possible: bool

    async def is_backup_available(self) -> bool: ...


@runtime_checkable
class ProtocolErrorRecoveryStrategy(Protocol):
    """Protocol for error recovery strategies."""

    strategy_type: str
    recovery_steps: list[str]
    estimated_recovery_time: int

    @property
    def success_probability(self) -> float: ...

    async def execute_recovery(self) -> bool: ...


@runtime_checkable
class ProtocolMemoryErrorRecoveryResponse(Protocol):
    """Protocol for error recovery operation responses."""

    correlation_id: UUID | None
    response_timestamp: "datetime"
    success: bool
    recovery_attempted: bool
    recovery_successful: bool
    recovery_strategy: "ProtocolErrorRecoveryStrategy | None"

    @property
    def error_message(self) -> str | None: ...

    @property
    def recovery_details(self) -> str | None: ...


@runtime_checkable
class ProtocolBatchErrorSummary(Protocol):
    """Protocol for batch operation error summaries."""

    total_operations: int
    failed_operations: int
    error_categories: "ProtocolErrorCategoryMap"

    @property
    def failure_rate(self) -> float: ...

    @property
    def most_common_error(self) -> str | None: ...


@runtime_checkable
class ProtocolBatchErrorResponse(Protocol):
    """Protocol for batch operation error responses."""

    correlation_id: UUID | None
    response_timestamp: "datetime"
    success: bool
    error: "ProtocolMemoryError"
    suggested_action: str
    batch_summary: "ProtocolBatchErrorSummary"
    individual_errors: list["ProtocolMemoryError"]

    @property
    def error_message(self) -> str | None: ...

    @property
    def retry_after_seconds(self) -> int | None: ...

    @property
    def partial_success_recovery(self) -> "ProtocolErrorRecoveryStrategy | None": ...
