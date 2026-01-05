"""
Tests for ProtocolGraphDatabaseHandler typed protocol changes.

This module validates that ProtocolGraphDatabaseHandler:
- Is properly runtime checkable
- Defines required methods and properties
- describe() is async (key change in PR #47)
- All methods have correct signatures
- Cannot be instantiated directly

These tests verify the typed-dynamic pattern introduced in PR #47 (OMN-710),
specifically that describe() is now async to support I/O operations.
"""

import inspect
from collections.abc import Mapping
from typing import Any, Protocol

import pytest

from omnibase_spi.protocols.storage.protocol_graph_database_handler import (
    ProtocolGraphDatabaseHandler,
)

# =============================================================================
# Mock Types for Testing
# =============================================================================


class MockGraphQueryResult:
    """Mock implementation of ModelGraphQueryResult."""

    def __init__(
        self,
        records: list[dict[str, Any]] | None = None,
        execution_time_ms: float = 10.0,
    ) -> None:
        self.records = records or []
        self.execution_time_ms = execution_time_ms
        self.summary = None
        self.counters = None


class MockGraphBatchResult:
    """Mock implementation of ModelGraphBatchResult."""

    def __init__(
        self,
        results: list[MockGraphQueryResult] | None = None,
        success: bool = True,
    ) -> None:
        self.results = results or []
        self.success = success
        self.transaction_id = None
        self.rollback_occurred = False
        self.execution_time_ms = 50.0


class MockGraphDatabaseNode:
    """Mock implementation of ModelGraphDatabaseNode."""

    def __init__(
        self,
        node_id: str | int = "node-1",
        labels: list[str] | None = None,
        properties: dict[str, Any] | None = None,
    ) -> None:
        self.id = node_id
        self.element_id = f"element:{node_id}"
        self.labels = labels or ["Node"]
        self.properties = properties or {}
        self.execution_time_ms = 5.0


class MockGraphRelationship:
    """Mock implementation of ModelGraphRelationship."""

    def __init__(
        self,
        rel_id: str | int = "rel-1",
        rel_type: str = "RELATES_TO",
        start_id: str | int = "node-1",
        end_id: str | int = "node-2",
    ) -> None:
        self.id = rel_id
        self.element_id = f"element:{rel_id}"
        self.relationship_type = rel_type
        self.start_node_id = start_id
        self.end_node_id = end_id
        self.properties: dict[str, Any] = {}
        self.execution_time_ms = 5.0


class MockGraphDeleteResult:
    """Mock implementation of ModelGraphDeleteResult."""

    def __init__(self, success: bool = True, entity_id: str | int = "node-1") -> None:
        self.success = success
        self.entity_id = entity_id
        self.relationships_deleted = 0
        self.execution_time_ms = 5.0


class MockGraphTraversalResult:
    """Mock implementation of ModelGraphTraversalResult."""

    def __init__(self) -> None:
        self.nodes: list[MockGraphDatabaseNode] = []
        self.relationships: list[MockGraphRelationship] = []
        self.paths: list[list[Any]] = []
        self.depth_reached = 1
        self.execution_time_ms = 20.0


class MockGraphHealthStatus:
    """Mock implementation of ModelGraphHealthStatus."""

    def __init__(
        self,
        healthy: bool = True,
        latency_ms: float = 5.0,
        database_version: str = "5.0.0",
    ) -> None:
        self.healthy = healthy
        self.latency_ms = latency_ms
        self.database_version = database_version
        self.connection_count = 10
        self.details: dict[str, Any] = {}
        self.last_error: str | None = None
        self.cached = False


class MockGraphHandlerMetadata:
    """Mock implementation of ModelGraphHandlerMetadata."""

    def __init__(
        self,
        handler_type: str = "graph_database",
        database_type: str = "neo4j",
    ) -> None:
        self.handler_type = handler_type
        self.database_type = database_type
        self.capabilities = ["cypher", "transactions", "traversal"]
        self.version = "1.0.0"
        self.supports_transactions = True
        self.connection_info: dict[str, Any] = {"host": "localhost", "port": 7687}


