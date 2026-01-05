"""
Tests for ProtocolVectorStoreHandler typed protocol changes.

This module validates that ProtocolVectorStoreHandler:
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

from omnibase_spi.protocols.storage.protocol_vector_store_handler import (
    ProtocolVectorStoreHandler,
)

# =============================================================================
# Mock Types for Testing
# =============================================================================


class MockVectorConnectionConfig:
    """Mock implementation of ModelVectorConnectionConfig."""

    def __init__(
        self,
        url: str = "http://localhost:6333",
        api_key: str | None = None,
        timeout: float = 30.0,
        pool_size: int = 10,
        collection_name: str | None = None,
    ) -> None:
        self.url = url
        self.api_key = api_key
        self.timeout = timeout
        self.pool_size = pool_size
        self.collection_name = collection_name


class MockVectorStoreResult:
    """Mock implementation of ModelVectorStoreResult."""

    def __init__(
        self,
        success: bool = True,
        embedding_id: str = "emb-1",
        index_name: str = "default",
    ) -> None:
        self.success = success
        self.embedding_id = embedding_id
        self.index_name = index_name
        self.timestamp = "2024-01-01T00:00:00Z"


class MockVectorBatchStoreResult:
    """Mock implementation of ModelVectorBatchStoreResult."""

    def __init__(
        self,
        success: bool = True,
        total_stored: int = 100,
    ) -> None:
        self.success = success
        self.total_stored = total_stored
        self.failed_ids: list[str] = []
        self.execution_time_ms = 150.0


class MockVectorSearchResult:
    """Mock individual search result."""

    def __init__(
        self,
        result_id: str = "emb-1",
        score: float = 0.95,
    ) -> None:
        self.id = result_id
        self.score = score
        self.metadata: dict[str, Any] = {}
        self.vector: list[float] | None = None


class MockVectorSearchResults:
    """Mock implementation of ModelVectorSearchResults."""

    def __init__(
        self,
        results: list[MockVectorSearchResult] | None = None,
        total_results: int = 0,
    ) -> None:
        self.results = results or []
        self.total_results = total_results or len(self.results)
        self.query_time_ms = 10.0


class MockVectorDeleteResult:
    """Mock implementation of ModelVectorDeleteResult."""

    def __init__(
        self,
        success: bool = True,
        embedding_id: str = "emb-1",
        deleted: bool = True,
    ) -> None:
        self.success = success
        self.embedding_id = embedding_id
        self.deleted = deleted
        self.total_deleted = 1 if deleted else 0
        self.failed_ids: list[str] = []
        self.not_found_ids: list[str] = []


class MockVectorIndexConfig:
    """Mock implementation of ModelVectorIndexConfig."""

    def __init__(
        self,
        shards: int = 1,
        replicas: int = 1,
        on_disk: bool = False,
    ) -> None:
        self.shards = shards
        self.replicas = replicas
        self.on_disk = on_disk
        self.quantization = None
        self.hnsw_config = None


class MockVectorIndexResult:
    """Mock implementation of ModelVectorIndexResult."""

    def __init__(
        self,
        success: bool = True,
        index_name: str = "test-index",
        dimension: int = 1536,
        metric: str = "cosine",
    ) -> None:
        self.success = success
        self.index_name = index_name
        self.dimension = dimension
        self.metric = metric
        self.created_at = "2024-01-01T00:00:00Z"
        self.deleted = False


class MockVectorHealthStatus:
    """Mock implementation of ModelVectorHealthStatus."""

    def __init__(
        self,
        healthy: bool = True,
        latency_ms: float = 5.0,
    ) -> None:
        self.healthy = healthy
        self.latency_ms = latency_ms
        self.details: dict[str, Any] = {}
        self.indices: list[str] = ["default"]
        self.last_error: str | None = None


class MockVectorHandlerMetadata:
    """Mock implementation of ModelVectorHandlerMetadata."""

    def __init__(
        self,
        handler_type: str = "vector_store",
    ) -> None:
        self.handler_type = handler_type
        self.capabilities = ["store", "search", "delete", "create_index"]
        self.supported_metrics = ["cosine", "euclidean", "dot_product"]
        self.max_dimension = 4096
        self.max_batch_size = 1000
        self.version = "1.0.0"


class MockEmbedding:
    """Mock implementation of ModelEmbedding."""

    def __init__(
        self,
        embedding_id: str = "emb-1",
        vector: list[float] | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        self.id = embedding_id
        self.vector = vector or [0.1] * 1536
        self.metadata = metadata or {}


class MockVectorMetadataFilter:
    """Mock implementation of ModelVectorMetadataFilter."""

    def __init__(
        self,
        field: str = "category",
        operator: str = "eq",
        value: Any = "test",
    ) -> None:
        self.field = field
        self.operator = operator
        self.value = value


# =============================================================================
# Compliant Implementation
# =============================================================================


class CompliantVectorStoreHandler:
    """
    Test double implementing all ProtocolVectorStoreHandler requirements.

    Key changes from PR #47:
    - describe() is now async (can perform I/O for accurate metadata)
    """

    @property
    def handler_type(self) -> str:
        """Return handler type identifier."""
        return "vector_store"

    @property
    def supported_metrics(self) -> list[str]:
        """Return supported distance metrics."""
        return ["cosine", "euclidean", "dot_product"]

    async def initialize(
        self,
        connection_config: MockVectorConnectionConfig,
    ) -> None:
        """Initialize the handler."""
        _ = connection_config

    async def shutdown(self, timeout_seconds: float = 30.0) -> None:
        """Shutdown the handler."""
        _ = timeout_seconds

    async def store_embedding(
        self,
        embedding_id: str,
        vector: list[float],
        metadata: Mapping[str, Any] | None = None,
        index_name: str | None = None,
    ) -> MockVectorStoreResult:
        """Store a single embedding."""
        _ = (vector, metadata)
        return MockVectorStoreResult(
            embedding_id=embedding_id,
            index_name=index_name or "default",
        )

    async def store_embeddings_batch(
        self,
        embeddings: list[MockEmbedding],
        index_name: str | None = None,
        batch_size: int = 100,
    ) -> MockVectorBatchStoreResult:
        """Store multiple embeddings."""
        _ = (index_name, batch_size)
        return MockVectorBatchStoreResult(total_stored=len(embeddings))

    async def query_similar(
        self,
        query_vector: list[float],
        top_k: int = 10,
        index_name: str | None = None,
        filter_metadata: MockVectorMetadataFilter | None = None,
        include_metadata: bool = True,
        include_vectors: bool = False,
        score_threshold: float | None = None,
    ) -> MockVectorSearchResults:
        """Query for similar vectors."""
        _ = (
            query_vector,
            index_name,
            filter_metadata,
            include_metadata,
            include_vectors,
            score_threshold,
        )
        results = [
            MockVectorSearchResult(f"emb-{i}", 0.9 - i * 0.05) for i in range(top_k)
        ]
        return MockVectorSearchResults(results=results, total_results=top_k)

    async def delete_embedding(
        self,
        embedding_id: str,
        index_name: str | None = None,
    ) -> MockVectorDeleteResult:
        """Delete a single embedding."""
        _ = index_name
        return MockVectorDeleteResult(embedding_id=embedding_id)

    async def delete_embeddings_batch(
        self,
        embedding_ids: list[str],
        index_name: str | None = None,
    ) -> MockVectorDeleteResult:
        """Delete multiple embeddings."""
        _ = index_name
        result = MockVectorDeleteResult()
        result.total_deleted = len(embedding_ids)
        return result

    async def create_index(
        self,
        index_name: str,
        dimension: int,
        metric: str = "cosine",
        index_config: MockVectorIndexConfig | None = None,
    ) -> MockVectorIndexResult:
        """Create a new index."""
        _ = index_config
        return MockVectorIndexResult(
            index_name=index_name,
            dimension=dimension,
            metric=metric,
        )

    async def delete_index(
        self,
        index_name: str,
    ) -> MockVectorIndexResult:
        """Delete an index."""
        result = MockVectorIndexResult(index_name=index_name)
        result.deleted = True
        return result

    async def health_check(self) -> MockVectorHealthStatus:
        """Check handler health."""
        return MockVectorHealthStatus(healthy=True)

    async def describe(self) -> MockVectorHandlerMetadata:
        """
        Return handler metadata.

        NOTE: This method is now async (PR #47 change) because implementations
        may need to check connection status, query backend capabilities, or
        perform other I/O operations to provide accurate metadata.
        """
        return MockVectorHandlerMetadata()


class PartialVectorStoreHandler:
    """
    Test double implementing only some ProtocolVectorStoreHandler methods.

    Missing: describe, query_similar, delete_*, create/delete_index
    """

    @property
    def handler_type(self) -> str:
        """Return handler type."""
        return "vector_store"

    @property
    def supported_metrics(self) -> list[str]:
        """Return supported metrics."""
        return ["cosine"]

    async def initialize(
        self,
        connection_config: MockVectorConnectionConfig,
    ) -> None:
        """Initialize handler."""
        _ = connection_config

    async def shutdown(self, timeout_seconds: float = 30.0) -> None:
        """Shutdown handler."""
        _ = timeout_seconds

    async def store_embedding(
        self,
        embedding_id: str,
        vector: list[float],
        metadata: Mapping[str, Any] | None = None,
        index_name: str | None = None,
    ) -> MockVectorStoreResult:
        """Store embedding."""
        _ = (vector, metadata, index_name)
        return MockVectorStoreResult(embedding_id=embedding_id)

    async def store_embeddings_batch(
        self,
        embeddings: list[MockEmbedding],
        index_name: str | None = None,
        batch_size: int = 100,
    ) -> MockVectorBatchStoreResult:
        """Store batch."""
        _ = (index_name, batch_size)
        return MockVectorBatchStoreResult(total_stored=len(embeddings))

    async def health_check(self) -> MockVectorHealthStatus:
        """Check health."""
        return MockVectorHealthStatus()


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def compliant_handler() -> CompliantVectorStoreHandler:
    """Provide a compliant vector store handler for testing."""
    return CompliantVectorStoreHandler()


# =============================================================================
# Protocol Definition Tests
# =============================================================================


@pytest.mark.unit
class TestProtocolVectorStoreHandlerProtocol:
    """Test suite for ProtocolVectorStoreHandler protocol definition."""

    def test_protocol_is_runtime_checkable(self) -> None:
        """ProtocolVectorStoreHandler should be runtime_checkable."""
        assert hasattr(ProtocolVectorStoreHandler, "_is_runtime_protocol") or hasattr(
            ProtocolVectorStoreHandler, "__runtime_protocol__"
        )

    def test_protocol_is_protocol(self) -> None:
        """ProtocolVectorStoreHandler should be a Protocol class."""
        assert any(
            base is Protocol or base.__name__ == "Protocol"
            for base in ProtocolVectorStoreHandler.__mro__
        )

    def test_protocol_has_handler_type_property(self) -> None:
        """Should define handler_type property."""
        assert "handler_type" in dir(ProtocolVectorStoreHandler)

    def test_protocol_has_supported_metrics_property(self) -> None:
        """Should define supported_metrics property."""
        assert "supported_metrics" in dir(ProtocolVectorStoreHandler)

    def test_protocol_has_initialize_method(self) -> None:
        """Should define initialize method."""
        assert "initialize" in dir(ProtocolVectorStoreHandler)

    def test_protocol_has_shutdown_method(self) -> None:
        """Should define shutdown method."""
        assert "shutdown" in dir(ProtocolVectorStoreHandler)

    def test_protocol_has_store_embedding_method(self) -> None:
        """Should define store_embedding method."""
        assert "store_embedding" in dir(ProtocolVectorStoreHandler)

    def test_protocol_has_store_embeddings_batch_method(self) -> None:
        """Should define store_embeddings_batch method."""
        assert "store_embeddings_batch" in dir(ProtocolVectorStoreHandler)

    def test_protocol_has_query_similar_method(self) -> None:
        """Should define query_similar method."""
        assert "query_similar" in dir(ProtocolVectorStoreHandler)

    def test_protocol_has_delete_embedding_method(self) -> None:
        """Should define delete_embedding method."""
        assert "delete_embedding" in dir(ProtocolVectorStoreHandler)

    def test_protocol_has_delete_embeddings_batch_method(self) -> None:
        """Should define delete_embeddings_batch method."""
        assert "delete_embeddings_batch" in dir(ProtocolVectorStoreHandler)

    def test_protocol_has_create_index_method(self) -> None:
        """Should define create_index method."""
        assert "create_index" in dir(ProtocolVectorStoreHandler)

    def test_protocol_has_delete_index_method(self) -> None:
        """Should define delete_index method."""
        assert "delete_index" in dir(ProtocolVectorStoreHandler)

    def test_protocol_has_health_check_method(self) -> None:
        """Should define health_check method."""
        assert "health_check" in dir(ProtocolVectorStoreHandler)

    def test_protocol_has_describe_method(self) -> None:
        """Should define describe method."""
        assert "describe" in dir(ProtocolVectorStoreHandler)

    def test_protocol_cannot_be_instantiated(self) -> None:
        """ProtocolVectorStoreHandler should not be directly instantiable."""
        with pytest.raises(TypeError):
            ProtocolVectorStoreHandler()  # type: ignore[misc]


# =============================================================================
# Protocol Compliance Tests
# =============================================================================


@pytest.mark.unit
class TestProtocolVectorStoreHandlerCompliance:
    """Test isinstance checks for ProtocolVectorStoreHandler compliance."""

    def test_compliant_class_passes_isinstance(
        self, compliant_handler: CompliantVectorStoreHandler
    ) -> None:
        """A class implementing all methods should pass isinstance check."""
        assert isinstance(compliant_handler, ProtocolVectorStoreHandler)

    def test_partial_implementation_fails_isinstance(self) -> None:
        """A class missing methods should fail isinstance check."""
        handler = PartialVectorStoreHandler()
        assert not isinstance(handler, ProtocolVectorStoreHandler)


# =============================================================================
# Async describe() Tests - Core PR #47 Change
# =============================================================================


@pytest.mark.unit
class TestProtocolVectorStoreHandlerDescribeAsync:
    """Test describe() is async (key change in PR #47).

    The describe() method was changed from sync to async to support I/O
    operations when gathering metadata (checking connection, querying
    backend capabilities, etc.).
    """

    def test_describe_is_async_in_protocol(self) -> None:
        """describe should be defined as async in the protocol."""
        protocol_method = getattr(ProtocolVectorStoreHandler, "describe", None)
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)

    def test_describe_is_async_in_compliant_implementation(self) -> None:
        """describe should be async in compliant implementations."""
        assert inspect.iscoroutinefunction(CompliantVectorStoreHandler.describe)

    @pytest.mark.asyncio
    async def test_describe_can_be_awaited(
        self, compliant_handler: CompliantVectorStoreHandler
    ) -> None:
        """describe() should be awaitable and return metadata."""
        metadata = await compliant_handler.describe()
        assert metadata is not None
        assert hasattr(metadata, "handler_type")
        assert metadata.handler_type == "vector_store"

    @pytest.mark.asyncio
    async def test_describe_returns_typed_metadata(
        self, compliant_handler: CompliantVectorStoreHandler
    ) -> None:
        """describe() should return typed ModelVectorHandlerMetadata."""
        metadata = await compliant_handler.describe()
        # Verify typed attributes exist
        assert hasattr(metadata, "handler_type")
        assert hasattr(metadata, "capabilities")
        assert hasattr(metadata, "supported_metrics")
        assert hasattr(metadata, "max_dimension")
        assert hasattr(metadata, "max_batch_size")

    @pytest.mark.asyncio
    async def test_describe_includes_capabilities(
        self, compliant_handler: CompliantVectorStoreHandler
    ) -> None:
        """describe() should include handler capabilities."""
        metadata = await compliant_handler.describe()
        assert isinstance(metadata.capabilities, list)
        assert len(metadata.capabilities) > 0

    @pytest.mark.asyncio
    async def test_describe_includes_supported_metrics(
        self, compliant_handler: CompliantVectorStoreHandler
    ) -> None:
        """describe() should include supported metrics."""
        metadata = await compliant_handler.describe()
        assert isinstance(metadata.supported_metrics, list)
        assert "cosine" in metadata.supported_metrics

    @pytest.mark.asyncio
    async def test_describe_does_not_include_credentials(
        self, compliant_handler: CompliantVectorStoreHandler
    ) -> None:
        """describe() should not expose credentials."""
        metadata = await compliant_handler.describe()
        # Convert to dict-like for inspection if needed
        forbidden_attrs = {"api_key", "password", "secret", "token", "credential"}
        for attr in forbidden_attrs:
            if hasattr(metadata, attr):
                value = getattr(metadata, attr)
                assert value is None, f"Credential attribute '{attr}' should be None"


# =============================================================================
# Async Method Tests
# =============================================================================


@pytest.mark.unit
class TestProtocolVectorStoreHandlerAsyncNature:
    """Test that all async methods are properly defined."""

    def test_initialize_is_async(self) -> None:
        """initialize should be async."""
        protocol_method = getattr(ProtocolVectorStoreHandler, "initialize", None)
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)

    def test_shutdown_is_async(self) -> None:
        """shutdown should be async."""
        protocol_method = getattr(ProtocolVectorStoreHandler, "shutdown", None)
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)

    def test_store_embedding_is_async(self) -> None:
        """store_embedding should be async."""
        protocol_method = getattr(ProtocolVectorStoreHandler, "store_embedding", None)
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)

    def test_store_embeddings_batch_is_async(self) -> None:
        """store_embeddings_batch should be async."""
        protocol_method = getattr(
            ProtocolVectorStoreHandler, "store_embeddings_batch", None
        )
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)

    def test_query_similar_is_async(self) -> None:
        """query_similar should be async."""
        protocol_method = getattr(ProtocolVectorStoreHandler, "query_similar", None)
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)

    def test_delete_embedding_is_async(self) -> None:
        """delete_embedding should be async."""
        protocol_method = getattr(ProtocolVectorStoreHandler, "delete_embedding", None)
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)

    def test_delete_embeddings_batch_is_async(self) -> None:
        """delete_embeddings_batch should be async."""
        protocol_method = getattr(
            ProtocolVectorStoreHandler, "delete_embeddings_batch", None
        )
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)

    def test_create_index_is_async(self) -> None:
        """create_index should be async."""
        protocol_method = getattr(ProtocolVectorStoreHandler, "create_index", None)
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)

    def test_delete_index_is_async(self) -> None:
        """delete_index should be async."""
        protocol_method = getattr(ProtocolVectorStoreHandler, "delete_index", None)
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)

    def test_health_check_is_async(self) -> None:
        """health_check should be async."""
        protocol_method = getattr(ProtocolVectorStoreHandler, "health_check", None)
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)

    def test_describe_is_async(self) -> None:
        """describe should be async (PR #47 change)."""
        protocol_method = getattr(ProtocolVectorStoreHandler, "describe", None)
        assert protocol_method is not None
        assert inspect.iscoroutinefunction(protocol_method)


# =============================================================================
# Method Signature Tests
# =============================================================================


@pytest.mark.unit
class TestProtocolVectorStoreHandlerMethodSignatures:
    """Test method signatures and parameter handling."""

    @pytest.mark.asyncio
    async def test_store_embedding_accepts_all_parameters(
        self, compliant_handler: CompliantVectorStoreHandler
    ) -> None:
        """store_embedding should accept all parameters."""
        result = await compliant_handler.store_embedding(
            embedding_id="emb-1",
            vector=[0.1] * 1536,
            metadata={"source": "test.pdf", "page": 1},
            index_name="documents",
        )
        assert result.success is True
        assert result.embedding_id == "emb-1"

    @pytest.mark.asyncio
    async def test_query_similar_accepts_all_parameters(
        self, compliant_handler: CompliantVectorStoreHandler
    ) -> None:
        """query_similar should accept all parameters."""
        query_filter = MockVectorMetadataFilter(
            field="category",
            operator="eq",
            value="technical",
        )
        results = await compliant_handler.query_similar(
            query_vector=[0.1] * 1536,
            top_k=5,
            index_name="documents",
            filter_metadata=query_filter,
            include_metadata=True,
            include_vectors=False,
            score_threshold=0.7,
        )
        assert results.total_results == 5

    @pytest.mark.asyncio
    async def test_create_index_accepts_all_parameters(
        self, compliant_handler: CompliantVectorStoreHandler
    ) -> None:
        """create_index should accept all parameters."""
        config = MockVectorIndexConfig(on_disk=True)
        result = await compliant_handler.create_index(
            index_name="test-index",
            dimension=1536,
            metric="cosine",
            index_config=config,
        )
        assert result.success is True
        assert result.dimension == 1536


# =============================================================================
# Property Tests
# =============================================================================


@pytest.mark.unit
class TestProtocolVectorStoreHandlerProperties:
    """Test property definitions and values."""

    def test_handler_type_returns_string(
        self, compliant_handler: CompliantVectorStoreHandler
    ) -> None:
        """handler_type should return a string."""
        assert isinstance(compliant_handler.handler_type, str)
        assert compliant_handler.handler_type == "vector_store"

    def test_supported_metrics_returns_list(
        self, compliant_handler: CompliantVectorStoreHandler
    ) -> None:
        """supported_metrics should return a list of strings."""
        metrics = compliant_handler.supported_metrics
        assert isinstance(metrics, list)
        assert all(isinstance(m, str) for m in metrics)
        assert "cosine" in metrics


# =============================================================================
# Import Tests
# =============================================================================


@pytest.mark.unit
class TestProtocolVectorStoreHandlerImports:
    """Test protocol imports from different locations."""

    def test_import_from_protocol_module(self) -> None:
        """Test direct import from protocol module."""
        from omnibase_spi.protocols.storage.protocol_vector_store_handler import (
            ProtocolVectorStoreHandler as DirectProtocol,
        )

        handler = CompliantVectorStoreHandler()
        assert isinstance(handler, DirectProtocol)

    def test_import_from_storage_package(self) -> None:
        """Test import from storage package."""
        from omnibase_spi.protocols.storage import (
            ProtocolVectorStoreHandler as PackageProtocol,
        )

        handler = CompliantVectorStoreHandler()
        assert isinstance(handler, PackageProtocol)


# =============================================================================
# Documentation Tests
# =============================================================================


@pytest.mark.unit
class TestProtocolVectorStoreHandlerDocumentation:
    """Test that protocol has proper documentation."""

    def test_protocol_has_docstring(self) -> None:
        """ProtocolVectorStoreHandler should have a docstring."""
        assert ProtocolVectorStoreHandler.__doc__ is not None
        assert len(ProtocolVectorStoreHandler.__doc__.strip()) > 0

    def test_describe_has_docstring(self) -> None:
        """describe method should have a docstring."""
        method = getattr(ProtocolVectorStoreHandler, "describe", None)
        assert method is not None
        assert method.__doc__ is not None

    def test_describe_docstring_mentions_async(self) -> None:
        """describe docstring should mention async nature."""
        method = getattr(ProtocolVectorStoreHandler, "describe", None)
        assert method is not None
        assert method.__doc__ is not None
        # Docstring should mention async or I/O requirement
        doc_lower = method.__doc__.lower()
        assert "async" in doc_lower or "i/o" in doc_lower
