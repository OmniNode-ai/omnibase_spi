"""
ONEX SPI workflow persistence protocols for event sourcing and state management.

These protocols define the data persistence contracts for workflow orchestration
including event stores, snapshot stores, and projection stores with ACID guarantees.
"""

from typing import Any, Optional, Protocol, runtime_checkable
from uuid import UUID

from omnibase.protocols.types.core_types import ProtocolDateTime
from omnibase.protocols.types.workflow_orchestration_types import (
    ProtocolWorkflowEvent,
    ProtocolWorkflowSnapshot,
    WorkflowEventType,
    WorkflowState,
)


@runtime_checkable
class ProtocolEventStoreTransaction(Protocol):
    """
    Protocol for event store transaction objects.

    Provides ACID transaction support for event store operations
    with rollback capabilities and consistency guarantees.
    """

    transaction_id: UUID
    is_active: bool

    async def commit(self) -> bool:
        """Commit transaction changes."""
        ...

    async def rollback(self) -> None:
        """Rollback transaction changes."""
        ...


@runtime_checkable
class ProtocolEventQueryOptions(Protocol):
    """
    Protocol for event query options.

    Defines filtering, ordering, and pagination options
    for event store queries.
    """

    workflow_type: Optional[str]
    instance_id: Optional[UUID]
    event_types: Optional[list[WorkflowEventType]]
    from_sequence: Optional[int]
    to_sequence: Optional[int]
    from_timestamp: Optional[ProtocolDateTime]
    to_timestamp: Optional[ProtocolDateTime]
    limit: Optional[int]
    offset: Optional[int]
    order_by: Optional[
        str
    ]  # "sequence_asc", "sequence_desc", "timestamp_asc", "timestamp_desc"


@runtime_checkable
class ProtocolEventStoreResult(Protocol):
    """
    Protocol for event store operation results.

    Provides operation outcome information with error details
    and performance metrics.
    """

    success: bool
    events_processed: int
    sequence_numbers: list[int]
    error_message: Optional[str]
    operation_time_ms: float
    storage_size_bytes: Optional[int]