class MockGraphTraversalFilters:
    """Mock implementation of ModelGraphTraversalFilters."""

    def __init__(self, node_labels: list[str] | None = None) -> None:
        self.node_labels = node_labels or []
        self.node_properties: dict[str, Any] = {}
        self.relationship_properties: dict[str, Any] = {}


# =============================================================================
# Compliant Implementation
# =============================================================================


class CompliantGraphDatabaseHandler:
    """
    Test double implementing all ProtocolGraphDatabaseHandler requirements.

    Key changes from PR #47:
    - describe() is now async (can perform I/O for accurate metadata)
    """

    @property
    def handler_type(self) -> str:
        """Return handler type identifier."""
        return "graph_database"

    @property
    def supports_transactions(self) -> bool:
        """Return whether transactions are supported."""
        return True

    async def initialize(
        self,
        connection_uri: str,
        auth: tuple[str, str] | None = None,
        *,
        options: Mapping[str, Any] | None = None,
    ) -> None:
        """Initialize connection."""
        _ = (connection_uri, auth, options)

    async def shutdown(self, timeout_seconds: float = 30.0) -> None:
        """Shutdown handler."""
        _ = timeout_seconds

    async def execute_query(
        self,
        query: str,
        parameters: Mapping[str, Any] | None = None,
    ) -> MockGraphQueryResult:
        """Execute a graph query."""
        _ = (query, parameters)
        return MockGraphQueryResult()

    async def execute_query_batch(
        self,
        queries: list[tuple[str, Mapping[str, Any] | None]],
        transaction: bool = True,
    ) -> MockGraphBatchResult:
        """Execute multiple queries."""
        _ = (queries, transaction)
        return MockGraphBatchResult()

    async def create_node(
        self,
        labels: list[str],
        properties: Mapping[str, Any],
    ) -> MockGraphDatabaseNode:
        """Create a node."""
        return MockGraphDatabaseNode(labels=labels, properties=dict(properties))

    async def create_relationship(
        self,
        from_node_id: str | int,
        to_node_id: str | int,
        relationship_type: str,
        properties: Mapping[str, Any] | None = None,
    ) -> MockGraphRelationship:
        """Create a relationship."""
        return MockGraphRelationship(
            rel_type=relationship_type,
            start_id=from_node_id,
            end_id=to_node_id,
        )

    async def delete_node(
        self,
        node_id: str | int,
        detach: bool = False,
    ) -> MockGraphDeleteResult:
        """Delete a node."""
        _ = detach
        return MockGraphDeleteResult(entity_id=node_id)

    async def delete_relationship(
        self,
        relationship_id: str | int,
    ) -> MockGraphDeleteResult:
        """Delete a relationship."""
        return MockGraphDeleteResult(entity_id=relationship_id)

    async def traverse(
        self,
        start_node_id: str | int,
        relationship_types: list[str] | None = None,
        direction: str = "outgoing",
        max_depth: int = 1,
        filters: MockGraphTraversalFilters | None = None,
    ) -> MockGraphTraversalResult:
        """Traverse the graph."""
        _ = (start_node_id, relationship_types, direction, max_depth, filters)
        return MockGraphTraversalResult()

    async def health_check(self) -> MockGraphHealthStatus:
        """Check handler health."""
        return MockGraphHealthStatus(healthy=True)

    async def describe(self) -> MockGraphHandlerMetadata:
        """
        Return handler metadata.

        NOTE: This method is now async (PR #47 change) because implementations
        may need to check connection status, query database version, or perform
        other I/O operations to populate accurate metadata.
        """
        return MockGraphHandlerMetadata()


