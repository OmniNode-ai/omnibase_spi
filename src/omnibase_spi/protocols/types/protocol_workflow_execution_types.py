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


# Forward reference for ProtocolWorkflowEvent
class _ProtocolWorkflowEventRef(Protocol):
    """Forward reference marker for ProtocolWorkflowEvent."""

    event_id: UUID
    event_type: LiteralWorkflowEventType


@runtime_checkable
class ProtocolEventStream(Protocol):
    """Protocol for event stream objects."""

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
    """Protocol for event projection objects."""

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
    """Protocol for health check result objects."""

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
    """Protocol for workflow execution state objects."""

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
