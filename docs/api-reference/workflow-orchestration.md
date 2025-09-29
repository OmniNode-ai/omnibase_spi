# Workflow Orchestration API Reference

## Overview

Comprehensive protocol interfaces for event-driven workflow orchestration with finite state machines (FSM), event sourcing, and distributed task coordination. These protocols enable robust, scalable workflow management across the ONEX ecosystem.

## Core Concepts

### Event Sourcing Architecture
- **Event Stream**: Complete history of workflow events with sequence numbers
- **State Reconstruction**: Replay events to rebuild workflow state
- **Causation Tracking**: Full causation chains for debugging and audit trails
- **Snapshot Optimization**: Periodic state snapshots for performance

### Workflow Isolation Pattern
- **`{workflowType, instanceId}` Isolation**: Each workflow instance operates independently
- **Namespace Separation**: Workflow types provide logical separation
- **Resource Isolation**: Independent resource allocation per instance
- **State Boundaries**: Clear state boundaries between instances

### Distributed Coordination
- **Node Registry**: Distributed node coordination and capability management
- **Task Distribution**: Intelligent task routing across available nodes
- **Health Monitoring**: Continuous health monitoring with automatic failover
- **Load Balancing**: Dynamic load balancing based on node capabilities

## Type Definitions

### Workflow States

#### `WorkflowState`
```python
WorkflowState = Literal[
    "pending", "initializing", "running", "paused",
    "completed", "failed", "cancelled", "timeout",
    "retrying", "waiting_for_dependency", "compensating", "compensated"
]
```

Hierarchical FSM states for workflow execution.

**States:**
- `pending`: Workflow is queued for execution
- `initializing`: Workflow is being initialized
- `running`: Workflow is actively executing
- `paused`: Workflow execution is temporarily suspended
- `completed`: Workflow finished successfully
- `failed`: Workflow encountered unrecoverable error
- `cancelled`: Workflow was cancelled by user/system
- `timeout`: Workflow exceeded time limits
- `retrying`: Workflow is retrying after failure
- `waiting_for_dependency`: Waiting for external dependencies
- `compensating`: Executing compensation actions (Saga pattern)
- `compensated`: Compensation actions completed

#### `TaskState`
```python
TaskState = Literal[
    "pending", "scheduled", "running", "completed",
    "failed", "cancelled", "skipped", "retrying",
    "waiting_for_dependency", "timeout", "paused"
]
```

Task-level execution states within workflows.

#### `WorkflowEventType`
```python
WorkflowEventType = Literal[
    "workflow.created", "workflow.started", "workflow.completed",
    "workflow.failed", "workflow.cancelled", "workflow.paused",
    "workflow.resumed", "workflow.retrying", "workflow.timeout",
    "task.scheduled", "task.started", "task.completed",
    "task.failed", "task.cancelled", "task.skipped",
    "dependency.resolved", "dependency.failed", "state.transitioned",
    "compensation.started", "compensation.completed", "compensation.failed",
    "resource.allocated", "resource.released", "error.occurred"
]
```

Complete event taxonomy for workflow orchestration.

### Data Types

#### `WorkflowData`
```python
WorkflowData = Union[
    str, int, float, bool,
    list[str],
    dict[str, Union[str, int, float, bool]]
]
```

Type-safe data values allowed in workflow contexts.

#### `TaskType`
```python
TaskType = Literal["compute", "effect", "decision", "wait", "parallel", "sequential"]
```

Task classification for execution strategy.

#### `ExecutionSemantics`
```python
ExecutionSemantics = Literal["at_most_once", "at_least_once", "exactly_once"]
```

Execution guarantees for task processing.

## Protocol Data Structures

### Core Workflow Protocols

#### `ProtocolWorkflowContext`
```python
class ProtocolWorkflowContext(Protocol):
    """Workflow execution context with isolation and security."""

    workflow_type: str
    instance_id: UUID
    correlation_id: UUID
    isolation_level: IsolationLevel
    data: dict[str, WorkflowData]
    secrets: dict[str, str]
    capabilities: list[str]
    resource_limits: dict[str, int]
    timeout_config: ProtocolTimeoutConfiguration
    retry_config: ProtocolRetryConfiguration
```

Complete workflow context defining the execution environment.

