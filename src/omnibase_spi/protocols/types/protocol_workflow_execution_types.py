"""
Workflow execution protocol types for ONEX SPI interfaces.

Domain: Execution state, recovery, replay, and service discovery for workflow orchestration.
"""

from typing import Literal, Protocol, runtime_checkable
from uuid import UUID

from omnibase_spi.protocols.types.protocol_core_types import (
    ContextValue,
    LiteralNodeType,
    ProtocolDateTime,
    ProtocolSemVer,
)
from omnibase_spi.protocols.types.protocol_workflow_value_types import (
    ProtocolRetryConfiguration,
    ProtocolWorkflowValue,
)

# Literal type aliases needed for this module
LiteralTaskType = Literal["compute", "effect", "orchestrator", "reducer"]
LiteralWorkflowState = Literal[
    "pending",
    "initializing",
    "running",
    "paused",
    "completed",
    "failed",
    "cancelled",
    "timeout",
    "retrying",
    "waiting_for_dependency",
    "compensating",
    "compensated",
]
LiteralWorkflowEventType = Literal[
    "workflow.created",
    "workflow.started",
    "workflow.paused",
    "workflow.resumed",
    "workflow.completed",
    "workflow.failed",
    "workflow.cancelled",
    "workflow.timeout",
    "task.scheduled",
    "task.started",
    "task.completed",
    "task.failed",
    "task.retry",
    "dependency.resolved",
    "dependency.failed",
    "state.transitioned",
    "compensation.started",
    "compensation.completed",
]


@runtime_checkable
class ProtocolCompensationAction(Protocol):
    """
    Protocol for compensation action objects.

    Defines compensation actions for workflow rollback and error recovery.
    Implements the saga pattern for distributed transactions, allowing
    workflows to undo completed steps when failures occur.

    Attributes:
        compensation_id: Unique identifier for this compensation action.
        task_id: ID of the task being compensated.
        action_type: Type of compensation (rollback, cleanup, notify, custom).
        action_data: Data required to execute the compensation.
        timeout_seconds: Maximum time allowed for compensation.
        retry_config: Retry configuration for compensation attempts.

    Example:
        ```python
        class OrderRollbackAction:
            '''Compensation action to rollback an order.'''

            compensation_id = UUID("550e8400-e29b-41d4-a716-446655440000")
            task_id = UUID("660e8400-e29b-41d4-a716-446655440001")
            action_type = "rollback"
            action_data = {"order_id": "ORD-123", "reason": "payment_failed"}
            timeout_seconds = 30
            retry_config = RetryConfig(max_attempts=3)

            async def validate_compensation(self) -> bool:
                return self.action_data.get("order_id") is not None

            async def can_execute(self) -> bool:
                return self.action_type in ["rollback", "cleanup", "notify"]

        action = OrderRollbackAction()
        assert isinstance(action, ProtocolCompensationAction)
        ```
    """

    compensation_id: UUID
    task_id: UUID
    action_type: Literal["rollback", "cleanup", "notify", "custom"]
    action_data: dict[str, "ProtocolWorkflowValue"]
    timeout_seconds: int
    retry_config: "ProtocolRetryConfiguration"

    async def validate_compensation(self) -> bool: ...

    async def can_execute(self) -> bool: ...


