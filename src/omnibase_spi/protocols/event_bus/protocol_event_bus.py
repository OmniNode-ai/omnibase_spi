from typing import Any, Awaitable, Callable, Literal, Protocol, runtime_checkable
from uuid import UUID

from omnibase_spi.protocols.types.protocol_core_types import (
    ProtocolDateTime,
    ProtocolSemVer,
)
from omnibase_spi.protocols.types.protocol_event_bus_types import ProtocolEventMessage


@runtime_checkable
class ProtocolEventBusHeaders(Protocol):
    """
    Protocol for standardized headers for ONEX event bus messages.

    Enforces strict interoperability across all agents and prevents
    integration failures from header naming inconsistencies.
    Based on ONEX messaging patterns and distributed tracing requirements.

    ID Format Specifications:
    - UUID format: "550e8400-e29b-41d4-a716-446655440000" (32 hex digits with hyphens)
    - OpenTelemetry Trace ID: "4bf92f3577b34da6a3ce929d0e0e4736" (32 hex digits, no hyphens)
    - OpenTelemetry Span ID: "00f067aa0ba902b7" (16 hex digits, no hyphens)
    """

    @property
    def content_type(self) -> str: ...

    @property
    def correlation_id(self) -> UUID: ...

    @property
    def message_id(self) -> UUID: ...

    @property
    def timestamp(self) -> ProtocolDateTime: ...

    @property
    def source(self) -> str: ...

    @property
    def event_type(self) -> str: ...

    @property
    def schema_version(self) -> ProtocolSemVer: ...

    @property
    def destination(self) -> str | None: ...

    @property
    def trace_id(self) -> str | None: ...

    @property
    def span_id(self) -> str | None: ...

    @property
    def parent_span_id(self) -> str | None: ...

    @property
    def operation_name(self) -> str | None: ...

    @property
    def priority(self) -> Literal["low", "normal", "high", "critical"] | None: ...

    @property
    def routing_key(self) -> str | None: ...

    @property
    def partition_key(self) -> str | None: ...

    @property
    def retry_count(self) -> int | None: ...

    @property
    def max_retries(self) -> int | None: ...

    @property
    def ttl_seconds(self) -> int | None: ...


@runtime_checkable
class ProtocolKafkaEventBusAdapter(Protocol):
    """
        Protocol for Event Bus Adapters supporting pluggable Kafka/Redpanda backends.

        Implements the ONEX Messaging Design v0.3 Event Bus Adapter interface
        enabling drop-in support for both Kafka and Redpanda without code changes.

        Environment isolation and node group mini-meshes are supported through
        topic naming conventions and group isolation patterns.

        Usage Example:
        ```python
        # Protocol usage example (SPI-compliant)
        service: "EventBus" = get_event_bus()

        # Usage demonstrates protocol interface without implementation details
        # All operations work through the protocol contract
        # Implementation details are abstracted away from the interface

        adapter: "ProtocolKafkaEventBusAdapter" = KafkaAdapter()

        # Publishing events
        await adapter.publish(
            topic="user-events",
            key=b"user-123",
            value=json.dumps({"event": "user_created"}).encode(),
            headers={
                "content_type": "application/json",
                "correlation_id": uuid.uuid4(),
                "message_id": uuid.uuid4(),
                "timestamp": datetime.now(),
                "source": "example-service",
                "event_type": "user.created",
                "schema_version": SemVerImplementation(1, 0, 0)  # Implementation example
            }
        )

        # Subscribing to events
        async def handle_message(msg: "ProtocolEventMessage") -> None:
            data = json.loads(msg.value.decode())
            print(f"Received: {data}")
            await msg.ack()

        unsubscribe = await adapter.subscribe(
            topic="user-events",
            group_id="user-service",
        on_message=handle_message
        )

    # Later cleanup
        await unsubscribe()
        await adapter.close()
        ```

    Topic Naming Conventions:
    - Environment isolation: `{env}-{topic}` (e.g., "prod-user-events")
    - Node group isolation: `{group}-{topic}` (e.g., "auth-user-events")
    - Combined: `{env}-{group}-{topic}` (e.g., "prod-auth-user-events")
    """

    async def publish(
        self,
        topic: str,
        key: bytes | None,
        value: bytes,
        headers: "ProtocolEventBusHeaders",
    ) -> None: ...

    async def subscribe(
        self,
        topic: str,
        group_id: str,
        on_message: Callable[[ProtocolEventMessage], Awaitable[None]],
    ) -> Callable[[], Awaitable[None]]: ...

    async def close(self) -> None: ...


@runtime_checkable
class ProtocolEventBus(Protocol):
    """
    ONEX event bus protocol for distributed messaging infrastructure.

    Implements the ONEX Messaging Design v0.3:
    - Environment isolation (dev, staging, prod)
    - Node group mini-meshes
    - Kafka/Redpanda adapter pattern
    - Standardized topic naming and headers
    """

    @property
    def adapter(self) -> ProtocolKafkaEventBusAdapter: ...

    @property
    def environment(self) -> str: ...

    @property
    def group(self) -> str: ...

    async def publish(
        self,
        topic: str,
        key: bytes | None,
        value: bytes,
        headers: "ProtocolEventBusHeaders | None" = None,
    ) -> None: ...

    async def subscribe(
        self,
        topic: str,
        group_id: str,
        on_message: Callable[[ProtocolEventMessage], Awaitable[None]],
    ) -> Callable[[], Awaitable[None]]: ...

    async def broadcast_to_environment(
        self,
        command: str,
        payload: dict[str, Any],
        target_environment: str | None = None,
    ) -> None: ...

    async def send_to_group(
        self, command: str, payload: dict[str, Any], target_group: str
    ) -> None: ...

    async def close(self) -> None: ...
