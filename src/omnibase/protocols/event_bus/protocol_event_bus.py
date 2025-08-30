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


from typing import Any, Awaitable, Callable, Dict, Optional, Protocol, runtime_checkable


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
    headers: Dict[str, str]
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
                            value: bytes, headers: Dict[str, str]) -> None:
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
            headers={"content-type": "application/json"}
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
        self, topic: str, key: Optional[bytes], value: bytes, headers: Dict[str, str]
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

    def __init__(
        self,
        adapter: ProtocolEventBusAdapter,
        environment: str = "dev",
        group: str = "default",
        **kwargs: Any,
    ):
        """
        Initialize event bus with pluggable adapter.

        Args:
            adapter: EventBusAdapter implementation (Kafka/Redpanda)
            environment: Environment name (dev, staging, prod)
            group: Node group name for mini-mesh isolation
        """
        ...

    # === Distributed Messaging Interface ===

    async def publish(
        self,
        topic: str,
        key: Optional[bytes],
        value: bytes,
        headers: Optional[Dict[str, str]] = None,
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