**Properties:**
- `workflow_type`: Logical workflow type identifier
- `instance_id`: Unique instance identifier within the workflow type
- `correlation_id`: Request correlation for tracing
- `isolation_level`: Transaction isolation level
- `data`: Workflow-specific data payload
- `secrets`: Encrypted sensitive data
- `capabilities`: Available system capabilities
- `resource_limits`: Resource consumption limits
- `timeout_config`: Timeout configuration
- `retry_config`: Retry behavior configuration

#### `ProtocolWorkflowEvent`
```python
class ProtocolWorkflowEvent(Protocol):
    """Event sourcing event with complete causation tracking."""

    event_id: UUID
    event_type: WorkflowEventType
    workflow_type: str
    instance_id: UUID
    sequence_number: int
    causation_id: Optional[UUID]
    correlation_chain: list[UUID]
    timestamp: ProtocolDateTime
    data: dict[str, WorkflowData]
    metadata: dict[str, str]
    idempotency_key: str
    source_node_id: str
```

Event sourcing event with full traceability.

**Properties:**
- `event_id`: Unique event identifier
- `event_type`: Classification of the event
- `workflow_type`: Target workflow type
- `instance_id`: Target workflow instance
- `sequence_number`: Event order within workflow instance
- `causation_id`: Event that caused this event
- `correlation_chain`: Complete causation chain
- `timestamp`: Event creation time
- `data`: Event-specific data payload
- `metadata`: Additional event metadata
- `idempotency_key`: Key for duplicate prevention
- `source_node_id`: Node that generated the event

#### `ProtocolWorkflowSnapshot`
```python
class ProtocolWorkflowSnapshot(Protocol):
    """Complete workflow state snapshot for persistence."""

    workflow_type: str
    instance_id: UUID
    sequence_number: int
    state: WorkflowState
    context: ProtocolWorkflowContext
    tasks: list[ProtocolTaskConfiguration]
    results: list[ProtocolTaskResult]
    error_history: list[ProtocolErrorInfo]
    compensation_log: list[ProtocolCompensationAction]
    created_at: ProtocolDateTime
    updated_at: ProtocolDateTime
    checkpoint_data: dict[str, WorkflowData]
    resource_usage: dict[str, int]
```

Complete workflow state for persistence and recovery.

### Task Management Protocols

#### `ProtocolTaskConfiguration`
```python
class ProtocolTaskConfiguration(Protocol):
    """Task configuration with dependencies and constraints."""

    task_id: UUID
    task_type: TaskType
    name: str
    description: str
    dependencies: list[ProtocolTaskDependency]
    parameters: dict[str, WorkflowData]
    constraints: dict[str, WorkflowData]
    timeout_config: ProtocolTimeoutConfiguration
    retry_config: ProtocolRetryConfiguration
    execution_semantics: ExecutionSemantics
    priority: TaskPriority
    tags: list[str]
    resource_requirements: dict[str, int]
    node_selector: Optional[dict[str, str]]
```

Complete task definition with execution parameters.

#### `ProtocolTaskResult`
```python
class ProtocolTaskResult(Protocol):
    """Task execution result with comprehensive metadata."""

    task_id: UUID
    execution_id: UUID
    state: TaskState
    result_data: Optional[dict[str, WorkflowData]]
    error: Optional[ProtocolErrorInfo]
    start_time: ProtocolDateTime
    end_time: Optional[ProtocolDateTime]
    duration_ms: Optional[int]
    node_id: str
    resource_usage: dict[str, int]
    metrics: dict[str, float]
    checkpoints: list[dict[str, WorkflowData]]
```

Comprehensive task execution result.

### Configuration Protocols

#### `ProtocolRetryConfiguration`
```python
class ProtocolRetryConfiguration(Protocol):
    """Retry behavior configuration."""

    max_attempts: int
    backoff_strategy: Literal["fixed", "linear", "exponential", "custom"]
    base_delay_ms: int
    max_delay_ms: int
    jitter: bool
    retry_on: list[str]
    stop_on: list[str]
```

Comprehensive retry configuration.

#### `ProtocolTimeoutConfiguration`
```python
class ProtocolTimeoutConfiguration(Protocol):
    """Timeout configuration for different operations."""

    execution_timeout_ms: int
    heartbeat_timeout_ms: int
    response_timeout_ms: int
    cleanup_timeout_ms: int
    grace_period_ms: int
```

Multi-level timeout configuration.

## Core Protocol Interfaces

### Event Bus Protocols

