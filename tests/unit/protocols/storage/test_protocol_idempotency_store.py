"""
Tests for ProtocolIdempotencyStore protocol.

Validates that ProtocolIdempotencyStore:
- Is properly runtime checkable
- Defines required methods (check_and_record, is_processed, mark_processed, cleanup_expired)
- Methods have correct signatures
- Cannot be instantiated directly
- Works correctly with isinstance checks for compliant/non-compliant classes
"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from omnibase_spi.protocols.storage.protocol_idempotency_store import (
    ProtocolIdempotencyStore,
)


class MockIdempotencyStore:
    """A class that fully implements the ProtocolIdempotencyStore protocol.

    This mock implementation provides an in-memory store for testing.
    It demonstrates how a compliant implementation should behave.
    """

    def __init__(self) -> None:
        """Initialize the mock store with an empty processed set."""
        self._processed: dict[tuple[str | None, UUID], datetime] = {}

    async def check_and_record(
        self,
        message_id: UUID,
        domain: str | None = None,
        correlation_id: UUID | None = None,
    ) -> bool:
        """
        Atomically check if message was processed and record if not.

        Args:
            message_id: Unique identifier for the message.
            domain: Optional domain namespace for isolated deduplication.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            True if message is new (should be processed).
            False if message is duplicate (should be skipped).
        """
        key = (domain, message_id)
        if key in self._processed:
            return False
        self._processed[key] = datetime.now(UTC)
        return True

    async def is_processed(
        self,
        message_id: UUID,
        domain: str | None = None,
    ) -> bool:
        """
        Check if a message was already processed.

        Args:
            message_id: Unique identifier for the message.
            domain: Optional domain namespace.

        Returns:
            True if the message has been processed.
            False if the message has not been processed.
        """
        key = (domain, message_id)
        return key in self._processed

    async def mark_processed(
        self,
        message_id: UUID,
        domain: str | None = None,
        correlation_id: UUID | None = None,
        processed_at: datetime | None = None,
    ) -> None:
        """
        Mark a message as processed.

        Args:
            message_id: Unique identifier for the message.
            domain: Optional domain namespace.
            correlation_id: Optional correlation ID for tracing.
            processed_at: Optional timestamp of when processing occurred.
        """
        key = (domain, message_id)
        self._processed[key] = processed_at or datetime.now(UTC)

    async def cleanup_expired(
        self,
        ttl_seconds: int,
    ) -> int:
        """
        Remove entries older than TTL.

        Args:
            ttl_seconds: Time-to-live in seconds.

        Returns:
            Number of entries removed.
        """
        now = datetime.now(UTC)
        expired_keys = [
            key
            for key, processed_at in self._processed.items()
            if (now - processed_at).total_seconds() > ttl_seconds
        ]
        for key in expired_keys:
            del self._processed[key]
        return len(expired_keys)


class PartialIdempotencyStore:
    """A class that only implements some ProtocolIdempotencyStore methods."""

    async def check_and_record(
        self,
        message_id: UUID,
        domain: str | None = None,
        correlation_id: UUID | None = None,
    ) -> bool:
        """Only implement check_and_record, missing other methods."""
        return True


class NonCompliantStore:
    """A class that implements none of the ProtocolIdempotencyStore methods."""

    pass


@pytest.mark.unit
class TestProtocolIdempotencyStoreProtocol:
    """Test suite for ProtocolIdempotencyStore protocol compliance."""

    def test_protocol_is_runtime_checkable(self) -> None:
        """ProtocolIdempotencyStore should be runtime_checkable."""
        # Python 3.11+ uses _is_runtime_protocol, older versions use __runtime_protocol__
        assert hasattr(ProtocolIdempotencyStore, "_is_runtime_protocol") or hasattr(
            ProtocolIdempotencyStore, "__runtime_protocol__"
        )

    def test_protocol_is_protocol(self) -> None:
        """ProtocolIdempotencyStore should be a Protocol class."""
        from typing import Protocol

        # Check that ProtocolIdempotencyStore has Protocol in its bases
        assert any(
            base is Protocol or base.__name__ == "Protocol"
            for base in ProtocolIdempotencyStore.__mro__
        )

    def test_protocol_has_check_and_record_method(self) -> None:
        """ProtocolIdempotencyStore should define check_and_record method."""
        assert "check_and_record" in dir(ProtocolIdempotencyStore)

    def test_protocol_has_is_processed_method(self) -> None:
        """ProtocolIdempotencyStore should define is_processed method."""
        assert "is_processed" in dir(ProtocolIdempotencyStore)

    def test_protocol_has_mark_processed_method(self) -> None:
        """ProtocolIdempotencyStore should define mark_processed method."""
        assert "mark_processed" in dir(ProtocolIdempotencyStore)

    def test_protocol_has_cleanup_expired_method(self) -> None:
        """ProtocolIdempotencyStore should define cleanup_expired method."""
        assert "cleanup_expired" in dir(ProtocolIdempotencyStore)

    def test_protocol_cannot_be_instantiated(self) -> None:
        """ProtocolIdempotencyStore protocol should not be directly instantiable."""
        with pytest.raises(TypeError):
            ProtocolIdempotencyStore()  # type: ignore[misc]


@pytest.mark.unit
class TestProtocolIdempotencyStoreCompliance:
    """Test isinstance checks for protocol compliance."""

    def test_compliant_class_passes_isinstance(self) -> None:
        """A class implementing all ProtocolIdempotencyStore methods should pass isinstance check."""
        store = MockIdempotencyStore()
        assert isinstance(store, ProtocolIdempotencyStore)

    def test_partial_implementation_fails_isinstance(self) -> None:
        """A class missing ProtocolIdempotencyStore methods should fail isinstance check."""
        store = PartialIdempotencyStore()
        assert not isinstance(store, ProtocolIdempotencyStore)

    def test_non_compliant_class_fails_isinstance(self) -> None:
        """A class with no ProtocolIdempotencyStore methods should fail isinstance check."""
        store = NonCompliantStore()
        assert not isinstance(store, ProtocolIdempotencyStore)


@pytest.mark.unit
class TestMockImplementsAllMethods:
    """Test that MockIdempotencyStore has all required methods."""

    def test_mock_has_check_and_record(self) -> None:
        """Mock should have check_and_record method."""
        store = MockIdempotencyStore()
        assert hasattr(store, "check_and_record")
        assert callable(store.check_and_record)

    def test_mock_has_is_processed(self) -> None:
        """Mock should have is_processed method."""
        store = MockIdempotencyStore()
        assert hasattr(store, "is_processed")
        assert callable(store.is_processed)

    def test_mock_has_mark_processed(self) -> None:
        """Mock should have mark_processed method."""
        store = MockIdempotencyStore()
        assert hasattr(store, "mark_processed")
        assert callable(store.mark_processed)

    def test_mock_has_cleanup_expired(self) -> None:
        """Mock should have cleanup_expired method."""
        store = MockIdempotencyStore()
        assert hasattr(store, "cleanup_expired")
        assert callable(store.cleanup_expired)


@pytest.mark.unit
class TestProtocolIdempotencyStoreAsyncNature:
    """Test that ProtocolIdempotencyStore methods are async."""

    def test_check_and_record_is_async(self) -> None:
        """check_and_record should be an async method."""
        import inspect

        assert inspect.iscoroutinefunction(MockIdempotencyStore.check_and_record)

    def test_is_processed_is_async(self) -> None:
        """is_processed should be an async method."""
        import inspect

        assert inspect.iscoroutinefunction(MockIdempotencyStore.is_processed)

    def test_mark_processed_is_async(self) -> None:
        """mark_processed should be an async method."""
        import inspect

        assert inspect.iscoroutinefunction(MockIdempotencyStore.mark_processed)

    def test_cleanup_expired_is_async(self) -> None:
        """cleanup_expired should be an async method."""
        import inspect

        assert inspect.iscoroutinefunction(MockIdempotencyStore.cleanup_expired)


@pytest.mark.unit
class TestProtocolIdempotencyStoreMethodSignatures:
    """Test method signatures from compliant mock implementation."""

    @pytest.mark.asyncio
    async def test_check_and_record_accepts_required_params(self) -> None:
        """check_and_record should accept message_id with optional domain and correlation_id."""
        store = MockIdempotencyStore()
        message_id = uuid4()

        # Should not raise with required param only
        result = await store.check_and_record(message_id)
        assert isinstance(result, bool)
        assert result is True

    @pytest.mark.asyncio
    async def test_check_and_record_accepts_all_params(self) -> None:
        """check_and_record should accept all parameters."""
        store = MockIdempotencyStore()
        message_id = uuid4()
        correlation_id = uuid4()

        result = await store.check_and_record(
            message_id=message_id,
            domain="test-domain",
            correlation_id=correlation_id,
        )
        assert isinstance(result, bool)

    @pytest.mark.asyncio
    async def test_is_processed_accepts_message_id_and_domain(self) -> None:
        """is_processed should accept message_id and optional domain."""
        store = MockIdempotencyStore()
        message_id = uuid4()

        result = await store.is_processed(message_id)
        assert isinstance(result, bool)
        assert result is False

        result = await store.is_processed(message_id, domain="test-domain")
        assert isinstance(result, bool)

    @pytest.mark.asyncio
    async def test_mark_processed_accepts_all_params(self) -> None:
        """mark_processed should accept message_id and optional params."""
        store = MockIdempotencyStore()
        message_id = uuid4()
        correlation_id = uuid4()
        processed_at = datetime.now(UTC)

        # Should not raise
        await store.mark_processed(
            message_id=message_id,
            domain="test-domain",
            correlation_id=correlation_id,
            processed_at=processed_at,
        )

    @pytest.mark.asyncio
    async def test_cleanup_expired_accepts_ttl_seconds(self) -> None:
        """cleanup_expired should accept ttl_seconds and return int."""
        store = MockIdempotencyStore()

        result = await store.cleanup_expired(ttl_seconds=86400)
        assert isinstance(result, int)
        assert result >= 0


@pytest.mark.unit
class TestProtocolIdempotencyStoreImports:
    """Test protocol imports from different locations."""

    def test_import_from_protocol_module(self) -> None:
        """Test direct import from protocol_idempotency_store module."""
        from omnibase_spi.protocols.storage.protocol_idempotency_store import (
            ProtocolIdempotencyStore as DirectProtocolIdempotencyStore,
        )

        store = MockIdempotencyStore()
        assert isinstance(store, DirectProtocolIdempotencyStore)

    def test_import_from_storage_package(self) -> None:
        """Test import from storage package."""
        from omnibase_spi.protocols.storage import (
            ProtocolIdempotencyStore as StorageProtocolIdempotencyStore,
        )

        store = MockIdempotencyStore()
        assert isinstance(store, StorageProtocolIdempotencyStore)

    def test_import_from_protocols_package(self) -> None:
        """Test import from protocols root package."""
        from omnibase_spi.protocols import (
            ProtocolIdempotencyStore as ProtocolsIdempotencyStore,
        )

        store = MockIdempotencyStore()
        assert isinstance(store, ProtocolsIdempotencyStore)

    def test_imports_are_identical(self) -> None:
        """Verify imports from different locations are the same class."""
        from omnibase_spi.protocols import (
            ProtocolIdempotencyStore as ProtocolsIdempotencyStore,
        )
        from omnibase_spi.protocols.storage import (
            ProtocolIdempotencyStore as StorageProtocolIdempotencyStore,
        )
        from omnibase_spi.protocols.storage.protocol_idempotency_store import (
            ProtocolIdempotencyStore as DirectProtocolIdempotencyStore,
        )

        assert DirectProtocolIdempotencyStore is StorageProtocolIdempotencyStore
        assert StorageProtocolIdempotencyStore is ProtocolsIdempotencyStore


@pytest.mark.unit
class TestProtocolIdempotencyStoreDocumentation:
    """Test that ProtocolIdempotencyStore has proper documentation."""

    def test_protocol_has_docstring(self) -> None:
        """ProtocolIdempotencyStore should have a docstring."""
        assert ProtocolIdempotencyStore.__doc__ is not None
        assert len(ProtocolIdempotencyStore.__doc__.strip()) > 0

    def test_mock_check_and_record_has_docstring(self) -> None:
        """check_and_record method should have a docstring."""
        assert MockIdempotencyStore.check_and_record.__doc__ is not None

    def test_mock_is_processed_has_docstring(self) -> None:
        """is_processed method should have a docstring."""
        assert MockIdempotencyStore.is_processed.__doc__ is not None

    def test_mock_mark_processed_has_docstring(self) -> None:
        """mark_processed method should have a docstring."""
        assert MockIdempotencyStore.mark_processed.__doc__ is not None

    def test_mock_cleanup_expired_has_docstring(self) -> None:
        """cleanup_expired method should have a docstring."""
        assert MockIdempotencyStore.cleanup_expired.__doc__ is not None
