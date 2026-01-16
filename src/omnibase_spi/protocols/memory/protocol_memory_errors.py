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

from omnibase_spi.protocols.memory.protocol_memory_base import LiteralErrorCategory

if TYPE_CHECKING:
    from datetime import datetime

    from omnibase_spi.protocols.memory.protocol_memory_base import (
        ProtocolErrorCategoryMap,
        ProtocolMemoryErrorContext,
    )


@runtime_checkable
class ProtocolMemoryError(Protocol):
    """
    Protocol for standardized memory operation errors.

    This protocol defines the base interface for all memory error types.
    It provides consistent error categorization, context preservation,
    and recovery guidance across all memory operations.

    Implementations should provide meaningful error codes and messages
    that enable proper error handling and user feedback.

    Attributes:
        error_code: Unique error code for programmatic handling.
        error_message: Human-readable error description.
        error_timestamp: When the error occurred.
        correlation_id: Request correlation ID for tracing.
        error_category: Category for error classification.

    Example:
        ```python
        class MemoryError:
            '''Concrete implementation of ProtocolMemoryError.'''

            def __init__(
                self,
                error_code: str,
                error_message: str,
                correlation_id: UUID | None = None,
            ) -> None:
                self.error_code = error_code
                self.error_message = error_message
                self.error_timestamp = datetime.now(UTC)
                self.correlation_id = correlation_id
                self.error_category: LiteralErrorCategory = "permanent"
                self._context = MemoryErrorContext()

            @property
            def error_context(self) -> ProtocolMemoryErrorContext:
                return self._context

            @property
            def recoverable(self) -> bool:
                return self.error_category == "transient"

            @property
            def retry_strategy(self) -> str | None:
                if self.recoverable:
                    return "exponential_backoff"
                return None

        # Usage
        error = MemoryError(
            error_code="MEM_001",
            error_message="Memory storage failed",
        )
        assert isinstance(error, ProtocolMemoryError)
        ```

    See Also:
        - ProtocolMemoryErrorResponse: For error response structure.
        - ProtocolMemoryValidationError: For validation-specific errors.
    """

    error_code: str
    error_message: str
    error_timestamp: datetime
    correlation_id: UUID | None
    error_category: LiteralErrorCategory

    @property
    def error_context(self) -> ProtocolMemoryErrorContext: ...

    @property
    def recoverable(self) -> bool: ...

    @property
    def retry_strategy(self) -> str | None: ...


@runtime_checkable
class ProtocolMemoryErrorResponse(Protocol):
    """
    Protocol for error responses from memory operations.

    This protocol defines the interface for structured error responses
    that include the error details, suggested recovery actions, and
    retry guidance for transient errors.

    Implementations should provide actionable suggested actions and
    appropriate retry timing for recoverable errors.

    Attributes:
        correlation_id: Request correlation ID for tracing.
        response_timestamp: When the response was generated.
        success: Always False for error responses.
        error: The detailed error information.
        suggested_action: Recommended action for error recovery.

    Example:
        ```python
        class MemoryErrorResponse:
            '''Concrete implementation of ProtocolMemoryErrorResponse.'''

            def __init__(
                self,
                correlation_id: UUID | None,
                error: ProtocolMemoryError,
                suggested_action: str,
            ) -> None:
                self.correlation_id = correlation_id
                self.response_timestamp = datetime.now(UTC)
                self.success = False
                self.error = error
                self.suggested_action = suggested_action

            @property
            def error_message(self) -> str | None:
                return self.error.error_message

            @property
            def retry_after_seconds(self) -> int | None:
                if self.error.recoverable:
                    return 5
                return None

        # Usage
        response = MemoryErrorResponse(
            correlation_id=uuid4(),
            error=error,
            suggested_action="Retry the operation after 5 seconds",
        )
        assert isinstance(response, ProtocolMemoryErrorResponse)
        assert not response.success
        ```

    See Also:
        - ProtocolMemoryError: For the error detail structure.
        - ProtocolMemoryResponse: For successful response structure.
    """

    correlation_id: UUID | None
    response_timestamp: datetime
    success: bool
    error: ProtocolMemoryError
    suggested_action: str

    @property
    def error_message(self) -> str | None: ...

    @property
    def retry_after_seconds(self) -> int | None: ...


