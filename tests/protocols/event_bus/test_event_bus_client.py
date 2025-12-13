"""
Tests for EventBus client protocol compliance.

Validates that EventBus protocols:
- Are properly runtime checkable
- Define required methods with correct signatures
- Cannot be instantiated directly
- Work correctly with isinstance checks for compliant/non-compliant classes

Key protocols tested:
- ProtocolEventBusClient: Core event bus producer operations
- ProtocolEventBusClientProvider: Factory for creating clients
- ProtocolEventBusConsumer: Consumer operations and offset management
- ProtocolEventBusBatchProducer: Batch producer operations
- ProtocolEventBusExtendedClient: Comprehensive client with admin operations
- ProtocolEventBusMessage: Message data structure
- ProtocolEventBusTransactionalProducer: Transactional producer operations
"""

import inspect
from typing import Any, Protocol

import pytest

from omnibase_spi.protocols.event_bus.protocol_event_bus_client import (
    ProtocolEventBusClient,
    ProtocolEventBusClientProvider,
)
from omnibase_spi.protocols.event_bus.protocol_event_bus_extended import (
    ProtocolEventBusBatchProducer,
    ProtocolEventBusConsumer,
    ProtocolEventBusExtendedClient,
    ProtocolEventBusMessage,
    ProtocolEventBusTransactionalProducer,
)

# =============================================================================
# Mock/Compliant Implementations for Testing
# =============================================================================


class CompliantEventBusClient:
    """A class that fully implements the ProtocolEventBusClient protocol."""

    async def start(self) -> None:
        """Start the EventBus client."""
        pass

    async def stop(self, timeout_seconds: float = 30.0) -> None:
        """Stop the EventBus client."""
        _ = timeout_seconds

    async def send_and_wait(
        self, topic: str, value: bytes, key: bytes | None = None
    ) -> None:
        """Send a message and wait for acknowledgment."""
        _ = topic, value, key

    def bootstrap_servers(self) -> list[str]:
        """Get bootstrap servers."""
        return ["localhost:9092"]

    async def validate_connection(self) -> bool:
        """Validate the connection."""
        return True

    async def validate_message(
        self, topic: str, value: bytes, key: bytes | None = None
    ) -> bool:
        """Validate a message before publishing."""
        _ = topic, value, key
        return True


class PartialEventBusClient:
    """A class that only implements some ProtocolEventBusClient methods."""

    async def start(self) -> None:
        """Start the EventBus client."""
        pass

    async def stop(self, timeout_seconds: float = 30.0) -> None:
        """Stop the EventBus client."""
        _ = timeout_seconds


class NonCompliantEventBusClient:
    """A class that implements none of the ProtocolEventBusClient methods."""

    pass


class CompliantEventBusClientProvider:
    """A class that fully implements the ProtocolEventBusClientProvider protocol."""

    async def create_event_bus_client(self) -> ProtocolEventBusClient:
        """Create a new EventBus client instance."""
        return CompliantEventBusClient()  # type: ignore[return-value]

    async def get_event_bus_configuration(self) -> dict[str, str | int | float | bool]:
        """Retrieve EventBus client configuration parameters."""
        return {"bootstrap_servers": "localhost:9092", "client_id": "test-client"}


class PartialEventBusClientProvider:
    """A class missing some ProtocolEventBusClientProvider methods."""

    async def create_event_bus_client(self) -> ProtocolEventBusClient:
        """Create a new EventBus client instance."""
        return CompliantEventBusClient()  # type: ignore[return-value]


class CompliantEventBusMessage:
    """A class that implements the ProtocolEventBusMessage protocol."""

    key: bytes | None = b"test-key"
    value: bytes = b'{"test": "data"}'
    topic: str = "test-topic"
    partition: int | None = 0
    offset: int | None = 100
    timestamp: int | None = 1699999999
    headers: dict[str, bytes] | None = None

    def __init__(self) -> None:
        self.headers = {}


class PartialEventBusMessage:
    """A class missing required attributes from ProtocolEventBusMessage."""

    key: bytes | None = b"test-key"
    value: bytes = b'{"test": "data"}'
    topic: str = "test-topic"
    # Missing: partition, offset, timestamp, headers


class CompliantEventBusConsumer:
    """A class that fully implements the ProtocolEventBusConsumer protocol."""

    async def subscribe_to_topics(self, topics: list[str], group_id: str) -> None:
        """Subscribe to topics."""
        _ = topics, group_id

    async def unsubscribe_from_topics(self, topics: list[str]) -> None:
        """Unsubscribe from topics."""
        _ = topics

    async def consume_messages(
        self, timeout_ms: int, max_messages: int
    ) -> list[ProtocolEventBusMessage]:
        """Consume messages."""
        _ = timeout_ms, max_messages
        return []

    async def consume_messages_stream(
        self, batch_timeout_ms: int
    ) -> list[ProtocolEventBusMessage]:
        """Consume a batch of messages with streaming semantics."""
        _ = batch_timeout_ms
        return []

    async def commit_offsets(self) -> None:
        """Commit current consumer offsets."""
        pass

    async def seek_to_beginning(self, topic: str, partition: int) -> None:
        """Seek to the beginning of a topic partition."""
        _ = topic, partition

    async def seek_to_end(self, topic: str, partition: int) -> None:
        """Seek to the end of a topic partition."""
        _ = topic, partition

    async def seek_to_offset(self, topic: str, partition: int, offset: int) -> None:
        """Seek to a specific offset."""
        _ = topic, partition, offset

    async def get_current_offsets(self) -> dict[str, dict[int, int]]:
        """Get current consumer offsets."""
        return {"test-topic": {0: 100}}

    async def close_consumer(self, timeout_seconds: float = 30.0) -> None:
        """Close the consumer."""
        _ = timeout_seconds

    async def validate_connection(self) -> bool:
        """Validate the connection."""
        return True


