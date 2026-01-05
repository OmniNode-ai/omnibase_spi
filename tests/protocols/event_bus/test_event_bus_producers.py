"""
Tests for EventBus producer protocol compliance (Batch and Transactional).

This module validates that EventBus producer protocols are correctly defined and can be
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
- **ProtocolEventBusBatchProducer**: Batch message sending with partitioning
  strategies and metrics collection.

- **ProtocolEventBusTransactionalProducer**: Transactional message production with
  begin/commit/abort transaction semantics.

Test Organization
-----------------
Tests are organized into the following categories:

1. **Protocol Tests** (TestProtocol*Protocol): Verify protocol definition structure.
2. **Compliance Tests** (TestProtocol*Compliance): Verify isinstance behavior.
3. **Signature Tests** (TestProtocol*MethodSignatures): Verify method signatures.
4. **Edge Case Tests** (Test*EdgeCases): Verify boundary conditions and edge cases.

Testing Approach
----------------
Each protocol is tested using three types of mock implementations:

- **Compliant***: Fully implements all protocol requirements
- **Partial***: Implements only some methods (should fail isinstance)

This pattern ensures that runtime_checkable protocols correctly distinguish between
complete and incomplete implementations.

Note on Type Ignores
--------------------
Type ignores in this file are used in specific contexts:

- ``# type: ignore[misc]`` on protocol instantiation: Required because we're
  intentionally testing that Protocol classes raise TypeError when instantiated.
  The type checker correctly flags this as an error, but we want to verify the
  runtime behavior.
"""

import inspect
from typing import Protocol, cast

import pytest

