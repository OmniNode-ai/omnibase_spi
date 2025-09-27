"""
Workflow orchestration protocol types for ONEX SPI interfaces.

Domain: Event-driven workflow orchestration with FSM states and event sourcing
"""

from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    Literal,
    Optional,
    Protocol,
    TypeVar,
    runtime_checkable,
)
from uuid import UUID

from omnibase_spi.protocols.types.protocol_core_types import (
    ContextValue,
    LiteralNodeType,
    ProtocolDateTime,
    ProtocolSemVer,
)

if TYPE_CHECKING:
    # Forward references for type checking - add any circular import types here
    pass


@runtime_checkable
class ProtocolWorkflowValue(Protocol):
    """Protocol for workflow data values supporting serialization and validation."""

    def serialize(self) -> dict[str, object]:
        """Serialize value to dictionary for persistence."""
        ...

    def validate(self) -> bool:
        """Validate the value meets workflow constraints."""
        ...

    def get_type_info(self) -> str:
        """Get type information for workflow introspection."""
        ...


@runtime_checkable
class ProtocolWorkflowStringValue(ProtocolWorkflowValue, Protocol):
    """Protocol for string-based workflow values."""

    value: str

    def get_string_length(self) -> int:
        """Get the length of the string value."""
        ...

    def is_empty_string(self) -> bool:
        """Check if the string value is empty."""
        ...


@runtime_checkable
class ProtocolWorkflowStringListValue(ProtocolWorkflowValue, Protocol):
    """Protocol for string list workflow values."""

    value: list[str]

    def get_list_length(self) -> int:
        """Get the number of items in the string list."""
        ...

    def is_empty_list(self) -> bool:
        """Check if the string list is empty."""
        ...


@runtime_checkable
class ProtocolWorkflowStringDictValue(ProtocolWorkflowValue, Protocol):
    """Protocol for string dictionary workflow values."""

    value: dict[str, "ContextValue"]

    def get_dict_keys(self) -> list[str]:
        """Get the keys in the dictionary value."""
        ...

    def has_key(self, key: str) -> bool:
        """Check if the dictionary contains the specified key."""
        ...


@runtime_checkable
class ProtocolWorkflowNumericValue(ProtocolWorkflowValue, Protocol):
    """Protocol for numeric workflow values (int or float)."""

    value: int | float

    def is_integer(self) -> bool:
        """Check if the numeric value is an integer."""
        ...

    def is_positive(self) -> bool:
        """Check if the numeric value is positive."""
        ...


@runtime_checkable
class ProtocolWorkflowStructuredValue(ProtocolWorkflowValue, Protocol):
    """Protocol for structured workflow values with context data."""

    value: dict[str, "ContextValue"]

    def get_structure_depth(self) -> int:
        """Get the nesting depth of the structured value."""
        ...

    def flatten_structure(self) -> dict[str, "ContextValue"]:
        """Flatten nested structure to a single level dictionary."""
        ...


T_WorkflowValue = TypeVar("T_WorkflowValue", str, int, float, bool)


@runtime_checkable
class ProtocolTypedWorkflowData(Generic[T_WorkflowValue], Protocol):
    """Protocol for strongly typed workflow data values."""

    value: T_WorkflowValue

    def get_type_name(self) -> str:
        """Get the type name for this workflow data."""
        ...

    def serialize_typed(self) -> dict[str, Any]:
        """Serialize with type information."""
        ...


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

    def validate_metadata(self) -> bool:
        """Validate that workflow metadata is complete and consistent."""
        ...

    def is_complete(self) -> bool:
        """Check if all required metadata fields are present and valid."""
        ...


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

    def validate_retry_config(self) -> bool:
        """Validate that retry configuration parameters are reasonable and consistent."""
        ...

    def is_valid_policy(self) -> bool:
        """Check if the retry policy is valid and the parameters are consistent with the policy."""
        ...


@runtime_checkable
class ProtocolTimeoutConfiguration(Protocol):
    """Protocol for timeout configuration objects."""

    timeout_type: LiteralTimeoutType
    timeout_seconds: int
    warning_seconds: int | None
    grace_period_seconds: int | None
    escalation_policy: str | None

    def validate_timeout_config(self) -> bool:
        """Validate that timeout configuration is reasonable and internally consistent."""
        ...

    def is_reasonable(self) -> bool:
        """Check if timeout values are within reasonable bounds for the timeout type."""
        ...


