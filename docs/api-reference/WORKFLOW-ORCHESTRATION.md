# Workflow Orchestration API Reference

## Overview

The ONEX workflow orchestration protocols provide comprehensive event-driven FSM coordination, event sourcing, workflow state management, and distributed task scheduling. These protocols enable sophisticated workflow orchestration patterns with event sourcing, state projections, and distributed execution.

## 🏗️ Protocol Architecture

The workflow orchestration domain consists of **12 specialized protocols** that provide complete workflow management:

### Workflow Event Bus Protocol

```python
from omnibase_spi.protocols.workflow_orchestration import ProtocolWorkflowEventBus
from omnibase_spi.protocols.types.protocol_workflow_orchestration_types import (
    LiteralWorkflowEventType,
    ProtocolWorkflowEvent,
)

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
    def base_event_bus(self) -> ProtocolEventBus: ...

    async def publish_workflow_event(
        self,
        event: ProtocolWorkflowEvent,
        target_topic: str | None = None,
        partition_key: str | None = None,
    ) -> None: ...

    async def subscribe_to_workflow_events(
        self,
        workflow_type: str,
        event_types: list[LiteralWorkflowEventType] | None = None,
        handler: ProtocolWorkflowEventHandler | None = None,
    ) -> str: ...

    async def unsubscribe_from_workflow_events(self, subscription_id: str) -> None: ...

    async def replay_workflow_events(
        self,
        workflow_type: str,
        instance_id: UUID,
        from_sequence: int,
        to_sequence: int | None = None,
        handler: ProtocolWorkflowEventHandler | None = None,
    ) -> list[ProtocolWorkflowEvent]: ...

    async def register_projection(
        self, projection: ProtocolLiteralWorkflowStateProjection
    ) -> None: ...

    async def unregister_projection(self, projection_name: str) -> None: ...

    async def get_projection_state(
        self, projection_name: str, workflow_type: str, instance_id: UUID
    ) -> dict[str, ContextValue]: ...

    async def create_workflow_topic(
        self, workflow_type: str, partition_count: int
    ) -> bool: ...

    async def delete_workflow_topic(self, workflow_type: str) -> bool: ...
```

### Workflow Event Message Protocol

```python
@runtime_checkable
class ProtocolWorkflowEventMessage(Protocol):
    """
    Protocol for workflow-specific event messages.

    Extends the base event message with workflow orchestration metadata
    for proper event sourcing and workflow coordination.
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
```

### Workflow Event Handler Protocol

```python
@runtime_checkable
class ProtocolWorkflowEventHandler(Protocol):
    """
    Protocol for workflow event handler functions.

    Event handlers process workflow events and update workflow state
    according to event sourcing patterns.
    """

    async def __call__(
        self, event: ProtocolWorkflowEvent, context: dict[str, ContextValue]
    ) -> None: ...
```

### Workflow State Projection Protocol

```python
@runtime_checkable
class ProtocolLiteralWorkflowStateProjection(Protocol):
    """
    Protocol for workflow state projection handlers.

    Projections maintain derived state from workflow events
    for query optimization and real-time monitoring.
    """

    projection_name: str

    async def apply_event(
        self, event: ProtocolWorkflowEvent, current_state: dict[str, ContextValue]
    ) -> dict[str, ContextValue]: ...

    async def get_state(
        self, workflow_type: str, instance_id: UUID
    ) -> dict[str, ContextValue]: ...
```

### Workflow Orchestrator Protocol

