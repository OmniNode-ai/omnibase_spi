"""
Event bus protocol types for ONEX SPI interfaces.

Domain: Event-driven architecture protocols
"""

from typing import TYPE_CHECKING, Literal, Protocol, runtime_checkable
from uuid import UUID

if TYPE_CHECKING:
    pass

from omnibase_spi.protocols.types.protocol_core_types import (
    ContextValue,
    LiteralBaseStatus,
    ProtocolDateTime,
    ProtocolSemVer,
)


@runtime_checkable
class ProtocolEventData(Protocol):
    """Protocol for event data values supporting validation and serialization."""

    async def validate_for_transport(self) -> bool: ...


@runtime_checkable
class ProtocolEventStringData(ProtocolEventData, Protocol):
    """Protocol for string-based event data."""

    value: str


@runtime_checkable
class ProtocolEventStringListData(ProtocolEventData, Protocol):
    """Protocol for string list event data."""

    value: list[str]


@runtime_checkable
class ProtocolEventStringDictData(ProtocolEventData, Protocol):
    """Protocol for string dictionary event data."""

    value: dict[str, "ContextValue"]


EventStatus = LiteralBaseStatus
LiteralAuthStatus = Literal["authenticated", "unauthenticated", "expired", "invalid"]
LiteralEventPriority = Literal["low", "normal", "high", "critical"]
MessageKey = bytes | None


@runtime_checkable
class ProtocolEvent(Protocol):
    """Protocol for event objects."""

    event_type: str
    event_data: dict[str, "ProtocolEventData"]
    correlation_id: UUID
    timestamp: "ProtocolDateTime"
    source: str

    async def validate_event(self) -> bool: ...


@runtime_checkable
class ProtocolEventResult(Protocol):
    """Protocol for event processing results."""

    success: bool
    event_id: UUID
    processing_time: float
    error_message: str | None

    async def validate_result(self) -> bool: ...


@runtime_checkable
class ProtocolSecurityContext(Protocol):
    """Protocol for security context objects."""

    user_id: str | None
    permissions: list[str]
    auth_status: LiteralAuthStatus
    token_expires_at: "ProtocolDateTime | None"

    async def validate_security_context(self) -> bool: ...


@runtime_checkable
class ProtocolEventSubscription(Protocol):
    """Protocol for event subscriptions."""

    event_type: str
    subscriber_id: str
    filter_criteria: dict[str, "ContextValue"]
    is_active: bool

    async def validate_subscription(self) -> bool: ...


@runtime_checkable
class ProtocolOnexEvent(Protocol):
    """Protocol for ONEX system events."""

    event_id: UUID
    event_type: str
    timestamp: "ProtocolDateTime"
    source: str
    payload: dict[str, "ProtocolEventData"]
    correlation_id: UUID
    metadata: dict[str, "ProtocolEventData"]

    async def validate_onex_event(self) -> bool: ...


@runtime_checkable
class ProtocolEventBusConnectionCredentials(Protocol):
    """Protocol for event bus connection credential models with connection parameters."""

    username: str
    password: str
    host: str
    port: int
    virtual_host: str | None
    connection_timeout: int
    heartbeat: int


@runtime_checkable
class ProtocolEventHeaders(Protocol):
    """
    Protocol for ONEX event bus message headers.

    Standardized headers for ONEX event bus messages ensuring strict
    interoperability across all agents and preventing integration failures.
    """

    content_type: str
    correlation_id: UUID
    message_id: UUID
    timestamp: "ProtocolDateTime"
    source: str
    event_type: str
    schema_version: "ProtocolSemVer"
    destination: str | None
    trace_id: str | None
    span_id: str | None
    parent_span_id: str | None
    operation_name: str | None
    priority: "LiteralEventPriority | None"
    routing_key: str | None
    partition_key: str | None
    retry_count: int | None
    max_retries: int | None
    ttl_seconds: int | None

    async def validate_headers(self) -> bool: ...


EventMessage = "ProtocolEventMessage"


@runtime_checkable
class ProtocolEventMessage(Protocol):
    """
    Protocol for ONEX event bus message objects.

    Defines the contract that all event message implementations must satisfy
    for Kafka/RedPanda compatibility following ONEX Messaging Design.
    """

    topic: str
    key: MessageKey
    value: bytes
    headers: "ProtocolEventHeaders"
    offset: str | None
    partition: int | None

    async def ack(self) -> None: ...


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
class ProtocolAgentStatus(Protocol):
    """Protocol for agent status objects."""

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
    estimated_completion: "ProtocolDateTime" | None
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
