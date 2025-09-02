"""
ONEX SPI workflow event bus protocols for distributed orchestration.

These protocols extend the base event bus with workflow-specific
messaging patterns, event sourcing, and orchestration coordination.
"""

from typing import Any, Awaitable, Callable, Optional, Protocol, runtime_checkable
from uuid import UUID

from omnibase.protocols.event_bus.protocol_event_bus import ProtocolEventBus
from omnibase.protocols.types.workflow_orchestration_types import (
    ProtocolWorkflowEvent,
    ProtocolWorkflowSnapshot,
    WorkflowEventType,
    WorkflowState,
)


@runtime_checkable
class ProtocolWorkflowEventMessage(Protocol):
    """
    Protocol for workflow-specific event messages.

    Extends the base event message with workflow orchestration metadata
    for proper event sourcing and workflow coordination.
    """

    # Base event message properties
    topic: str
    key: Optional[bytes]
    value: bytes
    headers: dict[str, Any]
    offset: Optional[str]
    partition: Optional[int]

    # Workflow-specific properties
    workflow_type: str
    instance_id: UUID
    correlation_id: UUID
    sequence_number: int
    event_type: WorkflowEventType
    idempotency_key: str

    async def ack(self) -> None:
        """Acknowledge message processing."""
        ...

    def get_workflow_event(self) -> ProtocolWorkflowEvent:
        """Extract workflow event from message."""
        ...


@runtime_checkable
class ProtocolWorkflowEventHandler(Protocol):
    """
    Protocol for workflow event handler functions.

    Event handlers process workflow events and update workflow state
    according to event sourcing patterns.
    """

    async def __call__(
        self, event: ProtocolWorkflowEvent, context: dict[str, Any]
    ) -> None:
        """
        Handle workflow event.

        Args:
            event: Workflow event to process
            context: Processing context and metadata
        """
        ...


