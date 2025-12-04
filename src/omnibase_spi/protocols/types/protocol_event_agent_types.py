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
    so producers can send only relevant data.
    """

    message: str | None
    success: bool | None
    code: int | None
    tags: list[str] | None

    def to_event_kwargs(self) -> dict[str, str | bool | int | list[str]]: ...


@runtime_checkable
class ProtocolAgentEvent(Protocol):
    """Protocol for agent event objects."""

    agent_id: str
    event_type: Literal["created", "started", "stopped", "error", "heartbeat"]
    timestamp: "ProtocolDateTime"
    correlation_id: UUID
    metadata: dict[str, "ContextValue"]

    async def validate_agent_event(self) -> bool: ...


@runtime_checkable
class ProtocolEventBusAgentStatus(Protocol):
    """Protocol for agent status objects in event bus domain."""

    agent_id: str
    status: Literal["idle", "busy", "error", "offline", "terminating"]
    current_task: str | None
    last_heartbeat: "ProtocolDateTime"
    performance_metrics: dict[str, "ContextValue"]

    async def validate_agent_status(self) -> bool: ...


@runtime_checkable
class ProtocolProgressUpdate(Protocol):
    """Protocol for progress update objects."""

    work_item_id: str
    progress_percentage: float
    status_message: str
    estimated_completion: "ProtocolDateTime | None"
    metadata: dict[str, "ContextValue"]

    async def validate_progress_update(self) -> bool: ...


@runtime_checkable
class ProtocolWorkResult(Protocol):
    """Protocol for work result objects."""

    work_ticket_id: str
    result_type: Literal["success", "failure", "timeout", "cancelled"]
    result_data: dict[str, "ContextValue"]
    execution_time_ms: int
    error_message: str | None
    metadata: dict[str, "ContextValue"]

    async def validate_work_result(self) -> bool: ...