@runtime_checkable
class ProtocolWorkflowDefinition(Protocol):
    """
    Protocol for workflow definition objects.

    Defines the complete specification for a workflow including its tasks,
    error handling, and validation rules. Used as the blueprint for
    creating workflow instances in the orchestration system.

    Attributes:
        workflow_type: Unique type identifier for this workflow.
        version: Semantic version of the workflow definition.
        name: Human-readable workflow name.
        description: Detailed description of the workflow purpose.
        tasks: List of task configurations in execution order.
        default_retry_config: Default retry settings for tasks.
        default_timeout_config: Default timeout settings for tasks.
        compensation_actions: Actions to execute on workflow failure.
        validation_rules: Rules for validating workflow inputs.
        schema: JSON schema for workflow input/output.

    Example:
        ```python
        class OrderProcessingWorkflow:
            '''Workflow definition for order processing.'''

            workflow_type = "order_processing"
            version = SemVer(1, 0, 0)
            name = "Order Processing Workflow"
            description = "Handles order validation, payment, and fulfillment"
            tasks = [ValidateOrderTask(), ProcessPaymentTask(), FulfillOrderTask()]
            default_retry_config = RetryConfig(max_attempts=3)
            default_timeout_config = TimeoutConfig(timeout_seconds=300)
            compensation_actions = [RefundPaymentAction(), CancelOrderAction()]
            validation_rules = {"order_id": "required", "amount": "positive"}
            schema = {"type": "object", "properties": {"order_id": {}}}

            async def validate_definition(self) -> bool:
                return len(self.tasks) > 0

            def is_valid_schema(self) -> bool:
                return "type" in self.schema

        workflow_def = OrderProcessingWorkflow()
        assert isinstance(workflow_def, ProtocolWorkflowDefinition)
        ```
    """

    workflow_type: str
    version: "ProtocolSemVer"
    name: str
    description: str
    tasks: list[object]  # Forward reference to ProtocolTaskConfiguration
    default_retry_config: "ProtocolRetryConfiguration"
    default_timeout_config: object  # Forward reference to ProtocolTimeoutConfiguration
    compensation_actions: list["ProtocolCompensationAction"]
    validation_rules: dict[str, ContextValue]
    schema: dict[str, ContextValue]

    async def validate_definition(self) -> bool: ...

    def is_valid_schema(self) -> bool: ...


@runtime_checkable
class ProtocolNodeCapability(Protocol):
    """
    Protocol for node capability objects.

    Describes the capabilities and requirements of a node in the ONEX
    distributed system. Used for capability-based task routing and
    resource allocation decisions.

    Attributes:
        capability_name: Unique name for this capability.
        version: Version of the capability implementation.
        node_types: Node types that support this capability.
        resource_requirements: CPU, memory, and other resource needs.
        configuration_schema: Schema for capability configuration.
        supported_task_types: Task types this capability can handle.

    Example:
        ```python
        class GPUComputeCapability:
            '''GPU-accelerated compute capability.'''

            capability_name = "gpu_compute"
            version = SemVer(1, 0, 0)
            node_types = ["COMPUTE"]
            resource_requirements = {"gpu_memory_gb": 8, "cuda_version": "11.0"}
            configuration_schema = {"type": "object", "properties": {"precision": {}}}
            supported_task_types = ["compute"]

            async def validate_capability(self) -> bool:
                return len(self.node_types) > 0

            def is_supported(self) -> bool:
                return True

        capability = GPUComputeCapability()
        assert isinstance(capability, ProtocolNodeCapability)
        ```
    """

    capability_name: str
    version: "ProtocolSemVer"
    node_types: list[LiteralNodeType]
    resource_requirements: dict[str, ContextValue]
    configuration_schema: dict[str, ContextValue]
    supported_task_types: list[LiteralTaskType]

    async def validate_capability(self) -> bool: ...

    def is_supported(self) -> bool: ...