#### `ProtocolWorkflowEventBus`
```python
@runtime_checkable
class ProtocolWorkflowEventBus(Protocol):
    """
    Workflow-specific event bus with event sourcing and orchestration.

    Extends the base event bus with workflow orchestration patterns:
    - Event sourcing with sequence numbers
    - Workflow instance isolation
    - Task coordination messaging
    - State projection updates
    - Recovery and replay support

    Key Features:
        - **Event Sourcing**: Complete event streams with causation tracking
        - **Instance Isolation**: {workflowType, instanceId} isolation pattern
        - **Task Coordination**: Distributed task execution coordination
        - **State Projections**: Real-time state projections for queries
        - **Recovery Support**: Event replay for failure recovery

    Example:
        ```python
        async def coordinate_workflow(event_bus: ProtocolWorkflowEventBus):
            # Subscribe to workflow events
            unsubscribe = await event_bus.subscribe_to_workflow_events(
                workflow_type="data_pipeline",
                event_types=["task.completed", "task.failed"],
                handler=handle_task_completion,
                group_id="orchestrator"
            )

            # Publish workflow event
            event = ProtocolWorkflowEvent(
                event_type="workflow.started",
                workflow_type="data_pipeline",
                instance_id=UUID("..."),
                sequence_number=1,
                # ... other fields
            )
            await event_bus.publish_workflow_event(event)
        ```
    """

    @property
    def base_event_bus(self) -> ProtocolEventBus:
        """Get underlying event bus implementation."""
        ...

    # Event Publishing
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
        metadata: Optional[dict[str, WorkflowData]],
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

    # Event Subscription
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

    # Task Coordination
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

    # Recovery and Replay
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
```

#### `ProtocolWorkflowEventHandler`
```python
@runtime_checkable
class ProtocolWorkflowEventHandler(Protocol):
    """
    Protocol for workflow event handler functions.

    Event handlers process workflow events and update workflow state
    according to event sourcing patterns.
    """

    async def __call__(
        self, event: ProtocolWorkflowEvent, context: dict[str, WorkflowData]
    ) -> None:
        """
        Handle workflow event.

        Args:
            event: Workflow event to process
            context: Processing context and metadata
        """
        ...
```

### Persistence Protocols

#### `ProtocolWorkflowPersistence`
```python
@runtime_checkable
class ProtocolWorkflowPersistence(Protocol):
    """
    Workflow state persistence with event sourcing support.

    Manages workflow state persistence, event storage, and recovery
    operations with ACID guarantees and consistency controls.

    Key Features:
        - **Event Storage**: Persistent event stream storage
        - **State Snapshots**: Periodic state snapshots for performance
        - **ACID Guarantees**: Transactional consistency
        - **Recovery Support**: State reconstruction from events
        - **Query Optimization**: Efficient state queries

    Example:
        ```python
        async def persist_workflow(persistence: ProtocolWorkflowPersistence):
            # Store workflow snapshot
            snapshot = ProtocolWorkflowSnapshot(
                workflow_type="data_pipeline",
                instance_id=UUID("..."),
                state="running",
                # ... other fields
            )
            await persistence.save_workflow_snapshot(snapshot)

            # Store event
            event = ProtocolWorkflowEvent(
                event_type="task.completed",
                # ... event fields
            )
            await persistence.store_workflow_event(event)
        ```
    """

    # Workflow State Management
    async def save_workflow_snapshot(
        self, snapshot: ProtocolWorkflowSnapshot
    ) -> bool:
        """
        Save workflow state snapshot.

        Args:
            snapshot: Complete workflow state snapshot

        Returns:
            True if save successful
        """
        ...

    async def load_workflow_snapshot(
        self, workflow_type: str, instance_id: UUID
    ) -> Optional[ProtocolWorkflowSnapshot]:
        """
        Load workflow state snapshot.

        Args:
            workflow_type: Workflow type identifier
            instance_id: Workflow instance ID

        Returns:
            Workflow snapshot or None if not found
        """
        ...

    async def delete_workflow_snapshot(
        self, workflow_type: str, instance_id: UUID
    ) -> bool:
        """
        Delete workflow state snapshot.

        Args:
            workflow_type: Workflow type identifier
            instance_id: Workflow instance ID

        Returns:
            True if deletion successful
        """
        ...

    # Event Storage
    async def store_workflow_event(
        self, event: ProtocolWorkflowEvent
    ) -> bool:
        """
        Store workflow event in event stream.

        Args:
            event: Workflow event to store

        Returns:
            True if storage successful
        """
        ...

    async def get_workflow_events(
        self,
        workflow_type: str,
        instance_id: UUID,
        from_sequence: int = 0,
        to_sequence: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> list[ProtocolWorkflowEvent]:
        """
        Retrieve workflow events from event stream.

        Args:
            workflow_type: Workflow type identifier
            instance_id: Workflow instance ID
            from_sequence: Starting sequence number
            to_sequence: Ending sequence number (optional)
            limit: Maximum number of events (optional)

        Returns:
            List of workflow events
        """
        ...

    # State Reconstruction
    async def reconstruct_workflow_state(
        self, workflow_type: str, instance_id: UUID, up_to_sequence: Optional[int] = None
    ) -> Optional[ProtocolWorkflowSnapshot]:
        """
        Reconstruct workflow state from events.

        Args:
            workflow_type: Workflow type identifier
            instance_id: Workflow instance ID
            up_to_sequence: Reconstruct up to this sequence number

        Returns:
            Reconstructed workflow state or None
        """
        ...

    # Queries and Analytics
    async def query_workflows(
        self,
        workflow_type: Optional[str] = None,
        state_filter: Optional[list[WorkflowState]] = None,
        created_after: Optional[ProtocolDateTime] = None,
        limit: int = 100,
    ) -> list[ProtocolWorkflowSnapshot]:
        """
        Query workflows with filtering.

        Args:
            workflow_type: Optional workflow type filter
            state_filter: Optional state filter
            created_after: Optional creation time filter
            limit: Maximum results to return

        Returns:
            List of matching workflow snapshots
        """
        ...
```

