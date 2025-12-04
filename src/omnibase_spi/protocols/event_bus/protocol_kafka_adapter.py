"""
Kafka Event Bus Adapter Protocol - ONEX SPI Interface.

Protocol definition for Kafka backend implementations.
Defines the contract for Kafka-specific event bus adapters.
"""

from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Optional,
    Protocol,
    runtime_checkable,
)

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_event_bus_types import (
        ProtocolEventMessage,
    )

# Type aliases to avoid namespace violations
EventBusHeaders = Any  # Generic headers type
EventMessage = Any  # Generic event message type


@runtime_checkable
class ProtocolKafkaConfig(Protocol):
    """
    Protocol for Kafka client configuration parameters.

    Defines security, authentication, and operational settings for
    Kafka connections including SASL/SSL configuration, consumer
    group behavior, and timeout management.

    Attributes:
        security_protocol: Security protocol (PLAINTEXT, SSL, SASL_SSL)
        sasl_mechanism: SASL auth mechanism (PLAIN, SCRAM-SHA-256, etc.)
        sasl_username: SASL authentication username
        sasl_password: SASL authentication password
        ssl_cafile: Path to CA certificate file for SSL
        auto_offset_reset: Consumer offset reset behavior (earliest, latest)
        enable_auto_commit: Whether to auto-commit consumer offsets
        session_timeout_ms: Consumer session timeout in milliseconds
        request_timeout_ms: Request timeout in milliseconds

    Example:
        ```python
        adapter: ProtocolKafkaAdapter = get_kafka_adapter()
        config = adapter.kafka_config

        print(f"Security: {config.security_protocol}")
        print(f"SASL: {config.sasl_mechanism}")
        print(f"Auto-commit: {config.enable_auto_commit}")
        print(f"Session timeout: {config.session_timeout_ms}ms")
        ```

    See Also:
        - ProtocolKafkaAdapter: Kafka adapter using this config
        - ProtocolKafkaClient: Low-level Kafka client
    """

    security_protocol: str
    sasl_mechanism: str
    sasl_username: str | None
    sasl_password: str | None
    ssl_cafile: str | None
    auto_offset_reset: str
    enable_auto_commit: bool
    session_timeout_ms: int
    request_timeout_ms: int


@runtime_checkable
class ProtocolKafkaAdapter(Protocol):
    """
    Protocol for Kafka-based event bus adapter implementations.

    Provides Kafka-specific configuration, connection management, and
    core event bus operations for publishing events and subscribing
    to topics with environment and group isolation.

    Example:
        ```python
        adapter: ProtocolKafkaAdapter = get_kafka_adapter()

        # Access configuration
        print(f"Servers: {adapter.bootstrap_servers}")
        print(f"Environment: {adapter.environment}")
        print(f"Group: {adapter.group}")

        # Build environment-aware topic name
        topic = await adapter.build_topic_name("user-events")

        # Publish event
        await adapter.publish(
            topic=topic,
            key=b"user:123",
            value=b'{"event": "user_created"}',
            headers={"correlation_id": "abc123"}
        )

        # Subscribe to events
        async def handle_message(msg: ProtocolEventMessage):
            print(f"Received: {msg}")

        unsubscribe = await adapter.subscribe(
            topic=topic,
            group_id="my-consumer-group",
            on_message=handle_message
        )

        # Cleanup
        await adapter.close()
        ```

    See Also:
        - ProtocolKafkaConfig: Configuration parameters
        - ProtocolEventBusProvider: ONEX event bus interface
        - ProtocolKafkaClient: Low-level Kafka operations
    """

    @property
    def bootstrap_servers(self) -> str: ...

    @property
    def environment(self) -> str: ...

    @property
    def group(self) -> str: ...

    @property
    def config(self) -> ProtocolKafkaConfig | None: ...

    @property
    def kafka_config(self) -> ProtocolKafkaConfig: ...

    async def build_topic_name(self, topic: str) -> str:
        """
        Build environment-aware topic name with prefixes.

        Args:
            topic: Base topic name.

        Returns:
            Fully qualified topic name with environment/group prefixes.
        """
        ...

    # Core event bus adapter interface methods
    async def publish(
        self,
        topic: str,
        key: bytes | None,
        value: bytes,
        headers: EventBusHeaders,
    ) -> None:
        """
        Publish event message to Kafka topic.

        Args:
            topic: Target topic name.
            key: Optional message key for partitioning.
            value: Message payload as bytes.
            headers: Event headers/metadata.

        Raises:
            PublishError: If message publication fails.
        """
        ...

    async def subscribe(
        self,
        topic: str,
        group_id: str,
        on_message: Callable[["ProtocolEventMessage"], Awaitable[None]],
    ) -> Callable[[], Awaitable[None]]:
        """
        Subscribe to Kafka topic with consumer group.

        Args:
            topic: Topic to subscribe to.
            group_id: Consumer group identifier.
            on_message: Async callback for message handling.

        Returns:
            Async callable to unsubscribe from the topic.

        Raises:
            SubscriptionError: If subscription fails.
        """
        ...

    async def close(self) -> None: ...
