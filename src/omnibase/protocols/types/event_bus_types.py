"""
Event bus protocol types for ONEX SPI interfaces.

Domain: Event-driven architecture protocols
"""

from typing import Dict, Literal, Protocol, Union
from uuid import UUID

# Event data types - more specific than Any
EventData = Union[
    str, int, float, bool, list[str], Dict[str, Union[str, int, float, bool]]
]

# Event status types
EventStatus = Literal["pending", "processing", "completed", "failed", "cancelled"]

# Authentication types
AuthStatus = Literal["authenticated", "unauthenticated", "expired", "invalid"]


# Event protocols
class ProtocolEvent(Protocol):
    """Protocol for event objects."""

    event_type: str
    event_data: Dict[str, EventData]
    correlation_id: UUID
    timestamp: float
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
    auth_status: AuthStatus
    token_expires_at: float | None


class ProtocolEventCredentials(Protocol):
    """Protocol for event bus credentials."""

    username: str
    password: str
    host: str
    port: int
    virtual_host: str | None


# Event subscription protocols
class ProtocolEventSubscription(Protocol):
    """Protocol for event subscriptions."""

    event_type: str
    subscriber_id: str
    filter_criteria: Dict[str, str]
    is_active: bool


# ONEX-specific event protocols
class ProtocolOnexEvent(Protocol):
    """Protocol for ONEX system events."""

    event_id: UUID
    event_type: str
    timestamp: float
    source: str
    payload: Dict[str, EventData]
    correlation_id: UUID
    metadata: Dict[str, EventData]


class ProtocolEventBusCredentials(Protocol):
    """Protocol for event bus credential models."""

    username: str
    password: str
    host: str
    port: int
    virtual_host: str | None
    connection_timeout: int
    heartbeat: int