class PartialGraphDatabaseHandler:
    """
    Test double implementing only some ProtocolGraphDatabaseHandler methods.

    Missing: describe, traverse, delete_*, create_relationship, execute_query_batch
    """

    @property
    def handler_type(self) -> str:
        """Return handler type."""
        return "graph_database"

    @property
    def supports_transactions(self) -> bool:
        """Return transaction support."""
        return False

    async def initialize(
        self,
        connection_uri: str,
        auth: tuple[str, str] | None = None,
        *,
        options: Mapping[str, Any] | None = None,
    ) -> None:
        """Initialize connection."""
        _ = (connection_uri, auth, options)

    async def shutdown(self, timeout_seconds: float = 30.0) -> None:
        """Shutdown handler."""
        _ = timeout_seconds

    async def execute_query(
        self,
        query: str,
        parameters: Mapping[str, Any] | None = None,
    ) -> MockGraphQueryResult:
        """Execute a query."""
        _ = (query, parameters)
        return MockGraphQueryResult()

    async def create_node(
        self,
        labels: list[str],
        properties: Mapping[str, Any],
    ) -> MockGraphDatabaseNode:
        """Create a node."""
        return MockGraphDatabaseNode(labels=labels)

    async def health_check(self) -> MockGraphHealthStatus:
        """Check health."""
        return MockGraphHealthStatus()


# =============================================================================
# Handler with Sync describe() for Negative Testing
# =============================================================================


class SyncDescribeGraphHandler:
    """
    Handler with synchronous describe() method.

    This represents the OLD pattern before PR #47. The describe() method
    should now be async.
    """

    @property
    def handler_type(self) -> str:
        return "graph_database"

    @property
    def supports_transactions(self) -> bool:
        return True

    async def initialize(
        self,
        connection_uri: str,
        auth: tuple[str, str] | None = None,
        *,
        options: Mapping[str, Any] | None = None,
    ) -> None:
        pass

    async def shutdown(self, timeout_seconds: float = 30.0) -> None:
        pass

    async def execute_query(
        self,
        query: str,
        parameters: Mapping[str, Any] | None = None,
    ) -> MockGraphQueryResult:
        return MockGraphQueryResult()

    async def execute_query_batch(
        self,
        queries: list[tuple[str, Mapping[str, Any] | None]],
        transaction: bool = True,
    ) -> MockGraphBatchResult:
        return MockGraphBatchResult()

    async def create_node(
        self,
        labels: list[str],
        properties: Mapping[str, Any],
    ) -> MockGraphDatabaseNode:
        return MockGraphDatabaseNode(labels=labels)

    async def create_relationship(
        self,
        from_node_id: str | int,
        to_node_id: str | int,
        relationship_type: str,
        properties: Mapping[str, Any] | None = None,
    ) -> MockGraphRelationship:
        return MockGraphRelationship()

    async def delete_node(
        self,
        node_id: str | int,
        detach: bool = False,
    ) -> MockGraphDeleteResult:
        return MockGraphDeleteResult()

    async def delete_relationship(
        self,
        relationship_id: str | int,
    ) -> MockGraphDeleteResult:
        return MockGraphDeleteResult()

    async def traverse(
        self,
        start_node_id: str | int,
        relationship_types: list[str] | None = None,
        direction: str = "outgoing",
        max_depth: int = 1,
        filters: MockGraphTraversalFilters | None = None,
    ) -> MockGraphTraversalResult:
        return MockGraphTraversalResult()

    async def health_check(self) -> MockGraphHealthStatus:
        return MockGraphHealthStatus()

    def describe(self) -> MockGraphHandlerMetadata:
        """Synchronous describe - OLD pattern (before PR #47)."""
        return MockGraphHandlerMetadata()


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def compliant_handler() -> CompliantGraphDatabaseHandler:
    """Provide a compliant graph database handler for testing."""
    return CompliantGraphDatabaseHandler()


# =============================================================================
# Protocol Definition Tests
# =============================================================================


