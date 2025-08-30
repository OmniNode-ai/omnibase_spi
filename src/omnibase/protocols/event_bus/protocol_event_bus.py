# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:27.128231'
# description: Stamped by NodePython
# entrypoint: python://protocol_event_bus
# hash: d08b73065d9e8de6ac3b18881f8669d08f07ca6678ec78d1f0cdb96e3b9016eb
# last_modified_at: '2025-05-29T14:14:00.220362+00:00'
# lifecycle: active
# meta_type: node
# metadata_version: 0.1.0
# name: protocol_event_bus.py
# namespace: python://omnibase.protocol.protocol_event_bus
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 2d9c79c5-6422-462b-b10c-e080a10c1d42
# version: 1.0.0
# === /OmniNode:Metadata ===


from datetime import datetime
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Literal,
    NotRequired,
    Optional,
    Protocol,
    Required,
    TypedDict,
    runtime_checkable,
)
from uuid import UUID

from omnibase.protocols.types.core_types import ProtocolDateTime, ProtocolSemVer


class ProtocolEventHeaders(TypedDict):
    """
    Standardized headers for ONEX event bus messages.

    Enforces strict interoperability across all agents and prevents
    integration failures from header naming inconsistencies.
    Based on ONEX messaging patterns and distributed tracing requirements.

    ID Format Specifications:
    - UUID format: "550e8400-e29b-41d4-a716-446655440000" (32 hex digits with hyphens)
    - OpenTelemetry Trace ID: "4bf92f3577b34da6a3ce929d0e0e4736" (32 hex digits, no hyphens)
    - OpenTelemetry Span ID: "00f067aa0ba902b7" (16 hex digits, no hyphens)
    """

    # REQUIRED - Essential for system operation and observability
    content_type: Required[
        str
    ]  # MIME type: "application/json", "application/avro", etc.
    correlation_id: Required[UUID]  # UUID format for distributed business tracing
    message_id: Required[UUID]  # UUID format for unique message identification
    timestamp: Required[
        ProtocolDateTime
    ]  # Message creation timestamp (datetime object)
    source: Required[str]  # Source agent/service identifier
    event_type: Required[str]  # Event classification (e.g., "core.node.start")
    schema_version: Required[ProtocolSemVer]  # Message schema version for compatibility

    # OPTIONAL - Standardized but not mandatory for all messages
    destination: NotRequired[str]  # Target agent/service (for direct routing)
    trace_id: NotRequired[str]  # OpenTelemetry trace ID (32 hex chars, no hyphens)
    span_id: NotRequired[str]  # OpenTelemetry span ID (16 hex chars, no hyphens)
    parent_span_id: NotRequired[str]  # Parent span ID (16 hex chars, no hyphens)
    operation_name: NotRequired[str]  # Operation being performed (for tracing context)
    priority: NotRequired[
        Literal["low", "normal", "high", "critical"]
    ]  # Message priority
    routing_key: NotRequired[str]  # Kafka/messaging routing key
    partition_key: NotRequired[str]  # Explicit partition assignment key
    retry_count: NotRequired[int]  # Number of retry attempts (for error handling)
    max_retries: NotRequired[int]  # Maximum retry attempts allowed
    ttl_seconds: NotRequired[int]  # Message time-to-live in seconds


@runtime_checkable
class ProtocolEventMessage(Protocol):
    """
    Protocol for ONEX event bus message objects.

    Defines the contract that all event message implementations must satisfy
    for Kafka/Redpanda compatibility following the ONEX Messaging Design v0.3.

    Implementations can use dataclass, NamedTuple, or custom classes as long
    as they provide the required attributes and methods.
    """

    topic: str
    key: Optional[bytes]
    value: bytes
    headers: ProtocolEventHeaders
    offset: Optional[str]
    partition: Optional[int]

    async def ack(self) -> None:
        """Acknowledge message processing (adapter-specific implementation)."""
        ...


@runtime_checkable
class ProtocolEventBusAdapter(Protocol):
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
                            value: bytes, headers: ProtocolEventHeaders) -> None:
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
        adapter: ProtocolEventBusAdapter = KafkaAdapter()

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
        async def handle_message(msg: ProtocolEventMessage) -> None:
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
        key: Optional[bytes],
        value: bytes,
        headers: ProtocolEventHeaders,
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
    def adapter(self) -> ProtocolEventBusAdapter:
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

    # === Distributed Messaging Interface ===

    async def publish(
        self,
        topic: str,
        key: Optional[bytes],
        value: bytes,
        headers: Optional[ProtocolEventHeaders] = None,
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
        payload: Dict[str, Any],
        target_environment: Optional[str] = None,
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
        self, command: str, payload: Dict[str, Any], target_group: str
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
