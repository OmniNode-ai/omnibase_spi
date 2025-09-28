"""
Workflow orchestration protocol types for ONEX SPI interfaces.

Domain: Event-driven workflow orchestration with FSM states and event sourcing
"""

from typing import TYPE_CHECKING, Generic, Literal, Protocol, TypeVar, runtime_checkable
from uuid import UUID

from omnibase_spi.protocols.types.protocol_core_types import (
    ContextValue,
    LiteralNodeType,
    ProtocolDateTime,
    ProtocolSemVer,
)

if TYPE_CHECKING:
    pass


@runtime_checkable
class ProtocolWorkflowValue(Protocol):
    """Protocol for workflow data values supporting serialization and validation."""

    def serialize(self) -> dict[str, object]: ...

    async def validate(self) -> bool: ...

    async def get_type_info(self) -> str: ...


@runtime_checkable
class ProtocolWorkflowStringValue(ProtocolWorkflowValue, Protocol):
    """Protocol for string-based workflow values."""

    value: str

    async def get_string_length(self) -> int: ...

    def is_empty_string(self) -> bool: ...


@runtime_checkable
class ProtocolWorkflowStringListValue(ProtocolWorkflowValue, Protocol):
    """Protocol for string list workflow values."""

    value: list[str]

    async def get_list_length(self) -> int: ...

    def is_empty_list(self) -> bool: ...


@runtime_checkable
class ProtocolWorkflowStringDictValue(ProtocolWorkflowValue, Protocol):
    """Protocol for string dictionary workflow values."""

    value: dict[str, "ContextValue"]

    async def get_dict_keys(self) -> list[str]: ...

    def has_key(self, key: str) -> bool: ...


@runtime_checkable
class ProtocolWorkflowNumericValue(ProtocolWorkflowValue, Protocol):
    """Protocol for numeric workflow values (int or float)."""

    value: int | float

    def is_integer(self) -> bool: ...

    def is_positive(self) -> bool: ...


@runtime_checkable
class ProtocolWorkflowStructuredValue(ProtocolWorkflowValue, Protocol):
    """Protocol for structured workflow values with context data."""

    value: dict[str, "ContextValue"]

    async def get_structure_depth(self) -> int: ...

    def flatten_structure(self) -> dict[str, "ContextValue"]: ...


T_WorkflowValue = TypeVar("T_WorkflowValue", str, int, float, bool)


@runtime_checkable
class ProtocolTypedWorkflowData(Generic[T_WorkflowValue], Protocol):
    """Protocol for strongly typed workflow data values."""

    value: T_WorkflowValue

    async def get_type_name(self) -> str: ...

    def serialize_typed(self) -> dict[str, ContextValue]: ...


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
LiteralRetryPolicy = Literal["none", "fixed", "exponential", "linear", "custom"]
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


@runtime_checkable
class ProtocolRetryConfiguration(Protocol):
    """Protocol for retry configuration objects."""

    policy: LiteralRetryPolicy
    max_attempts: int
    initial_delay_seconds: float
    max_delay_seconds: float
    backoff_multiplier: float
    jitter_enabled: bool
    retryable_errors: list[str]
    non_retryable_errors: list[str]

    async def validate_retry_config(self) -> bool: ...

    def is_valid_policy(self) -> bool: ...


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
class ProtocolCompensationAction(Protocol):
    """Protocol for compensation action objects."""

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
    """Protocol for workflow definition objects."""

    workflow_type: str
    version: "ProtocolSemVer"
    name: str
    description: str
    tasks: list["ProtocolTaskConfiguration"]
    default_retry_config: "ProtocolRetryConfiguration"
    default_timeout_config: "ProtocolTimeoutConfiguration"
    compensation_actions: list["ProtocolCompensationAction"]
    validation_rules: dict[str, ContextValue]
    schema: dict[str, ContextValue]

    async def validate_definition(self) -> bool: ...

    def is_valid_schema(self) -> bool: ...


@runtime_checkable
class ProtocolNodeCapability(Protocol):
    """Protocol for node capability objects."""

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
    """Protocol for discovered service instance objects in workflow orchestration."""

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
    """Protocol for recovery point objects."""

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
    """Protocol for replay strategy objects."""

    strategy_type: Literal["full", "partial", "from_checkpoint", "from_sequence"]
    start_sequence: int | None
    end_sequence: int | None
    event_filters: list[str]
    skip_failed_events: bool
    validate_state: bool

    async def validate_replay_strategy(self) -> bool: ...

    def is_executable(self) -> bool: ...


@runtime_checkable
class ProtocolEventStream(Protocol):
    """Protocol for event stream objects."""

    stream_id: str
    workflow_type: str
    instance_id: UUID
    start_sequence: int
    end_sequence: int
    events: list["ProtocolWorkflowEvent"]
    is_complete: bool
    next_token: str | None

    async def validate_stream(self) -> bool: ...

    async def is_complete_stream(self) -> bool: ...


@runtime_checkable
class ProtocolEventProjection(Protocol):
    """Protocol for event projection objects."""

    projection_name: str
    workflow_type: str
    last_processed_sequence: int
    projection_data: dict[str, "ProtocolWorkflowValue"]
    created_at: "ProtocolDateTime"
    updated_at: "ProtocolDateTime"

    async def validate_projection(self) -> bool: ...

    def is_up_to_date(self) -> bool: ...