@pytest.mark.unit
class TestProtocolGraphDatabaseHandlerProtocol:
    """Test suite for ProtocolGraphDatabaseHandler protocol definition."""

    def test_protocol_is_runtime_checkable(self) -> None:
        """ProtocolGraphDatabaseHandler should be runtime_checkable."""
        assert hasattr(ProtocolGraphDatabaseHandler, "_is_runtime_protocol") or hasattr(
            ProtocolGraphDatabaseHandler, "__runtime_protocol__"
        )

    def test_protocol_is_protocol(self) -> None:
        """ProtocolGraphDatabaseHandler should be a Protocol class."""
        assert any(
            base is Protocol or base.__name__ == "Protocol"
            for base in ProtocolGraphDatabaseHandler.__mro__
        )

    def test_protocol_has_handler_type_property(self) -> None:
        """Should define handler_type property."""
        assert "handler_type" in dir(ProtocolGraphDatabaseHandler)

    def test_protocol_has_supports_transactions_property(self) -> None:
        """Should define supports_transactions property."""
        assert "supports_transactions" in dir(ProtocolGraphDatabaseHandler)

    def test_protocol_has_initialize_method(self) -> None:
        """Should define initialize method."""
        assert "initialize" in dir(ProtocolGraphDatabaseHandler)

    def test_protocol_has_shutdown_method(self) -> None:
        """Should define shutdown method."""
        assert "shutdown" in dir(ProtocolGraphDatabaseHandler)

    def test_protocol_has_execute_query_method(self) -> None:
        """Should define execute_query method."""
        assert "execute_query" in dir(ProtocolGraphDatabaseHandler)

    def test_protocol_has_execute_query_batch_method(self) -> None:
        """Should define execute_query_batch method."""
        assert "execute_query_batch" in dir(ProtocolGraphDatabaseHandler)

    def test_protocol_has_create_node_method(self) -> None:
        """Should define create_node method."""
        assert "create_node" in dir(ProtocolGraphDatabaseHandler)

    def test_protocol_has_create_relationship_method(self) -> None:
        """Should define create_relationship method."""
        assert "create_relationship" in dir(ProtocolGraphDatabaseHandler)

    def test_protocol_has_delete_node_method(self) -> None:
        """Should define delete_node method."""
        assert "delete_node" in dir(ProtocolGraphDatabaseHandler)

    def test_protocol_has_delete_relationship_method(self) -> None:
        """Should define delete_relationship method."""
        assert "delete_relationship" in dir(ProtocolGraphDatabaseHandler)

    def test_protocol_has_traverse_method(self) -> None:
        """Should define traverse method."""
        assert "traverse" in dir(ProtocolGraphDatabaseHandler)

    def test_protocol_has_health_check_method(self) -> None:
        """Should define health_check method."""
        assert "health_check" in dir(ProtocolGraphDatabaseHandler)

    def test_protocol_has_describe_method(self) -> None:
        """Should define describe method."""
        assert "describe" in dir(ProtocolGraphDatabaseHandler)

    def test_protocol_cannot_be_instantiated(self) -> None:
        """ProtocolGraphDatabaseHandler should not be directly instantiable."""
        with pytest.raises(TypeError):
            ProtocolGraphDatabaseHandler()  # type: ignore[misc]


# =============================================================================
# Protocol Compliance Tests
# =============================================================================


@pytest.mark.unit
class TestProtocolGraphDatabaseHandlerCompliance:
    """Test isinstance checks for ProtocolGraphDatabaseHandler compliance."""

    def test_compliant_class_passes_isinstance(
        self, compliant_handler: CompliantGraphDatabaseHandler
    ) -> None:
        """A class implementing all methods should pass isinstance check."""
        assert isinstance(compliant_handler, ProtocolGraphDatabaseHandler)

    def test_partial_implementation_fails_isinstance(self) -> None:
        """A class missing methods should fail isinstance check."""
        handler = PartialGraphDatabaseHandler()
        assert not isinstance(handler, ProtocolGraphDatabaseHandler)


# =============================================================================
# Async describe() Tests - Core PR #47 Change
# =============================================================================


