"""
Simple Example Protocol - Demonstrating zero-dependency protocol design.

This serves as a template for creating protocols that don't depend on
external model types.
"""

from typing import TYPE_CHECKING, Any, Dict, Optional, Protocol

if TYPE_CHECKING:
    # Forward references to models that would be defined elsewhere
    from typing import TypeVar

    T = TypeVar("T")


class ProtocolSimpleSerializer(Protocol):
    """
    Simple serialization protocol with no external dependencies.

    This demonstrates the zero-dependency approach where protocols
    use built-in types and forward references.
    """

    def serialize(self, data: Any) -> str:
        """Serialize data to string representation."""
        ...

    def deserialize(self, data: str) -> Any:
        """Deserialize string back to original data."""
        ...

    def get_format(self) -> str:
        """Get the serialization format name."""
        ...


class ProtocolSimpleLogger(Protocol):
    """
    Simple logging protocol using only built-in types.
    """

    def log(self, level: str, message: str, **kwargs: Any) -> None:
        """Log a message with given level."""
        ...

    def is_enabled(self, level: str) -> bool:
        """Check if logging level is enabled."""
        ...


class ProtocolSimpleEventHandler(Protocol):
    """
    Simple event handling protocol.
    """

    def handle_event(
        self, event_type: str, event_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Handle an event and optionally return response data."""
        ...

    def can_handle(self, event_type: str) -> bool:
        """Check if this handler can process the given event type."""
        ...
