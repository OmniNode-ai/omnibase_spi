"""
Simple Example Protocol - Demonstrating zero-dependency protocol design.

This serves as a template for creating protocols that don't depend on
external data types.
"""

from typing import TYPE_CHECKING, Any, Dict, Optional, Protocol, runtime_checkable

if TYPE_CHECKING:
    # Forward references to data types that would be defined elsewhere
    from typing import TypeVar

    T = TypeVar("T")


@runtime_checkable
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


@runtime_checkable
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


@runtime_checkable
class ProtocolSimpleEventHandler(Protocol):
    """
    Simple event handling protocol.
    """

    def handle_event(
        self, event_type: str, event_data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
        """Handle an event and optionally return response data."""
        ...

    def can_handle(self, event_type: str) -> bool:
        """Check if this node can process the given event type."""
        ...
