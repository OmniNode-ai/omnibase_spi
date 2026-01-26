"""
Vector Store Handler Protocol - ONEX SPI Interface.

Protocol definition for vector store operations. This is a specialized handler
protocol that extends the ProtocolHandler pattern for backend-agnostic vector
database operations (supports Qdrant, Pinecone, Weaviate, Milvus, Chroma, and
other vector stores).

The vector store handler provides:
    - Embedding storage with metadata association
    - Single and batch embedding operations
    - Similarity/distance-based vector search (ANN)
    - Metadata filtering during search
    - Index lifecycle management (create, delete)
    - Multiple distance metrics (cosine, euclidean, dot product)
    - Health monitoring and introspection

Key Protocols:
    - ProtocolVectorStoreHandler: Vector store handler interface

Core Models:
    This protocol uses typed models from ``omnibase_core.models.vector``:
        - ModelVectorConnectionConfig: Connection configuration
        - ModelEmbedding: Embedding with vector and metadata
        - ModelVectorStoreResult: Single store operation result
        - ModelVectorBatchStoreResult: Batch store operation result
        - ModelVectorSearchResults: Similarity search results
        - ModelVectorDeleteResult: Deletion operation result
        - ModelVectorIndexConfig: Index creation configuration
        - ModelVectorIndexResult: Index operation result
        - ModelVectorMetadataFilter: Metadata filter for search
        - ModelVectorHealthStatus: Health check return type
        - ModelVectorHandlerMetadata: Handler introspection metadata

Handler Lifecycle:
    1. Create handler instance
    2. Call initialize() with ModelVectorConnectionConfig
    3. Create indices with create_index() if needed
    4. Store embeddings with store_embedding() or store_embeddings_batch()
    5. Query with query_similar() for similarity search
    6. Call shutdown() to release resources

Example:
    ```python
    from omnibase_spi.protocols.storage import ProtocolVectorStoreHandler
    from omnibase_core.models.vector import (
        ModelVectorConnectionConfig,
        ModelEmbedding,
        ModelVectorMetadataFilter,
    )

    # Get handler from dependency injection
    handler: ProtocolVectorStoreHandler = get_vector_handler()

    # Initialize connection
    config = ModelVectorConnectionConfig(
        url="http://localhost:6333",
        api_key="secret-key",
        timeout=30.0,
    )
    await handler.initialize(config)

    # Create an index for document embeddings
    await handler.create_index(
        index_name="documents",
        dimension=1536,  # OpenAI embedding dimension
        metric="cosine",
    )

    # Store a single embedding
    await handler.store_embedding(
        embedding_id="doc_001",
        vector=[0.1, 0.2, ...],  # 1536-dimensional vector
        metadata={"source": "report.pdf", "page": 1},
        index_name="documents",
    )

    # Store embeddings in batch for efficiency
    embeddings = [
        ModelEmbedding(id="doc_002", vector=[...], metadata={"page": 2}),
        ModelEmbedding(id="doc_003", vector=[...], metadata={"page": 3}),
    ]
    result = await handler.store_embeddings_batch(
        embeddings=embeddings,
        index_name="documents",
        batch_size=100,
    )
    print(f"Stored {result.total_stored} embeddings")

    # Query for similar documents with metadata filtering
    filter_config = ModelVectorMetadataFilter(
        field="source",
        operator="eq",
        value="report.pdf",
    )
    results = await handler.query_similar(
        query_vector=query_embedding,
        top_k=5,
        index_name="documents",
        filter_metadata=filter_config,
        score_threshold=0.7,
    )
    for match in results.results:
        print(f"ID: {match.id}, Score: {match.score}")

    # Health check with typed response
    health = await handler.health_check()
    if health.healthy:
        print(f"Vector store OK, latency: {health.latency_ms}ms")

    # Cleanup
    await handler.shutdown()
    ```

Example implementations:
    - QdrantVectorStoreHandler: Qdrant gRPC/REST operations
    - PineconeVectorStoreHandler: Pinecone serverless API
    - WeaviateVectorStoreHandler: Weaviate GraphQL interface
    - MilvusVectorStoreHandler: Milvus distributed vector DB
    - ChromaVectorStoreHandler: Chroma embedded database

See Also:
    - ProtocolHandler: Base handler protocol pattern
    - ProtocolGraphDatabaseHandler: Graph database handler for relationships
    - ProtocolStorageBackend: General checkpoint/state persistence
    - ModelVectorSearchResults: Core model for search results
    - ModelEmbedding: Core model for embedding data
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_core.models.vector import (
        ModelEmbedding,
        ModelVectorBatchStoreResult,
        ModelVectorConnectionConfig,
        ModelVectorDeleteResult,
        ModelVectorHandlerMetadata,
        ModelVectorHealthStatus,
        ModelVectorIndexConfig,
        ModelVectorIndexResult,
        ModelVectorMetadataFilter,
        ModelVectorSearchResults,
        ModelVectorStoreResult,
    )
    from omnibase_core.types import JsonType


@runtime_checkable
class ProtocolVectorStoreHandler(Protocol):
    """
    Protocol for vector store operations including embedding storage and similarity search.

    This protocol defines the interface for handlers that manage vector embeddings,
    perform similarity searches, and handle index lifecycle operations. Implementations
    enable AI/ML applications to store and retrieve high-dimensional vector data
    efficiently.

    Handler vs Storage Backend Distinction:
        ProtocolVectorStoreHandler is for active vector operations (store, query, search)
        with direct client interaction. This differs from ProtocolStorageBackend which
        handles general checkpoint/state persistence. Vector handlers are typically
        used within RAG pipelines, semantic search systems, and embedding-based retrieval.

    Distance Metrics:
        The handler supports multiple distance/similarity metrics for vector comparison:
        - cosine: Cosine similarity (1 - cosine distance), range [-1, 1]
        - euclidean: L2 (Euclidean) distance, range [0, inf)
        - dot_product: Dot product similarity (inner product)
        - manhattan: L1 (Manhattan) distance, range [0, inf)

    Example implementations:
        - QdrantVectorStoreHandler: Qdrant gRPC/REST operations
        - PineconeVectorStoreHandler: Pinecone serverless API
        - WeaviateVectorStoreHandler: Weaviate GraphQL interface
        - ChromaVectorStoreHandler: Chroma embedded database

    Migration:
        This protocol is introduced in v0.3.0 as the standard interface for
        vector store operations. Future versions may add streaming and
        batch optimization methods.

    See Also:
        - ProtocolHandler: Base handler protocol pattern
        - ProtocolGraphDatabaseHandler: Graph database handler for relationship data
        - ModelVectorSearchResults: Result model for similarity search
        - ModelEmbedding: Embedding model with vector and metadata
        - ModelVectorConnectionConfig: Configuration model for connections
    """

    @property
    def handler_type(self) -> str:
        """
        The type of handler as a string identifier.

        Used for handler identification, routing, and metrics collection.
        Vector store handlers should return "vector_store" to distinguish
        from other handler types.

        Returns:
            String identifier "vector_store" for this handler type.

        Example:
            ```python
            handler = QdrantVectorStoreHandler()
            assert handler.handler_type == "vector_store"
            ```
        """
        ...

    @property
    def supported_metrics(self) -> list[str]:
        """
        List of distance/similarity metrics supported by this handler.

        Different vector databases support different distance metrics.
        This property allows callers to check metric availability before
        creating indices or performing searches.

        Common metrics:
            - "cosine": Cosine similarity (most common for text embeddings)
            - "euclidean": L2 distance (good for dense vectors)
            - "dot_product": Inner product (for normalized vectors)
            - "manhattan": L1 distance (sparse vectors)

        Returns:
            List of supported metric names as lowercase strings.

        Example:
            ```python
            if "cosine" in handler.supported_metrics:
                await handler.create_index("my_index", dimension=1536, metric="cosine")
            ```
        """
        ...

    async def initialize(
        self,
        connection_config: ModelVectorConnectionConfig,
    ) -> None:
        """
        Initialize the vector store handler with connection configuration.

        Establishes connection to the vector database, validates credentials,
        and prepares the handler for operations. Must be called before any
        other operations.

        Args:
            connection_config: Configuration model containing connection parameters.
                See ModelVectorConnectionConfig for available fields including:
                - url: Vector database endpoint URL
                - api_key: Authentication API key (optional)
                - timeout: Connection timeout in seconds
                - pool_size: Connection pool size
                - collection_name: Default collection/index name

        Raises:
            HandlerInitializationError: If connection cannot be established
                or configuration is invalid.

        Example:
            ```python
            from omnibase_core.models.vector import ModelVectorConnectionConfig

            config = ModelVectorConnectionConfig(
                url="http://localhost:6333",
                api_key="secret-key",
                timeout=30.0,
            )
            await handler.initialize(config)
            ```
        """
        ...

    async def shutdown(self, timeout_seconds: float = 30.0) -> None:
        """
        Release resources and close connections to the vector store.

        Flushes any pending operations and releases all resources gracefully.
        After shutdown, the handler cannot be used until initialize() is
        called again.

        Args:
            timeout_seconds: Maximum time to wait for shutdown to complete.
                Defaults to 30.0 seconds.

        Raises:
            TimeoutError: If shutdown does not complete within the timeout.

        Example:
            ```python
            await handler.shutdown(timeout_seconds=10.0)
            ```
        """
        ...

    async def store_embedding(
        self,
        embedding_id: str,
        vector: list[float],
        metadata: Mapping[str, JsonType] | None = None,
        index_name: str | None = None,
    ) -> ModelVectorStoreResult:
        """
        Store a single embedding vector with optional metadata.

        Args:
            embedding_id: Unique identifier for the embedding.
            vector: The embedding vector as a list of floats.
            metadata: Optional metadata mapping to store with the embedding.
                Can include text content, source references, timestamps, etc.
                Must be JSON-serializable (JsonValue type enforces this).
            index_name: Name of the index/collection to store in.
                Uses default index if not specified.

        Dynamic Payload Policy:
            The metadata field is opaque user/backend-defined payload.
            Core logic MUST NOT depend on specific keys.
            Adapters MAY validate and normalize for backend requirements.
            Payloads MUST be JSON-serializable (JsonValue type enforces this).

        Metadata Constraints:
            Recommended max keys: 100 (CONTEXT_MAX_KEYS)
            Recommended max nesting depth: 5 (CONTEXT_MAX_NESTING_DEPTH)
            Note: Enforcement is in adapters, not protocol.

        Returns:
            ModelVectorStoreResult containing operation result with fields:
                - success: Boolean indicating success
                - embedding_id: The stored embedding ID
                - index_name: The index where stored
                - timestamp: ISO format timestamp of operation

        Raises:
            ProtocolHandlerError: If storage operation fails, including
                dimension mismatch errors.
            InvalidProtocolStateError: If called before initialize().

        Dimension Validation:
            The vector dimension MUST match the dimension of the target index.
            For example, if the index was created with dimension=1536, all stored
            vectors must have exactly 1536 elements.

            Implementations SHOULD validate dimensions before storage and raise
            ProtocolHandlerError with a descriptive message if dimensions do not
            match. Common embedding dimensions:
                - OpenAI text-embedding-ada-002: 1536
                - OpenAI text-embedding-3-small: 1536
                - OpenAI text-embedding-3-large: 3072
                - Cohere embed-english-v3.0: 1024
                - Sentence Transformers (varies): 384-1024

        Example:
            ```python
            result = await handler.store_embedding(
                embedding_id="doc_001",
                vector=[0.1, 0.2, 0.3, ...],  # 1536-dim for OpenAI embeddings
                metadata={"source": "document.pdf", "page": 1},
                index_name="documents",
            )
            ```
        """
        ...

    async def store_embeddings_batch(
        self,
        embeddings: list[ModelEmbedding],
        index_name: str | None = None,
        batch_size: int = 100,
    ) -> ModelVectorBatchStoreResult:
        """
        Store multiple embeddings efficiently in a batch operation.

        Optimized for bulk insertion of embeddings. Implementations should
        handle batching internally for optimal throughput.

        Args:
            embeddings: List of ModelEmbedding instances, each containing:
                - id: Unique embedding identifier (str)
                - vector: Embedding vector (list[float])
                - metadata: Optional metadata (Mapping[str, JsonValue])
            index_name: Name of the index/collection to store in.
                Uses default index if not specified.
            batch_size: Number of embeddings to process per batch.
                Defaults to 100. Larger batches improve throughput
                but increase memory usage.

        Dynamic Payload Policy:
            The metadata in each ModelEmbedding is opaque user/backend-defined payload.
            Core logic MUST NOT depend on specific keys.
            Adapters MAY validate and normalize for backend requirements.
            Payloads MUST be JSON-serializable (JsonValue type enforces this).

        Returns:
            ModelVectorBatchStoreResult containing batch operation result with fields:
                - success: Boolean indicating overall success
                - total_stored: Number of embeddings stored
                - failed_ids: List of IDs that failed to store
                - execution_time_ms: Total execution time in milliseconds

        Raises:
            ProtocolHandlerError: If batch operation fails.
            InvalidProtocolStateError: If called before initialize().

        Backend-Specific Batch Size Guidance:
            Optimal batch sizes vary significantly by vector database backend.
            Using inappropriate batch sizes can cause performance degradation,
            timeouts, or memory issues. Recommended ranges:

                - Qdrant: 100-1000 vectors per batch (default 100 is good)
                - Pinecone: 100 vectors max per upsert request (hard limit)
                - Weaviate: 100-500 vectors per batch
                - Milvus: 100-1000 vectors per batch
                - Chroma: 100-500 vectors per batch

            Consult your backend's documentation for the most current guidance.
            Consider these factors when choosing batch size:
                - Memory usage: Each batch is held in memory during processing
                - Network overhead: Smaller batches have more round-trip overhead
                - Timeout risk: Larger batches take longer and may timeout
                - Error recovery: Smaller batches limit blast radius on failures

            Implementations SHOULD respect backend-specific limits and may
            internally split batches that exceed optimal sizes.

        Example:
            ```python
            from omnibase_core.models.vector import ModelEmbedding

            embeddings = [
                ModelEmbedding(id="doc_001", vector=[...], metadata={"page": 1}),
                ModelEmbedding(id="doc_002", vector=[...], metadata={"page": 2}),
            ]
            result = await handler.store_embeddings_batch(
                embeddings=embeddings,
                index_name="documents",
                batch_size=50,
            )
            print(f"Stored {result.total_stored} embeddings")
            ```
        """
        ...

    async def query_similar(
        self,
        query_vector: list[float],
        top_k: int = 10,
        index_name: str | None = None,
        filter_metadata: ModelVectorMetadataFilter | None = None,
        include_metadata: bool = True,
        include_vectors: bool = False,
        score_threshold: float | None = None,
    ) -> ModelVectorSearchResults:
        """
        Find similar vectors using similarity/distance search.

        Performs approximate nearest neighbor (ANN) search to find vectors
        most similar to the query vector. Results are ordered by similarity
        score (descending for similarity metrics, ascending for distance).

        Args:
            query_vector: The query embedding vector to search against.
            top_k: Maximum number of results to return. Defaults to 10.
            index_name: Name of the index/collection to search.
                Uses default index if not specified.
            filter_metadata: Optional ModelVectorMetadataFilter to restrict search.
                See ModelVectorMetadataFilter for filter operators and syntax.
            include_metadata: Whether to include metadata in results.
                Defaults to True.
            include_vectors: Whether to include vectors in results.
                Defaults to False (saves bandwidth).
            score_threshold: Minimum similarity score threshold.
                Results below this threshold are excluded.

        Returns:
            ModelVectorSearchResults containing search results with fields:
                - results: List of ModelVectorSearchResult, each containing:
                    - id: Embedding ID
                    - score: Similarity/distance score
                    - metadata: Metadata dict (if include_metadata=True)
                    - vector: Vector (if include_vectors=True)
                - total_results: Number of results returned
                - query_time_ms: Search execution time in milliseconds

        Raises:
            ProtocolHandlerError: If search operation fails.
            InvalidProtocolStateError: If called before initialize().

        Example:
            ```python
            from omnibase_core.models.vector import ModelVectorMetadataFilter

            filter_config = ModelVectorMetadataFilter(
                field="category",
                operator="eq",
                value="technical",
            )
            results = await handler.query_similar(
                query_vector=query_embedding,
                top_k=5,
                index_name="documents",
                filter_metadata=filter_config,
                score_threshold=0.7,
            )
            for result in results.results:
                print(f"ID: {result.id}, Score: {result.score}")
            ```
        """
        ...

    async def delete_embedding(
        self,
        embedding_id: str,
        index_name: str | None = None,
    ) -> ModelVectorDeleteResult:
        """
        Remove a single embedding by ID.

        Args:
            embedding_id: Unique identifier of the embedding to delete.
            index_name: Name of the index/collection containing the embedding.
                Uses default index if not specified.

        Returns:
            ModelVectorDeleteResult containing deletion result with fields:
                - success: Boolean indicating success
                - embedding_id: The deleted embedding ID
                - deleted: Boolean indicating if embedding existed and was deleted

        Raises:
            ProtocolHandlerError: If deletion operation fails.
            InvalidProtocolStateError: If called before initialize().

        Example:
            ```python
            result = await handler.delete_embedding(
                embedding_id="doc_001",
                index_name="documents",
            )
            if result.deleted:
                print("Embedding removed successfully")
            ```
        """
        ...

    async def delete_embeddings_batch(
        self,
        embedding_ids: list[str],
        index_name: str | None = None,
    ) -> ModelVectorDeleteResult:
        """
        Remove multiple embeddings by their IDs.

        Optimized for bulk deletion operations. Implementations should
        handle batching internally for optimal performance.

        Args:
            embedding_ids: List of embedding IDs to delete.
            index_name: Name of the index/collection containing the embeddings.
                Uses default index if not specified.

        Returns:
            ModelVectorDeleteResult containing batch deletion result with fields:
                - success: Boolean indicating overall success
                - total_deleted: Number of embeddings deleted
                - failed_ids: List of IDs that failed to delete
                - not_found_ids: List of IDs that were not found

        Raises:
            ProtocolHandlerError: If batch deletion fails.
            InvalidProtocolStateError: If called before initialize().

        Example:
            ```python
            result = await handler.delete_embeddings_batch(
                embedding_ids=["doc_001", "doc_002", "doc_003"],
                index_name="documents",
            )
            print(f"Deleted {result.total_deleted} embeddings")
            ```
        """
        ...

    async def create_index(
        self,
        index_name: str,
        dimension: int,
        metric: str = "cosine",
        index_config: ModelVectorIndexConfig | None = None,
    ) -> ModelVectorIndexResult:
        """
        Create a new vector index/collection.

        Creates a new index with the specified vector dimension and
        distance metric. Index configuration varies by implementation.

        Args:
            index_name: Unique name for the new index.
            dimension: Vector dimension (e.g., 1536 for OpenAI embeddings).
            metric: Distance metric to use. Must be in supported_metrics.
                Defaults to "cosine".
            index_config: Optional ModelVectorIndexConfig with settings:
                - shards: Number of shards for distributed storage
                - replicas: Number of replicas for redundancy
                - on_disk: Whether to store vectors on disk
                - quantization: ModelQuantizationConfig for compression
                - hnsw_config: ModelHnswConfig for HNSW parameters

        Returns:
            ModelVectorIndexResult containing creation result with fields:
                - success: Boolean indicating success
                - index_name: The created index name
                - dimension: Vector dimension
                - metric: Distance metric used
                - created_at: ISO format creation timestamp

        Raises:
            ProtocolHandlerError: If index creation fails or index exists.
            InvalidProtocolStateError: If called before initialize().
            ValueError: If metric is not in supported_metrics.

        Example:
            ```python
            from omnibase_core.models.vector import ModelVectorIndexConfig

            config = ModelVectorIndexConfig(on_disk=True)
            result = await handler.create_index(
                index_name="documents",
                dimension=1536,
                metric="cosine",
                index_config=config,
            )
            ```
        """
        ...

    async def delete_index(
        self,
        index_name: str,
    ) -> ModelVectorIndexResult:
        """
        Delete a vector index/collection.

        Permanently removes the index and all its embeddings.
        This operation cannot be undone.

        Args:
            index_name: Name of the index to delete.

        Returns:
            ModelVectorIndexResult containing deletion result with fields:
                - success: Boolean indicating success
                - index_name: The deleted index name
                - deleted: Boolean indicating if index existed and was deleted

        Raises:
            ProtocolHandlerError: If deletion fails.
            InvalidProtocolStateError: If called before initialize().

        Example:
            ```python
            result = await handler.delete_index(index_name="old_documents")
            if result.deleted:
                print("Index removed successfully")
            ```

        Warning:
            This operation permanently deletes all embeddings in the index.
            Ensure you have backups before deleting production indices.
        """
        ...

    async def health_check(self) -> ModelVectorHealthStatus:
        """
        Check handler health and connectivity to the vector store.

        Performs a lightweight check to verify the handler is operational
        and can communicate with its backing vector database.

        Returns:
            ModelVectorHealthStatus containing health status with fields:
                - healthy: Boolean indicating overall health
                - latency_ms: Response time in milliseconds
                - details: Additional diagnostic information
                - indices: List of available indices (optional)
                - last_error: Most recent error message if unhealthy

        Example:
            ```python
            health = await handler.health_check()
            if health.healthy:
                print(f"Vector store OK, latency: {health.latency_ms}ms")
            else:
                print(f"Unhealthy: {health.last_error or 'Unknown error'}")
            ```

        Caching:
            Implementations SHOULD cache health check results for 5-30 seconds
            to avoid overwhelming the backend service with repeated probes.
            The caching TTL should balance freshness requirements against
            backend load. For high-availability scenarios, 5-10 seconds is
            recommended; for lower-traffic systems, 15-30 seconds is acceptable.

        Rate Limiting:
            Implementations SHOULD protect against DoS through excessive health
            check calls by tracking call frequency. Consider implementing:
                - Token bucket or sliding window rate limiting
                - Per-client rate limits if caller identity is available
                - Exponential backoff responses when limits are exceeded
                - Logging of rate limit violations for security monitoring

            A reasonable default is to allow no more than 12 health checks per
            minute (one every 5 seconds) per handler instance.

        Security:
            Error messages should be sanitized to avoid exposing credentials
            or internal system details.

        Raises:
            InvalidProtocolStateError: If called before initialize().
        """
        ...

    async def describe(self) -> ModelVectorHandlerMetadata:
        """
        Return handler metadata and capabilities.

        Provides introspection information about the handler including
        its type, supported operations, connection status, and
        vector-specific capabilities.

        .. versionchanged:: 0.5.0
            This method changed from synchronous to asynchronous.

        Breaking Change (v0.5.0):
            The ``describe()`` method is now async. Callers must update their code:

            Before (v0.4.x)::

                metadata = handler.describe()

            After (v0.5.0+)::

                metadata = await handler.describe()

        Note:
            This method is async because implementations may need to check
            connection status, query backend capabilities, or perform other
            I/O operations to provide accurate metadata.

        Returns:
            ModelVectorHandlerMetadata containing handler metadata with fields:
                - handler_type: "vector_store"
                - capabilities: List of supported operations
                - supported_metrics: List of distance metrics
                - max_dimension: Maximum vector dimension supported
                - max_batch_size: Maximum batch size for bulk operations
                - version: Handler implementation version

        Example:
            ```python
            metadata = await handler.describe()
            print(f"Metrics: {metadata.supported_metrics}")
            print(f"Max dimension: {metadata.max_dimension or 'unlimited'}")
            ```

        Security:
            NEVER include credentials, API keys, or connection strings
            in the returned metadata.

        Raises:
            InvalidProtocolStateError: If called before initialize().
        """
        ...