@runtime_checkable
class ProtocolWorkflowServiceInstance(Protocol):
    """
    Protocol for discovered service instance objects in workflow orchestration.

    Represents a running instance of a workflow service with its endpoint,
    capabilities, and health information. Used for service discovery and
    load balancing in the distributed workflow system.

    Attributes:
        service_name: Human-readable name for the service.
        service_type: Type of service (orchestrator, worker, etc.).
        endpoint: Network endpoint URL for the service.
        health_check_url: URL for health check requests.
        metadata: Additional service metadata.
        capabilities: List of capabilities this instance provides.
        last_heartbeat: Timestamp of most recent heartbeat.

    Example:
        ```python
        class WorkerInstance:
            '''A running workflow worker instance.'''

            service_name = "worker-node-01"
            service_type = "worker"
            endpoint = "http://worker-01:8080"
            health_check_url = "http://worker-01:8080/health"
            metadata = {"region": "us-east-1", "zone": "a"}
            capabilities = [ComputeCapability()]
            last_heartbeat = datetime.now()

            async def validate_service_instance(self) -> bool:
                return self.endpoint and self.service_type

            def is_healthy(self) -> bool:
                age = datetime.now() - self.last_heartbeat
                return age.total_seconds() < 30

        instance = WorkerInstance()
        assert isinstance(instance, ProtocolWorkflowServiceInstance)
        ```
    """

    service_name: str
    service_type: str
    endpoint: str
    health_check_url: str
    metadata: dict[str, "ContextValue"]
    capabilities: list["ProtocolNodeCapability"]
    last_heartbeat: "ProtocolDateTime"

    async def validate_service_instance(self) -> bool: ...

    def is_healthy(self) -> bool: ...


@runtime_checkable
class ProtocolRecoveryPoint(Protocol):
    """
    Protocol for recovery point objects.

    Represents a point from which a workflow can be restored, including
    checkpoints, savepoints, and snapshots. Used for fault tolerance and
    workflow recovery in distributed execution environments.

    Attributes:
        recovery_id: Unique identifier for this recovery point.
        workflow_type: Type of the workflow this point belongs to.
        instance_id: UUID of the specific workflow instance.
        sequence_number: Event sequence number at this point.
        state: Workflow state at the recovery point.
        recovery_type: Type of recovery point (checkpoint/savepoint/snapshot).
        created_at: When the recovery point was created.
        metadata: Additional recovery point metadata.

    Example:
        ```python
        class WorkflowCheckpoint:
            '''Checkpoint for workflow recovery.'''

            recovery_id = UUID("550e8400-e29b-41d4-a716-446655440000")
            workflow_type = "order_processing"
            instance_id = UUID("660e8400-e29b-41d4-a716-446655440001")
            sequence_number = 42
            state = "running"
            recovery_type = "checkpoint"
            created_at = datetime.now()
            metadata = {"step": "payment_processing", "attempts": 1}

            async def validate_recovery_point(self) -> bool:
                return self.sequence_number >= 0

            def is_restorable(self) -> bool:
                return self.state in ["running", "paused"]

        checkpoint = WorkflowCheckpoint()
        assert isinstance(checkpoint, ProtocolRecoveryPoint)
        ```
    """

    recovery_id: UUID
    workflow_type: str
    instance_id: UUID
    sequence_number: int
    state: LiteralWorkflowState
    recovery_type: Literal["checkpoint", "savepoint", "snapshot"]
    created_at: "ProtocolDateTime"
    metadata: dict[str, "ContextValue"]

    async def validate_recovery_point(self) -> bool: ...

    def is_restorable(self) -> bool: ...


@runtime_checkable
class ProtocolReplayStrategy(Protocol):
    """
    Protocol for replay strategy objects.

    Defines how workflow events should be replayed for recovery or
    debugging purposes. Supports full, partial, and checkpoint-based
    replay with configurable event filtering.

    Attributes:
        strategy_type: Type of replay (full, partial, from_checkpoint, etc.).
        start_sequence: Starting sequence number for partial replay.
        end_sequence: Ending sequence number for partial replay.
        event_filters: Event types to include/exclude during replay.
        skip_failed_events: Whether to skip previously failed events.
        validate_state: Whether to validate state after each event.

    Example:
        ```python
        class PartialReplayStrategy:
            '''Strategy for replaying events from a checkpoint.'''

            strategy_type = "from_checkpoint"
            start_sequence = 42
            end_sequence = None  # Replay to current
            event_filters = ["task.completed", "task.failed"]
            skip_failed_events = True
            validate_state = True

            async def validate_replay_strategy(self) -> bool:
                if self.strategy_type == "partial":
                    return self.start_sequence is not None
                return True

            def is_executable(self) -> bool:
                return self.strategy_type in ["full", "partial", "from_checkpoint"]

        strategy = PartialReplayStrategy()
        assert isinstance(strategy, ProtocolReplayStrategy)
        ```
    """

    strategy_type: Literal["full", "partial", "from_checkpoint", "from_sequence"]
    start_sequence: int | None
    end_sequence: int | None
    event_filters: list[str]
    skip_failed_events: bool
    validate_state: bool

    async def validate_replay_strategy(self) -> bool: ...

    def is_executable(self) -> bool: ...


