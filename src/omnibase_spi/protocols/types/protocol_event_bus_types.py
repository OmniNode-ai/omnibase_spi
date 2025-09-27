"""
Event bus protocol types for ONEX SPI interfaces.

Domain: Event-driven architecture protocols
"""

from typing import TYPE_CHECKING, Literal, Optional, Protocol, runtime_checkable
from uuid import UUID

if TYPE_CHECKING:
    from omnibase_spi.protocols.event_bus.protocol_event_bus import (
        ProtocolEventBusHeaders,
    )
from omnibase_spi.protocols.types.protocol_core_types import (
    ContextValue,
    LiteralBaseStatus,
    ProtocolDateTime,
    ProtocolSemVer,
)


@runtime_checkable
class ProtocolEventData(Protocol):
    """Protocol for event data values supporting validation and serialization."""

    def validate_for_transport(self) -> bool:
        """Validate value is safe for event transport."""
        ...

    def serialize_for_event(self) -> dict[str, object]:
        """Serialize value for event messaging."""
        ...

    def get_event_type_hint(self) -> str:
        """Get type hint for event schema validation."""
        ...


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

    def validate_event(self) -> bool:
        """Validate event data integrity and consistency."""
        ...

    def has_required_fields(self) -> bool:
        """Check if event required fields."""
        ...


@runtime_checkable
class ProtocolEventResult(Protocol):
    """Protocol for event processing results."""

    success: bool
    event_id: UUID
    processing_time: float
    error_message: str | None

    def validate_result(self) -> bool:
        """Validate eventresult data integrity and consistency."""
        ...

    def is_successful(self) -> bool:
        """Check if eventresult successful."""
        ...


@runtime_checkable
class ProtocolSecurityContext(Protocol):
    """Protocol for security context objects."""

    user_id: str | None
    permissions: list[str]
    auth_status: LiteralAuthStatus
    token_expires_at: "ProtocolDateTime | None"

    def validate_security_context(self) -> bool:
        """Validate securitycontext data integrity and consistency."""
        ...

    def is_authenticated(self) -> bool:
        """Check if securitycontext authenticated."""
        ...


@runtime_checkable
class ProtocolEventSubscription(Protocol):
    """Protocol for event subscriptions."""

    event_type: str
    subscriber_id: str
    filter_criteria: dict[str, "ContextValue"]
    is_active: bool

    def validate_subscription(self) -> bool:
        """Validate eventsubscription data integrity and consistency."""
        ...


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

    def validate_onex_event(self) -> bool:
        """Validate onexevent data integrity and consistency."""
        ...

    def is_well_formed(self) -> bool:
        """Check if onexevent well formed."""
        ...


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

    def validate_headers(self) -> bool:
        """Validate eventheaders data integrity and consistency."""
        ...

    def has_required_headers(self) -> bool:
        """Check if eventheaders required headers."""
        ...


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

    async def ack(self) -> None:
        """Acknowledge message processing (adapter-specific implementation)."""
        ...


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

    def to_event_kwargs(self) -> dict[str, str | bool | int | list[str]]:
        """Convert to kwargs for event creation, excluding None values."""
        ...