@runtime_checkable
class ProtocolEventStore(Protocol):
    """
    Protocol for workflow event store operations.

    Provides event sourcing capabilities with:
    - Append-only event storage
    - Sequence number guarantees
    - Transactional consistency
    - Event stream reading
    - Optimistic concurrency control

    Usage Example:
        ```python
        # Implementation example (not part of SPI)
        class PostgresEventStore:
            def __init__(self, connection_pool):
                self.pool = connection_pool
                self.sequence_counters: dict[tuple[str, UUID], int] = {}

            async def append_events(
                self,
                events: list[ProtocolWorkflowEvent],
                expected_sequence: Optional[int] = None,
                transaction: Optional[ProtocolEventStoreTransaction] = None
            ) -> ProtocolEventStoreResult:
                # Validate sequence numbers
                if not events:
                    return EventStoreResult(success=False, error_message="No events to append")

                first_event = events[0]
                stream_key = (first_event.workflow_type, first_event.instance_id)

                async with self.pool.acquire() as conn:
                    if transaction:
                        # Use existing transaction
                        db_transaction = conn.transaction()
                    else:
                        # Create new transaction
                        db_transaction = conn.transaction()
                        await db_transaction.start()

                    try:
                        # Check expected sequence if provided
                        if expected_sequence is not None:
                            current_seq = await conn.fetchval(
                                "SELECT COALESCE(MAX(sequence_number), 0) FROM workflow_events "
                                "WHERE workflow_type = $1 AND instance_id = $2",
                                first_event.workflow_type, first_event.instance_id
                            )
                            if current_seq != expected_sequence:
                                raise ConcurrencyError(f"Expected sequence {expected_sequence}, got {current_seq}")

                        # Insert events
                        sequence_numbers = []
                        for event in events:
                            # Get next sequence number
                            next_seq = await conn.fetchval(
                                "SELECT COALESCE(MAX(sequence_number), 0) + 1 FROM workflow_events "
                                "WHERE workflow_type = $1 AND instance_id = $2",
                                event.workflow_type, event.instance_id
                            )

                            # Insert event
                            await conn.execute(
                                '''INSERT INTO workflow_events
                                   (event_id, event_type, workflow_type, instance_id,
                                    correlation_id, sequence_number, timestamp, source,
                                    idempotency_key, payload, metadata, causation_id)
                                   VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)''',
                                event.event_id, event.event_type, event.workflow_type,
                                event.instance_id, event.correlation_id, next_seq,
                                event.timestamp, event.source, event.idempotency_key,
                                json.dumps(event.payload), json.dumps(event.metadata),
                                event.causation_id
                            )

                            sequence_numbers.append(next_seq)

                        if not transaction:
                            await db_transaction.commit()

                        return EventStoreResult(
                            success=True,
                            events_processed=len(events),
                            sequence_numbers=sequence_numbers,
                            operation_time_ms=time.time() * 1000 - start_time
                        )

                    except Exception as e:
                        if not transaction:
                            await db_transaction.rollback()
                        return EventStoreResult(
                            success=False,
                            events_processed=0,
                            sequence_numbers=[],
                            error_message=str(e)
                        )

            async def read_events(
                self,
                query_options: ProtocolEventQueryOptions,
                transaction: Optional[ProtocolEventStoreTransaction] = None
            ) -> list[ProtocolWorkflowEvent]:
                # Build query based on options
                where_conditions = []
                params = []

                if query_options.workflow_type:
                    where_conditions.append("workflow_type = $" + str(len(params) + 1))
                    params.append(query_options.workflow_type)

                if query_options.instance_id:
                    where_conditions.append("instance_id = $" + str(len(params) + 1))
                    params.append(query_options.instance_id)

                # Add more conditions...

                query = f'''SELECT * FROM workflow_events
                           WHERE {" AND ".join(where_conditions) if where_conditions else "1=1"}
                           ORDER BY sequence_number ASC'''

                if query_options.limit:
                    query += f" LIMIT {query_options.limit}"

                async with self.pool.acquire() as conn:
                    rows = await conn.fetch(query, *params)

                    events = []
                    for row in rows:
                        events.append(ProtocolWorkflowEvent(
                            event_id=row['event_id'],
                            event_type=row['event_type'],
                            workflow_type=row['workflow_type'],
                            instance_id=row['instance_id'],
                            correlation_id=row['correlation_id'],
                            sequence_number=row['sequence_number'],
                            timestamp=row['timestamp'],
                            source=row['source'],
                            idempotency_key=row['idempotency_key'],
                            payload=json.loads(row['payload']),
                            metadata=json.loads(row['metadata']),
                            causation_id=row['causation_id']
                        ))

                    return events

        # Usage in application
        event_store: ProtocolEventStore = PostgresEventStore(connection_pool)

        # Append events to stream
        workflow_events = [
            ProtocolWorkflowEvent(
                event_type="workflow.started",
                workflow_type="user_onboarding",
                instance_id=workflow_id,
                correlation_id=correlation_id,
                sequence_number=1,  # Will be assigned by store
                source="orchestrator",
                idempotency_key=f"start-{workflow_id}",
                payload={"user_id": "user-123"}
            ),
            ProtocolWorkflowEvent(
                event_type="task.scheduled",
                workflow_type="user_onboarding",
                instance_id=workflow_id,
                correlation_id=correlation_id,
                sequence_number=2,  # Will be assigned by store
                source="orchestrator",
                idempotency_key=f"schedule-task-{task_id}",
                payload={"task_id": str(task_id), "task_type": "compute"}
            )
        ]

        result = await event_store.append_events(workflow_events)
        if result.success:
            print(f"Appended {result.events_processed} events")

        # Read event stream
        query_options = EventQueryOptions(
            workflow_type="user_onboarding",
            instance_id=workflow_id,
            from_sequence=1,
            limit=100
        )

        events = await event_store.read_events(query_options)
        print(f"Read {len(events)} events from stream")

        # Use transaction for consistency
        async with event_store.begin_transaction() as tx:
            # Append multiple events atomically
            result1 = await event_store.append_events([event1, event2], transaction=tx)
            result2 = await event_store.append_events([event3], transaction=tx)

            if result1.success and result2.success:
                await tx.commit()
            else:
                await tx.rollback()
        ```
    """

    # Event storage operations
    async def append_events(
        self,
        events: list[ProtocolWorkflowEvent],
        expected_sequence: Optional[int] = None,
        transaction: Optional[ProtocolEventStoreTransaction] = None,
    ) -> ProtocolEventStoreResult:
        """
        Append events to event stream.

        Args:
            events: List of events to append
            expected_sequence: Expected current sequence for optimistic concurrency
            transaction: Optional transaction for consistency

        Returns:
            Operation result with sequence numbers assigned
        """
        ...

    async def read_events(
        self,
        query_options: ProtocolEventQueryOptions,
        transaction: Optional[ProtocolEventStoreTransaction] = None,
    ) -> list[ProtocolWorkflowEvent]:
        """
        Read events from event store.

        Args:
            query_options: Query filtering and pagination options
            transaction: Optional transaction for consistency

        Returns:
            List of matching events ordered by sequence
        """
        ...

    async def get_event_stream(
        self,
        workflow_type: str,
        instance_id: UUID,
        from_sequence: int = 1,
        to_sequence: Optional[int] = None,
    ) -> list[ProtocolWorkflowEvent]:
        """
        Get complete event stream for workflow instance.

        Args:
            workflow_type: Workflow type identifier
            instance_id: Workflow instance ID
            from_sequence: Starting sequence number
            to_sequence: Ending sequence number (optional)

        Returns:
            Ordered list of events in stream
        """
        ...

    async def get_last_sequence_number(
        self, workflow_type: str, instance_id: UUID
    ) -> int:
        """
        Get last sequence number for workflow stream.

        Args:
            workflow_type: Workflow type identifier
            instance_id: Workflow instance ID

        Returns:
            Last sequence number (0 if no events)
        """
        ...

    # Transaction management
    async def begin_transaction(self) -> ProtocolEventStoreTransaction:
        """
        Begin new event store transaction.

        Returns:
            Transaction object for atomic operations
        """
        ...

    # Maintenance operations
    async def delete_event_stream(
        self, workflow_type: str, instance_id: UUID
    ) -> ProtocolEventStoreResult:
        """
        Delete entire event stream (use with caution).

        Args:
            workflow_type: Workflow type identifier
            instance_id: Workflow instance ID

        Returns:
            Deletion operation result
        """
        ...

    async def archive_old_events(
        self, before_timestamp: ProtocolDateTime, batch_size: int = 1000
    ) -> ProtocolEventStoreResult:
        """
        Archive old events to cold storage.

        Args:
            before_timestamp: Archive events older than this
            batch_size: Number of events to process per batch

        Returns:
            Archive operation result
        """
        ...