# Forward reference for ProtocolWorkflowEvent
@runtime_checkable
class ProtocolWorkflowEventRef(Protocol):
    """
    Forward reference marker for ProtocolWorkflowEvent.

    Provides a minimal interface for referencing workflow events when
    the full ProtocolWorkflowEvent type is not available. Used to break
    circular dependencies in type definitions.

    Attributes:
        event_id: Unique identifier for the workflow event.
        event_type: Type of workflow event from the event type enumeration.

    Example:
        ```python
        class EventReference:
            '''Minimal reference to a workflow event.'''

            event_id = UUID("550e8400-e29b-41d4-a716-446655440000")
            event_type = "task.completed"

        ref = EventReference()
        assert isinstance(ref, ProtocolWorkflowEventRef)
        ```
    """

    event_id: UUID
    event_type: LiteralWorkflowEventType


@runtime_checkable
class ProtocolEventStream(Protocol):
    """
    Protocol for event stream objects.

    Represents a paginated stream of workflow events for a specific
    workflow instance. Used for event sourcing, audit trails, and
    workflow replay operations.

    Attributes:
        stream_id: Unique identifier for this stream.
        workflow_type: Type of workflow the events belong to.
        instance_id: UUID of the specific workflow instance.
        start_sequence: First sequence number in this batch.
        end_sequence: Last sequence number in this batch.
        events: List of events in this batch.
        is_complete: Whether this is the final batch.
        next_token: Pagination token for fetching next batch.

    Example:
        ```python
        class WorkflowEventStream:
            '''Stream of events from a workflow execution.'''

            stream_id = "stream_order_001"
            workflow_type = "order_processing"
            instance_id = UUID("550e8400-e29b-41d4-a716-446655440000")
            start_sequence = 0
            end_sequence = 49
            events = [TaskStartedEvent(), TaskCompletedEvent()]
            is_complete = False
            next_token = "cursor_50"

            async def validate_stream(self) -> bool:
                return self.start_sequence <= self.end_sequence

            async def is_complete_stream(self) -> bool:
                return self.is_complete

        stream = WorkflowEventStream()
        assert isinstance(stream, ProtocolEventStream)
        ```
    """

    stream_id: str
    workflow_type: str
    instance_id: UUID
    start_sequence: int
    end_sequence: int
    events: list[object]  # Forward reference to ProtocolWorkflowEvent
    is_complete: bool
    next_token: str | None

    async def validate_stream(self) -> bool: ...

    async def is_complete_stream(self) -> bool: ...


@runtime_checkable
class ProtocolEventProjection(Protocol):
    """
    Protocol for event projection objects.

    Represents a materialized view of workflow state computed from
    event streams. Used for CQRS read models and derived state
    representations in event-sourced systems.

    Attributes:
        projection_name: Unique name for this projection.
        workflow_type: Type of workflow being projected.
        last_processed_sequence: Most recent event sequence processed.
        projection_data: Current projected state data.
        created_at: When the projection was created.
        updated_at: When the projection was last updated.

    Example:
        ```python
        class OrderSummaryProjection:
            '''Projection of order status from events.'''

            projection_name = "order_summary"
            workflow_type = "order_processing"
            last_processed_sequence = 150
            projection_data = {
                "total_orders": 45,
                "pending_orders": 5,
                "completed_orders": 40
            }
            created_at = datetime.now() - timedelta(days=1)
            updated_at = datetime.now()

            async def validate_projection(self) -> bool:
                return self.last_processed_sequence >= 0

            def is_up_to_date(self) -> bool:
                age = datetime.now() - self.updated_at
                return age.total_seconds() < 60

        projection = OrderSummaryProjection()
        assert isinstance(projection, ProtocolEventProjection)
        ```
    """

    projection_name: str
    workflow_type: str
    last_processed_sequence: int
    projection_data: dict[str, "ProtocolWorkflowValue"]
    created_at: "ProtocolDateTime"
    updated_at: "ProtocolDateTime"

    async def validate_projection(self) -> bool: ...

    def is_up_to_date(self) -> bool: ...