@runtime_checkable
class ProtocolTaskDependency(Protocol):
    """Protocol for task dependency objects."""

    task_id: UUID
    dependency_type: Literal["hard", "soft", "conditional"]
    condition: str | None
    timeout_seconds: int | None

    def validate_dependency(self) -> bool:
        """Validate that the task dependency configuration is valid."""
        ...

    def is_conditional(self) -> bool:
        """Check if this is a conditional dependency with a valid condition."""
        ...


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

    def validate_context(self) -> bool:
        """Validate that workflow context is complete and consistent."""
        ...

    def has_required_data(self) -> bool:
        """Check if all required data fields are present for the workflow type."""
        ...


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
    resource_requirements: dict[str, Any]
    annotations: dict[str, "ContextValue"]

    def validate_task(self) -> bool:
        """Validate that task configuration is complete and consistent."""
        ...

    def has_valid_dependencies(self) -> bool:
        """Check if all task dependencies are valid and resolvable."""
        ...


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

    def validate_event(self) -> bool:
        """Validate that workflow event is well-formed and consistent."""
        ...

    def is_valid_sequence(self) -> bool:
        """Check if the event sequence number is valid for the workflow instance."""
        ...


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

    def validate_snapshot(self) -> bool:
        """Validate workflowsnapshot data integrity and consistency."""
        ...

    def is_consistent(self) -> bool:
        """Check if workflowsnapshot consistent."""
        ...


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

    def validate_result(self) -> bool:
        """Validate taskresult data integrity and consistency."""
        ...

    def is_success(self) -> bool:
        """Check if taskresult success."""
        ...


@runtime_checkable
class ProtocolCompensationAction(Protocol):
    """Protocol for compensation action objects."""

    compensation_id: UUID
    task_id: UUID
    action_type: Literal["rollback", "cleanup", "notify", "custom"]
    action_data: dict[str, "ProtocolWorkflowValue"]
    timeout_seconds: int
    retry_config: "ProtocolRetryConfiguration"

    def validate_compensation(self) -> bool:
        """Validate compensationaction data integrity and consistency."""
        ...

    async def can_execute(self) -> bool:
        """Check if compensation action can be executed."""
        ...


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
    validation_rules: dict[str, Any]
    schema: dict[str, Any]

    def validate_definition(self) -> bool:
        """Validate workflowdefinition data integrity and consistency."""
        ...

    def is_valid_schema(self) -> bool:
        """Check if workflowdefinition valid schema."""
        ...


@runtime_checkable
class ProtocolNodeCapability(Protocol):
    """Protocol for node capability objects."""

    capability_name: str
    version: "ProtocolSemVer"
    node_types: list[LiteralNodeType]
    resource_requirements: dict[str, Any]
    configuration_schema: dict[str, Any]
    supported_task_types: list[LiteralTaskType]

    def validate_capability(self) -> bool:
        """Validate nodecapability data integrity and consistency."""
        ...

    def is_supported(self) -> bool:
        """Check if nodecapability supported."""
        ...


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

    def validate_service_instance(self) -> bool:
        """Validate workflowserviceinstance data integrity and consistency."""
        ...

    def is_healthy(self) -> bool:
        """Check if workflowserviceinstance healthy."""
        ...


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

    def validate_recovery_point(self) -> bool:
        """Validate recoverypoint data integrity and consistency."""
        ...

    def is_restorable(self) -> bool:
        """Check if recoverypoint restorable."""
        ...


@runtime_checkable
class ProtocolReplayStrategy(Protocol):
    """Protocol for replay strategy objects."""

    strategy_type: Literal["full", "partial", "from_checkpoint", "from_sequence"]
    start_sequence: int | None
    end_sequence: int | None
    event_filters: list[str]
    skip_failed_events: bool
    validate_state: bool

    def validate_replay_strategy(self) -> bool:
        """Validate replaystrategy data integrity and consistency."""
        ...

    def is_executable(self) -> bool:
        """Check if replaystrategy executable."""
        ...


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

    def validate_stream(self) -> bool:
        """Validate eventstream data integrity and consistency."""
        ...

    def is_complete_stream(self) -> bool:
        """Check if eventstream complete stream."""
        ...


@runtime_checkable
class ProtocolEventProjection(Protocol):
    """Protocol for event projection objects."""

    projection_name: str
    workflow_type: str
    last_processed_sequence: int
    projection_data: dict[str, "ProtocolWorkflowValue"]
    created_at: "ProtocolDateTime"
    updated_at: "ProtocolDateTime"

    def validate_projection(self) -> bool:
        """Validate eventprojection data integrity and consistency."""
        ...

    def is_up_to_date(self) -> bool:
        """Check if eventprojection up to date."""
        ...
