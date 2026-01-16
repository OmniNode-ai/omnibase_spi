"""
Workflow orchestration protocol types for ONEX SPI interfaces.

Domain: Event-driven workflow orchestration with FSM states and event sourcing
"""

from typing import Literal, Protocol, runtime_checkable
from uuid import UUID

from omnibase_spi.protocols.types.protocol_core_types import (
    ContextValue,
    LiteralNodeType,
    ProtocolDateTime,
    ProtocolSemVer,
)

# Re-export execution types for backward compatibility
from omnibase_spi.protocols.types.protocol_workflow_execution_types import (  # noqa: F401
    ProtocolCompensationAction,
    ProtocolEventProjection,
    ProtocolEventStream,
    ProtocolHealthCheckResult,
    ProtocolNodeCapability,
    ProtocolRecoveryPoint,
    ProtocolReplayStrategy,
    ProtocolWorkflowDefinition,
    ProtocolWorkflowExecutionState,
    ProtocolWorkflowServiceInstance,
)

# Re-export value types for backward compatibility
from omnibase_spi.protocols.types.protocol_workflow_value_types import (  # noqa: F401
    LiteralRetryPolicy,
    ProtocolRetryConfiguration,
    ProtocolTypedWorkflowData,
    ProtocolWorkflowNumericValue,
    ProtocolWorkflowStringDictValue,
    ProtocolWorkflowStringListValue,
    ProtocolWorkflowStringValue,
    ProtocolWorkflowStructuredValue,
    ProtocolWorkflowValue,
    T_WorkflowValue,
)

# Explicit re-exports for backward compatibility
__all__ = [
    "LiteralExecutionSemantics",
    "LiteralIsolationLevel",
    "LiteralRetryPolicy",
    "LiteralTaskPriority",
    "LiteralTaskState",
    "LiteralTaskType",
    "LiteralTimeoutType",
    "LiteralWorkflowEventType",
    # Literal types
    "LiteralWorkflowState",
    # Execution types (from protocol_workflow_execution_types)
    "ProtocolCompensationAction",
    "ProtocolEventProjection",
    "ProtocolEventStream",
    "ProtocolHealthCheckResult",
    "ProtocolNodeCapability",
    "ProtocolRecoveryPoint",
    "ProtocolReplayStrategy",
    "ProtocolRetryConfiguration",
    "ProtocolTaskConfiguration",
    "ProtocolTaskDependency",
    "ProtocolTaskResult",
    "ProtocolTimeoutConfiguration",
    "ProtocolTypedWorkflowData",
    "ProtocolWorkTicket",
    "ProtocolWorkflowContext",
    "ProtocolWorkflowDefinition",
    "ProtocolWorkflowEvent",
    "ProtocolWorkflowExecutionState",
    "ProtocolWorkflowInputState",
    # Local protocols
    "ProtocolWorkflowMetadata",
    "ProtocolWorkflowNumericValue",
    "ProtocolWorkflowParameters",
    "ProtocolWorkflowServiceInstance",
    "ProtocolWorkflowSnapshot",
    "ProtocolWorkflowStringDictValue",
    "ProtocolWorkflowStringListValue",
    "ProtocolWorkflowStringValue",
    "ProtocolWorkflowStructuredValue",
    # Value types (from protocol_workflow_value_types)
    "ProtocolWorkflowValue",
    "T_WorkflowValue",
]

# Literal type aliases for workflow states and events
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
LiteralTaskState = Literal[
    "pending",
    "scheduled",
    "running",
    "completed",
    "failed",
    "cancelled",
    "timeout",
    "retrying",
    "skipped",
    "waiting_for_input",
    "blocked",
]
LiteralTaskType = Literal["compute", "effect", "orchestrator", "reducer"]
LiteralExecutionSemantics = Literal["await", "fire_and_forget", "async_await"]
# LiteralRetryPolicy is imported from protocol_workflow_value_types
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
LiteralTimeoutType = Literal["execution", "idle", "total", "heartbeat"]
LiteralTaskPriority = Literal["low", "normal", "high", "critical", "urgent"]
LiteralIsolationLevel = Literal[
    "read_uncommitted", "read_committed", "repeatable_read", "serializable"
]