@runtime_checkable
class ProtocolHealthCheckResult(Protocol):
    """
    Protocol for health check result objects.

    Reports the health status of a node in the workflow system including
    response times and error information. Used for monitoring, alerting,
    and load balancing decisions.

    Attributes:
        node_id: Identifier of the checked node.
        node_type: Type of node (COMPUTE, EFFECT, etc.).
        status: Health status (healthy, unhealthy, degraded, unknown).
        timestamp: When the health check was performed.
        response_time_ms: Response latency in milliseconds.
        error_message: Error details if unhealthy.
        metadata: Additional health check metadata.

    Example:
        ```python
        class ComputeNodeHealth:
            '''Health check result for a compute node.'''

            node_id = "compute-node-01"
            node_type = "COMPUTE"
            status = "healthy"
            timestamp = datetime.now()
            response_time_ms = 12.5
            error_message = None
            metadata = {"cpu_usage": 45, "memory_usage": 60}

            async def validate_health_result(self) -> bool:
                return self.node_id and self.node_type

            def is_healthy(self) -> bool:
                return self.status == "healthy"

        health = ComputeNodeHealth()
        assert isinstance(health, ProtocolHealthCheckResult)
        ```
    """

    node_id: str
    node_type: "LiteralNodeType"
    status: Literal["healthy", "unhealthy", "degraded", "unknown"]
    timestamp: "ProtocolDateTime"
    response_time_ms: float | None
    error_message: str | None
    metadata: dict[str, "ContextValue"]

    async def validate_health_result(self) -> bool: ...

    def is_healthy(self) -> bool: ...


@runtime_checkable
class ProtocolWorkflowExecutionState(Protocol):
    """
    Protocol for workflow execution state objects.

    Tracks the current state of a workflow execution including progress,
    timing, and context data. Used for workflow monitoring, resumption,
    and state persistence.

    Attributes:
        workflow_type: Type identifier for the workflow.
        instance_id: UUID of this specific execution instance.
        state: Current workflow state (pending, running, completed, etc.).
        current_step: Index of the current step being executed.
        total_steps: Total number of steps in the workflow.
        started_at: When the workflow execution started.
        updated_at: When the state was last updated.
        context: Execution context data passed between steps.
        execution_metadata: Additional execution metadata.

    Example:
        ```python
        class OrderExecutionState:
            '''Current state of an order processing workflow.'''

            workflow_type = "order_processing"
            instance_id = UUID("550e8400-e29b-41d4-a716-446655440000")
            state = "running"
            current_step = 2
            total_steps = 5
            started_at = datetime.now() - timedelta(minutes=5)
            updated_at = datetime.now()
            context = {"order_id": "ORD-123", "customer_id": "CUST-456"}
            execution_metadata = {"retry_count": 0, "priority": "high"}

            async def validate_execution_state(self) -> bool:
                return self.current_step <= self.total_steps

            def is_completed(self) -> bool:
                return self.state in ["completed", "failed", "cancelled"]

        state = OrderExecutionState()
        assert isinstance(state, ProtocolWorkflowExecutionState)
        ```
    """

    workflow_type: str
    instance_id: UUID
    state: LiteralWorkflowState
    current_step: int
    total_steps: int
    started_at: "ProtocolDateTime"
    updated_at: "ProtocolDateTime"
    context: dict[str, "ContextValue"]
    execution_metadata: dict[str, "ContextValue"]

    async def validate_execution_state(self) -> bool: ...

    def is_completed(self) -> bool: ...