@runtime_checkable
class ProtocolMemoryValidationError(ProtocolMemoryError, Protocol):
    """
    Protocol for memory validation errors during storage or update.

    This protocol extends the base error with validation-specific details
    including the list of validation failures and invalid field names.
    Validation errors are typically non-recoverable without user correction.

    Implementations should provide clear validation failure messages that
    help users understand what data corrections are needed.

    Attributes:
        validation_failures: List of validation failure descriptions.

    Example:
        ```python
        class MemoryValidationError:
            '''Concrete implementation of ProtocolMemoryValidationError.'''

            def __init__(
                self,
                validation_failures: list[str],
                invalid_fields: list[str],
            ) -> None:
                self.error_code = "MEM_VALIDATION"
                self.error_message = "Validation failed for memory content"
                self.error_timestamp = datetime.now(UTC)
                self.correlation_id = None
                self.error_category: LiteralErrorCategory = "validation"
                self.validation_failures = validation_failures
                self._invalid_fields = invalid_fields

            @property
            def error_context(self) -> ProtocolMemoryErrorContext:
                return MemoryErrorContext()

            @property
            def recoverable(self) -> bool:
                return False

            @property
            def retry_strategy(self) -> str | None:
                return None

            @property
            def invalid_fields(self) -> list[str]:
                return self._invalid_fields

        # Usage
        error = MemoryValidationError(
            validation_failures=["Content exceeds max length", "Invalid content type"],
            invalid_fields=["content", "content_type"],
        )
        assert isinstance(error, ProtocolMemoryValidationError)
        ```

    See Also:
        - ProtocolMemoryError: For the base error structure.
    """

    validation_failures: list[str]

    @property
    def invalid_fields(self) -> list[str]: ...


@runtime_checkable
class ProtocolMemoryAuthorizationError(ProtocolMemoryError, Protocol):
    """
    Protocol for memory authorization and access control errors.

    This protocol extends the base error with authorization-specific details
    including required permissions, current user permissions, and the
    list of missing permissions needed for the operation.

    Implementations should clearly identify what permissions are needed
    and which are missing to support proper access control debugging.

    Attributes:
        required_permissions: Permissions required for the operation.
        user_permissions: Current permissions of the requesting user.

    Example:
        ```python
        class MemoryAuthorizationError:
            '''Concrete implementation of ProtocolMemoryAuthorizationError.'''

            def __init__(
                self,
                required_permissions: list[str],
                user_permissions: list[str],
            ) -> None:
                self.error_code = "MEM_UNAUTHORIZED"
                self.error_message = "Insufficient permissions for memory access"
                self.error_timestamp = datetime.now(UTC)
                self.correlation_id = None
                self.error_category: LiteralErrorCategory = "authorization"
                self.required_permissions = required_permissions
                self.user_permissions = user_permissions

            @property
            def error_context(self) -> ProtocolMemoryErrorContext:
                return MemoryErrorContext()

            @property
            def recoverable(self) -> bool:
                return False

            @property
            def retry_strategy(self) -> str | None:
                return None

            @property
            def missing_permissions(self) -> list[str]:
                return [p for p in self.required_permissions if p not in self.user_permissions]

        # Usage
        error = MemoryAuthorizationError(
            required_permissions=["read", "write"],
            user_permissions=["read"],
        )
        assert isinstance(error, ProtocolMemoryAuthorizationError)
        assert error.missing_permissions == ["write"]
        ```

    See Also:
        - ProtocolMemoryError: For the base error structure.
    """

    required_permissions: list[str]
    user_permissions: list[str]

    @property
    def missing_permissions(self) -> list[str]: ...