### Node Registry Protocols

#### `ProtocolWorkflowNodeRegistry`
```python
@runtime_checkable
class ProtocolWorkflowNodeRegistry(Protocol):
    """
    Workflow node registry for distributed coordination.

    Manages workflow execution nodes, capabilities, and task assignment
    with health monitoring and automatic failover support.

    Key Features:
        - **Node Registration**: Register workflow execution capabilities
        - **Capability Matching**: Match tasks to node capabilities
        - **Health Monitoring**: Continuous health monitoring
        - **Load Balancing**: Distribute tasks based on node capacity
        - **Failover Support**: Automatic failover for failed nodes
    """

    # Node Management
    async def register_workflow_node(
        self,
        node_metadata: ProtocolNodeCapability,
        capabilities: list[str],
        capacity_limits: dict[str, int],
    ) -> str:
        """
        Register a workflow execution node.

        Args:
            node_metadata: Node identification and metadata
            capabilities: List of supported capabilities
            capacity_limits: Resource capacity limits

        Returns:
            Node registration ID
        """
        ...

    async def update_node_heartbeat(
        self,
        registration_id: str,
        health_status: HealthStatus,
        current_load: dict[str, int],
        active_tasks: list[UUID],
    ) -> bool:
        """
        Update node heartbeat and status.

        Args:
            registration_id: Node registration ID
            health_status: Current health status
            current_load: Current resource utilization
            active_tasks: List of active task IDs

        Returns:
            True if update successful
        """
        ...

    # Task Assignment
    async def find_capable_nodes(
        self,
        required_capabilities: list[str],
        resource_requirements: dict[str, int],
        exclude_nodes: Optional[list[str]] = None,
    ) -> list[ProtocolServiceDiscovery]:
        """
        Find nodes capable of executing a task.

        Args:
            required_capabilities: Required node capabilities
            resource_requirements: Required resources
            exclude_nodes: Nodes to exclude from search

        Returns:
            List of capable nodes
        """
        ...

    async def assign_task_to_node(
        self,
        task_config: ProtocolTaskConfiguration,
        preferred_node: Optional[str] = None,
    ) -> Optional[str]:
        """
        Assign task to an appropriate node.

        Args:
            task_config: Task configuration and requirements
            preferred_node: Preferred node ID (optional)

        Returns:
            Assigned node ID or None if no nodes available
        """
        ...
```

## Usage Examples

### Basic Workflow Event Handling

