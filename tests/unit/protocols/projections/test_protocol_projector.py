"""
Tests for ProtocolProjector protocol.

Validates that ProtocolProjector and related protocols:
- Are properly runtime checkable
- Define required methods with correct signatures
- Cannot be instantiated directly
- Work correctly with isinstance checks for compliant/non-compliant classes
- Support the sequence-based ordering semantics
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Literal

import pytest

from omnibase_spi.protocols.projections.protocol_projector import (
    ProtocolBatchPersistResult,
    ProtocolPersistResult,
    ProtocolProjector,
    ProtocolSequenceInfo,
)


class MockSequenceInfo:
    """A class that fully implements the ProtocolSequenceInfo protocol."""

    def __init__(self, sequence: int, partition: str | None = None) -> None:
        """Initialize the mock sequence info."""
        self._sequence = sequence
        self._partition = partition

    @property
    def sequence(self) -> int:
        """Return the sequence number."""
        return self._sequence

    @property
    def partition(self) -> str | None:
        """Return the partition identifier."""
        return self._partition


class MockPersistResult:
    """A class that fully implements the ProtocolPersistResult protocol."""

    def __init__(
        self,
        status: Literal["applied", "rejected_stale", "rejected_conflict"],
        entity_id: str,
        applied_sequence: int | None = None,
        rejected_reason: str | None = None,
    ) -> None:
        """Initialize the mock persist result."""
        self._status = status
        self._entity_id = entity_id
        self._applied_sequence = applied_sequence
        self._rejected_reason = rejected_reason

    @property
    def status(self) -> Literal["applied", "rejected_stale", "rejected_conflict"]:
        """Return the persist operation status."""
        return self._status

    @property
    def entity_id(self) -> str:
        """Return the entity ID."""
        return self._entity_id

    @property
    def applied_sequence(self) -> int | None:
        """Return the applied sequence number."""
        return self._applied_sequence

    @property
    def rejected_reason(self) -> str | None:
        """Return the rejection reason."""
        return self._rejected_reason


class MockBatchPersistResult:
    """A class that fully implements the ProtocolBatchPersistResult protocol."""

    def __init__(
        self,
        total_count: int,
        applied_count: int,
        rejected_count: int,
        results: Sequence[ProtocolPersistResult],
    ) -> None:
        """Initialize the mock batch persist result."""
        self._total_count = total_count
        self._applied_count = applied_count
        self._rejected_count = rejected_count
        self._results = results

    @property
    def total_count(self) -> int:
        """Return total count of projections."""
        return self._total_count

    @property
    def applied_count(self) -> int:
        """Return count of applied projections."""
        return self._applied_count

    @property
    def rejected_count(self) -> int:
        """Return count of rejected projections."""
        return self._rejected_count

    @property
    def results(self) -> Sequence[ProtocolPersistResult]:
        """Return individual results."""
        return self._results


class MockProjector:
    """A class that fully implements the ProtocolProjector protocol.

    This mock implementation provides an in-memory projector for testing.
    It demonstrates how a compliant implementation should behave.
    """

    def __init__(self) -> None:
        """Initialize the mock projector with empty sequence tracking."""
        # Maps (entity_id, domain) -> last applied sequence info
        self._sequences: dict[tuple[str, str], MockSequenceInfo] = {}
        # Maps (entity_id, domain) -> projection data
        self._projections: dict[tuple[str, str], object] = {}

    async def persist(
        self,
        projection: object,
        entity_id: str,
        domain: str,
        sequence_info: ProtocolSequenceInfo,
        *,
        correlation_id: str | None = None,
    ) -> ProtocolPersistResult:
        """
        Persist a single projection with ordering enforcement.

        Args:
            projection: The projection data to persist.
            entity_id: Unique identifier for the entity.
            domain: Domain namespace for the projection.
            sequence_info: Sequence information for ordering.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            PersistResult indicating success or rejection.
        """
        key = (entity_id, domain)
        last_seq = self._sequences.get(key)

        if last_seq is not None and sequence_info.sequence <= last_seq.sequence:
            return MockPersistResult(
                status="rejected_stale",
                entity_id=entity_id,
                rejected_reason=(
                    f"Sequence {sequence_info.sequence} <= "
                    f"last applied {last_seq.sequence}"
                ),
            )

        # Apply the projection
        self._projections[key] = projection
        self._sequences[key] = MockSequenceInfo(
            sequence=sequence_info.sequence,
            partition=sequence_info.partition,
        )

        return MockPersistResult(
            status="applied",
            entity_id=entity_id,
            applied_sequence=sequence_info.sequence,
        )

    async def batch_persist(
        self,
        projections: Sequence[tuple[object, str, str, ProtocolSequenceInfo]],
        *,
        correlation_id: str | None = None,
    ) -> ProtocolBatchPersistResult:
        """
        Persist multiple projections in a batch operation.

        Args:
            projections: Sequence of (projection, entity_id, domain, sequence_info).
            correlation_id: Optional correlation ID for tracing.

        Returns:
            BatchPersistResult with summary and individual results.
        """
        results: list[ProtocolPersistResult] = []
        applied = 0
        rejected = 0

        for projection, entity_id, domain, seq_info in projections:
            result = await self.persist(
                projection=projection,
                entity_id=entity_id,
                domain=domain,
                sequence_info=seq_info,
                correlation_id=correlation_id,
            )
            results.append(result)
            if result.status == "applied":
                applied += 1
            else:
                rejected += 1

        return MockBatchPersistResult(
            total_count=len(projections),
            applied_count=applied,
            rejected_count=rejected,
            results=results,
        )

    async def get_last_sequence(
        self,
        entity_id: str,
        domain: str,
    ) -> ProtocolSequenceInfo | None:
        """
        Get the last applied sequence for an entity.

        Args:
            entity_id: Unique identifier for the entity.
            domain: Domain namespace for the projection.

        Returns:
            SequenceInfo for the last applied projection, or None.
        """
        key = (entity_id, domain)
        return self._sequences.get(key)

    async def is_stale(
        self,
        entity_id: str,
        domain: str,
        sequence_info: ProtocolSequenceInfo,
    ) -> bool:
        """
        Check if a sequence would be rejected as stale.

        Args:
            entity_id: Unique identifier for the entity.
            domain: Domain namespace for the projection.
            sequence_info: Sequence information to check.

        Returns:
            True if the sequence is stale, False otherwise.
        """
        key = (entity_id, domain)
        last_seq = self._sequences.get(key)
        if last_seq is None:
            return False
        return sequence_info.sequence <= last_seq.sequence

    async def cleanup_before_sequence(
        self,
        domain: str,
        sequence: int,
        *,
        batch_size: int = 1000,
        confirmed: bool = False,
    ) -> int:
        """
        Remove sequence tracking entries older than the given sequence.

        Args:
            domain: Domain namespace to clean up.
            sequence: Remove tracking for sequences < this value.
            batch_size: Maximum entries to remove per batch.
            confirmed: Safety confirmation for destructive cleanup. This mock
                does not enforce the confirmation flag.

        Returns:
            Number of tracking entries removed.
        """
        keys_to_remove = [
            key
            for key, seq_info in self._sequences.items()
            if key[1] == domain and seq_info.sequence < sequence
        ]
        for key in keys_to_remove[:batch_size]:
            del self._sequences[key]
            if key in self._projections:
                del self._projections[key]
        return len(keys_to_remove[:batch_size])


class PartialProjector:
    """A class that only implements some ProtocolProjector methods."""

    async def persist(
        self,
        projection: object,
        entity_id: str,
        domain: str,
        sequence_info: ProtocolSequenceInfo,
        *,
        correlation_id: str | None = None,
    ) -> ProtocolPersistResult:
        """Only implement persist, missing other methods."""
        return MockPersistResult(status="applied", entity_id=entity_id)


class NonCompliantProjector:
    """A class that implements none of the ProtocolProjector methods."""

    pass


class TestProtocolSequenceInfoProtocol:
    """Test suite for ProtocolSequenceInfo protocol compliance."""

    def test_protocol_is_runtime_checkable(self) -> None:
        """ProtocolSequenceInfo should be runtime_checkable."""
        assert hasattr(ProtocolSequenceInfo, "_is_runtime_protocol") or hasattr(
            ProtocolSequenceInfo, "__runtime_protocol__"
        )

    def test_protocol_is_protocol(self) -> None:
        """ProtocolSequenceInfo should be a Protocol class."""
        from typing import Protocol

        assert any(
            base is Protocol or base.__name__ == "Protocol"
            for base in ProtocolSequenceInfo.__mro__
        )

    def test_protocol_has_sequence_property(self) -> None:
        """ProtocolSequenceInfo should define sequence property."""
        assert "sequence" in dir(ProtocolSequenceInfo)

    def test_protocol_has_partition_property(self) -> None:
        """ProtocolSequenceInfo should define partition property."""
        assert "partition" in dir(ProtocolSequenceInfo)

    def test_compliant_class_passes_isinstance(self) -> None:
        """A class implementing all properties should pass isinstance check."""
        seq_info = MockSequenceInfo(sequence=42, partition="part-0")
        assert isinstance(seq_info, ProtocolSequenceInfo)


class TestProtocolPersistResultProtocol:
    """Test suite for ProtocolPersistResult protocol compliance."""

    def test_protocol_is_runtime_checkable(self) -> None:
        """ProtocolPersistResult should be runtime_checkable."""
        assert hasattr(ProtocolPersistResult, "_is_runtime_protocol") or hasattr(
            ProtocolPersistResult, "__runtime_protocol__"
        )

    def test_protocol_has_status_property(self) -> None:
        """ProtocolPersistResult should define status property."""
        assert "status" in dir(ProtocolPersistResult)

    def test_protocol_has_entity_id_property(self) -> None:
        """ProtocolPersistResult should define entity_id property."""
        assert "entity_id" in dir(ProtocolPersistResult)

    def test_protocol_has_applied_sequence_property(self) -> None:
        """ProtocolPersistResult should define applied_sequence property."""
        assert "applied_sequence" in dir(ProtocolPersistResult)

    def test_protocol_has_rejected_reason_property(self) -> None:
        """ProtocolPersistResult should define rejected_reason property."""
        assert "rejected_reason" in dir(ProtocolPersistResult)

    def test_compliant_class_passes_isinstance(self) -> None:
        """A class implementing all properties should pass isinstance check."""
        result = MockPersistResult(status="applied", entity_id="e1", applied_sequence=1)
        assert isinstance(result, ProtocolPersistResult)


class TestProtocolBatchPersistResultProtocol:
    """Test suite for ProtocolBatchPersistResult protocol compliance."""

    def test_protocol_is_runtime_checkable(self) -> None:
        """ProtocolBatchPersistResult should be runtime_checkable."""
        assert hasattr(ProtocolBatchPersistResult, "_is_runtime_protocol") or hasattr(
            ProtocolBatchPersistResult, "__runtime_protocol__"
        )

    def test_protocol_has_total_count_property(self) -> None:
        """ProtocolBatchPersistResult should define total_count property."""
        assert "total_count" in dir(ProtocolBatchPersistResult)

    def test_protocol_has_applied_count_property(self) -> None:
        """ProtocolBatchPersistResult should define applied_count property."""
        assert "applied_count" in dir(ProtocolBatchPersistResult)

    def test_protocol_has_rejected_count_property(self) -> None:
        """ProtocolBatchPersistResult should define rejected_count property."""
        assert "rejected_count" in dir(ProtocolBatchPersistResult)

    def test_protocol_has_results_property(self) -> None:
        """ProtocolBatchPersistResult should define results property."""
        assert "results" in dir(ProtocolBatchPersistResult)

    def test_compliant_class_passes_isinstance(self) -> None:
        """A class implementing all properties should pass isinstance check."""
        result = MockBatchPersistResult(
            total_count=1,
            applied_count=1,
            rejected_count=0,
            results=[],
        )
        assert isinstance(result, ProtocolBatchPersistResult)


class TestProtocolProjectorProtocol:
    """Test suite for ProtocolProjector protocol compliance."""

    def test_protocol_is_runtime_checkable(self) -> None:
        """ProtocolProjector should be runtime_checkable."""
        assert hasattr(ProtocolProjector, "_is_runtime_protocol") or hasattr(
            ProtocolProjector, "__runtime_protocol__"
        )

    def test_protocol_is_protocol(self) -> None:
        """ProtocolProjector should be a Protocol class."""
        from typing import Protocol

        assert any(
            base is Protocol or base.__name__ == "Protocol"
            for base in ProtocolProjector.__mro__
        )

    def test_protocol_has_persist_method(self) -> None:
        """ProtocolProjector should define persist method."""
        assert "persist" in dir(ProtocolProjector)

    def test_protocol_has_batch_persist_method(self) -> None:
        """ProtocolProjector should define batch_persist method."""
        assert "batch_persist" in dir(ProtocolProjector)

    def test_protocol_has_get_last_sequence_method(self) -> None:
        """ProtocolProjector should define get_last_sequence method."""
        assert "get_last_sequence" in dir(ProtocolProjector)

    def test_protocol_has_is_stale_method(self) -> None:
        """ProtocolProjector should define is_stale method."""
        assert "is_stale" in dir(ProtocolProjector)

    def test_protocol_has_cleanup_before_sequence_method(self) -> None:
        """ProtocolProjector should define cleanup_before_sequence method."""
        assert "cleanup_before_sequence" in dir(ProtocolProjector)

    def test_protocol_cannot_be_instantiated(self) -> None:
        """ProtocolProjector protocol should not be directly instantiable."""
        with pytest.raises(TypeError):
            ProtocolProjector()  # type: ignore[misc]


class TestProtocolProjectorCompliance:
    """Test isinstance checks for protocol compliance."""

    def test_compliant_class_passes_isinstance(self) -> None:
        """A class implementing all ProtocolProjector methods should pass isinstance check."""
        projector = MockProjector()
        assert isinstance(projector, ProtocolProjector)

    def test_partial_implementation_fails_isinstance(self) -> None:
        """A class missing ProtocolProjector methods should fail isinstance check."""
        projector = PartialProjector()
        assert not isinstance(projector, ProtocolProjector)

    def test_non_compliant_class_fails_isinstance(self) -> None:
        """A class with no ProtocolProjector methods should fail isinstance check."""
        projector = NonCompliantProjector()
        assert not isinstance(projector, ProtocolProjector)


class TestMockImplementsAllMethods:
    """Test that MockProjector has all required methods."""

    def test_mock_has_persist(self) -> None:
        """Mock should have persist method."""
        projector = MockProjector()
        assert hasattr(projector, "persist")
        assert callable(projector.persist)

    def test_mock_has_batch_persist(self) -> None:
        """Mock should have batch_persist method."""
        projector = MockProjector()
        assert hasattr(projector, "batch_persist")
        assert callable(projector.batch_persist)

    def test_mock_has_get_last_sequence(self) -> None:
        """Mock should have get_last_sequence method."""
        projector = MockProjector()
        assert hasattr(projector, "get_last_sequence")
        assert callable(projector.get_last_sequence)

    def test_mock_has_is_stale(self) -> None:
        """Mock should have is_stale method."""
        projector = MockProjector()
        assert hasattr(projector, "is_stale")
        assert callable(projector.is_stale)

    def test_mock_has_cleanup_before_sequence(self) -> None:
        """Mock should have cleanup_before_sequence method."""
        projector = MockProjector()
        assert hasattr(projector, "cleanup_before_sequence")
        assert callable(projector.cleanup_before_sequence)


class TestProtocolProjectorAsyncNature:
    """Test that ProtocolProjector methods are async."""

    def test_persist_is_async(self) -> None:
        """persist should be an async method."""
        import inspect

        assert inspect.iscoroutinefunction(MockProjector.persist)

    def test_batch_persist_is_async(self) -> None:
        """batch_persist should be an async method."""
        import inspect

        assert inspect.iscoroutinefunction(MockProjector.batch_persist)

    def test_get_last_sequence_is_async(self) -> None:
        """get_last_sequence should be an async method."""
        import inspect

        assert inspect.iscoroutinefunction(MockProjector.get_last_sequence)

    def test_is_stale_is_async(self) -> None:
        """is_stale should be an async method."""
        import inspect

        assert inspect.iscoroutinefunction(MockProjector.is_stale)

    def test_cleanup_before_sequence_is_async(self) -> None:
        """cleanup_before_sequence should be an async method."""
        import inspect

        assert inspect.iscoroutinefunction(MockProjector.cleanup_before_sequence)


class TestProtocolProjectorMethodSignatures:
    """Test method signatures from compliant mock implementation."""

    @pytest.mark.asyncio
    async def test_persist_accepts_required_params(self) -> None:
        """persist should accept projection, entity_id, domain, sequence_info."""
        projector = MockProjector()
        seq_info = MockSequenceInfo(sequence=1)

        result = await projector.persist(
            projection={"key": "value"},
            entity_id="entity-1",
            domain="test-domain",
            sequence_info=seq_info,
        )
        assert result.status == "applied"
        assert result.entity_id == "entity-1"
        assert result.applied_sequence == 1

    @pytest.mark.asyncio
    async def test_persist_accepts_optional_correlation_id(self) -> None:
        """persist should accept optional correlation_id."""
        projector = MockProjector()
        seq_info = MockSequenceInfo(sequence=1)

        result = await projector.persist(
            projection={"key": "value"},
            entity_id="entity-1",
            domain="test-domain",
            sequence_info=seq_info,
            correlation_id="corr-123",
        )
        assert result.status == "applied"

    @pytest.mark.asyncio
    async def test_persist_rejects_stale_sequence(self) -> None:
        """persist should reject projections with sequence <= last applied."""
        projector = MockProjector()

        # Apply sequence 5
        result1 = await projector.persist(
            projection={"v": 1},
            entity_id="e1",
            domain="d1",
            sequence_info=MockSequenceInfo(sequence=5),
        )
        assert result1.status == "applied"

        # Try to apply sequence 3 (stale)
        result2 = await projector.persist(
            projection={"v": 2},
            entity_id="e1",
            domain="d1",
            sequence_info=MockSequenceInfo(sequence=3),
        )
        assert result2.status == "rejected_stale"
        assert result2.rejected_reason is not None
        assert "3" in result2.rejected_reason
        assert "5" in result2.rejected_reason

    @pytest.mark.asyncio
    async def test_persist_rejects_equal_sequence(self) -> None:
        """persist should reject projections with sequence == last applied."""
        projector = MockProjector()

        # Apply sequence 5
        await projector.persist(
            projection={"v": 1},
            entity_id="e1",
            domain="d1",
            sequence_info=MockSequenceInfo(sequence=5),
        )

        # Try to apply sequence 5 again (equal, should be rejected)
        result = await projector.persist(
            projection={"v": 2},
            entity_id="e1",
            domain="d1",
            sequence_info=MockSequenceInfo(sequence=5),
        )
        assert result.status == "rejected_stale"

    @pytest.mark.asyncio
    async def test_batch_persist_returns_results(self) -> None:
        """batch_persist should return BatchPersistResult with individual results."""
        projector = MockProjector()

        projections = [
            ({"id": 1}, "e1", "d1", MockSequenceInfo(sequence=1)),
            ({"id": 2}, "e2", "d1", MockSequenceInfo(sequence=1)),
            ({"id": 3}, "e3", "d1", MockSequenceInfo(sequence=1)),
        ]

        result = await projector.batch_persist(projections)

        assert result.total_count == 3
        assert result.applied_count == 3
        assert result.rejected_count == 0
        assert len(result.results) == 3
        for r in result.results:
            assert r.status == "applied"

    @pytest.mark.asyncio
    async def test_batch_persist_handles_mixed_results(self) -> None:
        """batch_persist should handle mix of applied and rejected."""
        projector = MockProjector()

        # Pre-apply sequence 5 for e1
        await projector.persist(
            projection={"v": 0},
            entity_id="e1",
            domain="d1",
            sequence_info=MockSequenceInfo(sequence=5),
        )

        projections = [
            ({"id": 1}, "e1", "d1", MockSequenceInfo(sequence=3)),  # stale
            ({"id": 2}, "e2", "d1", MockSequenceInfo(sequence=1)),  # fresh
            ({"id": 3}, "e1", "d1", MockSequenceInfo(sequence=10)),  # fresh (higher)
        ]

        result = await projector.batch_persist(projections)

        assert result.total_count == 3
        assert result.applied_count == 2
        assert result.rejected_count == 1
        assert result.results[0].status == "rejected_stale"
        assert result.results[1].status == "applied"
        assert result.results[2].status == "applied"

    @pytest.mark.asyncio
    async def test_get_last_sequence_returns_none_for_unknown(self) -> None:
        """get_last_sequence should return None for unknown entities."""
        projector = MockProjector()

        result = await projector.get_last_sequence("unknown-entity", "unknown-domain")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_last_sequence_returns_last_applied(self) -> None:
        """get_last_sequence should return the last applied sequence."""
        projector = MockProjector()

        await projector.persist(
            projection={"v": 1},
            entity_id="e1",
            domain="d1",
            sequence_info=MockSequenceInfo(sequence=42, partition="p0"),
        )

        result = await projector.get_last_sequence("e1", "d1")
        assert result is not None
        assert result.sequence == 42
        assert result.partition == "p0"

    @pytest.mark.asyncio
    async def test_is_stale_returns_false_for_unknown(self) -> None:
        """is_stale should return False for unknown entities."""
        projector = MockProjector()

        result = await projector.is_stale(
            "unknown",
            "unknown",
            MockSequenceInfo(sequence=1),
        )
        assert result is False

    @pytest.mark.asyncio
    async def test_is_stale_returns_true_for_stale(self) -> None:
        """is_stale should return True for stale sequences."""
        projector = MockProjector()

        await projector.persist(
            projection={"v": 1},
            entity_id="e1",
            domain="d1",
            sequence_info=MockSequenceInfo(sequence=10),
        )

        # Check sequence 5 (stale)
        result = await projector.is_stale(
            "e1",
            "d1",
            MockSequenceInfo(sequence=5),
        )
        assert result is True

        # Check sequence 10 (equal, also stale)
        result = await projector.is_stale(
            "e1",
            "d1",
            MockSequenceInfo(sequence=10),
        )
        assert result is True

        # Check sequence 15 (fresh)
        result = await projector.is_stale(
            "e1",
            "d1",
            MockSequenceInfo(sequence=15),
        )
        assert result is False

    @pytest.mark.asyncio
    async def test_cleanup_before_sequence_removes_entries(self) -> None:
        """cleanup_before_sequence should remove old tracking entries."""
        projector = MockProjector()

        # Add multiple entities with different sequences
        for i in range(5):
            await projector.persist(
                projection={"id": i},
                entity_id=f"e{i}",
                domain="d1",
                sequence_info=MockSequenceInfo(sequence=i + 1),
            )

        # Cleanup sequences < 3 (should remove e0, e1)
        removed = await projector.cleanup_before_sequence(domain="d1", sequence=3)
        assert removed == 2

        # Verify e0, e1 are gone
        assert await projector.get_last_sequence("e0", "d1") is None
        assert await projector.get_last_sequence("e1", "d1") is None

        # Verify e2, e3, e4 remain
        assert await projector.get_last_sequence("e2", "d1") is not None
        assert await projector.get_last_sequence("e3", "d1") is not None
        assert await projector.get_last_sequence("e4", "d1") is not None


class TestProtocolProjectorImports:
    """Test protocol imports from different locations."""

    def test_import_from_protocol_module(self) -> None:
        """Test direct import from protocol_projector module."""
        from omnibase_spi.protocols.projections.protocol_projector import (
            ProtocolProjector as DirectProtocolProjector,
        )

        projector = MockProjector()
        assert isinstance(projector, DirectProtocolProjector)

    def test_import_from_projections_package(self) -> None:
        """Test import from projections package."""
        from omnibase_spi.protocols.projections import (
            ProtocolProjector as ProjectionsProtocolProjector,
        )

        projector = MockProjector()
        assert isinstance(projector, ProjectionsProtocolProjector)

    def test_import_from_protocols_package(self) -> None:
        """Test import from protocols root package."""
        from omnibase_spi.protocols import (
            ProtocolProjector as ProtocolsProjector,
        )

        projector = MockProjector()
        assert isinstance(projector, ProtocolsProjector)

    def test_imports_are_identical(self) -> None:
        """Verify imports from different locations are the same class."""
        from omnibase_spi.protocols import (
            ProtocolProjector as ProtocolsProjector,
        )
        from omnibase_spi.protocols.projections import (
            ProtocolProjector as ProjectionsProtocolProjector,
        )
        from omnibase_spi.protocols.projections.protocol_projector import (
            ProtocolProjector as DirectProtocolProjector,
        )

        assert DirectProtocolProjector is ProjectionsProtocolProjector
        assert ProjectionsProtocolProjector is ProtocolsProjector


class TestProtocolProjectorDocumentation:
    """Test that ProtocolProjector has proper documentation."""

    def test_protocol_has_docstring(self) -> None:
        """ProtocolProjector should have a docstring."""
        assert ProtocolProjector.__doc__ is not None
        assert len(ProtocolProjector.__doc__.strip()) > 0

    def test_mock_persist_has_docstring(self) -> None:
        """persist method should have a docstring."""
        assert MockProjector.persist.__doc__ is not None

    def test_mock_batch_persist_has_docstring(self) -> None:
        """batch_persist method should have a docstring."""
        assert MockProjector.batch_persist.__doc__ is not None

    def test_mock_get_last_sequence_has_docstring(self) -> None:
        """get_last_sequence method should have a docstring."""
        assert MockProjector.get_last_sequence.__doc__ is not None

    def test_mock_is_stale_has_docstring(self) -> None:
        """is_stale method should have a docstring."""
        assert MockProjector.is_stale.__doc__ is not None

    def test_mock_cleanup_before_sequence_has_docstring(self) -> None:
        """cleanup_before_sequence method should have a docstring."""
        assert MockProjector.cleanup_before_sequence.__doc__ is not None


class TestSequenceInfoEdgeCases:
    """Test edge cases for sequence handling."""

    def test_sequence_zero_is_valid(self) -> None:
        """Sequence 0 should be a valid sequence number."""
        seq = MockSequenceInfo(sequence=0)
        assert seq.sequence == 0
        assert isinstance(seq, ProtocolSequenceInfo)

    def test_partition_none_is_valid(self) -> None:
        """None partition should be valid."""
        seq = MockSequenceInfo(sequence=1, partition=None)
        assert seq.partition is None
        assert isinstance(seq, ProtocolSequenceInfo)

    def test_large_sequence_numbers(self) -> None:
        """Large sequence numbers should work correctly."""
        seq = MockSequenceInfo(sequence=2**63 - 1)
        assert seq.sequence == 2**63 - 1
        assert isinstance(seq, ProtocolSequenceInfo)


class TestDomainIsolation:
    """Test that different domains are isolated."""

    @pytest.mark.asyncio
    async def test_same_entity_different_domains(self) -> None:
        """Same entity in different domains should have independent sequences."""
        projector = MockProjector()

        # Apply sequence 5 in domain d1
        await projector.persist(
            projection={"v": 1},
            entity_id="e1",
            domain="d1",
            sequence_info=MockSequenceInfo(sequence=5),
        )

        # Apply sequence 1 in domain d2 (should work, different domain)
        result = await projector.persist(
            projection={"v": 2},
            entity_id="e1",
            domain="d2",
            sequence_info=MockSequenceInfo(sequence=1),
        )
        assert result.status == "applied"

        # Verify d1 is at sequence 5
        d1_seq = await projector.get_last_sequence("e1", "d1")
        assert d1_seq is not None
        assert d1_seq.sequence == 5

        # Verify d2 is at sequence 1
        d2_seq = await projector.get_last_sequence("e1", "d2")
        assert d2_seq is not None
        assert d2_seq.sequence == 1