@runtime_checkable
class ProtocolMemoryNotFoundError(ProtocolMemoryError, Protocol):
    """
    Protocol for memory not found errors during retrieval operations.

    This protocol extends the base error with not-found-specific details
    including the requested memory ID and suggested alternative memories
    that might be relevant.

    Implementations should provide helpful search suggestions when a
    memory is not found to aid in finding related content.

    Attributes:
        requested_memory_id: UUID of the memory that was not found.
        suggested_alternatives: List of similar memory UUIDs.

    Example:
        ```python
        class MemoryNotFoundError:
            '''Concrete implementation of ProtocolMemoryNotFoundError.'''

            def __init__(
                self,
                requested_memory_id: UUID,
                suggested_alternatives: list[UUID] | None = None,
            ) -> None:
                self.error_code = "MEM_NOT_FOUND"
                self.error_message = f"Memory {requested_memory_id} not found"
                self.error_timestamp = datetime.now(UTC)
                self.correlation_id = None
                self.error_category: LiteralErrorCategory = "permanent"
                self.requested_memory_id = requested_memory_id
                self.suggested_alternatives = suggested_alternatives or []

            @property
            def error_context(self) -> ProtocolMemoryErrorContext:
                return MemoryErrorContext()

            @property
            def recoverable(self) -> bool:
                return False

            @property
            def retry_strategy(self) -> str | None:
                return None

            async def get_search_suggestions(self) -> list[str]:
                return ["Try searching by content", "Check memory ID"]

        # Usage
        error = MemoryNotFoundError(
            requested_memory_id=uuid4(),
            suggested_alternatives=[uuid4(), uuid4()],
        )
        assert isinstance(error, ProtocolMemoryNotFoundError)
        ```

    See Also:
        - ProtocolMemoryError: For the base error structure.
        - ProtocolMemoryRetrieveRequest: For retrieval operations.
    """

    requested_memory_id: UUID
    suggested_alternatives: list[UUID]

    async def get_search_suggestions(self) -> list[str]: ...


@runtime_checkable
class ProtocolMemoryTimeoutError(ProtocolMemoryError, Protocol):
    """
    Protocol for memory operation timeout errors.

    This protocol extends the base error with timeout-specific details
    including the timeout threshold, operation type, and any partial
    results that were obtained before the timeout.

    Implementations should preserve partial results when possible and
    provide progress information to enable resume operations.

    Attributes:
        timeout_seconds: The timeout threshold that was exceeded.
        operation_type: Type of operation that timed out.
        partial_results: Results obtained before timeout, if available.

    Example:
        ```python
        class MemoryTimeoutError:
            '''Concrete implementation of ProtocolMemoryTimeoutError.'''

            def __init__(
                self,
                timeout_seconds: float,
                operation_type: str,
                progress: float | None = None,
            ) -> None:
                self.error_code = "MEM_TIMEOUT"
                self.error_message = f"Operation {operation_type} timed out after {timeout_seconds}s"
                self.error_timestamp = datetime.now(UTC)
                self.correlation_id = None
                self.error_category: LiteralErrorCategory = "transient"
                self.timeout_seconds = timeout_seconds
                self.operation_type = operation_type
                self.partial_results = None
                self._progress = progress

            @property
            def error_context(self) -> ProtocolMemoryErrorContext:
                return MemoryErrorContext()

            @property
            def recoverable(self) -> bool:
                return True

            @property
            def retry_strategy(self) -> str | None:
                return "exponential_backoff"

            @property
            def progress_percentage(self) -> float | None:
                return self._progress

        # Usage
        error = MemoryTimeoutError(
            timeout_seconds=30.0,
            operation_type="batch_store",
            progress=0.75,
        )
        assert isinstance(error, ProtocolMemoryTimeoutError)
        assert error.recoverable
        ```

    See Also:
        - ProtocolMemoryError: For the base error structure.
    """

    timeout_seconds: float
    operation_type: str
    partial_results: str | None

    @property
    def progress_percentage(self) -> float | None: ...


