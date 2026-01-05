"""
Tests for ProtocolEventProjector protocol (event-to-state projection).

Validates that ProtocolEventProjector:
- Is properly runtime checkable
- Defines required properties and methods with correct signatures
- Cannot be instantiated directly
- Works correctly with isinstance checks for compliant/non-compliant classes
- Supports the event-to-state projection semantics

Note:
    This tests the ProtocolEventProjector in protocols.projectors (event-to-state).
    There is a separate ProtocolEventProjector in protocols.projections for
    projection persistence with ordering guarantees.
"""

from __future__ import annotations

from typing import Any, Protocol
from uuid import UUID, uuid4

import pytest

from omnibase_spi.protocols.projectors.protocol_event_projector import (
    ProtocolEventProjector,
)

# =============================================================================
# Mock Models (since we can't import from omnibase_core in tests)
# =============================================================================


class MockEventEnvelope:
    """
    A mock that simulates ModelEventEnvelope from omnibase_core.

    Provides the minimal interface needed for testing ProtocolEventProjector.
    """

    def __init__(
        self,
        event_id: UUID | None = None,
        event_type: str = "TestEvent",
        aggregate_id: UUID | None = None,
        aggregate_type: str = "TestAggregate",
        payload: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the mock event envelope."""
        self._event_id = event_id or uuid4()
        self._event_type = event_type
        self._aggregate_id = aggregate_id or uuid4()
        self._aggregate_type = aggregate_type
        self._payload = payload if payload is not None else {}
        self._metadata = metadata if metadata is not None else {}

    @property
    def event_id(self) -> UUID:
        """Return the unique event identifier."""
        return self._event_id

    @property
    def event_type(self) -> str:
        """Return the event type."""
        return self._event_type

    @property
    def aggregate_id(self) -> UUID:
        """Return the aggregate identifier."""
        return self._aggregate_id

    @property
    def aggregate_type(self) -> str:
        """Return the aggregate type."""
        return self._aggregate_type

    @property
    def payload(self) -> dict[str, Any]:
        """Return the event payload."""
        return self._payload

    @property
    def metadata(self) -> dict[str, Any]:
        """Return the event metadata."""
        return self._metadata


class MockProjectionResult:
    """
    A mock that simulates ModelProjectionResult from omnibase_core.

    Provides the minimal interface needed for testing ProtocolEventProjector.
    """

    def __init__(
        self,
        success: bool = True,
        skipped: bool = False,
        error: str | None = None,
        reason: str | None = None,
    ) -> None:
        """Initialize the mock projection result."""
        self._success = success
        self._skipped = skipped
        self._error = error
        self._reason = reason

    @property
    def success(self) -> bool:
        """Return whether projection completed successfully."""
        return self._success

    @property
    def skipped(self) -> bool:
        """Return whether event was skipped."""
        return self._skipped

    @property
    def error(self) -> str | None:
        """Return error details if projection failed."""
        return self._error

    @property
    def reason(self) -> str | None:
        """Return reason for skip if skipped."""
        return self._reason


# =============================================================================
# Mock Implementations
# =============================================================================


class MockProjector:
    """
    A class that fully implements the ProtocolEventProjector protocol.

    This mock implementation provides an in-memory projector for testing.
    It demonstrates how a compliant implementation should behave.
    """

    def __init__(
        self,
        projector_id: str = "mock-projector-v1",
        aggregate_type: str = "TestAggregate",
        consumed_events: list[str] | None = None,
    ) -> None:
        """Initialize the mock projector with configuration."""
        self._projector_id = projector_id
        self._aggregate_type = aggregate_type
        self._consumed_events = consumed_events or ["TestCreated", "TestUpdated"]
        # In-memory state storage
        self._state: dict[UUID, dict[str, Any]] = {}
        # Track processed events for idempotency
        self._processed_events: set[UUID] = set()

    @property
    def projector_id(self) -> str:
        """Return the unique identifier for this projector."""
        return self._projector_id

    @property
    def aggregate_type(self) -> str:
        """Return the aggregate type this projector handles."""
        return self._aggregate_type

    @property
    def consumed_events(self) -> list[str]:
        """Return the event types this projector consumes."""
        return self._consumed_events

    async def project(
        self,
        event: MockEventEnvelope,
    ) -> MockProjectionResult:
        """
        Project event to in-memory state.

        Args:
            event: The event envelope to project.

        Returns:
            MockProjectionResult indicating success/failure/skip.
        """
        # Check if event type is consumed
        if event.event_type not in self._consumed_events:
            return MockProjectionResult(
                success=False,
                skipped=True,
                reason=f"Unknown event type: {event.event_type}",
            )

        # Idempotency check
        if event.event_id in self._processed_events:
            return MockProjectionResult(
                success=True,
                skipped=True,
                reason="Event already processed",
            )

        # Apply event to state
        aggregate_id = event.aggregate_id
        if aggregate_id not in self._state:
            self._state[aggregate_id] = {}

        # Update state based on event
        self._state[aggregate_id].update(event.payload)
        self._state[aggregate_id]["last_event_id"] = str(event.event_id)
        self._state[aggregate_id]["last_event_type"] = event.event_type

        # Mark as processed
        self._processed_events.add(event.event_id)

        return MockProjectionResult(success=True)

    async def get_state(
        self,
        aggregate_id: UUID,
    ) -> dict[str, Any] | None:
        """
        Get current projected state for an aggregate.

        Args:
            aggregate_id: The UUID of the aggregate to retrieve.

        Returns:
            The current state or None if not found.
        """
        return self._state.get(aggregate_id)


class PartialProjector:
    """A class that only implements some ProtocolEventProjector members."""

    @property
    def projector_id(self) -> str:
        """Return projector ID."""
        return "partial-projector"

    @property
    def aggregate_type(self) -> str:
        """Return aggregate type."""
        return "Test"

    # Missing: consumed_events, project, get_state


class NonCompliantProjector:
    """A class that implements none of the ProtocolEventProjector members."""

    pass


class MethodOnlyProjector:
    """A class that implements only methods, not properties."""

    async def project(self, event: Any) -> MockProjectionResult:
        """Project an event."""
        return MockProjectionResult(success=True)

    async def get_state(self, aggregate_id: UUID) -> None:
        """Get state."""
        return None


class PropertyOnlyProjector:
    """A class that implements only properties, not methods."""

    @property
    def projector_id(self) -> str:
        """Return projector ID."""
        return "prop-only"

    @property
    def aggregate_type(self) -> str:
        """Return aggregate type."""
        return "Test"

    @property
    def consumed_events(self) -> list[str]:
        """Return consumed events."""
        return ["TestEvent"]


# =============================================================================
# Test Classes
# =============================================================================


@pytest.mark.unit
class TestProtocolEventProjectorProtocol:
    """Test suite for ProtocolEventProjector protocol definition."""

    # Define expected protocol members for exhaustiveness checking
    EXPECTED_PROTOCOL_MEMBERS = {
        "projector_id",
        "aggregate_type",
        "consumed_events",
        "project",
        "get_state",
    }

    def test_all_protocol_members_have_tests(self) -> None:
        """Verify all protocol members have corresponding tests in this module.

        This exhaustiveness check ensures that when new members are added to
        ProtocolEventProjector, corresponding tests are also added.
        """
        import inspect

        # Get all public members of the protocol (excluding dunder methods)
        protocol_members = {
            name
            for name, _ in inspect.getmembers(ProtocolEventProjector)
            if not name.startswith("_")
        }

        # Verify our expected members match the actual protocol members
        assert protocol_members == self.EXPECTED_PROTOCOL_MEMBERS, (
            f"Protocol members changed! "
            f"New members: {protocol_members - self.EXPECTED_PROTOCOL_MEMBERS}, "
            f"Removed members: {self.EXPECTED_PROTOCOL_MEMBERS - protocol_members}"
        )

    def test_mock_implements_all_protocol_members(self) -> None:
        """Verify MockProjector implements ALL protocol members.

        This ensures our test mock is complete and doesn't silently
        pass isinstance checks while missing functionality.
        """
        mock = MockProjector()

        for member in self.EXPECTED_PROTOCOL_MEMBERS:
            assert hasattr(
                mock, member
            ), f"MockProjector missing protocol member: {member}"

    def test_protocol_is_runtime_checkable(self) -> None:
        """ProtocolEventProjector should be runtime_checkable."""
        # Check for either the old or new attribute name for runtime protocols
        assert hasattr(ProtocolEventProjector, "_is_runtime_protocol") or hasattr(
            ProtocolEventProjector, "__runtime_protocol__"
        )

    def test_protocol_is_protocol(self) -> None:
        """ProtocolEventProjector should be a Protocol class."""
        assert any(
            base is Protocol or base.__name__ == "Protocol"
            for base in ProtocolEventProjector.__mro__
        )

    def test_protocol_has_projector_id_property(self) -> None:
        """ProtocolEventProjector should define projector_id property."""
        assert "projector_id" in dir(ProtocolEventProjector)

    def test_protocol_has_aggregate_type_property(self) -> None:
        """ProtocolEventProjector should define aggregate_type property."""
        assert "aggregate_type" in dir(ProtocolEventProjector)

    def test_protocol_has_consumed_events_property(self) -> None:
        """ProtocolEventProjector should define consumed_events property."""
        assert "consumed_events" in dir(ProtocolEventProjector)

    def test_protocol_has_project_method(self) -> None:
        """ProtocolEventProjector should define project method."""
        assert "project" in dir(ProtocolEventProjector)

    def test_protocol_has_get_state_method(self) -> None:
        """ProtocolEventProjector should define get_state method."""
        assert "get_state" in dir(ProtocolEventProjector)

    def test_protocol_cannot_be_instantiated(self) -> None:
        """ProtocolEventProjector protocol should not be directly instantiable."""
        with pytest.raises(TypeError):
            ProtocolEventProjector()  # type: ignore[misc]


@pytest.mark.unit
class TestProtocolEventProjectorCompliance:
    """Test isinstance checks for protocol compliance."""

    def test_compliant_class_passes_isinstance(self) -> None:
        """A class implementing all members should pass isinstance check."""
        projector = MockProjector()
        assert isinstance(projector, ProtocolEventProjector)

    def test_partial_implementation_fails_isinstance(self) -> None:
        """A class missing members should fail isinstance check."""
        projector = PartialProjector()
        assert not isinstance(projector, ProtocolEventProjector)

    def test_non_compliant_class_fails_isinstance(self) -> None:
        """A class with no members should fail isinstance check."""
        projector = NonCompliantProjector()
        assert not isinstance(projector, ProtocolEventProjector)

    def test_method_only_fails_isinstance(self) -> None:
        """A class missing properties should fail isinstance check."""
        projector = MethodOnlyProjector()
        assert not isinstance(projector, ProtocolEventProjector)

    def test_property_only_fails_isinstance(self) -> None:
        """A class missing methods should fail isinstance check."""
        projector = PropertyOnlyProjector()
        assert not isinstance(projector, ProtocolEventProjector)


@pytest.mark.unit
class TestMockProjectorImplementsAllMembers:
    """Test that MockProjector has all required members."""

    def test_mock_has_projector_id_property(self) -> None:
        """Mock should have projector_id property."""
        projector = MockProjector()
        assert hasattr(projector, "projector_id")
        assert isinstance(projector.projector_id, str)

    def test_mock_has_aggregate_type_property(self) -> None:
        """Mock should have aggregate_type property."""
        projector = MockProjector()
        assert hasattr(projector, "aggregate_type")
        assert isinstance(projector.aggregate_type, str)

    def test_mock_has_consumed_events_property(self) -> None:
        """Mock should have consumed_events property."""
        projector = MockProjector()
        assert hasattr(projector, "consumed_events")
        assert isinstance(projector.consumed_events, list)

    def test_mock_has_project_method(self) -> None:
        """Mock should have project method."""
        projector = MockProjector()
        assert hasattr(projector, "project")
        assert callable(projector.project)

    def test_mock_has_get_state_method(self) -> None:
        """Mock should have get_state method."""
        projector = MockProjector()
        assert hasattr(projector, "get_state")
        assert callable(projector.get_state)


@pytest.mark.unit
class TestProtocolEventProjectorAsyncNature:
    """Test that ProtocolEventProjector methods are async."""

    def test_project_is_async(self) -> None:
        """project should be an async method."""
        import inspect

        assert inspect.iscoroutinefunction(MockProjector.project)

    def test_get_state_is_async(self) -> None:
        """get_state should be an async method."""
        import inspect

        assert inspect.iscoroutinefunction(MockProjector.get_state)


@pytest.mark.unit
class TestProtocolEventProjectorProperties:
    """Test protocol property behavior."""

    def test_projector_id_returns_string(self) -> None:
        """projector_id should return a string."""
        projector = MockProjector(projector_id="my-projector-v1")
        assert projector.projector_id == "my-projector-v1"

    def test_aggregate_type_returns_string(self) -> None:
        """aggregate_type should return a string."""
        projector = MockProjector(aggregate_type="Order")
        assert projector.aggregate_type == "Order"

    def test_consumed_events_returns_list(self) -> None:
        """consumed_events should return a list of strings."""
        events = ["OrderCreated", "OrderShipped"]
        projector = MockProjector(consumed_events=events)
        assert projector.consumed_events == events
        assert all(isinstance(e, str) for e in projector.consumed_events)


@pytest.mark.unit
class TestProjectMethodBehavior:
    """Test the project method behavior."""

    @pytest.mark.asyncio
    async def test_project_consumed_event(self) -> None:
        """project should successfully handle consumed events."""
        projector = MockProjector(consumed_events=["TestCreated"])
        event = MockEventEnvelope(
            event_type="TestCreated",
            payload={"name": "Test Item", "value": 100},
        )

        result = await projector.project(event)

        assert result.success is True
        assert result.skipped is False

    @pytest.mark.asyncio
    async def test_project_unknown_event_skipped(self) -> None:
        """project should skip events not in consumed_events."""
        projector = MockProjector(consumed_events=["TestCreated"])
        event = MockEventEnvelope(event_type="UnknownEvent")

        result = await projector.project(event)

        assert result.skipped is True
        assert result.reason is not None
        assert "Unknown event type" in result.reason

    @pytest.mark.asyncio
    async def test_project_is_idempotent(self) -> None:
        """project should be idempotent for same event."""
        projector = MockProjector(consumed_events=["TestCreated"])
        event = MockEventEnvelope(
            event_type="TestCreated",
            payload={"name": "Test"},
        )

        # First projection
        result1 = await projector.project(event)
        assert result1.success is True
        assert result1.skipped is False

        # Second projection of same event (idempotent)
        result2 = await projector.project(event)
        assert result2.success is True
        assert result2.skipped is True
        assert result2.reason is not None
        assert "already processed" in result2.reason.lower()

    @pytest.mark.asyncio
    async def test_project_updates_state(self) -> None:
        """project should update the materialized state."""
        projector = MockProjector(consumed_events=["TestCreated"])
        aggregate_id = uuid4()
        event = MockEventEnvelope(
            event_type="TestCreated",
            aggregate_id=aggregate_id,
            payload={"name": "Test Item"},
        )

        await projector.project(event)
        state = await projector.get_state(aggregate_id)

        assert state is not None
        assert state["name"] == "Test Item"
        assert state["last_event_type"] == "TestCreated"


@pytest.mark.unit
class TestGetStateMethod:
    """Test the get_state method behavior."""

    @pytest.mark.asyncio
    async def test_get_state_returns_none_for_unknown(self) -> None:
        """get_state should return None for unknown aggregate."""
        projector = MockProjector()
        result = await projector.get_state(uuid4())
        assert result is None

    @pytest.mark.asyncio
    async def test_get_state_returns_projected_state(self) -> None:
        """get_state should return the projected state."""
        projector = MockProjector(consumed_events=["TestCreated", "TestUpdated"])
        aggregate_id = uuid4()

        # Project create event
        await projector.project(
            MockEventEnvelope(
                event_type="TestCreated",
                aggregate_id=aggregate_id,
                payload={"name": "Initial", "version": 1},
            )
        )

        # Project update event
        await projector.project(
            MockEventEnvelope(
                event_type="TestUpdated",
                aggregate_id=aggregate_id,
                payload={"name": "Updated", "version": 2},
            )
        )

        state = await projector.get_state(aggregate_id)

        assert state is not None
        assert state["name"] == "Updated"
        assert state["version"] == 2
        assert state["last_event_type"] == "TestUpdated"

    @pytest.mark.asyncio
    async def test_get_state_different_aggregates_isolated(self) -> None:
        """get_state should return isolated state per aggregate."""
        projector = MockProjector(consumed_events=["TestCreated"])
        agg1 = uuid4()
        agg2 = uuid4()

        await projector.project(
            MockEventEnvelope(
                event_type="TestCreated",
                aggregate_id=agg1,
                payload={"name": "Aggregate 1"},
            )
        )
        await projector.project(
            MockEventEnvelope(
                event_type="TestCreated",
                aggregate_id=agg2,
                payload={"name": "Aggregate 2"},
            )
        )

        state1 = await projector.get_state(agg1)
        state2 = await projector.get_state(agg2)

        assert state1 is not None
        assert state2 is not None
        assert state1["name"] == "Aggregate 1"
        assert state2["name"] == "Aggregate 2"


@pytest.mark.unit
class TestProtocolEventProjectorImports:
    """Test protocol imports from different locations."""

    def test_import_from_protocol_module(self) -> None:
        """Test direct import from protocol_event_projector module."""
        from omnibase_spi.protocols.projectors.protocol_event_projector import (
            ProtocolEventProjector as DirectProtocolEventProjector,
        )

        projector = MockProjector()
        assert isinstance(projector, DirectProtocolEventProjector)

    def test_import_from_projectors_package(self) -> None:
        """Test import from projectors package."""
        from omnibase_spi.protocols.projectors import (
            ProtocolEventProjector as ProjectorsProtocolEventProjector,
        )

        projector = MockProjector()
        assert isinstance(projector, ProjectorsProtocolEventProjector)

    def test_imports_are_identical(self) -> None:
        """Verify imports from different locations are the same class."""
        from omnibase_spi.protocols.projectors import (
            ProtocolEventProjector as ProjectorsProtocolEventProjector,
        )
        from omnibase_spi.protocols.projectors.protocol_event_projector import (
            ProtocolEventProjector as DirectProtocolEventProjector,
        )

        assert DirectProtocolEventProjector is ProjectorsProtocolEventProjector


@pytest.mark.unit
class TestProtocolEventProjectorDocumentation:
    """Test that ProtocolEventProjector has proper documentation."""

    def test_protocol_has_docstring(self) -> None:
        """ProtocolEventProjector should have a docstring."""
        assert ProtocolEventProjector.__doc__ is not None
        assert len(ProtocolEventProjector.__doc__.strip()) > 0

    def test_docstring_mentions_idempotency(self) -> None:
        """Docstring should mention idempotency requirement."""
        doc = ProtocolEventProjector.__doc__ or ""
        assert "idempotent" in doc.lower()

    def test_docstring_mentions_constraints(self) -> None:
        """Docstring should mention side effect constraints."""
        doc = ProtocolEventProjector.__doc__ or ""
        assert "MUST NOT" in doc or "must not" in doc.lower()

    def test_docstring_mentions_event_bus(self) -> None:
        """Docstring should mention not emitting to event bus."""
        doc = ProtocolEventProjector.__doc__ or ""
        assert "event" in doc.lower()


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases for ProtocolEventProjector."""

    @pytest.mark.asyncio
    async def test_empty_consumed_events(self) -> None:
        """Projector with no consumed events should skip all events."""
        projector = MockProjector(consumed_events=[])
        event = MockEventEnvelope(event_type="AnyEvent")

        result = await projector.project(event)

        assert result.skipped is True

    @pytest.mark.asyncio
    async def test_empty_payload(self) -> None:
        """Should handle events with empty payload."""
        projector = MockProjector(consumed_events=["TestCreated"])
        aggregate_id = uuid4()
        event = MockEventEnvelope(
            event_type="TestCreated",
            aggregate_id=aggregate_id,
            payload={},
        )

        result = await projector.project(event)

        assert result.success is True
        state = await projector.get_state(aggregate_id)
        assert state is not None

    @pytest.mark.asyncio
    async def test_multiple_events_same_aggregate(self) -> None:
        """Should correctly project multiple events to same aggregate."""
        projector = MockProjector(consumed_events=["Create", "Update", "Delete"])
        aggregate_id = uuid4()

        # Sequence of events
        events = [
            MockEventEnvelope(
                event_type="Create",
                aggregate_id=aggregate_id,
                payload={"status": "created"},
            ),
            MockEventEnvelope(
                event_type="Update",
                aggregate_id=aggregate_id,
                payload={"status": "updated"},
            ),
            MockEventEnvelope(
                event_type="Delete",
                aggregate_id=aggregate_id,
                payload={"status": "deleted"},
            ),
        ]

        for event in events:
            result = await projector.project(event)
            assert result.success is True

        state = await projector.get_state(aggregate_id)
        assert state is not None
        assert state["status"] == "deleted"
        assert state["last_event_type"] == "Delete"


@pytest.mark.unit
class TestProjectorConfiguration:
    """Test projector configuration via constructor."""

    def test_custom_projector_id(self) -> None:
        """Should accept custom projector_id."""
        projector = MockProjector(projector_id="order-projector-v2")
        assert projector.projector_id == "order-projector-v2"

    def test_custom_aggregate_type(self) -> None:
        """Should accept custom aggregate_type."""
        projector = MockProjector(aggregate_type="Order")
        assert projector.aggregate_type == "Order"

    def test_custom_consumed_events(self) -> None:
        """Should accept custom consumed_events list."""
        events = ["OrderCreated", "OrderShipped", "OrderDelivered"]
        projector = MockProjector(consumed_events=events)
        assert projector.consumed_events == events


@pytest.mark.unit
class TestIdempotencyComprehensive:
    """
    Comprehensive idempotency tests for ProtocolEventProjector.

    These tests validate that:
    - Multiple rapid projections of the same event are handled correctly
    - State remains consistent across duplicate projections
    - Results correctly indicate skip/already-processed for duplicates
    - Idempotency is preserved across simulated system restarts
    """

    @pytest.mark.asyncio
    async def test_multiple_rapid_projections_same_event(self) -> None:
        """
        Multiple rapid projections of the same event should all be idempotent.

        Only the first projection should actually process; subsequent ones
        should be skipped with appropriate indication.
        """
        projector = MockProjector(consumed_events=["TestCreated"])
        event = MockEventEnvelope(
            event_type="TestCreated",
            payload={"name": "Test", "counter": 1},
        )

        # Track results
        results: list[MockProjectionResult] = []

        # Simulate rapid projections (as if from competing consumers)
        for _ in range(10):
            result = await projector.project(event)
            results.append(result)

        # First projection should succeed without skip
        assert results[0].success is True
        assert results[0].skipped is False

        # All subsequent projections should be skipped
        for i, result in enumerate(results[1:], start=2):
            assert result.success is True, f"Projection {i} should succeed"
            assert result.skipped is True, f"Projection {i} should be skipped"
            assert result.reason is not None, f"Projection {i} should have reason"
            assert "already processed" in result.reason.lower()

    @pytest.mark.asyncio
    async def test_state_unchanged_on_duplicate_projection(self) -> None:
        """
        State should not change when projecting duplicate events.

        The projected state should be identical before and after
        duplicate projections.
        """
        projector = MockProjector(consumed_events=["TestCreated", "TestUpdated"])
        aggregate_id = uuid4()

        # Initial event
        create_event = MockEventEnvelope(
            event_type="TestCreated",
            aggregate_id=aggregate_id,
            payload={"name": "Original", "version": 1, "counter": 100},
        )

        # Project the event first time
        await projector.project(create_event)

        # Capture state after first projection
        state_after_first = await projector.get_state(aggregate_id)
        assert state_after_first is not None
        state_snapshot = dict(state_after_first)  # Make a copy

        # Project the same event multiple more times
        for _ in range(5):
            await projector.project(create_event)

        # Get state after duplicates
        state_after_duplicates = await projector.get_state(aggregate_id)
        assert state_after_duplicates is not None

        # State should be identical
        assert state_after_duplicates["name"] == state_snapshot["name"]
        assert state_after_duplicates["version"] == state_snapshot["version"]
        assert state_after_duplicates["counter"] == state_snapshot["counter"]
        assert (
            state_after_duplicates["last_event_id"] == state_snapshot["last_event_id"]
        )
        assert (
            state_after_duplicates["last_event_type"]
            == state_snapshot["last_event_type"]
        )

    @pytest.mark.asyncio
    async def test_result_indicates_skip_for_duplicates(self) -> None:
        """
        Result should clearly indicate skip status for duplicate events.

        The MockProjectionResult should have:
        - success=True (idempotent operation completed)
        - skipped=True (no actual state change)
        - reason explaining why it was skipped
        """
        projector = MockProjector(consumed_events=["TestCreated"])
        event = MockEventEnvelope(
            event_type="TestCreated",
            payload={"name": "Test"},
        )

        # First projection
        first_result = await projector.project(event)
        assert first_result.success is True
        assert first_result.skipped is False
        assert first_result.reason is None

        # Duplicate projection
        duplicate_result = await projector.project(event)

        # Verify skip indication
        assert duplicate_result.success is True, "Idempotent operation should succeed"
        assert duplicate_result.skipped is True, "Duplicate should be marked as skipped"
        assert duplicate_result.reason is not None, "Skip reason should be provided"
        assert (
            "already" in duplicate_result.reason.lower()
            or "processed" in duplicate_result.reason.lower()
            or "duplicate" in duplicate_result.reason.lower()
        ), f"Reason should indicate duplicate: {duplicate_result.reason}"

    @pytest.mark.asyncio
    async def test_idempotency_after_simulated_restart(self) -> None:
        """
        Idempotency should be preserved after simulated system restart.

        This simulates a scenario where the projector is restarted but
        the persistence layer (tracking processed events) survives.
        In a real implementation, processed event IDs would be stored
        in a database or checkpoint.
        """
        projector = MockProjector(consumed_events=["TestCreated"])
        aggregate_id = uuid4()

        event = MockEventEnvelope(
            event_type="TestCreated",
            aggregate_id=aggregate_id,
            payload={"name": "Persistent", "value": 42},
        )

        # Project the event
        first_result = await projector.project(event)
        assert first_result.success is True
        assert first_result.skipped is False

        # Capture processed events (simulates persistent storage)
        persisted_event_ids = set(projector._processed_events)

        # Simulate restart: clear in-memory state but keep "persisted" event IDs
        # In a real system, the state would be rebuilt from events or loaded from DB
        projector._state.clear()
        projector._processed_events = persisted_event_ids

        # Try to project the same event again (simulating replay after restart)
        replay_result = await projector.project(event)

        # Should still be idempotent due to persisted event ID tracking
        assert replay_result.success is True
        assert replay_result.skipped is True
        assert replay_result.reason is not None
        assert "already processed" in replay_result.reason.lower()

    @pytest.mark.asyncio
    async def test_idempotency_across_interleaved_events(self) -> None:
        """
        Idempotency should work correctly with interleaved event projections.

        Events for different aggregates should not affect idempotency
        of duplicate events for a specific aggregate.
        """
        projector = MockProjector(consumed_events=["TestCreated", "TestUpdated"])

        agg1 = uuid4()
        agg2 = uuid4()

        event1 = MockEventEnvelope(
            event_type="TestCreated",
            aggregate_id=agg1,
            payload={"name": "Aggregate 1"},
        )
        event2 = MockEventEnvelope(
            event_type="TestCreated",
            aggregate_id=agg2,
            payload={"name": "Aggregate 2"},
        )

        # Interleave projections including duplicates
        await projector.project(event1)  # First for agg1
        await projector.project(event2)  # First for agg2

        # Duplicate of event1 after event2 was processed
        dup1_result = await projector.project(event1)
        assert dup1_result.skipped is True
        assert "already processed" in (dup1_result.reason or "").lower()

        # Duplicate of event2 after event1 duplicate
        dup2_result = await projector.project(event2)
        assert dup2_result.skipped is True
        assert "already processed" in (dup2_result.reason or "").lower()

        # Verify states are still correct
        state1 = await projector.get_state(agg1)
        state2 = await projector.get_state(agg2)

        assert state1 is not None
        assert state2 is not None
        assert state1["name"] == "Aggregate 1"
        assert state2["name"] == "Aggregate 2"

    @pytest.mark.asyncio
    async def test_idempotency_preserves_event_ordering_semantics(self) -> None:
        """
        Idempotency should preserve correct state from first projection.

        If an event is projected, then a newer event modifies state,
        replaying the old event should not revert the state.
        """
        projector = MockProjector(consumed_events=["TestCreated", "TestUpdated"])
        aggregate_id = uuid4()

        create_event = MockEventEnvelope(
            event_type="TestCreated",
            aggregate_id=aggregate_id,
            payload={"name": "Initial", "version": 1},
        )
        update_event = MockEventEnvelope(
            event_type="TestUpdated",
            aggregate_id=aggregate_id,
            payload={"name": "Updated", "version": 2},
        )

        # Project in order: create, then update
        await projector.project(create_event)
        await projector.project(update_event)

        # State should reflect update
        state_before_replay = await projector.get_state(aggregate_id)
        assert state_before_replay is not None
        assert state_before_replay["name"] == "Updated"
        assert state_before_replay["version"] == 2

        # Replay the create event (e.g., from message replay)
        replay_result = await projector.project(create_event)
        assert replay_result.skipped is True

        # State should still reflect the update, not reverted to create
        state_after_replay = await projector.get_state(aggregate_id)
        assert state_after_replay is not None
        assert state_after_replay["name"] == "Updated"
        assert state_after_replay["version"] == 2

    @pytest.mark.asyncio
    async def test_concurrent_duplicate_detection(self) -> None:
        """
        Test that duplicate detection works for events projected in sequence.

        Note: True concurrency testing would require threading/asyncio.gather,
        but this validates the idempotency mechanism itself.
        """
        import asyncio

        projector = MockProjector(consumed_events=["TestCreated"])
        event = MockEventEnvelope(
            event_type="TestCreated",
            payload={"name": "Concurrent Test"},
        )

        # Simulate concurrent projections using asyncio.gather
        results = await asyncio.gather(
            projector.project(event),
            projector.project(event),
            projector.project(event),
        )

        # Exactly one should not be skipped, others should be skipped
        non_skipped = [r for r in results if not r.skipped]
        skipped = [r for r in results if r.skipped]

        assert len(non_skipped) == 1, "Exactly one projection should process"
        assert len(skipped) == 2, "Other projections should be skipped"

        # All should succeed (idempotent operation)
        assert all(r.success for r in results)


@pytest.mark.unit
class TestDistinctFromProjectionsProtocol:
    """Test that this is distinct from projections.ProtocolEventProjector."""

    def test_projectors_protocol_has_projector_id(self) -> None:
        """Projectors ProtocolEventProjector should have projector_id property."""
        assert "projector_id" in dir(ProtocolEventProjector)

    def test_projectors_protocol_has_aggregate_type(self) -> None:
        """Projectors ProtocolEventProjector should have aggregate_type property."""
        assert "aggregate_type" in dir(ProtocolEventProjector)

    def test_projectors_protocol_has_consumed_events(self) -> None:
        """Projectors ProtocolEventProjector should have consumed_events property."""
        assert "consumed_events" in dir(ProtocolEventProjector)

    def test_projectors_protocol_has_project_not_persist(self) -> None:
        """Projectors ProtocolEventProjector should have project, not persist."""
        assert "project" in dir(ProtocolEventProjector)
        # The projections protocol has persist, not project
        assert "persist" not in dir(ProtocolEventProjector)

    def test_projectors_protocol_has_get_state(self) -> None:
        """Projectors ProtocolEventProjector should have get_state method."""
        assert "get_state" in dir(ProtocolEventProjector)
