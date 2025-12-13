"""
Tests for ProtocolEventBusExtendedClient protocol compliance.

This module validates that the ProtocolEventBusExtendedClient protocol is correctly
defined and can be used for runtime type checking. The tests ensure that:

1. **Protocol Structure**: The protocol is properly decorated with @runtime_checkable
   and inherits from typing.Protocol.

2. **Method Signatures**: Required methods are defined with correct parameter types
   and return values.

3. **Instantiation Prevention**: The protocol cannot be directly instantiated.

4. **isinstance Checks**: Compliant implementations pass isinstance checks while
   partial or non-compliant implementations fail.

5. **Async Nature**: Async methods are properly defined as coroutines.

Protocol Tested
---------------
- **ProtocolEventBusExtendedClient**: Comprehensive client combining admin operations
  (topic management) with factory methods for consumers and producers.

Test Organization
-----------------
Tests are organized into the following categories:

1. **Protocol Tests** (TestProtocolEventBusExtendedClientProtocol): Verify protocol definition.
2. **Compliance Tests** (TestProtocolEventBusExtendedClientCompliance): Verify isinstance behavior.
3. **Signature Tests** (TestProtocolEventBusExtendedClientMethodSignatures): Verify method signatures.
4. **Async Nature Tests** (TestProtocolEventBusExtendedClientAsyncNature): Verify async/sync methods.
5. **Edge Case Tests** (TestProtocolEventBusExtendedClientEdgeCases): Verify boundary conditions.

Note on Type Ignores
--------------------
Type ignores in this file are used in specific contexts:

- ``# type: ignore[misc]`` on protocol instantiation: Required because we're
  intentionally testing that Protocol classes raise TypeError when instantiated.

- ``# type: ignore[comparison-overlap]`` on MRO checks: mypy incorrectly flags
  comparison with Protocol, but at runtime we need this check.
"""

import inspect
from typing import Protocol, cast

import pytest

from omnibase_spi.protocols.event_bus.protocol_event_bus_extended import (
    ProtocolEventBusBatchProducer,
    ProtocolEventBusConsumer,
    ProtocolEventBusExtendedClient,
    ProtocolEventBusMessage,
    ProtocolEventBusTransactionalProducer,
)
from omnibase_spi.protocols.event_bus.protocol_event_bus_types import (
    ProtocolTopicConfig,
)


# =============================================================================
# Mock/Compliant Implementations for Testing
# =============================================================================


