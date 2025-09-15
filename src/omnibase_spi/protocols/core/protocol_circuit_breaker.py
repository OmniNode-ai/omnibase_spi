# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-01-15T18:30:00.000000'
# description: Protocol definition for circuit breaker fault tolerance patterns
# entrypoint: python://protocol_circuit_breaker
# hash: auto-generated
# last_modified_at: '2025-01-15T18:30:00.000000+00:00'
# lifecycle: active
# meta_type: node
# metadata_version: 0.1.0
# name: protocol_circuit_breaker.py
# namespace: python://omnibase_spi.protocols.core.protocol_circuit_breaker
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: auto-generated
# version: 1.0.0
# === /OmniNode:Metadata ===

"""
Protocol definition for circuit breaker fault tolerance patterns.

This protocol defines the interface for circuit breaker implementations
following ONEX standards for external dependency resilience.
"""

from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Literal,
    Protocol,
    TypeVar,
    runtime_checkable,
)

# Remove datetime import - use float timestamps for SPI purity

T = TypeVar("T")

# Circuit breaker states with clear semantics
ProtocolCircuitBreakerState = Literal[
    "closed",  # Normal operation, requests pass through
    "open",  # Service is failing, requests fail fast
    "half_open",  # Testing recovery, limited requests allowed
]

# Events that can occur in circuit breaker lifecycle
ProtocolCircuitBreakerEvent = Literal[
    "success", "failure", "timeout", "state_change", "fallback_executed"
]


@runtime_checkable
class ProtocolCircuitBreakerConfig(Protocol):
    """Configuration protocol for circuit breaker settings."""

    @property
    def failure_threshold(self) -> int:
        """Number of failures that trigger OPEN state."""
        ...

    @property
    def recovery_timeout_seconds(self) -> float:
        """Timeout before transitioning from OPEN to HALF_OPEN."""
        ...

    @property
    def half_open_max_calls(self) -> int:
        """Maximum calls allowed in HALF_OPEN state for testing."""
        ...

    @property
    def success_threshold(self) -> int:
        """Required successful calls in HALF_OPEN to close circuit."""
        ...

    @property
    def metrics_window_seconds(self) -> float:
        """Time window for metrics calculation."""
        ...

    @property
    def request_timeout_seconds(self) -> float:
        """Default timeout for requests."""
        ...


@runtime_checkable
class ProtocolCircuitBreakerMetrics(Protocol):
    """Real-time circuit breaker metrics."""

    # Request counts
    @property
    def total_requests(self) -> int:
        """Total number of requests processed."""
        ...

    @property
    def successful_requests(self) -> int:
        """Number of successful requests."""
        ...

    @property
    def failed_requests(self) -> int:
        """Number of failed requests."""
        ...

    @property
    def timeout_requests(self) -> int:
        """Number of timed out requests."""
        ...

    # State tracking
    @property
    def current_state(self) -> ProtocolCircuitBreakerState:
        """Current circuit breaker state."""
        ...

    @property
    def state_changes(self) -> int:
        """Number of state changes."""
        ...

    @property
    def last_state_change(self) -> float | None:
        """Unix timestamp of last state change."""
        ...

    # Timing metrics
    @property
    def last_success_time(self) -> float | None:
        """Unix timestamp of last successful request."""
        ...

    @property
    def last_failure_time(self) -> float | None:
        """Unix timestamp of last failed request."""
        ...

    @property
    def average_response_time_ms(self) -> float:
        """Average response time in milliseconds."""
        ...

    # Window-based metrics (rolling)
    @property
    def requests_in_window(self) -> int:
        """Number of requests in current window."""
        ...

    @property
    def failures_in_window(self) -> int:
        """Number of failures in current window."""
        ...

    @property
    def successes_in_window(self) -> int:
        """Number of successes in current window."""
        ...

    # Half-open state tracking
    @property
    def half_open_requests(self) -> int:
        """Number of requests in half-open state."""
        ...

    @property
    def half_open_successes(self) -> int:
        """Number of successes in half-open state."""
        ...

    @property
    def half_open_failures(self) -> int:
        """Number of failures in half-open state."""
        ...

    def get_failure_rate(self) -> float:
        """Calculate current failure rate."""
        ...

    def get_success_rate(self) -> float:
        """Calculate current success rate."""
        ...

    def reset_window(self) -> None:
        """Reset window-based metrics."""
        ...