from omnibase_spi.protocols.event_bus.protocol_event_bus_extended import (
    ProtocolEventBusBatchProducer,
    ProtocolEventBusMessage,
    ProtocolEventBusTransactionalProducer,
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
#
# The pattern of marking unused parameters with `_ = (param, ...)` is intentional:
# it satisfies linters while making clear the mock doesn't use these values.
# =============================================================================


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


class PartialEventBusBatchProducer:
    """Test double implementing only SOME ProtocolEventBusBatchProducer methods.

    Missing methods (intentionally):
        - send_to_partition
        - send_with_custom_partitioner
        - get_batch_metrics
        - validate_connection
        - validate_message

    Used by: test_partial_implementation_fails_isinstance
    """

    async def send_batch(self, messages: list[ProtocolEventBusMessage]) -> None:
        """Send a batch of messages."""
        _ = messages  # Unused in mock

    async def flush_pending(self, timeout_ms: int) -> None:
        """Flush all pending messages."""
        _ = timeout_ms  # Unused in mock


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


class PartialEventBusTransactionalProducer:
    """Test double implementing only SOME ProtocolEventBusTransactionalProducer methods.

    Missing methods (intentionally):
        - init_transactions
        - send_transactional
        - abort_transaction

    Used by: test_partial_implementation_fails_isinstance
    """

    async def begin_transaction(self) -> None:
        """Begin a new transaction."""
        pass  # Mock implementation

    async def commit_transaction(self) -> None:
        """Commit the current transaction."""
        pass  # Mock implementation


# =============================================================================
# Pytest Fixtures
# =============================================================================
#
# Fixtures provide pre-configured test doubles for protocol compliance testing.
# Each fixture returns a fresh instance of the corresponding compliant mock,
# ensuring test isolation.
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
# Test Classes - Batch Producer
# =============================================================================


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
            base is Protocol or base.__name__ == "Protocol"  # type: ignore[comparison-overlap]
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
            # Intentionally testing that Protocol cannot be instantiated
            ProtocolEventBusBatchProducer()  # type: ignore[misc]


class TestProtocolEventBusBatchProducerCompliance:
    """Test isinstance checks for ProtocolEventBusBatchProducer compliance."""

    def test_compliant_class_passes_isinstance(
        self, compliant_batch_producer: CompliantEventBusBatchProducer
    ) -> None:
        """A class implementing all methods should pass isinstance check."""
        assert isinstance(compliant_batch_producer, ProtocolEventBusBatchProducer)

    def test_partial_implementation_fails_isinstance(self) -> None:
        """A class missing methods should fail isinstance check."""
        producer = PartialEventBusBatchProducer()
        assert not isinstance(producer, ProtocolEventBusBatchProducer)


class TestProtocolEventBusBatchProducerMethodSignatures:
    """Test method signatures for ProtocolEventBusBatchProducer."""

    @pytest.mark.asyncio
    async def test_send_batch_accepts_message_list(
        self, compliant_batch_producer: CompliantEventBusBatchProducer
    ) -> None:
        """send_batch should accept a list of messages."""
        await compliant_batch_producer.send_batch([])  # Empty list should work

    @pytest.mark.asyncio
    async def test_send_to_partition_accepts_all_params(
        self, compliant_batch_producer: CompliantEventBusBatchProducer
    ) -> None:
        """send_to_partition should accept topic, partition, key, value, headers."""
        await compliant_batch_producer.send_to_partition(
            topic="test",
            partition=0,
            key=b"key",
            value=b"value",
            headers={"header": b"value"},
        )

    @pytest.mark.asyncio
    async def test_send_with_custom_partitioner_accepts_strategy(
        self, compliant_batch_producer: CompliantEventBusBatchProducer
    ) -> None:
        """send_with_custom_partitioner should accept partition_strategy."""
        await compliant_batch_producer.send_with_custom_partitioner(
            topic="test",
            key=b"key",
            value=b"value",
            partition_strategy="round_robin",
        )

    @pytest.mark.asyncio
    async def test_get_batch_metrics_returns_dict(
        self, compliant_batch_producer: CompliantEventBusBatchProducer
    ) -> None:
        """get_batch_metrics should return dict[str, int]."""
        metrics = await compliant_batch_producer.get_batch_metrics()
        assert isinstance(metrics, dict)
        for key, value in metrics.items():
            assert isinstance(key, str)
            assert isinstance(value, int)


class TestProtocolEventBusBatchProducerAsyncNature:
    """Test that ProtocolEventBusBatchProducer methods are async."""

    def test_send_batch_is_async(self) -> None:
        """send_batch should be an async method in both protocol and implementation."""
        # Check protocol defines async signature
        protocol_method = getattr(ProtocolEventBusBatchProducer, "send_batch", None)
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)
        # Check compliant implementation is async
        assert inspect.iscoroutinefunction(CompliantEventBusBatchProducer.send_batch)

    def test_send_to_partition_is_async(self) -> None:
        """send_to_partition should be an async method."""
        protocol_method = getattr(
            ProtocolEventBusBatchProducer, "send_to_partition", None
        )
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)
        assert inspect.iscoroutinefunction(
            CompliantEventBusBatchProducer.send_to_partition
        )

    def test_send_with_custom_partitioner_is_async(self) -> None:
        """send_with_custom_partitioner should be an async method."""
        protocol_method = getattr(
            ProtocolEventBusBatchProducer, "send_with_custom_partitioner", None
        )
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)
        assert inspect.iscoroutinefunction(
            CompliantEventBusBatchProducer.send_with_custom_partitioner
        )

    def test_flush_pending_is_async(self) -> None:
        """flush_pending should be an async method."""
        protocol_method = getattr(ProtocolEventBusBatchProducer, "flush_pending", None)
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)
        assert inspect.iscoroutinefunction(CompliantEventBusBatchProducer.flush_pending)

    def test_get_batch_metrics_is_async(self) -> None:
        """get_batch_metrics should be an async method."""
        protocol_method = getattr(
            ProtocolEventBusBatchProducer, "get_batch_metrics", None
        )
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)
        assert inspect.iscoroutinefunction(
            CompliantEventBusBatchProducer.get_batch_metrics
        )

    def test_validate_connection_is_async(self) -> None:
        """validate_connection should be an async method."""
        protocol_method = getattr(
            ProtocolEventBusBatchProducer, "validate_connection", None
        )
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)
        assert inspect.iscoroutinefunction(
            CompliantEventBusBatchProducer.validate_connection
        )

    def test_validate_message_is_async(self) -> None:
        """validate_message should be an async method."""
        protocol_method = getattr(
            ProtocolEventBusBatchProducer, "validate_message", None
        )
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)
        assert inspect.iscoroutinefunction(
            CompliantEventBusBatchProducer.validate_message
        )


# =============================================================================
# Test Classes - Transactional Producer
# =============================================================================


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
            base is Protocol or base.__name__ == "Protocol"  # type: ignore[comparison-overlap]
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
            # Intentionally testing that Protocol cannot be instantiated
            ProtocolEventBusTransactionalProducer()  # type: ignore[misc]


class TestProtocolEventBusTransactionalProducerCompliance:
    """Test isinstance checks for ProtocolEventBusTransactionalProducer compliance."""

    def test_compliant_class_passes_isinstance(
        self, compliant_transactional_producer: CompliantEventBusTransactionalProducer
    ) -> None:
        """A class implementing all methods should pass isinstance check."""
        assert isinstance(
            compliant_transactional_producer, ProtocolEventBusTransactionalProducer
        )

    def test_partial_implementation_fails_isinstance(self) -> None:
        """A class missing methods should fail isinstance check."""
        producer = PartialEventBusTransactionalProducer()
        assert not isinstance(producer, ProtocolEventBusTransactionalProducer)


