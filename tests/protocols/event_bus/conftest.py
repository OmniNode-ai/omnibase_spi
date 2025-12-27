"""
Shared fixtures and mock implementations for EventBus protocol tests.

This module provides common test doubles and pytest fixtures used across
multiple EventBus test files. Centralizing these reduces code duplication
and ensures consistent behavior across all EventBus protocol tests.

Mock Implementation Categories
------------------------------
1. **CompliantEventBusMessage**: Data container satisfying ProtocolEventBusMessage
   with validation logic for proper message construction.

2. **CompliantEventBusConsumer**: Full consumer implementation for protocol testing
   with all required async methods.

3. **CompliantEventBusBatchProducer**: Batch producer with send_batch, send_to_partition,
   custom partitioning, and metrics.

4. **CompliantEventBusTransactionalProducer**: Transactional producer supporting
   full transaction lifecycle (init -> begin -> send -> commit/abort).

Design Rationale
----------------
- All mock classes implement ALL required protocol methods/attributes
- Async methods are no-ops (pass/return immediately) - we test protocol compliance, not behavior
- The pattern ``_ = (param, ...)`` marks unused parameters while satisfying linters
- Validation in CompliantEventBusMessage helps test edge cases in error tests

Usage
-----
Import fixtures directly in test functions - pytest auto-discovers conftest.py:

.. code-block:: python

    def test_example(compliant_message: CompliantEventBusMessage) -> None:
        assert isinstance(compliant_message, ProtocolEventBusMessage)

For mock classes, import from conftest:

.. code-block:: python

    from tests.protocols.event_bus.conftest import CompliantEventBusMessage
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, cast

import pytest

from omnibase_spi.protocols.event_bus.protocol_event_bus_extended import (
    ProtocolEventBusBatchProducer,
    ProtocolEventBusConsumer,
    ProtocolEventBusMessage,
    ProtocolEventBusTransactionalProducer,
)
from omnibase_spi.protocols.types.protocol_event_bus_types import ProtocolEventMessage

# =============================================================================
# Mock Implementations - Message
# =============================================================================


class CompliantEventBusMessage:
    """Test double implementing all ProtocolEventBusMessage attribute requirements.

    This mock provides a data container satisfying the message protocol,
    with validation logic to ensure proper message construction.

    Attributes:
        key: Optional message key for partitioning.
        value: Message payload (required, must be bytes).
        topic: Destination topic name (required, non-empty).
        partition: Target partition (optional, must be >= 0).
        offset: Message offset (optional, must be >= 0).
        timestamp: Unix timestamp in milliseconds (optional).
        headers: Message headers dictionary (defaults to {}).

    The constructor performs validation to ensure messages are well-formed,
    which helps test edge cases in the validation error tests.

    Example:
        >>> msg = CompliantEventBusMessage(value=b"data", topic="events")
        >>> isinstance(msg, ProtocolEventBusMessage)
        True
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


# =============================================================================
# Mock Implementations - Consumer
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


# =============================================================================
# Mock Implementations - Batch Producer
# =============================================================================


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


# =============================================================================
# Mock Implementations - Transactional Producer
# =============================================================================


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


# =============================================================================
# Mock Implementations - EventBus Base (for inheritance tests)
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
# Pytest Fixtures - Message
# =============================================================================


@pytest.fixture
def compliant_message() -> CompliantEventBusMessage:
    """Provide a compliant EventBus message for protocol compliance testing.

    Returns:
        A fresh CompliantEventBusMessage instance with default values,
        implementing all ProtocolEventBusMessage attribute requirements.
    """
    return CompliantEventBusMessage()


# =============================================================================
# Pytest Fixtures - Consumer
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
# Pytest Fixtures - Producers
# =============================================================================


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


# =============================================================================
# Pytest Fixtures - EventBus Mixin (for inheritance tests)
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
# Helper Functions
# =============================================================================


def create_compliant_message_as_protocol() -> ProtocolEventBusMessage:
    """Create a CompliantEventBusMessage cast to ProtocolEventBusMessage.

    This helper is useful when tests need to pass a message to functions
    that expect the protocol type rather than the concrete mock type.

    Returns:
        A CompliantEventBusMessage instance cast to ProtocolEventBusMessage.

    Example:
        >>> msg = create_compliant_message_as_protocol()
        >>> await producer.send_batch([msg])
    """
    return cast(ProtocolEventBusMessage, CompliantEventBusMessage())


def create_compliant_consumer_as_protocol() -> ProtocolEventBusConsumer:
    """Create a CompliantEventBusConsumer cast to ProtocolEventBusConsumer.

    Returns:
        A CompliantEventBusConsumer instance cast to ProtocolEventBusConsumer.
    """
    return cast(ProtocolEventBusConsumer, CompliantEventBusConsumer())


def create_compliant_batch_producer_as_protocol() -> ProtocolEventBusBatchProducer:
    """Create a CompliantEventBusBatchProducer cast to ProtocolEventBusBatchProducer.

    Returns:
        A CompliantEventBusBatchProducer instance cast to ProtocolEventBusBatchProducer.
    """
    return cast(ProtocolEventBusBatchProducer, CompliantEventBusBatchProducer())


def create_compliant_transactional_producer_as_protocol() -> (
    ProtocolEventBusTransactionalProducer
):
    """Create a CompliantEventBusTransactionalProducer cast to protocol type.

    Returns:
        A CompliantEventBusTransactionalProducer instance cast to
        ProtocolEventBusTransactionalProducer.
    """
    return cast(
        ProtocolEventBusTransactionalProducer, CompliantEventBusTransactionalProducer()
    )