```python
from omnibase_spi.protocols.workflow_orchestration import (
    ProtocolWorkflowEventBus,
    ProtocolWorkflowEventHandler
)
from omnibase_spi.protocols.types.workflow_orchestration_types import (
    ProtocolWorkflowEvent
)

class MyWorkflowHandler(ProtocolWorkflowEventHandler):
    async def __call__(
        self,
        event: ProtocolWorkflowEvent,
        context: dict[str, WorkflowData]
    ) -> None:
        if event.event_type == "task.completed":
            await self.handle_task_completion(event)
        elif event.event_type == "task.failed":
            await self.handle_task_failure(event)

    async def handle_task_completion(self, event: ProtocolWorkflowEvent) -> None:
        print(f"Task completed in workflow {event.workflow_type}")

    async def handle_task_failure(self, event: ProtocolWorkflowEvent) -> None:
        print(f"Task failed in workflow {event.workflow_type}")

# Usage
async def setup_workflow_processing(event_bus: ProtocolWorkflowEventBus):
    handler = MyWorkflowHandler()

    # Subscribe to workflow events
    unsubscribe = await event_bus.subscribe_to_workflow_events(
        workflow_type="data_processing_pipeline",
        event_types=["task.completed", "task.failed"],
        handler=handler,
        group_id="workflow_orchestrator"
    )

    # Later, unsubscribe
    await unsubscribe()
```

### Event Sourcing Pattern

```python
from uuid import uuid4
from datetime import datetime
from omnibase_spi.protocols.types.workflow_orchestration_types import (
    ProtocolWorkflowEvent, WorkflowEventType
)

async def create_workflow_event(
    event_type: WorkflowEventType,
    workflow_type: str,
    instance_id: UUID,
    sequence_number: int,
    causation_id: Optional[UUID] = None
) -> ProtocolWorkflowEvent:
    return ProtocolWorkflowEvent(
        event_id=uuid4(),
        event_type=event_type,
        workflow_type=workflow_type,
        instance_id=instance_id,
        sequence_number=sequence_number,
        causation_id=causation_id,
        correlation_chain=[instance_id] if causation_id is None else [causation_id, instance_id],
        timestamp=datetime.now(),
        data={"source": "orchestrator"},
        metadata={"version": "1.0"},
        idempotency_key=f"{workflow_type}-{instance_id}-{sequence_number}",
        source_node_id="orchestrator-001"
    )

# Create and publish event
async def publish_workflow_started(
    event_bus: ProtocolWorkflowEventBus,
    workflow_type: str,
    instance_id: UUID
) -> None:
    event = await create_workflow_event(
        event_type="workflow.started",
        workflow_type=workflow_type,
        instance_id=instance_id,
        sequence_number=1
    )
    await event_bus.publish_workflow_event(event)
```

### State Reconstruction

```python
from omnibase_spi.protocols.workflow_orchestration import ProtocolWorkflowPersistence

async def recover_workflow_state(
    persistence: ProtocolWorkflowPersistence,
    workflow_type: str,
    instance_id: UUID
) -> Optional[ProtocolWorkflowSnapshot]:
    # Try to load latest snapshot
    snapshot = await persistence.load_workflow_snapshot(workflow_type, instance_id)

    if snapshot is None:
        # Reconstruct from events if no snapshot
        snapshot = await persistence.reconstruct_workflow_state(
            workflow_type, instance_id
        )

    return snapshot
```

### Task Coordination

```python
from omnibase_spi.protocols.workflow_orchestration import ProtocolWorkflowNodeRegistry

async def schedule_tasks(
    node_registry: ProtocolWorkflowNodeRegistry,
    tasks: list[ProtocolTaskConfiguration]
) -> dict[UUID, str]:
    """Schedule tasks across available nodes."""
    task_assignments = {}

    for task in tasks:
        # Find capable nodes
        capable_nodes = await node_registry.find_capable_nodes(
            required_capabilities=task.capabilities,
            resource_requirements=task.resource_requirements
        )

        if capable_nodes:
            # Assign to first available node
            assigned_node = await node_registry.assign_task_to_node(task)
            if assigned_node:
                task_assignments[task.task_id] = assigned_node

    return task_assignments
```

## Integration Notes

### Event Sourcing Implementation

```python
class WorkflowEventStore:
    """Example event store implementation."""

    def __init__(self, persistence: ProtocolWorkflowPersistence):
        self.persistence = persistence

    async def append_event(self, event: ProtocolWorkflowEvent) -> None:
        """Append event to stream with idempotency."""
        # Check idempotency
        existing_events = await self.persistence.get_workflow_events(
            event.workflow_type,
            event.instance_id,
            from_sequence=event.sequence_number,
            to_sequence=event.sequence_number
        )

        if not existing_events:
            await self.persistence.store_workflow_event(event)

    async def get_events_since(
        self,
        workflow_type: str,
        instance_id: UUID,
        since_sequence: int
    ) -> list[ProtocolWorkflowEvent]:
        """Get events since sequence number."""
        return await self.persistence.get_workflow_events(
            workflow_type, instance_id, from_sequence=since_sequence + 1
        )
```

