"""
ONEX SPI workflow event bus protocols for distributed orchestration.

These protocols extend the base event bus with workflow-specific
messaging patterns, event sourcing, and orchestration coordination.
"""

from typing import TYPE_CHECKING, Any, Protocol, Union, runtime_checkable
from uuid import UUID

from omnibase_spi.protocols.types.protocol_core_types import ContextValue
from omnibase_spi.protocols.types.protocol_workflow_orchestration_types import (
    LiteralWorkflowEventType,
    ProtocolWorkflowEvent,
)

if TYPE_CHECKING:
    from omnibase_spi.protocols.event_bus.protocol_event_bus import ProtocolEventBus


@runtime_checkable
class ProtocolWorkflowEventMessage(Protocol):
    """
    Protocol for workflow-specific event messages.

    Extends the base event message with workflow orchestration metadata
    for proper event sourcing and workflow coordination.
    """

    topic: str
    key: Union[bytes, None]
    value: bytes
    headers: dict[str, ContextValue]
    offset: Union[str, None]
    partition: Union[int, None]
    workflow_type: str
    instance_id: UUID
    correlation_id: UUID
    sequence_number: int
    event_type: LiteralWorkflowEventType
    idempotency_key: str

    async def ack(self) -> None: ...

    async def get_workflow_event(self) -> ProtocolWorkflowEvent: ...


@runtime_checkable
class ProtocolWorkflowEventHandler(Protocol):
    """
    Protocol for workflow event handler functions.

    Event handlers process workflow events and update workflow state
    according to event sourcing patterns.
    """

    async def __call__(
        self, event: "ProtocolWorkflowEvent", context: dict[str, ContextValue]
    ) -> None: ...


@runtime_checkable
class ProtocolLiteralWorkflowStateProjection(Protocol):
    """
    Protocol for workflow state projection handlers.

    Projections maintain derived state from workflow events
    for query optimization and real-time monitoring.
    """

    projection_name: str

    async def apply_event(
        self, event: "ProtocolWorkflowEvent", current_state: dict[str, ContextValue]
    ) -> dict[str, ContextValue]: ...

    async def get_state(
        self, workflow_type: str, instance_id: UUID
    ) -> dict[str, ContextValue]: ...


@runtime_checkable
class ProtocolWorkflowEventBus(Protocol):
    """
    Protocol for workflow-specific event bus operations.

    Extends the base event bus with workflow orchestration patterns:
    - Event sourcing with sequence numbers
    - Workflow instance isolation
    - Task coordination messaging
    - State projection updates
    - Recovery and replay support
    """

    @property
    def base_event_bus(self) -> "ProtocolEventBus": ...

    async def publish_workflow_event(
        self,
        event: "ProtocolWorkflowEvent",
        target_topic: Union[str, None] = None,
        partition_key: Union[str, None] = None,
    ) -> None: ...

    async def subscribe_to_workflow_events(
        self,
        workflow_type: str,
        event_types: Union[list[LiteralWorkflowEventType], None] = None,
        handler: Union["ProtocolWorkflowEventHandler", None] = None,
    ) -> str: ...

    async def unsubscribe_from_workflow_events(self, subscription_id: str) -> None: ...

    async def replay_workflow_events(
        self,
        workflow_type: str,
        instance_id: UUID,
        from_sequence: int,
        to_sequence: Union[int, None] = None,
        handler: Union["ProtocolWorkflowEventHandler", None] = None,
    ) -> list["ProtocolWorkflowEvent"]: ...

    async def register_projection(
        self, projection: "ProtocolLiteralWorkflowStateProjection"
    ) -> None: ...

    async def unregister_projection(self, projection_name: str) -> None: ...

    async def get_projection_state(
        self, projection_name: str, workflow_type: str, instance_id: UUID
    ) -> dict[str, ContextValue]: ...

    async def create_workflow_topic(
        self, workflow_type: str, partition_count: int
    ) -> bool: ...

    async def delete_workflow_topic(self, workflow_type: str) -> bool: ...
