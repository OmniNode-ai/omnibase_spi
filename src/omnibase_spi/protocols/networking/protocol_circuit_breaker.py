"""
Protocol definition for circuit breaker fault tolerance patterns.

This protocol defines the interface for circuit breaker implementations
following ONEX standards for external dependency resilience.
"""

from collections.abc import Awaitable, Callable
from typing import Literal, Protocol, TypeVar, runtime_checkable

T = TypeVar("T")
LiteralProtocolCircuitBreakerState = Literal["closed", "open", "half_open"]
LiteralProtocolCircuitBreakerEvent = Literal[
    "success", "failure", "timeout", "state_change", "fallback_executed"
]


@runtime_checkable
class ProtocolCircuitBreakerConfig(Protocol):
    """
    Configuration protocol for circuit breaker settings.

    Defines the configurable parameters for circuit breaker behavior,
    including failure thresholds, recovery timeouts, and metrics windows.

    Example:
        ```python
        # Implementation example (not part of SPI)
        # All properties defined in the protocol contract must be implemented

        # Usage in application
        config: "ProtocolCircuitBreakerConfig" = get_circuit_breaker_config()

        # Access configuration values
        failure_threshold = config.failure_threshold  # e.g., 5 failures
        recovery_timeout = config.recovery_timeout_seconds  # e.g., 60.0 seconds
        half_open_calls = await config.half_open_max_calls()  # e.g., 3 calls
        success_threshold = config.success_threshold  # e.g., 3 successes
        metrics_window = config.metrics_window_seconds  # e.g., 300.0 seconds
        request_timeout = config.request_timeout_seconds  # e.g., 30.0 seconds

        # Configure circuit breaker
        circuit_breaker = create_circuit_breaker(
            service_name="external-api",
            config=config
        )
        ```

    Configuration Parameters:
        - failure_threshold: Number of failures before opening circuit
        - recovery_timeout_seconds: Time to wait before attempting recovery
        - half_open_max_calls: Maximum calls in half-open state
        - success_threshold: Successes needed to close circuit
        - metrics_window_seconds: Time window for metrics collection
        - request_timeout_seconds: Default timeout for requests
    """

    @property
    def failure_threshold(self) -> int: ...
    @property
    def recovery_timeout_seconds(self) -> float:
        """Time in seconds to wait before attempting recovery."""
        ...

    async def half_open_max_calls(self) -> int:
        """Maximum number of calls allowed in half-open state."""
        ...

    @property
    def success_threshold(self) -> int:
        """Number of successes needed to close circuit."""
        ...

    @property
    def metrics_window_seconds(self) -> float:
        """Time window in seconds for metrics collection."""
        ...

    @property
    def request_timeout_seconds(self) -> float:
        """Default timeout in seconds for requests."""
        ...


@runtime_checkable
class ProtocolCircuitBreakerMetrics(Protocol):
    """
    Protocol for real-time circuit breaker metrics and statistics.

    Provides comprehensive metrics about circuit breaker operation
    including request counts, success/failure rates, timing data,
    and state change history for monitoring and alerting.

    Example:
        ```python
        breaker: ProtocolCircuitBreaker = get_circuit_breaker()
        metrics = await breaker.get_metrics()

        print(f"Total requests: {metrics.total_requests}")
        print(f"Successes: {metrics.successful_requests}")
        print(f"Failures: {metrics.failed_requests}")
        print(f"Current state: {metrics.current_state}")

        failure_rate = await metrics.get_failure_rate()
        print(f"Failure rate: {failure_rate:.2%}")
        ```

    See Also:
        - ProtocolCircuitBreaker: Main circuit breaker interface
        - ProtocolCircuitBreakerConfig: Configuration parameters
    """

    @property
    def total_requests(self) -> int: ...

    @property
    def successful_requests(self) -> int: ...

    @property
    def failed_requests(self) -> int: ...

    @property
    def timeout_requests(self) -> int: ...

    @property
    def current_state(self) -> "LiteralProtocolCircuitBreakerState": ...

    @property
    def state_changes(self) -> int: ...

    @property
    def last_state_change(self) -> float | None: ...

    @property
    def last_success_time(self) -> float | None: ...

    @property
    def last_failure_time(self) -> float | None: ...

    @property
    def average_response_time_ms(self) -> float: ...

    @property
    def requests_in_window(self) -> int: ...

    @property
    def failures_in_window(self) -> int: ...

    @property
    def successes_in_window(self) -> int: ...

    async def half_open_requests(self) -> int: ...

    async def half_open_successes(self) -> int: ...

    async def half_open_failures(self) -> int: ...

    async def get_failure_rate(self) -> float: ...

    async def get_success_rate(self) -> float: ...

    async def reset_window(self) -> None: ...


@runtime_checkable
class ProtocolCircuitBreaker(Protocol):
    """
    Protocol for circuit breaker fault tolerance implementations.

    Circuit breakers prevent cascading failures by monitoring external
    service calls and temporarily stopping requests when failure thresholds
    are exceeded.

    Example:
        class MyCircuitBreaker:
            def get_state(self) -> "LiteralProtocolCircuitBreakerState":
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
    def service_name(self) -> str: ...

    async def get_state(self) -> "LiteralProtocolCircuitBreakerState": ...

    async def get_metrics(self) -> ProtocolCircuitBreakerMetrics: ...

    async def call(
        self,
        func: Callable[[], Awaitable[T]],
        fallback: Callable[[], Awaitable[T]] | None = None,
        timeout: float | None = None,
    ) -> T: ...

    async def record_success(self, execution_time_ms: float | None = None) -> None: ...

    async def record_failure(self, exception: Exception | None = None) -> None: ...

    async def record_timeout(self) -> None: ...


@runtime_checkable
class ProtocolCircuitBreakerFactory(Protocol):
    """
    Protocol for circuit breaker factory and instance management.

    Provides centralized creation, registration, and management of
    circuit breaker instances with consistent configuration across
    services and support for dynamic instance lookup.

    Example:
        ```python
        factory: ProtocolCircuitBreakerFactory = get_circuit_breaker_factory()

        # Get or create circuit breaker for a service
        breaker = await factory.get_circuit_breaker(
            service_name="external-api",
            create_if_missing=True
        )

        # Register a custom-configured breaker
        custom_breaker = create_custom_breaker()
        await factory.register_circuit_breaker("payment-service", custom_breaker)

        # List all circuit breakers
        all_breakers = await factory.get_all_circuit_breakers()
        for name, breaker in all_breakers.items():
            state = await breaker.get_state()
            print(f"{name}: {state}")
        ```

    See Also:
        - ProtocolCircuitBreaker: Individual breaker interface
        - ProtocolCircuitBreakerConfig: Configuration protocol
    """

    async def get_circuit_breaker(
        self,
        service_name: str,
        config: "ProtocolCircuitBreakerConfig | None" = None,
        *,
        create_if_missing: bool | None = None,
    ) -> ProtocolCircuitBreaker | None: ...

    async def register_circuit_breaker(
        self, service_name: str, circuit_breaker: "ProtocolCircuitBreaker"
    ) -> None: ...

    def remove_circuit_breaker(self, service_name: str) -> bool: ...

    async def get_all_circuit_breakers(self) -> dict[str, "ProtocolCircuitBreaker"]: ...
