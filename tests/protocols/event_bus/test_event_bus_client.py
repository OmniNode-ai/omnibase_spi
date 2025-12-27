"""
Tests for EventBus client protocol compliance.

This module validates that EventBus protocols are correctly defined and can be
used for runtime type checking. The tests ensure that:

1. **Protocol Structure**: All protocols are properly decorated with @runtime_checkable
   and inherit from typing.Protocol.

2. **Method Signatures**: Required methods are defined with correct parameter types
   and return values.

3. **Instantiation Prevention**: Protocols cannot be directly instantiated (as expected
   for abstract protocol definitions).

4. **isinstance Checks**: Compliant implementations pass isinstance checks while
   partial or non-compliant implementations fail.

5. **Async Nature**: Async methods are properly defined as coroutines in both
   protocol definitions and compliant implementations.

Protocols Tested
----------------
- **ProtocolEventBusClient**: Core event bus producer with start/stop lifecycle,
  message sending, and connection validation.

- **ProtocolEventBusClientProvider**: Factory protocol for creating client instances
  and retrieving configuration.

- **ProtocolEventBusConsumer**: Consumer operations including topic subscription,
  message consumption, offset management, and seek operations.

- **ProtocolEventBusBatchProducer**: Batch message sending with partitioning
  strategies and metrics collection.

- **ProtocolEventBusExtendedClient**: Comprehensive client combining admin operations
  (topic management) with factory methods for consumers and producers.

- **ProtocolEventBusMessage**: Data structure protocol defining message attributes
  (key, value, topic, partition, offset, timestamp, headers).

- **ProtocolEventBusTransactionalProducer**: Transactional message production with
  begin/commit/abort transaction semantics.

Test Organization
-----------------
Tests are organized into the following categories:

1. **Protocol Tests** (TestProtocol*Protocol): Now in split files.
2. **Compliance Tests** (TestProtocol*Compliance): Now in split files.
3. **Signature Tests** (TestProtocol*MethodSignatures): Now in split files.
4. **Async Nature Tests** (TestProtocol*AsyncNature): Now in split files.
5. **Integration Tests** (TestProtocolEventBusIntegration): Here.
6. **Edge Case Tests** (Test*EdgeCases): Here and in split files.
7. **Import Tests** (TestProtocolImports): Here.
8. **Documentation Tests** (TestProtocolDocumentation): Here.
9. **Error Handling Tests** (TestErrorHandlingPaths): Here.
10. **Timeout Tests** (TestTimeoutBehavior): Here.

Testing Approach
----------------
Each protocol is tested using three types of mock implementations:

- **Compliant***: Fully implements all protocol requirements
- **Partial***: Implements only some methods (should fail isinstance)
- **NonCompliant***: Implements no methods (should fail isinstance)

This pattern ensures that runtime_checkable protocols correctly distinguish between
complete and incomplete implementations.

Note on Type Ignores
--------------------
Type ignores in this file are used in specific contexts:

- ``# type: ignore[misc]`` on protocol instantiation: Required because we're
  intentionally testing that Protocol classes raise TypeError when instantiated.
  The type checker correctly flags this as an error, but we want to verify the
  runtime behavior.

- ``# type: ignore[arg-type]`` in edge case tests: Used when intentionally passing
  invalid types to test validation logic (e.g., passing str where bytes expected).
"""

from typing import cast

import pytest

from omnibase_spi.protocols.event_bus.protocol_event_bus_client import (
    ProtocolEventBusClient,
)
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
#
# These mock implementations serve as test doubles for protocol compliance testing.
# They are intentionally minimal - providing just enough implementation to satisfy
# protocol requirements while allowing us to verify isinstance checks work correctly.
#
# Design Rationale:
# - Compliant* classes implement ALL required protocol methods/attributes
# - Partial* classes implement SOME methods (to test isinstance failure)
# - NonCompliant* classes implement NO methods (to test isinstance failure)
#
# The pattern of marking unused parameters with `_ = (param, ...)` is intentional:
# it satisfies linters while making clear the mock doesn't use these values.
# =============================================================================


class CompliantEventBusClient:
    """Test double implementing all ProtocolEventBusClient requirements.

    This mock provides a complete implementation of the ProtocolEventBusClient
    protocol, suitable for use in tests that require a compliant client instance.

    Implements:
        - start(): Async lifecycle start
        - stop(timeout_seconds): Async lifecycle stop with configurable timeout
        - send_and_wait(topic, value, key): Async message send with acknowledgment
        - bootstrap_servers(): Sync method returning server list
        - validate_connection(): Async connection validation
        - validate_message(topic, value, key): Async message validation

    All async methods are no-ops (pass/return immediately) since we're only
    testing protocol compliance, not actual EventBus behavior.
    """

    async def start(self) -> None:
        """Start the EventBus client."""
        pass

    async def stop(self, timeout_seconds: float = 30.0) -> None:
        """Stop the EventBus client."""
        _ = timeout_seconds  # Unused in mock

    async def send_and_wait(
        self, topic: str, value: bytes, key: bytes | None = None
    ) -> None:
        """Send a message and wait for acknowledgment."""
        _ = (topic, value, key)  # Unused in mock

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
        _ = (topic, value, key)  # Unused in mock
        return True


class CompliantEventBusClientProvider:
    """Test double implementing all ProtocolEventBusClientProvider requirements.

    This mock provides a factory implementation that creates compliant client
    instances, suitable for testing provider protocol compliance.

    Implements:
        - create_event_bus_client(): Creates a new ProtocolEventBusClient
        - get_event_bus_configuration(): Returns configuration dict
    """

    async def create_event_bus_client(self) -> ProtocolEventBusClient:
        """Create a new EventBus client instance."""
        # Cast is safe: CompliantEventBusClient implements all ProtocolEventBusClient methods.
        # The cast is needed because CompliantEventBusClient doesn't explicitly inherit
        # from the Protocol, but it structurally satisfies it (duck typing).
        return cast(ProtocolEventBusClient, CompliantEventBusClient())

    async def get_event_bus_configuration(self) -> dict[str, str | int | float | bool]:
        """Retrieve EventBus client configuration parameters."""
        return {"bootstrap_servers": "localhost:9092", "client_id": "test-client"}


class CompliantEventBusMessage:
    """Test double implementing all ProtocolEventBusMessage attribute requirements.

    This mock provides a data container satisfying the message protocol,
    with validation logic to ensure proper message construction.

    Attributes:
        key: Optional message key for partitioning
        value: Message payload (required, must be bytes)
        topic: Destination topic name (required, non-empty)
        partition: Target partition (optional, must be >= 0)
        offset: Message offset (optional, must be >= 0)
        timestamp: Unix timestamp in milliseconds (optional)
        headers: Message headers dictionary (defaults to {})

    The constructor performs validation to ensure messages are well-formed,
    which helps test edge cases in the validation error tests.
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
        """Initialize a compliant EventBus message with validation.

        Args:
            value: Message payload (required, must be bytes).
            topic: Topic name (must be non-empty string).
            key: Optional message key.
            partition: Optional partition number (must be >= 0 if provided).
            offset: Optional offset (must be >= 0 if provided).
            timestamp: Optional timestamp in milliseconds.
            headers: Optional headers dictionary.

        Raises:
            TypeError: If value is not bytes.
            ValueError: If topic is empty or partition/offset is negative.
        """
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


class CompliantEventBusBatchProducer:
    """Test double implementing all ProtocolEventBusBatchProducer requirements.

    This mock provides a complete batch producer implementation for protocol testing.
    All async methods are no-ops since we're only testing protocol compliance.

    Implements:
        - send_batch(messages) -> None
        - send_to_partition(topic, partition, key, value, headers) -> None
        - send_with_custom_partitioner(topic, key, value, strategy, headers) -> None
        - flush_pending(timeout_ms) -> None
        - get_batch_metrics() -> dict[str, int]
        - validate_connection() -> bool
        - validate_message(message) -> bool
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

    Implements:
        - init_transactions(transaction_id) -> None
        - begin_transaction() -> None
        - send_transactional(topic, value, key, headers) -> None
        - commit_transaction() -> None
        - abort_transaction() -> None
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


