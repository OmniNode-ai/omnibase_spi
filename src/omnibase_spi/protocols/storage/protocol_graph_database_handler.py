"""
Graph Database Handler Protocol - ONEX SPI Interface.

Protocol definition for graph database operations. This is a specialized handler
protocol that extends the ProtocolHandler pattern for backend-agnostic graph
database operations (supports Neo4j, Amazon Neptune, TigerGraph, and other
graph databases).

The graph database handler provides:
    - Cypher/Gremlin/GSQL query execution with parameterization
    - Node and relationship CRUD operations
    - Graph traversal with configurable depth and filters
    - Transaction support for atomic multi-query operations
    - Connection pooling and resource management
    - Health monitoring and introspection

Key Protocols:
    - ProtocolGraphDatabaseHandler: Graph database handler interface

Core Models:
    This protocol uses typed models from ``omnibase_core.models.graph``:
        - ModelGraphQueryResult: Query execution results with records and counters
        - ModelGraphDatabaseNode: Node with labels, properties, and identifiers
        - ModelGraphRelationship: Relationship with type and connected nodes
        - ModelGraphTraversalResult: Traversal results with paths and discovered nodes
        - ModelGraphBatchResult: Batch query execution results
        - ModelGraphDeleteResult: Deletion operation results
        - ModelGraphHealthStatus: Health check return type
        - ModelGraphHandlerMetadata: Handler introspection metadata
        - ModelGraphTraversalFilters: Filters for traversal operations

Handler Lifecycle:
    1. Create handler instance
    2. Call initialize() with connection URI and credentials
    3. Execute operations (queries, node/relationship management, traversals)
    4. Call shutdown() to release resources

Example:
    ```python
    from omnibase_spi.protocols.storage import ProtocolGraphDatabaseHandler
    from omnibase_core.models.graph import ModelGraphQueryResult

    # Get handler from dependency injection
    handler: ProtocolGraphDatabaseHandler = get_graph_handler()

    # Initialize connection
    await handler.initialize(
        connection_uri="bolt://localhost:7687",
        auth=("neo4j", "password"),
        options={"max_connection_pool_size": 50},
    )

    # Execute parameterized query (safe from injection)
    result = await handler.execute_query(
        query="MATCH (n:Person {name: $name}) RETURN n",
        parameters={"name": "Alice"},
    )
    for record in result.records:
        print(record)

    # Create nodes and relationships
    alice = await handler.create_node(
        labels=["Person"],
        properties={"name": "Alice", "age": 30},
    )
    bob = await handler.create_node(
        labels=["Person"],
        properties={"name": "Bob", "age": 25},
    )
    await handler.create_relationship(
        from_node_id=alice.id,
        to_node_id=bob.id,
        relationship_type="KNOWS",
        properties={"since": "2023-01-15"},
    )

    # Traverse the graph
    result = await handler.traverse(
        start_node_id=alice.id,
        relationship_types=["KNOWS"],
        direction="outgoing",
        max_depth=2,
    )
    print(f"Found {len(result.nodes)} connected nodes")

    # Health check with typed response
    health = await handler.health_check()
    if health.healthy:
        print(f"Database OK, latency: {health.latency_ms}ms")

    # Cleanup
    await handler.shutdown()
    ```

See Also:
    - ProtocolHandler: Base handler protocol pattern
    - ProtocolVectorStoreHandler: Vector store handler for embeddings
    - ProtocolStorageBackend: General checkpoint/state persistence
    - ModelGraphQueryResult: Core model for query results
    - ModelGraphDatabaseNode: Core model for graph nodes
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    # Graph database models from omnibase_core.models.graph (PR #250, OMN-1053)
    # These models replace dict[str, Any] for type-safe graph database operations.
    # Available in omnibase_core >= 0.5.6
    from omnibase_core.models.graph import (
        ModelGraphBatchResult,
        ModelGraphDatabaseNode,
        ModelGraphDeleteResult,
        ModelGraphHandlerMetadata,
        ModelGraphHealthStatus,
        ModelGraphQueryResult,
        ModelGraphRelationship,
        ModelGraphTraversalFilters,
        ModelGraphTraversalResult,
    )
    from omnibase_core.types import JsonType


@runtime_checkable
class ProtocolGraphDatabaseHandler(Protocol):
    """
    Protocol for graph database handler implementations.

    Defines the interface for graph database operations including Cypher query
    execution, node and relationship management, graph traversal, and transaction
    support. Implementations can support various graph databases like Neo4j,
    Amazon Neptune, or TigerGraph.

    This protocol extends the general ProtocolHandler pattern with graph-specific
    operations while maintaining consistency with the handler lifecycle pattern
    (initialize -> execute operations -> shutdown).

    Handler vs Event Bus Distinction:
        ProtocolGraphDatabaseHandler is for request-response graph operations
        where a direct response is expected (query results, created nodes, etc.).
        This differs from event bus patterns which handle asynchronous messaging.

    Example implementations:
        - Neo4jHandler: Neo4j via Bolt protocol with Cypher queries
        - NeptuneHandler: Amazon Neptune with Gremlin/SPARQL
        - TigerGraphHandler: TigerGraph with GSQL

    Example:
        ```python
        from collections.abc import Mapping
        from omnibase_core.models.graph import ModelGraphQueryResult
        from omnibase_core.types import JsonType

        class Neo4jHandler:
            '''Neo4j graph database handler implementation.'''

            @property
            def handler_type(self) -> str:
                return "graph_database"

            @property
            def supports_transactions(self) -> bool:
                return True

            async def execute_query(
                self,
                query: str,
                parameters: Mapping[str, JsonType] | None = None,
            ) -> ModelGraphQueryResult:
                # Execute Cypher query via Bolt protocol
                async with self._driver.session() as session:
                    result = await session.run(query, dict(parameters) if parameters else {})
                    records = [dict(r) for r in await result.data()]
                    return ModelGraphQueryResult(records=records)

        handler = Neo4jHandler()
        assert isinstance(handler, ProtocolGraphDatabaseHandler)
        ```

    See Also:
        - ProtocolHandler: Base handler protocol pattern
        - ProtocolVectorStoreHandler: Vector store handler for embedding operations
        - ModelGraphQueryResult: Result model for query operations
        - ModelGraphDatabaseNode: Node model with labels and properties
        - ModelGraphRelationship: Relationship model with type and endpoints
    """

    @property
    def handler_type(self) -> str:
        """
        The type of handler as a string identifier.

        Used for handler identification, routing, and metrics collection.
        Implementations should return "graph_database" as the handler type.

        Note:
            The return type is ``str`` (not an enum) by design to maintain
            SPI/Core decoupling. Implementations may use the string directly
            or derive it from an enum value.

        Returns:
            String identifier "graph_database" for this handler type.
        """
        ...

    @property
    def supports_transactions(self) -> bool:
        """
        Whether this handler supports transactional operations.

        When True, the handler can execute multiple operations atomically
        via execute_query_batch() with transaction semantics (all-or-nothing).
        When False, batch operations are executed individually without
        transaction guarantees.

        Returns:
            True if the handler supports transactions, False otherwise.
        """
        ...

    async def initialize(
        self,
        connection_uri: str,
        auth: tuple[str, str] | None = None,
        *,
        options: Mapping[str, JsonType] | None = None,
    ) -> None:
        """
        Initialize the graph database connection.

        Establishes connection to the graph database using the provided URI
        and authentication credentials. Should configure connection pools,
        validate connectivity, and prepare the handler for operation.

        Args:
            connection_uri: Database connection URI (e.g., "bolt://localhost:7687"
                for Neo4j, "wss://neptune-endpoint:8182" for Neptune).
            auth: Optional tuple of (username, password) for authentication.
                If None, attempts connection without authentication.
            options: Additional connection parameters as JSON-serializable mapping.
                Common options include:
                - max_connection_pool_size: Maximum connections in pool
                - connection_timeout: Timeout in seconds for connections
                - encrypted: Whether to use TLS/SSL encryption
                - trust: Certificate trust strategy

                NOTE: Dynamic payload policy
                - This field is opaque backend-defined configuration
                - Core logic MUST NOT depend on specific keys
                - Adapters MAY validate and normalize for backend requirements
                - Payloads MUST be JSON-serializable (JsonType type enforces this)
                - Recommended constraints: max_keys=100, max_depth=5

        Raises:
            HandlerInitializationError: If connection cannot be established,
                authentication fails, or configuration is invalid.

        Example:
            ```python
            await handler.initialize(
                connection_uri="bolt://localhost:7687",
                auth=("neo4j", "password"),
                options={
                    "max_connection_pool_size": 50,
                    "encrypted": True,
                },
            )
            ```
        """
        ...

    async def shutdown(self, timeout_seconds: float = 30.0) -> None:
        """
        Close database connections and release resources.

        Gracefully shuts down the handler by closing all active connections,
        draining connection pools, and releasing resources. Should wait for
        pending operations to complete within the timeout.

        Args:
            timeout_seconds: Maximum time to wait for shutdown to complete.
                Defaults to 30.0 seconds.

        Raises:
            TimeoutError: If shutdown does not complete within the specified
                timeout period.
        """
        ...

    async def execute_query(
        self,
        query: str,
        parameters: Mapping[str, JsonType] | None = None,
    ) -> ModelGraphQueryResult:
        """
        Execute a Cypher or graph query language query.

        Executes a single query against the graph database and returns
        the results. Supports parameterized queries for security and
        performance.

        Security:
            **WARNING: QUERY INJECTION RISK**

            Never construct queries by string concatenation or f-string
            interpolation with user-provided input. Doing so exposes your
            application to query injection attacks, which can lead to:

            - Unauthorized data access or exfiltration
            - Data modification or deletion
            - Privilege escalation
            - Denial of service

            **UNSAFE** (vulnerable to injection)::

                # DO NOT DO THIS - user_input could contain malicious Cypher
                user_input = "Alice' OR 1=1 WITH n MATCH (m) DETACH DELETE m //"
                query = f"MATCH (n:User {{name: '{user_input}'}}) RETURN n"
                await handler.execute_query(query)  # DANGEROUS!

            **SAFE** (parameterized query)::

                # ALWAYS use parameterized queries
                query = "MATCH (n:User {name: $name}) RETURN n"
                parameters = {"name": user_input}  # Safe - properly escaped
                await handler.execute_query(query, parameters)

            Implementations MUST properly escape parameter values according
            to their graph database's parameterization mechanism.

        Args:
            query: The graph query string (Cypher for Neo4j, Gremlin for
                Neptune, GSQL for TigerGraph, etc.).
            parameters: Optional mapping of query parameters for
                parameterized queries. Keys are parameter names, values
                are JSON-serializable parameter values. **Always use this
                for user input.**

                NOTE: Dynamic payload policy
                - This field contains user-provided query parameters
                - Core logic MUST NOT depend on specific keys
                - Adapters MAY validate and normalize for backend requirements
                - Payloads MUST be JSON-serializable (JsonType type enforces this)

        Returns:
            ModelGraphQueryResult containing:
                - records: List of result records
                - summary: Query execution summary (ModelGraphQuerySummary)
                - counters: Statistics about nodes/relationships affected
                  (ModelGraphQueryCounters)
                - execution_time_ms: Query execution time in milliseconds

        Raises:
            ProtocolHandlerError: If query execution fails due to syntax
                errors, constraint violations, or connection issues.

        Example:
            ```python
            result = await handler.execute_query(
                query="MATCH (n:Person {name: $name}) RETURN n",
                parameters={"name": "Alice"},
            )
            for record in result.records:
                print(record)
            ```
        """
        ...

    async def execute_query_batch(
        self,
        queries: list[tuple[str, Mapping[str, JsonType] | None]],
        transaction: bool = True,
    ) -> ModelGraphBatchResult:
        """
        Execute multiple queries, optionally within a transaction.

        Executes a batch of queries either atomically within a transaction
        (if transaction=True and supports_transactions=True) or individually.
        Provides efficient bulk operations and atomic multi-query execution.

        Args:
            queries: List of (query, parameters) tuples to execute.
                Each tuple contains the query string and optional parameters
                as a JSON-serializable mapping.

                NOTE: Dynamic payload policy (for parameters)
                - Parameters contain user-provided query values
                - Core logic MUST NOT depend on specific keys
                - Adapters MAY validate and normalize for backend requirements
                - Payloads MUST be JSON-serializable (JsonType type enforces this)

            transaction: If True and handler supports transactions, execute
                all queries within a single transaction. If any query fails,
                all changes are rolled back. Defaults to True.

        Returns:
            ModelGraphBatchResult containing:
                - results: List of individual ModelGraphQueryResult objects
                - success: Overall success status
                - transaction_id: Transaction identifier (if transactional)
                - rollback_occurred: Whether rollback was triggered
                - execution_time_ms: Total batch execution time

        Raises:
            ProtocolHandlerError: If any query fails. In transactional mode,
                all changes are rolled back before raising the exception.

        Example:
            ```python
            result = await handler.execute_query_batch(
                queries=[
                    ("CREATE (a:Person {name: $name})", {"name": "Alice"}),
                    ("CREATE (b:Person {name: $name})", {"name": "Bob"}),
                    ("MATCH (a:Person {name: 'Alice'}), (b:Person {name: 'Bob'}) "
                     "CREATE (a)-[:KNOWS]->(b)", None),
                ],
                transaction=True,
            )
            ```
        """
        ...

    async def create_node(
        self,
        labels: list[str],
        properties: Mapping[str, JsonType],
    ) -> ModelGraphDatabaseNode:
        """
        Create a new node in the graph.

        Creates a node with the specified labels and properties. Returns
        the created node including its database-assigned identifier.

        Args:
            labels: List of labels to assign to the node (e.g., ["Person"],
                ["User", "Admin"]). At least one label is recommended.
            properties: Mapping of property key-value pairs for the node.
                Values must be JSON-serializable (strings, numbers, booleans,
                lists, nested objects).

                NOTE: Dynamic payload policy
                - This field contains user-defined node properties
                - Core logic MUST NOT depend on specific keys
                - Adapters MAY validate and normalize for backend requirements
                - Payloads MUST be JSON-serializable (JsonType type enforces this)
                - Recommended constraints: max_keys=100, max_depth=5

        Returns:
            ModelGraphDatabaseNode containing:
                - id: Database-assigned node identifier (internal ID)
                - element_id: Unique element identifier (Neo4j 5.x+)
                - labels: List of node labels
                - properties: Node properties as stored
                - execution_time_ms: Operation execution time

        Raises:
            ProtocolHandlerError: If node creation fails due to constraint
                violations, invalid property types, or connection issues.

        Example:
            ```python
            node = await handler.create_node(
                labels=["Person", "Employee"],
                properties={
                    "name": "Alice",
                    "email": "alice@example.com",
                    "age": 30,
                },
            )
            print(f"Created node with ID: {node.id}")
            ```
        """
        ...

    async def create_relationship(
        self,
        from_node_id: str | int,
        to_node_id: str | int,
        relationship_type: str,
        properties: Mapping[str, JsonType] | None = None,
    ) -> ModelGraphRelationship:
        """
        Create a relationship between two nodes.

        Creates a directed relationship from one node to another with
        the specified type and optional properties.

        Args:
            from_node_id: Identifier of the source node (start of relationship).
                Can be internal ID (int) or element ID (str) depending on
                the graph database.
            to_node_id: Identifier of the target node (end of relationship).
                Can be internal ID (int) or element ID (str).
            relationship_type: Type of the relationship (e.g., "KNOWS",
                "WORKS_FOR", "PURCHASED"). Should be uppercase by convention.
            properties: Optional mapping of property key-value pairs for
                the relationship. Must be JSON-serializable.

                NOTE: Dynamic payload policy
                - This field contains user-defined relationship properties
                - Core logic MUST NOT depend on specific keys
                - Adapters MAY validate and normalize for backend requirements
                - Payloads MUST be JSON-serializable (JsonType type enforces this)
                - Recommended constraints: max_keys=100, max_depth=5

        Returns:
            ModelGraphRelationship containing:
                - id: Database-assigned relationship identifier
                - element_id: Unique element identifier (Neo4j 5.x+)
                - relationship_type: Relationship type as stored
                - properties: Relationship properties as stored
                - start_node_id: Source node identifier
                - end_node_id: Target node identifier
                - execution_time_ms: Operation execution time

        Raises:
            ProtocolHandlerError: If relationship creation fails due to
                non-existent nodes, constraint violations, or connection issues.

        Example:
            ```python
            relationship = await handler.create_relationship(
                from_node_id=alice_node.id,
                to_node_id=bob_node.id,
                relationship_type="KNOWS",
                properties={"since": "2023-01-15", "closeness": 0.8},
            )
            ```
        """
        ...

    async def delete_node(
        self,
        node_id: str | int,
        detach: bool = False,
    ) -> ModelGraphDeleteResult:
        """
        Delete a node from the graph.

        Removes a node by its identifier. If detach=True, also removes
        all relationships connected to the node. If detach=False and the
        node has relationships, the operation will fail.

        Args:
            node_id: Identifier of the node to delete. Can be internal ID
                (int) or element ID (str) depending on the graph database.
            detach: If True, delete all relationships connected to the node
                before deleting the node (DETACH DELETE). If False, fail if
                the node has any relationships. Defaults to False.

        Returns:
            ModelGraphDeleteResult containing:
                - success: Whether the deletion succeeded
                - entity_id: Identifier of the deleted node
                - relationships_deleted: Number of relationships removed
                    (only if detach=True)
                - execution_time_ms: Operation execution time

        Raises:
            ProtocolHandlerError: If deletion fails due to non-existent node,
                existing relationships (when detach=False), or connection issues.

        Example:
            ```python
            # Delete node and its relationships
            result = await handler.delete_node(
                node_id=node.id,
                detach=True,
            )
            print(f"Deleted node, removed {result.relationships_deleted} relationships")
            ```
        """
        ...

    async def delete_relationship(
        self,
        relationship_id: str | int,
    ) -> ModelGraphDeleteResult:
        """
        Delete a relationship from the graph.

        Removes a relationship by its identifier. Does not affect the
        connected nodes.

        Args:
            relationship_id: Identifier of the relationship to delete.
                Can be internal ID (int) or element ID (str) depending on
                the graph database.

        Returns:
            ModelGraphDeleteResult containing:
                - success: Whether the deletion succeeded
                - entity_id: Identifier of the deleted relationship
                - execution_time_ms: Operation execution time

        Raises:
            ProtocolHandlerError: If deletion fails due to non-existent
                relationship or connection issues.

        Example:
            ```python
            result = await handler.delete_relationship(
                relationship_id=relationship.id,
            )
            if result.success:
                print("Relationship deleted successfully")
            ```
        """
        ...

    async def traverse(
        self,
        start_node_id: str | int,
        relationship_types: list[str] | None = None,
        direction: str = "outgoing",
        max_depth: int = 1,
        filters: ModelGraphTraversalFilters | None = None,
    ) -> ModelGraphTraversalResult:
        """
        Traverse the graph from a starting node.

        Performs a graph traversal starting from the specified node,
        following relationships according to the specified criteria.
        Returns the discovered nodes and relationships.

        Args:
            start_node_id: Identifier of the node to start traversal from.
            relationship_types: Optional list of relationship types to follow.
                If None, follows all relationship types.
            direction: Direction to traverse. One of:
                - "outgoing": Follow outgoing relationships only (default)
                - "incoming": Follow incoming relationships only
                - "both": Follow relationships in both directions
            max_depth: Maximum traversal depth (number of hops from start).
                Defaults to 1. Use with caution for large graphs.
            filters: Optional ModelGraphTraversalFilters to apply during traversal,
                containing:
                - node_labels: List of labels nodes must have
                - node_properties: Property conditions for nodes
                - relationship_properties: Property conditions for relationships

        Returns:
            ModelGraphTraversalResult containing:
                - nodes: List of discovered ModelGraphDatabaseNode objects
                - relationships: List of traversed ModelGraphRelationship objects
                - paths: List of paths from start node to each discovered node
                - depth_reached: Actual maximum depth reached
                - execution_time_ms: Traversal execution time

        Raises:
            ProtocolHandlerError: If traversal fails due to non-existent
                start node, invalid parameters, or connection issues.

        Example:
            ```python
            from omnibase_core.models.graph import ModelGraphTraversalFilters

            filters = ModelGraphTraversalFilters(node_labels=["Person"])
            result = await handler.traverse(
                start_node_id=alice_node.id,
                relationship_types=["KNOWS", "WORKS_WITH"],
                direction="both",
                max_depth=2,
                filters=filters,
            )
            print(f"Found {len(result.nodes)} connected people")
            for path in result.paths:
                print(f"Path: {' -> '.join(str(n) for n in path)}")
            ```
        """
        ...

    async def health_check(self) -> ModelGraphHealthStatus:
        """
        Check handler health and database connectivity.

        Performs a lightweight check to verify the handler is operational
        and can communicate with the graph database. Should return quickly
        and not perform heavy operations.

        Returns:
            ModelGraphHealthStatus containing:
                - healthy: Boolean indicating overall health
                - latency_ms: Response time in milliseconds
                - database_version: Graph database version (if available)
                - connection_count: Active connections in pool
                - details: Additional diagnostic information
                - last_error: Most recent error message if unhealthy
                - cached: Boolean indicating if result was from cache (optional)

        Caching:
            Implementations SHOULD cache health check results for 5-30 seconds
            to avoid overwhelming the backend with repeated health probes.
            The cache duration should be configurable and may vary based on:

            - Production environments: 10-30 seconds (stability over freshness)
            - Development environments: 5-10 seconds (faster feedback)
            - High-availability setups: 5-15 seconds (balance)

            When returning cached results, implementations SHOULD set the
            ``cached`` field to True to indicate staleness.

        Rate Limiting:
            Implementations SHOULD protect against denial-of-service through
            excessive health check calls by:

            - Tracking call frequency per client/source when possible
            - Returning cached results for rapid repeated calls (e.g., >1 call/second)
            - Implementing exponential backoff for cache refresh under load
            - Optionally returning HTTP 429 (Too Many Requests) equivalent errors
              for egregiously abusive patterns

            Example rate limiting strategy::

                # Return cached result if called within last N seconds
                if time.time() - self._last_health_check < self._min_interval:
                    return self._cached_health.model_copy(update={"cached": True})

        Security:
            Error messages SHOULD be sanitized to avoid exposing credentials,
            internal paths, or other sensitive information.

        Raises:
            HandlerNotInitializedError: If called before initialize().

        Example:
            ```python
            health = await handler.health_check()
            if health.healthy:
                print(f"Database OK, latency: {health.latency_ms}ms")
                print(f"Version: {health.database_version}")
                if health.cached:
                    print("(cached result)")
            else:
                print(f"Unhealthy: {health.last_error or 'Unknown error'}")
            ```
        """
        ...

    async def describe(self) -> ModelGraphHandlerMetadata:
        """
        Return handler metadata and capabilities.

        Provides introspection information about the handler including
        its type, supported operations, connection status, and any
        handler-specific capabilities.

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
            connection status, query database version, or perform other I/O
            operations to populate accurate metadata.

        Returns:
            ModelGraphHandlerMetadata containing:
                - handler_type: "graph_database"
                - capabilities: List of supported operations/features
                - database_type: Specific graph database type (neo4j, neptune, etc.)
                - version: Handler implementation version (optional)
                - supports_transactions: Whether transactions are supported
                - connection_info: Non-sensitive connection details

        Security:
            NEVER include in output:
                - Credentials (passwords, API keys, tokens, secrets)
                - Full connection strings with authentication details
                - Internal file paths or system configuration details

        Raises:
            HandlerNotInitializedError: If called before initialize().

        Example:
            ```python
            metadata = await handler.describe()
            print(f"Handler: {metadata.handler_type}")
            print(f"Database: {metadata.database_type}")
            print(f"Capabilities: {metadata.capabilities}")
            ```
        """
        ...