@runtime_checkable
class ProtocolWorkflowMetadata(Protocol):
    """
    Protocol for workflow metadata providing identification and context information.

    Contains essential metadata about a workflow instance including type,
    identifiers, ownership, environment context, and versioning information.
    Used for workflow tracking, correlation, and auditing across the system.

    Attributes:
        workflow_type: Type identifier for the workflow (e.g., "data-pipeline").
        instance_id: Unique identifier for this workflow instance.
        correlation_id: ID for correlating related workflows and events.
        created_by: User or service that created this workflow.
        environment: Deployment environment (e.g., "production", "staging").
        group: Logical grouping or namespace for the workflow.
        version: Semantic version of the workflow definition.
        tags: Key-value tags for categorization and filtering.
        metadata: Additional custom metadata.

    Example:
        ```python
        class WorkflowMeta:
            '''Metadata for data processing workflow.'''
            workflow_type: str = "data-pipeline"
            instance_id: UUID = uuid4()
            correlation_id: UUID = uuid4()
            created_by: str = "scheduler-service"
            environment: str = "production"
            group: str = "analytics"
            version: ProtocolSemVer = SemVer(2, 1, 0)
            tags: dict[str, ContextValue] = {"priority": "high"}
            metadata: dict[str, ContextValue] = {}

            async def validate_metadata(self) -> bool:
                return bool(self.workflow_type and self.instance_id)

            def is_complete(self) -> bool:
                return bool(self.created_by and self.environment)

        obj = WorkflowMeta()
        assert isinstance(obj, ProtocolWorkflowMetadata)
        ```
    """

    workflow_type: str
    instance_id: UUID
    correlation_id: UUID
    created_by: str
    environment: str
    group: str
    version: "ProtocolSemVer"
    tags: dict[str, "ContextValue"]
    metadata: dict[str, "ContextValue"]

    async def validate_metadata(self) -> bool: ...

    def is_complete(self) -> bool: ...


# ProtocolRetryConfiguration is imported from protocol_workflow_value_types


@runtime_checkable
class ProtocolTimeoutConfiguration(Protocol):
    """
    Protocol for timeout configuration defining time-based execution limits.

    Specifies timeout parameters for workflow and task execution including
    the timeout type, duration, warning thresholds, and escalation policies.
    Used to ensure workflows complete within acceptable time bounds.

    Attributes:
        timeout_type: Type of timeout (execution, idle, total, heartbeat).
        timeout_seconds: Maximum allowed time in seconds.
        warning_seconds: Time before timeout to issue warnings.
        grace_period_seconds: Additional time after timeout before termination.
        escalation_policy: Policy name for timeout escalation handling.

    Example:
        ```python
        class TimeoutConfig:
            '''Timeout configuration for long-running tasks.'''
            timeout_type: LiteralTimeoutType = "execution"
            timeout_seconds: int = 3600
            warning_seconds: int | None = 3000
            grace_period_seconds: int | None = 60
            escalation_policy: str | None = "notify-oncall"

            async def validate_timeout_config(self) -> bool:
                return self.timeout_seconds > 0

            def is_reasonable(self) -> bool:
                return self.timeout_seconds <= 86400  # Max 24 hours

        obj = TimeoutConfig()
        assert isinstance(obj, ProtocolTimeoutConfiguration)
        ```
    """

    timeout_type: LiteralTimeoutType
    timeout_seconds: int
    warning_seconds: int | None
    grace_period_seconds: int | None
    escalation_policy: str | None

    async def validate_timeout_config(self) -> bool: ...

    def is_reasonable(self) -> bool: ...


