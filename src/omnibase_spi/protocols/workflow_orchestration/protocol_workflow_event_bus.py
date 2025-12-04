"""
ONEX SPI workflow event bus protocols for distributed orchestration.

These protocols extend the base event bus with workflow-specific
messaging patterns, event sourcing, and orchestration coordination.
"""

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable
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
    Protocol for workflow-specific event messages with orchestration metadata.

    Extends the base event message with workflow orchestration metadata
    including instance tracking, sequence numbers, and idempotency keys
    for proper event sourcing and workflow coordination.

    Attributes:
        topic: Kafka topic for the message
        key: Message key for partitioning
        value: Serialized message payload
        headers: Message headers with context values
        offset: Kafka message offset
        partition: Kafka partition number
        workflow_type: Type identifier for the workflow
        instance_id: Unique workflow instance identifier
        correlation_id: Correlation ID for request tracking
        sequence_number: Event sequence within workflow
        event_type: Workflow event classification
        idempotency_key: Key for duplicate detection

    Example:
        ```python
        # ProtocolWorkflowEventMessage is received via handler callback
        async def handle_workflow_message(
            msg: ProtocolWorkflowEventMessage,
        ) -> None:
            print(f"Workflow: {msg.workflow_type}/{msg.instance_id}")
            print(f"Event: {msg.event_type} (seq: {msg.sequence_number})")

            event = await msg.get_workflow_event()
            await process_event(event)
            await msg.ack()

        # Register handler with the event bus
        bus: ProtocolWorkflowEventBus = get_workflow_event_bus()
        subscription_id = await bus.subscribe_to_workflow_events(
            workflow_type="data_processing",
            handler=handle_workflow_message,
        )
        ```

    See Also:
        ProtocolWorkflowEventBus: Event bus interface for subscription.
        ProtocolWorkflowEvent: Event payload structure.
    """

    topic: str
    key: bytes | None
    value: bytes
    headers: dict[str, ContextValue]
    offset: str | None
    partition: int | None
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
    Protocol for workflow event handler callback functions.

    Defines the interface for handlers that process workflow events
    and update workflow state according to event sourcing patterns,
    enabling reactive workflow processing.

    Example:
        ```python
        async def handle_task_completed(
            event: ProtocolWorkflowEvent,
            context: dict[str, ContextValue]
        ) -> None:
            task_id = event.payload.get("task_id")
            result = event.payload.get("result")
            await update_workflow_state(task_id, "completed", result)

        bus: ProtocolWorkflowEventBus = get_workflow_event_bus()
        await bus.subscribe_to_workflow_events(
            workflow_type="data_processing",
            event_types=["task_completed"],
            handler=handle_task_completed
        )
        ```

    See Also:
        - ProtocolWorkflowEventBus: Event subscription
        - ProtocolWorkflowEvent: Event structure
    """

    async def __call__(
        self, event: "ProtocolWorkflowEvent", context: dict[str, ContextValue]
    ) -> None: ...


@runtime_checkable
class ProtocolLiteralWorkflowStateProjection(Protocol):
    """
    Protocol for workflow state projection handlers.

    Projections maintain derived state from workflow events for
    query optimization and real-time monitoring, enabling CQRS
    patterns with event-sourced workflows.

    Attributes:
        projection_name: Unique name for this projection

    Example:
        ```python
        class TaskCountProjection:
            projection_name = "task_counts"

            async def apply_event(
                self,
                event: ProtocolWorkflowEvent,
                current_state: dict[str, ContextValue]
            ) -> dict[str, ContextValue]:
                if event.event_type == "task_started":
                    current_state["pending"] = current_state.get("pending", 0) + 1
                elif event.event_type == "task_completed":
                    current_state["pending"] = current_state.get("pending", 1) - 1
                    current_state["completed"] = current_state.get("completed", 0) + 1
                return current_state

            async def get_state(
                self, workflow_type: str, instance_id: UUID
            ) -> dict[str, ContextValue]:
                return await load_projection_state(workflow_type, instance_id)

        bus: ProtocolWorkflowEventBus = get_workflow_event_bus()
        await bus.register_projection(TaskCountProjection())
        ```

    See Also:
        - ProtocolWorkflowEventBus: Projection registration
        - ProtocolWorkflowEvent: Events applied to projection
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
    Event bus protocol for workflow-related event publishing and subscription.

    This protocol defines the contract for publishing workflow events
    and subscribing to workflow state changes. Implementations enable
    decoupled communication between workflow components with support for:

    - Event sourcing with sequence numbers for ordering guarantees
    - Workflow instance isolation via partition keys
    - Task coordination messaging between workflow stages
    - State projection updates for CQRS query optimization
    - Recovery and replay support for fault tolerance

    Attributes:
        base_event_bus: Reference to the underlying event bus implementation.

    Example:
        ```python
        class WorkflowEventBusImpl:
            def __init__(self, base_bus: ProtocolEventBus) -> None:
                self._base_bus = base_bus

            @property
            def base_event_bus(self) -> ProtocolEventBus:
                return self._base_bus

            async def publish_workflow_event(
                self,
                event: ProtocolWorkflowEvent,
                target_topic: str | None = None,
                partition_key: str | None = None,
            ) -> None:
                # Publish to workflow-specific topic
                pass

            async def subscribe_to_workflow_events(
                self,
                workflow_type: str,
                event_types: list[LiteralWorkflowEventType] | None = None,
                handler: ProtocolWorkflowEventHandler | None = None,
            ) -> str:
                # Return subscription ID for later unsubscription
                return "subscription-123"

            # ... other method implementations

        bus = WorkflowEventBusImpl(base_bus)
        assert isinstance(bus, ProtocolWorkflowEventBus)

        # Subscribe with handler callback
        subscription_id = await bus.subscribe_to_workflow_events(
            workflow_type="data_processing",
            event_types=["task_started", "task_completed"],
            handler=my_event_handler,
        )

        # Later: unsubscribe when done
        await bus.unsubscribe_from_workflow_events(subscription_id)
        ```

    See Also:
        ProtocolWorkflowEventMessage: Message format for workflow events.
        ProtocolWorkflowEventHandler: Handler for processing workflow events.
        ProtocolLiteralWorkflowStateProjection: State projection for CQRS.
        ProtocolEventBus: Base event bus interface.
    """

    @property
    def base_event_bus(self) -> "ProtocolEventBus": ...

    async def publish_workflow_event(
        self,
        event: "ProtocolWorkflowEvent",
        target_topic: str | None = None,
        partition_key: str | None = None,
    ) -> None: ...

    async def subscribe_to_workflow_events(
        self,
        workflow_type: str,
        event_types: list[LiteralWorkflowEventType] | None = None,
        handler: "ProtocolWorkflowEventHandler | None" = None,
    ) -> str: ...

    async def unsubscribe_from_workflow_events(self, subscription_id: str) -> None: ...

    async def replay_workflow_events(
        self,
        workflow_type: str,
        instance_id: UUID,
        from_sequence: int,
        to_sequence: int | None = None,
        handler: "ProtocolWorkflowEventHandler | None" = None,
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
