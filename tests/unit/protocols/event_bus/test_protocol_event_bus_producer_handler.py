"""
Tests for ProtocolEventBusProducerHandler typed protocol changes.

This module validates that ProtocolEventBusProducerHandler:
- Is properly runtime checkable
- Defines required methods (send, send_batch, flush, close, health_check, etc.)
- send_batch accepts Sequence[ModelProducerMessage] (not dicts)
- All async methods are properly defined as coroutines
- Properties are correctly defined (handler_type, supports_transactions, supports_exactly_once)

These tests verify the typed-dynamic pattern introduced in PR #47 (OMN-710).
"""

import inspect
from collections.abc import Sequence
from typing import Protocol

import pytest

from omnibase_spi.protocols.event_bus.protocol_event_bus_producer_handler import (
    DeliveryCallback,
    ProtocolEventBusProducerHandler,
)

# =============================================================================
# Mock/Compliant Implementations for Testing
# =============================================================================


class MockProducerMessage:
    """
    Mock implementation of ModelProducerMessage for testing.

    This class simulates the typed message structure that send_batch accepts.
    The actual ModelProducerMessage comes from omnibase_core.models.event_bus.

    Attributes:
        topic: Target topic name
        value: Message payload as bytes
        key: Optional partition key
        headers: Optional message headers
        partition: Optional explicit partition
    """

    def __init__(
        self,
        topic: str = "test-topic",
        value: bytes = b'{"test": "data"}',
        key: bytes | None = None,
        headers: dict[str, bytes] | None = None,
        partition: int | None = None,
    ) -> None:
        """Initialize mock producer message."""
        self.topic = topic
        self.value = value
        self.key = key
        self.headers = headers
        self.partition = partition


class MockProducerHealthStatus:
    """
    Mock implementation of ModelProducerHealthStatus for testing.

    Simulates the typed health status returned by health_check().
    """

    def __init__(
        self,
        healthy: bool = True,
        latency_ms: float | None = 5.0,
        connected: bool = True,
        pending_messages: int = 0,
        last_error: str | None = None,
        messages_sent: int = 100,
        messages_failed: int = 0,
        broker_count: int = 3,
    ) -> None:
        """Initialize mock health status."""
        self.healthy = healthy
        self.latency_ms = latency_ms
        self.connected = connected
        self.pending_messages = pending_messages
        self.last_error = last_error
        self.last_error_timestamp = None
        self.messages_sent = messages_sent
        self.messages_failed = messages_failed
        self.broker_count = broker_count


class CompliantEventBusProducerHandler:
    """
    Test double implementing all ProtocolEventBusProducerHandler requirements.

    This mock demonstrates proper typed implementation:
    - send_batch accepts Sequence[ModelProducerMessage], not dicts
    - health_check returns ModelProducerHealthStatus, not dict
    - All required properties and methods are implemented
    """

    @property
    def handler_type(self) -> str:
        """Return handler type identifier."""
        return "event_bus_producer"

    @property
    def supports_transactions(self) -> bool:
        """Return whether transactions are supported."""
        return True

    @property
    def supports_exactly_once(self) -> bool:
        """Return whether exactly-once semantics are supported."""
        return True

    async def send(
        self,
        topic: str,
        value: bytes,
        key: bytes | None = None,
        headers: dict[str, bytes] | None = None,
        partition: int | None = None,
        on_success: DeliveryCallback | None = None,
        on_error: DeliveryCallback | None = None,
    ) -> None:
        """Send a single message."""
        _ = (topic, value, key, headers, partition, on_success, on_error)

    async def send_batch(
        self,
        messages: Sequence[MockProducerMessage],
        on_success: DeliveryCallback | None = None,
        on_error: DeliveryCallback | None = None,
    ) -> int:
        """
        Send batch of typed messages.

        Args:
            messages: Sequence of ModelProducerMessage (typed, not dicts).
            on_success: Optional success callback.
            on_error: Optional error callback.

        Returns:
            Number of messages queued.
        """
        _ = (on_success, on_error)
        return len(messages)

    async def flush(self, timeout_seconds: float = 30.0) -> None:
        """Flush pending messages."""
        _ = timeout_seconds

    async def close(self, timeout_seconds: float = 30.0) -> None:
        """Close the producer."""
        _ = timeout_seconds

    async def health_check(self) -> MockProducerHealthStatus:
        """Return typed health status."""
        return MockProducerHealthStatus(healthy=True)

    async def begin_transaction(self) -> None:
        """Begin a transaction."""
        pass

    async def commit_transaction(self) -> None:
        """Commit the current transaction."""
        pass

    async def abort_transaction(self) -> None:
        """Abort the current transaction."""
        pass