class CompliantEventBusExtendedClient:
    """Test double implementing all ProtocolEventBusExtendedClient requirements.

    This mock provides a comprehensive client implementation combining:
    - Factory methods for creating consumers and producers
    - Admin operations for topic management
    - Health and validation methods

    Implements:
        - create_consumer() -> ProtocolEventBusConsumer
        - create_batch_producer() -> ProtocolEventBusBatchProducer
        - create_transactional_producer() -> ProtocolEventBusTransactionalProducer
        - create_topic(name, partitions, replication_factor, config) -> None
        - delete_topic(name) -> None
        - list_topics() -> list[str]
        - get_topic_metadata(name) -> dict[str, str | int]
        - health_check() -> bool
        - validate_connection() -> bool
        - validate_message(message) -> bool
        - close_client(timeout_seconds) -> None

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


# =============================================================================
# Pytest Fixtures
# =============================================================================
#
# Fixtures provide pre-configured test doubles for protocol compliance testing.
# Each fixture returns a fresh instance of the corresponding compliant mock,
# ensuring test isolation.
# =============================================================================


@pytest.fixture
def compliant_client() -> CompliantEventBusClient:
    """Provide a compliant EventBus client for protocol compliance testing.

    Returns:
        A fresh CompliantEventBusClient instance implementing all
        ProtocolEventBusClient requirements.
    """
    return CompliantEventBusClient()


@pytest.fixture
def compliant_consumer() -> CompliantEventBusConsumer:
    """Provide a compliant EventBus consumer for protocol compliance testing.

    Returns:
        A fresh CompliantEventBusConsumer instance implementing all
        ProtocolEventBusConsumer requirements.
    """
    return CompliantEventBusConsumer()


@pytest.fixture
def compliant_batch_producer() -> CompliantEventBusBatchProducer:
    """Provide a compliant batch producer for protocol compliance testing.

    Returns:
        A fresh CompliantEventBusBatchProducer instance implementing all
        ProtocolEventBusBatchProducer requirements.
    """
    return CompliantEventBusBatchProducer()


@pytest.fixture
def compliant_transactional_producer() -> CompliantEventBusTransactionalProducer:
    """Provide a compliant transactional producer for protocol compliance testing.

    Returns:
        A fresh CompliantEventBusTransactionalProducer instance implementing all
        ProtocolEventBusTransactionalProducer requirements.
    """
    return CompliantEventBusTransactionalProducer()


@pytest.fixture
def compliant_extended_client() -> CompliantEventBusExtendedClient:
    """Provide a compliant extended client for protocol compliance testing.

    Returns:
        A fresh CompliantEventBusExtendedClient instance implementing all
        ProtocolEventBusExtendedClient requirements.
    """
    return CompliantEventBusExtendedClient()


@pytest.fixture
def compliant_message() -> CompliantEventBusMessage:
    """Provide a compliant EventBus message for protocol compliance testing.

    Returns:
        A fresh CompliantEventBusMessage instance with default values,
        implementing all ProtocolEventBusMessage attribute requirements.
    """
    return CompliantEventBusMessage()


@pytest.fixture
def compliant_client_provider() -> CompliantEventBusClientProvider:
    """Provide a compliant EventBus client provider for protocol compliance testing.

    Returns:
        A fresh CompliantEventBusClientProvider instance implementing all
        ProtocolEventBusClientProvider requirements.
    """
    return CompliantEventBusClientProvider()


# =============================================================================
# Test Classes - Import and Documentation Tests
# =============================================================================


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


# =============================================================================
# Test Classes - Lifecycle Tests
# =============================================================================


class TestProtocolEventBusClientLifecycle:
    """Test lifecycle patterns for EventBus client protocols."""

    @pytest.mark.asyncio
    async def test_client_lifecycle_pattern(
        self, compliant_client: CompliantEventBusClient
    ) -> None:
        """Test typical client lifecycle: start, use, stop."""
        # Start
        await compliant_client.start()

        # Validate connection
        is_connected = await compliant_client.validate_connection()
        assert is_connected

        # Send message
        await compliant_client.send_and_wait(topic="test", value=b"data")

        # Stop
        await compliant_client.stop()

    @pytest.mark.asyncio
    async def test_extended_client_factory_lifecycle(
        self, compliant_extended_client: CompliantEventBusExtendedClient
    ) -> None:
        """Test extended client creating consumer and producer."""
        # Create consumer
        consumer = await compliant_extended_client.create_consumer()
        assert isinstance(consumer, ProtocolEventBusConsumer)

        # Create batch producer
        producer = await compliant_extended_client.create_batch_producer()
        assert isinstance(producer, ProtocolEventBusBatchProducer)

        # Health check
        healthy = await compliant_extended_client.health_check()
        assert isinstance(healthy, bool)

        # Close
        await compliant_extended_client.close_client()

    @pytest.mark.asyncio
    async def test_consumer_lifecycle_pattern(
        self, compliant_consumer: CompliantEventBusConsumer
    ) -> None:
        """Test consumer lifecycle: subscribe, consume, commit, close."""
        # Subscribe
        await compliant_consumer.subscribe_to_topics(topics=["test"], group_id="test-group")

        # Consume
        messages = await compliant_consumer.consume_messages(timeout_ms=100, max_messages=10)
        assert isinstance(messages, list)

        # Commit
        await compliant_consumer.commit_offsets()

        # Get offsets
        offsets = await compliant_consumer.get_current_offsets()
        assert isinstance(offsets, dict)

        # Close
        await compliant_consumer.close_consumer()

    @pytest.mark.asyncio
    async def test_batch_producer_lifecycle_pattern(
        self, compliant_batch_producer: CompliantEventBusBatchProducer
    ) -> None:
        """Test batch producer lifecycle: send batch, flush, get metrics."""
        # Validate connection first
        is_connected = await compliant_batch_producer.validate_connection()
        assert is_connected

        # Send batch (empty for this test)
        await compliant_batch_producer.send_batch([])

        # Flush pending
        await compliant_batch_producer.flush_pending(timeout_ms=5000)

        # Get metrics
        metrics = await compliant_batch_producer.get_batch_metrics()
        assert isinstance(metrics, dict)
        assert "messages_sent" in metrics


# =============================================================================
# Integration Tests - Protocol Interactions
# =============================================================================


class TestProtocolEventBusIntegration:
    """Integration tests validating protocol interactions.

    These tests verify that protocols work together correctly,
    simulating real-world usage patterns.
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
    async def test_provider_creates_compliant_client(self) -> None:
        """ClientProvider.create_event_bus_client returns protocol-compliant client."""
        provider = CompliantEventBusClientProvider()
        client = await provider.create_event_bus_client()

        # Verify returned client is protocol compliant
        assert isinstance(client, ProtocolEventBusClient)

        # Verify client is functional
        is_connected = await client.validate_connection()
        assert isinstance(is_connected, bool)

    @pytest.mark.asyncio
    async def test_consumer_workflow_integration(self) -> None:
        """Test complete consumer workflow: subscribe -> consume -> commit -> close."""
        consumer = CompliantEventBusConsumer()

        # Subscribe
        await consumer.subscribe_to_topics(["test-topic"], "test-group")

        # Consume (mock returns empty list)
        messages = await consumer.consume_messages(timeout_ms=100, max_messages=10)
        assert isinstance(messages, list)

        # Commit offsets
        await consumer.commit_offsets()

        # Get offsets
        offsets = await consumer.get_current_offsets()
        assert isinstance(offsets, dict)

        # Close
        await consumer.close_consumer()

    @pytest.mark.asyncio
    async def test_batch_producer_workflow_integration(self) -> None:
        """Test complete batch producer workflow: validate -> send -> flush -> metrics."""
        producer = CompliantEventBusBatchProducer()

        # Validate connection
        is_connected = await producer.validate_connection()
        assert is_connected

        # Send empty batch (valid operation)
        await producer.send_batch([])

        # Flush pending
        await producer.flush_pending(timeout_ms=1000)

        # Get metrics
        metrics = await producer.get_batch_metrics()
        assert "messages_sent" in metrics

    @pytest.mark.asyncio
    async def test_transactional_producer_complete_workflow(self) -> None:
        """Test complete transactional workflow: init -> begin -> send -> commit."""
        producer = CompliantEventBusTransactionalProducer()

        # Initialize
        await producer.init_transactions("integration-test-tx")

        # Begin transaction
        await producer.begin_transaction()

        # Send message
        await producer.send_transactional(
            topic="test-events",
            value=b'{"event": "test"}',
            key=b"test-key",
            headers={"correlation_id": b"test-123"},
        )

        # Commit
        await producer.commit_transaction()

    @pytest.mark.asyncio
    async def test_transactional_producer_abort_workflow(self) -> None:
        """Test transaction abort workflow: init -> begin -> send -> abort."""
        producer = CompliantEventBusTransactionalProducer()

        # Initialize
        await producer.init_transactions("integration-test-abort")

        # Begin transaction
        await producer.begin_transaction()

        # Send message
        await producer.send_transactional(
            topic="test-events",
            value=b'{"event": "will_abort"}',
        )

        # Abort (simulating error scenario)
        await producer.abort_transaction()

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
    async def test_message_validation_before_batch_send(self) -> None:
        """Test message validation integration with batch producer."""
        producer = CompliantEventBusBatchProducer()
        message = CompliantEventBusMessage()

        # Validate message
        is_valid = await producer.validate_message(cast(ProtocolEventBusMessage, message))
        assert is_valid

        # Then send (if valid)
        await producer.send_batch([])  # Would include message in real impl