@runtime_checkable
class ProtocolMemoryCapacityError(ProtocolMemoryError, Protocol):
    """
    Protocol for memory capacity and resource exhaustion errors.

    This protocol extends the base error with capacity-specific details
    including resource type, current usage, and maximum capacity.
    These errors indicate resource limits have been reached.

    Implementations should provide clear usage metrics to enable
    capacity planning and resource management decisions.

    Attributes:
        resource_type: Type of resource exhausted (storage, memory, etc.).
        current_usage: Current usage of the resource.
        maximum_capacity: Maximum allowed capacity for the resource.

    Example:
        ```python
        class MemoryCapacityError:
            '''Concrete implementation of ProtocolMemoryCapacityError.'''

            def __init__(
                self,
                resource_type: str,
                current_usage: float,
                maximum_capacity: float,
            ) -> None:
                self.error_code = "MEM_CAPACITY"
                self.error_message = f"Resource {resource_type} capacity exceeded"
                self.error_timestamp = datetime.now(UTC)
                self.correlation_id = None
                self.error_category: LiteralErrorCategory = "permanent"
                self.resource_type = resource_type
                self.current_usage = current_usage
                self.maximum_capacity = maximum_capacity

            @property
            def error_context(self) -> ProtocolMemoryErrorContext:
                return MemoryErrorContext()

            @property
            def recoverable(self) -> bool:
                return False

            @property
            def retry_strategy(self) -> str | None:
                return None

            @property
            def usage_percentage(self) -> float:
                return (self.current_usage / self.maximum_capacity) * 100

        # Usage
        error = MemoryCapacityError(
            resource_type="storage",
            current_usage=950.0,
            maximum_capacity=1000.0,
        )
        assert isinstance(error, ProtocolMemoryCapacityError)
        assert error.usage_percentage == 95.0
        ```

    See Also:
        - ProtocolMemoryError: For the base error structure.
    """

    resource_type: str
    current_usage: float
    maximum_capacity: float

    @property
    def usage_percentage(self) -> float: ...


@runtime_checkable
class ProtocolMemoryCorruptionError(ProtocolMemoryError, Protocol):
    """
    Protocol for memory corruption and data integrity errors.

    This protocol extends the base error with corruption-specific details
    including the type of corruption, affected memories, and whether
    recovery is possible from backups.

    Implementations should identify all affected memories and provide
    information about backup availability for recovery operations.

    Attributes:
        corruption_type: Type of corruption detected (checksum, format, etc.).
        affected_memory_ids: List of memory UUIDs affected by corruption.
        recovery_possible: Whether recovery from backup is possible.

    Example:
        ```python
        class MemoryCorruptionError:
            '''Concrete implementation of ProtocolMemoryCorruptionError.'''

            def __init__(
                self,
                corruption_type: str,
                affected_memory_ids: list[UUID],
                recovery_possible: bool,
            ) -> None:
                self.error_code = "MEM_CORRUPT"
                self.error_message = f"Memory corruption detected: {corruption_type}"
                self.error_timestamp = datetime.now(UTC)
                self.correlation_id = None
                self.error_category: LiteralErrorCategory = "permanent"
                self.corruption_type = corruption_type
                self.affected_memory_ids = affected_memory_ids
                self.recovery_possible = recovery_possible

            @property
            def error_context(self) -> ProtocolMemoryErrorContext:
                return MemoryErrorContext()

            @property
            def recoverable(self) -> bool:
                return self.recovery_possible

            @property
            def retry_strategy(self) -> str | None:
                return "restore_from_backup" if self.recovery_possible else None

            async def is_backup_available(self) -> bool:
                return self.recovery_possible

        # Usage
        error = MemoryCorruptionError(
            corruption_type="checksum_mismatch",
            affected_memory_ids=[uuid4(), uuid4()],
            recovery_possible=True,
        )
        assert isinstance(error, ProtocolMemoryCorruptionError)
        ```

    See Also:
        - ProtocolMemoryError: For the base error structure.
        - ProtocolErrorRecoveryStrategy: For recovery operations.
    """

    corruption_type: str
    affected_memory_ids: list[UUID]
    recovery_possible: bool

    async def is_backup_available(self) -> bool: ...


