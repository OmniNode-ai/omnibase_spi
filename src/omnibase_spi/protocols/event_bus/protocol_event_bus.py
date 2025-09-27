from typing import (
    Any,
    Awaitable,
    Callable,
    Literal,
    Optional,
    Protocol,
    runtime_checkable,
)
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
    def content_type(self) -> str:
        """MIME type: 'application/json', 'application/avro', etc."""
        ...

    @property
    def correlation_id(self) -> UUID:
        """UUID format for distributed business tracing."""
        ...

    @property
    def message_id(self) -> UUID:
        """UUID format for unique message identification."""
        ...

    @property
    def timestamp(self) -> ProtocolDateTime:
        """Message creation timestamp (datetime object)."""
        ...

    @property
    def source(self) -> str:
        """Source agent/service identifier."""
        ...

    @property
    def event_type(self) -> str:
        """Event classification (e.g., 'core.node.start')."""
        ...

    @property
    def schema_version(self) -> ProtocolSemVer:
        """Message schema version for compatibility."""
        ...

    @property
    def destination(self) -> str | None:
        """Target agent/service (for direct routing)."""
        ...

    @property
    def trace_id(self) -> str | None:
        """OpenTelemetry trace ID (32 hex chars, no hyphens)."""
        ...

    @property
    def span_id(self) -> str | None:
        """OpenTelemetry span ID (16 hex chars, no hyphens)."""
        ...

    @property
    def parent_span_id(self) -> str | None:
        """Parent span ID (16 hex chars, no hyphens)."""
        ...

    @property
    def operation_name(self) -> str | None:
        """Operation being performed (for tracing context)."""
        ...

    @property
    def priority(self) -> Literal["low", "normal", "high", "critical"] | None:
        """Message priority."""
        ...

    @property
    def routing_key(self) -> str | None:
        """Kafka/messaging routing key."""
        ...

    @property
    def partition_key(self) -> str | None:
        """Explicit partition assignment key."""
        ...

    @property
    def retry_count(self) -> int | None:
        """Number of retry attempts (for error handling)."""
        ...

    @property
    def max_retries(self) -> int | None:
        """Maximum retry attempts allowed."""
        ...

    @property
    def ttl_seconds(self) -> int | None:
        """Message time-to-live in seconds."""
        ...


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
        # Implementation example (not part of SPI)
        class KafkaAdapter:
            async def publish(self, topic: str, key: Optional[bytes],
                            value: bytes, headers: "ProtocolEventBusHeaders") -> None:
                # Kafka-specific publishing logic
                producer = self._get_producer()
                await producer.send(topic, key=key, value=value, headers=headers)

            async def subscribe(self, topic: str, group_id: str,
                              on_message: Callable) -> Callable:
                # Kafka-specific subscription logic
                consumer = self._create_consumer(group_id)
                consumer.subscribe([topic])
                # Return unsubscribe function
                return lambda: consumer.unsubscribe()

        # Usage in application code
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
    ) -> None:
        """
        Publish message to topic.

        Args:
            topic: Target topic following ONEX naming conventions
            key: Optional message key for partitioning
            value: Serialized message payload
            headers: Message metadata and routing headers
        """
        ...

    async def subscribe(
        self,
        topic: str,
        group_id: str,
        on_message: Callable[[ProtocolEventMessage], Awaitable[None]],
    ) -> Callable[[], Awaitable[None]]:
        """
        Subscribe to topic with message node.

        Args:
            topic: Source topic following ONEX naming conventions
            group_id: Consumer group for load balancing
            on_message: Async message node

        Returns:
            Unsubscribe function to clean up subscription
        """
        ...

    async def close(self) -> None:
        """Close adapter and clean up resources."""
        ...


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
    def adapter(self) -> ProtocolKafkaEventBusAdapter:
        """Get the event bus adapter implementation."""
        ...

    @property
    def environment(self) -> str:
        """Get environment name for topic isolation."""
        ...

    @property
    def group(self) -> str:
        """Get node group name for mini-mesh isolation."""
        ...

    async def publish(
        self,
        topic: str,
        key: bytes | None,
        value: bytes,
        headers: "ProtocolEventBusHeaders | None" = None,
    ) -> None:
        """
        Publish message to topic.

        Args:
            topic: Target topic (supports ONEX naming conventions)
            key: Optional message key for partitioning
            value: Serialized message payload
            headers: Optional message headers
        """
        ...

    async def subscribe(
        self,
        topic: str,
        group_id: str,
        on_message: Callable[[ProtocolEventMessage], Awaitable[None]],
    ) -> Callable[[], Awaitable[None]]:
        """
        Subscribe to topic with message node.

        Args:
            topic: Source topic (supports ONEX naming conventions)
            group_id: Consumer group for load balancing
            on_message: Message node

        Returns:
            Unsubscribe function
        """
        ...

    async def broadcast_to_environment(
        self,
        command: str,
        payload: dict[str, Any],
        target_environment: str | None = None,
    ) -> None:
        """
        Broadcast command to entire environment.

        Args:
            command: Command type (e.g., 'introspection')
            payload: Command payload
            target_environment: Target env (default: current environment)
        """
        ...

    async def send_to_group(
        self, command: str, payload: dict[str, Any], target_group: str
    ) -> None:
        """
        Send command to specific node group.

        Args:
            command: Command type
            payload: Command payload
            target_group: Target node group name
        """
        ...

    async def close(self) -> None:
        """
        Close event bus and clean up resources.
        """
        ...