class PartialEventBusProducerHandler:
    """
    Test double implementing only some ProtocolEventBusProducerHandler methods.

    Missing methods (intentionally):
    - supports_exactly_once
    - send_batch
    - close
    - begin_transaction / commit_transaction / abort_transaction
    """

    @property
    def handler_type(self) -> str:
        """Return handler type."""
        return "event_bus_producer"

    @property
    def supports_transactions(self) -> bool:
        """Return transaction support."""
        return False

    async def send(
        self,
        topic: str,
        value: bytes,
        key: bytes | None = None,
        headers: dict[str, bytes] | None = None,
        partition: int | None = None,
        on_success: DeliveryCallback | None = None,
        on_error: DeliveryCallback | None = None,
    ) -> None:
        """Send a single message."""
        _ = (topic, value, key, headers, partition, on_success, on_error)

    async def flush(self, timeout_seconds: float = 30.0) -> None:
        """Flush pending messages."""
        _ = timeout_seconds

    async def health_check(self) -> MockProducerHealthStatus:
        """Return health status."""
        return MockProducerHealthStatus(healthy=True)


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def compliant_producer() -> CompliantEventBusProducerHandler:
    """Provide a compliant producer handler for testing."""
    return CompliantEventBusProducerHandler()


# =============================================================================
# Protocol Definition Tests
# =============================================================================


@pytest.mark.unit
class TestProtocolEventBusProducerHandlerProtocol:
    """Test suite for ProtocolEventBusProducerHandler protocol definition."""

    def test_protocol_is_runtime_checkable(self) -> None:
        """ProtocolEventBusProducerHandler should be runtime_checkable."""
        assert hasattr(
            ProtocolEventBusProducerHandler, "_is_runtime_protocol"
        ) or hasattr(ProtocolEventBusProducerHandler, "__runtime_protocol__")

    def test_protocol_is_protocol(self) -> None:
        """ProtocolEventBusProducerHandler should be a Protocol class."""
        assert any(
            base is Protocol or base.__name__ == "Protocol"
            for base in ProtocolEventBusProducerHandler.__mro__
        )

    def test_protocol_has_handler_type_property(self) -> None:
        """Should define handler_type property."""
        assert "handler_type" in dir(ProtocolEventBusProducerHandler)

    def test_protocol_has_supports_transactions_property(self) -> None:
        """Should define supports_transactions property."""
        assert "supports_transactions" in dir(ProtocolEventBusProducerHandler)

    def test_protocol_has_supports_exactly_once_property(self) -> None:
        """Should define supports_exactly_once property."""
        assert "supports_exactly_once" in dir(ProtocolEventBusProducerHandler)

    def test_protocol_has_send_method(self) -> None:
        """Should define send method."""
        assert "send" in dir(ProtocolEventBusProducerHandler)

    def test_protocol_has_send_batch_method(self) -> None:
        """Should define send_batch method."""
        assert "send_batch" in dir(ProtocolEventBusProducerHandler)

    def test_protocol_has_flush_method(self) -> None:
        """Should define flush method."""
        assert "flush" in dir(ProtocolEventBusProducerHandler)

    def test_protocol_has_close_method(self) -> None:
        """Should define close method."""
        assert "close" in dir(ProtocolEventBusProducerHandler)

    def test_protocol_has_health_check_method(self) -> None:
        """Should define health_check method."""
        assert "health_check" in dir(ProtocolEventBusProducerHandler)

    def test_protocol_has_begin_transaction_method(self) -> None:
        """Should define begin_transaction method."""
        assert "begin_transaction" in dir(ProtocolEventBusProducerHandler)

    def test_protocol_has_commit_transaction_method(self) -> None:
        """Should define commit_transaction method."""
        assert "commit_transaction" in dir(ProtocolEventBusProducerHandler)

    def test_protocol_has_abort_transaction_method(self) -> None:
        """Should define abort_transaction method."""
        assert "abort_transaction" in dir(ProtocolEventBusProducerHandler)

    def test_protocol_cannot_be_instantiated(self) -> None:
        """ProtocolEventBusProducerHandler should not be directly instantiable."""
        with pytest.raises(TypeError):
            ProtocolEventBusProducerHandler()  # type: ignore[misc]