@runtime_checkable
class ProtocolErrorRecoveryStrategy(Protocol):
    """
    Protocol for error recovery strategy definitions.

    This protocol defines the interface for describing and executing
    recovery strategies for recoverable memory errors. Strategies include
    the type, steps, estimated time, and success probability.

    Implementations should provide executable recovery procedures and
    realistic success probability estimates based on error type.

    Attributes:
        strategy_type: Type of recovery strategy (retry, rollback, restore).
        recovery_steps: Ordered list of recovery step descriptions.
        estimated_recovery_time: Estimated time to complete recovery in seconds.

    Example:
        ```python
        class ErrorRecoveryStrategy:
            '''Concrete implementation of ProtocolErrorRecoveryStrategy.'''

            def __init__(
                self,
                strategy_type: str,
                recovery_steps: list[str],
            ) -> None:
                self.strategy_type = strategy_type
                self.recovery_steps = recovery_steps
                self.estimated_recovery_time = len(recovery_steps) * 5

            @property
            def success_probability(self) -> float:
                if self.strategy_type == "retry":
                    return 0.85
                elif self.strategy_type == "restore":
                    return 0.95
                return 0.50

            async def execute_recovery(self) -> bool:
                # Execute recovery steps
                for step in self.recovery_steps:
                    pass  # Execute step
                return True

        # Usage
        strategy = ErrorRecoveryStrategy(
            strategy_type="retry",
            recovery_steps=["Wait for backoff", "Retry operation"],
        )
        assert isinstance(strategy, ProtocolErrorRecoveryStrategy)
        ```

    See Also:
        - ProtocolMemoryErrorRecoveryResponse: For recovery operation responses.
    """

    strategy_type: str
    recovery_steps: list[str]
    estimated_recovery_time: int

    @property
    def success_probability(self) -> float: ...

    async def execute_recovery(self) -> bool: ...


@runtime_checkable
class ProtocolMemoryErrorRecoveryResponse(Protocol):
    """
    Protocol for error recovery operation responses.

    This protocol defines the interface for responses from error recovery
    attempts. It includes information about whether recovery was attempted,
    its success, and details about the recovery strategy used.

    Implementations should provide detailed recovery information and
    clear success/failure indicators for monitoring.

    Attributes:
        correlation_id: Request correlation ID for tracing.
        response_timestamp: When the response was generated.
        success: Overall success of the operation.
        recovery_attempted: Whether recovery was attempted.
        recovery_successful: Whether recovery succeeded.
        recovery_strategy: The recovery strategy that was used.

    Example:
        ```python
        class MemoryErrorRecoveryResponse:
            '''Concrete implementation of ProtocolMemoryErrorRecoveryResponse.'''

            def __init__(
                self,
                correlation_id: UUID | None,
                recovery_strategy: ProtocolErrorRecoveryStrategy | None,
                recovery_successful: bool,
            ) -> None:
                self.correlation_id = correlation_id
                self.response_timestamp = datetime.now(UTC)
                self.recovery_attempted = recovery_strategy is not None
                self.recovery_successful = recovery_successful
                self.success = recovery_successful
                self.recovery_strategy = recovery_strategy

            @property
            def error_message(self) -> str | None:
                if not self.recovery_successful:
                    return "Recovery failed"
                return None

            @property
            def recovery_details(self) -> str | None:
                if self.recovery_strategy:
                    return f"Used strategy: {self.recovery_strategy.strategy_type}"
                return None

        # Usage
        response = MemoryErrorRecoveryResponse(
            correlation_id=uuid4(),
            recovery_strategy=strategy,
            recovery_successful=True,
        )
        assert isinstance(response, ProtocolMemoryErrorRecoveryResponse)
        ```

    See Also:
        - ProtocolErrorRecoveryStrategy: For the recovery strategy structure.
    """

    correlation_id: UUID | None
    response_timestamp: datetime
    success: bool
    recovery_attempted: bool
    recovery_successful: bool
    recovery_strategy: ProtocolErrorRecoveryStrategy | None

    @property
    def error_message(self) -> str | None: ...

    @property
    def recovery_details(self) -> str | None: ...


