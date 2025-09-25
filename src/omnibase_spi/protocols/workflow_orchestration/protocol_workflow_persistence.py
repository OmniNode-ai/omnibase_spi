"""
ONEX SPI workflow persistence protocols for event sourcing and state management.

These protocols define the data persistence contracts for workflow orchestration
including event stores, snapshot stores, and projection stores with ACID guarantees.
"""

from typing import Any, Optional, Protocol, runtime_checkable
from uuid import UUID

from omnibase_spi.protocols.types.core_types import ProtocolDateTime
from omnibase_spi.protocols.types.workflow_orchestration_types import (
    LiteralWorkflowEventType,
    LiteralWorkflowState,
    ProtocolWorkflowEvent,
    ProtocolWorkflowSnapshot,
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
    event_types: Optional[list[LiteralWorkflowEventType]]
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

    """

    # Event storage operations
    async def append_events(
        self,
        events: list[ProtocolWorkflowEvent],
        expected_sequence: Optional[int],
        transaction: Optional[ProtocolEventStoreTransaction],
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
        transaction: Optional[ProtocolEventStoreTransaction],
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
        from_sequence: int,
        to_sequence: Optional[int],
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
        self, before_timestamp: ProtocolDateTime, batch_size: int
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

    """

    async def save_snapshot(
        self,
        snapshot: ProtocolWorkflowSnapshot,
        transaction: Optional[ProtocolEventStoreTransaction],
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
        sequence_number: Optional[int],
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
        self, workflow_type: str, instance_id: UUID, limit: int
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
        self, workflow_type: str, instance_id: UUID, keep_count: int
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
class ProtocolLiteralWorkflowStateStore(Protocol):
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
        workflow_type: Optional[str],
        state: Optional[LiteralWorkflowState],
        correlation_id: Optional[UUID],
        limit: int,
        offset: int,
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
        timeout_seconds: int,
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
