"""
Tests for EventBus protocol inheritance relationships.

This module validates that protocol inheritance chains are correctly defined
and that isinstance checks work properly for parent and child protocols.

Inheritance Relationships Tested
--------------------------------
1. **ProtocolSyncEventBus** inherits from **ProtocolEventBusBase**:
   - Adds synchronous publish_sync() method
   - Inherits all base methods: publish, publish_envelope, subscribe, etc.

2. **ProtocolAsyncEventBus** inherits from **ProtocolEventBusBase**:
   - Adds asynchronous publish_async() method
   - Inherits all base methods: publish, publish_envelope, subscribe, etc.

3. Protocol Method Inclusion:
   - Child protocols include ALL parent methods
   - isinstance checks work for both parent and child protocols

Test Organization
-----------------
1. **Inheritance Structure Tests**: Verify Protocol MRO and inheritance chain
2. **Parent Method Tests**: Verify child protocols include parent methods
3. **isinstance Tests**: Verify isinstance behavior across inheritance
4. **Type Compatibility Tests**: Verify implementations work with parent types

Testing Approach
----------------
Mock implementations are used to test protocol compliance:

- **MockEventBusBase**: Implements only ProtocolEventBusBase
- **MockSyncEventBus**: Implements ProtocolSyncEventBus (base + sync)
- **MockAsyncEventBus**: Implements ProtocolAsyncEventBus (base + async)

Note on Type Ignores
--------------------
- ``# type: ignore[comparison-overlap]`` on Protocol MRO checks: mypy flags
  the comparison, but at runtime we verify Protocol is in the MRO.
"""

from collections.abc import Awaitable, Callable
from typing import Any, Protocol

import pytest

from omnibase_spi.protocols.event_bus.protocol_event_bus_mixin import (
    ProtocolAsyncEventBus,
    ProtocolEventBusBase,
    ProtocolSyncEventBus,
)
from omnibase_spi.protocols.types.protocol_event_bus_types import ProtocolEventMessage


# =============================================================================
# Mock Implementations for Testing Inheritance
# =============================================================================


class MockEventBusBase:
    """Test double implementing ONLY ProtocolEventBusBase requirements.

    Used to verify that base protocol implementation does NOT satisfy
    child protocol isinstance checks.

    Implements:
        - publish(event) -> None
        - publish_envelope(envelope, topic) -> None
        - subscribe(topic, handler) -> None
        - start_consuming(timeout_seconds) -> None
        - stop_consuming(timeout_seconds) -> None
        - health_check() -> dict[str, Any]
    """

    async def publish(self, event: ProtocolEventMessage) -> None:
        """Publish an event message."""
        pass

    async def publish_envelope(self, envelope: object, topic: str) -> None:
        """Publish an envelope to a topic."""
        pass

    async def subscribe(
        self,
        topic: str,
        handler: Callable[[object], Awaitable[None]],
    ) -> None:
        """Subscribe to a topic with a handler."""
        pass

    async def start_consuming(self, timeout_seconds: float | None = None) -> None:
        """Start consuming messages."""
        pass

    async def stop_consuming(self, timeout_seconds: float = 30.0) -> None:
        """Stop consuming messages."""
        pass

    async def health_check(self) -> dict[str, Any]:
        """Check health status."""
        return {"healthy": True}


class MockSyncEventBus(MockEventBusBase):
    """Test double implementing ProtocolSyncEventBus (base + sync method).

    Extends MockEventBusBase with the synchronous publish method required
    by ProtocolSyncEventBus.

    Additional method:
        - publish_sync(event) -> None
    """

    async def publish_sync(self, event: ProtocolEventMessage) -> None:
        """Publish an event synchronously with blocking semantics."""
        pass


class MockAsyncEventBus(MockEventBusBase):
    """Test double implementing ProtocolAsyncEventBus (base + async method).

    Extends MockEventBusBase with the asynchronous publish method required
    by ProtocolAsyncEventBus.

    Additional method:
        - publish_async(event) -> None
    """

    async def publish_async(self, event: ProtocolEventMessage) -> None:
        """Publish an event asynchronously with non-blocking semantics."""
        pass


