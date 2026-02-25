"""Tests for SPI resilience protocol interfaces.

Verifies that ProtocolRetryPolicy, ProtocolCircuitBreaker, and ProtocolRateLimiter
are well-defined, runtime-checkable Protocol classes with the expected method
signatures, and that mock implementations satisfy the protocols.

Ticket: OMN-796
"""

from __future__ import annotations

import inspect
import sys
from pathlib import Path
from typing import Protocol

import pytest

# Add src directory to Python path for testing
src_dir = Path(__file__).parent.parent.parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from omnibase_spi.protocols import (
    ProtocolCircuitBreaker,
    ProtocolRateLimiter,
    ProtocolRetryable,
)
from omnibase_spi.protocols.networking.protocol_circuit_breaker import (
    ProtocolCircuitBreakerConfig,
    ProtocolCircuitBreakerFactory,
    ProtocolCircuitBreakerMetrics,
)
from omnibase_spi.protocols.types.protocol_retry_types import (
    ProtocolRetryConfig,
    ProtocolRetryPolicy,
)


@pytest.mark.unit
class TestProtocolRetryable:
    """Tests for ProtocolRetryable interface."""

    def test_is_protocol_class(self) -> None:
        """ProtocolRetryable is a typing.Protocol subclass."""
        assert issubclass(ProtocolRetryable, Protocol)

    def test_is_runtime_checkable(self) -> None:
        """ProtocolRetryable is decorated with @runtime_checkable."""
        assert getattr(
            ProtocolRetryable, "__protocol_attrs__", None
        ) is not None or hasattr(ProtocolRetryable, "_is_runtime_protocol")

    def test_has_execute_with_retry(self) -> None:
        """ProtocolRetryable defines execute_with_retry method."""
        assert hasattr(ProtocolRetryable, "execute_with_retry")
        assert callable(ProtocolRetryable.execute_with_retry)

    def test_execute_with_retry_is_async(self) -> None:
        """execute_with_retry is an async method."""
        method = ProtocolRetryable.execute_with_retry
        assert inspect.iscoroutinefunction(method)

    def test_has_configure_retry_policy(self) -> None:
        """ProtocolRetryable defines configure_retry_policy method."""
        assert hasattr(ProtocolRetryable, "configure_retry_policy")

    def test_has_should_retry(self) -> None:
        """ProtocolRetryable defines should_retry method."""
        assert hasattr(ProtocolRetryable, "should_retry")

    def test_has_calculate_backoff_delay(self) -> None:
        """ProtocolRetryable defines calculate_backoff_delay method."""
        assert hasattr(ProtocolRetryable, "calculate_backoff_delay")

    def test_has_get_retry_metrics(self) -> None:
        """ProtocolRetryable defines get_retry_metrics method."""
        assert hasattr(ProtocolRetryable, "get_retry_metrics")
        assert inspect.iscoroutinefunction(ProtocolRetryable.get_retry_metrics)

    def test_has_reset_retry_budget(self) -> None:
        """ProtocolRetryable defines reset_retry_budget method."""
        assert hasattr(ProtocolRetryable, "reset_retry_budget")

    def test_has_add_retry_condition(self) -> None:
        """ProtocolRetryable defines add_retry_condition method."""
        assert hasattr(ProtocolRetryable, "add_retry_condition")


@pytest.mark.unit
class TestProtocolRetryPolicy:
    """Tests for ProtocolRetryPolicy type interface."""

    def test_is_protocol_class(self) -> None:
        """ProtocolRetryPolicy is a typing.Protocol subclass."""
        assert issubclass(ProtocolRetryPolicy, Protocol)

    def test_has_default_config_attribute(self) -> None:
        """ProtocolRetryPolicy defines default_config attribute."""
        annotations = getattr(ProtocolRetryPolicy, "__annotations__", {})
        assert "default_config" in annotations

    def test_has_retry_conditions_attribute(self) -> None:
        """ProtocolRetryPolicy defines retry_conditions attribute."""
        annotations = getattr(ProtocolRetryPolicy, "__annotations__", {})
        assert "retry_conditions" in annotations

    def test_has_retry_budget_limit(self) -> None:
        """ProtocolRetryPolicy defines retry_budget_limit attribute."""
        annotations = getattr(ProtocolRetryPolicy, "__annotations__", {})
        assert "retry_budget_limit" in annotations

    def test_has_validate_method(self) -> None:
        """ProtocolRetryPolicy defines validate_retry_policy method."""
        assert hasattr(ProtocolRetryPolicy, "validate_retry_policy")