class PartialEventBusConsumer:
    """A class missing required ProtocolEventBusConsumer methods."""

    async def subscribe_to_topics(self, topics: list[str], group_id: str) -> None:
        """Subscribe to topics."""
        _ = topics, group_id

    async def consume_messages(
        self, timeout_ms: int, max_messages: int
    ) -> list[ProtocolEventBusMessage]:
        """Consume messages."""
        _ = timeout_ms, max_messages
        return []


class CompliantEventBusBatchProducer:
    """A class that fully implements the ProtocolEventBusBatchProducer protocol."""

    async def send_batch(self, messages: list[ProtocolEventBusMessage]) -> None:
        """Send a batch of messages."""
        _ = messages

    async def send_to_partition(
        self,
        topic: str,
        partition: int,
        key: bytes | None,
        value: bytes,
        headers: dict[str, bytes] | None = None,
    ) -> None:
        """Send a message to a specific partition."""
        _ = topic, partition, key, value, headers

    async def send_with_custom_partitioner(
        self,
        topic: str,
        key: bytes | None,
        value: bytes,
        partition_strategy: str,
        headers: dict[str, bytes] | None = None,
    ) -> None:
        """Send a message using a custom partitioning strategy."""
        _ = topic, key, value, partition_strategy, headers

    async def flush_pending(self, timeout_ms: int) -> None:
        """Flush all pending messages."""
        _ = timeout_ms

    async def get_batch_metrics(self) -> dict[str, int]:
        """Get metrics for batch producer operations."""
        return {"messages_sent": 100, "bytes_sent": 50000, "errors_count": 0}

    async def validate_connection(self) -> bool:
        """Validate the connection."""
        return True

    async def validate_message(self, message: ProtocolEventBusMessage) -> bool:
        """Validate a message before publishing."""
        _ = message
        return True


class PartialEventBusBatchProducer:
    """A class missing required ProtocolEventBusBatchProducer methods."""

    async def send_batch(self, messages: list[ProtocolEventBusMessage]) -> None:
        """Send a batch of messages."""
        _ = messages

    async def flush_pending(self, timeout_ms: int) -> None:
        """Flush all pending messages."""
        _ = timeout_ms


class CompliantEventBusTransactionalProducer:
    """A class that implements ProtocolEventBusTransactionalProducer protocol."""

    async def init_transactions(self, transaction_id: str) -> None:
        """Initialize the transactional producer."""
        _ = transaction_id

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
        _ = topic, value, key, headers

    async def commit_transaction(self) -> None:
        """Commit the current transaction."""
        pass

    async def abort_transaction(self) -> None:
        """Abort the current transaction."""
        pass


class PartialEventBusTransactionalProducer:
    """A class missing some ProtocolEventBusTransactionalProducer methods."""

    async def begin_transaction(self) -> None:
        """Begin a new transaction."""
        pass

    async def commit_transaction(self) -> None:
        """Commit the current transaction."""
        pass


class CompliantEventBusExtendedClient:
    """A class that fully implements the ProtocolEventBusExtendedClient protocol."""

    async def create_consumer(self) -> ProtocolEventBusConsumer:
        """Create a new consumer instance."""
        return CompliantEventBusConsumer()  # type: ignore[return-value]

    async def create_batch_producer(self) -> ProtocolEventBusBatchProducer:
        """Create a new batch producer instance."""
        return CompliantEventBusBatchProducer()  # type: ignore[return-value]

    async def create_transactional_producer(
        self,
    ) -> ProtocolEventBusTransactionalProducer:
        """Create a new transactional producer instance."""
        return CompliantEventBusTransactionalProducer()  # type: ignore[return-value]

    async def create_topic(
        self,
        topic_name: str,
        partitions: int,
        replication_factor: int,
        topic_config: Any = None,
    ) -> None:
        """Create a new topic."""
        _ = topic_name, partitions, replication_factor, topic_config

    async def delete_topic(self, topic_name: str) -> None:
        """Delete a topic."""
        _ = topic_name

    async def list_topics(self) -> list[str]:
        """List all topics."""
        return ["topic-1", "topic-2"]

    async def get_topic_metadata(self, topic_name: str) -> dict[str, str | int]:
        """Get topic metadata."""
        _ = topic_name
        return {"partitions": 3, "replication_factor": 2}

    async def health_check(self) -> bool:
        """Check connection health."""
        return True

    async def validate_connection(self) -> bool:
        """Validate the connection."""
        return True

    async def validate_message(self, message: ProtocolEventBusMessage) -> bool:
        """Validate a message before publishing."""
        _ = message
        return True

    async def close_client(self, timeout_seconds: float = 30.0) -> None:
        """Close the client."""
        _ = timeout_seconds