```python
@runtime_checkable
class ProtocolWorkflowOrchestrator(Protocol):
    """
    Protocol for workflow orchestration and coordination.

    Manages workflow lifecycle, state transitions, and distributed execution
    across multiple nodes in the ONEX ecosystem.

    Key Features:
        - Workflow lifecycle management
        - State transition coordination
        - Distributed task scheduling
        - Workflow recovery and replay
        - Performance monitoring and optimization
    """

    async def start_workflow(
        self,
        workflow_type: str,
        instance_id: UUID,
        initial_data: dict[str, ContextValue],
        correlation_id: UUID | None = None,
    ) -> ProtocolWorkflowInstance: ...

    async def pause_workflow(
        self, workflow_type: str, instance_id: UUID
    ) -> bool: ...

    async def resume_workflow(
        self, workflow_type: str, instance_id: UUID
    ) -> bool: ...

    async def cancel_workflow(
        self, workflow_type: str, instance_id: UUID, reason: str | None = None
    ) -> bool: ...

    async def get_workflow_state(
        self, workflow_type: str, instance_id: UUID
    ) -> ProtocolWorkflowState: ...

    async def get_workflow_history(
        self, workflow_type: str, instance_id: UUID
    ) -> list[ProtocolWorkflowEvent]: ...

    async def replay_workflow(
        self,
        workflow_type: str,
        instance_id: UUID,
        from_sequence: int,
        to_sequence: int | None = None,
    ) -> list[ProtocolWorkflowEvent]: ...

    async def get_workflow_metrics(
        self, workflow_type: str | None = None
    ) -> ProtocolWorkflowMetrics: ...
```

### Workflow Persistence Protocol

```python
@runtime_checkable
class ProtocolWorkflowPersistence(Protocol):
    """
    Protocol for workflow state persistence and recovery.

    Provides durable storage for workflow state, events, and snapshots
    with support for recovery and replay operations.

    Key Features:
        - Workflow state persistence
        - Event store operations
        - Snapshot management
        - Recovery and replay support
        - Performance optimization
    """

    async def save_workflow_state(
        self,
        workflow_type: str,
        instance_id: UUID,
        state: ProtocolWorkflowState,
    ) -> bool: ...

    async def load_workflow_state(
        self, workflow_type: str, instance_id: UUID
    ) -> ProtocolWorkflowState | None: ...

    async def save_workflow_event(
        self, event: ProtocolWorkflowEvent
    ) -> bool: ...

    async def load_workflow_events(
        self,
        workflow_type: str,
        instance_id: UUID,
        from_sequence: int = 0,
        to_sequence: int | None = None,
    ) -> list[ProtocolWorkflowEvent]: ...

    async def create_snapshot(
        self,
        workflow_type: str,
        instance_id: UUID,
        sequence_number: int,
    ) -> bool: ...

    async def load_snapshot(
        self, workflow_type: str, instance_id: UUID
    ) -> ProtocolWorkflowSnapshot | None: ...

    async def cleanup_old_events(
        self, workflow_type: str, instance_id: UUID, before_sequence: int
    ) -> int: ...
```

### Work Queue Protocol

```python
@runtime_checkable
class ProtocolWorkQueue(Protocol):
    """
    Protocol for distributed work queue management.

    Provides task scheduling, work distribution, and load balancing
    across multiple worker nodes in the ONEX ecosystem.

    Key Features:
        - Task scheduling and prioritization
        - Work distribution and load balancing
        - Task retry and error handling
        - Performance monitoring
        - Queue management and optimization
    """

    async def enqueue_task(
        self,
        task: ProtocolWorkTask,
        priority: LiteralWorkQueuePriority = "normal",
        delay_seconds: int = 0,
    ) -> str: ...

    async def dequeue_task(
        self, worker_id: str, max_tasks: int = 1
    ) -> list[ProtocolWorkTask]: ...

    async def complete_task(
        self, task_id: str, result: dict[str, ContextValue] | None = None
    ) -> bool: ...

    async def fail_task(
        self, task_id: str, error: str, retry_count: int | None = None
    ) -> bool: ...

    async def get_task_status(self, task_id: str) -> ProtocolTaskStatus: ...

    async def get_queue_metrics(self) -> ProtocolQueueMetrics: ...

    async def pause_queue(self, queue_name: str) -> bool: ...

    async def resume_queue(self, queue_name: str) -> bool: ...

    async def get_queue_status(self, queue_name: str) -> ProtocolQueueStatus: ...
```

### Workflow Node Registry Protocol

