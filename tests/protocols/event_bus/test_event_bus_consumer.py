"""
Tests for ProtocolEventBusConsumer protocol compliance.

This module validates that the ProtocolEventBusConsumer protocol is correctly
defined and can be used for runtime type checking.

Protocols Tested
----------------
- **ProtocolEventBusConsumer**: Consumer operations including topic subscription,
  message consumption, offset management, and seek operations.

Test Organization
-----------------
1. **Protocol Tests** (TestProtocolEventBusConsumerProtocol): Verify protocol structure.
2. **Compliance Tests** (TestProtocolEventBusConsumerCompliance): Verify isinstance behavior.
3. **Signature Tests** (TestProtocolEventBusConsumerMethodSignatures): Verify method signatures.
4. **Async Nature Tests** (TestProtocolEventBusConsumerAsyncNature): Verify async methods.
5. **Edge Case Tests** (TestProtocolEventBusConsumerEdgeCases): Verify boundary conditions.

Testing Approach
----------------
Mock implementations are used to test protocol compliance:

- **CompliantEventBusConsumer**: Fully implements ProtocolEventBusConsumer
- **PartialEventBusConsumer**: Implements only some methods (should fail isinstance)

Note on Type Ignores
--------------------
- ``# type: ignore[misc]`` on protocol instantiation: Required because we're
  intentionally testing that Protocol classes raise TypeError when instantiated.

- ``# type: ignore[comparison-overlap]`` on Protocol MRO check: mypy incorrectly
  flags the comparison, but at runtime we need to verify Protocol is in the MRO.
"""

import inspect
from typing import Protocol

import pytest

from omnibase_spi.protocols.event_bus.protocol_event_bus_extended import (
    ProtocolEventBusConsumer,
    ProtocolEventBusMessage,
)

# =============================================================================
# Mock/Compliant Implementations for Testing
# =============================================================================


class CompliantEventBusConsumer:
    """Test double implementing all ProtocolEventBusConsumer requirements.

    This mock provides a complete consumer implementation for protocol testing.
    All async methods are no-ops since we're only testing protocol compliance.

    Implements:
        - subscribe_to_topics(topics, group_id)
        - unsubscribe_from_topics(topics)
        - consume_messages(timeout_ms, max_messages) -> list[Message]
        - consume_messages_stream(batch_timeout_ms) -> list[Message]
        - commit_offsets()
        - seek_to_beginning(topic, partition)
        - seek_to_end(topic, partition)
        - seek_to_offset(topic, partition, offset)
        - get_current_offsets() -> dict[str, dict[int, int]]
        - close_consumer(timeout_seconds)
        - validate_connection() -> bool
    """

    async def subscribe_to_topics(self, topics: list[str], group_id: str) -> None:
        """Subscribe to topics."""
        _ = (topics, group_id)  # Unused in mock

    async def unsubscribe_from_topics(self, topics: list[str]) -> None:
        """Unsubscribe from topics."""
        _ = topics  # Unused in mock

    async def consume_messages(
        self, timeout_ms: int, max_messages: int
    ) -> list[ProtocolEventBusMessage]:
        """Consume messages."""
        _ = (timeout_ms, max_messages)  # Unused in mock
        return []

    async def consume_messages_stream(
        self, batch_timeout_ms: int
    ) -> list[ProtocolEventBusMessage]:
        """Consume a batch of messages with streaming semantics."""
        _ = batch_timeout_ms  # Unused in mock
        return []

    async def commit_offsets(self) -> None:
        """Commit current consumer offsets."""
        pass

    async def seek_to_beginning(self, topic: str, partition: int) -> None:
        """Seek to the beginning of a topic partition."""
        _ = (topic, partition)  # Unused in mock

    async def seek_to_end(self, topic: str, partition: int) -> None:
        """Seek to the end of a topic partition."""
        _ = (topic, partition)  # Unused in mock

    async def seek_to_offset(self, topic: str, partition: int, offset: int) -> None:
        """Seek to a specific offset."""
        _ = (topic, partition, offset)  # Unused in mock

    async def get_current_offsets(self) -> dict[str, dict[int, int]]:
        """Get current consumer offsets."""
        return {"test-topic": {0: 100}}

    async def close_consumer(self, timeout_seconds: float = 30.0) -> None:
        """Close the consumer."""
        _ = timeout_seconds  # Unused in mock

    async def validate_connection(self) -> bool:
        """Validate the connection."""
        return True


class PartialEventBusConsumer:
    """Test double implementing only SOME ProtocolEventBusConsumer methods.

    Missing methods (intentionally):
        - unsubscribe_from_topics
        - consume_messages_stream
        - commit_offsets
        - seek_to_beginning, seek_to_end, seek_to_offset
        - get_current_offsets
        - close_consumer
        - validate_connection

    Used by: test_partial_implementation_fails_isinstance
    """

    async def subscribe_to_topics(self, topics: list[str], group_id: str) -> None:
        """Subscribe to topics."""
        _ = (topics, group_id)  # Unused in mock

    async def consume_messages(
        self, timeout_ms: int, max_messages: int
    ) -> list[ProtocolEventBusMessage]:
        """Consume messages."""
        _ = (timeout_ms, max_messages)  # Unused in mock
        return []