@runtime_checkable
class ProtocolTaskDependency(Protocol):
    """
    Protocol for task dependency defining relationships between workflow tasks.

    Specifies a dependency relationship between tasks including the type
    of dependency (hard, soft, conditional) and any conditions that must
    be met. Used for task scheduling and execution ordering.

    Attributes:
        task_id: UUID of the task this dependency refers to.
        dependency_type: Type of dependency (hard requires completion, soft is optional).
        condition: Optional condition expression for conditional dependencies.
        timeout_seconds: Maximum time to wait for dependency resolution.

    Example:
        ```python
        class TaskDep:
            '''Dependency on data extraction task.'''
            task_id: UUID = uuid4()
            dependency_type: Literal["hard", "soft", "conditional"] = "hard"
            condition: str | None = None
            timeout_seconds: int | None = 300

            async def validate_dependency(self) -> bool:
                return bool(self.task_id)

            def is_conditional(self) -> bool:
                return self.dependency_type == "conditional"

        obj = TaskDep()
        assert isinstance(obj, ProtocolTaskDependency)
        ```
    """

    task_id: UUID
    dependency_type: Literal["hard", "soft", "conditional"]
    condition: str | None
    timeout_seconds: int | None

    async def validate_dependency(self) -> bool: ...

    def is_conditional(self) -> bool: ...


@runtime_checkable
class ProtocolWorkflowContext(Protocol):
    """
    Protocol for workflow context providing execution environment and data isolation.

    Contains the complete execution context for a workflow including data,
    secrets, capabilities, and resource limits. Supports transaction isolation
    levels for concurrent workflow execution safety.

    Attributes:
        workflow_type: Type identifier for the workflow.
        instance_id: Unique identifier for this workflow instance.
        correlation_id: ID for correlating related workflows and events.
        isolation_level: Transaction isolation level for data access.
        data: Workflow data values accessible to tasks.
        secrets: Sensitive values with restricted access.
        capabilities: List of capabilities available to the workflow.
        resource_limits: Resource constraints (memory, cpu, etc.).

    Example:
        ```python
        class WorkflowCtx:
            '''Context for data processing workflow.'''
            workflow_type: str = "data-pipeline"
            instance_id: UUID = uuid4()
            correlation_id: UUID = uuid4()
            isolation_level: LiteralIsolationLevel = "read_committed"
            data: dict[str, ProtocolWorkflowValue] = {}
            secrets: dict[str, ContextValue] = {}
            capabilities: list[str] = ["read_database", "write_s3"]
            resource_limits: dict[str, int] = {"memory_mb": 1024}

            async def validate_context(self) -> bool:
                return bool(self.workflow_type and self.instance_id)

            def has_required_data(self) -> bool:
                return len(self.data) > 0

        obj = WorkflowCtx()
        assert isinstance(obj, ProtocolWorkflowContext)
        ```
    """

    workflow_type: str
    instance_id: UUID
    correlation_id: UUID
    isolation_level: LiteralIsolationLevel
    data: dict[str, "ProtocolWorkflowValue"]
    secrets: dict[str, "ContextValue"]
    capabilities: list[str]
    resource_limits: dict[str, int]

    async def validate_context(self) -> bool: ...

    def has_required_data(self) -> bool: ...