class PartialEventBusExtendedClient:
    """A class missing required ProtocolEventBusExtendedClient methods."""

    async def create_consumer(self) -> ProtocolEventBusConsumer:
        """Create a new consumer instance."""
        return CompliantEventBusConsumer()  # type: ignore[return-value]

    async def list_topics(self) -> list[str]:
        """List all topics."""
        return []


# =============================================================================
# Test Classes
# =============================================================================


class TestProtocolEventBusClientProtocol:
    """Test suite for ProtocolEventBusClient protocol compliance."""

    def test_protocol_is_runtime_checkable(self) -> None:
        """ProtocolEventBusClient should be runtime_checkable."""
        # Python 3.11+ uses _is_runtime_protocol
        assert hasattr(ProtocolEventBusClient, "_is_runtime_protocol") or hasattr(
            ProtocolEventBusClient, "__runtime_protocol__"
        )

    def test_protocol_is_protocol(self) -> None:
        """ProtocolEventBusClient should be a Protocol class."""
        assert any(
            base is Protocol or base.__name__ == "Protocol"
            for base in ProtocolEventBusClient.__mro__
        )

    def test_protocol_has_start_method(self) -> None:
        """ProtocolEventBusClient should define start method."""
        assert "start" in dir(ProtocolEventBusClient)

    def test_protocol_has_stop_method(self) -> None:
        """ProtocolEventBusClient should define stop method."""
        assert "stop" in dir(ProtocolEventBusClient)

    def test_protocol_has_send_and_wait_method(self) -> None:
        """ProtocolEventBusClient should define send_and_wait method."""
        assert "send_and_wait" in dir(ProtocolEventBusClient)

    def test_protocol_has_bootstrap_servers_method(self) -> None:
        """ProtocolEventBusClient should define bootstrap_servers method."""
        assert "bootstrap_servers" in dir(ProtocolEventBusClient)

    def test_protocol_has_validate_connection_method(self) -> None:
        """ProtocolEventBusClient should define validate_connection method."""
        assert "validate_connection" in dir(ProtocolEventBusClient)

    def test_protocol_has_validate_message_method(self) -> None:
        """ProtocolEventBusClient should define validate_message method."""
        assert "validate_message" in dir(ProtocolEventBusClient)

    def test_protocol_cannot_be_instantiated(self) -> None:
        """ProtocolEventBusClient should not be directly instantiable."""
        with pytest.raises(TypeError):
            ProtocolEventBusClient()  # type: ignore[misc]


class TestProtocolEventBusClientCompliance:
    """Test isinstance checks for ProtocolEventBusClient protocol compliance."""

    def test_compliant_class_passes_isinstance(self) -> None:
        """A class implementing all methods should pass isinstance check."""
        client = CompliantEventBusClient()
        assert isinstance(client, ProtocolEventBusClient)

    def test_partial_implementation_fails_isinstance(self) -> None:
        """A class missing methods should fail isinstance check."""
        client = PartialEventBusClient()
        assert not isinstance(client, ProtocolEventBusClient)

    def test_non_compliant_class_fails_isinstance(self) -> None:
        """A class with no methods should fail isinstance check."""
        client = NonCompliantEventBusClient()
        assert not isinstance(client, ProtocolEventBusClient)


class TestProtocolEventBusClientMethodSignatures:
    """Test method signatures from compliant implementations."""

    @pytest.mark.asyncio
    async def test_start_takes_no_args(self) -> None:
        """start method should take no arguments."""
        client = CompliantEventBusClient()
        await client.start()  # Should not raise

    @pytest.mark.asyncio
    async def test_stop_accepts_timeout(self) -> None:
        """stop method should accept optional timeout parameter."""
        client = CompliantEventBusClient()
        await client.stop()  # Default timeout
        await client.stop(timeout_seconds=10.0)  # Custom timeout

    @pytest.mark.asyncio
    async def test_send_and_wait_accepts_required_params(self) -> None:
        """send_and_wait should accept topic and value parameters."""
        client = CompliantEventBusClient()
        await client.send_and_wait(topic="test", value=b"data")

    @pytest.mark.asyncio
    async def test_send_and_wait_accepts_optional_key(self) -> None:
        """send_and_wait should accept optional key parameter."""
        client = CompliantEventBusClient()
        await client.send_and_wait(topic="test", value=b"data", key=b"key")

    def test_bootstrap_servers_returns_list(self) -> None:
        """bootstrap_servers should return a list of strings."""
        client = CompliantEventBusClient()
        servers = client.bootstrap_servers()
        assert isinstance(servers, list)
        assert all(isinstance(s, str) for s in servers)

    @pytest.mark.asyncio
    async def test_validate_connection_returns_bool(self) -> None:
        """validate_connection should return a boolean."""
        client = CompliantEventBusClient()
        result = await client.validate_connection()
        assert isinstance(result, bool)

    @pytest.mark.asyncio
    async def test_validate_message_returns_bool(self) -> None:
        """validate_message should return a boolean."""
        client = CompliantEventBusClient()
        result = await client.validate_message(topic="test", value=b"data")
        assert isinstance(result, bool)


