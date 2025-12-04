"""
Event agent protocol types for ONEX SPI interfaces.

Domain: Agent-related event types including progress, completion, and work results.
"""

from typing import Literal, Protocol, runtime_checkable
from uuid import UUID

from omnibase_spi.protocols.types.protocol_core_types import (
    ContextValue,
    ProtocolDateTime,
)


@runtime_checkable
class ProtocolCompletionData(Protocol):
    """
    Protocol for completion event data following ONEX naming conventions.

    Defines structure for completion event payloads with optional fields
    so producers can send only relevant data. Used to signal workflow or
    task completion with status, exit codes, and categorization tags.

    Attributes:
        message: Optional completion message describing the outcome.
        success: Optional success indicator (True/False/None).
        code: Optional exit or status code.
        tags: Optional categorization tags for the completion event.

    Example:
        ```python
        class TaskCompletionData:
            message: str | None = "Processing completed successfully"
            success: bool | None = True
            code: int | None = 0
            tags: list[str] | None = ["batch", "processed"]

            def to_event_kwargs(self) -> dict[str, str | bool | int | list[str]]:
                result = {}
                if self.message is not None:
                    result["message"] = self.message
                if self.success is not None:
                    result["success"] = self.success
                if self.code is not None:
                    result["code"] = self.code
                if self.tags is not None:
                    result["tags"] = self.tags
                return result

        data = TaskCompletionData()
        assert isinstance(data, ProtocolCompletionData)
        kwargs = data.to_event_kwargs()
        assert kwargs["success"] is True
        ```
    """

    message: str | None
    success: bool | None
    code: int | None
    tags: list[str] | None

    def to_event_kwargs(self) -> dict[str, str | bool | int | list[str]]: ...


@runtime_checkable
class ProtocolAgentEvent(Protocol):
    """
    Protocol for agent lifecycle and operational events.

    Defines the structure for events emitted by agents during their lifecycle
    including creation, start, stop, error, and heartbeat events. Enables
    distributed agent monitoring and coordination via event-driven architecture.

    Attributes:
        agent_id: Unique identifier of the agent emitting the event.
        event_type: Type of lifecycle event (created, started, stopped, error, heartbeat).
        timestamp: When the event occurred.
        correlation_id: UUID for tracking related events across services.
        metadata: Additional event-specific metadata.

    Example:
        ```python
        from uuid import uuid4

        class AgentStartedEvent:
            agent_id: str = "agent-worker-001"
            event_type: Literal["created", "started", "stopped", "error", "heartbeat"] = "started"
            timestamp: ProtocolDateTime
            correlation_id: UUID = uuid4()
            metadata: dict[str, ContextValue] = {"host": "worker-node-1"}

            async def validate_agent_event(self) -> bool:
                return bool(self.agent_id) and self.event_type is not None

        event = AgentStartedEvent()
        assert isinstance(event, ProtocolAgentEvent)
        assert event.event_type == "started"
        ```
    """

    agent_id: str
    event_type: Literal["created", "started", "stopped", "error", "heartbeat"]
    timestamp: "ProtocolDateTime"
    correlation_id: UUID
    metadata: dict[str, "ContextValue"]

    async def validate_agent_event(self) -> bool: ...


@runtime_checkable
class ProtocolEventBusAgentStatus(Protocol):
    """
    Protocol for agent status published via the event bus.

    Provides comprehensive agent status information for monitoring and load
    balancing, including current task, heartbeat timing, and performance
    metrics. Published periodically by agents for health monitoring.

    Attributes:
        agent_id: Unique identifier of the agent.
        status: Current operational status (idle, busy, error, offline, terminating).
        current_task: Identifier of the current task if busy, None otherwise.
        last_heartbeat: Timestamp of the most recent heartbeat.
        performance_metrics: Performance data (CPU, memory, task throughput).

    Example:
        ```python
        class AgentStatus:
            agent_id: str = "agent-worker-001"
            status: Literal["idle", "busy", "error", "offline", "terminating"] = "busy"
            current_task: str | None = "task-12345"
            last_heartbeat: ProtocolDateTime
            performance_metrics: dict[str, ContextValue] = {
                "cpu_percent": 45.2,
                "memory_mb": 512,
                "tasks_completed": 100
            }

            async def validate_agent_status(self) -> bool:
                return bool(self.agent_id) and self.status is not None

        status = AgentStatus()
        assert isinstance(status, ProtocolEventBusAgentStatus)
        assert status.status == "busy"
        assert status.current_task is not None
        ```
    """

    agent_id: str
    status: Literal["idle", "busy", "error", "offline", "terminating"]
    current_task: str | None
    last_heartbeat: "ProtocolDateTime"
    performance_metrics: dict[str, "ContextValue"]

    async def validate_agent_status(self) -> bool: ...


