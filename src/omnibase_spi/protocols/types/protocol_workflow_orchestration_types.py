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

# Explicit re-exports for backward compatibility
__all__ = [
    # Value types (from protocol_workflow_value_types)
    "ProtocolWorkflowValue",
    "ProtocolWorkflowStringValue",
    "ProtocolWorkflowStringListValue",
    "ProtocolWorkflowStringDictValue",
    "ProtocolWorkflowNumericValue",
    "ProtocolWorkflowStructuredValue",
    "ProtocolTypedWorkflowData",
    "T_WorkflowValue",
    # Execution types (from protocol_workflow_execution_types)
    "ProtocolCompensationAction",
    "ProtocolWorkflowDefinition",
    "ProtocolNodeCapability",
    "ProtocolWorkflowServiceInstance",
    "ProtocolRecoveryPoint",
    "ProtocolReplayStrategy",
    "ProtocolEventStream",
    "ProtocolEventProjection",
    "ProtocolHealthCheckResult",
    "ProtocolWorkflowExecutionState",
    # Local protocols
    "ProtocolWorkflowMetadata",
    "ProtocolRetryConfiguration",
    "ProtocolTimeoutConfiguration",
    "ProtocolTaskDependency",
    "ProtocolWorkflowContext",
    "ProtocolTaskConfiguration",
    "ProtocolWorkflowEvent",
    "ProtocolWorkflowSnapshot",
    "ProtocolTaskResult",
    "ProtocolWorkTicket",
    "ProtocolWorkflowInputState",
    "ProtocolWorkflowParameters",
    # Literal types
    "LiteralWorkflowState",
    "LiteralTaskState",
    "LiteralTaskType",
    "LiteralExecutionSemantics",
    "LiteralRetryPolicy",
    "LiteralWorkflowEventType",
    "LiteralTimeoutType",
    "LiteralTaskPriority",
    "LiteralIsolationLevel",
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
    """Protocol for workflow metadata objects."""

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
    """Protocol for timeout configuration objects."""

    timeout_type: LiteralTimeoutType
    timeout_seconds: int
    warning_seconds: int | None
    grace_period_seconds: int | None
    escalation_policy: str | None

    async def validate_timeout_config(self) -> bool: ...

    def is_reasonable(self) -> bool: ...


@runtime_checkable
class ProtocolTaskDependency(Protocol):
    """Protocol for task dependency objects."""

    task_id: UUID
    dependency_type: Literal["hard", "soft", "conditional"]
    condition: str | None
    timeout_seconds: int | None

    async def validate_dependency(self) -> bool: ...

    def is_conditional(self) -> bool: ...


@runtime_checkable
class ProtocolWorkflowContext(Protocol):
    """Protocol for workflow context objects with isolation."""

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
    """Protocol for task configuration objects."""

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
    """Protocol for workflow event objects with event sourcing."""

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
    """Protocol for workflow snapshot objects."""

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
    """Protocol for task execution results."""

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
    """Protocol for work ticket objects."""

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
    Distinct from ProtocolOnexInputState which handles format conversion.
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
    """Protocol for workflow parameters objects."""

    parameters: dict[str, "ContextValue"]
    defaults: dict[str, "ContextValue"]
    required: list[str]
    validation_rules: dict[str, "ContextValue"]

    async def validate_parameters(self) -> bool: ...