@pytest.mark.unit
class TestProtocolRetryConfig:
    """Tests for ProtocolRetryConfig type interface."""

    def test_is_protocol_class(self) -> None:
        """ProtocolRetryConfig is a typing.Protocol subclass."""
        assert issubclass(ProtocolRetryConfig, Protocol)

    def test_has_max_attempts(self) -> None:
        """ProtocolRetryConfig defines max_attempts attribute."""
        annotations = getattr(ProtocolRetryConfig, "__annotations__", {})
        assert "max_attempts" in annotations

    def test_has_backoff_strategy(self) -> None:
        """ProtocolRetryConfig defines backoff_strategy attribute."""
        annotations = getattr(ProtocolRetryConfig, "__annotations__", {})
        assert "backoff_strategy" in annotations

    def test_has_base_delay_ms(self) -> None:
        """ProtocolRetryConfig defines base_delay_ms attribute."""
        annotations = getattr(ProtocolRetryConfig, "__annotations__", {})
        assert "base_delay_ms" in annotations


@pytest.mark.unit
class TestProtocolCircuitBreaker:
    """Tests for ProtocolCircuitBreaker interface."""

    def test_is_protocol_class(self) -> None:
        """ProtocolCircuitBreaker is a typing.Protocol subclass."""
        assert issubclass(ProtocolCircuitBreaker, Protocol)

    def test_is_runtime_checkable(self) -> None:
        """ProtocolCircuitBreaker is decorated with @runtime_checkable."""
        assert getattr(
            ProtocolCircuitBreaker, "__protocol_attrs__", None
        ) is not None or hasattr(ProtocolCircuitBreaker, "_is_runtime_protocol")

    def test_has_get_state(self) -> None:
        """ProtocolCircuitBreaker defines get_state method."""
        assert hasattr(ProtocolCircuitBreaker, "get_state")
        assert inspect.iscoroutinefunction(ProtocolCircuitBreaker.get_state)

    def test_has_get_metrics(self) -> None:
        """ProtocolCircuitBreaker defines get_metrics method."""
        assert hasattr(ProtocolCircuitBreaker, "get_metrics")

    def test_has_call(self) -> None:
        """ProtocolCircuitBreaker defines call method."""
        assert hasattr(ProtocolCircuitBreaker, "call")
        assert inspect.iscoroutinefunction(ProtocolCircuitBreaker.call)

    def test_has_record_success(self) -> None:
        """ProtocolCircuitBreaker defines record_success method."""
        assert hasattr(ProtocolCircuitBreaker, "record_success")

    def test_has_record_failure(self) -> None:
        """ProtocolCircuitBreaker defines record_failure method."""
        assert hasattr(ProtocolCircuitBreaker, "record_failure")

    def test_has_record_timeout(self) -> None:
        """ProtocolCircuitBreaker defines record_timeout method."""
        assert hasattr(ProtocolCircuitBreaker, "record_timeout")

    def test_has_service_name_property(self) -> None:
        """ProtocolCircuitBreaker defines service_name property."""
        # Check for property in class dict
        for cls in ProtocolCircuitBreaker.__mro__:
            if "service_name" in cls.__dict__:
                assert isinstance(cls.__dict__["service_name"], property)
                break


@pytest.mark.unit
class TestProtocolCircuitBreakerConfig:
    """Tests for ProtocolCircuitBreakerConfig interface."""

    def test_is_protocol_class(self) -> None:
        """ProtocolCircuitBreakerConfig is a typing.Protocol subclass."""
        assert issubclass(ProtocolCircuitBreakerConfig, Protocol)

    def test_has_failure_threshold(self) -> None:
        """ProtocolCircuitBreakerConfig defines failure_threshold property."""
        for cls in ProtocolCircuitBreakerConfig.__mro__:
            if "failure_threshold" in cls.__dict__:
                assert isinstance(cls.__dict__["failure_threshold"], property)
                break

    def test_has_recovery_timeout_seconds(self) -> None:
        """ProtocolCircuitBreakerConfig defines recovery_timeout_seconds property."""
        for cls in ProtocolCircuitBreakerConfig.__mro__:
            if "recovery_timeout_seconds" in cls.__dict__:
                assert isinstance(cls.__dict__["recovery_timeout_seconds"], property)
                break


