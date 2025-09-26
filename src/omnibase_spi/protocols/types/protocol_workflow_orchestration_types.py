"""
Workflow orchestration protocol types for ONEX SPI interfaces.

Domain: Event-driven workflow orchestration with FSM states and event sourcing
"""

from typing import Any, Generic, Literal, Optional, Protocol, TypeVar, runtime_checkable

# Note on Any usage in workflow types:
# dict[str, Any] is used for resource requirements and configuration schemas because:
# 1. Resource specs vary widely (CPU, memory, disk, GPU, custom hardware)
# 2. Configuration schemas must support arbitrary workflow-specific parameters
# 3. Workflow data can contain complex nested structures from external systems
from uuid import UUID

from omnibase_spi.protocols.types.protocol_core_types import (
    ContextValue,
    LiteralNodeType,
    ProtocolDateTime,
    ProtocolSemVer,
)

# === Protocol-Based Value Types ===


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


# === Workflow Value Protocol Hierarchy (Eliminates Union anti-patterns) ===


@runtime_checkable
class ProtocolWorkflowStringValue(ProtocolWorkflowValue, Protocol):
    """Protocol for string-based workflow values."""

    value: str


@runtime_checkable
class ProtocolWorkflowStringListValue(ProtocolWorkflowValue, Protocol):
    """Protocol for string list workflow values."""

    value: list[str]


@runtime_checkable
class ProtocolWorkflowStringDictValue(ProtocolWorkflowValue, Protocol):
    """Protocol for string dictionary workflow values."""

    value: dict[str, str]


@runtime_checkable
class ProtocolWorkflowNumericValue(ProtocolWorkflowValue, Protocol):
    """Protocol for numeric workflow values (int or float)."""

    value: int | float


@runtime_checkable
class ProtocolWorkflowStructuredValue(ProtocolWorkflowValue, Protocol):
    """Protocol for structured workflow values with context data."""

    value: dict[str, ContextValue]


# === Generic Type Definitions ===

# Constrained TypeVar for workflow primitive values
T_WorkflowValue = TypeVar("T_WorkflowValue", str, int, float, bool)


# Generic protocol for typed workflow data
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


# Workflow state types - hierarchical FSM states
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

# Task state types - individual task execution states
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

# Task types - dispatch annotations for effects[] and computes[]
LiteralTaskType = Literal["compute", "effect", "orchestrator", "reducer"]

# Execution semantics - await vs fire-and-forget
LiteralExecutionSemantics = Literal["await", "fire_and_forget", "async_await"]

# Retry policy types
LiteralRetryPolicy = Literal["none", "fixed", "exponential", "linear", "custom"]

# Event types for workflow orchestration
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

# Timeout types
LiteralTimeoutType = Literal["execution", "idle", "total", "heartbeat"]

# Priority levels for task scheduling
LiteralTaskPriority = Literal["low", "normal", "high", "critical", "urgent"]

# Isolation levels for workflow instances
LiteralIsolationLevel = Literal[
    "read_uncommitted", "read_committed", "repeatable_read", "serializable"
]


# Core workflow protocols
class ProtocolWorkflowMetadata(Protocol):
    """Protocol for workflow metadata objects."""

    workflow_type: str
    instance_id: UUID
    correlation_id: UUID
    created_by: str
    environment: str
    group: str
    version: ProtocolSemVer
    tags: dict[str, str]
    metadata: dict[str, ContextValue]


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


class ProtocolTimeoutConfiguration(Protocol):
    """Protocol for timeout configuration objects."""

    timeout_type: LiteralTimeoutType
    timeout_seconds: int
    warning_seconds: Optional[int]
    grace_period_seconds: Optional[int]
    escalation_policy: Optional[str]


class ProtocolTaskDependency(Protocol):
    """Protocol for task dependency objects."""

    task_id: UUID
    dependency_type: Literal["hard", "soft", "conditional"]
    condition: Optional[str]
    timeout_seconds: Optional[int]


class ProtocolWorkflowContext(Protocol):
    """Protocol for workflow context objects with isolation."""

    workflow_type: str
    instance_id: UUID
    correlation_id: UUID
    isolation_level: LiteralIsolationLevel
    data: dict[str, ProtocolWorkflowValue]
    secrets: dict[str, str]  # Encrypted/protected values
    capabilities: list[str]
    resource_limits: dict[str, int]


