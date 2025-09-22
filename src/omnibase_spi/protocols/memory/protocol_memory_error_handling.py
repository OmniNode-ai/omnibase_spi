"""
Enhanced error handling protocol definitions for OmniMemory operations.

Defines error categorization, retry policies, compensation/rollback patterns,
and comprehensive error recovery for memory operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Protocol, runtime_checkable
from uuid import UUID

if TYPE_CHECKING:
    from datetime import datetime

    from .protocol_memory_base import ProtocolMemoryMetadata


@runtime_checkable
class ProtocolErrorCategory(Protocol):
    """
    Error category classification for memory operations.

    Categorizes errors as transient, permanent, security, validation,
    or infrastructure to enable appropriate error handling strategies.
    """

    @property
    def error_type(self) -> str:
        """Primary error type (transient, permanent, security, validation, infrastructure)."""
        ...

    @property
    def error_code(self) -> str:
        """Specific error code for programmatic handling."""
        ...

    @property
    def error_severity(self) -> str:
        """Error severity (low, medium, high, critical)."""
        ...

    @property
    def is_recoverable(self) -> bool:
        """Whether this error can be recovered from."""
        ...

    @property
    def recovery_strategy(self) -> str:
        """Recommended recovery strategy."""
        ...

    @property
    def requires_user_intervention(self) -> bool:
        """Whether this error requires user intervention."""
        ...

    @property
    def compliance_impact(self) -> Optional[str]:
        """Compliance frameworks impacted by this error."""
        ...


@runtime_checkable
class ProtocolRetryPolicy(Protocol):
    """
    Retry policy configuration for error recovery.

    Defines retry behavior, backoff strategies, and retry limits
    for different types of operations and error conditions.
    """

    @property
    def max_retries(self) -> int:
        """Maximum number of retry attempts."""
        ...

    @property
    def initial_delay_seconds(self) -> float:
        """Initial delay before first retry."""
        ...

    @property
    def backoff_strategy(self) -> str:
        """Backoff strategy (linear, exponential, fibonacci)."""
        ...

    @property
    def backoff_multiplier(self) -> float:
        """Multiplier for backoff calculation."""
        ...

    @property
    def max_delay_seconds(self) -> float:
        """Maximum delay between retries."""
        ...

    @property
    def jitter_enabled(self) -> bool:
        """Whether to add random jitter to delays."""
        ...

    @property
    def retry_on_error_types(self) -> list[str]:
        """Error types that should trigger retries."""
        ...

    @property
    def circuit_breaker_enabled(self) -> bool:
        """Whether circuit breaker is enabled."""
        ...

    @property
    def circuit_breaker_threshold(self) -> int:
        """Failure threshold for circuit breaker."""
        ...


@runtime_checkable
class ProtocolCompensationAction(Protocol):
    """
    Compensation action for failed operations.

    Defines rollback, cleanup, and compensation actions to maintain
    data consistency when operations fail partially or completely.
    """

    @property
    def action_id(self) -> UUID:
        """Unique identifier for this compensation action."""
        ...

    @property
    def action_type(self) -> str:
        """Type of compensation action (rollback, cleanup, notify)."""
        ...

    @property
    def target_operation_id(self) -> UUID:
        """ID of the failed operation being compensated."""
        ...

    @property
    def compensation_order(self) -> int:
        """Order in which compensation should be executed."""
        ...

    @property
    def is_idempotent(self) -> bool:
        """Whether this action can be safely repeated."""
        ...

    @property
    def timeout_seconds(self) -> float:
        """Timeout for compensation action execution."""
        ...

    @property
    def action_metadata(self) -> "ProtocolMemoryMetadata":
        """Additional metadata for compensation action."""
        ...


@runtime_checkable
class ProtocolOperationContext(Protocol):
    """
    Context information for operation tracking and error recovery.

    Maintains operation state, dependencies, and recovery information
    for comprehensive error handling and rollback capabilities.
    """

    @property
    def operation_id(self) -> UUID:
        """Unique identifier for this operation."""
        ...

    @property
    def operation_type(self) -> str:
        """Type of operation being performed."""
        ...

    @property
    def parent_operation_id(self) -> Optional[UUID]:
        """Parent operation ID for nested operations."""
        ...

    @property
    def correlation_id(self) -> UUID:
        """Correlation ID for request tracking."""
        ...

    @property
    def started_at(self) -> "datetime":
        """Timestamp when operation started."""
        ...

    @property
    def timeout_at(self) -> Optional["datetime"]:
        """Timestamp when operation times out."""
        ...

    @property
    def dependencies(self) -> list[UUID]:
        """List of operation IDs this operation depends on."""
        ...

    @property
    def compensation_actions(self) -> list["ProtocolCompensationAction"]:
        """List of compensation actions for rollback."""
        ...

    @property
    def operation_metadata(self) -> "ProtocolMemoryMetadata":
        """Additional operation metadata."""
        ...


@runtime_checkable
class ProtocolMemoryErrorHandler(Protocol):
    """
    Error handling and recovery for memory operations.

    Provides comprehensive error categorization, retry handling,
    compensation execution, and error reporting capabilities.
    """

    async def categorize_error(
        self,
        error: Exception,
        operation_context: "ProtocolOperationContext",
        correlation_id: Optional[UUID] = None,
    ) -> "ProtocolErrorCategory":
        """
        Categorize error for appropriate handling strategy.

        Args:
            error: Exception that occurred
            operation_context: Context of the failed operation
            correlation_id: Request correlation ID

        Returns:
            Error category with handling recommendations

        Raises:
            ErrorHandlingError: If error categorization fails
        """
        ...

    async def should_retry_operation(
        self,
        error_category: "ProtocolErrorCategory",
        retry_policy: "ProtocolRetryPolicy",
        current_attempt: int,
        operation_context: "ProtocolOperationContext",
        correlation_id: Optional[UUID] = None,
    ) -> "ProtocolMemoryMetadata":
        """
        Determine if operation should be retried.

        Args:
            error_category: Categorized error information
            retry_policy: Retry policy configuration
            current_attempt: Current retry attempt number
            operation_context: Context of the failed operation
            correlation_id: Request correlation ID

        Returns:
            Retry decision with delay information

        Raises:
            RetryPolicyError: If retry policy evaluation fails
        """
        ...

    async def execute_retry(
        self,
        operation_context: "ProtocolOperationContext",
        retry_policy: "ProtocolRetryPolicy",
        retry_attempt: int,
        correlation_id: Optional[UUID] = None,
        timeout_seconds: Optional[float] = None,
    ) -> "ProtocolMemoryMetadata":
        """
        Execute retry of failed operation.

        Args:
            operation_context: Context of the operation to retry
            retry_policy: Retry policy configuration
            retry_attempt: Current retry attempt number
            correlation_id: Request correlation ID
            timeout_seconds: Optional timeout for retry operation

        Returns:
            Retry execution result

        Raises:
            RetryExecutionError: If retry execution fails
            TimeoutError: If retry exceeds timeout
        """
        ...

    async def execute_compensation_actions(
        self,
        operation_context: "ProtocolOperationContext",
        compensation_actions: list["ProtocolCompensationAction"],
        correlation_id: Optional[UUID] = None,
        timeout_seconds: Optional[float] = None,
    ) -> "ProtocolMemoryMetadata":
        """
        Execute compensation actions for failed operation.

        Args:
            operation_context: Context of the failed operation
            compensation_actions: List of compensation actions to execute
            correlation_id: Request correlation ID
            timeout_seconds: Optional timeout for compensation execution

        Returns:
            Compensation execution results

        Raises:
            CompensationError: If compensation execution fails
            TimeoutError: If compensation exceeds timeout
        """
        ...

    async def create_error_report(
        self,
        error: Exception,
        error_category: "ProtocolErrorCategory",
        operation_context: "ProtocolOperationContext",
        recovery_actions: list[str],
        correlation_id: Optional[UUID] = None,
    ) -> "ProtocolMemoryMetadata":
        """
        Create comprehensive error report for analysis.

        Args:
            error: Original exception that occurred
            error_category: Categorized error information
            operation_context: Context of the failed operation
            recovery_actions: List of recovery actions taken
            correlation_id: Request correlation ID

        Returns:
            Generated error report with analysis

        Raises:
            ReportGenerationError: If error report creation fails
        """
        ...

    async def handle_circuit_breaker(
        self,
        operation_type: str,
        error_rate: float,
        failure_threshold: int,
        time_window_seconds: int,
        correlation_id: Optional[UUID] = None,
    ) -> "ProtocolMemoryMetadata":
        """
        Handle circuit breaker logic for operation protection.

        Args:
            operation_type: Type of operation for circuit breaker
            error_rate: Current error rate for operation type
            failure_threshold: Threshold for opening circuit
            time_window_seconds: Time window for error rate calculation
            correlation_id: Request correlation ID

        Returns:
            Circuit breaker status and recommendations

        Raises:
            CircuitBreakerError: If circuit breaker handling fails
        """
        ...

    async def recover_from_partial_failure(
        self,
        operation_context: "ProtocolOperationContext",
        successful_operations: list[UUID],
        failed_operations: list[UUID],
        recovery_strategy: str,
        correlation_id: Optional[UUID] = None,
        timeout_seconds: Optional[float] = None,
    ) -> "ProtocolMemoryMetadata":
        """
        Recover from partial failure in batch or complex operations.

        Args:
            operation_context: Context of the partially failed operation
            successful_operations: Operations that completed successfully
            failed_operations: Operations that failed
            recovery_strategy: Strategy for partial failure recovery
            correlation_id: Request correlation ID
            timeout_seconds: Optional timeout for recovery operation

        Returns:
            Partial failure recovery results

        Raises:
            PartialRecoveryError: If partial recovery fails
            TimeoutError: If recovery exceeds timeout
        """
        ...


@runtime_checkable
class ProtocolMemoryHealthMonitor(Protocol):
    """
    Health monitoring and early warning system for memory operations.

    Monitors system health, detects degradation patterns, and provides
    early warnings to prevent cascading failures.
    """

    async def monitor_operation_health(
        self,
        operation_types: list[str],
        monitoring_window_minutes: int,
        correlation_id: Optional[UUID] = None,
    ) -> "ProtocolMemoryMetadata":
        """
        Monitor health of memory operations.

        Args:
            operation_types: Types of operations to monitor
            monitoring_window_minutes: Time window for health monitoring
            correlation_id: Request correlation ID

        Returns:
            Health monitoring results with metrics

        Raises:
            MonitoringError: If health monitoring fails
        """
        ...

    async def detect_degradation_patterns(
        self,
        metric_types: list[str],
        baseline_period_hours: int,
        detection_sensitivity: float,
        correlation_id: Optional[UUID] = None,
        timeout_seconds: Optional[float] = None,
    ) -> "ProtocolMemoryMetadata":
        """
        Detect performance degradation patterns.

        Args:
            metric_types: Types of metrics to analyze for degradation
            baseline_period_hours: Period for baseline comparison
            detection_sensitivity: Sensitivity for degradation detection
            correlation_id: Request correlation ID
            timeout_seconds: Optional timeout for detection operation

        Returns:
            Degradation detection results

        Raises:
            DegradationDetectionError: If pattern detection fails
            TimeoutError: If detection exceeds timeout
        """
        ...

    async def generate_early_warning(
        self,
        warning_type: str,
        severity_level: str,
        affected_operations: list[str],
        warning_metadata: "ProtocolMemoryMetadata",
        correlation_id: Optional[UUID] = None,
    ) -> "ProtocolMemoryMetadata":
        """
        Generate early warning for potential issues.

        Args:
            warning_type: Type of warning (performance, capacity, security)
            severity_level: Severity of the warning
            affected_operations: Operations affected by the warning
            warning_metadata: Additional warning metadata
            correlation_id: Request correlation ID

        Returns:
            Early warning generation result

        Raises:
            WarningGenerationError: If warning generation fails
        """
        ...

    async def create_health_dashboard(
        self,
        dashboard_scope: str,
        time_window_hours: int,
        correlation_id: Optional[UUID] = None,
        timeout_seconds: Optional[float] = None,
    ) -> "ProtocolMemoryMetadata":
        """
        Create health dashboard with key metrics.

        Args:
            dashboard_scope: Scope for dashboard (system, user, operation)
            time_window_hours: Time window for dashboard data
            correlation_id: Request correlation ID
            timeout_seconds: Optional timeout for dashboard creation

        Returns:
            Health dashboard data and visualizations

        Raises:
            DashboardError: If dashboard creation fails
            TimeoutError: If creation exceeds timeout
        """
        ...
