"""
Protocol for projection persistence with ordering and idempotency guarantees.

This module defines the contract for projectors that persist projections derived
from reducer outputs. The projector enforces per-entity monotonic ordering using
sequence numbers to prevent stale updates and ensure exactly-once semantics.

Architecture Context:
    In the ONEX event-driven architecture, projections flow through this pipeline:

    1. Events arrive at handlers via the event bus
    2. Reducer nodes process events and produce projections
    3. Runtime invokes the projector synchronously after reducer completion
    4. Projector persists projections with ordering enforcement
    5. Stale updates (lower sequence) are rejected

Sequence Diagram:
    ```
    Handler          Runtime         Reducer         Projector         DB
       |                |               |               |               |
       |-- dispatch --> |               |               |               |
       |                |-- execute --> |               |               |
       |                |               |-- returns     |               |
       |                | <-- projections[] ---         |               |
       |                |                               |               |
       |                |-- persist(projection, seq) -->|               |
       |                |                               |-- write if    |
       |                |                               |   seq > last ->|
       |                | <-- PersistResult ------------+               |
       |                |   (applied | rejected_stale)  |               |
       | <-- response --|               |               |               |
    ```

Idempotency Layers:
    The ONEX platform uses two distinct idempotency mechanisms:

    1. Runtime Idempotency (B3 / ProtocolIdempotencyStore):
       - Prevents duplicate handler execution for the same message
       - Uses message_id as the deduplication key
       - Guards the entry point to handler execution
       - Scope: message-level (prevents reprocessing same message)

    2. Projector Idempotency (F0 / ProtocolProjector - this protocol):
       - Prevents stale or out-of-order projection writes
       - Uses (entity_id, domain, sequence) for ordering
       - Guards the projection persistence layer
       - Scope: entity-level (ensures monotonic state updates)

    Together these layers ensure:
    - Each message is processed exactly once (B3)
    - Each entity's projections are applied in order (F0)

Ordering Semantics:
    - Per-entity monotonic: sequence numbers are per (entity_id, domain) pair
    - Partition-aware: optionally uses (partition, offset) as sequence info
    - Gap tolerance: gaps in sequence numbers are allowed (out-of-order delivery)
    - Concurrent safety: atomic check-and-persist for thread safety

Example implementations:
    - PostgresProjector: Uses INSERT ON CONFLICT with sequence comparison
    - ValkeyProjector: Uses WATCH/MULTI for optimistic locking
    - InMemoryProjector: Uses threading.Lock for testing

Related tickets:
    - OMN-940: Define ProtocolProjector in omnibase_spi
    - OMN-930: Define ProtocolProjectionReader for orchestrators
    - OMN-991: Define ProtocolIdempotencyStore (B3 runtime deduplication)
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Literal, Protocol, runtime_checkable


@runtime_checkable
class ProtocolSequenceInfo(Protocol):
    """
    Sequence information for ordering projections.

    This protocol defines the minimal contract for sequence tracking.
    Implementations may use various schemes:
    - Simple sequence numbers (1, 2, 3, ...)
    - Kafka-style (partition, offset) tuples
    - Hybrid approaches with vector clocks

    The projector uses this information to determine if a projection
    is stale (sequence <= last applied) or should be applied.

    Attributes:
        sequence: The monotonically increasing sequence number.
            Higher values indicate more recent updates.
        partition: Optional partition identifier for partitioned systems.
            When present, ordering is per (entity_id, domain, partition).
    """

    @property
    def sequence(self) -> int:
        """
        The sequence number for ordering.

        Must be monotonically increasing within a partition.
        Higher values indicate more recent events.

        Returns:
            The sequence number as a non-negative integer.
        """
        ...

    @property
    def partition(self) -> str | None:
        """
        Optional partition identifier.

        When using partitioned event sources (e.g., Kafka), this
        identifies the partition. Ordering is enforced per-partition.

        Returns:
            The partition identifier or None for non-partitioned systems.
        """
        ...


@runtime_checkable
class ProtocolPersistResult(Protocol):
    """
    Result of a projection persist operation.

    Provides information about whether the projection was applied
    or rejected due to staleness.

    Attributes:
        status: The persist operation outcome.
        entity_id: The entity this projection targeted.
        applied_sequence: The sequence that was applied (if successful).
        rejected_reason: Reason for rejection (if rejected).
    """

    @property
    def status(self) -> Literal["applied", "rejected_stale", "rejected_conflict"]:
        """
        The outcome of the persist operation.

        Values:
            - "applied": Projection was successfully persisted
            - "rejected_stale": Projection was rejected due to lower sequence
            - "rejected_conflict": Projection was rejected due to concurrent update

        Returns:
            The status literal indicating the outcome.
        """
        ...

    @property
    def entity_id(self) -> str:
        """
        The entity identifier this operation targeted.

        Returns:
            The entity ID as a string.
        """
        ...

    @property
    def applied_sequence(self) -> int | None:
        """
        The sequence number that was applied.

        Returns:
            The sequence number if status is "applied", None otherwise.
        """
        ...

    @property
    def rejected_reason(self) -> str | None:
        """
        Reason for rejection when status is not "applied".

        Returns:
            A descriptive reason string if rejected, None if applied.
        """
        ...


@runtime_checkable
class ProtocolBatchPersistResult(Protocol):
    """
    Result of a batch projection persist operation.

    Aggregates results from persisting multiple projections,
    providing summary statistics and individual outcomes.
    """

    @property
    def total_count(self) -> int:
        """
        Total number of projections in the batch.

        Returns:
            The count of projections submitted.
        """
        ...

    @property
    def applied_count(self) -> int:
        """
        Number of projections successfully applied.

        Returns:
            The count of applied projections.
        """
        ...

    @property
    def rejected_count(self) -> int:
        """
        Number of projections rejected (stale or conflict).

        Returns:
            The count of rejected projections.
        """
        ...

    @property
    def results(self) -> Sequence[ProtocolPersistResult]:
        """
        Individual results for each projection in the batch.

        Results are in the same order as the input projections.

        Returns:
            Sequence of individual persist results.
        """
        ...


@runtime_checkable
class ProtocolProjector(Protocol):
    """
    Persists projections with ordering and idempotency guarantees.

    The projector is invoked by the runtime after a reducer produces
    projections. It enforces per-entity monotonic ordering by tracking
    the last applied sequence for each (entity_id, domain) pair.

    Execution Model:
        1. Reducer returns projections in handler output
        2. Runtime invokes projector.persist() synchronously
        3. Projector checks if sequence > last_applied for entity
        4. If yes: persist and update last_applied sequence
        5. If no: reject as stale

    Ordering Invariants:
        - Uses (entity_id, domain, sequence) for ordering decisions
        - Per-entity monotonic: sequence must increase for each entity
        - Partition-aware: optionally uses (partition, offset) as sequence
        - Reject updates with sequence <= last applied sequence

    Concurrency:
        - persist() MUST be atomic (check + write in single operation)
        - Implementations MUST handle concurrent calls for same entity
        - First writer wins; concurrent lower-sequence writes rejected

    Error Handling:
        - Connection errors raise ProjectorError
        - Stale updates return rejected_stale status (not an error)
        - Invalid projections raise ValueError

    Type Design Note:
        The `projection` parameter in persist() and batch_persist() uses
        `Any` type intentionally. This is a deliberate SPI design decision:

        - SPI protocols must remain domain-agnostic to support any projection
          type (OrderProjection, UserProjection, InventoryProjection, etc.)
        - Concrete implementations in omnibase_infra should validate and
          narrow the projection type as appropriate for their domain
        - This allows maximum flexibility while maintaining type safety at
          the implementation layer where domain knowledge exists

    Example Usage:
        ```python
        # Single projection persistence
        projection = reducer.execute(event)
        sequence = SequenceInfo(sequence=event.offset, partition=event.partition)

        result = await projector.persist(
            projection=projection,
            entity_id=projection.entity_id,
            domain="orders",
            sequence_info=sequence,
        )

        if result.status == "applied":
            logger.info(f"Applied projection at sequence {result.applied_sequence}")
        elif result.status == "rejected_stale":
            logger.debug(f"Skipped stale update: {result.rejected_reason}")
        ```

    Migration:
        This protocol is introduced in v0.4.1 as part of the projection
        persistence feature (F0). Future versions may add:
        - Snapshot creation triggers
        - Projection compaction
        - Read-your-writes consistency options
    """

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

        Atomically checks if the projection's sequence is higher than
        the last applied sequence for this entity. If so, persists the
        projection and updates the tracking. If not, rejects as stale.

        Args:
            projection: The projection data to persist. Type depends on
                the projection domain (e.g., OrderProjection, UserProjection).
            entity_id: Unique identifier for the entity this projection
                represents. Combined with domain for isolation.
            domain: Domain namespace for the projection. Examples:
                "orders", "users", "inventory". Enables domain-isolated
                sequence tracking.
            sequence_info: Sequence information for ordering. Contains
                the sequence number and optional partition identifier.
            correlation_id: Optional correlation ID for distributed tracing.
                Propagated to logs and metrics.

        Returns:
            PersistResult indicating success (applied) or rejection
            (rejected_stale, rejected_conflict).

        Raises:
            ProjectorError: If the atomic persist operation fails due to
                connection issues or other storage errors.
            ValueError: If projection, entity_id, or domain is invalid.

        Ordering Semantics:
            Given last_applied_sequence L for (entity_id, domain):
            - If sequence_info.sequence > L: persist and update L
            - If sequence_info.sequence <= L: return rejected_stale

        Concurrency:
            When multiple callers invoke this method simultaneously with
            the same (entity_id, domain), only the highest sequence wins.
            Lower sequences are rejected as stale.

        Example:
            ```python
            result = await projector.persist(
                projection={"order_id": "123", "status": "shipped"},
                entity_id="order-123",
                domain="orders",
                sequence_info=SequenceInfo(sequence=42, partition="orders-0"),
                correlation_id="corr-456",
            )

            match result.status:
                case "applied":
                    print(f"Persisted at sequence {result.applied_sequence}")
                case "rejected_stale":
                    print(f"Stale: {result.rejected_reason}")
                case "rejected_conflict":
                    print(f"Conflict: {result.rejected_reason}")
            ```
        """
        ...

    async def batch_persist(
        self,
        projections: Sequence[tuple[object, str, str, ProtocolSequenceInfo]],
        *,
        correlation_id: str | None = None,
    ) -> ProtocolBatchPersistResult:
        """
        Persist multiple projections in a batch operation.

        Processes multiple projections efficiently, maintaining ordering
        guarantees for each entity. Projections for different entities
        may be processed in parallel by implementations.

        Args:
            projections: Sequence of tuples, each containing:
                - projection: The projection data to persist
                - entity_id: Entity identifier for this projection
                - domain: Domain namespace for the projection
                - sequence_info: Sequence information for ordering
            correlation_id: Optional correlation ID for distributed tracing.

        Returns:
            BatchPersistResult containing summary statistics and
            individual results for each projection.

        Raises:
            ProjectorError: If the batch operation fails critically.
                Partial failures are reported in the result, not raised.
            ValueError: If any projection tuple is malformed.

        Atomicity:
            Individual projections within the batch are atomic, but the
            batch as a whole is NOT atomic. Some projections may succeed
            while others fail. Check individual results for status.

            Per-projection guarantee: Each projection in the batch either
            fully succeeds or fully fails; partial writes within a single
            projection are not allowed. An individual projection will never
            be left in an inconsistent state.

        Ordering:
            Projections for the same (entity_id, domain) within a batch
            are processed in sequence order, highest first. This ensures
            that if multiple updates for the same entity are in the batch,
            only the highest sequence is applied.

        Example:
            ```python
            projections = [
                ({"id": "1", "v": 1}, "e1", "orders", seq_info_1),
                ({"id": "2", "v": 2}, "e2", "orders", seq_info_2),
                ({"id": "1", "v": 3}, "e1", "orders", seq_info_3),  # Higher seq
            ]

            result = await projector.batch_persist(projections)

            print(f"Applied: {result.applied_count}/{result.total_count}")
            for r in result.results:
                print(f"  {r.entity_id}: {r.status}")
            ```
        """
        ...

    async def get_last_sequence(
        self,
        entity_id: str,
        domain: str,
    ) -> ProtocolSequenceInfo | None:
        """
        Get the last applied sequence for an entity.

        Retrieves the sequence information for the most recently
        applied projection for the given (entity_id, domain) pair.

        Args:
            entity_id: Unique identifier for the entity.
            domain: Domain namespace for the projection.

        Returns:
            SequenceInfo for the last applied projection, or None if
            no projection has been applied for this entity/domain.

        Raises:
            ProjectorError: If the query fails due to connection issues.

        Use Cases:
            - Diagnostic queries for debugging
            - Pre-flight checks before batch operations
            - Recovery and replay scenarios

        Note:
            For normal projection persistence, use persist() which
            atomically checks and updates. Use get_last_sequence()
            only for diagnostics or recovery scenarios.

        Example:
            ```python
            last_seq = await projector.get_last_sequence("order-123", "orders")
            if last_seq:
                print(f"Last applied: sequence={last_seq.sequence}")
            else:
                print("No projections applied for this entity")
            ```
        """
        ...

    async def is_stale(
        self,
        entity_id: str,
        domain: str,
        sequence_info: ProtocolSequenceInfo,
    ) -> bool:
        """
        Check if a sequence would be rejected as stale.

        Performs a read-only check to determine if a projection with
        the given sequence would be rejected. Useful for pre-flight
        validation before expensive projection computation.

        Args:
            entity_id: Unique identifier for the entity.
            domain: Domain namespace for the projection.
            sequence_info: Sequence information to check.

        Returns:
            True if the sequence is stale (would be rejected).
            False if the sequence is fresh (would be applied).

        Raises:
            ProjectorError: If the query fails due to connection issues.

        Staleness Definition:
            A sequence is stale if:
            sequence_info.sequence <= last_applied_sequence(entity_id, domain)

        Note:
            This is a point-in-time check. Between is_stale() and persist(),
            another caller might apply a higher sequence. For correctness,
            always rely on the persist() result, not is_stale().

        Use Cases:
            - Pre-flight validation before expensive computation
            - Debugging and diagnostics
            - Metrics and monitoring (tracking stale event rates)

        Example:
            ```python
            if await projector.is_stale("order-123", "orders", seq_info):
                # Skip expensive projection computation
                logger.debug(f"Skipping stale event for order-123")
                return

            # Proceed with projection computation
            projection = compute_projection(event)
            await projector.persist(projection, "order-123", "orders", seq_info)
            ```
        """
        ...

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

        Cleans up old sequence tracking entries to prevent unbounded
        storage growth. Should be called periodically by a background
        job after snapshots are taken.

        Args:
            domain: Domain namespace to clean up.
            sequence: Remove tracking for sequences strictly less than
                this value. Typically set to the last snapshot sequence.
            batch_size: Maximum entries to remove per batch. Implementations
                should batch deletions to avoid long-running transactions.
            confirmed: Safety confirmation for destructive cleanup. Implementations
                MAY require this to be True before performing the cleanup operation.
                This provides an extra layer of protection against accidental
                cleanup calls. Default is False.

        Returns:
            Number of tracking entries removed.

        Raises:
            ProjectorError: If the cleanup operation fails.

        Safety:
            Only removes sequence tracking metadata, not the projections
            themselves. Projections may be managed separately with their
            own retention policies.

        Warning:
            After cleanup, the projector cannot detect stale updates for
            sequences BELOW the cleanup threshold. Stale detection continues
            to work normally for sequences at or above the threshold. This
            means:

            - Sequences >= threshold: Normal stale detection and rejection
            - Sequences < threshold: No stale detection (tracking removed)

            Only call after taking a snapshot at or above the cleanup sequence
            to ensure no data loss from undetected stale updates.

        Example:
            ```python
            # After taking snapshot at sequence 10000
            removed = await projector.cleanup_before_sequence(
                domain="orders",
                sequence=10000,
                batch_size=5000,
                confirmed=True,  # Required by some implementations
            )
            logger.info(f"Cleaned up {removed} tracking entries")
            ```
        """
        ...