class ProtocolTaskConfiguration(Protocol):
    """Protocol for task configuration objects."""

    task_id: UUID
    task_name: str
    task_type: LiteralTaskType
    node_type: LiteralNodeType
    execution_semantics: LiteralExecutionSemantics
    priority: LiteralTaskPriority
    dependencies: list[ProtocolTaskDependency]
    retry_config: ProtocolRetryConfiguration
    timeout_config: ProtocolTimeoutConfiguration
    resource_requirements: dict[str, Any]
    annotations: dict[str, str]


class ProtocolWorkflowEvent(Protocol):
    """Protocol for workflow event objects with event sourcing."""

    event_id: UUID
    event_type: LiteralWorkflowEventType
    workflow_type: str
    instance_id: UUID
    correlation_id: UUID
    sequence_number: int
    timestamp: ProtocolDateTime
    source: str
    idempotency_key: str
    payload: dict[str, ProtocolWorkflowValue]
    metadata: dict[str, ContextValue]
    causation_id: Optional[UUID]  # Event that caused this event
    correlation_chain: list[UUID]  # Full correlation chain


class ProtocolWorkflowSnapshot(Protocol):
    """Protocol for workflow snapshot objects."""

    workflow_type: str
    instance_id: UUID
    sequence_number: int
    state: LiteralWorkflowState
    context: ProtocolWorkflowContext
    tasks: list[ProtocolTaskConfiguration]
    created_at: ProtocolDateTime
    metadata: dict[str, ContextValue]


class ProtocolTaskResult(Protocol):
    """Protocol for task execution results."""

    task_id: UUID
    execution_id: UUID
    state: LiteralTaskState
    result_data: dict[str, ProtocolWorkflowValue]
    error_message: Optional[str]
    error_code: Optional[str]
    retry_count: int
    execution_time_seconds: float
    resource_usage: dict[str, float]
    output_artifacts: list[str]
    events_emitted: list[ProtocolWorkflowEvent]


class ProtocolCompensationAction(Protocol):
    """Protocol for compensation action objects."""

    compensation_id: UUID
    task_id: UUID
    action_type: Literal["rollback", "cleanup", "notify", "custom"]
    action_data: dict[str, ProtocolWorkflowValue]
    timeout_seconds: int
    retry_config: ProtocolRetryConfiguration


class ProtocolWorkflowDefinition(Protocol):
    """Protocol for workflow definition objects."""

    workflow_type: str
    version: ProtocolSemVer
    name: str
    description: str
    tasks: list[ProtocolTaskConfiguration]
    default_retry_config: ProtocolRetryConfiguration
    default_timeout_config: ProtocolTimeoutConfiguration
    compensation_actions: list[ProtocolCompensationAction]
    validation_rules: dict[str, Any]
    schema: dict[str, Any]  # JSON schema for workflow data


# Node capability protocols
class ProtocolNodeCapability(Protocol):
    """Protocol for node capability objects."""

    capability_name: str
    version: ProtocolSemVer
    node_types: list[LiteralNodeType]
    resource_requirements: dict[str, Any]
    configuration_schema: dict[str, Any]
    supported_task_types: list[LiteralTaskType]


class ProtocolServiceDiscovery(Protocol):
    """Protocol for service discovery objects."""

    service_name: str
    service_type: str
    endpoint: str
    health_check_url: str
    metadata: dict[str, ContextValue]
    capabilities: list[ProtocolNodeCapability]
    last_heartbeat: ProtocolDateTime


# Recovery and replay protocols
class ProtocolRecoveryPoint(Protocol):
    """Protocol for recovery point objects."""

    recovery_id: UUID
    workflow_type: str
    instance_id: UUID
    sequence_number: int
    state: LiteralWorkflowState
    recovery_type: Literal["checkpoint", "savepoint", "snapshot"]
    created_at: ProtocolDateTime
    metadata: dict[str, ContextValue]


class ProtocolReplayStrategy(Protocol):
    """Protocol for replay strategy objects."""

    strategy_type: Literal["full", "partial", "from_checkpoint", "from_sequence"]
    start_sequence: Optional[int]
    end_sequence: Optional[int]
    event_filters: list[str]
    skip_failed_events: bool
    validate_state: bool


# Event sourcing specific protocols
class ProtocolEventStream(Protocol):
    """Protocol for event stream objects."""

    stream_id: str
    workflow_type: str
    instance_id: UUID
    start_sequence: int
    end_sequence: int
    events: list[ProtocolWorkflowEvent]
    is_complete: bool
    next_token: Optional[str]


class ProtocolEventProjection(Protocol):
    """Protocol for event projection objects."""

    projection_name: str
    workflow_type: str
    last_processed_sequence: int
    projection_data: dict[str, ProtocolWorkflowValue]
    created_at: ProtocolDateTime
    updated_at: ProtocolDateTime