@runtime_checkable
class ProtocolWorkflowStateProjection(Protocol):
    """
    Protocol for workflow state projection handlers.

    Projections maintain derived state from workflow events
    for query optimization and real-time monitoring.
    """

    projection_name: str

    async def apply_event(
        self, event: ProtocolWorkflowEvent, current_state: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Apply event to projection state.

        Args:
            event: Workflow event to apply
            current_state: Current projection state

        Returns:
            Updated projection state
        """
        ...

    async def get_state(self, workflow_type: str, instance_id: UUID) -> dict[str, Any]:
        """
        Get current projection state.

        Args:
            workflow_type: Workflow type identifier
            instance_id: Workflow instance ID

        Returns:
            Current projection state
        """
        ...


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

    Usage Example:
        ```python
        # Implementation example (not part of SPI)
        class WorkflowEventBus:
            def __init__(self, base_event_bus: ProtocolEventBus):
                self.base_bus = base_event_bus
                self.projections: dict[str, ProtocolWorkflowStateProjection] = {}
                self.handlers: dict[WorkflowEventType, list[ProtocolWorkflowEventHandler]] = {}

            async def publish_workflow_event(
                self,
                event: ProtocolWorkflowEvent,
                target_topic: Optional[str] = None
            ) -> None:
                # Serialize event with workflow-specific metadata
                topic = target_topic or f"workflow-{event.workflow_type}"
                key = f"{event.workflow_type}:{event.instance_id}".encode()
                value = event.json().encode()

                headers = {
                    "workflow_type": event.workflow_type,
                    "instance_id": str(event.instance_id),
                    "sequence_number": str(event.sequence_number),
                    "event_type": event.event_type,
                    "idempotency_key": event.idempotency_key
                }

                await self.base_bus.publish(topic, key, value, headers)

            async def subscribe_to_workflow_events(
                self,
                workflow_type: str,
                event_types: list[WorkflowEventType],
                handler: ProtocolWorkflowEventHandler,
                group_id: str
            ) -> Callable[[], Awaitable[None]]:
                # Subscribe to workflow events with filtering
                topic = f"workflow-{workflow_type}"

                async def message_handler(msg: ProtocolEventMessage) -> None:
                    # Convert to workflow event
                    workflow_msg = cast_to_workflow_message(msg)
                    if workflow_msg.event_type in event_types:
                        event = workflow_msg.get_workflow_event()
                        context = {"source_topic": topic, "group_id": group_id}
                        await handler(event, context)
                    await msg.ack()

                return await self.base_bus.subscribe(topic, group_id, message_handler)

            async def coordinate_task_execution(
                self,
                workflow_instance: ProtocolWorkflowSnapshot,
                task_assignments: dict[UUID, str]
            ) -> None:
                # Coordinate task execution across nodes
                for task_id, node_group in task_assignments.items():
                    coordination_event = ProtocolWorkflowEvent(
                        event_type="task.scheduled",
                        workflow_type=workflow_instance.workflow_type,
                        instance_id=workflow_instance.instance_id,
                        correlation_id=workflow_instance.metadata.correlation_id,
                        sequence_number=workflow_instance.sequence_number + 1,
                        source="orchestrator",
                        idempotency_key=f"task-schedule-{task_id}",
                        payload={"task_id": str(task_id), "target_node_group": node_group}
                    )

                    target_topic = f"tasks-{node_group}"
                    await self.publish_workflow_event(coordination_event, target_topic)

        # Usage in application
        workflow_bus: ProtocolWorkflowEventBus = WorkflowEventBus(base_event_bus)

        # Publish workflow event
        workflow_started_event = ProtocolWorkflowEvent(
            event_type="workflow.started",
            workflow_type="user_onboarding",
            instance_id=uuid.uuid4(),
            correlation_id=uuid.uuid4(),
            sequence_number=1,
            source="orchestrator",
            idempotency_key=f"start-{instance_id}",
            payload={"user_id": "user-123", "plan": "premium"}
        )

        await workflow_bus.publish_workflow_event(workflow_started_event)

        # Subscribe to workflow events
        async def handle_workflow_completion(event: ProtocolWorkflowEvent, context: dict[str, Any]):
            print(f"Workflow {event.instance_id} completed: {event.payload}")
            # Update external systems, send notifications, etc.

        unsubscribe = await workflow_bus.subscribe_to_workflow_events(
            workflow_type="user_onboarding",
            event_types=["workflow.completed"],
            handler=handle_workflow_completion,
            group_id="notification-service"
        )

        # Coordinate task execution
        workflow_instance = get_workflow_instance(instance_id)
        task_assignments = {
            task1_id: "compute-group",
            task2_id: "effect-group",
            task3_id: "orchestrator-group"
        }

        await workflow_bus.coordinate_task_execution(workflow_instance, task_assignments)
        ```
    """

    # Base event bus access
    @property
    def base_event_bus(self) -> ProtocolEventBus:
        """Get underlying event bus implementation."""
        ...

    # Workflow event operations
    async def publish_workflow_event(
        self, event: ProtocolWorkflowEvent, target_topic: Optional[str] = None
    ) -> None:
        """
        Publish workflow event to event stream.

        Args:
            event: Workflow event to publish
            target_topic: Optional topic override (default: workflow-{type})
        """
        ...

    async def publish_workflow_state_change(
        self,
        workflow_instance: ProtocolWorkflowSnapshot,
        previous_state: WorkflowState,
        new_state: WorkflowState,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Publish workflow state change event.

        Args:
            workflow_instance: Workflow instance
            previous_state: Previous workflow state
            new_state: New workflow state
            metadata: Additional event metadata
        """
        ...

    # Event subscription and handling
    async def subscribe_to_workflow_events(
        self,
        workflow_type: str,
        event_types: list[WorkflowEventType],
        handler: ProtocolWorkflowEventHandler,
        group_id: str,
    ) -> Callable[[], Awaitable[None]]:
        """
        Subscribe to specific workflow events.

        Args:
            workflow_type: Workflow type to subscribe to
            event_types: Event types to handle
            handler: Event handler function
            group_id: Consumer group ID

        Returns:
            Unsubscribe function
        """
        ...

    async def subscribe_to_all_workflow_events(
        self,
        handler: ProtocolWorkflowEventHandler,
        group_id: str,
        event_type_filter: Optional[list[WorkflowEventType]] = None,
    ) -> Callable[[], Awaitable[None]]:
        """
        Subscribe to all workflow events across types.

        Args:
            handler: Event handler function
            group_id: Consumer group ID
            event_type_filter: Optional event type filter

        Returns:
            Unsubscribe function
        """
        ...

    # Task coordination
    async def coordinate_task_execution(
        self,
        workflow_instance: ProtocolWorkflowSnapshot,
        task_assignments: dict[UUID, str],
    ) -> None:
        """
        Coordinate task execution across node groups.

        Args:
            workflow_instance: Workflow instance to coordinate
            task_assignments: Mapping of task IDs to node groups
        """
        ...

    async def send_task_command(
        self,
        task_id: UUID,
        command: str,
        payload: dict[str, Any],
        target_node_group: str,
        timeout_seconds: Optional[int] = None,
    ) -> None:
        """
        Send command to specific task.

        Args:
            task_id: Target task ID
            command: Command to execute
            payload: Command payload
            target_node_group: Target node group
            timeout_seconds: Command timeout
        """
        ...

    # State projection management
    async def register_projection(
        self, projection: ProtocolWorkflowStateProjection
    ) -> None:
        """
        Register state projection handler.

        Args:
            projection: State projection to register
        """
        ...

    async def update_projections(self, event: ProtocolWorkflowEvent) -> None:
        """
        Update all registered projections with event.

        Args:
            event: Workflow event to apply to projections
        """
        ...

    # Recovery and replay
    async def replay_events(
        self,
        workflow_type: str,
        instance_id: UUID,
        from_sequence: int,
        to_sequence: Optional[int] = None,
        handler: Optional[ProtocolWorkflowEventHandler] = None,
    ) -> list[ProtocolWorkflowEvent]:
        """
        Replay workflow events for recovery.

        Args:
            workflow_type: Workflow type identifier
            instance_id: Workflow instance ID
            from_sequence: Starting sequence number
            to_sequence: Ending sequence number (optional)
            handler: Optional event handler for processing

        Returns:
            List of replayed events
        """
        ...

    async def get_workflow_event_stream(
        self,
        workflow_type: str,
        instance_id: UUID,
        from_sequence: int = 1,
        limit: int = 1000,
    ) -> list[ProtocolWorkflowEvent]:
        """
        Get workflow event stream.

        Args:
            workflow_type: Workflow type identifier
            instance_id: Workflow instance ID
            from_sequence: Starting sequence number
            limit: Maximum events to return

        Returns:
            List of workflow events
        """
        ...

    # Monitoring and metrics
    async def get_workflow_metrics(
        self, workflow_type: Optional[str] = None, time_window_seconds: int = 3600
    ) -> dict[str, Any]:
        """
        Get workflow execution metrics.

        Args:
            workflow_type: Optional workflow type filter
            time_window_seconds: Metrics time window

        Returns:
            Workflow execution metrics
        """
        ...

    async def get_active_workflows(
        self, workflow_type: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """
        Get list of active workflow instances.

        Args:
            workflow_type: Optional workflow type filter

        Returns:
            List of active workflow summaries
        """
        ...