class TestProtocolEventBusTransactionalProducerMethodSignatures:
    """Test method signatures for ProtocolEventBusTransactionalProducer."""

    @pytest.mark.asyncio
    async def test_init_transactions_accepts_transaction_id(
        self, compliant_transactional_producer: CompliantEventBusTransactionalProducer
    ) -> None:
        """init_transactions should accept transaction_id."""
        await compliant_transactional_producer.init_transactions(transaction_id="tx-1")

    @pytest.mark.asyncio
    async def test_send_transactional_accepts_all_params(
        self, compliant_transactional_producer: CompliantEventBusTransactionalProducer
    ) -> None:
        """send_transactional should accept topic, value, key, headers."""
        await compliant_transactional_producer.send_transactional(
            topic="test",
            value=b"value",
            key=b"key",
            headers={"header": b"value"},
        )

    @pytest.mark.asyncio
    async def test_transaction_workflow(
        self, compliant_transactional_producer: CompliantEventBusTransactionalProducer
    ) -> None:
        """Test complete transaction workflow."""
        await compliant_transactional_producer.init_transactions("tx-1")
        await compliant_transactional_producer.begin_transaction()
        await compliant_transactional_producer.send_transactional("test", b"data")
        await compliant_transactional_producer.commit_transaction()

    @pytest.mark.asyncio
    async def test_transaction_abort_workflow(
        self, compliant_transactional_producer: CompliantEventBusTransactionalProducer
    ) -> None:
        """Test transaction abort workflow."""
        await compliant_transactional_producer.init_transactions("tx-2")
        await compliant_transactional_producer.begin_transaction()
        await compliant_transactional_producer.send_transactional("test", b"data")
        await compliant_transactional_producer.abort_transaction()


class TestProtocolEventBusTransactionalProducerAsyncNature:
    """Test that ProtocolEventBusTransactionalProducer methods are async."""

    def test_init_transactions_is_async(self) -> None:
        """init_transactions should be an async method."""
        protocol_method = getattr(
            ProtocolEventBusTransactionalProducer, "init_transactions", None
        )
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)
        assert inspect.iscoroutinefunction(
            CompliantEventBusTransactionalProducer.init_transactions
        )

    def test_begin_transaction_is_async(self) -> None:
        """begin_transaction should be an async method."""
        protocol_method = getattr(
            ProtocolEventBusTransactionalProducer, "begin_transaction", None
        )
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)
        assert inspect.iscoroutinefunction(
            CompliantEventBusTransactionalProducer.begin_transaction
        )

    def test_send_transactional_is_async(self) -> None:
        """send_transactional should be an async method."""
        protocol_method = getattr(
            ProtocolEventBusTransactionalProducer, "send_transactional", None
        )
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)
        assert inspect.iscoroutinefunction(
            CompliantEventBusTransactionalProducer.send_transactional
        )

    def test_commit_transaction_is_async(self) -> None:
        """commit_transaction should be an async method."""
        protocol_method = getattr(
            ProtocolEventBusTransactionalProducer, "commit_transaction", None
        )
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)
        assert inspect.iscoroutinefunction(
            CompliantEventBusTransactionalProducer.commit_transaction
        )

    def test_abort_transaction_is_async(self) -> None:
        """abort_transaction should be an async method."""
        protocol_method = getattr(
            ProtocolEventBusTransactionalProducer, "abort_transaction", None
        )
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)
        assert inspect.iscoroutinefunction(
            CompliantEventBusTransactionalProducer.abort_transaction
        )


# =============================================================================
# Edge Case Tests - Transactional Producer
# =============================================================================