# =============================================================================
# Edge Case Tests - Message Edge Cases
# =============================================================================


class TestCompliantEventBusMessageEdgeCases:
    """Test edge cases for CompliantEventBusMessage."""

    def test_empty_value_is_valid_bytes(self) -> None:
        """Empty bytes is valid for value."""
        msg = CompliantEventBusMessage(value=b"", topic="test")
        assert msg.value == b""

    def test_large_value_accepted(self) -> None:
        """Large byte payloads should be accepted."""
        large_value = b"x" * 10_000_000  # 10MB
        msg = CompliantEventBusMessage(value=large_value, topic="test")
        assert len(msg.value) == 10_000_000

    def test_unicode_topic_encoded(self) -> None:
        """Topic with unicode characters works."""
        msg = CompliantEventBusMessage(topic="evenements-\u65e5\u672c\u8a9e", value=b"data")
        assert msg.topic == "evenements-\u65e5\u672c\u8a9e"

    def test_none_optional_fields(self) -> None:
        """All optional fields can be None."""
        msg = CompliantEventBusMessage(
            value=b"data",
            topic="test",
            key=None,
            partition=None,
            offset=None,
            timestamp=None,
            headers=None,
        )
        assert msg.key is None
        assert msg.partition is None
        assert msg.offset is None
        assert msg.timestamp is None
        # headers defaults to {} not None
        assert msg.headers == {}

    def test_zero_partition_is_valid(self) -> None:
        """Partition 0 is a valid partition number."""
        msg = CompliantEventBusMessage(value=b"data", topic="test", partition=0)
        assert msg.partition == 0

    def test_zero_offset_is_valid(self) -> None:
        """Offset 0 is a valid offset."""
        msg = CompliantEventBusMessage(value=b"data", topic="test", offset=0)
        assert msg.offset == 0

    def test_binary_value_with_null_bytes(self) -> None:
        """Binary value with null bytes should be accepted."""
        binary_data = b"\x00\x01\x02\x03\x00\xff"
        msg = CompliantEventBusMessage(value=binary_data, topic="test")
        assert msg.value == binary_data

    def test_message_with_headers(self) -> None:
        """Message with headers should preserve them."""
        headers = {"content-type": b"application/json", "version": b"1.0"}
        msg = CompliantEventBusMessage(value=b"data", topic="test", headers=headers)
        assert msg.headers == headers

    def test_very_long_topic_name(self) -> None:
        """Very long topic names should be accepted."""
        long_topic = "t" * 1000
        msg = CompliantEventBusMessage(value=b"data", topic=long_topic)
        assert msg.topic == long_topic

    def test_topic_with_special_characters(self) -> None:
        """Topic with dots, hyphens, underscores should work."""
        msg = CompliantEventBusMessage(value=b"data", topic="my.topic-name_v1")
        assert msg.topic == "my.topic-name_v1"


class TestCompliantEventBusMessageValidationErrors:
    """Test validation error handling for CompliantEventBusMessage."""

    def test_non_bytes_value_raises_type_error(self) -> None:
        """Non-bytes value should raise TypeError."""
        with pytest.raises(TypeError, match="value must be bytes"):
            CompliantEventBusMessage(value="not bytes", topic="test")  # type: ignore[arg-type]

    def test_empty_topic_raises_value_error(self) -> None:
        """Empty topic should raise ValueError."""
        with pytest.raises(ValueError, match="topic must be a non-empty string"):
            CompliantEventBusMessage(value=b"data", topic="")

    def test_negative_partition_raises_value_error(self) -> None:
        """Negative partition should raise ValueError."""
        with pytest.raises(ValueError, match="partition must be non-negative"):
            CompliantEventBusMessage(value=b"data", topic="test", partition=-1)

    def test_negative_offset_raises_value_error(self) -> None:
        """Negative offset should raise ValueError."""
        with pytest.raises(ValueError, match="offset must be non-negative"):
            CompliantEventBusMessage(value=b"data", topic="test", offset=-1)

    def test_none_value_raises_type_error(self) -> None:
        """None value should raise TypeError."""
        with pytest.raises(TypeError, match="value must be bytes"):
            CompliantEventBusMessage(value=None, topic="test")  # type: ignore[arg-type]

    def test_int_value_raises_type_error(self) -> None:
        """Integer value should raise TypeError."""
        with pytest.raises(TypeError, match="value must be bytes"):
            CompliantEventBusMessage(value=12345, topic="test")  # type: ignore[arg-type]

    def test_list_value_raises_type_error(self) -> None:
        """List value should raise TypeError."""
        with pytest.raises(TypeError, match="value must be bytes"):
            CompliantEventBusMessage(value=[1, 2, 3], topic="test")  # type: ignore[arg-type]