class TestProtocolEventBusClientAsyncNature:
    """Test that ProtocolEventBusClient methods are async."""

    def test_start_is_async(self) -> None:
        """start should be an async method in both protocol and implementation."""
        # Check protocol defines async signature
        protocol_method = getattr(ProtocolEventBusClient, "start", None)
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)
        # Check compliant implementation is async
        assert inspect.iscoroutinefunction(CompliantEventBusClient.start)

    def test_stop_is_async(self) -> None:
        """stop should be an async method in both protocol and implementation."""
        # Check protocol defines async signature
        protocol_method = getattr(ProtocolEventBusClient, "stop", None)
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)
        # Check compliant implementation is async
        assert inspect.iscoroutinefunction(CompliantEventBusClient.stop)

    def test_send_and_wait_is_async(self) -> None:
        """send_and_wait should be an async method in both protocol and implementation."""
        # Check protocol defines async signature
        protocol_method = getattr(ProtocolEventBusClient, "send_and_wait", None)
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)
        # Check compliant implementation is async
        assert inspect.iscoroutinefunction(CompliantEventBusClient.send_and_wait)

    def test_validate_connection_is_async(self) -> None:
        """validate_connection should be an async method in both protocol and implementation."""
        # Check protocol defines async signature
        protocol_method = getattr(ProtocolEventBusClient, "validate_connection", None)
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)
        # Check compliant implementation is async
        assert inspect.iscoroutinefunction(CompliantEventBusClient.validate_connection)

    def test_validate_message_is_async(self) -> None:
        """validate_message should be an async method in both protocol and implementation."""
        # Check protocol defines async signature
        protocol_method = getattr(ProtocolEventBusClient, "validate_message", None)
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)
        # Check compliant implementation is async
        assert inspect.iscoroutinefunction(CompliantEventBusClient.validate_message)

    def test_bootstrap_servers_is_sync(self) -> None:
        """bootstrap_servers should be a sync method in both protocol and implementation."""
        # Check protocol defines sync signature
        protocol_method = getattr(ProtocolEventBusClient, "bootstrap_servers", None)
        assert protocol_method is not None
        assert not inspect.iscoroutinefunction(protocol_method)
        # Check compliant implementation is sync
        assert not inspect.iscoroutinefunction(CompliantEventBusClient.bootstrap_servers)


class TestProtocolEventBusClientProviderProtocol:
    """Test suite for ProtocolEventBusClientProvider protocol compliance."""

    def test_protocol_is_runtime_checkable(self) -> None:
        """ProtocolEventBusClientProvider should be runtime_checkable."""
        assert hasattr(
            ProtocolEventBusClientProvider, "_is_runtime_protocol"
        ) or hasattr(ProtocolEventBusClientProvider, "__runtime_protocol__")

    def test_protocol_is_protocol(self) -> None:
        """ProtocolEventBusClientProvider should be a Protocol class."""
        assert any(
            base is Protocol or base.__name__ == "Protocol"
            for base in ProtocolEventBusClientProvider.__mro__
        )

    def test_protocol_has_create_event_bus_client_method(self) -> None:
        """Should define create_event_bus_client method."""
        assert "create_event_bus_client" in dir(ProtocolEventBusClientProvider)

    def test_protocol_has_get_event_bus_configuration_method(self) -> None:
        """Should define get_event_bus_configuration method."""
        assert "get_event_bus_configuration" in dir(ProtocolEventBusClientProvider)

    def test_protocol_cannot_be_instantiated(self) -> None:
        """ProtocolEventBusClientProvider should not be directly instantiable."""
        with pytest.raises(TypeError):
            ProtocolEventBusClientProvider()  # type: ignore[misc]


class TestProtocolEventBusClientProviderCompliance:
    """Test isinstance checks for ProtocolEventBusClientProvider compliance."""

    def test_compliant_class_passes_isinstance(self) -> None:
        """A class implementing all methods should pass isinstance check."""
        provider = CompliantEventBusClientProvider()
        assert isinstance(provider, ProtocolEventBusClientProvider)

    def test_partial_implementation_fails_isinstance(self) -> None:
        """A class missing methods should fail isinstance check."""
        provider = PartialEventBusClientProvider()
        assert not isinstance(provider, ProtocolEventBusClientProvider)


class TestProtocolEventBusClientProviderMethodSignatures:
    """Test method signatures for ProtocolEventBusClientProvider."""

    @pytest.mark.asyncio
    async def test_create_event_bus_client_returns_client(self) -> None:
        """create_event_bus_client should return a ProtocolEventBusClient."""
        provider = CompliantEventBusClientProvider()
        client = await provider.create_event_bus_client()
        assert isinstance(client, ProtocolEventBusClient)

    @pytest.mark.asyncio
    async def test_get_event_bus_configuration_returns_dict(self) -> None:
        """get_event_bus_configuration should return a configuration dict."""
        provider = CompliantEventBusClientProvider()
        config = await provider.get_event_bus_configuration()
        assert isinstance(config, dict)