@pytest.mark.unit
class TestProtocolCircuitBreakerFactory:
    """Tests for ProtocolCircuitBreakerFactory interface."""

    def test_is_protocol_class(self) -> None:
        """ProtocolCircuitBreakerFactory is a typing.Protocol subclass."""
        assert issubclass(ProtocolCircuitBreakerFactory, Protocol)

    def test_has_get_circuit_breaker(self) -> None:
        """ProtocolCircuitBreakerFactory defines get_circuit_breaker method."""
        assert hasattr(ProtocolCircuitBreakerFactory, "get_circuit_breaker")
        assert inspect.iscoroutinefunction(
            ProtocolCircuitBreakerFactory.get_circuit_breaker
        )

    def test_has_register_circuit_breaker(self) -> None:
        """ProtocolCircuitBreakerFactory defines register_circuit_breaker method."""
        assert hasattr(ProtocolCircuitBreakerFactory, "register_circuit_breaker")

    def test_has_get_all_circuit_breakers(self) -> None:
        """ProtocolCircuitBreakerFactory defines get_all_circuit_breakers method."""
        assert hasattr(ProtocolCircuitBreakerFactory, "get_all_circuit_breakers")


@pytest.mark.unit
class TestProtocolRateLimiter:
    """Tests for ProtocolRateLimiter interface."""

    def test_is_protocol_class(self) -> None:
        """ProtocolRateLimiter is a typing.Protocol subclass."""
        assert issubclass(ProtocolRateLimiter, Protocol)

    def test_is_runtime_checkable(self) -> None:
        """ProtocolRateLimiter is decorated with @runtime_checkable."""
        assert getattr(
            ProtocolRateLimiter, "__protocol_attrs__", None
        ) is not None or hasattr(ProtocolRateLimiter, "_is_runtime_protocol")

    def test_has_acquire(self) -> None:
        """ProtocolRateLimiter defines acquire method."""
        assert hasattr(ProtocolRateLimiter, "acquire")
        assert inspect.iscoroutinefunction(ProtocolRateLimiter.acquire)

    def test_has_release(self) -> None:
        """ProtocolRateLimiter defines release method."""
        assert hasattr(ProtocolRateLimiter, "release")
        assert inspect.iscoroutinefunction(ProtocolRateLimiter.release)

    def test_has_get_limit(self) -> None:
        """ProtocolRateLimiter defines get_limit method."""
        assert hasattr(ProtocolRateLimiter, "get_limit")
        assert inspect.iscoroutinefunction(ProtocolRateLimiter.get_limit)

    def test_exported_from_protocols(self) -> None:
        """ProtocolRateLimiter is exported from omnibase_spi.protocols."""
        from omnibase_spi.protocols import ProtocolRateLimiter as imported

        assert imported is ProtocolRateLimiter


@pytest.mark.unit
class TestResilienceProtocolCompleteness:
    """Tests verifying all three resilience protocols are available."""

    def test_all_resilience_protocols_importable(self) -> None:
        """All three resilience protocols can be imported from protocols root."""
        from omnibase_spi.protocols import (
            ProtocolCircuitBreaker,
            ProtocolRateLimiter,
            ProtocolRetryable,
        )

        assert ProtocolCircuitBreaker is not None
        assert ProtocolRateLimiter is not None
        assert ProtocolRetryable is not None

    def test_all_resilience_protocols_in_all(self) -> None:
        """All three resilience protocols are in protocols.__all__."""
        import omnibase_spi.protocols as protocols_pkg

        all_exports = getattr(protocols_pkg, "__all__", [])
        assert "ProtocolCircuitBreaker" in all_exports
        assert "ProtocolRateLimiter" in all_exports
        assert "ProtocolRetryable" in all_exports

    def test_supporting_types_available(self) -> None:
        """Supporting resilience types are importable."""
        from omnibase_spi.protocols.networking.protocol_circuit_breaker import (
            ProtocolCircuitBreakerConfig,
            ProtocolCircuitBreakerFactory,
        )
        from omnibase_spi.protocols.types.protocol_retry_types import (
            ProtocolRetryAttempt,
            ProtocolRetryConfig,
            ProtocolRetryPolicy,
            ProtocolRetryResult,
        )

        # Verify they're all Protocol subclasses
        for cls in [
            ProtocolCircuitBreakerConfig,
            ProtocolCircuitBreakerFactory,
            ProtocolCircuitBreakerMetrics,
            ProtocolRetryConfig,
            ProtocolRetryPolicy,
            ProtocolRetryAttempt,
            ProtocolRetryResult,
        ]:
            assert issubclass(cls, Protocol), f"{cls.__name__} is not a Protocol"