```python
@runtime_checkable
class ProtocolWorkflowNodeRegistry(Protocol):
    """
    Protocol for workflow node registration and discovery.

    Manages workflow node capabilities, registration, and discovery
    for distributed workflow execution.

    Key Features:
        - Node registration and discovery
        - Capability management
        - Load balancing and failover
        - Health monitoring
        - Performance tracking
    """

    async def register_node(
        self,
        node_info: ProtocolWorkflowNodeInfo,
        capabilities: list[ProtocolWorkflowNodeCapability],
    ) -> str: ...

    async def unregister_node(self, node_id: str) -> bool: ...

    async def discover_nodes(
        self,
        capability: str | None = None,
        healthy_only: bool = True,
    ) -> list[ProtocolWorkflowNodeInfo]: ...

    async def get_node_capabilities(
        self, node_id: str
    ) -> list[ProtocolWorkflowNodeCapability]: ...

    async def update_node_health(
        self, node_id: str, health_status: LiteralHealthStatus
    ) -> bool: ...

    async def get_node_metrics(self, node_id: str) -> ProtocolNodeMetrics: ...

    async def assign_workflow_to_node(
        self, workflow_type: str, instance_id: UUID, node_id: str
    ) -> bool: ...

    async def get_workflow_assignments(
        self, node_id: str
    ) -> list[ProtocolWorkflowAssignment]: ...
```

## 🧩 ONEX Node Protocols

The ONEX framework defines four specialized node types for distributed workflow execution. Each node type has a specific responsibility in the workflow execution pipeline:

### Effect Node Protocol

```python
from omnibase_spi.protocols.onex import ProtocolEffectNode

@runtime_checkable
class ProtocolEffectNode(Protocol):
    """
    Protocol for ONEX effect node implementations.

    Effect nodes perform side-effecting operations such as I/O, external API calls,
    database operations, file system access, and other interactions with external
    systems. They encapsulate all operations that have observable effects outside
    the workflow's computational context.

    Key Responsibilities:
        - External API and service integration
        - Database read/write operations
        - File system operations
        - Message queue publishing
        - Network requests and responses
        - Third-party service interactions
    """

    async def execute_effect(self, contract: Any) -> Any: ...

    @property
    def node_id(self) -> str: ...

    @property
    def node_type(self) -> str: ...
```

### Compute Node Protocol

```python
from omnibase_spi.protocols.onex import ProtocolComputeNode

@runtime_checkable
class ProtocolComputeNode(Protocol):
    """
    Protocol for ONEX compute node implementations.

    Compute nodes perform pure computational transformations without side effects.
    They implement algorithms, data transformations, business logic, and
    computational operations that produce outputs solely based on their inputs.

    Key Responsibilities:
        - Pure functional transformations
        - Business logic execution
        - Data validation and sanitization
        - Algorithm implementation (sorting, filtering, mapping)
        - Mathematical and statistical computations
        - Data format conversions
    """

    async def execute_compute(self, contract: Any) -> Any: ...

    @property
    def node_id(self) -> str: ...

    @property
    def node_type(self) -> str: ...
```

### Reducer Node Protocol

```python
from omnibase_spi.protocols.onex import ProtocolReducerNode

@runtime_checkable
class ProtocolReducerNode(Protocol):
    """
    Protocol for ONEX reducer node implementations.

    Reducer nodes aggregate and transform data from multiple sources,
    implementing reduction operations that combine, summarize, or synthesize
    outputs from other nodes. They are the final stage in many workflows,
    producing consolidated results.

    Key Responsibilities:
        - Data aggregation from multiple node outputs
        - Result synthesis and transformation
        - State persistence and snapshot creation
        - Final workflow result generation
        - Metrics and summary computation
    """

    async def execute_reduction(self, contract: Any) -> Any: ...

    @property
    def node_id(self) -> str: ...

    @property
    def node_type(self) -> str: ...
```

### Orchestrator Node Protocol

```python
from omnibase_spi.protocols.onex import ProtocolOrchestratorNode

@runtime_checkable
class ProtocolOrchestratorNode(Protocol):
    """
    Protocol for ONEX orchestrator node implementations.

    Orchestrator nodes coordinate workflow execution across multiple nodes,
    managing task distribution, dependency resolution, and workflow state
    transitions. They implement the orchestration logic that drives complex
    multi-node workflows.

    Key Responsibilities:
        - Workflow coordination and task distribution
        - Dependency resolution and execution ordering
        - State management across distributed nodes
        - Error handling and compensation logic
        - Workflow lifecycle management
    """

    async def execute_orchestration(self, contract: Any) -> Any: ...

    @property
    def node_id(self) -> str: ...

    @property
    def node_type(self) -> str: ...
```

