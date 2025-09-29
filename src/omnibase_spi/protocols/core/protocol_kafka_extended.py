"""
Extended Kafka protocol definitions for comprehensive event streaming.

Provides enhanced Kafka protocols with consumer operations, batch processing,
transactions, partitioning strategies, and advanced configuration.
"""

from typing import Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_core_types import ContextValue


@runtime_checkable
class ProtocolKafkaMessage(Protocol):
    """
    Protocol for Kafka message data.

    Represents a single message with key, value, headers, and metadata
    for comprehensive message handling across producers and consumers.
    """

    key: bytes | None
    value: bytes
    topic: str
    partition: int | None
    offset: int | None
    timestamp: int | None
    headers: dict[str, bytes]


@runtime_checkable
class ProtocolKafkaConsumer(Protocol):
    """
    Protocol for Kafka consumer operations.

    Supports topic subscription, message consumption, offset management,
    and consumer group coordination for distributed event processing.

    Example:
        ```python
        consumer: "ProtocolKafkaConsumer" = get_kafka_consumer()

        # Subscribe to topics
        await consumer.subscribe_to_topics(
            topics=["events", "notifications"],
            group_id="service_processor"
        )

        # Consume messages
        async for messages in consumer.consume_messages_stream():
            for message in messages:
                await process_message(message)
            await consumer.commit_offsets()
        ```
    """

    async def subscribe_to_topics(self, topics: list[str], group_id: str) -> None: ...

    async def unsubscribe_from_topics(self, topics: list[str]) -> None: ...

    async def consume_messages(
        self, timeout_ms: int, max_messages: int
    ) -> list["ProtocolKafkaMessage"]: ...

    async def consume_messages_stream(
        self, batch_timeout_ms: int
    ) -> list["ProtocolKafkaMessage"]: ...

    async def commit_offsets(self) -> None: ...

    async def seek_to_beginning(self, topic: str, partition: int) -> None: ...

    async def seek_to_end(self, topic: str, partition: int) -> None: ...

    async def seek_to_offset(self, topic: str, partition: int, offset: int) -> None: ...

    async def get_current_offsets(self) -> dict[str, dict[int, int]]: ...

    async def close_consumer(self) -> None: ...


@runtime_checkable
class ProtocolKafkaBatchProducer(Protocol):
    """
    Protocol for batch Kafka producer operations.

    Supports batching multiple messages, custom partitioning strategies,
    transaction management, and high-throughput message production.

    Example:
        ```python
        producer: "ProtocolKafkaBatchProducer" = get_batch_producer()

        # Prepare batch of messages
        messages = [
            create_kafka_message("user.created", user_data),
            create_kafka_message("notification.sent", notification_data)
        ]

        # Send batch
        await producer.send_batch(messages)
        await producer.flush_pending()
        ```
    """

    async def send_batch(self, messages: list["ProtocolKafkaMessage"]) -> None: ...

    async def send_to_partition(
        self,
        topic: str,
        partition: int,
        key: bytes | None,
        value: bytes,
        headers: dict[str, bytes] | None = None,
    ) -> None: ...

    async def send_with_custom_partitioner(
        self,
        topic: str,
        key: bytes | None,
        value: bytes,
        partition_strategy: str,
        headers: dict[str, bytes] | None = None,
    ) -> None: ...

    async def flush_pending(self, timeout_ms: int) -> None: ...

    async def get_batch_metrics(self) -> dict[str, int]: ...


@runtime_checkable
class ProtocolKafkaTransactionalProducer(Protocol):
    """
    Protocol for transactional Kafka producer operations.

    Supports exactly-once semantics with transaction management,
    atomic message production, and consumer-producer coordination.

    Example:
        ```python
        producer: "ProtocolKafkaTransactionalProducer" = get_transactional_producer()

        # Start transaction
        await producer.begin_transaction()

        try:
            await producer.send_transactional("events", event_data)
            await producer.send_transactional("audit", audit_data)
            await producer.commit_transaction()
        except Exception:
            await producer.abort_transaction()
            raise
        ```
    """

    async def init_transactions(self, transaction_id: str) -> None: ...

    async def begin_transaction(self) -> None: ...

    async def send_transactional(
        self,
        topic: str,
        value: bytes,
        key: bytes | None = None,
        headers: dict[str, bytes] | None = None,
    ) -> None: ...

    async def commit_transaction(self) -> None: ...

    async def abort_transaction(self) -> None: ...


@runtime_checkable
class ProtocolKafkaExtendedClient(Protocol):
    """
    Protocol for comprehensive Kafka client with all operations.

    Combines producer, consumer, and administrative operations
    with advanced features like schema registry and monitoring.

    Example:
        ```python
        client: "ProtocolKafkaExtendedClient" = get_extended_kafka_client()

        # Create consumer and producer
        consumer = client.create_consumer()
        producer = client.create_batch_producer()

        # Administrative operations
        await client.create_topic("new_events", partitions=3, replication=2)
        topics = await client.list_topics()
        ```
    """

    async def create_consumer(self) -> ProtocolKafkaConsumer: ...

    async def create_batch_producer(self) -> ProtocolKafkaBatchProducer: ...

    async def create_transactional_producer(
        self,
    ) -> ProtocolKafkaTransactionalProducer: ...

    async def create_topic(
        self,
        topic_name: str,
        partitions: int,
        replication_factor: int,
        config: dict[str, "ContextValue"] | None = None,
    ) -> None: ...

    async def delete_topic(self, topic_name: str) -> None: ...

    async def list_topics(self) -> list[str]: ...

    async def get_topic_metadata(self, topic_name: str) -> dict[str, str | int]: ...

    async def health_check(self) -> bool: ...

    async def close_client(self) -> None: ...
