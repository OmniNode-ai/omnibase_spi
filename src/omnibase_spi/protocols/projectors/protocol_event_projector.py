"""Protocol for event-to-state projection.

This module defines the interface for projectors that consume event streams
and materialize state to a persistence store. Projectors are strictly read-model
builders with no side effects beyond their target store.

Architectural Context:
    In the ONEX event-driven architecture, projectors serve as the bridge
    between event streams and queryable read models:

    1. Events flow through the event bus (via ModelEnvelope)
    2. Projectors consume specific event types they are configured to handle
    3. Projectors materialize state to their target persistence store
    4. Orchestrators and services query this materialized state

Core Principle:
    Projectors are consumers only - they materialize state from events but
    NEVER emit events, intents, or projections. They are pure read-model
    builders with no outbound side effects.

Idempotency:
    All projection operations MUST be idempotent. Replaying the same event
    must produce the same result without additional side effects. This
    enables safe event replay and catch-up scenarios.

Related tickets:
    - OMN-1167: Define ProtocolEventProjector in omnibase_spi
    - OMN-940: ProtocolProjector (projection persistence with ordering)
    - OMN-930: ProtocolProjectionReader for orchestrators

Note:
    This protocol (ProtocolEventProjector in projectors/) is distinct from
    ProtocolProjector in projections/, which handles projection persistence
    with ordering guarantees. This protocol focuses on event-to-state
    projection semantics.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable
from uuid import UUID

if TYPE_CHECKING:
    from omnibase_core.models.common import ModelEnvelope
    from omnibase_core.models.projectors import ModelProjectionResult
    from omnibase_core.types import JsonType

__all__ = ["ProtocolEventProjector"]


@runtime_checkable
class ProtocolEventProjector(Protocol):
    """Interface for event-to-state projection.

    Projectors consume ModelEnvelope streams and materialize
    state to a persistence store. They are strictly read-model
    builders with no side effects beyond their target store.

    Execution Model:
        1. Event bus delivers ModelEnvelope to projector
        2. Projector checks if event type is in consumed_events
        3. Projector extracts aggregate_id and payload from event
        4. Projector applies business logic to update state
        5. Projector persists updated state to target store
        6. Projector returns ModelProjectionResult

    Constraints:
        Projectors MUST NOT:
        - Emit events to any event bus
        - Publish messages to any messaging system
        - Create intents or commands
        - Have side effects beyond the target persistence store
        - Modify the original event envelope

    Idempotency:
        The project() method MUST be idempotent. Given the same event
        envelope, it must produce the same state changes. This is
        critical for event replay and catch-up scenarios.

    Thread Safety:
        Implementations should be safe for concurrent calls with
        different aggregate_id values. Concurrent calls with the
        same aggregate_id may require serialization at the
        implementation level.

    Error Handling:
        The projector uses a consistent exception hierarchy from omnibase_spi.exceptions:

        - ProjectorError: Persistence layer failures. Raised when database
          connections fail, writes timeout, or other infrastructure errors
          occur during projection or state retrieval.

        - ValueError: Invalid input validation. Raised when an event with
          an unsupported event_type (not in consumed_events) is passed to
          project(). Implementations may also raise this for malformed
          event payloads.

        Note: Idempotency violations (duplicate event processing) are NOT
        errors. The project() method should return ModelProjectionResult
        with skipped=True instead of raising an exception.

    Example:
        ```python
        class OrderProjector:
            @property
            def projector_id(self) -> str:
                return "order-projector-v1"

            @property
            def aggregate_type(self) -> str:
                return "Order"

            @property
            def consumed_events(self) -> list[str]:
                return ["OrderCreated", "OrderShipped", "OrderCancelled"]

            async def project(self, event: ModelEnvelope) -> ModelProjectionResult:
                # Extract and apply event to state
                order_id = event.aggregate_id
                if event.event_type == "OrderCreated":
                    await self._create_order(order_id, event.payload)
                elif event.event_type == "OrderShipped":
                    await self._mark_shipped(order_id, event.payload)
                # ... etc
                return ModelProjectionResult(success=True)

            async def get_state(self, aggregate_id: UUID) -> Order | None:
                return await self._repository.find_by_id(aggregate_id)
        ```

    Migration:
        This protocol is introduced in v0.4.2 as part of the event-sourcing
        infrastructure. It complements ProtocolProjector in projections/
        which handles the persistence ordering layer.

    Performance:
        Implementations should consider these performance characteristics:

        Batch Projection:
            When processing event backlogs or catch-up scenarios,
            implementations may benefit from batching writes to the
            persistence store. While project() handles single events,
            the backing store operations can be buffered and flushed
            periodically (e.g., every N events or every M milliseconds).

        State Caching:
            The get_state() method may be called frequently by query
            services. Implementations should consider:
            - In-memory caching with appropriate TTL for hot aggregates
            - Read-through cache patterns for cold aggregates
            - Cache invalidation on successful project() calls

        Concurrent Projection:
            - Different aggregate_ids: Safe for parallel processing
            - Same aggregate_id: Requires serialization to maintain
              event ordering within an aggregate
            - Consider partitioning strategies (e.g., aggregate_id hash)
              to enable parallel processing while preserving per-aggregate
              ordering

        Connection Pooling:
            Persistence store connections should be pooled and reused.
            Avoid creating new connections per project() call.
    """

    @property
    def projector_id(self) -> str:
        """Unique identifier for this projector.

        The projector ID is used for:
        - Logging and tracing
        - Consumer group identification in event bus
        - Checkpoint tracking for replay scenarios
        - Metrics and monitoring

        Format:
            Recommended format is "{aggregate-type}-projector-{version}"
            Example: "order-projector-v1", "inventory-projector-v2"

        Returns:
            A unique string identifier for this projector instance.

        Invariants:
            - Must be unique across all projectors in the system
            - Must be stable (same value across restarts)
            - Should include version for safe rolling updates
        """
        ...

    @property
    def aggregate_type(self) -> str:
        """The aggregate type this projector handles.

        Identifies the domain aggregate that this projector builds
        read models for. Events with matching aggregate types are
        routed to this projector.

        Format:
            PascalCase aggregate name.
            Example: "Order", "Inventory", "User", "Payment"

        Returns:
            The aggregate type string.

        Routing:
            The event bus may use this property to route events
            to the appropriate projector based on the event's
            aggregate_type field.
        """
        ...

    @property
    def consumed_events(self) -> list[str]:
        """Event types this projector consumes.

        Lists all event types that this projector knows how to
        handle. Events not in this list should be ignored
        (or trigger a warning if delivered).

        Format:
            PascalCase event type names.
            Example: ["OrderCreated", "OrderShipped", "OrderCancelled"]

        Returns:
            List of event type strings this projector handles.

        Usage:
            - Event bus filtering: Only deliver matching events
            - Validation: Warn if unexpected event types arrive
            - Documentation: Self-documenting projector capabilities
            - Testing: Generate test events for each consumed type
        """
        ...

    async def project(
        self,
        event: ModelEnvelope,
    ) -> ModelProjectionResult:
        """Project event to persistence store.

        Processes a single event and updates the materialized state
        accordingly. This is the core projection logic.

        Idempotency:
            This method MUST be idempotent. Replaying the same event
            (same event_id) must produce the same result without
            creating duplicate side effects.

        Implementation Patterns:
            1. Upsert pattern: Use event_id as idempotency key
            2. Version check: Compare event sequence with stored version
            3. Conditional write: Only update if event is newer

        Constraints:
            This method MUST NOT:
            - Emit events to any event bus
            - Publish to messaging systems
            - Create intents or commands
            - Have side effects beyond target store
            - Block indefinitely

        Args:
            event: The event envelope to project. Contains:
                - event_id: Unique event identifier
                - event_type: Type of event (must be in consumed_events)
                - aggregate_id: The aggregate this event belongs to
                - aggregate_type: Type of aggregate
                - payload: Event-specific data
                - metadata: Tracing and correlation info

        Returns:
            ModelProjectionResult indicating:
                - success: Whether projection completed successfully
                - skipped: Whether event was skipped (already processed)
                - error: Error details if projection failed

        Raises:
            ValueError: If event_type is not in consumed_events
            ProjectorError: If persistence operation fails

        Example:
            ```python
            async def project(self, event: ModelEnvelope) -> ModelProjectionResult:
                if event.event_type not in self.consumed_events:
                    return ModelProjectionResult(skipped=True, reason="Unknown event")

                try:
                    await self._apply_event(event)
                    return ModelProjectionResult(success=True)
                except DuplicateEventError:
                    return ModelProjectionResult(skipped=True, reason="Already processed")
            ```
        """
        ...

    async def get_state(
        self,
        aggregate_id: UUID,
    ) -> JsonType | None:
        """Get current projected state for an aggregate.

        Retrieves the materialized state for a specific aggregate.
        This represents the current view built from all projected
        events for that aggregate.

        Consistency:
            The returned state reflects all successfully projected
            events up to the most recent one. There may be a lag
            between event publication and state availability.

        Args:
            aggregate_id: The UUID of the aggregate to retrieve.
                Must match the aggregate_id from projected events.

        Returns:
            The current materialized state for the aggregate, or
            None if no events have been projected for this aggregate.

            The return type is JsonType because the specific state type
            depends on the domain. Implementations should document
            their concrete return type.

        Raises:
            ProjectorError: If state retrieval fails due to
                persistence issues.

        Example:
            ```python
            async def get_state(self, aggregate_id: UUID) -> Order | None:
                return await self._db.orders.find_one({"_id": str(aggregate_id)})
            ```

        Note:
            This method is read-only and has no side effects.
            It may be called frequently for queries and should
            be optimized for read performance.

        Performance:
            This method is often on the hot path for query services.
            Consider caching strategies (see class-level Performance
            section) and ensure the underlying persistence query is
            indexed appropriately on aggregate_id.
        """
        ...
