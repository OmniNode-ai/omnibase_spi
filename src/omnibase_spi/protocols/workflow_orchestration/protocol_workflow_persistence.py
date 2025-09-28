"""
ONEX SPI workflow persistence protocols for event sourcing and state management.

These protocols define the data persistence contracts for workflow orchestration
including event stores, snapshot stores, and projection stores with ACID guarantees.
"""

from typing import TYPE_CHECKING, Any, Protocol, Union, runtime_checkable
from uuid import UUID

from omnibase_spi.protocols.types.protocol_workflow_orchestration_types import (
    LiteralWorkflowEventType,
    LiteralWorkflowState,
    ProtocolWorkflowEvent,
    ProtocolWorkflowSnapshot,
)

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_core_types import ProtocolDateTime


@runtime_checkable
class ProtocolEventStoreTransaction(Protocol):
    """
    Protocol for event store transaction objects.

    Provides ACID transaction support for event store operations
    with rollback capabilities and consistency guarantees.
    """

    transaction_id: UUID
    is_active: bool

    async def commit(self) -> bool: ...

    async def rollback(self) -> None: ...


@runtime_checkable
class ProtocolEventQueryOptions(Protocol):
    """
    Protocol for event query options.

    Defines filtering, ordering, and pagination options
    for event store queries.
    """

    workflow_type: Union[str, None]
    instance_id: Union[UUID, None]
    event_types: Union[list[LiteralWorkflowEventType], None]
    from_sequence: Union[int, None]
    to_sequence: Union[int, None]
    from_timestamp: Union["ProtocolDateTime", None]
    to_timestamp: Union["ProtocolDateTime", None]
    limit: Union[int, None]
    offset: Union[int, None]
    order_by: Union[str, None]


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
    error_message: Union[str, None]
    operation_time_ms: float
    storage_size_bytes: Union[int, None]


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

    async def append_events(
        self,
        events: list["ProtocolWorkflowEvent"],
        expected_sequence: Union[int, None],
        transaction: Union["ProtocolEventStoreTransaction", None],
    ) -> ProtocolEventStoreResult: ...

    async def read_events(
        self,
        query_options: "ProtocolEventQueryOptions",
        transaction: Union["ProtocolEventStoreTransaction", None],
    ) -> list["ProtocolWorkflowEvent"]: ...

    async def get_event_stream(
        self,
        workflow_type: str,
        instance_id: UUID,
        from_sequence: int,
        to_sequence: Union[int, None],
    ) -> list["ProtocolWorkflowEvent"]: ...

    async def get_last_sequence_number(
        self, workflow_type: str, instance_id: UUID
    ) -> int: ...

    async def begin_transaction(self) -> ProtocolEventStoreTransaction: ...

    async def delete_event_stream(
        self, workflow_type: str, instance_id: UUID
    ) -> ProtocolEventStoreResult: ...

    async def archive_old_events(
        self, before_timestamp: "ProtocolDateTime", batch_size: int
    ) -> ProtocolEventStoreResult: ...


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
        snapshot: "ProtocolWorkflowSnapshot",
        transaction: Union["ProtocolEventStoreTransaction", None],
    ) -> bool: ...

    async def load_snapshot(
        self, workflow_type: str, instance_id: UUID, sequence_number: Union[int, None]
    ) -> Union[ProtocolWorkflowSnapshot, None]: ...

    async def list_snapshots(
        self, workflow_type: str, instance_id: UUID, limit: int
    ) -> list[dict[str, Any]]: ...

    async def delete_snapshot(
        self, workflow_type: str, instance_id: UUID, sequence_number: int
    ) -> bool: ...

    async def cleanup_old_snapshots(
        self, workflow_type: str, instance_id: UUID, keep_count: int
    ) -> int: ...


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
        self, workflow_instance: "ProtocolWorkflowSnapshot"
    ) -> bool: ...

    async def load_workflow_instance(
        self, workflow_type: str, instance_id: UUID
    ) -> Union[ProtocolWorkflowSnapshot, None]: ...

    async def query_workflow_instances(
        self,
        workflow_type: Union[str, None],
        state: Union["LiteralWorkflowState", None],
        correlation_id: Union[UUID, None],
        limit: int,
        offset: int,
    ) -> list["ProtocolWorkflowSnapshot"]: ...

    async def delete_workflow_instance(
        self, workflow_type: str, instance_id: UUID
    ) -> bool: ...

    async def lock_workflow_instance(
        self,
        workflow_type: str,
        instance_id: UUID,
        lock_owner: str,
        timeout_seconds: int,
    ) -> bool: ...

    async def unlock_workflow_instance(
        self, workflow_type: str, instance_id: UUID, lock_owner: str
    ) -> bool: ...