# =============================================================================
# Pytest Fixtures
# =============================================================================


@pytest.fixture
def compliant_consumer() -> CompliantEventBusConsumer:
    """Provide a compliant EventBus consumer for protocol compliance testing.

    Returns:
        A fresh CompliantEventBusConsumer instance implementing all
        ProtocolEventBusConsumer requirements.
    """
    return CompliantEventBusConsumer()


# =============================================================================
# Test Classes
# =============================================================================


class TestProtocolEventBusConsumerProtocol:
    """Test suite for ProtocolEventBusConsumer protocol compliance."""

    def test_protocol_is_runtime_checkable(self) -> None:
        """ProtocolEventBusConsumer should be runtime_checkable."""
        assert hasattr(ProtocolEventBusConsumer, "_is_runtime_protocol") or hasattr(
            ProtocolEventBusConsumer, "__runtime_protocol__"
        )

    def test_protocol_is_protocol(self) -> None:
        """ProtocolEventBusConsumer should be a Protocol class."""
        assert any(
            base is Protocol or base.__name__ == "Protocol"  # type: ignore[comparison-overlap]
            for base in ProtocolEventBusConsumer.__mro__
        )

    def test_protocol_has_subscribe_to_topics_method(self) -> None:
        """Should define subscribe_to_topics method."""
        assert "subscribe_to_topics" in dir(ProtocolEventBusConsumer)

    def test_protocol_has_unsubscribe_from_topics_method(self) -> None:
        """Should define unsubscribe_from_topics method."""
        assert "unsubscribe_from_topics" in dir(ProtocolEventBusConsumer)

    def test_protocol_has_consume_messages_method(self) -> None:
        """Should define consume_messages method."""
        assert "consume_messages" in dir(ProtocolEventBusConsumer)

    def test_protocol_has_consume_messages_stream_method(self) -> None:
        """Should define consume_messages_stream method."""
        assert "consume_messages_stream" in dir(ProtocolEventBusConsumer)

    def test_protocol_has_commit_offsets_method(self) -> None:
        """Should define commit_offsets method."""
        assert "commit_offsets" in dir(ProtocolEventBusConsumer)

    def test_protocol_has_seek_methods(self) -> None:
        """Should define all seek methods."""
        assert "seek_to_beginning" in dir(ProtocolEventBusConsumer)
        assert "seek_to_end" in dir(ProtocolEventBusConsumer)
        assert "seek_to_offset" in dir(ProtocolEventBusConsumer)

    def test_protocol_has_get_current_offsets_method(self) -> None:
        """Should define get_current_offsets method."""
        assert "get_current_offsets" in dir(ProtocolEventBusConsumer)

    def test_protocol_has_close_consumer_method(self) -> None:
        """Should define close_consumer method."""
        assert "close_consumer" in dir(ProtocolEventBusConsumer)

    def test_protocol_has_validate_connection_method(self) -> None:
        """Should define validate_connection method."""
        assert "validate_connection" in dir(ProtocolEventBusConsumer)

    def test_protocol_cannot_be_instantiated(self) -> None:
        """ProtocolEventBusConsumer should not be directly instantiable."""
        with pytest.raises(TypeError):
            # Intentionally testing that Protocol cannot be instantiated
            ProtocolEventBusConsumer()  # type: ignore[misc]


class TestProtocolEventBusConsumerCompliance:
    """Test isinstance checks for ProtocolEventBusConsumer compliance."""

    def test_compliant_class_passes_isinstance(
        self, compliant_consumer: CompliantEventBusConsumer
    ) -> None:
        """A class implementing all methods should pass isinstance check."""
        assert isinstance(compliant_consumer, ProtocolEventBusConsumer)

    def test_partial_implementation_fails_isinstance(self) -> None:
        """A class missing methods should fail isinstance check."""
        consumer = PartialEventBusConsumer()
        assert not isinstance(consumer, ProtocolEventBusConsumer)


class TestProtocolEventBusConsumerMethodSignatures:
    """Test method signatures for ProtocolEventBusConsumer."""

    @pytest.mark.asyncio
    async def test_subscribe_to_topics_accepts_topics_and_group(
        self, compliant_consumer: CompliantEventBusConsumer
    ) -> None:
        """subscribe_to_topics should accept topics and group_id."""
        await compliant_consumer.subscribe_to_topics(topics=["test"], group_id="group")

    @pytest.mark.asyncio
    async def test_consume_messages_accepts_timeout_and_max(
        self, compliant_consumer: CompliantEventBusConsumer
    ) -> None:
        """consume_messages should accept timeout_ms and max_messages."""
        messages = await compliant_consumer.consume_messages(timeout_ms=1000, max_messages=100)
        assert isinstance(messages, list)

    @pytest.mark.asyncio
    async def test_consume_messages_stream_accepts_batch_timeout(
        self, compliant_consumer: CompliantEventBusConsumer
    ) -> None:
        """consume_messages_stream should accept batch_timeout_ms."""
        messages = await compliant_consumer.consume_messages_stream(batch_timeout_ms=1000)
        assert isinstance(messages, list)

    @pytest.mark.asyncio
    async def test_get_current_offsets_returns_nested_dict(
        self, compliant_consumer: CompliantEventBusConsumer
    ) -> None:
        """get_current_offsets should return dict[str, dict[int, int]]."""
        offsets = await compliant_consumer.get_current_offsets()
        assert isinstance(offsets, dict)
        for topic, partitions in offsets.items():
            assert isinstance(topic, str)
            assert isinstance(partitions, dict)


