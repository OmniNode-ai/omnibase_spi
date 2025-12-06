"""
Tests for ProtocolEventBusProvider protocol.

Validates that ProtocolEventBusProvider:
- Is properly runtime checkable
- Defines required methods (get_event_bus, create_event_bus, close_all)
- Defines required properties (default_environment, default_group)
- Methods have correct signatures
- Cannot be instantiated directly
- Works correctly with isinstance checks for compliant/non-compliant classes
"""

import pytest

from omnibase_spi.protocols.event_bus.protocol_event_bus_mixin import (
    ProtocolEventBusBase,
)
from omnibase_spi.protocols.event_bus.protocol_event_bus_provider import (
    ProtocolEventBusProvider,
)
from omnibase_spi.protocols.types.protocol_event_bus_types import ProtocolEventMessage


class MockEventBus:
    """Test double implementing ProtocolEventBusBase for testing purposes.

    Provides a minimal implementation of the event bus protocol that can be
    used as a return value from provider methods without requiring MagicMock.
    """

    def __init__(self) -> None:
        """Initialize the mock event bus with empty state."""
        self._published_events: list[ProtocolEventMessage] = []
        self._handlers: dict[str, list[object]] = {}
        self._consuming: bool = False

    async def publish(self, event: ProtocolEventMessage) -> None:
        """Record published events for test verification.

        Args:
            event: The event message to publish.
        """
        self._published_events.append(event)

    async def publish_envelope(self, envelope: object, topic: str) -> None:
        """Publish an envelope to a topic (mock implementation).

        Args:
            envelope: The envelope to publish.
            topic: The topic to publish to.
        """
        pass

    async def subscribe(
        self,
        topic: str,
        handler: object,
    ) -> None:
        """Subscribe to a topic with a handler (mock implementation).

        Args:
            topic: The topic to subscribe to.
            handler: The handler function.
        """
        if topic not in self._handlers:
            self._handlers[topic] = []
        self._handlers[topic].append(handler)

    async def start_consuming(self) -> None:
        """Start consuming messages (mock implementation)."""
        self._consuming = True

    async def health_check(self) -> bool:
        """Check health status (mock implementation).

        Returns:
            Always True for mock.
        """
        return True

    @property
    def published_events(self) -> list[ProtocolEventMessage]:
        """Access recorded events for test assertions.

        Returns:
            List of events that were published to this bus.
        """
        return self._published_events


# Verify MockEventBus satisfies the protocol
assert isinstance(MockEventBus(), ProtocolEventBusBase)


class CompliantProvider:
    """A class that fully implements the ProtocolEventBusProvider protocol."""

    async def get_event_bus(
        self,
        environment: str | None = None,  # noqa: ARG002
        group: str | None = None,  # noqa: ARG002
    ) -> ProtocolEventBusBase:
        """Get or create an event bus instance."""
        return MockEventBus()

    async def create_event_bus(
        self,
        environment: str,  # noqa: ARG002
        group: str,  # noqa: ARG002
        config: dict[str, object] | None = None,  # noqa: ARG002
    ) -> ProtocolEventBusBase:
        """Create a new event bus instance."""
        return MockEventBus()

    async def close_all(self) -> None:
        """Close all managed event bus instances."""
        pass

    @property
    def default_environment(self) -> str:
        """Get the default environment."""
        return "local"

    @property
    def default_group(self) -> str:
        """Get the default consumer group."""
        return "default-group"


class PartialProvider:
    """A class that only implements some ProtocolEventBusProvider methods."""

    async def get_event_bus(
        self,
        _environment: str | None = None,
        _group: str | None = None,
    ) -> ProtocolEventBusBase:
        """Get or create an event bus instance."""
        return MockEventBus()


class NonCompliantProvider:
    """A class that implements none of the ProtocolEventBusProvider methods."""

    pass


class MissingPropertiesProvider:
    """A class that has methods but not properties."""

    async def get_event_bus(
        self,
        _environment: str | None = None,
        _group: str | None = None,
    ) -> ProtocolEventBusBase:
        """Get or create an event bus instance."""
        return MockEventBus()

    async def create_event_bus(
        self,
        _environment: str,
        _group: str,
        _config: dict[str, object] | None = None,
    ) -> ProtocolEventBusBase:
        """Create a new event bus instance."""
        return MockEventBus()

    async def close_all(self) -> None:
        """Close all managed event bus instances."""
        pass


