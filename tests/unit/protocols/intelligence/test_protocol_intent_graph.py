"""Tests for ProtocolIntentGraph protocol compliance.

Validates that ProtocolIntentGraph:
- Is properly runtime checkable
- Defines required methods with correct signatures
- Cannot be instantiated directly
- Works correctly with isinstance checks for compliant/non-compliant classes
"""

from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any, Protocol

import pytest

from omnibase_spi.protocols.intelligence import ProtocolIntentGraph

if TYPE_CHECKING:
    pass


# =============================================================================
# Mock Models (since we can't import from omnibase_core in tests)
# =============================================================================


class MockIntentStoredEvent:
    """Mock that simulates ModelIntentStoredEvent from omnibase_core.

    Provides the minimal interface needed for testing ProtocolIntentGraph.
    """

    def __init__(
        self,
        event_id: str = "event-123",
        session_id: str = "session-456",
        timestamp: str | None = None,
        correlation_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the mock event."""
        self.event_id = event_id
        self.session_id = session_id
        self.timestamp = timestamp or "2025-01-25T12:00:00Z"
        self.correlation_id = correlation_id
        self.metadata = metadata or {}


class MockIntentClassificationInput:
    """Mock that simulates ModelIntentClassificationInput from omnibase_core.

    Provides the minimal interface needed for testing ProtocolIntentGraph.
    """

    def __init__(
        self,
        content: str = "",
        correlation_id: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the mock input."""
        self.content = content
        self.correlation_id = correlation_id
        self.context = context or {}


class MockIntentRecordPayload:
    """Mock that simulates IntentRecordPayload from omnibase_core.

    Provides the minimal interface needed for testing ProtocolIntentGraph.
    """

    def __init__(
        self,
        intent_category: str = "code_generation",
        confidence: float = 0.95,
        timestamp: str | None = None,
        content_hash: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the mock payload."""
        self.intent_category = intent_category
        self.confidence = confidence
        self.timestamp = timestamp or "2025-01-25T12:00:00Z"
        self.content_hash = content_hash or "abc123"
        self.metadata = metadata or {}


# =============================================================================
# Mock Implementations
# =============================================================================


class MockIntentGraph:
    """A class that fully implements the ProtocolIntentGraph protocol.

    This mock implementation provides a simple in-memory intent graph for testing.
    It demonstrates how a compliant implementation should behave.
    """

    def __init__(self) -> None:
        """Initialize the mock intent graph."""
        self._intents: dict[str, list[MockIntentRecordPayload]] = {}
        self._event_counter: int = 0

    async def store_intent(
        self,
        session_id: str,
        intent_data: Any,  # Would be ModelIntentClassificationInput
        correlation_id: str | None = None,
    ) -> Any:  # Would be ModelIntentStoredEvent
        """Store an intent classification result in the graph.

        Args:
            session_id: Unique identifier for the session.
            intent_data: The intent classification input.
            correlation_id: Optional identifier for distributed tracing.

        Returns:
            Event confirming the intent was stored.
        """
        if session_id not in self._intents:
            self._intents[session_id] = []

        self._event_counter += 1
        record = MockIntentRecordPayload(
            intent_category="code_generation",  # Default for testing
            confidence=0.95,
            content_hash=str(hash(getattr(intent_data, "content", ""))),
        )
        self._intents[session_id].append(record)

        return MockIntentStoredEvent(
            event_id=f"event-{self._event_counter}",
            session_id=session_id,
            correlation_id=correlation_id or f"corr-{self._event_counter}",
        )

    async def get_session_intents(
        self,
        session_id: str,
        min_confidence: float = 0.0,
        limit: int | None = None,
    ) -> list[Any]:  # Would be list[IntentRecordPayload]
        """Retrieve stored intents for a session.

        Args:
            session_id: Unique identifier for the session to query.
            min_confidence: Minimum confidence threshold (0.0 to 1.0).
            limit: Maximum number of intents to return.

        Returns:
            List of intent records matching the criteria.
        """
        intents = self._intents.get(session_id, [])

        # Filter by confidence
        filtered = [i for i in intents if i.confidence >= min_confidence]

        # Apply limit
        if limit is not None:
            filtered = filtered[:limit]

        return filtered

    async def health_check(self) -> bool:
        """Check if the intent graph service is healthy.

        Returns:
            True if the service is operational, False otherwise.
        """
        return True


class NonCompliantGraph:
    """A class that does not implement the ProtocolIntentGraph protocol."""

    pass


class PartialGraph:
    """A class that has only store_intent, missing other methods."""

    async def store_intent(
        self,
        session_id: str,
        intent_data: Any,
        correlation_id: str | None = None,
    ) -> Any:
        """Only has store_intent, missing other methods."""
        return MockIntentStoredEvent()

    # Missing get_session_intents and health_check


class PartialGraphMissingHealthCheck:
    """A class that has store_intent and get_session_intents but missing health_check."""

    async def store_intent(
        self,
        session_id: str,
        intent_data: Any,
        correlation_id: str | None = None,
    ) -> Any:
        """Store an intent."""
        return MockIntentStoredEvent()

    async def get_session_intents(
        self,
        session_id: str,
        min_confidence: float = 0.0,
        limit: int | None = None,
    ) -> list[Any]:
        """Get session intents."""
        return []

    # Missing health_check


class SyncGraph:
    """A class that has sync methods instead of async."""

    def store_intent(
        self,
        session_id: str,
        intent_data: Any,
        correlation_id: str | None = None,
    ) -> Any:
        """Sync method - should be async."""
        return MockIntentStoredEvent()

    def get_session_intents(
        self,
        session_id: str,
        min_confidence: float = 0.0,
        limit: int | None = None,
    ) -> list[Any]:
        """Sync method - should be async."""
        return []

    def health_check(self) -> bool:
        """Sync method - should be async."""
        return True


class WrongSignatureGraph:
    """A class with methods but wrong signatures (missing parameters)."""

    async def store_intent(self) -> Any:
        """Missing session_id and intent_data parameters."""
        return MockIntentStoredEvent()

    async def get_session_intents(self) -> list[Any]:
        """Missing session_id parameter."""
        return []

    async def health_check(self) -> bool:
        """This one is correct."""
        return True


# =============================================================================
# Test Classes
# =============================================================================


@pytest.mark.unit
class TestProtocolIntentGraphProtocol:
    """Test suite for ProtocolIntentGraph protocol definition."""

    def test_protocol_is_runtime_checkable(self) -> None:
        """ProtocolIntentGraph should be runtime_checkable.

        Runtime checkable protocols have either _is_runtime_protocol
        or __runtime_protocol__ attribute set to True.
        """
        # Check for either the old or new attribute name for runtime protocols
        assert hasattr(ProtocolIntentGraph, "_is_runtime_protocol") or hasattr(
            ProtocolIntentGraph, "__runtime_protocol__"
        )

    def test_protocol_is_protocol(self) -> None:
        """ProtocolIntentGraph should be a Protocol class."""
        assert any(
            base is Protocol or base.__name__ == "Protocol"
            for base in ProtocolIntentGraph.__mro__
        )

    def test_protocol_has_store_intent_method(self) -> None:
        """ProtocolIntentGraph should define store_intent method."""
        assert "store_intent" in dir(ProtocolIntentGraph)

    def test_protocol_has_get_session_intents_method(self) -> None:
        """ProtocolIntentGraph should define get_session_intents method."""
        assert "get_session_intents" in dir(ProtocolIntentGraph)

    def test_protocol_has_health_check_method(self) -> None:
        """ProtocolIntentGraph should define health_check method."""
        assert "health_check" in dir(ProtocolIntentGraph)

    def test_protocol_methods_are_async(self) -> None:
        """All protocol methods should be coroutine functions."""
        # Get the methods from the protocol
        store_intent = getattr(ProtocolIntentGraph, "store_intent", None)
        get_session_intents = getattr(ProtocolIntentGraph, "get_session_intents", None)
        health_check = getattr(ProtocolIntentGraph, "health_check", None)

        assert store_intent is not None
        assert get_session_intents is not None
        assert health_check is not None

        # Check if they're defined as async (coroutine functions)
        assert inspect.iscoroutinefunction(store_intent)
        assert inspect.iscoroutinefunction(get_session_intents)
        assert inspect.iscoroutinefunction(health_check)

    def test_protocol_cannot_be_instantiated(self) -> None:
        """ProtocolIntentGraph should not be directly instantiable."""
        with pytest.raises(TypeError):
            ProtocolIntentGraph()  # type: ignore[misc]


@pytest.mark.unit
class TestProtocolIntentGraphCompliance:
    """Test isinstance checks for protocol compliance."""

    def test_compliant_class_passes_isinstance_check(self) -> None:
        """A class implementing the protocol should pass isinstance check."""
        graph = MockIntentGraph()
        assert isinstance(graph, ProtocolIntentGraph)

    def test_non_compliant_class_fails_isinstance_check(self) -> None:
        """A class not implementing the protocol should fail isinstance check."""
        not_a_graph = NonCompliantGraph()
        assert not isinstance(not_a_graph, ProtocolIntentGraph)

    def test_partial_implementation_fails_isinstance_check(self) -> None:
        """A class with missing methods should fail isinstance check."""
        partial = PartialGraph()
        assert not isinstance(partial, ProtocolIntentGraph)

    def test_partial_missing_health_check_fails_isinstance_check(self) -> None:
        """A class missing health_check should fail isinstance check."""
        partial = PartialGraphMissingHealthCheck()
        assert not isinstance(partial, ProtocolIntentGraph)

    def test_sync_methods_still_pass_isinstance_check(self) -> None:
        """A class with sync methods passes isinstance (runtime check is structural).

        Note: Python's runtime protocol checking only verifies attribute presence,
        not whether it's async. This is a limitation of runtime_checkable.
        Static type checkers would catch this issue.
        """
        sync_graph = SyncGraph()
        # Runtime check only verifies methods exist, not that they're async
        assert isinstance(sync_graph, ProtocolIntentGraph)

    def test_wrong_signature_still_passes_isinstance_check(self) -> None:
        """A class with wrong signature passes isinstance (runtime check is structural).

        Note: Python's runtime protocol checking only verifies attribute presence,
        not the full method signature. Static type checkers would catch this.
        """
        wrong_sig = WrongSignatureGraph()
        # Runtime check only verifies methods exist
        assert isinstance(wrong_sig, ProtocolIntentGraph)


@pytest.mark.unit
class TestMockIntentGraphImplementation:
    """Test that MockIntentGraph has all required members."""

    def test_mock_has_all_methods(self) -> None:
        """Mock should have all required methods."""
        graph = MockIntentGraph()
        assert hasattr(graph, "store_intent")
        assert hasattr(graph, "get_session_intents")
        assert hasattr(graph, "health_check")
        assert callable(graph.store_intent)
        assert callable(graph.get_session_intents)
        assert callable(graph.health_check)

    def test_mock_methods_are_async(self) -> None:
        """Mock methods should all be async."""
        graph = MockIntentGraph()
        assert inspect.iscoroutinefunction(graph.store_intent)
        assert inspect.iscoroutinefunction(graph.get_session_intents)
        assert inspect.iscoroutinefunction(graph.health_check)

    @pytest.mark.asyncio
    async def test_mock_store_intent_returns_result(self) -> None:
        """Mock store_intent should return a stored event."""
        graph = MockIntentGraph()
        intent_data = MockIntentClassificationInput(
            content="Generate a Python function",
            correlation_id="test-corr-123",
        )

        result = await graph.store_intent(
            session_id="test-session",
            intent_data=intent_data,
            correlation_id="test-corr-123",
        )

        assert result is not None
        assert result.event_id is not None
        assert result.session_id == "test-session"
        assert result.correlation_id == "test-corr-123"

    @pytest.mark.asyncio
    async def test_mock_store_intent_generates_correlation_id(self) -> None:
        """Mock store_intent should generate correlation_id if not provided."""
        graph = MockIntentGraph()
        intent_data = MockIntentClassificationInput(content="Test content")

        result = await graph.store_intent(
            session_id="test-session",
            intent_data=intent_data,
        )

        assert result.correlation_id is not None
        assert len(result.correlation_id) > 0

    @pytest.mark.asyncio
    async def test_mock_get_session_intents_returns_list(self) -> None:
        """Mock get_session_intents should return a list of intents."""
        graph = MockIntentGraph()

        # Store some intents first
        for i in range(3):
            intent_data = MockIntentClassificationInput(content=f"Test content {i}")
            await graph.store_intent(
                session_id="test-session",
                intent_data=intent_data,
            )

        # Retrieve intents
        intents = await graph.get_session_intents("test-session")

        assert intents is not None
        assert isinstance(intents, list)
        assert len(intents) == 3

    @pytest.mark.asyncio
    async def test_mock_get_session_intents_returns_empty_for_unknown_session(
        self,
    ) -> None:
        """Mock get_session_intents should return empty list for unknown session."""
        graph = MockIntentGraph()

        intents = await graph.get_session_intents("nonexistent-session")

        assert intents is not None
        assert isinstance(intents, list)
        assert len(intents) == 0

    @pytest.mark.asyncio
    async def test_mock_get_session_intents_filters_by_min_confidence(self) -> None:
        """Mock get_session_intents should filter by min_confidence."""
        graph = MockIntentGraph()

        # Store intents (mock uses default 0.95 confidence)
        for i in range(3):
            intent_data = MockIntentClassificationInput(content=f"Test {i}")
            await graph.store_intent(session_id="test-session", intent_data=intent_data)

        # All intents have 0.95 confidence, so filtering at 0.9 returns all
        intents = await graph.get_session_intents("test-session", min_confidence=0.9)
        assert len(intents) == 3

        # Filtering at 0.99 returns none (since mock uses 0.95)
        intents = await graph.get_session_intents("test-session", min_confidence=0.99)
        assert len(intents) == 0

    @pytest.mark.asyncio
    async def test_mock_get_session_intents_respects_limit(self) -> None:
        """Mock get_session_intents should respect the limit parameter."""
        graph = MockIntentGraph()

        # Store 5 intents
        for i in range(5):
            intent_data = MockIntentClassificationInput(content=f"Test {i}")
            await graph.store_intent(session_id="test-session", intent_data=intent_data)

        # Request only 2
        intents = await graph.get_session_intents("test-session", limit=2)
        assert len(intents) == 2

        # Request all (no limit)
        intents = await graph.get_session_intents("test-session")
        assert len(intents) == 5

    @pytest.mark.asyncio
    async def test_mock_health_check_returns_bool(self) -> None:
        """Mock health_check should return a boolean."""
        graph = MockIntentGraph()

        result = await graph.health_check()

        assert result is not None
        assert isinstance(result, bool)
        assert result is True


@pytest.mark.unit
class TestProtocolIntentGraphImports:
    """Test protocol imports from different locations."""

    def test_import_from_protocol_module(self) -> None:
        """Test direct import from protocol_intent_graph module."""
        from omnibase_spi.protocols.intelligence.protocol_intent_graph import (
            ProtocolIntentGraph as DirectProtocolIntentGraph,
        )

        graph = MockIntentGraph()
        assert isinstance(graph, DirectProtocolIntentGraph)

    def test_protocol_exports_from_intelligence_module(self) -> None:
        """Protocol should be importable from intelligence module."""
        from omnibase_spi.protocols.intelligence import (
            ProtocolIntentGraph as IntelligenceProtocolIntentGraph,
        )

        graph = MockIntentGraph()
        assert isinstance(graph, IntelligenceProtocolIntentGraph)

    def test_imports_are_identical(self) -> None:
        """Verify imports from different locations are the same class."""
        from omnibase_spi.protocols.intelligence import (
            ProtocolIntentGraph as IntelligenceProtocolIntentGraph,
        )
        from omnibase_spi.protocols.intelligence.protocol_intent_graph import (
            ProtocolIntentGraph as DirectProtocolIntentGraph,
        )

        assert DirectProtocolIntentGraph is IntelligenceProtocolIntentGraph

    def test_protocol_exports_from_main_module(self) -> None:
        """Protocol should be importable from main protocols module."""
        from omnibase_spi.protocols import (
            ProtocolIntentGraph as MainProtocolIntentGraph,
        )

        graph = MockIntentGraph()
        assert isinstance(graph, MainProtocolIntentGraph)


@pytest.mark.unit
class TestProtocolIntentGraphDocumentation:
    """Test that ProtocolIntentGraph has proper documentation."""

    def test_protocol_has_docstring(self) -> None:
        """ProtocolIntentGraph should have a docstring."""
        assert ProtocolIntentGraph.__doc__ is not None
        assert len(ProtocolIntentGraph.__doc__.strip()) > 0

    def test_docstring_mentions_intent_graph(self) -> None:
        """Docstring should mention intent graph purpose."""
        doc = ProtocolIntentGraph.__doc__ or ""
        # Should mention intent or persistence/storage concepts
        assert "intent" in doc.lower() or "graph" in doc.lower()

    def test_store_intent_method_has_docstring(self) -> None:
        """The store_intent method should have a docstring."""
        method = getattr(ProtocolIntentGraph, "store_intent", None)
        assert method is not None
        assert method.__doc__ is not None
        assert len(method.__doc__.strip()) > 0

    def test_get_session_intents_method_has_docstring(self) -> None:
        """The get_session_intents method should have a docstring."""
        method = getattr(ProtocolIntentGraph, "get_session_intents", None)
        assert method is not None
        assert method.__doc__ is not None
        assert len(method.__doc__.strip()) > 0

    def test_health_check_method_has_docstring(self) -> None:
        """The health_check method should have a docstring."""
        method = getattr(ProtocolIntentGraph, "health_check", None)
        assert method is not None
        assert method.__doc__ is not None
        assert len(method.__doc__.strip()) > 0


@pytest.mark.unit
class TestIntentGraphSessionIsolation:
    """Test that the intent graph properly isolates sessions."""

    @pytest.mark.asyncio
    async def test_intents_are_isolated_by_session(self) -> None:
        """Intents stored in one session should not appear in another."""
        graph = MockIntentGraph()

        # Store intents in different sessions
        intent_data1 = MockIntentClassificationInput(content="Session 1 content")
        intent_data2 = MockIntentClassificationInput(content="Session 2 content")

        await graph.store_intent(session_id="session-1", intent_data=intent_data1)
        await graph.store_intent(session_id="session-2", intent_data=intent_data2)

        # Verify isolation
        session1_intents = await graph.get_session_intents("session-1")
        session2_intents = await graph.get_session_intents("session-2")

        assert len(session1_intents) == 1
        assert len(session2_intents) == 1

    @pytest.mark.asyncio
    async def test_multiple_intents_same_session(self) -> None:
        """Multiple intents can be stored in the same session."""
        graph = MockIntentGraph()

        # Store multiple intents in same session
        for i in range(3):
            intent_data = MockIntentClassificationInput(content=f"Content {i}")
            await graph.store_intent(
                session_id="multi-intent-session",
                intent_data=intent_data,
            )

        # Verify all intents are present
        intents = await graph.get_session_intents("multi-intent-session")
        assert len(intents) == 3


@pytest.mark.unit
class TestIntentGraphCorrelationTracking:
    """Test correlation ID handling in the intent graph."""

    @pytest.mark.asyncio
    async def test_correlation_id_preserved(self) -> None:
        """Correlation ID passed to store_intent should be preserved in result."""
        graph = MockIntentGraph()
        intent_data = MockIntentClassificationInput(content="Test content")

        result = await graph.store_intent(
            session_id="test-session",
            intent_data=intent_data,
            correlation_id="my-correlation-123",
        )

        assert result.correlation_id == "my-correlation-123"

    @pytest.mark.asyncio
    async def test_correlation_id_auto_generated_when_not_provided(self) -> None:
        """Correlation ID should be auto-generated when not provided."""
        graph = MockIntentGraph()
        intent_data = MockIntentClassificationInput(content="Test content")

        result = await graph.store_intent(
            session_id="test-session",
            intent_data=intent_data,
            # No correlation_id provided
        )

        assert result.correlation_id is not None
        assert len(result.correlation_id) > 0

    @pytest.mark.asyncio
    async def test_each_store_gets_unique_event_id(self) -> None:
        """Each store operation should generate a unique event ID."""
        graph = MockIntentGraph()
        intent_data = MockIntentClassificationInput(content="Test content")

        result1 = await graph.store_intent(
            session_id="test-session", intent_data=intent_data
        )
        result2 = await graph.store_intent(
            session_id="test-session", intent_data=intent_data
        )

        assert result1.event_id != result2.event_id