class CompliantEventBusConsumer:
    """Test double implementing all ProtocolEventBusConsumer requirements.

    This mock provides a complete consumer implementation for protocol testing.
    All async methods are no-ops since we're only testing protocol compliance.
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


class CompliantEventBusBatchProducer:
    """Test double implementing all ProtocolEventBusBatchProducer requirements.

    This mock provides a complete batch producer implementation for protocol testing.
    All async methods are no-ops since we're only testing protocol compliance.
    """

    async def send_batch(self, messages: list[ProtocolEventBusMessage]) -> None:
        """Send a batch of messages."""
        _ = messages  # Unused in mock

    async def send_to_partition(
        self,
        topic: str,
        partition: int,
        key: bytes | None,
        value: bytes,
        headers: dict[str, bytes] | None = None,
    ) -> None:
        """Send a message to a specific partition."""
        _ = (topic, partition, key, value, headers)  # Unused in mock

    async def send_with_custom_partitioner(
        self,
        topic: str,
        key: bytes | None,
        value: bytes,
        partition_strategy: str,
        headers: dict[str, bytes] | None = None,
    ) -> None:
        """Send a message using a custom partitioning strategy."""
        _ = (topic, key, value, partition_strategy, headers)  # Unused in mock

    async def flush_pending(self, timeout_ms: int) -> None:
        """Flush all pending messages."""
        _ = timeout_ms  # Unused in mock

    async def get_batch_metrics(self) -> dict[str, int]:
        """Get metrics for batch producer operations."""
        return {"messages_sent": 100, "bytes_sent": 50000, "errors_count": 0}

    async def validate_connection(self) -> bool:
        """Validate the connection."""
        return True

    async def validate_message(self, message: ProtocolEventBusMessage) -> bool:
        """Validate a message before publishing."""
        _ = message  # Unused in mock
        return True


class CompliantEventBusTransactionalProducer:
    """Test double implementing all ProtocolEventBusTransactionalProducer requirements.

    This mock provides a complete transactional producer implementation for protocol
    testing. Supports the full transaction lifecycle: init -> begin -> send -> commit/abort.
    """

    async def init_transactions(self, transaction_id: str) -> None:
        """Initialize the transactional producer."""
        _ = transaction_id  # Unused in mock

    async def begin_transaction(self) -> None:
        """Begin a new transaction."""
        pass

    async def send_transactional(
        self,
        topic: str,
        value: bytes,
        key: bytes | None = None,
        headers: dict[str, bytes] | None = None,
    ) -> None:
        """Send a message as part of the current transaction."""
        _ = (topic, value, key, headers)  # Unused in mock

    async def commit_transaction(self) -> None:
        """Commit the current transaction."""
        pass

    async def abort_transaction(self) -> None:
        """Abort the current transaction."""
        pass


class CompliantEventBusMessage:
    """Test double implementing all ProtocolEventBusMessage attribute requirements.

    This mock provides a data container satisfying the message protocol,
    with validation logic to ensure proper message construction.
    """

    def __init__(
        self,
        value: bytes = b'{"test": "data"}',
        topic: str = "test-topic",
        key: bytes | None = b"test-key",
        partition: int | None = 0,
        offset: int | None = 100,
        timestamp: int | None = 1699999999,
        headers: dict[str, bytes] | None = None,
    ) -> None:
        """Initialize a compliant EventBus message with validation."""
        if not isinstance(value, bytes):
            raise TypeError("value must be bytes")
        if not topic or not isinstance(topic, str):
            raise ValueError("topic must be a non-empty string")
        if partition is not None and partition < 0:
            raise ValueError("partition must be non-negative")
        if offset is not None and offset < 0:
            raise ValueError("offset must be non-negative")

        self.key = key
        self.value = value
        self.topic = topic
        self.partition = partition
        self.offset = offset
        self.timestamp = timestamp
        self.headers: dict[str, bytes] = headers if headers is not None else {}


class CompliantEventBusExtendedClient:
    """Test double implementing all ProtocolEventBusExtendedClient requirements.

    This mock provides a comprehensive client implementation combining:
    - Factory methods for creating consumers and producers
    - Admin operations for topic management
    - Health and validation methods

    The cast() calls in factory methods are necessary because the mock implementations
    don't explicitly inherit from protocols, but they structurally satisfy them.
    """

    async def create_consumer(self) -> ProtocolEventBusConsumer:
        """Create a new consumer instance."""
        # Cast is safe: CompliantEventBusConsumer implements all ProtocolEventBusConsumer methods
        return cast(ProtocolEventBusConsumer, CompliantEventBusConsumer())

    async def create_batch_producer(self) -> ProtocolEventBusBatchProducer:
        """Create a new batch producer instance."""
        # Cast is safe: CompliantEventBusBatchProducer implements all protocol methods
        return cast(ProtocolEventBusBatchProducer, CompliantEventBusBatchProducer())

    async def create_transactional_producer(
        self,
    ) -> ProtocolEventBusTransactionalProducer:
        """Create a new transactional producer instance."""
        # Cast is safe: CompliantEventBusTransactionalProducer implements all protocol methods
        return cast(
            ProtocolEventBusTransactionalProducer,
            CompliantEventBusTransactionalProducer(),
        )

    async def create_topic(
        self,
        topic_name: str,
        partitions: int,
        replication_factor: int,
        topic_config: ProtocolTopicConfig | None = None,
    ) -> None:
        """Create a new topic."""
        _ = (topic_name, partitions, replication_factor, topic_config)  # Unused in mock

    async def delete_topic(self, topic_name: str) -> None:
        """Delete a topic."""
        _ = topic_name  # Unused in mock

    async def list_topics(self) -> list[str]:
        """List all topics."""
        return ["topic-1", "topic-2"]

    async def get_topic_metadata(self, topic_name: str) -> dict[str, str | int]:
        """Get topic metadata."""
        _ = topic_name  # Unused in mock
        return {"partitions": 3, "replication_factor": 2}

    async def health_check(self) -> bool:
        """Check connection health."""
        return True

    async def validate_connection(self) -> bool:
        """Validate the connection."""
        return True

    async def validate_message(self, message: ProtocolEventBusMessage) -> bool:
        """Validate a message before publishing."""
        _ = message  # Unused in mock
        return True

    async def close_client(self, timeout_seconds: float = 30.0) -> None:
        """Close the client."""
        _ = timeout_seconds  # Unused in mock


class PartialEventBusExtendedClient:
    """Test double implementing only SOME ProtocolEventBusExtendedClient methods.

    Missing methods (intentionally):
        - create_batch_producer
        - create_transactional_producer
        - create_topic
        - delete_topic
        - get_topic_metadata
        - health_check
        - validate_connection
        - validate_message
        - close_client

    Used by: test_partial_implementation_fails_isinstance
    """

    async def create_consumer(self) -> ProtocolEventBusConsumer:
        """Create a new consumer instance."""
        # Cast is safe: CompliantEventBusConsumer implements all ProtocolEventBusConsumer methods
        return cast(ProtocolEventBusConsumer, CompliantEventBusConsumer())

    async def list_topics(self) -> list[str]:
        """List all topics."""
        return []


# =============================================================================
# Pytest Fixtures
# =============================================================================


@pytest.fixture
def compliant_extended_client() -> CompliantEventBusExtendedClient:
    """Provide a compliant extended client for protocol compliance testing.

    Returns:
        A fresh CompliantEventBusExtendedClient instance implementing all
        ProtocolEventBusExtendedClient requirements.
    """
    return CompliantEventBusExtendedClient()


# =============================================================================
# Test Classes
# =============================================================================


class TestProtocolEventBusExtendedClientProtocol:
    """Test suite for ProtocolEventBusExtendedClient protocol compliance."""

    def test_protocol_is_runtime_checkable(self) -> None:
        """ProtocolEventBusExtendedClient should be runtime_checkable."""
        assert hasattr(
            ProtocolEventBusExtendedClient, "_is_runtime_protocol"
        ) or hasattr(ProtocolEventBusExtendedClient, "__runtime_protocol__")

    def test_protocol_is_protocol(self) -> None:
        """ProtocolEventBusExtendedClient should be a Protocol class."""
        assert any(
            base is Protocol or base.__name__ == "Protocol"  # type: ignore[comparison-overlap]
            for base in ProtocolEventBusExtendedClient.__mro__
        )

    def test_protocol_has_create_consumer_method(self) -> None:
        """Should define create_consumer method."""
        assert "create_consumer" in dir(ProtocolEventBusExtendedClient)

    def test_protocol_has_create_batch_producer_method(self) -> None:
        """Should define create_batch_producer method."""
        assert "create_batch_producer" in dir(ProtocolEventBusExtendedClient)

    def test_protocol_has_create_transactional_producer_method(self) -> None:
        """Should define create_transactional_producer method."""
        assert "create_transactional_producer" in dir(ProtocolEventBusExtendedClient)

    def test_protocol_has_create_topic_method(self) -> None:
        """Should define create_topic method."""
        assert "create_topic" in dir(ProtocolEventBusExtendedClient)

    def test_protocol_has_delete_topic_method(self) -> None:
        """Should define delete_topic method."""
        assert "delete_topic" in dir(ProtocolEventBusExtendedClient)

    def test_protocol_has_list_topics_method(self) -> None:
        """Should define list_topics method."""
        assert "list_topics" in dir(ProtocolEventBusExtendedClient)

    def test_protocol_has_get_topic_metadata_method(self) -> None:
        """Should define get_topic_metadata method."""
        assert "get_topic_metadata" in dir(ProtocolEventBusExtendedClient)

    def test_protocol_has_health_check_method(self) -> None:
        """Should define health_check method."""
        assert "health_check" in dir(ProtocolEventBusExtendedClient)

    def test_protocol_has_validate_connection_method(self) -> None:
        """Should define validate_connection method."""
        assert "validate_connection" in dir(ProtocolEventBusExtendedClient)

    def test_protocol_has_validate_message_method(self) -> None:
        """Should define validate_message method."""
        assert "validate_message" in dir(ProtocolEventBusExtendedClient)

    def test_protocol_has_close_client_method(self) -> None:
        """Should define close_client method."""
        assert "close_client" in dir(ProtocolEventBusExtendedClient)

    def test_protocol_cannot_be_instantiated(self) -> None:
        """ProtocolEventBusExtendedClient should not be directly instantiable."""
        with pytest.raises(TypeError):
            # Intentionally testing that Protocol cannot be instantiated
            ProtocolEventBusExtendedClient()  # type: ignore[misc]


class TestProtocolEventBusExtendedClientCompliance:
    """Test isinstance checks for ProtocolEventBusExtendedClient compliance."""

    def test_compliant_class_passes_isinstance(
        self, compliant_extended_client: CompliantEventBusExtendedClient
    ) -> None:
        """A class implementing all methods should pass isinstance check."""
        assert isinstance(compliant_extended_client, ProtocolEventBusExtendedClient)

    def test_partial_implementation_fails_isinstance(self) -> None:
        """A class missing methods should fail isinstance check."""
        client = PartialEventBusExtendedClient()
        assert not isinstance(client, ProtocolEventBusExtendedClient)


class TestProtocolEventBusExtendedClientMethodSignatures:
    """Test method signatures for ProtocolEventBusExtendedClient."""

    @pytest.mark.asyncio
    async def test_create_consumer_returns_consumer(
        self, compliant_extended_client: CompliantEventBusExtendedClient
    ) -> None:
        """create_consumer should return a ProtocolEventBusConsumer."""
        consumer = await compliant_extended_client.create_consumer()
        assert isinstance(consumer, ProtocolEventBusConsumer)

    @pytest.mark.asyncio
    async def test_create_batch_producer_returns_producer(
        self, compliant_extended_client: CompliantEventBusExtendedClient
    ) -> None:
        """create_batch_producer should return a ProtocolEventBusBatchProducer."""
        producer = await compliant_extended_client.create_batch_producer()
        assert isinstance(producer, ProtocolEventBusBatchProducer)

    @pytest.mark.asyncio
    async def test_create_transactional_producer_returns_producer(
        self, compliant_extended_client: CompliantEventBusExtendedClient
    ) -> None:
        """create_transactional_producer returns ProtocolEventBusTransactionalProducer."""
        producer = await compliant_extended_client.create_transactional_producer()
        assert isinstance(producer, ProtocolEventBusTransactionalProducer)

    @pytest.mark.asyncio
    async def test_create_topic_accepts_all_params(
        self, compliant_extended_client: CompliantEventBusExtendedClient
    ) -> None:
        """create_topic should accept topic_name, partitions, replication_factor."""
        await compliant_extended_client.create_topic(
            topic_name="test-topic",
            partitions=3,
            replication_factor=2,
        )

    @pytest.mark.asyncio
    async def test_list_topics_returns_list(
        self, compliant_extended_client: CompliantEventBusExtendedClient
    ) -> None:
        """list_topics should return a list of strings."""
        topics = await compliant_extended_client.list_topics()
        assert isinstance(topics, list)
        assert all(isinstance(t, str) for t in topics)

    @pytest.mark.asyncio
    async def test_get_topic_metadata_returns_dict(
        self, compliant_extended_client: CompliantEventBusExtendedClient
    ) -> None:
        """get_topic_metadata should return a dict."""
        metadata = await compliant_extended_client.get_topic_metadata("test-topic")
        assert isinstance(metadata, dict)

    @pytest.mark.asyncio
    async def test_health_check_returns_bool(
        self, compliant_extended_client: CompliantEventBusExtendedClient
    ) -> None:
        """health_check should return a boolean."""
        result = await compliant_extended_client.health_check()
        assert isinstance(result, bool)

    @pytest.mark.asyncio
    async def test_close_client_accepts_timeout(
        self, compliant_extended_client: CompliantEventBusExtendedClient
    ) -> None:
        """close_client should accept optional timeout parameter."""
        await compliant_extended_client.close_client()  # Default timeout
        await compliant_extended_client.close_client(timeout_seconds=10.0)  # Custom timeout


class TestProtocolEventBusExtendedClientAsyncNature:
    """Test that ProtocolEventBusExtendedClient methods are async."""

    def test_create_consumer_is_async(self) -> None:
        """create_consumer should be async in both protocol and implementation."""
        # Check protocol defines async signature
        protocol_method = getattr(ProtocolEventBusExtendedClient, "create_consumer", None)
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)
        # Check compliant implementation is async
        assert inspect.iscoroutinefunction(
            CompliantEventBusExtendedClient.create_consumer
        )

    def test_create_batch_producer_is_async(self) -> None:
        """create_batch_producer should be async in both protocol and implementation."""
        # Check protocol defines async signature
        protocol_method = getattr(
            ProtocolEventBusExtendedClient, "create_batch_producer", None
        )
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)
        # Check compliant implementation is async
        assert inspect.iscoroutinefunction(
            CompliantEventBusExtendedClient.create_batch_producer
        )

    def test_create_topic_is_async(self) -> None:
        """create_topic should be async in both protocol and implementation."""
        # Check protocol defines async signature
        protocol_method = getattr(ProtocolEventBusExtendedClient, "create_topic", None)
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)
        # Check compliant implementation is async
        assert inspect.iscoroutinefunction(
            CompliantEventBusExtendedClient.create_topic
        )

    def test_list_topics_is_async(self) -> None:
        """list_topics should be async in both protocol and implementation."""
        # Check protocol defines async signature
        protocol_method = getattr(ProtocolEventBusExtendedClient, "list_topics", None)
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)
        # Check compliant implementation is async
        assert inspect.iscoroutinefunction(
            CompliantEventBusExtendedClient.list_topics
        )

    def test_health_check_is_async(self) -> None:
        """health_check should be async in both protocol and implementation."""
        # Check protocol defines async signature
        protocol_method = getattr(ProtocolEventBusExtendedClient, "health_check", None)
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)
        # Check compliant implementation is async
        assert inspect.iscoroutinefunction(
            CompliantEventBusExtendedClient.health_check
        )

    def test_create_transactional_producer_is_async(self) -> None:
        """create_transactional_producer should be async in both protocol and implementation."""
        # Check protocol defines async signature
        protocol_method = getattr(
            ProtocolEventBusExtendedClient, "create_transactional_producer", None
        )
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)
        # Check compliant implementation is async
        assert inspect.iscoroutinefunction(
            CompliantEventBusExtendedClient.create_transactional_producer
        )

    def test_delete_topic_is_async(self) -> None:
        """delete_topic should be async in both protocol and implementation."""
        # Check protocol defines async signature
        protocol_method = getattr(ProtocolEventBusExtendedClient, "delete_topic", None)
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)
        # Check compliant implementation is async
        assert inspect.iscoroutinefunction(
            CompliantEventBusExtendedClient.delete_topic
        )

    def test_get_topic_metadata_is_async(self) -> None:
        """get_topic_metadata should be async in both protocol and implementation."""
        # Check protocol defines async signature
        protocol_method = getattr(
            ProtocolEventBusExtendedClient, "get_topic_metadata", None
        )
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)
        # Check compliant implementation is async
        assert inspect.iscoroutinefunction(
            CompliantEventBusExtendedClient.get_topic_metadata
        )

    def test_validate_connection_is_async(self) -> None:
        """validate_connection should be async in both protocol and implementation."""
        # Check protocol defines async signature
        protocol_method = getattr(
            ProtocolEventBusExtendedClient, "validate_connection", None
        )
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)
        # Check compliant implementation is async
        assert inspect.iscoroutinefunction(
            CompliantEventBusExtendedClient.validate_connection
        )

    def test_validate_message_is_async(self) -> None:
        """validate_message should be async in both protocol and implementation."""
        # Check protocol defines async signature
        protocol_method = getattr(
            ProtocolEventBusExtendedClient, "validate_message", None
        )
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)
        # Check compliant implementation is async
        assert inspect.iscoroutinefunction(
            CompliantEventBusExtendedClient.validate_message
        )

    def test_close_client_is_async(self) -> None:
        """close_client should be async in both protocol and implementation."""
        # Check protocol defines async signature
        protocol_method = getattr(ProtocolEventBusExtendedClient, "close_client", None)
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)
        # Check compliant implementation is async
        assert inspect.iscoroutinefunction(
            CompliantEventBusExtendedClient.close_client
        )


class TestProtocolEventBusExtendedClientEdgeCases:
    """Test edge cases for extended client."""

    @pytest.mark.asyncio
    async def test_create_topic_with_single_partition(self) -> None:
        """Creating topic with single partition should work."""
        client = CompliantEventBusExtendedClient()
        await client.create_topic(
            topic_name="single-partition",
            partitions=1,
            replication_factor=1,
        )

    @pytest.mark.asyncio
    async def test_create_topic_with_many_partitions(self) -> None:
        """Creating topic with many partitions should work."""
        client = CompliantEventBusExtendedClient()
        await client.create_topic(
            topic_name="many-partitions",
            partitions=100,
            replication_factor=3,
        )

    @pytest.mark.asyncio
    async def test_close_client_with_zero_timeout(self) -> None:
        """Close client with zero timeout should work."""
        client = CompliantEventBusExtendedClient()
        await client.close_client(timeout_seconds=0.0)

    @pytest.mark.asyncio
    async def test_validate_compliant_message(self) -> None:
        """Validate a compliant message should return True."""
        client = CompliantEventBusExtendedClient()
        msg = CompliantEventBusMessage(value=b"data", topic="test")
        result = await client.validate_message(cast(ProtocolEventBusMessage, msg))
        assert result is True

    @pytest.mark.asyncio
    async def test_create_topic_with_config(self) -> None:
        """Creating topic with optional config should work."""
        client = CompliantEventBusExtendedClient()
        await client.create_topic(
            topic_name="configured-topic",
            partitions=3,
            replication_factor=1,
            topic_config=None,  # Config is optional
        )

    @pytest.mark.asyncio
    async def test_delete_topic_accepts_topic_name(self) -> None:
        """delete_topic should accept topic name."""
        client = CompliantEventBusExtendedClient()
        await client.delete_topic("test-topic")

    @pytest.mark.asyncio
    async def test_list_topics_returns_non_empty_list(self) -> None:
        """list_topics from mock should return non-empty list."""
        client = CompliantEventBusExtendedClient()
        topics = await client.list_topics()
        assert len(topics) >= 1

    @pytest.mark.asyncio
    async def test_get_topic_metadata_returns_expected_keys(self) -> None:
        """get_topic_metadata should return dict with expected keys."""
        client = CompliantEventBusExtendedClient()
        metadata = await client.get_topic_metadata("test-topic")
        assert "partitions" in metadata
        assert "replication_factor" in metadata

    @pytest.mark.asyncio
    async def test_health_check_returns_true_for_compliant_mock(self) -> None:
        """health_check from compliant mock should return True."""
        client = CompliantEventBusExtendedClient()
        result = await client.health_check()
        assert result is True

    @pytest.mark.asyncio
    async def test_validate_connection_returns_true_for_compliant_mock(self) -> None:
        """validate_connection from compliant mock should return True."""
        client = CompliantEventBusExtendedClient()
        result = await client.validate_connection()
        assert result is True


class TestProtocolEventBusExtendedClientIntegration:
    """Integration tests for ProtocolEventBusExtendedClient.

    These tests verify that the extended client works correctly
    in combination with other protocols it creates.
    """

    @pytest.mark.asyncio
    async def test_extended_client_creates_compliant_consumer(self) -> None:
        """ExtendedClient.create_consumer returns protocol-compliant consumer."""
        client = CompliantEventBusExtendedClient()
        consumer = await client.create_consumer()

        # Verify returned consumer is protocol compliant
        assert isinstance(consumer, ProtocolEventBusConsumer)

        # Verify consumer is functional
        is_connected = await consumer.validate_connection()
        assert isinstance(is_connected, bool)

    @pytest.mark.asyncio
    async def test_extended_client_creates_compliant_batch_producer(self) -> None:
        """ExtendedClient.create_batch_producer returns protocol-compliant producer."""
        client = CompliantEventBusExtendedClient()
        producer = await client.create_batch_producer()

        # Verify returned producer is protocol compliant
        assert isinstance(producer, ProtocolEventBusBatchProducer)

        # Verify producer is functional
        is_connected = await producer.validate_connection()
        assert isinstance(is_connected, bool)

    @pytest.mark.asyncio
    async def test_extended_client_creates_compliant_transactional_producer(self) -> None:
        """ExtendedClient.create_transactional_producer returns compliant producer."""
        client = CompliantEventBusExtendedClient()
        producer = await client.create_transactional_producer()

        # Verify returned producer is protocol compliant
        assert isinstance(producer, ProtocolEventBusTransactionalProducer)

    @pytest.mark.asyncio
    async def test_extended_client_topic_management_workflow(self) -> None:
        """Test topic management workflow: create -> list -> metadata -> delete."""
        client = CompliantEventBusExtendedClient()

        # Create topic
        await client.create_topic(
            topic_name="integration-test-topic",
            partitions=3,
            replication_factor=1,
        )

        # List topics
        topics = await client.list_topics()
        assert isinstance(topics, list)

        # Get metadata
        metadata = await client.get_topic_metadata("integration-test-topic")
        assert isinstance(metadata, dict)

        # Delete topic
        await client.delete_topic("integration-test-topic")

        # Close client
        await client.close_client()

    @pytest.mark.asyncio
    async def test_extended_client_full_lifecycle(self) -> None:
        """Test extended client creating consumer and producer."""
        client = CompliantEventBusExtendedClient()

        # Create consumer
        consumer = await client.create_consumer()
        assert isinstance(consumer, ProtocolEventBusConsumer)

        # Create batch producer
        producer = await client.create_batch_producer()
        assert isinstance(producer, ProtocolEventBusBatchProducer)

        # Health check
        healthy = await client.health_check()
        assert isinstance(healthy, bool)

        # Close
        await client.close_client()

    @pytest.mark.asyncio
    async def test_extended_client_consumer_full_workflow(self) -> None:
        """ExtendedClient creates Consumer that can perform full workflow."""
        client = CompliantEventBusExtendedClient()

        # Create consumer via extended client
        consumer = await client.create_consumer()
        assert isinstance(consumer, ProtocolEventBusConsumer)

        # Perform full consumer workflow
        await consumer.subscribe_to_topics(["topic-1", "topic-2"], "test-group")
        messages = await consumer.consume_messages(timeout_ms=100, max_messages=10)
        assert isinstance(messages, list)
        await consumer.commit_offsets()
        offsets = await consumer.get_current_offsets()
        assert isinstance(offsets, dict)
        await consumer.close_consumer()

        # Close extended client
        await client.close_client()

    @pytest.mark.asyncio
    async def test_extended_client_batch_producer_full_workflow(self) -> None:
        """ExtendedClient creates BatchProducer that can perform full workflow."""
        client = CompliantEventBusExtendedClient()

        # Create batch producer via extended client
        producer = await client.create_batch_producer()
        assert isinstance(producer, ProtocolEventBusBatchProducer)

        # Perform full producer workflow
        is_connected = await producer.validate_connection()
        assert is_connected

        # Create and validate message
        msg = CompliantEventBusMessage(value=b"test-data", topic="test-topic")
        is_valid = await producer.validate_message(cast(ProtocolEventBusMessage, msg))
        assert is_valid

        # Send operations
        await producer.send_batch([cast(ProtocolEventBusMessage, msg)])
        await producer.send_to_partition("test", 0, b"key", b"value")
        await producer.send_with_custom_partitioner(
            "test", b"key", b"value", "round_robin"
        )
        await producer.flush_pending(timeout_ms=1000)

        # Get metrics
        metrics = await producer.get_batch_metrics()
        assert "messages_sent" in metrics

        # Close extended client
        await client.close_client()

    @pytest.mark.asyncio
    async def test_extended_client_transactional_producer_full_workflow(self) -> None:
        """ExtendedClient creates TransactionalProducer for full workflow."""
        client = CompliantEventBusExtendedClient()

        # Create transactional producer via extended client
        producer = await client.create_transactional_producer()
        assert isinstance(producer, ProtocolEventBusTransactionalProducer)

        # Perform full transactional workflow
        await producer.init_transactions("integration-tx")
        await producer.begin_transaction()
        await producer.send_transactional(
            "test-topic",
            b'{"event": "test"}',
            key=b"key",
            headers={"correlation_id": b"123"},
        )
        await producer.commit_transaction()

        # Close extended client
        await client.close_client()


class TestProtocolEventBusExtendedClientErrorHandling:
    """Test error handling for extended client.

    These tests verify error-raising mock implementations work correctly
    and that error propagation patterns are sound.
    """

    @pytest.mark.asyncio
    async def test_error_raising_extended_client(self) -> None:
        """Test that error-raising mock can be created and raises expected errors."""
        # Create a simple error-raising variant inline
        class ErrorRaisingClient:
            """Extended client that raises errors for testing."""

            def __init__(self, error: Exception) -> None:
                self._error = error

            async def create_consumer(self) -> ProtocolEventBusConsumer:
                raise self._error

            async def create_batch_producer(self) -> ProtocolEventBusBatchProducer:
                return cast(ProtocolEventBusBatchProducer, CompliantEventBusBatchProducer())

            async def create_transactional_producer(self) -> ProtocolEventBusTransactionalProducer:
                return cast(
                    ProtocolEventBusTransactionalProducer,
                    CompliantEventBusTransactionalProducer(),
                )

            async def create_topic(
                self,
                topic_name: str,
                partitions: int,
                replication_factor: int,
                topic_config: ProtocolTopicConfig | None = None,
            ) -> None:
                _ = (topic_name, partitions, replication_factor, topic_config)

            async def delete_topic(self, topic_name: str) -> None:
                _ = topic_name

            async def list_topics(self) -> list[str]:
                return []

            async def get_topic_metadata(self, topic_name: str) -> dict[str, str | int]:
                _ = topic_name
                return {}

            async def health_check(self) -> bool:
                return True

            async def validate_connection(self) -> bool:
                return True

            async def validate_message(self, message: ProtocolEventBusMessage) -> bool:
                _ = message
                return True

            async def close_client(self, timeout_seconds: float = 30.0) -> None:
                _ = timeout_seconds

        error = RuntimeError("Failed to create consumer")
        client = ErrorRaisingClient(error)

        with pytest.raises(RuntimeError, match="Failed to create consumer"):
            await client.create_consumer()

    @pytest.mark.asyncio
    async def test_error_with_isinstance_check(self) -> None:
        """Verify error-raising mocks still pass isinstance checks."""
        # The compliant mock should still pass isinstance after errors elsewhere
        client = CompliantEventBusExtendedClient()
        assert isinstance(client, ProtocolEventBusExtendedClient)