class TestProtocolEventBusProviderProtocol:
    """Test suite for ProtocolEventBusProvider protocol compliance."""

    def test_protocol_is_runtime_checkable(self) -> None:
        """ProtocolEventBusProvider should be runtime_checkable."""
        # Python 3.11+ uses _is_runtime_protocol, older versions use __runtime_protocol__
        assert hasattr(ProtocolEventBusProvider, "_is_runtime_protocol") or hasattr(
            ProtocolEventBusProvider, "__runtime_protocol__"
        )

    def test_protocol_is_protocol(self) -> None:
        """ProtocolEventBusProvider should be a Protocol class."""
        from typing import Protocol

        # Check that ProtocolEventBusProvider has Protocol in its bases
        assert any(
            base is Protocol or base.__name__ == "Protocol"
            for base in ProtocolEventBusProvider.__mro__
        )

    def test_protocol_has_get_event_bus_method(self) -> None:
        """ProtocolEventBusProvider should define get_event_bus method."""
        assert "get_event_bus" in dir(ProtocolEventBusProvider)

    def test_protocol_has_create_event_bus_method(self) -> None:
        """ProtocolEventBusProvider should define create_event_bus method."""
        assert "create_event_bus" in dir(ProtocolEventBusProvider)

    def test_protocol_has_close_all_method(self) -> None:
        """ProtocolEventBusProvider should define close_all method."""
        assert "close_all" in dir(ProtocolEventBusProvider)

    def test_protocol_has_default_environment_property(self) -> None:
        """ProtocolEventBusProvider should define default_environment property."""
        assert "default_environment" in dir(ProtocolEventBusProvider)

    def test_protocol_has_default_group_property(self) -> None:
        """ProtocolEventBusProvider should define default_group property."""
        assert "default_group" in dir(ProtocolEventBusProvider)

    def test_protocol_cannot_be_instantiated(self) -> None:
        """ProtocolEventBusProvider protocol should not be directly instantiable."""
        with pytest.raises(TypeError):
            ProtocolEventBusProvider()  # type: ignore[misc]


class TestProtocolEventBusProviderCompliance:
    """Test isinstance checks for protocol compliance."""

    def test_compliant_class_passes_isinstance(self) -> None:
        """A class implementing all ProtocolEventBusProvider methods should pass isinstance check."""
        provider = CompliantProvider()
        assert isinstance(provider, ProtocolEventBusProvider)

    def test_partial_implementation_fails_isinstance(self) -> None:
        """A class missing ProtocolEventBusProvider methods should fail isinstance check."""
        provider = PartialProvider()
        assert not isinstance(provider, ProtocolEventBusProvider)

    def test_non_compliant_class_fails_isinstance(self) -> None:
        """A class with no ProtocolEventBusProvider methods should fail isinstance check."""
        provider = NonCompliantProvider()
        assert not isinstance(provider, ProtocolEventBusProvider)

    def test_missing_properties_fails_isinstance(self) -> None:
        """A class missing properties should fail isinstance check."""
        provider = MissingPropertiesProvider()
        assert not isinstance(provider, ProtocolEventBusProvider)


class TestProtocolEventBusProviderMethodSignatures:
    """Test method signatures from compliant implementations."""

    @pytest.mark.asyncio
    async def test_get_event_bus_with_defaults(self) -> None:
        """get_event_bus should work with default parameters."""
        provider = CompliantProvider()
        bus = await provider.get_event_bus()
        assert bus is not None

    @pytest.mark.asyncio
    async def test_get_event_bus_with_environment(self) -> None:
        """get_event_bus should accept environment parameter."""
        provider = CompliantProvider()
        bus = await provider.get_event_bus(environment="prod")
        assert bus is not None

    @pytest.mark.asyncio
    async def test_get_event_bus_with_group(self) -> None:
        """get_event_bus should accept group parameter."""
        provider = CompliantProvider()
        bus = await provider.get_event_bus(group="my-service")
        assert bus is not None

    @pytest.mark.asyncio
    async def test_get_event_bus_with_all_params(self) -> None:
        """get_event_bus should accept both environment and group."""
        provider = CompliantProvider()
        bus = await provider.get_event_bus(environment="prod", group="my-service")
        assert bus is not None

    @pytest.mark.asyncio
    async def test_create_event_bus_accepts_required_params(self) -> None:
        """create_event_bus should require environment and group."""
        provider = CompliantProvider()
        bus = await provider.create_event_bus(environment="test", group="test-consumer")
        assert bus is not None

    @pytest.mark.asyncio
    async def test_create_event_bus_accepts_config(self) -> None:
        """create_event_bus should accept optional config."""
        provider = CompliantProvider()
        bus = await provider.create_event_bus(
            environment="test",
            group="test-consumer",
            config={"auto_offset_reset": "earliest"},
        )
        assert bus is not None

    @pytest.mark.asyncio
    async def test_close_all_takes_no_args(self) -> None:
        """close_all should take no arguments."""
        provider = CompliantProvider()
        # Should not raise
        await provider.close_all()

    def test_default_environment_returns_string(self) -> None:
        """default_environment should return a string."""
        provider = CompliantProvider()
        env = provider.default_environment
        assert isinstance(env, str)

    def test_default_group_returns_string(self) -> None:
        """default_group should return a string."""
        provider = CompliantProvider()
        group = provider.default_group
        assert isinstance(group, str)