### Node Type Usage Example

```python
from omnibase_spi.protocols.onex import (
    ProtocolEffectNode,
    ProtocolComputeNode,
    ProtocolReducerNode,
    ProtocolOrchestratorNode
)

# Effect Node: External API call
class APICallEffect:
    async def execute_effect(self, contract):
        response = await http_client.post(contract.url, data=contract.payload)
        return response

    @property
    def node_id(self) -> str:
        return "effect-api-call-1"

    @property
    def node_type(self) -> str:
        return "effect"

# Compute Node: Data transformation
class DataTransformCompute:
    async def execute_compute(self, contract):
        return transform_data(contract.input_data)

    @property
    def node_id(self) -> str:
        return "compute-transform-1"

    @property
    def node_type(self) -> str:
        return "compute"

# Reducer Node: Result aggregation
class ResultAggregationReducer:
    async def execute_reduction(self, contract):
        return aggregate_results(contract.partial_results)

    @property
    def node_id(self) -> str:
        return "reducer-aggregation-1"

    @property
    def node_type(self) -> str:
        return "reducer"

# Orchestrator Node: Workflow coordination
class WorkflowOrchestrator:
    async def execute_orchestration(self, contract):
        effect_result = await effect_node.execute_effect(contract.effect_contract)
        compute_result = await compute_node.execute_compute(contract.compute_contract)
        final_result = await reducer_node.execute_reduction(contract.reduce_contract)
        return final_result

    @property
    def node_id(self) -> str:
        return "orchestrator-workflow-1"

    @property
    def node_type(self) -> str:
        return "orchestrator"
```

## 🔧 Type Definitions

### Workflow State Types

```python
LiteralWorkflowState = Literal[
    "pending", "running", "completed", "failed", "cancelled", "paused"
]
"""
Workflow execution states.

Values:
    pending: Workflow is waiting to start
    running: Workflow is currently executing
    completed: Workflow finished successfully
    failed: Workflow encountered an error
    cancelled: Workflow was cancelled
    paused: Workflow is temporarily paused
"""

LiteralWorkflowEventType = Literal[
    "started", "completed", "failed", "cancelled", "paused", "resumed", "task_assigned", "task_completed"
]
"""
Workflow event types for event sourcing.

Values:
    started: Workflow execution started
    completed: Workflow execution completed
    failed: Workflow execution failed
    cancelled: Workflow execution cancelled
    paused: Workflow execution paused
    resumed: Workflow execution resumed
    task_assigned: Task assigned to node
    task_completed: Task completed by node
"""

LiteralWorkQueuePriority = Literal["low", "normal", "high", "critical"]
"""
Work queue priority levels.

Values:
    low: Low priority tasks
    normal: Normal priority tasks
    high: High priority tasks
    critical: Critical priority tasks
"""
```

## 🚀 Usage Examples

### Workflow Orchestration

```python
from omnibase_spi.protocols.workflow_orchestration import ProtocolWorkflowOrchestrator

# Initialize orchestrator
orchestrator: ProtocolWorkflowOrchestrator = get_workflow_orchestrator()

# Start workflow
workflow_instance = await orchestrator.start_workflow(
    workflow_type="order-processing",
    instance_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
    initial_data={
        "order_id": "ORD-12345",
        "customer_id": "CUST-67890",
        "amount": 99.99
    },
    correlation_id=UUID("req-abc123")
)

# Get workflow state
state = await orchestrator.get_workflow_state(
    "order-processing",
    UUID("123e4567-e89b-12d3-a456-426614174000")
)
print(f"Workflow state: {state.current_state}")
```

### Event Sourcing