@runtime_checkable
class ProtocolSnapshotStore(Protocol):
    """
    Protocol for workflow snapshot store operations.

    Provides state snapshot capabilities for:
    - Point-in-time state capture
    - Fast state reconstruction
    - Recovery and replay optimization
    - State validation checkpoints

    Usage Example:
        ```python
        # Implementation example (not part of SPI)
        class RedisSnapshotStore:
            def __init__(self, redis_client):
                self.redis = redis_client

            async def save_snapshot(
                self,
                snapshot: ProtocolWorkflowSnapshot,
                transaction: Optional[ProtocolEventStoreTransaction] = None
            ) -> bool:
                # Serialize snapshot
                snapshot_key = f"snapshot:{snapshot.workflow_type}:{snapshot.instance_id}:{snapshot.sequence_number}"
                snapshot_data = {
                    "workflow_type": snapshot.workflow_type,
                    "instance_id": str(snapshot.instance_id),
                    "sequence_number": snapshot.sequence_number,
                    "state": snapshot.state,
                    "context": snapshot.context.dict(),
                    "tasks": [task.dict() for task in snapshot.tasks],
                    "created_at": snapshot.created_at.isoformat(),
                    "metadata": snapshot.metadata
                }

                # Store with expiration
                pipeline = self.redis.pipeline()
                pipeline.hset(snapshot_key, mapping=snapshot_data)
                pipeline.expire(snapshot_key, 86400 * 30)  # 30 days

                # Update latest snapshot pointer
                latest_key = f"latest_snapshot:{snapshot.workflow_type}:{snapshot.instance_id}"
                pipeline.set(latest_key, snapshot.sequence_number)
                pipeline.expire(latest_key, 86400 * 30)

                try:
                    await pipeline.execute()
                    return True
                except Exception:
                    return False

            async def load_snapshot(
                self,
                workflow_type: str,
                instance_id: UUID,
                sequence_number: Optional[int] = None
            ) -> Optional[ProtocolWorkflowSnapshot]:
                if sequence_number is None:
                    # Get latest snapshot
                    latest_key = f"latest_snapshot:{workflow_type}:{instance_id}"
                    sequence_number = await self.redis.get(latest_key)
                    if not sequence_number:
                        return None
                    sequence_number = int(sequence_number)

                snapshot_key = f"snapshot:{workflow_type}:{instance_id}:{sequence_number}"
                snapshot_data = await self.redis.hgetall(snapshot_key)

                if not snapshot_data:
                    return None

                # Deserialize snapshot
                return ProtocolWorkflowSnapshot(
                    workflow_type=snapshot_data["workflow_type"],
                    instance_id=UUID(snapshot_data["instance_id"]),
                    sequence_number=int(snapshot_data["sequence_number"]),
                    state=snapshot_data["state"],
                    # Implementation would reconstruct context and tasks from stored data
                    created_at=datetime.fromisoformat(snapshot_data["created_at"]),
                    metadata=json.loads(snapshot_data.get("metadata", "{}"))
                )

        # Usage in application
        snapshot_store: ProtocolSnapshotStore = RedisSnapshotStore(redis_client)

        # Save workflow snapshot
        snapshot = ProtocolWorkflowSnapshot(
            workflow_type="user_onboarding",
            instance_id=workflow_id,
            sequence_number=current_sequence,
            state="running",
            context=workflow_context,
            tasks=workflow_tasks,
            metadata={"checkpoint": "task_completion"}
        )

        success = await snapshot_store.save_snapshot(snapshot)
        if success:
            print("Snapshot saved successfully")

        # Load latest snapshot for recovery
        latest_snapshot = await snapshot_store.load_snapshot(
            "user_onboarding",
            workflow_id
        )

        if latest_snapshot:
            print(f"Loaded snapshot at sequence {latest_snapshot.sequence_number}")
            # Reconstruct workflow state from snapshot
            workflow_instance = reconstruct_from_snapshot(latest_snapshot)
        ```
    """

    async def save_snapshot(
        self,
        snapshot: ProtocolWorkflowSnapshot,
        transaction: Optional[ProtocolEventStoreTransaction] = None,
    ) -> bool:
        """
        Save workflow state snapshot.

        Args:
            snapshot: Workflow snapshot to save
            transaction: Optional transaction for consistency

        Returns:
            True if save successful
        """
        ...

    async def load_snapshot(
        self,
        workflow_type: str,
        instance_id: UUID,
        sequence_number: Optional[int] = None,
    ) -> Optional[ProtocolWorkflowSnapshot]:
        """
        Load workflow state snapshot.

        Args:
            workflow_type: Workflow type identifier
            instance_id: Workflow instance ID
            sequence_number: Specific sequence (optional, defaults to latest)

        Returns:
            Workflow snapshot or None if not found
        """
        ...

    async def list_snapshots(
        self, workflow_type: str, instance_id: UUID, limit: int = 10
    ) -> list[dict[str, Any]]:
        """
        List available snapshots for workflow.

        Args:
            workflow_type: Workflow type identifier
            instance_id: Workflow instance ID
            limit: Maximum snapshots to return

        Returns:
            List of snapshot metadata (without full content)
        """
        ...

    async def delete_snapshot(
        self, workflow_type: str, instance_id: UUID, sequence_number: int
    ) -> bool:
        """
        Delete specific workflow snapshot.

        Args:
            workflow_type: Workflow type identifier
            instance_id: Workflow instance ID
            sequence_number: Snapshot sequence number

        Returns:
            True if deletion successful
        """
        ...

    async def cleanup_old_snapshots(
        self, workflow_type: str, instance_id: UUID, keep_count: int = 5
    ) -> int:
        """
        Clean up old snapshots, keeping only recent ones.

        Args:
            workflow_type: Workflow type identifier
            instance_id: Workflow instance ID
            keep_count: Number of snapshots to retain

        Returns:
            Number of snapshots deleted
        """
        ...