@runtime_checkable
class ProtocolBatchErrorSummary(Protocol):
    """
    Protocol for batch operation error summaries.

    This protocol defines the interface for summarizing errors that occurred
    during batch operations. It provides aggregated error statistics and
    categorization for monitoring and debugging.

    Implementations should accurately categorize errors and identify the
    most common error type for troubleshooting.

    Attributes:
        total_operations: Total number of operations attempted.
        failed_operations: Number of operations that failed.
        error_categories: Map of error categories to their counts.

    Example:
        ```python
        class BatchErrorSummary:
            '''Concrete implementation of ProtocolBatchErrorSummary.'''

            def __init__(
                self,
                total_operations: int,
                failed_operations: int,
                error_categories: ProtocolErrorCategoryMap,
            ) -> None:
                self.total_operations = total_operations
                self.failed_operations = failed_operations
                self.error_categories = error_categories

            @property
            def failure_rate(self) -> float:
                if self.total_operations == 0:
                    return 0.0
                return self.failed_operations / self.total_operations

            @property
            def most_common_error(self) -> str | None:
                categories = self.error_categories.category_names
                if not categories:
                    return None
                # Return category with highest count
                return max(categories, key=lambda c: self.error_categories._counts.get(c, 0))

        # Usage
        summary = BatchErrorSummary(
            total_operations=100,
            failed_operations=5,
            error_categories=error_category_map,
        )
        assert isinstance(summary, ProtocolBatchErrorSummary)
        assert summary.failure_rate == 0.05
        ```

    See Also:
        - ProtocolBatchErrorResponse: Uses this for batch error details.
        - ProtocolErrorCategoryMap: For error category structure.
    """

    total_operations: int
    failed_operations: int
    error_categories: ProtocolErrorCategoryMap

    @property
    def failure_rate(self) -> float: ...

    @property
    def most_common_error(self) -> str | None: ...


@runtime_checkable
class ProtocolBatchErrorResponse(Protocol):
    """
    Protocol for batch operation error responses.

    This protocol defines the interface for structured error responses from
    batch operations. It includes the overall error, batch summary statistics,
    and individual errors for each failed operation.

    Implementations should provide detailed per-operation error information
    and support partial success recovery when applicable.

    Attributes:
        correlation_id: Request correlation ID for tracing.
        response_timestamp: When the response was generated.
        success: Overall success (False if any operation failed).
        error: The primary error for the batch.
        suggested_action: Recommended action for error handling.
        batch_summary: Summary of batch operation results.
        individual_errors: List of errors for each failed operation.

    Example:
        ```python
        class BatchErrorResponse:
            '''Concrete implementation of ProtocolBatchErrorResponse.'''

            def __init__(
                self,
                correlation_id: UUID | None,
                error: ProtocolMemoryError,
                batch_summary: ProtocolBatchErrorSummary,
                individual_errors: list[ProtocolMemoryError],
            ) -> None:
                self.correlation_id = correlation_id
                self.response_timestamp = datetime.now(UTC)
                self.success = False
                self.error = error
                self.suggested_action = "Review individual errors"
                self.batch_summary = batch_summary
                self.individual_errors = individual_errors

            @property
            def error_message(self) -> str | None:
                return f"Batch operation failed: {self.batch_summary.failed_operations} errors"

            @property
            def retry_after_seconds(self) -> int | None:
                if any(e.recoverable for e in self.individual_errors):
                    return 5
                return None

            @property
            def partial_success_recovery(self) -> ProtocolErrorRecoveryStrategy | None:
                if self.batch_summary.failed_operations < self.batch_summary.total_operations:
                    return ErrorRecoveryStrategy("retry_failed", ["Retry failed operations"])
                return None

        # Usage
        response = BatchErrorResponse(
            correlation_id=uuid4(),
            error=error,
            batch_summary=summary,
            individual_errors=[error1, error2],
        )
        assert isinstance(response, ProtocolBatchErrorResponse)
        ```

    See Also:
        - ProtocolBatchErrorSummary: For batch statistics.
        - ProtocolBatchMemoryStoreResponse: For batch store responses.
    """

    correlation_id: UUID | None
    response_timestamp: datetime
    success: bool
    error: ProtocolMemoryError
    suggested_action: str
    batch_summary: ProtocolBatchErrorSummary
    individual_errors: list[ProtocolMemoryError]

    @property
    def error_message(self) -> str | None: ...

    @property
    def retry_after_seconds(self) -> int | None: ...

    @property
    def partial_success_recovery(self) -> ProtocolErrorRecoveryStrategy | None: ...