@runtime_checkable
class ProtocolProgressUpdate(Protocol):
    """
    Protocol for progress update objects tracking work item completion.

    Provides progress tracking for long-running work items including
    percentage completion, status messages, estimated completion time,
    and arbitrary metadata. Enables real-time progress monitoring and
    user feedback in distributed workflow systems.

    Attributes:
        work_item_id: Unique identifier of the work item being tracked.
        progress_percentage: Completion percentage (0.0 to 100.0).
        status_message: Human-readable status message describing current state.
        estimated_completion: Estimated completion timestamp; None if unknown.
        metadata: Additional context-specific metadata for the update.

    Example:
        ```python
        class TaskProgressUpdate:
            work_item_id: str = "task_abc123"
            progress_percentage: float = 75.5
            status_message: str = "Processing batch 3 of 4"
            estimated_completion: ProtocolDateTime | None = datetime_instance
            metadata: dict[str, ContextValue] = {
                "current_batch": 3,
                "total_batches": 4,
                "items_processed": 750
            }

            async def validate_progress_update(self) -> bool:
                return 0.0 <= self.progress_percentage <= 100.0

        update = TaskProgressUpdate()
        assert isinstance(update, ProtocolProgressUpdate)
        assert update.progress_percentage == 75.5
        ```
    """

    work_item_id: str
    progress_percentage: float
    status_message: str
    estimated_completion: "ProtocolDateTime | None"
    metadata: dict[str, "ContextValue"]

    async def validate_progress_update(self) -> bool: ...


@runtime_checkable
class ProtocolWorkResult(Protocol):
    """
    Protocol for work result objects containing execution outcomes.

    Captures the complete result of a work ticket execution including
    success/failure status, result data, execution timing, and error
    details. Used for work completion reporting and result aggregation
    in distributed task processing systems.

    Attributes:
        work_ticket_id: Unique identifier of the completed work ticket.
        result_type: Outcome type ("success", "failure", "timeout", "cancelled").
        result_data: Dictionary containing the execution output or results.
        execution_time_ms: Total execution time in milliseconds.
        error_message: Error description if result_type is not "success"; None otherwise.
        metadata: Additional execution metadata (retries, resource usage, etc.).

    Example:
        ```python
        class SuccessfulWorkResult:
            work_ticket_id: str = "ticket_xyz789"
            result_type: Literal["success", "failure", "timeout", "cancelled"] = "success"
            result_data: dict[str, ContextValue] = {
                "output": "Processed 1000 records",
                "records_processed": 1000,
                "checksum": "abc123def456"
            }
            execution_time_ms: int = 5432
            error_message: str | None = None
            metadata: dict[str, ContextValue] = {
                "retry_count": 0,
                "worker_id": "worker-001"
            }

            async def validate_work_result(self) -> bool:
                valid_types = ("success", "failure", "timeout", "cancelled")
                return bool(self.work_ticket_id) and self.result_type in valid_types

        result = SuccessfulWorkResult()
        assert isinstance(result, ProtocolWorkResult)
        assert result.result_type == "success"
        ```
    """

    work_ticket_id: str
    result_type: Literal["success", "failure", "timeout", "cancelled"]
    result_data: dict[str, "ContextValue"]
    execution_time_ms: int
    error_message: str | None
    metadata: dict[str, "ContextValue"]

    async def validate_work_result(self) -> bool: ...