class TestProtocolEventBusMessageProtocol:
    """Test suite for ProtocolEventBusMessage protocol compliance."""

    def test_protocol_is_runtime_checkable(self) -> None:
        """ProtocolEventBusMessage should be runtime_checkable."""
        assert hasattr(ProtocolEventBusMessage, "_is_runtime_protocol") or hasattr(
            ProtocolEventBusMessage, "__runtime_protocol__"
        )

    def test_protocol_has_key_attribute(self) -> None:
        """ProtocolEventBusMessage should define key attribute."""
        # Check protocol defines the attribute in annotations
        assert "key" in ProtocolEventBusMessage.__annotations__
        # Also verify compliant implementation has it
        assert hasattr(CompliantEventBusMessage, "key")

    def test_protocol_has_value_attribute(self) -> None:
        """ProtocolEventBusMessage should define value attribute."""
        # Check protocol defines the attribute in annotations
        assert "value" in ProtocolEventBusMessage.__annotations__
        # Also verify compliant implementation has it
        assert hasattr(CompliantEventBusMessage, "value")

    def test_protocol_has_topic_attribute(self) -> None:
        """ProtocolEventBusMessage should define topic attribute."""
        # Check protocol defines the attribute in annotations
        assert "topic" in ProtocolEventBusMessage.__annotations__
        # Also verify compliant implementation has it
        assert hasattr(CompliantEventBusMessage, "topic")

    def test_protocol_has_partition_attribute(self) -> None:
        """ProtocolEventBusMessage should define partition attribute."""
        # Check protocol defines the attribute in annotations
        assert "partition" in ProtocolEventBusMessage.__annotations__
        # Also verify compliant implementation has it
        assert hasattr(CompliantEventBusMessage, "partition")

    def test_protocol_has_offset_attribute(self) -> None:
        """ProtocolEventBusMessage should define offset attribute."""
        # Check protocol defines the attribute in annotations
        assert "offset" in ProtocolEventBusMessage.__annotations__
        # Also verify compliant implementation has it
        assert hasattr(CompliantEventBusMessage, "offset")

    def test_protocol_has_timestamp_attribute(self) -> None:
        """ProtocolEventBusMessage should define timestamp attribute."""
        # Check protocol defines the attribute in annotations
        assert "timestamp" in ProtocolEventBusMessage.__annotations__
        # Also verify compliant implementation has it
        assert hasattr(CompliantEventBusMessage, "timestamp")

    def test_protocol_has_headers_attribute(self) -> None:
        """ProtocolEventBusMessage should define headers attribute."""
        # Check protocol defines the attribute in annotations
        assert "headers" in ProtocolEventBusMessage.__annotations__
        # Also verify compliant implementation has it
        assert hasattr(CompliantEventBusMessage, "headers")

    def test_protocol_cannot_be_instantiated(self) -> None:
        """ProtocolEventBusMessage should not be directly instantiable."""
        with pytest.raises(TypeError):
            ProtocolEventBusMessage()  # type: ignore[misc]


class TestProtocolEventBusMessageCompliance:
    """Test isinstance checks for ProtocolEventBusMessage compliance."""

    def test_compliant_class_passes_isinstance(self) -> None:
        """A class implementing all attributes should pass isinstance check."""
        message = CompliantEventBusMessage()
        assert isinstance(message, ProtocolEventBusMessage)

    def test_partial_implementation_fails_isinstance(self) -> None:
        """A class missing attributes should fail isinstance check."""
        message = PartialEventBusMessage()
        assert not isinstance(message, ProtocolEventBusMessage)


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
            base is Protocol or base.__name__ == "Protocol"
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
            ProtocolEventBusConsumer()  # type: ignore[misc]


class TestProtocolEventBusConsumerCompliance:
    """Test isinstance checks for ProtocolEventBusConsumer compliance."""

    def test_compliant_class_passes_isinstance(self) -> None:
        """A class implementing all methods should pass isinstance check."""
        consumer = CompliantEventBusConsumer()
        assert isinstance(consumer, ProtocolEventBusConsumer)

    def test_partial_implementation_fails_isinstance(self) -> None:
        """A class missing methods should fail isinstance check."""
        consumer = PartialEventBusConsumer()
        assert not isinstance(consumer, ProtocolEventBusConsumer)


class TestProtocolEventBusConsumerMethodSignatures:
    """Test method signatures for ProtocolEventBusConsumer."""

    @pytest.mark.asyncio
    async def test_subscribe_to_topics_accepts_topics_and_group(self) -> None:
        """subscribe_to_topics should accept topics and group_id."""
        consumer = CompliantEventBusConsumer()
        await consumer.subscribe_to_topics(topics=["test"], group_id="group")

    @pytest.mark.asyncio
    async def test_consume_messages_accepts_timeout_and_max(self) -> None:
        """consume_messages should accept timeout_ms and max_messages."""
        consumer = CompliantEventBusConsumer()
        messages = await consumer.consume_messages(timeout_ms=1000, max_messages=100)
        assert isinstance(messages, list)

    @pytest.mark.asyncio
    async def test_consume_messages_stream_accepts_batch_timeout(self) -> None:
        """consume_messages_stream should accept batch_timeout_ms."""
        consumer = CompliantEventBusConsumer()
        messages = await consumer.consume_messages_stream(batch_timeout_ms=1000)
        assert isinstance(messages, list)

    @pytest.mark.asyncio
    async def test_get_current_offsets_returns_nested_dict(self) -> None:
        """get_current_offsets should return dict[str, dict[int, int]]."""
        consumer = CompliantEventBusConsumer()
        offsets = await consumer.get_current_offsets()
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