class TestProtocolEventBusProviderAsyncNature:
    """Test that ProtocolEventBusProvider methods are async."""

    def test_get_event_bus_is_async(self) -> None:
        """get_event_bus should be an async method."""
        import inspect

        assert inspect.iscoroutinefunction(CompliantProvider.get_event_bus)

    def test_create_event_bus_is_async(self) -> None:
        """create_event_bus should be an async method."""
        import inspect

        assert inspect.iscoroutinefunction(CompliantProvider.create_event_bus)

    def test_close_all_is_async(self) -> None:
        """close_all should be an async method."""
        import inspect

        assert inspect.iscoroutinefunction(CompliantProvider.close_all)


class TestProtocolEventBusProviderImports:
    """Test protocol imports from different locations."""

    def test_import_from_provider_module(self) -> None:
        """Test direct import from protocol_event_bus_provider module."""
        from omnibase_spi.protocols.event_bus.protocol_event_bus_provider import (
            ProtocolEventBusProvider as DirectProvider,
        )

        provider = CompliantProvider()
        assert isinstance(provider, DirectProvider)

    def test_import_from_event_bus_package(self) -> None:
        """Test import from event_bus package."""
        from omnibase_spi.protocols.event_bus import (
            ProtocolEventBusProvider as PackageProvider,
        )

        provider = CompliantProvider()
        assert isinstance(provider, PackageProvider)

    def test_imports_are_identical(self) -> None:
        """Verify imports from different locations are the same class."""
        from omnibase_spi.protocols.event_bus import (
            ProtocolEventBusProvider as PackageProvider,
        )
        from omnibase_spi.protocols.event_bus.protocol_event_bus_provider import (
            ProtocolEventBusProvider as DirectProvider,
        )

        assert PackageProvider is DirectProvider


class TestProtocolEventBusProviderDocumentation:
    """Test that ProtocolEventBusProvider has proper documentation."""

    def test_protocol_has_docstring(self) -> None:
        """ProtocolEventBusProvider should have a docstring."""
        assert ProtocolEventBusProvider.__doc__ is not None
        assert len(ProtocolEventBusProvider.__doc__.strip()) > 0

    def test_get_event_bus_has_docstring(self) -> None:
        """get_event_bus method should have a docstring."""
        assert CompliantProvider.get_event_bus.__doc__ is not None

    def test_create_event_bus_has_docstring(self) -> None:
        """create_event_bus method should have a docstring."""
        assert CompliantProvider.create_event_bus.__doc__ is not None

    def test_close_all_has_docstring(self) -> None:
        """close_all method should have a docstring."""
        assert CompliantProvider.close_all.__doc__ is not None


class TestProtocolEventBusProviderContextManagerLifecycle:
    """Test context manager lifecycle patterns for event bus provider."""

    @pytest.mark.asyncio
    async def test_provider_lifecycle_pattern(self) -> None:
        """Test typical provider lifecycle: get bus, use, close all."""
        provider = CompliantProvider()

        # Get event bus
        bus = await provider.get_event_bus(environment="test", group="test-consumer")
        assert bus is not None

        # Create additional bus
        bus2 = await provider.create_event_bus(
            environment="test", group="another-consumer"
        )
        assert bus2 is not None

        # Cleanup
        await provider.close_all()

    @pytest.mark.asyncio
    async def test_factory_pattern_returns_different_instances(self) -> None:
        """create_event_bus should create new instances (no caching)."""
        provider = CompliantProvider()

        bus1 = await provider.create_event_bus(environment="test", group="consumer-1")
        bus2 = await provider.create_event_bus(environment="test", group="consumer-2")

        # create_event_bus should return different instances
        # (Note: MockEventBus always returns new instances, matching expected behavior)
        assert bus1 is not None
        assert bus2 is not None
        assert bus1 is not bus2  # Verify different instances returned