# =============================================================================
# Edge Case Tests - Client Edge Cases
# =============================================================================


class TestProtocolEventBusClientEdgeCases:
    """Test edge cases for basic EventBus client."""

    @pytest.mark.asyncio
    async def test_stop_with_zero_timeout(self) -> None:
        """Stop with zero timeout should work."""
        client = CompliantEventBusClient()
        await client.stop(timeout_seconds=0.0)

    @pytest.mark.asyncio
    async def test_send_empty_value(self) -> None:
        """Sending empty bytes should work."""
        client = CompliantEventBusClient()
        await client.send_and_wait(topic="test", value=b"")

    @pytest.mark.asyncio
    async def test_send_with_null_key(self) -> None:
        """Sending with null key should work."""
        client = CompliantEventBusClient()
        await client.send_and_wait(topic="test", value=b"data", key=None)

    @pytest.mark.asyncio
    async def test_send_large_value(self) -> None:
        """Sending large bytes should work."""
        client = CompliantEventBusClient()
        large_value = b"x" * 1_000_000  # 1MB
        await client.send_and_wait(topic="test", value=large_value)

    @pytest.mark.asyncio
    async def test_validate_empty_message(self) -> None:
        """Validate empty bytes message should work."""
        client = CompliantEventBusClient()
        result = await client.validate_message(topic="test", value=b"")
        assert result is True

    def test_bootstrap_servers_returns_non_empty_list(self) -> None:
        """Bootstrap servers should return at least one server."""
        client = CompliantEventBusClient()
        servers = client.bootstrap_servers()
        assert len(servers) >= 1


# =============================================================================
# Error-Raising Mock Implementations
# =============================================================================


class ErrorRaisingEventBusClient:
    """A client that raises errors on operations to test error handling paths."""

    def __init__(
        self,
        start_error: Exception | None = None,
        stop_error: Exception | None = None,
        send_error: Exception | None = None,
        validate_error: Exception | None = None,
    ) -> None:
        """Initialize with configurable errors.

        Args:
            start_error: Exception to raise on start()
            stop_error: Exception to raise on stop()
            send_error: Exception to raise on send_and_wait()
            validate_error: Exception to raise on validate_connection()
        """
        self._start_error = start_error
        self._stop_error = stop_error
        self._send_error = send_error
        self._validate_error = validate_error

    async def start(self) -> None:
        """Start the EventBus client - may raise configured error."""
        if self._start_error:
            raise self._start_error

    async def stop(self, timeout_seconds: float = 30.0) -> None:
        """Stop the EventBus client - may raise configured error."""
        _ = timeout_seconds
        if self._stop_error:
            raise self._stop_error

    async def send_and_wait(
        self, topic: str, value: bytes, key: bytes | None = None
    ) -> None:
        """Send a message - may raise configured error."""
        _ = (topic, value, key)
        if self._send_error:
            raise self._send_error

    def bootstrap_servers(self) -> list[str]:
        """Get bootstrap servers."""
        return ["localhost:9092"]

    async def validate_connection(self) -> bool:
        """Validate connection - may raise configured error."""
        if self._validate_error:
            raise self._validate_error
        return True

    async def validate_message(
        self, topic: str, value: bytes, key: bytes | None = None
    ) -> bool:
        """Validate a message before publishing."""
        _ = (topic, value, key)
        return True


class ErrorRaisingEventBusConsumer:
    """A consumer that raises errors on operations to test error handling paths."""

    def __init__(
        self,
        subscribe_error: Exception | None = None,
        consume_error: Exception | None = None,
        commit_error: Exception | None = None,
        close_error: Exception | None = None,
    ) -> None:
        """Initialize with configurable errors."""
        self._subscribe_error = subscribe_error
        self._consume_error = consume_error
        self._commit_error = commit_error
        self._close_error = close_error

    async def subscribe_to_topics(self, topics: list[str], group_id: str) -> None:
        """Subscribe to topics - may raise configured error."""
        _ = (topics, group_id)
        if self._subscribe_error:
            raise self._subscribe_error

    async def unsubscribe_from_topics(self, topics: list[str]) -> None:
        """Unsubscribe from topics."""
        _ = topics

    async def consume_messages(
        self, timeout_ms: int, max_messages: int
    ) -> list[ProtocolEventBusMessage]:
        """Consume messages - may raise configured error."""
        _ = (timeout_ms, max_messages)
        if self._consume_error:
            raise self._consume_error
        return []

    async def consume_messages_stream(
        self, batch_timeout_ms: int
    ) -> list[ProtocolEventBusMessage]:
        """Consume a batch of messages with streaming semantics."""
        _ = batch_timeout_ms
        return []

    async def commit_offsets(self) -> None:
        """Commit current consumer offsets - may raise configured error."""
        if self._commit_error:
            raise self._commit_error

    async def seek_to_beginning(self, topic: str, partition: int) -> None:
        """Seek to the beginning of a topic partition."""
        _ = (topic, partition)

    async def seek_to_end(self, topic: str, partition: int) -> None:
        """Seek to the end of a topic partition."""
        _ = (topic, partition)

    async def seek_to_offset(self, topic: str, partition: int, offset: int) -> None:
        """Seek to a specific offset."""
        _ = (topic, partition, offset)

    async def get_current_offsets(self) -> dict[str, dict[int, int]]:
        """Get current consumer offsets."""
        return {"test-topic": {0: 100}}

    async def close_consumer(self, timeout_seconds: float = 30.0) -> None:
        """Close the consumer - may raise configured error."""
        _ = timeout_seconds
        if self._close_error:
            raise self._close_error

    async def validate_connection(self) -> bool:
        """Validate the connection."""
        return True


class ErrorRaisingTransactionalProducer:
    """A transactional producer that raises errors to test error handling paths."""

    def __init__(
        self,
        init_error: Exception | None = None,
        begin_error: Exception | None = None,
        send_error: Exception | None = None,
        commit_error: Exception | None = None,
        abort_error: Exception | None = None,
    ) -> None:
        """Initialize with configurable errors."""
        self._init_error = init_error
        self._begin_error = begin_error
        self._send_error = send_error
        self._commit_error = commit_error
        self._abort_error = abort_error

    async def init_transactions(self, transaction_id: str) -> None:
        """Initialize the transactional producer - may raise configured error."""
        _ = transaction_id
        if self._init_error:
            raise self._init_error

    async def begin_transaction(self) -> None:
        """Begin a new transaction - may raise configured error."""
        if self._begin_error:
            raise self._begin_error

    async def send_transactional(
        self,
        topic: str,
        value: bytes,
        key: bytes | None = None,
        headers: dict[str, bytes] | None = None,
    ) -> None:
        """Send a message as part of transaction - may raise configured error."""
        _ = (topic, value, key, headers)
        if self._send_error:
            raise self._send_error

    async def commit_transaction(self) -> None:
        """Commit the current transaction - may raise configured error."""
        if self._commit_error:
            raise self._commit_error

    async def abort_transaction(self) -> None:
        """Abort the current transaction - may raise configured error."""
        if self._abort_error:
            raise self._abort_error