class TestProtocolEventBusBatchProducerProtocol:
    """Test suite for ProtocolEventBusBatchProducer protocol compliance."""

    def test_protocol_is_runtime_checkable(self) -> None:
        """ProtocolEventBusBatchProducer should be runtime_checkable."""
        assert hasattr(
            ProtocolEventBusBatchProducer, "_is_runtime_protocol"
        ) or hasattr(ProtocolEventBusBatchProducer, "__runtime_protocol__")

    def test_protocol_is_protocol(self) -> None:
        """ProtocolEventBusBatchProducer should be a Protocol class."""
        assert any(
            base is Protocol or base.__name__ == "Protocol"
            for base in ProtocolEventBusBatchProducer.__mro__
        )

    def test_protocol_has_send_batch_method(self) -> None:
        """Should define send_batch method."""
        assert "send_batch" in dir(ProtocolEventBusBatchProducer)

    def test_protocol_has_send_to_partition_method(self) -> None:
        """Should define send_to_partition method."""
        assert "send_to_partition" in dir(ProtocolEventBusBatchProducer)

    def test_protocol_has_send_with_custom_partitioner_method(self) -> None:
        """Should define send_with_custom_partitioner method."""
        assert "send_with_custom_partitioner" in dir(ProtocolEventBusBatchProducer)

    def test_protocol_has_flush_pending_method(self) -> None:
        """Should define flush_pending method."""
        assert "flush_pending" in dir(ProtocolEventBusBatchProducer)

    def test_protocol_has_get_batch_metrics_method(self) -> None:
        """Should define get_batch_metrics method."""
        assert "get_batch_metrics" in dir(ProtocolEventBusBatchProducer)

    def test_protocol_has_validate_connection_method(self) -> None:
        """Should define validate_connection method."""
        assert "validate_connection" in dir(ProtocolEventBusBatchProducer)

    def test_protocol_has_validate_message_method(self) -> None:
        """Should define validate_message method."""
        assert "validate_message" in dir(ProtocolEventBusBatchProducer)

    def test_protocol_cannot_be_instantiated(self) -> None:
        """ProtocolEventBusBatchProducer should not be directly instantiable."""
        with pytest.raises(TypeError):
            ProtocolEventBusBatchProducer()  # type: ignore[misc]


class TestProtocolEventBusBatchProducerCompliance:
    """Test isinstance checks for ProtocolEventBusBatchProducer compliance."""

    def test_compliant_class_passes_isinstance(self) -> None:
        """A class implementing all methods should pass isinstance check."""
        producer = CompliantEventBusBatchProducer()
        assert isinstance(producer, ProtocolEventBusBatchProducer)

    def test_partial_implementation_fails_isinstance(self) -> None:
        """A class missing methods should fail isinstance check."""
        producer = PartialEventBusBatchProducer()
        assert not isinstance(producer, ProtocolEventBusBatchProducer)


class TestProtocolEventBusBatchProducerMethodSignatures:
    """Test method signatures for ProtocolEventBusBatchProducer."""

    @pytest.mark.asyncio
    async def test_send_batch_accepts_message_list(self) -> None:
        """send_batch should accept a list of messages."""
        producer = CompliantEventBusBatchProducer()
        await producer.send_batch([])  # Empty list should work

    @pytest.mark.asyncio
    async def test_send_to_partition_accepts_all_params(self) -> None:
        """send_to_partition should accept topic, partition, key, value, headers."""
        producer = CompliantEventBusBatchProducer()
        await producer.send_to_partition(
            topic="test",
            partition=0,
            key=b"key",
            value=b"value",
            headers={"header": b"value"},
        )

    @pytest.mark.asyncio
    async def test_send_with_custom_partitioner_accepts_strategy(self) -> None:
        """send_with_custom_partitioner should accept partition_strategy."""
        producer = CompliantEventBusBatchProducer()
        await producer.send_with_custom_partitioner(
            topic="test",
            key=b"key",
            value=b"value",
            partition_strategy="round_robin",
        )

    @pytest.mark.asyncio
    async def test_get_batch_metrics_returns_dict(self) -> None:
        """get_batch_metrics should return dict[str, int]."""
        producer = CompliantEventBusBatchProducer()
        metrics = await producer.get_batch_metrics()
        assert isinstance(metrics, dict)
        for key, value in metrics.items():
            assert isinstance(key, str)
            assert isinstance(value, int)


class TestProtocolEventBusTransactionalProducerProtocol:
    """Test suite for ProtocolEventBusTransactionalProducer protocol compliance."""

    def test_protocol_is_runtime_checkable(self) -> None:
        """ProtocolEventBusTransactionalProducer should be runtime_checkable."""
        assert hasattr(
            ProtocolEventBusTransactionalProducer, "_is_runtime_protocol"
        ) or hasattr(ProtocolEventBusTransactionalProducer, "__runtime_protocol__")

    def test_protocol_is_protocol(self) -> None:
        """ProtocolEventBusTransactionalProducer should be a Protocol class."""
        assert any(
            base is Protocol or base.__name__ == "Protocol"
            for base in ProtocolEventBusTransactionalProducer.__mro__
        )

    def test_protocol_has_init_transactions_method(self) -> None:
        """Should define init_transactions method."""
        assert "init_transactions" in dir(ProtocolEventBusTransactionalProducer)

    def test_protocol_has_begin_transaction_method(self) -> None:
        """Should define begin_transaction method."""
        assert "begin_transaction" in dir(ProtocolEventBusTransactionalProducer)

    def test_protocol_has_send_transactional_method(self) -> None:
        """Should define send_transactional method."""
        assert "send_transactional" in dir(ProtocolEventBusTransactionalProducer)

    def test_protocol_has_commit_transaction_method(self) -> None:
        """Should define commit_transaction method."""
        assert "commit_transaction" in dir(ProtocolEventBusTransactionalProducer)

    def test_protocol_has_abort_transaction_method(self) -> None:
        """Should define abort_transaction method."""
        assert "abort_transaction" in dir(ProtocolEventBusTransactionalProducer)

    def test_protocol_cannot_be_instantiated(self) -> None:
        """ProtocolEventBusTransactionalProducer should not be directly instantiable."""
        with pytest.raises(TypeError):
            ProtocolEventBusTransactionalProducer()  # type: ignore[misc]


