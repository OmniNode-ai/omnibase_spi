"""
Example usage of ProtocolContainer protocol.

Demonstrates how to implement and use the ProtocolContainer protocol
for wrapping values with metadata in a type-safe manner.
"""

from typing import Any, Generic, TypeVar

from omnibase_spi.protocols.container import ProtocolContainer

T = TypeVar("T", covariant=True)


class ServiceResolutionContainer(Generic[T]):
    """
    Container for service resolution results with metadata.

    Example implementation showing how to use ProtocolContainer
    for dependency injection results.
    """

    def __init__(
        self,
        value: T,
        lifecycle: str = "singleton",
        scope: str = "global",
        resolution_time_ms: float | None = None,
    ):
        """
        Initialize service resolution container.

        Args:
            value: The resolved service instance
            lifecycle: Service lifecycle (singleton, transient, etc.)
            scope: Injection scope (global, request, etc.)
            resolution_time_ms: Time taken to resolve the service
        """
        self._value = value
        self._metadata = {
            "lifecycle": lifecycle,
            "scope": scope,
            "resolution_time_ms": resolution_time_ms,
            "type": type(value).__name__,
        }

    @property
    def value(self) -> T:
        """Get the resolved service instance."""
        return self._value

    @property
    def metadata(self) -> dict[str, Any]:
        """Get service resolution metadata."""
        return self._metadata.copy()

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get specific metadata field."""
        return self._metadata.get(key, default)


class EventPayloadContainer(Generic[T]):
    """
    Container for event payloads with routing metadata.

    Example implementation showing how to use ProtocolContainer
    for event bus message payloads.
    """

    def __init__(
        self,
        value: T,
        event_type: str,
        correlation_id: str,
        timestamp: str,
        source: str,
    ):
        """
        Initialize event payload container.

        Args:
            value: The event payload data
            event_type: Type of event
            correlation_id: Correlation ID for tracing
            timestamp: Event timestamp
            source: Event source identifier
        """
        self._value = value
        self._metadata = {
            "event_type": event_type,
            "correlation_id": correlation_id,
            "timestamp": timestamp,
            "source": source,
        }

    @property
    def value(self) -> T:
        """Get the event payload."""
        return self._value

    @property
    def metadata(self) -> dict[str, Any]:
        """Get event metadata."""
        return self._metadata.copy()

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get specific metadata field."""
        return self._metadata.get(key, default)


def process_service_resolution(container: ProtocolContainer[Any]) -> None:
    """
    Process a service resolution result.

    Demonstrates how to work with ProtocolContainer protocol
    without depending on concrete implementations.

    Args:
        container: Container with resolved service and metadata
    """
    service = container.value
    lifecycle = container.get_metadata("lifecycle", "unknown")
    scope = container.get_metadata("scope", "unknown")
    resolution_time = container.get_metadata("resolution_time_ms")

    print(f"Service resolved: {type(service).__name__}")
    print(f"  Lifecycle: {lifecycle}")
    print(f"  Scope: {scope}")
    if resolution_time is not None:
        print(f"  Resolution time: {resolution_time}ms")


def process_event(container: ProtocolContainer[dict[str, Any]]) -> None:
    """
    Process an event payload container.

    Demonstrates type-safe event processing with metadata.

    Args:
        container: Container with event payload and metadata
    """
    payload = container.value
    event_type = container.get_metadata("event_type", "unknown")
    correlation_id = container.get_metadata("correlation_id", "none")

    print(f"Event received: {event_type}")
    print(f"  Correlation ID: {correlation_id}")
    print(f"  Payload: {payload}")


def main() -> None:
    """Demonstrate ProtocolContainer usage patterns."""
    print("=== ProtocolContainer Usage Examples ===\n")

    # Example 1: Service Resolution Container
    print("Example 1: Service Resolution Container")
    print("-" * 40)

    class DatabaseService:
        """Example database service."""

        def query(self, sql: str) -> list[dict[str, Any]]:
            """Execute a query."""
            return [{"id": 1, "name": "example"}]

    db_service = DatabaseService()
    service_container: ProtocolContainer[DatabaseService] = ServiceResolutionContainer(
        value=db_service,
        lifecycle="singleton",
        scope="global",
        resolution_time_ms=2.5,
    )

    process_service_resolution(service_container)
    print()

    # Example 2: Event Payload Container
    print("Example 2: Event Payload Container")
    print("-" * 40)

    event_data = {"user_id": "12345", "action": "login", "success": True}
    event_container: ProtocolContainer[dict[str, Any]] = EventPayloadContainer(
        value=event_data,
        event_type="user.authentication",
        correlation_id="cor-abc-123",
        timestamp="2025-01-15T10:30:00Z",
        source="auth-service",
    )

    process_event(event_container)
    print()

    # Example 3: Type Safety Demonstration
    print("Example 3: Type Safety Demonstration")
    print("-" * 40)

    # String container
    str_container: ProtocolContainer[str] = ServiceResolutionContainer(
        value="Hello, World!", lifecycle="transient"
    )
    text: str = str_container.value  # Type checker knows this is str
    print(f"String value: {text}")

    # Integer container
    int_container: ProtocolContainer[int] = ServiceResolutionContainer(
        value=42, lifecycle="transient"
    )
    number: int = int_container.value  # Type checker knows this is int
    print(f"Integer value: {number}")

    # Dict container
    dict_container: ProtocolContainer[dict[str, str]] = ServiceResolutionContainer(
        value={"key": "value"}, lifecycle="transient"
    )
    data: dict[str, str] = dict_container.value  # Type checker knows this is dict
    print(f"Dict value: {data}")
    print()

    # Example 4: Protocol Validation
    print("Example 4: Protocol Validation")
    print("-" * 40)

    containers: list[ProtocolContainer[Any]] = [
        service_container,
        event_container,
        str_container,
        int_container,
        dict_container,
    ]

    for i, container in enumerate(containers, 1):
        is_valid = isinstance(container, ProtocolContainer)
        print(f"Container {i} is valid ProtocolContainer: {is_valid}")

    print("\n=== All Examples Complete ===")


if __name__ == "__main__":
    main()