class ErrorRaisingExtendedClient:
    """An extended client that raises errors to test error handling paths."""

    def __init__(
        self,
        create_consumer_error: Exception | None = None,
        create_topic_error: Exception | None = None,
        health_check_error: Exception | None = None,
    ) -> None:
        """Initialize with configurable errors."""
        self._create_consumer_error = create_consumer_error
        self._create_topic_error = create_topic_error
        self._health_check_error = health_check_error

    async def create_consumer(self) -> ProtocolEventBusConsumer:
        """Create a new consumer instance - may raise configured error."""
        if self._create_consumer_error:
            raise self._create_consumer_error
        return cast(ProtocolEventBusConsumer, CompliantEventBusConsumer())

    async def create_batch_producer(self) -> ProtocolEventBusBatchProducer:
        """Create a new batch producer instance."""
        return cast(ProtocolEventBusBatchProducer, CompliantEventBusBatchProducer())

    async def create_transactional_producer(
        self,
    ) -> ProtocolEventBusTransactionalProducer:
        """Create a new transactional producer instance."""
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
        """Create a new topic - may raise configured error."""
        _ = (topic_name, partitions, replication_factor, topic_config)
        if self._create_topic_error:
            raise self._create_topic_error

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
        """Check connection health - may raise configured error."""
        if self._health_check_error:
            raise self._health_check_error
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


# =============================================================================
# Error Handling Path Tests
# =============================================================================


class TestErrorHandlingPaths:
    """Test error propagation patterns for EventBus protocols.

    These tests validate that mock implementations can properly raise exceptions
    and that error handling paths work correctly.
    """

    @pytest.mark.asyncio
    async def test_client_start_error_propagation(self) -> None:
        """Client start error should propagate correctly."""
        error = ConnectionError("Failed to connect to broker")
        client = ErrorRaisingEventBusClient(start_error=error)

        with pytest.raises(ConnectionError, match="Failed to connect"):
            await client.start()

    @pytest.mark.asyncio
    async def test_client_stop_error_propagation(self) -> None:
        """Client stop error should propagate correctly."""
        error = TimeoutError("Shutdown timeout exceeded")
        client = ErrorRaisingEventBusClient(stop_error=error)

        with pytest.raises(TimeoutError, match="Shutdown timeout"):
            await client.stop()

    @pytest.mark.asyncio
    async def test_client_send_error_propagation(self) -> None:
        """Client send error should propagate correctly."""
        error = RuntimeError("Message delivery failed")
        client = ErrorRaisingEventBusClient(send_error=error)

        with pytest.raises(RuntimeError, match="Message delivery failed"):
            await client.send_and_wait(topic="test", value=b"data")

    @pytest.mark.asyncio
    async def test_client_validate_connection_error_propagation(self) -> None:
        """Client validate_connection error should propagate correctly."""
        error = ConnectionError("Connection validation failed")
        client = ErrorRaisingEventBusClient(validate_error=error)

        with pytest.raises(ConnectionError, match="Connection validation failed"):
            await client.validate_connection()

    @pytest.mark.asyncio
    async def test_consumer_subscribe_error_propagation(self) -> None:
        """Consumer subscribe error should propagate correctly."""
        error = ValueError("Invalid topic format")
        consumer = ErrorRaisingEventBusConsumer(subscribe_error=error)

        with pytest.raises(ValueError, match="Invalid topic format"):
            await consumer.subscribe_to_topics(["test"], "group")

    @pytest.mark.asyncio
    async def test_consumer_consume_error_propagation(self) -> None:
        """Consumer consume error should propagate correctly."""
        error = RuntimeError("Consumer poll failed")
        consumer = ErrorRaisingEventBusConsumer(consume_error=error)

        with pytest.raises(RuntimeError, match="Consumer poll failed"):
            await consumer.consume_messages(timeout_ms=1000, max_messages=10)

    @pytest.mark.asyncio
    async def test_consumer_commit_error_propagation(self) -> None:
        """Consumer commit error should propagate correctly."""
        error = RuntimeError("Offset commit failed")
        consumer = ErrorRaisingEventBusConsumer(commit_error=error)

        with pytest.raises(RuntimeError, match="Offset commit failed"):
            await consumer.commit_offsets()

    @pytest.mark.asyncio
    async def test_consumer_close_error_propagation(self) -> None:
        """Consumer close error should propagate correctly."""
        error = TimeoutError("Consumer close timeout")
        consumer = ErrorRaisingEventBusConsumer(close_error=error)

        with pytest.raises(TimeoutError, match="Consumer close timeout"):
            await consumer.close_consumer()

    @pytest.mark.asyncio
    async def test_transactional_init_error_propagation(self) -> None:
        """Transactional producer init error should propagate correctly."""
        error = RuntimeError("Transaction coordinator unavailable")
        producer = ErrorRaisingTransactionalProducer(init_error=error)

        with pytest.raises(RuntimeError, match="Transaction coordinator unavailable"):
            await producer.init_transactions("tx-1")

    @pytest.mark.asyncio
    async def test_transactional_begin_error_propagation(self) -> None:
        """Transactional producer begin error should propagate correctly."""
        error = RuntimeError("Transaction already in progress")
        producer = ErrorRaisingTransactionalProducer(begin_error=error)

        with pytest.raises(RuntimeError, match="Transaction already in progress"):
            await producer.begin_transaction()

    @pytest.mark.asyncio
    async def test_transactional_send_error_propagation(self) -> None:
        """Transactional producer send error should propagate correctly."""
        error = RuntimeError("Transaction was aborted")
        producer = ErrorRaisingTransactionalProducer(send_error=error)

        with pytest.raises(RuntimeError, match="Transaction was aborted"):
            await producer.send_transactional("test", b"data")

    @pytest.mark.asyncio
    async def test_transactional_commit_error_propagation(self) -> None:
        """Transactional producer commit error should propagate correctly."""
        error = RuntimeError("Transaction commit failed")
        producer = ErrorRaisingTransactionalProducer(commit_error=error)

        with pytest.raises(RuntimeError, match="Transaction commit failed"):
            await producer.commit_transaction()

    @pytest.mark.asyncio
    async def test_transactional_abort_error_propagation(self) -> None:
        """Transactional producer abort error should propagate correctly."""
        error = RuntimeError("Transaction abort failed")
        producer = ErrorRaisingTransactionalProducer(abort_error=error)

        with pytest.raises(RuntimeError, match="Transaction abort failed"):
            await producer.abort_transaction()

    @pytest.mark.asyncio
    async def test_extended_client_create_consumer_error_propagation(self) -> None:
        """Extended client create_consumer error should propagate correctly."""
        error = RuntimeError("Failed to create consumer")
        client = ErrorRaisingExtendedClient(create_consumer_error=error)

        with pytest.raises(RuntimeError, match="Failed to create consumer"):
            await client.create_consumer()

    @pytest.mark.asyncio
    async def test_extended_client_create_topic_error_propagation(self) -> None:
        """Extended client create_topic error should propagate correctly."""
        error = RuntimeError("Topic already exists")
        client = ErrorRaisingExtendedClient(create_topic_error=error)

        with pytest.raises(RuntimeError, match="Topic already exists"):
            await client.create_topic("test", 3, 1)

    @pytest.mark.asyncio
    async def test_extended_client_health_check_error_propagation(self) -> None:
        """Extended client health_check error should propagate correctly."""
        error = ConnectionError("Broker connection lost")
        client = ErrorRaisingExtendedClient(health_check_error=error)

        with pytest.raises(ConnectionError, match="Broker connection lost"):
            await client.health_check()

    @pytest.mark.asyncio
    async def test_multiple_errors_in_workflow(self) -> None:
        """Test error handling in a multi-step workflow."""
        # Start works, but send fails
        client = ErrorRaisingEventBusClient(
            send_error=RuntimeError("Network error during send")
        )

        await client.start()  # Should succeed

        with pytest.raises(RuntimeError, match="Network error during send"):
            await client.send_and_wait("test", b"data")

    @pytest.mark.asyncio
    async def test_error_with_isinstance_check(self) -> None:
        """Verify error-raising mocks still pass isinstance checks."""
        client = ErrorRaisingEventBusClient(start_error=RuntimeError("Test error"))
        assert isinstance(client, ProtocolEventBusClient)

        consumer = ErrorRaisingEventBusConsumer(consume_error=RuntimeError("Test"))
        assert isinstance(consumer, ProtocolEventBusConsumer)