```python
from omnibase_spi.protocols.workflow_orchestration import ProtocolWorkflowEventBus

# Initialize event bus
event_bus: ProtocolWorkflowEventBus = get_workflow_event_bus()

# Publish workflow event
await event_bus.publish_workflow_event(
    event=ProtocolWorkflowEvent(
        workflow_type="order-processing",
        instance_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
        event_type="task_completed",
        sequence_number=5,
        data={"task": "payment_processing", "result": "success"}
    )
)

# Subscribe to workflow events
subscription_id = await event_bus.subscribe_to_workflow_events(
    workflow_type="order-processing",
    event_types=["task_completed", "task_failed"],
    handler=workflow_event_handler
)
```

### Work Queue Management

```python
from omnibase_spi.protocols.workflow_orchestration import ProtocolWorkQueue

# Initialize work queue
work_queue: ProtocolWorkQueue = get_work_queue()

# Enqueue task
task_id = await work_queue.enqueue_task(
    task=ProtocolWorkTask(
        task_type="payment_processing",
        data={"order_id": "ORD-12345", "amount": 99.99}
    ),
    priority="high",
    delay_seconds=0
)

# Dequeue tasks for worker
tasks = await work_queue.dequeue_task(
    worker_id="worker-node-1",
    max_tasks=5
)

# Complete task
await work_queue.complete_task(
    task_id=task_id,
    result={"status": "success", "transaction_id": "TXN-789"}
)
```

### State Projections

```python
from omnibase_spi.protocols.workflow_orchestration import ProtocolLiteralWorkflowStateProjection

# Define projection
class OrderStatusProjection:
    projection_name = "order_status"

    async def apply_event(
        self, event: ProtocolWorkflowEvent, current_state: dict[str, ContextValue]
    ) -> dict[str, ContextValue]:
        if event.event_type == "task_completed":
            return {
                **current_state,
                "last_completed_task": event.data.get("task"),
                "completion_count": current_state.get("completion_count", 0) + 1
            }
        return current_state

    async def get_state(
        self, workflow_type: str, instance_id: UUID
    ) -> dict[str, ContextValue]:
        # Return current projection state
        return await self._load_projection_state(workflow_type, instance_id)

# Register projection
projection = OrderStatusProjection()
await event_bus.register_projection(projection)

# Get projection state
state = await event_bus.get_projection_state(
    "order_status",
    "order-processing",
    UUID("123e4567-e89b-12d3-a456-426614174000")
)
```

### Node Management

```python
from omnibase_spi.protocols.workflow_orchestration import ProtocolWorkflowNodeRegistry

# Initialize node registry
node_registry: ProtocolWorkflowNodeRegistry = get_workflow_node_registry()

# Register node
node_id = await node_registry.register_node(
    node_info=ProtocolWorkflowNodeInfo(
        node_id="worker-node-1",
        node_type="compute",
        host="192.168.1.100",
        port=8080
    ),
    capabilities=[
        ProtocolWorkflowNodeCapability(
            capability_name="payment_processing",
            max_concurrent_tasks=10
        ),
        ProtocolWorkflowNodeCapability(
            capability_name="email_notification",
            max_concurrent_tasks=50
        )
    ]
)

# Discover nodes
nodes = await node_registry.discover_nodes(
    capability="payment_processing",
    healthy_only=True
)

# Assign workflow to node
await node_registry.assign_workflow_to_node(
    "order-processing",
    UUID("123e4567-e89b-12d3-a456-426614174000"),
    "worker-node-1"
)
```

## 🔍 Implementation Notes

### Event Sourcing Patterns

The workflow orchestration protocols support comprehensive event sourcing:

```python
# Event replay for recovery
events = await event_bus.replay_workflow_events(
    workflow_type="order-processing",
    instance_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
    from_sequence=0,
    to_sequence=10
)

# State reconstruction from events
current_state = {}
for event in events:
    current_state = await projection.apply_event(event, current_state)
```

### Workflow Lifecycle Management

Complete workflow lifecycle support:

```python
# Workflow state transitions
await orchestrator.start_workflow("order-processing", instance_id, initial_data)
await orchestrator.pause_workflow("order-processing", instance_id)
await orchestrator.resume_workflow("order-processing", instance_id)
await orchestrator.cancel_workflow("order-processing", instance_id, "User cancelled")
```

### Distributed Task Scheduling

Advanced work queue patterns:

```python
# Priority-based task scheduling
await work_queue.enqueue_task(task, priority="critical")
await work_queue.enqueue_task(task, priority="normal", delay_seconds=300)

# Load balancing across nodes
tasks = await work_queue.dequeue_task("worker-node-1", max_tasks=5)
for task in tasks:
    result = await process_task(task)
    await work_queue.complete_task(task.task_id, result)
```

### Workflow Event Coordinator Protocol

```python
from omnibase_spi.protocols.workflow_orchestration import ProtocolWorkflowEventCoordinator

@runtime_checkable
class ProtocolWorkflowEventCoordinator(Protocol):
    """
    Protocol for Workflow event coordinator tools that manage event-driven
    workflow coordination in ONEX systems.

    These tools handle the coordination of events, triggers, and state
    transitions within workflow execution with strict SPI purity compliance.

    Key Features:
        - Event-driven workflow coordination
        - Event bus integration for publish/subscribe
        - State transition management
        - Event status tracking and monitoring
        - Registry integration for tool access
    """

    def set_registry(self, registry: "ProtocolNodeRegistry") -> None: ...

    def set_event_bus(self, event_bus: "ProtocolEventBus") -> None: ...

    async def run(self, input_state: dict[str, ContextValue]) -> "ProtocolOnexResult": ...

    async def coordinate_events(
        self,
        workflow_events: list["ProtocolWorkflowEvent"],
        scenario_id: str,
        correlation_id: str,
    ) -> "ProtocolOnexResult": ...

    async def publish_workflow_event(
        self,
        event: "ProtocolWorkflowEvent",
        correlation_id: str,
    ) -> "ProtocolOnexResult": ...

    async def subscribe_to_events(
        self,
        event_types: list[str],
        callback: Callable[..., None],
        correlation_id: str,
    ) -> "ProtocolOnexResult": ...

    async def get_event_status(self, event_id: str) -> dict[str, ContextValue] | None: ...

    async def health_check(self) -> dict[str, ContextValue]: ...
```

### Event Coordinator Usage

```python
from omnibase_spi.protocols.workflow_orchestration import ProtocolWorkflowEventCoordinator

# Get coordinator
coordinator: ProtocolWorkflowEventCoordinator = get_workflow_event_coordinator()

# Set up dependencies
coordinator.set_registry(node_registry)
coordinator.set_event_bus(event_bus)

# Create and coordinate workflow events
events = [
    create_workflow_event(
        event_type="task.started",
        workflow_type="order-processing",
        instance_id=uuid4()
    ),
    create_workflow_event(
        event_type="task.completed",
        workflow_type="order-processing",
        instance_id=uuid4()
    )
]

result = await coordinator.coordinate_events(
    workflow_events=events,
    scenario_id="order-flow-001",
    correlation_id=str(uuid4())
)

if result.success:
    print("Events coordinated successfully")
else:
    print(f"Coordination failed: {result.error}")

# Check event status
status = await coordinator.get_event_status("event-123")
if status:
    print(f"Event state: {status['state']}")

# Health check
health = await coordinator.health_check()
print(f"Coordinator health: {health['status']}")
```

## Protocol Statistics

| Metric | Value |
|--------|-------|
| **Total Protocols** | 13 workflow orchestration protocols |
| **ONEX Node Types** | 4 specialized node protocols (Effect, Compute, Reducer, Orchestrator) |
| **Event Sourcing** | Complete event sourcing with sequence numbers and replay |
| **State Management** | Workflow state persistence and projections |
| **Task Scheduling** | Distributed work queue with priority support |
| **Node Management** | Dynamic node registration and capability discovery |
| **Recovery Support** | Workflow recovery and replay capabilities |
| **Event Coordination** | Event-driven workflow coordination with status tracking |
| **Performance Monitoring** | Comprehensive metrics and monitoring |

## See Also

- **[Event Bus](EVENT-BUS.md)** - Base event bus protocols
- **[Developer Guide](../developer-guide/README.md)** - Implementation patterns
- **[Examples](../examples/README.md)** - Working code examples

---

*This API reference documents the workflow orchestration protocols defined in `omnibase_spi`.*