# =============================================================================
# Protocol Compliance Tests
# =============================================================================


@pytest.mark.unit
class TestProtocolEventBusProducerHandlerCompliance:
    """Test isinstance checks for ProtocolEventBusProducerHandler compliance."""

    def test_compliant_class_passes_isinstance(
        self, compliant_producer: CompliantEventBusProducerHandler
    ) -> None:
        """A class implementing all methods should pass isinstance check."""
        assert isinstance(compliant_producer, ProtocolEventBusProducerHandler)

    def test_partial_implementation_fails_isinstance(self) -> None:
        """A class missing methods should fail isinstance check."""
        producer = PartialEventBusProducerHandler()
        assert not isinstance(producer, ProtocolEventBusProducerHandler)


# =============================================================================
# Typed send_batch Tests - Core PR #47 Changes
# =============================================================================


@pytest.mark.unit
class TestProtocolEventBusProducerHandlerSendBatch:
    """Test send_batch method accepts typed ModelProducerMessage.

    These tests verify the key change from PR #47: send_batch accepts
    Sequence[ModelProducerMessage] (typed models) instead of dicts.
    """

    @pytest.mark.asyncio
    async def test_send_batch_accepts_typed_messages(
        self, compliant_producer: CompliantEventBusProducerHandler
    ) -> None:
        """send_batch should accept Sequence[ModelProducerMessage]."""
        messages = [
            MockProducerMessage(topic="events", value=b"msg1", key=b"k1"),
            MockProducerMessage(topic="events", value=b"msg2", key=b"k2"),
        ]
        result = await compliant_producer.send_batch(messages)
        assert result == 2

    @pytest.mark.asyncio
    async def test_send_batch_accepts_empty_sequence(
        self, compliant_producer: CompliantEventBusProducerHandler
    ) -> None:
        """send_batch should accept empty sequences."""
        result = await compliant_producer.send_batch([])
        assert result == 0

    @pytest.mark.asyncio
    async def test_send_batch_accepts_single_message(
        self, compliant_producer: CompliantEventBusProducerHandler
    ) -> None:
        """send_batch should accept single-element sequences."""
        messages = [MockProducerMessage(topic="test", value=b"data")]
        result = await compliant_producer.send_batch(messages)
        assert result == 1

    @pytest.mark.asyncio
    async def test_send_batch_with_all_message_fields(
        self, compliant_producer: CompliantEventBusProducerHandler
    ) -> None:
        """send_batch should accept messages with all optional fields."""
        message = MockProducerMessage(
            topic="events",
            value=b'{"event": "test"}',
            key=b"partition-key",
            headers={"correlation_id": b"abc123"},
            partition=0,
        )
        result = await compliant_producer.send_batch([message])
        assert result == 1

    @pytest.mark.asyncio
    async def test_send_batch_returns_int(
        self, compliant_producer: CompliantEventBusProducerHandler
    ) -> None:
        """send_batch should return an integer count."""
        messages = [MockProducerMessage(topic="t", value=b"v") for _ in range(5)]
        result = await compliant_producer.send_batch(messages)
        assert isinstance(result, int)

    def test_send_batch_signature_accepts_sequence(self) -> None:
        """Verify send_batch signature shows Sequence type in annotations."""
        # Get the signature from the protocol
        send_batch_method = getattr(ProtocolEventBusProducerHandler, "send_batch", None)
        assert send_batch_method is not None

        sig = inspect.signature(send_batch_method)
        messages_param = sig.parameters.get("messages")
        assert messages_param is not None

        # The annotation should reference Sequence or list
        annotation = str(messages_param.annotation)
        # Should contain "Sequence" or similar collection type
        assert "Sequence" in annotation or "ModelProducerMessage" in annotation