# =============================================================================
# Timeout Behavior Tests
# =============================================================================


class TestTimeoutBehavior:
    """Test timeout parameter handling across EventBus protocols.

    These tests validate that timeout parameters are properly accepted
    and edge cases are handled gracefully.
    """

    @pytest.mark.asyncio
    async def test_client_stop_default_timeout(self) -> None:
        """Client stop should work with default timeout."""
        client = CompliantEventBusClient()
        await client.stop()  # Uses default 30.0

    @pytest.mark.asyncio
    async def test_client_stop_zero_timeout(self) -> None:
        """Client stop with zero timeout should be accepted."""
        client = CompliantEventBusClient()
        await client.stop(timeout_seconds=0.0)

    @pytest.mark.asyncio
    async def test_client_stop_negative_timeout_accepted(self) -> None:
        """Client stop with negative timeout should be accepted (impl handles)."""
        client = CompliantEventBusClient()
        # Negative values are passed through - implementation decides behavior
        await client.stop(timeout_seconds=-1.0)

    @pytest.mark.asyncio
    async def test_client_stop_very_large_timeout(self) -> None:
        """Client stop with very large timeout should be accepted."""
        client = CompliantEventBusClient()
        await client.stop(timeout_seconds=float(2**31))  # ~68 years

    @pytest.mark.asyncio
    async def test_client_stop_fractional_timeout(self) -> None:
        """Client stop with fractional timeout should be accepted."""
        client = CompliantEventBusClient()
        await client.stop(timeout_seconds=0.001)
        await client.stop(timeout_seconds=0.5)
        await client.stop(timeout_seconds=1.5)

    @pytest.mark.asyncio
    async def test_consumer_close_default_timeout(self) -> None:
        """Consumer close should work with default timeout."""
        consumer = CompliantEventBusConsumer()
        await consumer.close_consumer()  # Uses default 30.0

    @pytest.mark.asyncio
    async def test_consumer_close_zero_timeout(self) -> None:
        """Consumer close with zero timeout should be accepted."""
        consumer = CompliantEventBusConsumer()
        await consumer.close_consumer(timeout_seconds=0.0)

    @pytest.mark.asyncio
    async def test_consumer_close_negative_timeout_accepted(self) -> None:
        """Consumer close with negative timeout should be accepted (impl handles)."""
        consumer = CompliantEventBusConsumer()
        await consumer.close_consumer(timeout_seconds=-1.0)

    @pytest.mark.asyncio
    async def test_consumer_close_very_large_timeout(self) -> None:
        """Consumer close with very large timeout should be accepted."""
        consumer = CompliantEventBusConsumer()
        await consumer.close_consumer(timeout_seconds=float(2**31))

    @pytest.mark.asyncio
    async def test_consumer_consume_zero_timeout(self) -> None:
        """Consumer consume with zero timeout should return immediately."""
        consumer = CompliantEventBusConsumer()
        messages = await consumer.consume_messages(timeout_ms=0, max_messages=10)
        assert isinstance(messages, list)

    @pytest.mark.asyncio
    async def test_consumer_consume_negative_timeout_accepted(self) -> None:
        """Consumer consume with negative timeout should be accepted (impl handles)."""
        consumer = CompliantEventBusConsumer()
        messages = await consumer.consume_messages(timeout_ms=-1, max_messages=10)
        assert isinstance(messages, list)

    @pytest.mark.asyncio
    async def test_consumer_consume_very_large_timeout(self) -> None:
        """Consumer consume with very large timeout should be accepted."""
        consumer = CompliantEventBusConsumer()
        # Max int value for timeout
        messages = await consumer.consume_messages(
            timeout_ms=2**31 - 1, max_messages=10
        )
        assert isinstance(messages, list)

    @pytest.mark.asyncio
    async def test_consumer_stream_zero_timeout(self) -> None:
        """Consumer stream with zero timeout should be accepted."""
        consumer = CompliantEventBusConsumer()
        messages = await consumer.consume_messages_stream(batch_timeout_ms=0)
        assert isinstance(messages, list)

    @pytest.mark.asyncio
    async def test_consumer_stream_negative_timeout_accepted(self) -> None:
        """Consumer stream with negative timeout should be accepted."""
        consumer = CompliantEventBusConsumer()
        messages = await consumer.consume_messages_stream(batch_timeout_ms=-1)
        assert isinstance(messages, list)

    @pytest.mark.asyncio
    async def test_batch_producer_flush_zero_timeout(self) -> None:
        """Batch producer flush with zero timeout should be accepted."""
        producer = CompliantEventBusBatchProducer()
        await producer.flush_pending(timeout_ms=0)

    @pytest.mark.asyncio
    async def test_batch_producer_flush_negative_timeout_accepted(self) -> None:
        """Batch producer flush with negative timeout should be accepted."""
        producer = CompliantEventBusBatchProducer()
        await producer.flush_pending(timeout_ms=-1)

    @pytest.mark.asyncio
    async def test_batch_producer_flush_very_large_timeout(self) -> None:
        """Batch producer flush with very large timeout should be accepted."""
        producer = CompliantEventBusBatchProducer()
        await producer.flush_pending(timeout_ms=2**31 - 1)

    @pytest.mark.asyncio
    async def test_extended_client_close_default_timeout(self) -> None:
        """Extended client close should work with default timeout."""
        client = CompliantEventBusExtendedClient()
        await client.close_client()  # Uses default 30.0

    @pytest.mark.asyncio
    async def test_extended_client_close_zero_timeout(self) -> None:
        """Extended client close with zero timeout should be accepted."""
        client = CompliantEventBusExtendedClient()
        await client.close_client(timeout_seconds=0.0)

    @pytest.mark.asyncio
    async def test_extended_client_close_very_large_timeout(self) -> None:
        """Extended client close with very large timeout should be accepted."""
        client = CompliantEventBusExtendedClient()
        await client.close_client(timeout_seconds=float(2**31))


# =============================================================================
# Enhanced Integration Tests
# =============================================================================