class MockBothEventBus(MockEventBusBase):
    """Test double implementing both sync and async methods.

    Used to verify an implementation can satisfy both ProtocolSyncEventBus
    and ProtocolAsyncEventBus protocols simultaneously.
    """

    async def publish_sync(self, event: ProtocolEventMessage) -> None:
        """Publish an event synchronously."""
        pass

    async def publish_async(self, event: ProtocolEventMessage) -> None:
        """Publish an event asynchronously."""
        pass


# =============================================================================
# Pytest Fixtures
# =============================================================================


@pytest.fixture
def mock_base_bus() -> MockEventBusBase:
    """Provide a mock implementing only ProtocolEventBusBase."""
    return MockEventBusBase()


@pytest.fixture
def mock_sync_bus() -> MockSyncEventBus:
    """Provide a mock implementing ProtocolSyncEventBus."""
    return MockSyncEventBus()


@pytest.fixture
def mock_async_bus() -> MockAsyncEventBus:
    """Provide a mock implementing ProtocolAsyncEventBus."""
    return MockAsyncEventBus()


@pytest.fixture
def mock_both_bus() -> MockBothEventBus:
    """Provide a mock implementing both sync and async protocols."""
    return MockBothEventBus()


# =============================================================================
# Test Classes
# =============================================================================


class TestProtocolInheritanceStructure:
    """Test protocol inheritance chain structure.

    These tests verify that child protocols correctly inherit from
    ProtocolEventBusBase and that the MRO (Method Resolution Order)
    reflects the intended inheritance hierarchy.
    """

    def test_sync_event_bus_inherits_from_base(self) -> None:
        """ProtocolSyncEventBus should inherit from ProtocolEventBusBase."""
        # Check that ProtocolEventBusBase is in the MRO
        mro_names = [cls.__name__ for cls in ProtocolSyncEventBus.__mro__]
        assert "ProtocolEventBusBase" in mro_names

    def test_async_event_bus_inherits_from_base(self) -> None:
        """ProtocolAsyncEventBus should inherit from ProtocolEventBusBase."""
        # Check that ProtocolEventBusBase is in the MRO
        mro_names = [cls.__name__ for cls in ProtocolAsyncEventBus.__mro__]
        assert "ProtocolEventBusBase" in mro_names

    def test_sync_event_bus_is_protocol(self) -> None:
        """ProtocolSyncEventBus should be a Protocol class."""
        # Verify Protocol is in the inheritance chain
        assert any(
            base is Protocol or base.__name__ == "Protocol"  # type: ignore[comparison-overlap]
            for base in ProtocolSyncEventBus.__mro__
        )

    def test_async_event_bus_is_protocol(self) -> None:
        """ProtocolAsyncEventBus should be a Protocol class."""
        # Verify Protocol is in the inheritance chain
        assert any(
            base is Protocol or base.__name__ == "Protocol"  # type: ignore[comparison-overlap]
            for base in ProtocolAsyncEventBus.__mro__
        )

    def test_base_event_bus_is_protocol(self) -> None:
        """ProtocolEventBusBase should be a Protocol class."""
        # Verify Protocol is in the inheritance chain
        assert any(
            base is Protocol or base.__name__ == "Protocol"  # type: ignore[comparison-overlap]
            for base in ProtocolEventBusBase.__mro__
        )

    def test_all_protocols_are_runtime_checkable(self) -> None:
        """All EventBus protocols should be runtime_checkable."""
        protocols = [
            ProtocolEventBusBase,
            ProtocolSyncEventBus,
            ProtocolAsyncEventBus,
        ]
        for protocol in protocols:
            # Python 3.11+ uses _is_runtime_protocol
            # Older versions use __runtime_protocol__
            has_runtime_check = hasattr(protocol, "_is_runtime_protocol") or hasattr(
                protocol, "__runtime_protocol__"
            )
            assert has_runtime_check, f"{protocol.__name__} should be @runtime_checkable"