@pytest.mark.unit
class TestProtocolGraphDatabaseHandlerDescribeAsync:
    """Test describe() is async (key change in PR #47).

    The describe() method was changed from sync to async to support I/O
    operations when gathering metadata (checking connection, querying
    database version, etc.).
    """

    def test_describe_is_async_in_protocol(self) -> None:
        """describe should be defined as async in the protocol."""
        protocol_method = getattr(ProtocolGraphDatabaseHandler, "describe", None)
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)

    def test_describe_is_async_in_compliant_implementation(self) -> None:
        """describe should be async in compliant implementations."""
        assert inspect.iscoroutinefunction(CompliantGraphDatabaseHandler.describe)

    @pytest.mark.asyncio
    async def test_describe_can_be_awaited(
        self, compliant_handler: CompliantGraphDatabaseHandler
    ) -> None:
        """describe() should be awaitable and return metadata."""
        metadata = await compliant_handler.describe()
        assert metadata is not None
        assert hasattr(metadata, "handler_type")
        assert metadata.handler_type == "graph_database"

    @pytest.mark.asyncio
    async def test_describe_returns_typed_metadata(
        self, compliant_handler: CompliantGraphDatabaseHandler
    ) -> None:
        """describe() should return typed ModelGraphHandlerMetadata."""
        metadata = await compliant_handler.describe()
        # Verify typed attributes exist
        assert hasattr(metadata, "handler_type")
        assert hasattr(metadata, "database_type")
        assert hasattr(metadata, "capabilities")
        assert hasattr(metadata, "supports_transactions")

    @pytest.mark.asyncio
    async def test_describe_includes_capabilities(
        self, compliant_handler: CompliantGraphDatabaseHandler
    ) -> None:
        """describe() should include handler capabilities."""
        metadata = await compliant_handler.describe()
        assert isinstance(metadata.capabilities, list)
        assert len(metadata.capabilities) > 0

    @pytest.mark.asyncio
    async def test_describe_does_not_include_credentials(
        self, compliant_handler: CompliantGraphDatabaseHandler
    ) -> None:
        """describe() should not expose credentials in connection_info."""
        metadata = await compliant_handler.describe()
        if hasattr(metadata, "connection_info") and metadata.connection_info:
            info = metadata.connection_info
            forbidden_keys = {"password", "api_key", "secret", "token", "credential"}
            info_keys_lower = {k.lower() for k in info.keys()}
            for key in forbidden_keys:
                assert key not in info_keys_lower


# =============================================================================
# Async Method Tests
# =============================================================================


@pytest.mark.unit
class TestProtocolGraphDatabaseHandlerAsyncNature:
    """Test that all async methods are properly defined."""

    def test_initialize_is_async(self) -> None:
        """initialize should be async."""
        protocol_method = getattr(ProtocolGraphDatabaseHandler, "initialize", None)
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)

    def test_shutdown_is_async(self) -> None:
        """shutdown should be async."""
        protocol_method = getattr(ProtocolGraphDatabaseHandler, "shutdown", None)
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)

    def test_execute_query_is_async(self) -> None:
        """execute_query should be async."""
        protocol_method = getattr(ProtocolGraphDatabaseHandler, "execute_query", None)
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)

    def test_execute_query_batch_is_async(self) -> None:
        """execute_query_batch should be async."""
        protocol_method = getattr(
            ProtocolGraphDatabaseHandler, "execute_query_batch", None
        )
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)

    def test_create_node_is_async(self) -> None:
        """create_node should be async."""
        protocol_method = getattr(ProtocolGraphDatabaseHandler, "create_node", None)
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)

    def test_create_relationship_is_async(self) -> None:
        """create_relationship should be async."""
        protocol_method = getattr(
            ProtocolGraphDatabaseHandler, "create_relationship", None
        )
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)

    def test_delete_node_is_async(self) -> None:
        """delete_node should be async."""
        protocol_method = getattr(ProtocolGraphDatabaseHandler, "delete_node", None)
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)

    def test_delete_relationship_is_async(self) -> None:
        """delete_relationship should be async."""
        protocol_method = getattr(
            ProtocolGraphDatabaseHandler, "delete_relationship", None
        )
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)

    def test_traverse_is_async(self) -> None:
        """traverse should be async."""
        protocol_method = getattr(ProtocolGraphDatabaseHandler, "traverse", None)
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)

    def test_health_check_is_async(self) -> None:
        """health_check should be async."""
        protocol_method = getattr(ProtocolGraphDatabaseHandler, "health_check", None)
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)

    def test_describe_is_async(self) -> None:
        """describe should be async (PR #47 change)."""
        protocol_method = getattr(ProtocolGraphDatabaseHandler, "describe", None)
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)