class TestProtocolEventBusTransactionalProducerCompliance:
    """Test isinstance checks for ProtocolEventBusTransactionalProducer compliance."""

    def test_compliant_class_passes_isinstance(self) -> None:
        """A class implementing all methods should pass isinstance check."""
        producer = CompliantEventBusTransactionalProducer()
        assert isinstance(producer, ProtocolEventBusTransactionalProducer)

    def test_partial_implementation_fails_isinstance(self) -> None:
        """A class missing methods should fail isinstance check."""
        producer = PartialEventBusTransactionalProducer()
        assert not isinstance(producer, ProtocolEventBusTransactionalProducer)


class TestProtocolEventBusTransactionalProducerMethodSignatures:
    """Test method signatures for ProtocolEventBusTransactionalProducer."""

    @pytest.mark.asyncio
    async def test_init_transactions_accepts_transaction_id(self) -> None:
        """init_transactions should accept transaction_id."""
        producer = CompliantEventBusTransactionalProducer()
        await producer.init_transactions(transaction_id="tx-1")

    @pytest.mark.asyncio
    async def test_send_transactional_accepts_all_params(self) -> None:
        """send_transactional should accept topic, value, key, headers."""
        producer = CompliantEventBusTransactionalProducer()
        await producer.send_transactional(
            topic="test",
            value=b"value",
            key=b"key",
            headers={"header": b"value"},
        )

    @pytest.mark.asyncio
    async def test_transaction_workflow(self) -> None:
        """Test complete transaction workflow."""
        producer = CompliantEventBusTransactionalProducer()
        await producer.init_transactions("tx-1")
        await producer.begin_transaction()
        await producer.send_transactional("test", b"data")
        await producer.commit_transaction()

    @pytest.mark.asyncio
    async def test_transaction_abort_workflow(self) -> None:
        """Test transaction abort workflow."""
        producer = CompliantEventBusTransactionalProducer()
        await producer.init_transactions("tx-2")
        await producer.begin_transaction()
        await producer.send_transactional("test", b"data")
        await producer.abort_transaction()


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
            base is Protocol or base.__name__ == "Protocol"
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
            ProtocolEventBusExtendedClient()  # type: ignore[misc]


class TestProtocolEventBusExtendedClientCompliance:
    """Test isinstance checks for ProtocolEventBusExtendedClient compliance."""

    def test_compliant_class_passes_isinstance(self) -> None:
        """A class implementing all methods should pass isinstance check."""
        client = CompliantEventBusExtendedClient()
        assert isinstance(client, ProtocolEventBusExtendedClient)

    def test_partial_implementation_fails_isinstance(self) -> None:
        """A class missing methods should fail isinstance check."""
        client = PartialEventBusExtendedClient()
        assert not isinstance(client, ProtocolEventBusExtendedClient)


class TestProtocolEventBusExtendedClientMethodSignatures:
    """Test method signatures for ProtocolEventBusExtendedClient."""

    @pytest.mark.asyncio
    async def test_create_consumer_returns_consumer(self) -> None:
        """create_consumer should return a ProtocolEventBusConsumer."""
        client = CompliantEventBusExtendedClient()
        consumer = await client.create_consumer()
        assert isinstance(consumer, ProtocolEventBusConsumer)

    @pytest.mark.asyncio
    async def test_create_batch_producer_returns_producer(self) -> None:
        """create_batch_producer should return a ProtocolEventBusBatchProducer."""
        client = CompliantEventBusExtendedClient()
        producer = await client.create_batch_producer()
        assert isinstance(producer, ProtocolEventBusBatchProducer)

    @pytest.mark.asyncio
    async def test_create_transactional_producer_returns_producer(self) -> None:
        """create_transactional_producer returns ProtocolEventBusTransactionalProducer."""
        client = CompliantEventBusExtendedClient()
        producer = await client.create_transactional_producer()
        assert isinstance(producer, ProtocolEventBusTransactionalProducer)

    @pytest.mark.asyncio
    async def test_create_topic_accepts_all_params(self) -> None:
        """create_topic should accept topic_name, partitions, replication_factor."""
        client = CompliantEventBusExtendedClient()
        await client.create_topic(
            topic_name="test-topic",
            partitions=3,
            replication_factor=2,
        )

    @pytest.mark.asyncio
    async def test_list_topics_returns_list(self) -> None:
        """list_topics should return a list of strings."""
        client = CompliantEventBusExtendedClient()
        topics = await client.list_topics()
        assert isinstance(topics, list)
        assert all(isinstance(t, str) for t in topics)

    @pytest.mark.asyncio
    async def test_get_topic_metadata_returns_dict(self) -> None:
        """get_topic_metadata should return a dict."""
        client = CompliantEventBusExtendedClient()
        metadata = await client.get_topic_metadata("test-topic")
        assert isinstance(metadata, dict)

    @pytest.mark.asyncio
    async def test_health_check_returns_bool(self) -> None:
        """health_check should return a boolean."""
        client = CompliantEventBusExtendedClient()
        result = await client.health_check()
        assert isinstance(result, bool)

    @pytest.mark.asyncio
    async def test_close_client_accepts_timeout(self) -> None:
        """close_client should accept optional timeout parameter."""
        client = CompliantEventBusExtendedClient()
        await client.close_client()  # Default timeout
        await client.close_client(timeout_seconds=10.0)  # Custom timeout


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