class TestParentMethodInheritance:
    """Test that child protocols include all parent methods.

    These tests verify that ProtocolSyncEventBus and ProtocolAsyncEventBus
    expose all methods from ProtocolEventBusBase in addition to their own.
    """

    def test_sync_event_bus_has_base_publish_method(self) -> None:
        """ProtocolSyncEventBus should have publish method from base."""
        assert "publish" in dir(ProtocolSyncEventBus)

    def test_sync_event_bus_has_base_publish_envelope_method(self) -> None:
        """ProtocolSyncEventBus should have publish_envelope method from base."""
        assert "publish_envelope" in dir(ProtocolSyncEventBus)

    def test_sync_event_bus_has_base_subscribe_method(self) -> None:
        """ProtocolSyncEventBus should have subscribe method from base."""
        assert "subscribe" in dir(ProtocolSyncEventBus)

    def test_sync_event_bus_has_base_start_consuming_method(self) -> None:
        """ProtocolSyncEventBus should have start_consuming method from base."""
        assert "start_consuming" in dir(ProtocolSyncEventBus)

    def test_sync_event_bus_has_base_stop_consuming_method(self) -> None:
        """ProtocolSyncEventBus should have stop_consuming method from base."""
        assert "stop_consuming" in dir(ProtocolSyncEventBus)

    def test_sync_event_bus_has_base_health_check_method(self) -> None:
        """ProtocolSyncEventBus should have health_check method from base."""
        assert "health_check" in dir(ProtocolSyncEventBus)

    def test_sync_event_bus_has_own_publish_sync_method(self) -> None:
        """ProtocolSyncEventBus should have its own publish_sync method."""
        assert "publish_sync" in dir(ProtocolSyncEventBus)

    def test_async_event_bus_has_base_publish_method(self) -> None:
        """ProtocolAsyncEventBus should have publish method from base."""
        assert "publish" in dir(ProtocolAsyncEventBus)

    def test_async_event_bus_has_base_publish_envelope_method(self) -> None:
        """ProtocolAsyncEventBus should have publish_envelope method from base."""
        assert "publish_envelope" in dir(ProtocolAsyncEventBus)

    def test_async_event_bus_has_base_subscribe_method(self) -> None:
        """ProtocolAsyncEventBus should have subscribe method from base."""
        assert "subscribe" in dir(ProtocolAsyncEventBus)

    def test_async_event_bus_has_base_start_consuming_method(self) -> None:
        """ProtocolAsyncEventBus should have start_consuming method from base."""
        assert "start_consuming" in dir(ProtocolAsyncEventBus)

    def test_async_event_bus_has_base_stop_consuming_method(self) -> None:
        """ProtocolAsyncEventBus should have stop_consuming method from base."""
        assert "stop_consuming" in dir(ProtocolAsyncEventBus)

    def test_async_event_bus_has_base_health_check_method(self) -> None:
        """ProtocolAsyncEventBus should have health_check method from base."""
        assert "health_check" in dir(ProtocolAsyncEventBus)

    def test_async_event_bus_has_own_publish_async_method(self) -> None:
        """ProtocolAsyncEventBus should have its own publish_async method."""
        assert "publish_async" in dir(ProtocolAsyncEventBus)


class TestIsinstanceInheritance:
    """Test isinstance behavior across protocol inheritance.

    These tests verify that:
    - Implementations of child protocols satisfy parent protocol isinstance
    - Implementations of base protocol do NOT satisfy child protocol isinstance
    - Child protocols are properly distinguished from each other
    """

    def test_base_impl_satisfies_base_protocol(
        self, mock_base_bus: MockEventBusBase
    ) -> None:
        """Base implementation should satisfy ProtocolEventBusBase."""
        assert isinstance(mock_base_bus, ProtocolEventBusBase)

    def test_base_impl_does_not_satisfy_sync_protocol(
        self, mock_base_bus: MockEventBusBase
    ) -> None:
        """Base implementation should NOT satisfy ProtocolSyncEventBus."""
        # Missing publish_sync method
        assert not isinstance(mock_base_bus, ProtocolSyncEventBus)

    def test_base_impl_does_not_satisfy_async_protocol(
        self, mock_base_bus: MockEventBusBase
    ) -> None:
        """Base implementation should NOT satisfy ProtocolAsyncEventBus."""
        # Missing publish_async method
        assert not isinstance(mock_base_bus, ProtocolAsyncEventBus)

    def test_sync_impl_satisfies_base_protocol(
        self, mock_sync_bus: MockSyncEventBus
    ) -> None:
        """Sync implementation should satisfy ProtocolEventBusBase (parent)."""
        assert isinstance(mock_sync_bus, ProtocolEventBusBase)

    def test_sync_impl_satisfies_sync_protocol(
        self, mock_sync_bus: MockSyncEventBus
    ) -> None:
        """Sync implementation should satisfy ProtocolSyncEventBus."""
        assert isinstance(mock_sync_bus, ProtocolSyncEventBus)

    def test_sync_impl_does_not_satisfy_async_protocol(
        self, mock_sync_bus: MockSyncEventBus
    ) -> None:
        """Sync implementation should NOT satisfy ProtocolAsyncEventBus."""
        # Missing publish_async method
        assert not isinstance(mock_sync_bus, ProtocolAsyncEventBus)

    def test_async_impl_satisfies_base_protocol(
        self, mock_async_bus: MockAsyncEventBus
    ) -> None:
        """Async implementation should satisfy ProtocolEventBusBase (parent)."""
        assert isinstance(mock_async_bus, ProtocolEventBusBase)

    def test_async_impl_satisfies_async_protocol(
        self, mock_async_bus: MockAsyncEventBus
    ) -> None:
        """Async implementation should satisfy ProtocolAsyncEventBus."""
        assert isinstance(mock_async_bus, ProtocolAsyncEventBus)

    def test_async_impl_does_not_satisfy_sync_protocol(
        self, mock_async_bus: MockAsyncEventBus
    ) -> None:
        """Async implementation should NOT satisfy ProtocolSyncEventBus."""
        # Missing publish_sync method
        assert not isinstance(mock_async_bus, ProtocolSyncEventBus)

    def test_both_impl_satisfies_all_protocols(
        self, mock_both_bus: MockBothEventBus
    ) -> None:
        """Implementation with both methods should satisfy all protocols."""
        assert isinstance(mock_both_bus, ProtocolEventBusBase)
        assert isinstance(mock_both_bus, ProtocolSyncEventBus)
        assert isinstance(mock_both_bus, ProtocolAsyncEventBus)