class TestEnhancedProtocolIntegration:
    """Enhanced integration tests for multi-protocol workflows.

    These tests validate deeper integration patterns between protocols,
    ensuring created objects can be used end-to-end.
    """

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

    @pytest.mark.asyncio
    async def test_provider_creates_usable_client_end_to_end(self) -> None:
        """Provider creates Client that can be used end-to-end."""
        provider = CompliantEventBusClientProvider()

        # Get configuration
        config = await provider.get_event_bus_configuration()
        assert isinstance(config, dict)
        assert "bootstrap_servers" in config

        # Create client via provider
        client = await provider.create_event_bus_client()
        assert isinstance(client, ProtocolEventBusClient)

        # Perform full client lifecycle
        await client.start()
        is_connected = await client.validate_connection()
        assert is_connected

        servers = client.bootstrap_servers()
        assert len(servers) > 0

        # Validate and send message
        is_valid = await client.validate_message("test", b"data")
        assert is_valid
        await client.send_and_wait("test-topic", b"message-data", key=b"key")

        await client.stop()

    @pytest.mark.asyncio
    async def test_multi_protocol_parallel_operations(self) -> None:
        """Test parallel operations across multiple protocols."""
        client = CompliantEventBusExtendedClient()

        # Create multiple components
        consumer = await client.create_consumer()
        batch_producer = await client.create_batch_producer()
        tx_producer = await client.create_transactional_producer()

        # Run operations in parallel (simulated)
        # Subscribe consumer
        await consumer.subscribe_to_topics(["topic-1"], "group-1")

        # Send batch message
        msg = CompliantEventBusMessage(value=b"batch-data", topic="topic-1")
        await batch_producer.send_batch([cast(ProtocolEventBusMessage, msg)])

        # Send transactional message
        await tx_producer.init_transactions("parallel-tx")
        await tx_producer.begin_transaction()
        await tx_producer.send_transactional("topic-1", b"tx-data")
        await tx_producer.commit_transaction()

        # Consume messages
        messages = await consumer.consume_messages(timeout_ms=100, max_messages=10)
        assert isinstance(messages, list)

        # Cleanup
        await consumer.close_consumer()
        await client.close_client()

    @pytest.mark.asyncio
    async def test_topic_management_with_consumer_workflow(self) -> None:
        """Test topic management integrated with consumer workflow."""
        client = CompliantEventBusExtendedClient()

        # Create topic
        await client.create_topic(
            "integration-topic", partitions=3, replication_factor=1
        )

        # Verify topic exists
        topics = await client.list_topics()
        assert isinstance(topics, list)

        # Get topic metadata
        metadata = await client.get_topic_metadata("integration-topic")
        assert "partitions" in metadata

        # Create consumer and subscribe to topic
        consumer = await client.create_consumer()
        await consumer.subscribe_to_topics(["integration-topic"], "integration-group")

        # Consume (no messages in mock, but validates the flow)
        messages = await consumer.consume_messages(timeout_ms=100, max_messages=10)
        assert isinstance(messages, list)

        # Cleanup
        await consumer.close_consumer()
        await client.delete_topic("integration-topic")
        await client.close_client()

    @pytest.mark.asyncio
    async def test_health_check_in_workflow(self) -> None:
        """Test health check integration in operational workflow."""
        client = CompliantEventBusExtendedClient()

        # Health check before operations
        healthy = await client.health_check()
        assert healthy is True

        # Create consumer
        consumer = await client.create_consumer()
        consumer_connected = await consumer.validate_connection()
        assert consumer_connected is True

        # Create batch producer
        producer = await client.create_batch_producer()
        producer_connected = await producer.validate_connection()
        assert producer_connected is True

        # Connection validation
        client_connected = await client.validate_connection()
        assert client_connected is True

        # Cleanup
        await consumer.close_consumer()
        await client.close_client()

    @pytest.mark.asyncio
    async def test_seek_operations_workflow(self) -> None:
        """Test seek operations in consumer workflow."""
        consumer = CompliantEventBusConsumer()

        # Subscribe
        await consumer.subscribe_to_topics(["seek-topic"], "seek-group")

        # Various seek operations
        await consumer.seek_to_beginning("seek-topic", partition=0)
        await consumer.seek_to_end("seek-topic", partition=0)
        await consumer.seek_to_offset("seek-topic", partition=0, offset=100)

        # Get current offsets after seeking
        offsets = await consumer.get_current_offsets()
        assert isinstance(offsets, dict)

        # Consume after seeking
        messages = await consumer.consume_messages(timeout_ms=100, max_messages=10)
        assert isinstance(messages, list)

        await consumer.close_consumer()


# =============================================================================
# Negative and Boundary Tests
# =============================================================================


