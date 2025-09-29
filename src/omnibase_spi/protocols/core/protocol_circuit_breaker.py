"""
Protocol definition for circuit breaker fault tolerance patterns.

This protocol defines the interface for circuit breaker implementations
following ONEX standards for external dependency resilience.
"""

from typing import Awaitable, Callable, Literal, Protocol, TypeVar, runtime_checkable

T = TypeVar("T")
LiteralProtocolCircuitBreakerState = Literal["closed", "open", "half_open"]
LiteralProtocolCircuitBreakerEvent = Literal[
    "success", "failure", "timeout", "state_change", "fallback_executed"
]


@runtime_checkable
class ProtocolCircuitBreakerConfig(Protocol):
    """Configuration protocol for circuit breaker settings."""

    @property
    def failure_threshold(self) -> int: ...

    @property
    def recovery_timeout_seconds(self) -> float: ...

    async def half_open_max_calls(self) -> int: ...

    @property
    def success_threshold(self) -> int: ...

    @property
    def metrics_window_seconds(self) -> float: ...

    @property
    def request_timeout_seconds(self) -> float: ...


@runtime_checkable
class ProtocolCircuitBreakerMetrics(Protocol):
    """Real-time circuit breaker metrics."""

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
    Protocol for circuit breaker factory implementations.

    Factories manage circuit breaker instances and provide
    consistent configuration across services.
    """

    async def get_circuit_breaker(
        self,
        service_name: str,
        config: "ProtocolCircuitBreakerConfig | None" = None,
        *,
        create_if_missing: bool = True,
    ) -> ProtocolCircuitBreaker | None: ...

    async def register_circuit_breaker(
        self, service_name: str, circuit_breaker: "ProtocolCircuitBreaker"
    ) -> None: ...

    def remove_circuit_breaker(self, service_name: str) -> bool: ...

    async def get_all_circuit_breakers(self) -> dict[str, "ProtocolCircuitBreaker"]: ...