class TestTypeCompatibilityWithParent:
    """Test type compatibility between child implementations and parent types.

    These tests verify that child protocol implementations can be used where
    parent protocol types are expected, supporting Liskov Substitution Principle.
    """

    @pytest.mark.asyncio
    async def test_sync_impl_callable_with_base_type_hint(
        self, mock_sync_bus: MockSyncEventBus
    ) -> None:
        """Sync implementation can be used where base type is expected."""

        async def use_base_bus(bus: ProtocolEventBusBase) -> dict[str, Any]:
            """Function accepting ProtocolEventBusBase parameter."""
            return await bus.health_check()

        # This should work without type errors at runtime
        result = await use_base_bus(mock_sync_bus)
        assert result == {"healthy": True}

    @pytest.mark.asyncio
    async def test_async_impl_callable_with_base_type_hint(
        self, mock_async_bus: MockAsyncEventBus
    ) -> None:
        """Async implementation can be used where base type is expected."""

        async def use_base_bus(bus: ProtocolEventBusBase) -> dict[str, Any]:
            """Function accepting ProtocolEventBusBase parameter."""
            return await bus.health_check()

        # This should work without type errors at runtime
        result = await use_base_bus(mock_async_bus)
        assert result == {"healthy": True}

    @pytest.mark.asyncio
    async def test_both_impl_callable_with_any_type_hint(
        self, mock_both_bus: MockBothEventBus
    ) -> None:
        """Both implementation can be used with any protocol type."""

        async def use_base_bus(bus: ProtocolEventBusBase) -> dict[str, Any]:
            return await bus.health_check()

        async def use_sync_bus(bus: ProtocolSyncEventBus) -> None:
            # Create a minimal event for testing
            class MinimalEvent:
                topic: str = "test"
                payload: bytes = b"test"
                headers: dict[str, str] = {}

            await bus.publish_sync(MinimalEvent())  # type: ignore[arg-type]

        async def use_async_bus(bus: ProtocolAsyncEventBus) -> None:
            class MinimalEvent:
                topic: str = "test"
                payload: bytes = b"test"
                headers: dict[str, str] = {}

            await bus.publish_async(MinimalEvent())  # type: ignore[arg-type]

        # All should work
        result = await use_base_bus(mock_both_bus)
        assert result == {"healthy": True}
        await use_sync_bus(mock_both_bus)
        await use_async_bus(mock_both_bus)