# =============================================================================
# Method Signature Tests
# =============================================================================


@pytest.mark.unit
class TestProtocolGraphDatabaseHandlerMethodSignatures:
    """Test method signatures and parameter handling."""

    @pytest.mark.asyncio
    async def test_execute_query_accepts_parameters(
        self, compliant_handler: CompliantGraphDatabaseHandler
    ) -> None:
        """execute_query should accept query and parameters."""
        result = await compliant_handler.execute_query(
            query="MATCH (n) RETURN n",
            parameters={"limit": 10},
        )
        assert result is not None

    @pytest.mark.asyncio
    async def test_create_node_accepts_labels_and_properties(
        self, compliant_handler: CompliantGraphDatabaseHandler
    ) -> None:
        """create_node should accept labels list and properties mapping."""
        node = await compliant_handler.create_node(
            labels=["Person", "Employee"],
            properties={"name": "Alice", "age": 30},
        )
        assert node is not None
        assert "Person" in node.labels

    @pytest.mark.asyncio
    async def test_traverse_accepts_all_parameters(
        self, compliant_handler: CompliantGraphDatabaseHandler
    ) -> None:
        """traverse should accept all optional parameters."""
        filters = MockGraphTraversalFilters(node_labels=["Person"])
        result = await compliant_handler.traverse(
            start_node_id="node-1",
            relationship_types=["KNOWS", "WORKS_WITH"],
            direction="both",
            max_depth=3,
            filters=filters,
        )
        assert result is not None


# =============================================================================
# Property Tests
# =============================================================================


@pytest.mark.unit
class TestProtocolGraphDatabaseHandlerProperties:
    """Test property definitions and values."""

    def test_handler_type_returns_string(
        self, compliant_handler: CompliantGraphDatabaseHandler
    ) -> None:
        """handler_type should return a string."""
        assert isinstance(compliant_handler.handler_type, str)
        assert compliant_handler.handler_type == "graph_database"

    def test_supports_transactions_returns_bool(
        self, compliant_handler: CompliantGraphDatabaseHandler
    ) -> None:
        """supports_transactions should return a boolean."""
        assert isinstance(compliant_handler.supports_transactions, bool)


# =============================================================================
# Import Tests
# =============================================================================


@pytest.mark.unit
class TestProtocolGraphDatabaseHandlerImports:
    """Test protocol imports from different locations."""

    def test_import_from_protocol_module(self) -> None:
        """Test direct import from protocol module."""
        from omnibase_spi.protocols.storage.protocol_graph_database_handler import (
            ProtocolGraphDatabaseHandler as DirectProtocol,
        )

        handler = CompliantGraphDatabaseHandler()
        assert isinstance(handler, DirectProtocol)

    def test_import_from_storage_package(self) -> None:
        """Test import from storage package."""
        from omnibase_spi.protocols.storage import (
            ProtocolGraphDatabaseHandler as PackageProtocol,
        )

        handler = CompliantGraphDatabaseHandler()
        assert isinstance(handler, PackageProtocol)


# =============================================================================
# Documentation Tests
# =============================================================================


@pytest.mark.unit
class TestProtocolGraphDatabaseHandlerDocumentation:
    """Test that protocol has proper documentation."""

    def test_protocol_has_docstring(self) -> None:
        """ProtocolGraphDatabaseHandler should have a docstring."""
        assert ProtocolGraphDatabaseHandler.__doc__ is not None
        assert len(ProtocolGraphDatabaseHandler.__doc__.strip()) > 0

    def test_describe_has_docstring(self) -> None:
        """describe method should have a docstring."""
        method = getattr(ProtocolGraphDatabaseHandler, "describe", None)
        assert method is not None
        assert method.__doc__ is not None

    def test_describe_docstring_mentions_async(self) -> None:
        """describe docstring should mention async nature."""
        method = getattr(ProtocolGraphDatabaseHandler, "describe", None)
        assert method is not None
        assert method.__doc__ is not None
        # Docstring should mention async or I/O requirement
        doc_lower = method.__doc__.lower()
        assert "async" in doc_lower or "i/o" in doc_lower