@runtime_checkable
class ProtocolTaskConfiguration(Protocol):
    """
    Protocol for task configuration defining complete task execution parameters.

    Specifies all configuration needed to execute a workflow task including
    identity, type, execution semantics, dependencies, retry and timeout
    behavior, and resource requirements.

    Attributes:
        task_id: Unique identifier for this task.
        task_name: Human-readable name for the task.
        task_type: Type of task (compute, effect, orchestrator, reducer).
        node_type: ONEX node type that implements this task.
        execution_semantics: How task execution is handled (await, fire_and_forget).
        priority: Task priority level for scheduling.
        dependencies: List of task dependencies that must complete first.
        retry_config: Retry configuration for failed attempts.
        timeout_config: Timeout configuration for execution limits.
        resource_requirements: Required resources for task execution.
        annotations: Additional task annotations and metadata.

    Example:
        ```python
        class TaskConfig:
            '''Configuration for data transformation task.'''
            task_id: UUID = uuid4()
            task_name: str = "transform-data"
            task_type: LiteralTaskType = "compute"
            node_type: LiteralNodeType = "compute"
            execution_semantics: LiteralExecutionSemantics = "await"
            priority: LiteralTaskPriority = "normal"
            dependencies: list[ProtocolTaskDependency] = []
            retry_config: ProtocolRetryConfiguration = retry_cfg
            timeout_config: ProtocolTimeoutConfiguration = timeout_cfg
            resource_requirements: dict[str, ContextValue] = {}
            annotations: dict[str, ContextValue] = {}

            async def validate_task(self) -> bool:
                return bool(self.task_id and self.task_name)

            def has_valid_dependencies(self) -> bool:
                return all(d.task_id for d in self.dependencies)

        obj = TaskConfig()
        assert isinstance(obj, ProtocolTaskConfiguration)
        ```
    """

    task_id: UUID
    task_name: str
    task_type: LiteralTaskType
    node_type: LiteralNodeType
    execution_semantics: LiteralExecutionSemantics
    priority: LiteralTaskPriority
    dependencies: list["ProtocolTaskDependency"]
    retry_config: "ProtocolRetryConfiguration"
    timeout_config: "ProtocolTimeoutConfiguration"
    resource_requirements: dict[str, ContextValue]
    annotations: dict[str, "ContextValue"]

    async def validate_task(self) -> bool: ...

    def has_valid_dependencies(self) -> bool: ...


@runtime_checkable
class ProtocolWorkflowEvent(Protocol):
    """
    Protocol for workflow events supporting event sourcing and audit trails.

    Represents an immutable event in the workflow lifecycle with full
    traceability including sequence numbers, causation tracking, and
    correlation chains. Used for event sourcing, replay, and auditing.

    Attributes:
        event_id: Unique identifier for this event.
        event_type: Type of workflow event (e.g., "workflow.started").
        workflow_type: Type of the workflow this event belongs to.
        instance_id: ID of the workflow instance.
        correlation_id: Correlation ID for distributed tracing.
        sequence_number: Monotonically increasing sequence number.
        timestamp: When the event occurred.
        source: Service or component that generated the event.
        idempotency_key: Key for ensuring idempotent event processing.
        payload: Event-specific data payload.
        metadata: Additional event metadata.
        causation_id: ID of the event that caused this event.
        correlation_chain: Chain of correlation IDs for tracing.

    Example:
        ```python
        class WorkflowEvent:
            '''Event for workflow completion.'''
            event_id: UUID = uuid4()
            event_type: LiteralWorkflowEventType = "workflow.completed"
            workflow_type: str = "data-pipeline"
            instance_id: UUID = uuid4()
            correlation_id: UUID = uuid4()
            sequence_number: int = 42
            timestamp: ProtocolDateTime = datetime.now()
            source: str = "workflow-engine"
            idempotency_key: str = "wf-12345-completed"
            payload: dict[str, ProtocolWorkflowValue] = {}
            metadata: dict[str, ContextValue] = {}
            causation_id: UUID | None = None
            correlation_chain: list[UUID] = []

            async def validate_event(self) -> bool:
                return bool(self.event_id and self.event_type)

            def is_valid_sequence(self) -> bool:
                return self.sequence_number >= 0

        obj = WorkflowEvent()
        assert isinstance(obj, ProtocolWorkflowEvent)
        ```
    """

    event_id: UUID
    event_type: LiteralWorkflowEventType
    workflow_type: str
    instance_id: UUID
    correlation_id: UUID
    sequence_number: int
    timestamp: "ProtocolDateTime"
    source: str
    idempotency_key: str
    payload: dict[str, "ProtocolWorkflowValue"]
    metadata: dict[str, "ContextValue"]
    causation_id: UUID | None
    correlation_chain: list[UUID]

    async def validate_event(self) -> bool: ...

    def is_valid_sequence(self) -> bool: ...