class TestMethodSignatureInheritance:
    """Test that method signatures are consistent across inheritance.

    These tests verify that inherited methods have consistent signatures
    in both parent and child protocols.
    """

    def test_publish_signature_consistent(self) -> None:
        """publish method should have consistent signature in all protocols."""
        import inspect

        base_sig = inspect.signature(ProtocolEventBusBase.publish)
        sync_sig = inspect.signature(ProtocolSyncEventBus.publish)
        async_sig = inspect.signature(ProtocolAsyncEventBus.publish)

        # Parameter names should match
        base_params = list(base_sig.parameters.keys())
        sync_params = list(sync_sig.parameters.keys())
        async_params = list(async_sig.parameters.keys())

        assert base_params == sync_params == async_params

    def test_health_check_signature_consistent(self) -> None:
        """health_check method should have consistent signature in all protocols."""
        import inspect

        base_sig = inspect.signature(ProtocolEventBusBase.health_check)
        sync_sig = inspect.signature(ProtocolSyncEventBus.health_check)
        async_sig = inspect.signature(ProtocolAsyncEventBus.health_check)

        # Parameter names should match (just 'self')
        base_params = list(base_sig.parameters.keys())
        sync_params = list(sync_sig.parameters.keys())
        async_params = list(async_sig.parameters.keys())

        assert base_params == sync_params == async_params

    def test_subscribe_signature_consistent(self) -> None:
        """subscribe method should have consistent signature in all protocols."""
        import inspect

        base_sig = inspect.signature(ProtocolEventBusBase.subscribe)
        sync_sig = inspect.signature(ProtocolSyncEventBus.subscribe)
        async_sig = inspect.signature(ProtocolAsyncEventBus.subscribe)

        # Parameter names should match
        base_params = list(base_sig.parameters.keys())
        sync_params = list(sync_sig.parameters.keys())
        async_params = list(async_sig.parameters.keys())

        assert base_params == sync_params == async_params


class TestDocstringInheritance:
    """Test that protocols have proper documentation.

    These tests verify that both parent and child protocols have
    docstrings explaining their purpose and inheritance relationship.
    """

    def test_base_protocol_has_docstring(self) -> None:
        """ProtocolEventBusBase should have a docstring."""
        assert ProtocolEventBusBase.__doc__ is not None
        assert len(ProtocolEventBusBase.__doc__.strip()) > 0

    def test_sync_protocol_has_docstring(self) -> None:
        """ProtocolSyncEventBus should have a docstring."""
        assert ProtocolSyncEventBus.__doc__ is not None
        assert len(ProtocolSyncEventBus.__doc__.strip()) > 0

    def test_async_protocol_has_docstring(self) -> None:
        """ProtocolAsyncEventBus should have a docstring."""
        assert ProtocolAsyncEventBus.__doc__ is not None
        assert len(ProtocolAsyncEventBus.__doc__.strip()) > 0

    def test_sync_protocol_docstring_mentions_inheritance(self) -> None:
        """ProtocolSyncEventBus docstring should mention inheritance."""
        docstring = ProtocolSyncEventBus.__doc__ or ""
        # Should mention inheriting from base or having unified interface
        assert (
            "inherit" in docstring.lower()
            or "base" in docstring.lower()
            or "unified" in docstring.lower()
        )

    def test_async_protocol_docstring_mentions_inheritance(self) -> None:
        """ProtocolAsyncEventBus docstring should mention inheritance."""
        docstring = ProtocolAsyncEventBus.__doc__ or ""
        # Should mention inheriting from base or having unified interface
        assert (
            "inherit" in docstring.lower()
            or "base" in docstring.lower()
            or "unified" in docstring.lower()
        )


class TestProtocolCannotBeInstantiated:
    """Test that protocols cannot be directly instantiated.

    These tests verify the standard Protocol behavior that prevents
    direct instantiation of Protocol classes.
    """

    def test_base_protocol_cannot_be_instantiated(self) -> None:
        """ProtocolEventBusBase should not be directly instantiable."""
        with pytest.raises(TypeError):
            ProtocolEventBusBase()  # type: ignore[misc]

    def test_sync_protocol_cannot_be_instantiated(self) -> None:
        """ProtocolSyncEventBus should not be directly instantiable."""
        with pytest.raises(TypeError):
            ProtocolSyncEventBus()  # type: ignore[misc]

    def test_async_protocol_cannot_be_instantiated(self) -> None:
        """ProtocolAsyncEventBus should not be directly instantiable."""
        with pytest.raises(TypeError):
            ProtocolAsyncEventBus()  # type: ignore[misc]
