"""
Security Event Protocol Interface

Protocol interface for security events in audit trails.
Defines the minimal contract needed by security event collections and consumers.
"""

from datetime import datetime
from typing import Any, Protocol, runtime_checkable
from uuid import UUID


@runtime_checkable
class ProtocolSecurityEvent(Protocol):
    """
    Protocol interface for security events.

    Defines the minimal contract needed for security event handling in audit trails.
    All security event implementations must provide these attributes.
    """

    @property
    def event_id(self) -> UUID:
        """Unique event identifier."""
        ...

    @property
    def event_type(self) -> Any:  # EnumSecurityEventType
        """Type of security event."""
        ...

    @property
    def timestamp(self) -> datetime:
        """When the event occurred."""
        ...

    @property
    def envelope_id(self) -> UUID:
        """Associated envelope ID."""
        ...

    @property
    def status(self) -> Any:  # EnumSecurityEventStatus
        """Event status."""
        ...

    @property
    def user_id(self) -> UUID | None:
        """User associated with event."""
        ...

    @property
    def node_id(self) -> UUID | None:
        """Node that generated the event."""
        ...

    def model_dump(self) -> dict[str, Any]:
        """Export event as dictionary."""
        ...
