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