class TestProtocolEventBusTransactionalProducerEdgeCases:
    """Test edge cases for transactional producer."""

    @pytest.mark.asyncio
    async def test_empty_transaction_commit(self) -> None:
        """Committing a transaction with no messages should work."""
        producer = CompliantEventBusTransactionalProducer()
        await producer.init_transactions("tx-empty")
        await producer.begin_transaction()
        # No messages sent
        await producer.commit_transaction()

    @pytest.mark.asyncio
    async def test_transaction_with_empty_value(self) -> None:
        """Sending empty bytes in transaction should work."""
        producer = CompliantEventBusTransactionalProducer()
        await producer.init_transactions("tx-empty-value")
        await producer.begin_transaction()
        await producer.send_transactional("test", b"")
        await producer.commit_transaction()

    @pytest.mark.asyncio
    async def test_empty_transaction_abort(self) -> None:
        """Aborting a transaction with no messages should work."""
        producer = CompliantEventBusTransactionalProducer()
        await producer.init_transactions("tx-abort-empty")
        await producer.begin_transaction()
        # No messages sent
        await producer.abort_transaction()

    @pytest.mark.asyncio
    async def test_transaction_with_large_value(self) -> None:
        """Sending large bytes in transaction should work."""
        producer = CompliantEventBusTransactionalProducer()
        await producer.init_transactions("tx-large")
        await producer.begin_transaction()
        large_value = b"x" * 1_000_000  # 1MB
        await producer.send_transactional("test", large_value)
        await producer.commit_transaction()

    @pytest.mark.asyncio
    async def test_transaction_with_headers(self) -> None:
        """Sending message with headers in transaction should work."""
        producer = CompliantEventBusTransactionalProducer()
        await producer.init_transactions("tx-headers")
        await producer.begin_transaction()
        headers = {"correlation-id": b"abc123", "content-type": b"application/json"}
        await producer.send_transactional("test", b"data", headers=headers)
        await producer.commit_transaction()

    @pytest.mark.asyncio
    async def test_multiple_messages_in_transaction(self) -> None:
        """Sending multiple messages in a single transaction should work."""
        producer = CompliantEventBusTransactionalProducer()
        await producer.init_transactions("tx-multi")
        await producer.begin_transaction()
        for i in range(10):
            await producer.send_transactional("test", f"message-{i}".encode())
        await producer.commit_transaction()


# =============================================================================
# Edge Case Tests - Batch Producer
# =============================================================================


class TestProtocolEventBusBatchProducerEdgeCases:
    """Test edge cases for batch producer."""

    @pytest.mark.asyncio
    async def test_send_empty_batch(self) -> None:
        """Sending empty batch should work."""
        producer = CompliantEventBusBatchProducer()
        await producer.send_batch([])

    @pytest.mark.asyncio
    async def test_send_single_message_batch(self) -> None:
        """Sending batch with single message should work."""
        producer = CompliantEventBusBatchProducer()
        msg = CompliantEventBusMessage(value=b"data", topic="test")
        await producer.send_batch([cast(ProtocolEventBusMessage, msg)])

    @pytest.mark.asyncio
    async def test_send_to_partition_zero(self) -> None:
        """Sending to partition 0 should work."""
        producer = CompliantEventBusBatchProducer()
        await producer.send_to_partition(
            topic="test",
            partition=0,
            key=None,
            value=b"data",
        )

    @pytest.mark.asyncio
    async def test_send_with_null_key(self) -> None:
        """Sending with null key should work."""
        producer = CompliantEventBusBatchProducer()
        await producer.send_to_partition(
            topic="test",
            partition=0,
            key=None,
            value=b"data",
        )

    @pytest.mark.asyncio
    async def test_send_with_empty_headers(self) -> None:
        """Sending with empty headers dict should work."""
        producer = CompliantEventBusBatchProducer()
        await producer.send_to_partition(
            topic="test",
            partition=0,
            key=b"key",
            value=b"data",
            headers={},
        )

    @pytest.mark.asyncio
    async def test_flush_with_zero_timeout(self) -> None:
        """Flush with zero timeout should work."""
        producer = CompliantEventBusBatchProducer()
        await producer.flush_pending(timeout_ms=0)

    @pytest.mark.asyncio
    async def test_validate_compliant_message(self) -> None:
        """Validate a compliant message should return True."""
        producer = CompliantEventBusBatchProducer()
        msg = CompliantEventBusMessage(value=b"data", topic="test")
        result = await producer.validate_message(cast(ProtocolEventBusMessage, msg))
        assert result is True

    @pytest.mark.asyncio
    async def test_send_batch_with_multiple_messages(self) -> None:
        """Sending batch with multiple messages should work."""
        producer = CompliantEventBusBatchProducer()
        messages = [
            cast(
                ProtocolEventBusMessage,
                CompliantEventBusMessage(value=f"data-{i}".encode(), topic="test"),
            )
            for i in range(10)
        ]
        await producer.send_batch(messages)

    @pytest.mark.asyncio
    async def test_send_with_various_partitioning_strategies(self) -> None:
        """Sending with different partitioning strategies should work."""
        producer = CompliantEventBusBatchProducer()
        strategies = ["round_robin", "hash", "sticky", "random"]
        for strategy in strategies:
            await producer.send_with_custom_partitioner(
                topic="test",
                key=b"key",
                value=b"data",
                partition_strategy=strategy,
            )

    @pytest.mark.asyncio
    async def test_validate_connection_returns_bool(self) -> None:
        """validate_connection should return a boolean."""
        producer = CompliantEventBusBatchProducer()
        result = await producer.validate_connection()
        assert isinstance(result, bool)
        assert result is True
