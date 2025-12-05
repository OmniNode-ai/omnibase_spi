"""
Integration test fixtures and configuration.

This module provides:
- pytest marker configuration for integration tests
- Shared fixtures for integration testing
- Mock implementations that simulate real providers

Note on type annotations:
    Mock implementations in this module return concrete types (MockEventBus,
    MockComputeNode) rather than protocol types. This allows tests to access
    mock-specific helper methods (get_published_messages, get_execution_count)
    while still satisfying protocol isinstance checks.
"""

from collections.abc import AsyncGenerator
from unittest.mock import MagicMock

import pytest


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers for integration tests."""
    config.addinivalue_line(
        "markers",
        "integration: mark test as integration test (deselect with '-m \"not integration\"')",
    )
    config.addinivalue_line(
        "markers",
        "slow: mark test as slow (deselect with '-m \"not slow\"')",
    )


# -----------------------------------------------------------------------------
# Mock Event Bus Implementation for Integration Testing
# -----------------------------------------------------------------------------


class MockEventBus:
    """
    A mock event bus implementation for integration testing.

    This provides a minimal but functional implementation that can be used
    to verify protocol interactions work correctly end-to-end.
    """

    def __init__(self, environment: str, group: str) -> None:
        """Initialize the mock event bus."""
        self._environment = environment
        self._group = group
        self._messages: list[dict[str, object]] = []
        self._subscriptions: dict[str, list[object]] = {}
        self._connected = False

    @property
    def environment(self) -> str:
        """Get the environment this bus belongs to."""
        return self._environment

    @property
    def group(self) -> str:
        """Get the consumer group for this bus."""
        return self._group

    @property
    def is_connected(self) -> bool:
        """Check if the bus is connected."""
        return self._connected

    async def connect(self) -> None:
        """Connect the event bus."""
        self._connected = True

    async def disconnect(self) -> None:
        """Disconnect the event bus."""
        self._connected = False

    async def publish(self, topic: str, message: dict[str, object]) -> None:
        """Publish a message to a topic."""
        if not self._connected:
            raise RuntimeError("Event bus not connected")
        self._messages.append({"topic": topic, "message": message})

    async def subscribe(self, topic: str, handler: object) -> None:
        """Subscribe to a topic."""
        if topic not in self._subscriptions:
            self._subscriptions[topic] = []
        self._subscriptions[topic].append(handler)

    def get_published_messages(self) -> list[dict[str, object]]:
        """Get all published messages (for testing)."""
        return self._messages.copy()

    def clear_messages(self) -> None:
        """Clear all published messages (for testing)."""
        self._messages.clear()


class MockEventBusProvider:
    """
    A mock event bus provider for integration testing.

    This implements the ProtocolEventBusProvider protocol with a functional
    mock implementation that tracks created buses and allows testing of
    provider lifecycle operations.
    """

    def __init__(
        self,
        default_env: str = "test",
        default_group: str = "test-group",
    ) -> None:
        """Initialize the mock provider."""
        self._default_environment = default_env
        self._default_group = default_group
        self._buses: dict[str, MockEventBus] = {}

    @property
    def default_environment(self) -> str:
        """Get the default environment."""
        return self._default_environment

    @property
    def default_group(self) -> str:
        """Get the default consumer group."""
        return self._default_group

    async def get_event_bus(
        self,
        environment: str | None = None,
        group: str | None = None,
    ) -> "MockEventBus":
        """Get or create an event bus instance."""
        env = environment or self._default_environment
        grp = group or self._default_group
        key = f"{env}:{grp}"

        if key not in self._buses:
            self._buses[key] = MockEventBus(env, grp)
            await self._buses[key].connect()

        return self._buses[key]

    async def create_event_bus(
        self,
        environment: str,
        group: str,
        config: dict[str, object] | None = None,  # noqa: ARG002
    ) -> "MockEventBus":
        """Create a new event bus instance."""
        bus = MockEventBus(environment, group)
        await bus.connect()
        # Store with unique key to avoid overwriting
        key = f"{environment}:{group}:{id(bus)}"
        self._buses[key] = bus
        return bus

    async def close_all(self) -> None:
        """Close all managed event bus instances."""
        for bus in self._buses.values():
            await bus.disconnect()
        self._buses.clear()

    def get_active_bus_count(self) -> int:
        """Get count of active buses (for testing)."""
        return len(self._buses)


# -----------------------------------------------------------------------------
# Mock Compute Node Implementation for Integration Testing
# -----------------------------------------------------------------------------


class MockComputeNode:
    """
    A mock compute node for integration testing.

    Implements ProtocolComputeNode with configurable behavior for testing
    different execution scenarios.
    """

    def __init__(
        self,
        node_id: str = "mock-compute-v1",
        deterministic: bool = True,
        transform_fn: object | None = None,
    ) -> None:
        """Initialize the mock compute node."""
        self._node_id = node_id
        self._deterministic = deterministic
        self._transform_fn = transform_fn
        self._execution_count = 0

    @property
    def node_id(self) -> str:
        """Return node identifier."""
        return self._node_id

    @property
    def node_type(self) -> str:
        """Return node type."""
        return "compute"

    @property
    def version(self) -> str:
        """Return semantic version."""
        return "1.0.0"

    @property
    def is_deterministic(self) -> bool:
        """Return whether node is deterministic."""
        return self._deterministic

    async def execute(self, input_data: object) -> object:
        """Execute compute operation."""
        self._execution_count += 1
        if self._transform_fn is not None:
            return self._transform_fn(input_data)  # type: ignore[operator]
        return {"processed": True, "input": input_data}

    def get_execution_count(self) -> int:
        """Get the number of times execute was called (for testing)."""
        return self._execution_count


# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------


@pytest.fixture
def mock_event_bus_provider() -> MockEventBusProvider:
    """
    Fixture providing a mock event bus provider for integration testing.

    This fixture provides a fully functional mock implementation that
    can be used to test code that depends on ProtocolEventBusProvider.

    Returns:
        MockEventBusProvider: A mock implementation of ProtocolEventBusProvider

    Example:
        def test_my_service(mock_event_bus_provider):
            service = MyService(event_bus_provider=mock_event_bus_provider)
            # Test service behavior with the mock provider
    """
    return MockEventBusProvider()


@pytest.fixture
async def connected_event_bus(
    mock_event_bus_provider: MockEventBusProvider,
) -> AsyncGenerator[MockEventBus, None]:
    """
    Fixture providing a connected mock event bus.

    This fixture creates and connects an event bus, yielding it for use
    in tests, and automatically disconnects it after the test completes.

    Yields:
        MockEventBus: A connected mock event bus instance

    Example:
        @pytest.mark.asyncio
        async def test_publish(connected_event_bus):
            await connected_event_bus.publish("topic", {"key": "value"})
            assert len(connected_event_bus.get_published_messages()) == 1
    """
    bus = await mock_event_bus_provider.get_event_bus()
    yield bus
    await mock_event_bus_provider.close_all()


@pytest.fixture
def mock_compute_node() -> MockComputeNode:
    """
    Fixture providing a mock compute node for integration testing.

    Returns:
        MockComputeNode: A mock implementation of ProtocolComputeNode

    Example:
        @pytest.mark.asyncio
        async def test_compute_execution(mock_compute_node):
            result = await mock_compute_node.execute({"data": "test"})
            assert result["processed"] is True
    """
    return MockComputeNode()


@pytest.fixture
def mock_handler() -> MagicMock:
    """
    Fixture providing a generic mock handler.

    This is useful for testing subscription and callback patterns.

    Returns:
        MagicMock: A mock object that can be used as a handler
    """
    return MagicMock()