class TestProtocolEventBusConsumerAsyncNature:
    """Test that ProtocolEventBusConsumer methods are async."""

    def test_subscribe_to_topics_is_async(self) -> None:
        """subscribe_to_topics should be async in both protocol and implementation."""
        # Check protocol defines async signature
        protocol_method = getattr(ProtocolEventBusConsumer, "subscribe_to_topics", None)
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)
        # Check compliant implementation is async
        assert inspect.iscoroutinefunction(CompliantEventBusConsumer.subscribe_to_topics)

    def test_consume_messages_is_async(self) -> None:
        """consume_messages should be async in both protocol and implementation."""
        # Check protocol defines async signature
        protocol_method = getattr(ProtocolEventBusConsumer, "consume_messages", None)
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)
        # Check compliant implementation is async
        assert inspect.iscoroutinefunction(CompliantEventBusConsumer.consume_messages)

    def test_commit_offsets_is_async(self) -> None:
        """commit_offsets should be async in both protocol and implementation."""
        # Check protocol defines async signature
        protocol_method = getattr(ProtocolEventBusConsumer, "commit_offsets", None)
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)
        # Check compliant implementation is async
        assert inspect.iscoroutinefunction(CompliantEventBusConsumer.commit_offsets)

    def test_validate_connection_is_async(self) -> None:
        """validate_connection should be async in both protocol and implementation."""
        # Check protocol defines async signature
        protocol_method = getattr(ProtocolEventBusConsumer, "validate_connection", None)
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)
        # Check compliant implementation is async
        assert inspect.iscoroutinefunction(
            CompliantEventBusConsumer.validate_connection
        )


class TestProtocolEventBusConsumerEdgeCases:
    """Test edge cases for ProtocolEventBusConsumer."""

    @pytest.mark.asyncio
    async def test_consume_with_zero_timeout(self) -> None:
        """Consume with zero timeout should return immediately."""
        consumer = CompliantEventBusConsumer()
        messages = await consumer.consume_messages(timeout_ms=0, max_messages=10)
        assert isinstance(messages, list)

    @pytest.mark.asyncio
    async def test_consume_with_zero_max_messages(self) -> None:
        """Consume with zero max_messages returns empty list."""
        consumer = CompliantEventBusConsumer()
        messages = await consumer.consume_messages(timeout_ms=1000, max_messages=0)
        assert messages == []

    @pytest.mark.asyncio
    async def test_subscribe_to_empty_topics_list(self) -> None:
        """Subscribe to empty topics list should work."""
        consumer = CompliantEventBusConsumer()
        await consumer.subscribe_to_topics(topics=[], group_id="test-group")

    @pytest.mark.asyncio
    async def test_seek_to_offset_zero(self) -> None:
        """Seeking to offset 0 should work."""
        consumer = CompliantEventBusConsumer()
        await consumer.seek_to_offset(topic="test", partition=0, offset=0)

    @pytest.mark.asyncio
    async def test_subscribe_to_single_topic(self) -> None:
        """Subscribe to a single topic should work."""
        consumer = CompliantEventBusConsumer()
        await consumer.subscribe_to_topics(topics=["single-topic"], group_id="group")

    @pytest.mark.asyncio
    async def test_subscribe_to_many_topics(self) -> None:
        """Subscribe to many topics should work."""
        consumer = CompliantEventBusConsumer()
        topics = [f"topic-{i}" for i in range(100)]
        await consumer.subscribe_to_topics(topics=topics, group_id="group")

    @pytest.mark.asyncio
    async def test_unsubscribe_from_empty_topics_list(self) -> None:
        """Unsubscribe from empty topics list should work."""
        consumer = CompliantEventBusConsumer()
        await consumer.unsubscribe_from_topics(topics=[])

    @pytest.mark.asyncio
    async def test_close_with_zero_timeout(self) -> None:
        """Close with zero timeout should work."""
        consumer = CompliantEventBusConsumer()
        await consumer.close_consumer(timeout_seconds=0.0)

    @pytest.mark.asyncio
    async def test_seek_to_partition_zero(self) -> None:
        """Seeking to partition 0 should work."""
        consumer = CompliantEventBusConsumer()
        await consumer.seek_to_beginning(topic="test", partition=0)
        await consumer.seek_to_end(topic="test", partition=0)