class TestProtocolImports:
    """Test protocol imports from different locations."""

    def test_import_from_client_module(self) -> None:
        """Test direct import from protocol_event_bus_client module."""
        from omnibase_spi.protocols.event_bus.protocol_event_bus_client import (
            ProtocolEventBusClient as DirectClient,
        )

        client = CompliantEventBusClient()
        assert isinstance(client, DirectClient)

    def test_import_from_extended_module(self) -> None:
        """Test direct import from protocol_event_bus_extended module."""
        from omnibase_spi.protocols.event_bus.protocol_event_bus_extended import (
            ProtocolEventBusConsumer as DirectConsumer,
        )

        consumer = CompliantEventBusConsumer()
        assert isinstance(consumer, DirectConsumer)

    def test_import_from_event_bus_package(self) -> None:
        """Test import from event_bus package __init__."""
        from omnibase_spi.protocols.event_bus import (
            ProtocolEventBusClient as PackageClient,
        )
        from omnibase_spi.protocols.event_bus import (
            ProtocolEventBusConsumer as PackageConsumer,
        )

        assert isinstance(CompliantEventBusClient(), PackageClient)
        assert isinstance(CompliantEventBusConsumer(), PackageConsumer)

    def test_imports_are_identical(self) -> None:
        """Verify imports from different locations are the same class."""
        from omnibase_spi.protocols.event_bus import (
            ProtocolEventBusClient as PackageClient,
        )
        from omnibase_spi.protocols.event_bus.protocol_event_bus_client import (
            ProtocolEventBusClient as DirectClient,
        )

        assert PackageClient is DirectClient


class TestProtocolDocumentation:
    """Test that protocols have proper documentation."""

    def test_event_bus_client_has_docstring(self) -> None:
        """ProtocolEventBusClient should have a docstring."""
        assert ProtocolEventBusClient.__doc__ is not None
        assert len(ProtocolEventBusClient.__doc__.strip()) > 0

    def test_event_bus_consumer_has_docstring(self) -> None:
        """ProtocolEventBusConsumer should have a docstring."""
        assert ProtocolEventBusConsumer.__doc__ is not None
        assert len(ProtocolEventBusConsumer.__doc__.strip()) > 0

    def test_event_bus_batch_producer_has_docstring(self) -> None:
        """ProtocolEventBusBatchProducer should have a docstring."""
        assert ProtocolEventBusBatchProducer.__doc__ is not None
        assert len(ProtocolEventBusBatchProducer.__doc__.strip()) > 0

    def test_event_bus_extended_client_has_docstring(self) -> None:
        """ProtocolEventBusExtendedClient should have a docstring."""
        assert ProtocolEventBusExtendedClient.__doc__ is not None
        assert len(ProtocolEventBusExtendedClient.__doc__.strip()) > 0

    def test_event_bus_message_has_docstring(self) -> None:
        """ProtocolEventBusMessage should have a docstring."""
        assert ProtocolEventBusMessage.__doc__ is not None
        assert len(ProtocolEventBusMessage.__doc__.strip()) > 0


class TestProtocolEventBusClientLifecycle:
    """Test lifecycle patterns for EventBus client protocols."""

    @pytest.mark.asyncio
    async def test_client_lifecycle_pattern(self) -> None:
        """Test typical client lifecycle: start, use, stop."""
        client = CompliantEventBusClient()

        # Start
        await client.start()

        # Validate connection
        is_connected = await client.validate_connection()
        assert is_connected

        # Send message
        await client.send_and_wait(topic="test", value=b"data")

        # Stop
        await client.stop()

    @pytest.mark.asyncio
    async def test_extended_client_factory_lifecycle(self) -> None:
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
    async def test_consumer_lifecycle_pattern(self) -> None:
        """Test consumer lifecycle: subscribe, consume, commit, close."""
        consumer = CompliantEventBusConsumer()

        # Subscribe
        await consumer.subscribe_to_topics(topics=["test"], group_id="test-group")

        # Consume
        messages = await consumer.consume_messages(timeout_ms=100, max_messages=10)
        assert isinstance(messages, list)

        # Commit
        await consumer.commit_offsets()

        # Get offsets
        offsets = await consumer.get_current_offsets()
        assert isinstance(offsets, dict)

        # Close
        await consumer.close_consumer()

    @pytest.mark.asyncio
    async def test_batch_producer_lifecycle_pattern(self) -> None:
        """Test batch producer lifecycle: send batch, flush, get metrics."""
        producer = CompliantEventBusBatchProducer()

        # Validate connection first
        is_connected = await producer.validate_connection()
        assert is_connected

        # Send batch (empty for this test)
        await producer.send_batch([])

        # Flush pending
        await producer.flush_pending(timeout_ms=5000)

        # Get metrics
        metrics = await producer.get_batch_metrics()
        assert isinstance(metrics, dict)
        assert "messages_sent" in metrics