@runtime_checkable
class ProtocolWorkflowStateStore(Protocol):
    """
    Protocol for workflow state store operations.

    Provides current state management for:
    - Active workflow instance storage
    - Fast state queries and updates
    - Locking and concurrency control
    - State validation and consistency
    """

    async def save_workflow_instance(
        self, workflow_instance: ProtocolWorkflowSnapshot
    ) -> bool:
        """
        Save or update workflow instance state.

        Args:
            workflow_instance: Workflow instance to save

        Returns:
            True if save successful
        """
        ...

    async def load_workflow_instance(
        self, workflow_type: str, instance_id: UUID
    ) -> Optional[ProtocolWorkflowSnapshot]:
        """
        Load workflow instance by ID.

        Args:
            workflow_type: Workflow type identifier
            instance_id: Workflow instance ID

        Returns:
            Workflow instance or None if not found
        """
        ...

    async def query_workflow_instances(
        self,
        workflow_type: Optional[str] = None,
        state: Optional[WorkflowState] = None,
        correlation_id: Optional[UUID] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ProtocolWorkflowSnapshot]:
        """
        Query workflow instances by criteria.

        Args:
            workflow_type: Optional workflow type filter
            state: Optional state filter
            correlation_id: Optional correlation filter
            limit: Maximum instances to return
            offset: Query offset for pagination

        Returns:
            List of matching workflow instances
        """
        ...

    async def delete_workflow_instance(
        self, workflow_type: str, instance_id: UUID
    ) -> bool:
        """
        Delete workflow instance.

        Args:
            workflow_type: Workflow type identifier
            instance_id: Workflow instance ID

        Returns:
            True if deletion successful
        """
        ...

    async def lock_workflow_instance(
        self,
        workflow_type: str,
        instance_id: UUID,
        lock_owner: str,
        timeout_seconds: int = 300,
    ) -> bool:
        """
        Acquire exclusive lock on workflow instance.

        Args:
            workflow_type: Workflow type identifier
            instance_id: Workflow instance ID
            lock_owner: Lock owner identifier
            timeout_seconds: Lock timeout

        Returns:
            True if lock acquired
        """
        ...

    async def unlock_workflow_instance(
        self, workflow_type: str, instance_id: UUID, lock_owner: str
    ) -> bool:
        """
        Release lock on workflow instance.

        Args:
            workflow_type: Workflow type identifier
            instance_id: Workflow instance ID
            lock_owner: Lock owner identifier

        Returns:
            True if unlock successful
        """
        ...