class TestNegativeAndBoundaryConditions:
    """Test negative cases, malformed data, and boundary conditions.

    These tests validate how protocols handle invalid inputs and edge cases.
    """

    def test_message_with_none_topic_raises_error(self) -> None:
        """Message with None topic should raise error."""
        with pytest.raises((ValueError, TypeError)):
            CompliantEventBusMessage(value=b"data", topic=None)  # type: ignore[arg-type]

    def test_message_with_integer_topic_raises_error(self) -> None:
        """Message with integer topic should raise error."""
        with pytest.raises((ValueError, TypeError)):
            CompliantEventBusMessage(value=b"data", topic=123)  # type: ignore[arg-type]

    def test_message_with_empty_string_topic_raises_error(self) -> None:
        """Message with empty string topic should raise ValueError."""
        with pytest.raises(ValueError, match="topic must be a non-empty string"):
            CompliantEventBusMessage(value=b"data", topic="")

    def test_message_with_whitespace_only_topic_is_valid(self) -> None:
        """Message with whitespace-only topic is technically valid (non-empty)."""
        # This is a design decision - whitespace-only topic passes basic validation
        msg = CompliantEventBusMessage(value=b"data", topic="   ")
        assert msg.topic == "   "

    def test_message_with_very_negative_partition(self) -> None:
        """Message with very negative partition should raise ValueError."""
        with pytest.raises(ValueError, match="partition must be non-negative"):
            CompliantEventBusMessage(value=b"data", topic="test", partition=-999999)

    def test_message_with_very_negative_offset(self) -> None:
        """Message with very negative offset should raise ValueError."""
        with pytest.raises(ValueError, match="offset must be non-negative"):
            CompliantEventBusMessage(value=b"data", topic="test", offset=-999999)

    def test_message_with_max_int_partition(self) -> None:
        """Message with max int partition should be accepted."""
        msg = CompliantEventBusMessage(
            value=b"data", topic="test", partition=2**31 - 1
        )
        assert msg.partition == 2**31 - 1

    def test_message_with_max_int_offset(self) -> None:
        """Message with max int offset should be accepted."""
        msg = CompliantEventBusMessage(value=b"data", topic="test", offset=2**63 - 1)
        assert msg.offset == 2**63 - 1

    def test_message_with_very_large_timestamp(self) -> None:
        """Message with very large timestamp should be accepted."""
        # Timestamp far in the future (year 5138)
        msg = CompliantEventBusMessage(
            value=b"data", topic="test", timestamp=100_000_000_000_000
        )
        assert msg.timestamp == 100_000_000_000_000

    def test_message_with_negative_timestamp_is_allowed(self) -> None:
        """Message with negative timestamp is allowed (before epoch)."""
        msg = CompliantEventBusMessage(value=b"data", topic="test", timestamp=-1000)
        assert msg.timestamp == -1000

    def test_message_with_zero_timestamp(self) -> None:
        """Message with zero timestamp (Unix epoch) should be allowed."""
        msg = CompliantEventBusMessage(value=b"data", topic="test", timestamp=0)
        assert msg.timestamp == 0

    @pytest.mark.asyncio
    async def test_consumer_subscribe_with_empty_group_id(self) -> None:
        """Consumer subscribe with empty group_id should be accepted (impl handles)."""
        consumer = CompliantEventBusConsumer()
        # Empty group_id is passed through - implementation decides behavior
        await consumer.subscribe_to_topics(["test"], group_id="")

    @pytest.mark.asyncio
    async def test_consumer_subscribe_with_special_chars_in_group(self) -> None:
        """Consumer subscribe with special characters in group_id."""
        consumer = CompliantEventBusConsumer()
        await consumer.subscribe_to_topics(
            ["test"], group_id="group/with:special.chars"
        )

    @pytest.mark.asyncio
    async def test_consumer_consume_with_max_int_max_messages(self) -> None:
        """Consumer consume with max int for max_messages."""
        consumer = CompliantEventBusConsumer()
        messages = await consumer.consume_messages(
            timeout_ms=100, max_messages=2**31 - 1
        )
        assert isinstance(messages, list)

    @pytest.mark.asyncio
    async def test_batch_producer_send_to_high_partition(self) -> None:
        """Batch producer send to very high partition number."""
        producer = CompliantEventBusBatchProducer()
        await producer.send_to_partition(
            topic="test",
            partition=9999,  # High partition number
            key=b"key",
            value=b"data",
        )

    @pytest.mark.asyncio
    async def test_extended_client_create_topic_zero_partitions(self) -> None:
        """Extended client create topic with zero partitions."""
        client = CompliantEventBusExtendedClient()
        # Zero partitions is passed through - implementation decides behavior
        await client.create_topic(
            "zero-partitions", partitions=0, replication_factor=1
        )

    @pytest.mark.asyncio
    async def test_extended_client_create_topic_negative_partitions(self) -> None:
        """Extended client create topic with negative partitions."""
        client = CompliantEventBusExtendedClient()
        # Negative partitions is passed through - implementation decides behavior
        await client.create_topic(
            "neg-partitions", partitions=-1, replication_factor=1
        )

    @pytest.mark.asyncio
    async def test_extended_client_create_topic_zero_replication(self) -> None:
        """Extended client create topic with zero replication factor."""
        client = CompliantEventBusExtendedClient()
        # Zero replication is passed through - implementation decides behavior
        await client.create_topic("zero-repl", partitions=1, replication_factor=0)

    @pytest.mark.asyncio
    async def test_transactional_empty_transaction_id(self) -> None:
        """Transactional producer with empty transaction ID."""
        producer = CompliantEventBusTransactionalProducer()
        # Empty transaction ID is passed through - implementation decides behavior
        await producer.init_transactions("")

    @pytest.mark.asyncio
    async def test_transactional_very_long_transaction_id(self) -> None:
        """Transactional producer with very long transaction ID."""
        producer = CompliantEventBusTransactionalProducer()
        long_tx_id = "tx-" + "x" * 10000
        await producer.init_transactions(long_tx_id)

    @pytest.mark.asyncio
    async def test_client_send_to_empty_topic(self) -> None:
        """Client send to empty topic string."""
        client = CompliantEventBusClient()
        # Empty topic is passed through - implementation decides behavior
        await client.send_and_wait(topic="", value=b"data")

    @pytest.mark.asyncio
    async def test_client_validate_message_empty_topic(self) -> None:
        """Client validate_message with empty topic."""
        client = CompliantEventBusClient()
        # Returns True in mock - real impl might return False
        result = await client.validate_message(topic="", value=b"data")
        assert isinstance(result, bool)

    def test_message_headers_with_empty_key(self) -> None:
        """Message headers with empty string key."""
        headers = {"": b"value"}
        msg = CompliantEventBusMessage(value=b"data", topic="test", headers=headers)
        assert "" in msg.headers

    def test_message_headers_with_empty_value(self) -> None:
        """Message headers with empty bytes value."""
        headers = {"key": b""}
        msg = CompliantEventBusMessage(value=b"data", topic="test", headers=headers)
        assert msg.headers["key"] == b""

    def test_message_with_binary_topic_name(self) -> None:
        """Message with topic containing non-printable characters."""
        topic = "topic\x00with\x01binary"
        msg = CompliantEventBusMessage(value=b"data", topic=topic)
        assert msg.topic == topic

    def test_message_value_with_all_null_bytes(self) -> None:
        """Message value that is all null bytes."""
        null_data = b"\x00" * 1000
        msg = CompliantEventBusMessage(value=null_data, topic="test")
        assert msg.value == null_data

    @pytest.mark.asyncio
    async def test_consumer_seek_to_very_large_offset(self) -> None:
        """Consumer seek to very large offset."""
        consumer = CompliantEventBusConsumer()
        # Max int64 offset
        await consumer.seek_to_offset("test", partition=0, offset=2**63 - 1)

    @pytest.mark.asyncio
    async def test_batch_producer_custom_partitioner_empty_strategy(self) -> None:
        """Batch producer with empty partition strategy string."""
        producer = CompliantEventBusBatchProducer()
        await producer.send_with_custom_partitioner(
            topic="test",
            key=b"key",
            value=b"value",
            partition_strategy="",
        )

    @pytest.mark.asyncio
    async def test_extended_client_get_metadata_empty_topic(self) -> None:
        """Extended client get_topic_metadata with empty topic name."""
        client = CompliantEventBusExtendedClient()
        metadata = await client.get_topic_metadata("")
        assert isinstance(metadata, dict)

    @pytest.mark.asyncio
    async def test_extended_client_delete_empty_topic(self) -> None:
        """Extended client delete_topic with empty topic name."""
        client = CompliantEventBusExtendedClient()
        await client.delete_topic("")


class TestMessageDataIntegrity:
    """Test data integrity for message values and keys."""

    def test_message_preserves_all_byte_values(self) -> None:
        """Message should preserve all possible byte values (0-255)."""
        all_bytes = bytes(range(256))
        msg = CompliantEventBusMessage(value=all_bytes, topic="test")
        assert msg.value == all_bytes
        assert len(msg.value) == 256

    def test_message_preserves_key_bytes(self) -> None:
        """Message should preserve key byte values."""
        key_bytes = b"\x00\xff\x80\x7f"
        msg = CompliantEventBusMessage(value=b"data", topic="test", key=key_bytes)
        assert msg.key == key_bytes

    def test_message_preserves_header_values(self) -> None:
        """Message should preserve header byte values."""
        headers = {
            "binary": b"\x00\x01\x02\x03",
            # Using encode() without explicit utf-8 argument (Python default)
            "unicode": "\u65e5\u672c\u8a9e".encode(),
            "empty": b"",
        }
        msg = CompliantEventBusMessage(value=b"data", topic="test", headers=headers)
        assert msg.headers == headers

    def test_message_with_json_value(self) -> None:
        """Message with JSON-encoded value."""
        import json

        data = {"key": "value", "nested": {"items": [1, 2, 3]}}
        json_bytes = json.dumps(data).encode("utf-8")
        msg = CompliantEventBusMessage(value=json_bytes, topic="test")
        # Verify round-trip
        parsed = json.loads(msg.value.decode("utf-8"))
        assert parsed == data

    def test_message_with_protobuf_like_value(self) -> None:
        """Message with binary (protobuf-like) value."""
        # Simulated protobuf-like binary data
        binary_value = b"\x08\x96\x01\x12\x07testing\x18\x01"
        msg = CompliantEventBusMessage(value=binary_value, topic="test")
        assert msg.value == binary_value

    def test_message_with_compressed_value(self) -> None:
        """Message with compressed value (gzip)."""
        import gzip

        original = b"data to compress" * 100
        compressed = gzip.compress(original)
        msg = CompliantEventBusMessage(value=compressed, topic="test")
        # Verify round-trip
        decompressed = gzip.decompress(msg.value)
        assert decompressed == original