### Distributed Task Execution

```python
class DistributedTaskExecutor:
    """Example distributed task executor."""

    def __init__(
        self,
        event_bus: ProtocolWorkflowEventBus,
        node_registry: ProtocolWorkflowNodeRegistry
    ):
        self.event_bus = event_bus
        self.node_registry = node_registry

    async def execute_task(
        self,
        task_config: ProtocolTaskConfiguration,
        workflow_instance: ProtocolWorkflowSnapshot
    ) -> ProtocolTaskResult:
        """Execute task on appropriate node."""
        # Find and assign node
        assigned_node = await self.node_registry.assign_task_to_node(task_config)

        if not assigned_node:
            raise RuntimeError("No nodes available for task execution")

        # Create task started event
        started_event = ProtocolWorkflowEvent(
            event_type="task.started",
            workflow_type=workflow_instance.workflow_type,
            instance_id=workflow_instance.instance_id,
            sequence_number=workflow_instance.sequence_number + 1,
            # ... other fields
        )
        await self.event_bus.publish_workflow_event(started_event)

        # Execute task (implementation specific)
        # This would typically send a message to the assigned node
        # and wait for the result

        # Return task result
        return ProtocolTaskResult(
            task_id=task_config.task_id,
            execution_id=uuid4(),
            state="completed",
            # ... other fields
        )
```

## Best Practices

### Event Design

```python
# Good - Rich event with complete context
event = ProtocolWorkflowEvent(
    event_type="task.completed",
    workflow_type="data_pipeline",
    instance_id=workflow_instance_id,
    sequence_number=next_sequence_number(),
    causation_id=triggering_event_id,
    correlation_chain=build_correlation_chain(triggering_event_id),
    timestamp=datetime.now(),
    data={"task_id": task_id, "result": task_result},
    metadata={"node_id": "worker-001", "duration_ms": 1500},
    idempotency_key=f"task-{task_id}-completed",
    source_node_id="worker-001"
)

# Avoid - Minimal event with missing context
bad_event = ProtocolWorkflowEvent(
    event_type="task.completed",
    workflow_type="data_pipeline",
    instance_id=workflow_instance_id,
    sequence_number=1,  # Missing proper sequencing
    # Missing causation tracking
    # Missing detailed data
)
```

### State Management

```python
# Good - Immutable state updates
def apply_event_to_state(
    current_state: ProtocolWorkflowSnapshot,
    event: ProtocolWorkflowEvent
) -> ProtocolWorkflowSnapshot:
    """Apply event to workflow state immutably."""
    if event.event_type == "task.completed":
        # Create new state with updates
        updated_tasks = [
            task if task.task_id != event.data["task_id"] else
            ProtocolTaskConfiguration(
                **task.__dict__,
                state="completed"
            )
            for task in current_state.tasks
        ]

        return ProtocolWorkflowSnapshot(
            **current_state.__dict__,
            tasks=updated_tasks,
            sequence_number=event.sequence_number,
            updated_at=event.timestamp
        )

    return current_state

# Avoid - Mutable state updates that break event sourcing
def bad_apply_event(state: ProtocolWorkflowSnapshot, event: ProtocolWorkflowEvent):
    # Direct mutation breaks immutability
    state.sequence_number = event.sequence_number
    state.updated_at = event.timestamp
```

### Error Handling

```python
class WorkflowEventProcessor:
    """Example event processor with proper error handling."""

    async def process_event(
        self,
        event: ProtocolWorkflowEvent
    ) -> None:
        try:
            await self._handle_event(event)
        except Exception as e:
            # Create error event for audit trail
            error_event = ProtocolWorkflowEvent(
                event_type="error.occurred",
                workflow_type=event.workflow_type,
                instance_id=event.instance_id,
                sequence_number=event.sequence_number + 1,
                causation_id=event.event_id,
                data={
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "original_event_id": str(event.event_id)
                },
                # ... other fields
            )
            await self.event_bus.publish_workflow_event(error_event)
            raise
```

---

*This documentation covers the complete workflow orchestration protocol suite. For integration with other domains, see the respective API reference sections.*