# =============================================================================
# Async Method Tests
# =============================================================================


@pytest.mark.unit
class TestProtocolEventBusProducerHandlerAsyncNature:
    """Test that ProtocolEventBusProducerHandler methods are async."""

    def test_send_is_async(self) -> None:
        """send should be an async method."""
        protocol_method = getattr(ProtocolEventBusProducerHandler, "send", None)
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)
        assert inspect.iscoroutinefunction(CompliantEventBusProducerHandler.send)

    def test_send_batch_is_async(self) -> None:
        """send_batch should be an async method."""
        protocol_method = getattr(ProtocolEventBusProducerHandler, "send_batch", None)
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)
        assert inspect.iscoroutinefunction(CompliantEventBusProducerHandler.send_batch)

    def test_flush_is_async(self) -> None:
        """flush should be an async method."""
        protocol_method = getattr(ProtocolEventBusProducerHandler, "flush", None)
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)
        assert inspect.iscoroutinefunction(CompliantEventBusProducerHandler.flush)

    def test_close_is_async(self) -> None:
        """close should be an async method."""
        protocol_method = getattr(ProtocolEventBusProducerHandler, "close", None)
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)
        assert inspect.iscoroutinefunction(CompliantEventBusProducerHandler.close)

    def test_health_check_is_async(self) -> None:
        """health_check should be an async method."""
        protocol_method = getattr(ProtocolEventBusProducerHandler, "health_check", None)
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)
        assert inspect.iscoroutinefunction(
            CompliantEventBusProducerHandler.health_check
        )

    def test_begin_transaction_is_async(self) -> None:
        """begin_transaction should be an async method."""
        protocol_method = getattr(
            ProtocolEventBusProducerHandler, "begin_transaction", None
        )
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)

    def test_commit_transaction_is_async(self) -> None:
        """commit_transaction should be an async method."""
        protocol_method = getattr(
            ProtocolEventBusProducerHandler, "commit_transaction", None
        )
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)

    def test_abort_transaction_is_async(self) -> None:
        """abort_transaction should be an async method."""
        protocol_method = getattr(
            ProtocolEventBusProducerHandler, "abort_transaction", None
        )
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)


# =============================================================================
# Property Tests
# =============================================================================


@pytest.mark.unit
class TestProtocolEventBusProducerHandlerProperties:
    """Test property definitions and values."""

    def test_handler_type_returns_string(
        self, compliant_producer: CompliantEventBusProducerHandler
    ) -> None:
        """handler_type should return a string."""
        assert isinstance(compliant_producer.handler_type, str)
        assert compliant_producer.handler_type == "event_bus_producer"

    def test_supports_transactions_returns_bool(
        self, compliant_producer: CompliantEventBusProducerHandler
    ) -> None:
        """supports_transactions should return a boolean."""
        assert isinstance(compliant_producer.supports_transactions, bool)

    def test_supports_exactly_once_returns_bool(
        self, compliant_producer: CompliantEventBusProducerHandler
    ) -> None:
        """supports_exactly_once should return a boolean."""
        assert isinstance(compliant_producer.supports_exactly_once, bool)


# =============================================================================
# Health Check Typed Return Tests
# =============================================================================


