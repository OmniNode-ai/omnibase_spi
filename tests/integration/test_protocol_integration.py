"""
Integration tests for SPI protocols.

These tests verify that protocols work correctly with real implementations
in end-to-end scenarios. Unlike unit tests that verify protocol compliance
in isolation, these tests validate actual behavior.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from omnibase_spi.protocols.event_bus import ProtocolEventBusProvider
from omnibase_spi.protocols.nodes import ProtocolComputeNode

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from tests.integration.conftest import (
        MockComputeNode,
        MockEventBus,
        MockEventBusProvider,
    )


@pytest.mark.integration
class TestEventBusProviderIntegration:
    """Integration tests for ProtocolEventBusProvider implementations."""

    def test_mock_provider_satisfies_protocol(
        self,
        mock_event_bus_provider: MockEventBusProvider,
    ) -> None:
        """MockEventBusProvider should satisfy ProtocolEventBusProvider."""
        assert isinstance(mock_event_bus_provider, ProtocolEventBusProvider)

    @pytest.mark.asyncio
    async def test_provider_creates_bus_on_get(
        self,
        mock_event_bus_provider: MockEventBusProvider,
    ) -> None:
        """get_event_bus should create and return a connected bus."""
        bus = await mock_event_bus_provider.get_event_bus()
        assert bus is not None
        assert bus.is_connected

    @pytest.mark.asyncio
    async def test_provider_returns_same_bus_for_same_params(
        self,
        mock_event_bus_provider: MockEventBusProvider,
    ) -> None:
        """get_event_bus should return the same bus for same environment/group."""
        bus1 = await mock_event_bus_provider.get_event_bus(
            environment="test", group="consumer"
        )
        bus2 = await mock_event_bus_provider.get_event_bus(
            environment="test", group="consumer"
        )
        assert bus1 is bus2

    @pytest.mark.asyncio
    async def test_provider_creates_different_bus_for_different_params(
        self,
        mock_event_bus_provider: MockEventBusProvider,
    ) -> None:
        """get_event_bus should return different buses for different params."""
        bus1 = await mock_event_bus_provider.get_event_bus(
            environment="test", group="consumer-1"
        )
        bus2 = await mock_event_bus_provider.get_event_bus(
            environment="test", group="consumer-2"
        )
        assert bus1 is not bus2

    @pytest.mark.asyncio
    async def test_create_event_bus_always_creates_new(
        self,
        mock_event_bus_provider: MockEventBusProvider,
    ) -> None:
        """create_event_bus should always create a new bus instance."""
        bus1 = await mock_event_bus_provider.create_event_bus(
            environment="test", group="consumer"
        )
        bus2 = await mock_event_bus_provider.create_event_bus(
            environment="test", group="consumer"
        )
        assert bus1 is not bus2

    @pytest.mark.asyncio
    async def test_close_all_disconnects_buses(
        self,
        mock_event_bus_provider: MockEventBusProvider,
    ) -> None:
        """close_all should disconnect all managed buses."""
        bus1 = await mock_event_bus_provider.get_event_bus(
            environment="test", group="group-1"
        )
        bus2 = await mock_event_bus_provider.get_event_bus(
            environment="test", group="group-2"
        )

        assert bus1.is_connected
        assert bus2.is_connected

        await mock_event_bus_provider.close_all()

        assert not bus1.is_connected
        assert not bus2.is_connected

    @pytest.mark.asyncio
    async def test_provider_uses_defaults(
        self,
        mock_event_bus_provider: MockEventBusProvider,
    ) -> None:
        """Provider should use default environment and group when not specified."""
        bus = await mock_event_bus_provider.get_event_bus()
        assert bus.environment == mock_event_bus_provider.default_environment
        assert bus.group == mock_event_bus_provider.default_group


@pytest.mark.integration
class TestEventBusIntegration:
    """Integration tests for event bus publish/subscribe behavior."""

    @pytest.mark.asyncio
    async def test_publish_stores_message(
        self,
        connected_event_bus: MockEventBus,
    ) -> None:
        """Published messages should be stored and retrievable."""
        await connected_event_bus.publish("test-topic", {"key": "value"})

        messages = connected_event_bus.get_published_messages()
        assert len(messages) == 1
        assert messages[0]["topic"] == "test-topic"
        assert messages[0]["message"] == {"key": "value"}

    @pytest.mark.asyncio
    async def test_multiple_publishes(
        self,
        connected_event_bus: MockEventBus,
    ) -> None:
        """Multiple publishes should accumulate messages."""
        await connected_event_bus.publish("topic-1", {"msg": 1})
        await connected_event_bus.publish("topic-2", {"msg": 2})
        await connected_event_bus.publish("topic-1", {"msg": 3})

        messages = connected_event_bus.get_published_messages()
        assert len(messages) == 3

    @pytest.mark.asyncio
    async def test_publish_requires_connection(
        self,
        mock_event_bus_provider: MockEventBusProvider,
    ) -> None:
        """Publishing to a disconnected bus should raise an error."""
        bus = await mock_event_bus_provider.get_event_bus()
        await bus.disconnect()

        with pytest.raises(RuntimeError, match="not connected"):
            await bus.publish("topic", {"key": "value"})

    @pytest.mark.asyncio
    async def test_subscribe_registers_handler(
        self,
        connected_event_bus: MockEventBus,
        mock_handler: MagicMock,
    ) -> None:
        """Subscribe should register the handler for the topic."""
        await connected_event_bus.subscribe("test-topic", mock_handler)

        assert "test-topic" in connected_event_bus._subscriptions
        assert mock_handler in connected_event_bus._subscriptions["test-topic"]


@pytest.mark.integration
class TestComputeNodeIntegration:
    """Integration tests for ProtocolComputeNode implementations."""

    def test_mock_node_satisfies_protocol(
        self,
        mock_compute_node: MockComputeNode,
    ) -> None:
        """MockComputeNode should satisfy ProtocolComputeNode."""
        assert isinstance(mock_compute_node, ProtocolComputeNode)

    @pytest.mark.asyncio
    async def test_execute_processes_input(
        self,
        mock_compute_node: MockComputeNode,
    ) -> None:
        """Execute should process input and return result."""
        result = await mock_compute_node.execute({"data": "test"})

        assert result is not None
        assert isinstance(result, dict)
        assert result["processed"] is True
        assert result["input"] == {"data": "test"}

    @pytest.mark.asyncio
    async def test_execution_count_tracks_calls(
        self,
        mock_compute_node: MockComputeNode,
    ) -> None:
        """Execution count should track number of execute calls."""
        assert mock_compute_node.get_execution_count() == 0

        await mock_compute_node.execute({"data": 1})
        assert mock_compute_node.get_execution_count() == 1

        await mock_compute_node.execute({"data": 2})
        await mock_compute_node.execute({"data": 3})
        assert mock_compute_node.get_execution_count() == 3

    def test_node_properties(
        self,
        mock_compute_node: MockComputeNode,
    ) -> None:
        """Node should have all required properties."""
        assert mock_compute_node.node_id == "mock-compute-v1"
        assert mock_compute_node.node_type == "compute"
        assert mock_compute_node.version == "1.0.0"
        assert mock_compute_node.is_deterministic is True


@pytest.mark.integration
class TestCustomComputeNodeIntegration:
    """Integration tests with custom compute node configurations."""

    @pytest.mark.asyncio
    async def test_custom_transform_function(self) -> None:
        """Compute node should use custom transform function when provided."""
        from tests.integration.conftest import MockComputeNode

        def double_value(data: dict[str, object]) -> dict[str, int]:
            """Double numeric values in input."""
            value = data.get("value", 0)
            return {"doubled": int(value) * 2 if isinstance(value, (int, float)) else 0}

        node = MockComputeNode(transform_fn=double_value)
        result = await node.execute({"value": 5})

        assert result == {"doubled": 10}

    @pytest.mark.asyncio
    async def test_non_deterministic_node(self) -> None:
        """Non-deterministic node should report is_deterministic=False."""
        from tests.integration.conftest import MockComputeNode

        node = MockComputeNode(deterministic=False)
        assert node.is_deterministic is False

    @pytest.mark.asyncio
    async def test_custom_node_id(self) -> None:
        """Node should use custom node_id when provided."""
        from tests.integration.conftest import MockComputeNode

        node = MockComputeNode(node_id="custom-node-v2")
        assert node.node_id == "custom-node-v2"


@pytest.mark.integration
class TestProviderLifecycleIntegration:
    """Integration tests for provider lifecycle patterns."""

    @pytest.mark.asyncio
    async def test_full_provider_lifecycle(
        self,
        mock_event_bus_provider: MockEventBusProvider,
    ) -> None:
        """Test complete provider lifecycle: create, use, cleanup."""
        # Create buses
        bus1 = await mock_event_bus_provider.get_event_bus(
            environment="prod", group="service-a"
        )
        bus2 = await mock_event_bus_provider.create_event_bus(
            environment="prod", group="service-b"
        )

        # Use buses
        await bus1.publish("events", {"type": "created"})
        await bus2.publish("events", {"type": "updated"})

        # Verify messages
        assert len(bus1.get_published_messages()) == 1
        assert len(bus2.get_published_messages()) == 1

        # Cleanup
        await mock_event_bus_provider.close_all()

        # Verify cleanup
        assert not bus1.is_connected
        assert not bus2.is_connected

    @pytest.mark.asyncio
    async def test_provider_with_config(
        self,
        mock_event_bus_provider: MockEventBusProvider,
    ) -> None:
        """create_event_bus should accept optional configuration."""
        config = {
            "auto_offset_reset": "earliest",
            "batch_size": 100,
            "timeout_ms": 5000,
        }

        bus = await mock_event_bus_provider.create_event_bus(
            environment="test",
            group="configured-consumer",
            config=config,
        )

        assert bus is not None
        assert bus.is_connected


@pytest.mark.integration
class TestCrossProtocolIntegration:
    """Integration tests verifying multiple protocols working together."""

    @pytest.mark.asyncio
    async def test_compute_node_with_event_bus(
        self,
        mock_compute_node: MockComputeNode,
        connected_event_bus: MockEventBus,
    ) -> None:
        """
        Test pattern: compute node publishes results to event bus.

        This simulates a common pattern where a compute node processes data
        and publishes the results to an event bus for downstream consumers.
        """
        # Process input through compute node
        input_data = {"value": 42, "operation": "transform"}
        result = await mock_compute_node.execute(input_data)

        # Publish result to event bus
        await connected_event_bus.publish(
            "compute-results",
            {"node_id": mock_compute_node.node_id, "result": result},
        )

        # Verify the message was published
        messages = connected_event_bus.get_published_messages()
        assert len(messages) == 1
        assert messages[0]["topic"] == "compute-results"
        message_payload = messages[0]["message"]
        assert isinstance(message_payload, dict)
        assert message_payload["node_id"] == "mock-compute-v1"