@runtime_checkable
class ProtocolWorkflowSnapshot(Protocol):
    """
    Protocol for workflow snapshots capturing point-in-time workflow state.

    Provides a complete snapshot of workflow state at a specific sequence
    number for event sourcing recovery, debugging, and state inspection.
    Used to efficiently restore workflow state without replaying all events.

    Attributes:
        workflow_type: Type of the workflow.
        instance_id: ID of the workflow instance.
        sequence_number: Sequence number this snapshot represents.
        state: Current workflow state at this snapshot.
        context: Complete workflow context at snapshot time.
        tasks: List of task configurations in the workflow.
        created_at: When the snapshot was created.
        metadata: Additional snapshot metadata.

    Example:
        ```python
        class Snapshot:
            '''Snapshot of running workflow.'''
            workflow_type: str = "data-pipeline"
            instance_id: UUID = uuid4()
            sequence_number: int = 100
            state: LiteralWorkflowState = "running"
            context: ProtocolWorkflowContext = ctx
            tasks: list[ProtocolTaskConfiguration] = [task1, task2]
            created_at: ProtocolDateTime = datetime.now()
            metadata: dict[str, ContextValue] = {}

            async def validate_snapshot(self) -> bool:
                return self.sequence_number >= 0

            def is_consistent(self) -> bool:
                return bool(self.context and self.tasks)

        obj = Snapshot()
        assert isinstance(obj, ProtocolWorkflowSnapshot)
        ```
    """

    workflow_type: str
    instance_id: UUID
    sequence_number: int
    state: LiteralWorkflowState
    context: "ProtocolWorkflowContext"
    tasks: list["ProtocolTaskConfiguration"]
    created_at: "ProtocolDateTime"
    metadata: dict[str, "ContextValue"]

    async def validate_snapshot(self) -> bool: ...

    def is_consistent(self) -> bool: ...


@runtime_checkable
class ProtocolTaskResult(Protocol):
    """
    Protocol for task execution results capturing complete execution outcome.

    Contains the full result of a task execution including success/failure
    status, output data, error information, performance metrics, and any
    events emitted during execution.

    Attributes:
        task_id: ID of the task that was executed.
        execution_id: Unique ID for this specific execution attempt.
        state: Final state of the task after execution.
        result_data: Output data produced by the task.
        error_message: Error message if task failed.
        error_code: Error code if task failed.
        retry_count: Number of retry attempts made.
        execution_time_seconds: Total execution time in seconds.
        resource_usage: Resource consumption metrics.
        output_artifacts: List of artifact paths produced.
        events_emitted: Workflow events emitted during execution.

    Example:
        ```python
        class TaskRes:
            '''Result from data transformation task.'''
            task_id: UUID = uuid4()
            execution_id: UUID = uuid4()
            state: LiteralTaskState = "completed"
            result_data: dict[str, ProtocolWorkflowValue] = {"rows": 1000}
            error_message: str | None = None
            error_code: str | None = None
            retry_count: int = 0
            execution_time_seconds: float = 45.2
            resource_usage: dict[str, float] = {"memory_mb": 512}
            output_artifacts: list[str] = ["s3://bucket/output.parquet"]
            events_emitted: list[ProtocolWorkflowEvent] = []

            async def validate_result(self) -> bool:
                return bool(self.task_id and self.execution_id)

            def is_success(self) -> bool:
                return self.state == "completed"

        obj = TaskRes()
        assert isinstance(obj, ProtocolTaskResult)
        ```
    """

    task_id: UUID
    execution_id: UUID
    state: LiteralTaskState
    result_data: dict[str, "ProtocolWorkflowValue"]
    error_message: str | None
    error_code: str | None
    retry_count: int
    execution_time_seconds: float
    resource_usage: dict[str, float]
    output_artifacts: list[str]
    events_emitted: list["ProtocolWorkflowEvent"]

    async def validate_result(self) -> bool: ...

    def is_success(self) -> bool: ...


