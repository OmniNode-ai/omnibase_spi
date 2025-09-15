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

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Awaitable, Callable, Protocol, TypeVar, runtime_checkable

T = TypeVar("T")


class ProtocolCircuitBreakerState(str, Enum):
    """Circuit breaker states with clear semantics."""

    CLOSED = "closed"  # Normal operation, requests pass through
    OPEN = "open"  # Service is failing, requests fail fast
    HALF_OPEN = "half_open"  # Testing recovery, limited requests allowed


class ProtocolCircuitBreakerEvent(str, Enum):
    """Events that can occur in circuit breaker lifecycle."""

    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    STATE_CHANGE = "state_change"
    FALLBACK_EXECUTED = "fallback_executed"


@dataclass
class ProtocolCircuitBreakerMetrics:
    """Real-time circuit breaker metrics."""

    # Request counts
    total_requests: int
    successful_requests: int
    failed_requests: int
    timeout_requests: int

    # State tracking
    current_state: ProtocolCircuitBreakerState
    state_changes: int
    last_state_change: datetime | None

    # Timing metrics
    last_success_time: datetime | None
    last_failure_time: datetime | None
    average_response_time_ms: float

    # Window-based metrics (rolling)
    requests_in_window: int
    failures_in_window: int
    successes_in_window: int

    # Half-open state tracking
    half_open_requests: int
    half_open_successes: int
    half_open_failures: int


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
                if self.get_state() == ProtocolCircuitBreakerState.OPEN:
                    if fallback:
                        return await fallback()
                    raise CircuitBreakerOpenException()

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
            CircuitBreakerOpenException: If circuit is open and no fallback
            CircuitBreakerTimeoutException: If request times out
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

    async def force_open(self) -> None:
        """Force circuit breaker to OPEN state for testing or emergency."""
        ...

    async def force_close(self) -> None:
        """Force circuit breaker to CLOSED state for testing or recovery."""
        ...

    async def force_half_open(self) -> None:
        """Force circuit breaker to HALF_OPEN state for testing."""
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
        config: Any = None,
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


# Exception types that should be available for protocol implementations
class CircuitBreakerException(Exception):
    """Base exception for circuit breaker errors."""

    def __init__(
        self,
        service_name: str,
        state: ProtocolCircuitBreakerState,
        metrics: ProtocolCircuitBreakerMetrics | None = None,
    ):
        self.service_name = service_name
        self.state = state
        self.metrics = metrics
        super().__init__(
            f"Circuit breaker is {state.value} for service '{service_name}'"
        )


class CircuitBreakerOpenException(CircuitBreakerException):
    """Exception for when circuit breaker is in OPEN state."""


class CircuitBreakerTimeoutException(CircuitBreakerException):
    """Exception for when request times out."""
