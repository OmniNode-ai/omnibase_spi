"""
Event bus protocol types for ONEX SPI interfaces.

Domain: Event-driven architecture protocols
"""

from typing import Literal, Optional, Protocol, runtime_checkable
from uuid import UUID

from omnibase_spi.protocols.types.protocol_core_types import (
    ContextValue,
    LiteralBaseStatus,
    ProtocolDateTime,
    ProtocolSemVer,
)

# === Protocol-Based Event Value Types ===


@runtime_checkable
class ProtocolEventValue(Protocol):
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


# === Event Data Protocol Hierarchy (Eliminates Union anti-patterns) ===


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

    value: dict[str, ContextValue]


# Event status types - using consolidated LiteralBaseStatus
EventStatus = LiteralBaseStatus

# Authentication types
LiteralAuthStatus = Literal["authenticated", "unauthenticated", "expired", "invalid"]

# Event priority types for ONEX messaging
LiteralEventPriority = Literal["low", "normal", "high", "critical"]

# Message key types - for partitioning and routing
MessageKey = Optional[bytes]


# Event protocols
class ProtocolEvent(Protocol):
    """Protocol for event objects."""

    event_type: str
    event_data: dict[str, ProtocolEventData]
    correlation_id: UUID
    timestamp: ProtocolDateTime
    source: str


class ProtocolEventResult(Protocol):
    """Protocol for event processing results."""

    success: bool
    event_id: UUID
    processing_time: float
    error_message: str | None


# Security context protocols
class ProtocolSecurityContext(Protocol):
    """Protocol for security context objects."""

    user_id: str | None
    permissions: list[str]
    auth_status: LiteralAuthStatus
    token_expires_at: ProtocolDateTime | None


# ProtocolEventCredentials removed - consolidated into ProtocolEventBusCredentials below


# Event subscription protocols
class ProtocolEventSubscription(Protocol):
    """Protocol for event subscriptions."""

    event_type: str
    subscriber_id: str
    filter_criteria: dict[str, ContextValue]
    is_active: bool


# ONEX-specific event protocols
class ProtocolOnexEvent(Protocol):
    """Protocol for ONEX system events."""

    event_id: UUID
    event_type: str
    timestamp: ProtocolDateTime
    source: str
    payload: dict[str, ProtocolEventData]
    correlation_id: UUID
    metadata: dict[str, ProtocolEventData]


class ProtocolEventBusCredentials(Protocol):
    """Protocol for event bus credential models."""

    username: str
    password: str
    host: str
    port: int
    virtual_host: str | None
    connection_timeout: int
    heartbeat: int


# ONEX Messaging Event Headers Protocol
class ProtocolEventHeaders(Protocol):
    """
    Protocol for ONEX event bus message headers.

    Standardized headers for ONEX event bus messages ensuring strict
    interoperability across all agents and preventing integration failures.
    """

    # REQUIRED - Essential for system operation and observability
    content_type: str  # MIME type: "application/json", "application/avro", etc.
    correlation_id: UUID  # UUID format for distributed business tracing
    message_id: UUID  # UUID format for unique message identification
    timestamp: ProtocolDateTime  # Message creation timestamp
    source: str  # Source agent/service identifier
    event_type: str  # Event classification (e.g., "core.node.start")
    schema_version: ProtocolSemVer  # Message schema version for compatibility

    # OPTIONAL - Standardized but not mandatory
    destination: Optional[str]  # Target agent/service (for direct routing)
    trace_id: Optional[str]  # OpenTelemetry trace ID (32 hex chars, no hyphens)
    span_id: Optional[str]  # OpenTelemetry span ID (16 hex chars, no hyphens)
    parent_span_id: Optional[str]  # Parent span ID (16 hex chars, no hyphens)
    operation_name: Optional[str]  # Operation being performed (for tracing context)
    priority: Optional[LiteralEventPriority]  # Message priority
    routing_key: Optional[str]  # Kafka/messaging routing key
    partition_key: Optional[str]  # Explicit partition assignment key
    retry_count: Optional[int]  # Number of retry attempts (for error handling)
    max_retries: Optional[int]  # Maximum retry attempts allowed
    ttl_seconds: Optional[int]  # Message time-to-live in seconds


# Event Message alias for backward compatibility
EventMessage = "ProtocolEventMessage"


# Event Message Protocol
class ProtocolEventMessage(Protocol):
    """
    Protocol for ONEX event bus message objects.

    Defines the contract that all event message implementations must satisfy
    for Kafka/RedPanda compatibility following ONEX Messaging Design.
    """

    topic: str
    key: MessageKey
    value: bytes
    headers: ProtocolEventHeaders
    offset: Optional[str]
    partition: Optional[int]

    async def ack(self) -> None:
        """Acknowledge message processing (adapter-specific implementation)."""
        ...


# Completion Data Protocol
class ProtocolCompletionData(Protocol):
    """
    Protocol for completion event data following ONEX naming conventions.

    Defines structure for completion event payloads with optional fields
    so producers can send only relevant data.
    """

    message: Optional[str]  # Human-readable completion message
    success: Optional[bool]  # Whether the operation succeeded
    code: Optional[int]  # Numeric status or error code
    tags: Optional[list[str]]  # Labels for search/filtering

    def to_event_kwargs(self) -> dict[str, str | bool | int | list[str]]:
        """Convert to kwargs for event creation, excluding None values."""
        ...