@runtime_checkable
class ProtocolWorkTicket(Protocol):
    """
    Protocol for work tickets representing assignable units of work.

    Represents a discrete unit of work that can be assigned to workers
    or services for processing. Includes priority, assignment tracking,
    timing information, and custom payload data.

    Attributes:
        ticket_id: Unique identifier for the work ticket.
        work_type: Type of work to be performed.
        priority: Priority level for scheduling.
        status: Current status of the ticket.
        assigned_to: Worker or service the ticket is assigned to.
        created_at: When the ticket was created.
        due_at: Optional deadline for completion.
        completed_at: When the ticket was completed.
        payload: Work-specific data and parameters.
        metadata: Additional ticket metadata.

    Example:
        ```python
        class WorkTicket:
            '''Work ticket for data export job.'''
            ticket_id: str = "ticket-12345"
            work_type: str = "data-export"
            priority: LiteralTaskPriority = "high"
            status: Literal["pending", "assigned", "in_progress",
                           "completed", "failed"] = "pending"
            assigned_to: str | None = None
            created_at: ProtocolDateTime = datetime.now()
            due_at: ProtocolDateTime | None = datetime.now() + timedelta(hours=1)
            completed_at: ProtocolDateTime | None = None
            payload: dict[str, ContextValue] = {"format": "csv"}
            metadata: dict[str, ContextValue] = {}

            async def validate_work_ticket(self) -> bool:
                return bool(self.ticket_id and self.work_type)

            def is_overdue(self) -> bool:
                return self.due_at is not None and datetime.now() > self.due_at

        obj = WorkTicket()
        assert isinstance(obj, ProtocolWorkTicket)
        ```
    """

    ticket_id: str
    work_type: str
    priority: LiteralTaskPriority
    status: Literal["pending", "assigned", "in_progress", "completed", "failed"]
    assigned_to: str | None
    created_at: "ProtocolDateTime"
    due_at: "ProtocolDateTime | None"
    completed_at: "ProtocolDateTime | None"
    payload: dict[str, "ContextValue"]
    metadata: dict[str, "ContextValue"]

    async def validate_work_ticket(self) -> bool: ...

    def is_overdue(self) -> bool: ...


@runtime_checkable
class ProtocolWorkflowInputState(Protocol):
    """
    Protocol for workflow input state objects.

    Used for workflow orchestration input data and parameters.
    Distinct from ProtocolInputState which handles format conversion.
    """

    workflow_type: str
    input_data: dict[str, "ContextValue"]
    parameters: dict[str, "ContextValue"]
    metadata: dict[str, "ContextValue"]

    async def validate_workflow_input(self) -> bool:
        """
        Validate workflow input state for orchestration.

        Returns:
            True if workflow_type, input_data, and parameters are valid
        """
        ...


@runtime_checkable
class ProtocolWorkflowParameters(Protocol):
    """
    Protocol for workflow parameters defining input configuration and validation.

    Specifies the parameters a workflow accepts including default values,
    required parameters, and validation rules. Used for workflow configuration
    and input validation before execution.

    Attributes:
        parameters: Current parameter values.
        defaults: Default values for parameters.
        required: List of required parameter names.
        validation_rules: Validation rules by parameter name.

    Example:
        ```python
        class WorkflowParams:
            '''Parameters for data pipeline workflow.'''
            parameters: dict[str, ContextValue] = {
                "source_table": "users",
                "batch_size": 1000
            }
            defaults: dict[str, ContextValue] = {"batch_size": 100}
            required: list[str] = ["source_table"]
            validation_rules: dict[str, ContextValue] = {
                "batch_size": {"min": 1, "max": 10000}
            }

            async def validate_parameters(self) -> bool:
                return all(r in self.parameters for r in self.required)

        obj = WorkflowParams()
        assert isinstance(obj, ProtocolWorkflowParameters)
        ```
    """

    parameters: dict[str, "ContextValue"]
    defaults: dict[str, "ContextValue"]
    required: list[str]
    validation_rules: dict[str, "ContextValue"]

    async def validate_parameters(self) -> bool: ...