@pytest.mark.unit
class TestProtocolEventBusProducerHandlerHealthCheck:
    """Test health_check returns typed ModelProducerHealthStatus."""

    @pytest.mark.asyncio
    async def test_health_check_returns_typed_status(
        self, compliant_producer: CompliantEventBusProducerHandler
    ) -> None:
        """health_check should return typed health status object."""
        health = await compliant_producer.health_check()
        # Should be an object with typed attributes, not a dict
        assert hasattr(health, "healthy")
        assert hasattr(health, "connected")
        assert hasattr(health, "pending_messages")

    @pytest.mark.asyncio
    async def test_health_check_healthy_is_bool(
        self, compliant_producer: CompliantEventBusProducerHandler
    ) -> None:
        """health_check.healthy should be a boolean."""
        health = await compliant_producer.health_check()
        assert isinstance(health.healthy, bool)

    @pytest.mark.asyncio
    async def test_health_check_has_metrics(
        self, compliant_producer: CompliantEventBusProducerHandler
    ) -> None:
        """health_check should include message metrics."""
        health = await compliant_producer.health_check()
        assert hasattr(health, "messages_sent")
        assert hasattr(health, "messages_failed")


# =============================================================================
# Transaction Workflow Tests
# =============================================================================


@pytest.mark.unit
class TestProtocolEventBusProducerHandlerTransactions:
    """Test transaction-related methods."""

    @pytest.mark.asyncio
    async def test_transaction_workflow(
        self, compliant_producer: CompliantEventBusProducerHandler
    ) -> None:
        """Test complete transaction workflow."""
        await compliant_producer.begin_transaction()
        # Send messages (would be part of transaction)
        await compliant_producer.send(topic="events", value=b"data")
        await compliant_producer.commit_transaction()

    @pytest.mark.asyncio
    async def test_transaction_abort_workflow(
        self, compliant_producer: CompliantEventBusProducerHandler
    ) -> None:
        """Test transaction abort workflow."""
        await compliant_producer.begin_transaction()
        await compliant_producer.send(topic="events", value=b"data")
        await compliant_producer.abort_transaction()


# =============================================================================
# Import Tests
# =============================================================================


@pytest.mark.unit
class TestProtocolEventBusProducerHandlerImports:
    """Test protocol imports from different locations."""

    def test_import_from_protocol_module(self) -> None:
        """Test direct import from protocol module."""
        from omnibase_spi.protocols.event_bus.protocol_event_bus_producer_handler import (
            ProtocolEventBusProducerHandler as DirectProtocol,
        )

        producer = CompliantEventBusProducerHandler()
        assert isinstance(producer, DirectProtocol)

    def test_import_from_event_bus_package(self) -> None:
        """Test import from event_bus package."""
        from omnibase_spi.protocols.event_bus import (
            ProtocolEventBusProducerHandler as PackageProtocol,
        )

        producer = CompliantEventBusProducerHandler()
        assert isinstance(producer, PackageProtocol)

    def test_delivery_callback_is_importable(self) -> None:
        """Test DeliveryCallback type alias is importable."""
        from omnibase_spi.protocols.event_bus.protocol_event_bus_producer_handler import (
            DeliveryCallback,
        )

        assert DeliveryCallback is not None


# =============================================================================
# Documentation Tests
# =============================================================================


@pytest.mark.unit
class TestProtocolEventBusProducerHandlerDocumentation:
    """Test that protocol has proper documentation."""

    def test_protocol_has_docstring(self) -> None:
        """ProtocolEventBusProducerHandler should have a docstring."""
        assert ProtocolEventBusProducerHandler.__doc__ is not None
        assert len(ProtocolEventBusProducerHandler.__doc__.strip()) > 0

    def test_send_batch_has_docstring(self) -> None:
        """send_batch method should have a docstring."""
        method = getattr(ProtocolEventBusProducerHandler, "send_batch", None)
        assert method is not None
        assert method.__doc__ is not None
        # Should mention ModelProducerMessage in the docstring
        assert "ModelProducerMessage" in method.__doc__
