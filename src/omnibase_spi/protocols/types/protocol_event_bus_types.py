"""
Event Bus Protocol Types for ONEX SPI.

Provides protocol definitions for event bus message types including
event headers and event structures used in ONEX event-driven architecture.

Domain: Event bus and messaging infrastructure
Author: ONEX Framework Team
"""

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_core_types import ContextValue


# Type alias for event headers (commonly used as dict of string to string)
ProtocolEventHeaders = dict[str, str]


@runtime_checkable
class ProtocolOnexEvent(Protocol):
    """
    Protocol for ONEX event representation.

    Represents a standard event in the ONEX event-driven architecture
    with support for event type, source, timestamp, and data payload.

    Key Features:
        - Unique event identification
        - Event type classification
        - Source tracking
        - Timestamp for event ordering
        - Flexible data payload
        - Optional correlation ID for event tracing

    Usage Example:
        ```python
        event: ProtocolOnexEvent = create_event(
            event_type="workflow.started",
            source="orchestrator",
            data={"workflow_id": "abc123"}
        )
        await event_bus.publish(event)
        ```
    """

    @property
    def event_id(self) -> str:
        """Unique identifier for the event."""
        ...

    @property
    def event_type(self) -> str:
        """Type/category of the event."""
        ...

    @property
    def source(self) -> str:
        """Source system or component that generated the event."""
        ...

    @property
    def timestamp(self) -> float:
        """Unix timestamp of when the event was created."""
        ...

    @property
    def data(self) -> dict[str, "ContextValue"]:
        """Event payload data."""
        ...

    @property
    def correlation_id(self) -> str | None:
        """Optional correlation ID for event tracing."""
        ...

    @property
    def headers(self) -> ProtocolEventHeaders:
        """Optional event headers for metadata."""
        ...
