"""
Protocol for projection-backed state reading.

Defines the contract for reading materialized projection state used by orchestrators
to make decisions. This protocol enforces the critical architectural constraint that
orchestrators MUST NEVER scan topics directly for state - all orchestration decisions
must be projection-backed.

Projections are materialized views of event streams that provide consistent,
queryable state without requiring real-time event stream scanning. This enables:
- Fast point queries for entity state
- Domain-isolated queries with consistent views
- Registration-specific queries for node management
- Extensible criteria-based lookups for any domain

CRITICAL ARCHITECTURAL CONSTRAINT:
    Orchestrators MUST NEVER scan Kafka/event topics directly to determine state.
    Topic scanning introduces:
    - Race conditions with ongoing event processing
    - Inconsistent reads during projection rebuilds
    - Unbounded query latency for large topics
    - Coupling between orchestration and event infrastructure

    All orchestration decisions MUST use projection queries through this interface.

Example implementations:
    - PostgresProjectionReader: PostgreSQL-based projection queries
    - ValkeyProjectionReader: Valkey/Redis-based projection cache
    - InMemoryProjectionReader: In-memory projection for testing

Related tickets:
    - OMN-930: Define ProtocolProjectionReader for orchestrators
    - OMN-940: Projection infrastructure for event-driven orchestration
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_core.types import JsonType


@runtime_checkable
class ProtocolProjectionReader(Protocol):
    """
    Read-only interface for querying projection state.

    Orchestrators use this protocol to make decisions based on materialized views
    of event streams. This interface provides the ONLY sanctioned mechanism for
    orchestrators to query current state.

    CRITICAL CONSTRAINT:
        NEVER scan topics directly for state. All orchestration decisions
        MUST be projection-backed through this interface. Topic scanning
        leads to race conditions, inconsistent reads, and unbounded latency.

    Design Principles:
        - Read-only: This protocol only reads state; writes go through event sourcing
        - Domain-isolated: Queries are scoped to specific domains for isolation
        - Strongly typed: Entity IDs and criteria use well-defined types
        - Extensible: Criteria-based queries support any domain's needs

    Generic Query Methods:
        - get_entity_state(): Point lookup for a single entity's current state
        - exists(): Existence check without retrieving full state
        - get_by_criteria(): Flexible criteria-based lookups for complex queries

    Registration-Specific Methods:
        These methods provide specialized access for node registration workflows:
        - get_registration_status(): Check registration state of a node
        - get_registered_nodes(): List nodes matching registration criteria
        - get_node_capabilities(): Retrieve capability metadata for a node

    Thread Safety:
        Implementations MUST be thread-safe for concurrent read access.
        Multiple orchestrator instances may query projections simultaneously.

    Consistency Model:
        Projections provide eventual consistency with the event store.
        Implementations SHOULD document their consistency guarantees.
        Typical lag: <100ms for well-tuned implementations.

    Example usage:
        ```python
        # Check if a node is registered before routing work
        status = await reader.get_registration_status(
            node_id="node-uuid-here",
            domain="compute",
        )
        if status and status.get("state") == "active":
            # Route work to this node
            ...

        # Find all active compute nodes with specific capability
        criteria = {"state": "active", "capability": "gpu-inference"}
        nodes = await reader.get_by_criteria(
            criteria=criteria,
            domain="registration",
        )
        ```

    Migration:
        This protocol is introduced in v0.4.1 as part of the projection
        infrastructure for event-driven orchestration (B3). Future versions
        may add streaming queries and subscription-based updates.
    """

    async def get_entity_state(
        self,
        entity_id: str,
        domain: str,
    ) -> JsonType | None:
        """
        Get the current projected state of an entity.

        Retrieves the materialized state for a specific entity within a domain.
        This is the primary method for point lookups when an orchestrator needs
        to check current state before making a decision.

        Args:
            entity_id: Unique identifier for the entity. Format depends on domain:
                - Registration domain: node UUID as string
                - Workflow domain: workflow instance UUID as string
                - Custom domains: domain-specific identifier
            domain: The domain namespace for the projection. Examples:
                - "registration": Node registration state
                - "workflow": Workflow instance state
                - "billing": Billing/subscription state

        Returns:
            Dictionary containing the entity's projected state if found.
            None if the entity does not exist in the projection.

            The state dictionary structure is domain-specific. Common patterns:
            - Registration: {"state": "active", "capabilities": [...], "last_heartbeat": "..."}
            - Workflow: {"state": "running", "current_step": "...", "started_at": "..."}

        Raises:
            ProjectionReadError: If the query fails due to connection issues,
                timeout, or other infrastructure errors.

        Performance:
            This should be a fast point lookup (O(1) for indexed entities).
            Implementations SHOULD complete within 10ms for typical queries.

        Example:
            ```python
            state = await reader.get_entity_state(
                entity_id="550e8400-e29b-41d4-a716-446655440000",
                domain="registration",
            )
            if state and state.get("state") == "active":
                print(f"Node is active, capabilities: {state.get('capabilities')}")
            ```
        """
        ...

    async def exists(
        self,
        entity_id: str,
        domain: str,
    ) -> bool:
        """
        Check if an entity exists in the projection.

        Lightweight existence check without retrieving the full state.
        Use this when you only need to verify existence, not access state.

        Args:
            entity_id: Unique identifier for the entity.
            domain: The domain namespace for the projection.

        Returns:
            True if the entity exists in the projection.
            False if the entity does not exist.

        Raises:
            ProjectionReadError: If the query fails due to infrastructure errors.

        Performance:
            This should be faster than get_entity_state() as it only checks
            existence without deserializing state. Target: <5ms.

        Example:
            ```python
            if await reader.exists(node_id, domain="registration"):
                # Node is known, proceed with detailed state lookup
                state = await reader.get_entity_state(node_id, domain="registration")
            else:
                # Node not registered, trigger registration flow
                await initiate_registration(node_id)
            ```
        """
        ...

    async def get_by_criteria(
        self,
        criteria: JsonType,
        domain: str,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[JsonType]:
        """
        Query entities matching specified criteria.

        Flexible criteria-based lookup for finding entities that match
        specific conditions. Supports pagination for large result sets.

        Args:
            criteria: Dictionary of field-value pairs to match. Semantics:
                - Exact match: {"field": "value"}
                - List membership: {"field": ["value1", "value2"]} (OR semantics)
                - Nested fields: {"metadata.region": "us-east-1"}
                Implementation-specific operators may be supported.
            domain: The domain namespace for the projection.
            limit: Maximum number of results to return. When None, implementations
                SHOULD use a reasonable default limit (e.g., 100) to prevent
                unbounded queries that could cause performance issues or resource
                exhaustion. Note: None does NOT mean unlimited; implementations
                must enforce a default limit for safety.
            offset: Number of results to skip for pagination. None for no offset
                (start from beginning). Used with limit for cursor-based pagination.

        Returns:
            List of dictionaries containing matching entities' projected state.
            Empty list if no entities match the criteria.
            Each dictionary includes entity_id and the entity's state.

        Raises:
            ProjectionReadError: If the query fails due to infrastructure errors.
            ValueError: If criteria contains invalid or unsupported operators.

        Security:
            Implementations MUST sanitize all criteria values to prevent injection
            attacks (e.g., SQL injection, NoSQL injection, LDAP injection).
            Field names SHOULD be validated against an allowlist of queryable fields
            to prevent access to internal or sensitive fields.
            Nested field access (e.g., "metadata.region") MUST respect domain access
            control policies and not expose fields outside the caller's authorization.

            Recommendations for implementations:
            - Use parameterized queries for database operations
            - Validate field names against allowed queryable fields before query execution
            - Implement rate limiting to prevent DoS via expensive or frequent queries
            - Log and audit sensitive projection queries for security monitoring
            - Sanitize string values to prevent injection patterns
            - Limit query complexity (e.g., maximum number of criteria, nesting depth)

        Performance:
            Performance depends on criteria complexity and index availability.
            Implementations SHOULD optimize for common query patterns.
            Consider adding indexes for frequently queried fields.

        Example:
            ```python
            # Find all active nodes with GPU capability in us-east region
            active_gpu_nodes = await reader.get_by_criteria(
                criteria={
                    "state": "active",
                    "capabilities": "gpu-inference",
                    "metadata.region": "us-east-1",
                },
                domain="registration",
                limit=10,
            )
            for node in active_gpu_nodes:
                print(f"Node {node['entity_id']}: {node['capabilities']}")
            ```
        """
        ...

    # -------------------------------------------------------------------------
    # Registration-Specific Query Methods
    # -------------------------------------------------------------------------
    # These methods provide specialized access for node registration workflows.
    # They are convenience wrappers around the generic methods with
    # registration-specific semantics and validation.

    async def get_registration_status(
        self,
        node_id: str,
        domain: str | None = None,
    ) -> JsonType | None:
        """
        Get the registration status of a specific node.

        Convenience method for retrieving node registration state. This is
        the primary method orchestrators use to check if a node is available
        for work assignment.

        Args:
            node_id: Unique identifier for the node (UUID as string).
            domain: Optional domain qualifier for multi-domain registrations.
                If None, uses the default registration domain.
                Examples: "compute", "effect", "orchestrator"

        Returns:
            Dictionary containing registration state if the node is registered.
            None if the node is not registered.

            Typical state structure:
            {
                "node_id": "uuid-string",
                "state": "active" | "inactive" | "draining" | "suspended",
                "registered_at": "ISO-8601 timestamp",
                "last_heartbeat": "ISO-8601 timestamp",
                "capabilities": ["cap1", "cap2"],
                "metadata": {...}
            }

        Raises:
            ProjectionReadError: If the query fails due to infrastructure errors.

        Example:
            ```python
            status = await reader.get_registration_status(
                node_id="550e8400-e29b-41d4-a716-446655440000",
                domain="compute",
            )
            if status:
                if status["state"] == "active":
                    print(f"Node active since {status['registered_at']}")
                elif status["state"] == "draining":
                    print("Node is draining, don't assign new work")
            else:
                print("Node not registered")
            ```
        """
        ...

    async def get_registered_nodes(
        self,
        domain: str | None = None,
        state: str | None = None,
        capabilities: list[str] | None = None,
        limit: int | None = None,
    ) -> list[JsonType]:
        """
        List registered nodes matching optional filters.

        Query registered nodes with optional filtering by domain, state,
        and capabilities. Used by orchestrators to find available nodes
        for work distribution.

        Args:
            domain: Optional domain filter (e.g., "compute", "effect").
                If None, returns nodes from all domains.
            state: Optional state filter. Common values:
                - "active": Currently available for work
                - "inactive": Registered but not available
                - "draining": Completing current work, no new assignments
                - "suspended": Temporarily unavailable
            capabilities: Optional list of required capabilities.
                Nodes must have ALL listed capabilities (AND semantics).
            limit: Maximum number of results to return. When None, implementations
                SHOULD use a reasonable default limit (e.g., 100) to prevent
                unbounded queries. None does NOT mean unlimited.

        Returns:
            List of dictionaries containing node registration state.
            Empty list if no nodes match the filters.

        Raises:
            ProjectionReadError: If the query fails due to infrastructure errors.

        Example:
            ```python
            # Find active compute nodes with GPU capability
            gpu_nodes = await reader.get_registered_nodes(
                domain="compute",
                state="active",
                capabilities=["gpu-inference", "cuda-12"],
                limit=10,
            )
            if gpu_nodes:
                # Select best node for GPU workload
                selected = select_least_loaded(gpu_nodes)
            else:
                raise NoAvailableNodesError("No GPU nodes available")
            ```
        """
        ...

    async def get_node_capabilities(
        self,
        node_id: str,
    ) -> list[str] | None:
        """
        Get the capability list for a specific node.

        Convenience method for retrieving just the capabilities of a node
        without the full registration state. Useful for capability-based
        routing decisions.

        Args:
            node_id: Unique identifier for the node (UUID as string).

        Returns:
            List of capability strings if the node is registered.
            None if the node is not registered.

            Example capabilities:
            ["compute", "gpu-inference", "cuda-12", "high-memory"]

        Raises:
            ProjectionReadError: If the query fails due to infrastructure errors.

        Example:
            ```python
            caps = await reader.get_node_capabilities(node_id)
            if caps and "gpu-inference" in caps:
                # Route GPU workload to this node
                await route_to_node(node_id, workload)
            ```
        """
        ...