@runtime_checkable
class ProtocolCircuitBreaker(Protocol):
    """
    Protocol for circuit breaker fault tolerance implementations.

    Circuit breakers prevent cascading failures by monitoring external
    service calls and temporarily stopping requests when failure thresholds
    are exceeded.

    Example:
        class MyCircuitBreaker:
            def get_state(self) -> ProtocolCircuitBreakerState:
                return self._current_state

            async def call(self, func, fallback=None, timeout=None):
                if self.get_state() == "open":
                    if fallback:
                        return await fallback()
                    raise Exception("Circuit breaker is open")

                try:
                    result = await func()
                    await self.record_success()
                    return result
                except Exception as e:
                    await self.record_failure(e)
                    raise
    """

    @property
    def service_name(self) -> str:
        """Get the service name this circuit breaker protects."""
        ...

    def get_state(self) -> ProtocolCircuitBreakerState:
        """
        Get current circuit breaker state.

        Returns:
            ProtocolCircuitBreakerState: Current state (CLOSED, OPEN, HALF_OPEN)
        """
        ...

    def get_metrics(self) -> ProtocolCircuitBreakerMetrics:
        """
        Get current metrics snapshot.

        Returns:
            ProtocolCircuitBreakerMetrics: Current performance and state metrics
        """
        ...

    async def call(
        self,
        func: Callable[[], Awaitable[T]],
        fallback: Callable[[], Awaitable[T]] | None = None,
        timeout: float | None = None,
    ) -> T:
        """
        Execute function through circuit breaker with optional fallback.

        Args:
            func: Async function to execute
            fallback: Optional fallback function if circuit is open
            timeout: Override default timeout for this call

        Returns:
            Result of function execution or fallback

        Raises:
            Exception: If circuit is open and no fallback provided
            TimeoutError: If request times out
            Any exception raised by func or fallback
        """
        ...

    async def record_success(self, execution_time_ms: float | None = None) -> None:
        """
        Record a successful operation.

        Args:
            execution_time_ms: Optional execution time for metrics
        """
        ...

    async def record_failure(self, exception: Exception | None = None) -> None:
        """
        Record a failed operation.

        Args:
            exception: Optional exception that caused the failure
        """
        ...

    async def record_timeout(self) -> None:
        """Record a timeout operation."""
        ...


@runtime_checkable
class ProtocolCircuitBreakerFactory(Protocol):
    """
    Protocol for circuit breaker factory implementations.

    Factories manage circuit breaker instances and provide
    consistent configuration across services.
    """

    def get_circuit_breaker(
        self,
        service_name: str,
        config: ProtocolCircuitBreakerConfig | None = None,
        *,
        create_if_missing: bool = True,
    ) -> ProtocolCircuitBreaker | None:
        """
        Get or create a circuit breaker for a service.

        Args:
            service_name: Name of the service to protect
            config: Optional configuration for the circuit breaker
            create_if_missing: Whether to create if doesn't exist

        Returns:
            Circuit breaker instance or None if not found and not creating
        """
        ...

    def register_circuit_breaker(
        self,
        service_name: str,
        circuit_breaker: ProtocolCircuitBreaker,
    ) -> None:
        """
        Register an existing circuit breaker instance.

        Args:
            service_name: Name of the service
            circuit_breaker: Circuit breaker instance to register
        """
        ...

    def remove_circuit_breaker(self, service_name: str) -> bool:
        """
        Remove a circuit breaker from the factory.

        Args:
            service_name: Name of the service

        Returns:
            True if removed, False if not found
        """
        ...

    def get_all_circuit_breakers(self) -> dict[str, ProtocolCircuitBreaker]:
        """
        Get all registered circuit breakers.

        Returns:
            Dictionary mapping service names to circuit breakers
        """
        ...
