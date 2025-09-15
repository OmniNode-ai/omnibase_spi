"""
Extended Kafka protocol definitions for comprehensive event streaming.

Provides enhanced Kafka protocols with consumer operations, batch processing,
transactions, partitioning strategies, and advanced configuration.
"""

from typing import Optional, Protocol, runtime_checkable


@runtime_checkable
class ProtocolKafkaMessage(Protocol):
    """
    Protocol for Kafka message data.

    Represents a single message with key, value, headers, and metadata
    for comprehensive message handling across producers and consumers.
    """

    key: Optional[bytes]
    value: bytes
    topic: str
    partition: Optional[int]
    offset: Optional[int]
    timestamp: Optional[int]
    headers: dict[str, bytes]


@runtime_checkable
class ProtocolKafkaConsumer(Protocol):
    """
    Protocol for Kafka consumer operations.

    Supports topic subscription, message consumption, offset management,
    and consumer group coordination for distributed event processing.

    Example:
        ```python
        consumer: ProtocolKafkaConsumer = get_kafka_consumer()

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

    async def subscribe_to_topics(self, topics: list[str], group_id: str) -> None:
        """
        Subscribe to Kafka topics with consumer group.

        Args:
            topics: List of topic names to subscribe to
            group_id: Consumer group ID for coordination

        Raises:
            OnexError: If subscription fails or topics don't exist
        """
        ...

    async def unsubscribe_from_topics(self, topics: list[str]) -> None:
        """
        Unsubscribe from specific Kafka topics.

        Args:
            topics: List of topic names to unsubscribe from

        Raises:
            OnexError: If unsubscription encounters errors
        """
        ...

    async def consume_messages(
        self, timeout_ms: int = 1000, max_messages: int = 100
    ) -> list[ProtocolKafkaMessage]:
        """
        Consume messages from subscribed topics.

        Args:
            timeout_ms: Maximum time to wait for messages in milliseconds
            max_messages: Maximum number of messages to consume in one batch

        Returns:
            List of consumed messages

        Raises:
            OnexError: If message consumption encounters errors
        """
        ...

    async def consume_messages_stream(
        self, batch_timeout_ms: int = 1000
    ) -> list[ProtocolKafkaMessage]:
        """
        Stream consume messages continuously from subscribed topics.

        Args:
            batch_timeout_ms: Timeout for each batch of messages

        Yields:
            Batches of consumed messages

        Raises:
            OnexError: If streaming consumption encounters errors
        """
        ...

    async def commit_offsets(self) -> None:
        """
        Commit current message offsets to Kafka.

        Acknowledges processing of consumed messages and advances
        consumer position to prevent reprocessing.

        Raises:
            OnexError: If offset commit fails
        """
        ...

    async def seek_to_beginning(self, topic: str, partition: int) -> None:
        """
        Seek to the beginning of a topic partition.

        Args:
            topic: Topic name to seek in
            partition: Partition number to seek in

        Raises:
            OnexError: If seek operation fails
        """
        ...

    async def seek_to_end(self, topic: str, partition: int) -> None:
        """
        Seek to the end of a topic partition.

        Args:
            topic: Topic name to seek in
            partition: Partition number to seek in

        Raises:
            OnexError: If seek operation fails
        """
        ...

    async def seek_to_offset(self, topic: str, partition: int, offset: int) -> None:
        """
        Seek to specific offset in a topic partition.

        Args:
            topic: Topic name to seek in
            partition: Partition number to seek in
            offset: Target offset position

        Raises:
            OnexError: If seek operation fails
        """
        ...

    async def get_current_offsets(self) -> dict[str, dict[int, int]]:
        """
        Get current consumer offsets for all assigned partitions.

        Returns:
            Dictionary mapping topic -> partition -> current offset

        Raises:
            OnexError: If offset retrieval fails
        """
        ...

    async def close_consumer(self) -> None:
        """
        Close consumer and release resources.

        Properly closes connections and commits any pending offsets.

        Raises:
            OnexError: If consumer close encounters errors
        """
        ...


@runtime_checkable
class ProtocolKafkaBatchProducer(Protocol):
    """
    Protocol for batch Kafka producer operations.

    Supports batching multiple messages, custom partitioning strategies,
    transaction management, and high-throughput message production.

    Example:
        ```python
        producer: ProtocolKafkaBatchProducer = get_batch_producer()

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

    async def send_batch(self, messages: list[ProtocolKafkaMessage]) -> None:
        """
        Send batch of messages to Kafka.

        Args:
            messages: List of messages to send in batch

        Raises:
            OnexError: If batch sending fails
        """
        ...

    async def send_to_partition(
        self,
        topic: str,
        partition: int,
        key: Optional[bytes],
        value: bytes,
        headers: Optional[dict[str, bytes]] = None,
    ) -> None:
        """
        Send message to specific partition.

        Args:
            topic: Target topic name
            partition: Target partition number
            key: Optional message key
            value: Message value as bytes
            headers: Optional message headers

        Raises:
            OnexError: If message sending fails
        """
        ...

    async def send_with_custom_partitioner(
        self,
        topic: str,
        key: Optional[bytes],
        value: bytes,
        partition_strategy: str,
        headers: Optional[dict[str, bytes]] = None,
    ) -> None:
        """
        Send message using custom partitioning strategy.

        Args:
            topic: Target topic name
            key: Optional message key
            value: Message value as bytes
            partition_strategy: Partitioning strategy name
            headers: Optional message headers

        Raises:
            OnexError: If message sending fails
        """
        ...

    async def flush_pending(self, timeout_ms: int = 30000) -> None:
        """
        Flush all pending messages and wait for acknowledgments.

        Args:
            timeout_ms: Maximum time to wait for flush completion

        Raises:
            OnexError: If flush operation times out or fails
        """
        ...

    async def get_batch_metrics(self) -> dict[str, int]:
        """
        Get batch producer performance metrics.

        Returns:
            Dictionary with metrics like messages_sent, batches_sent,
            average_batch_size, etc.

        Raises:
            OnexError: If metrics retrieval fails
        """
        ...


@runtime_checkable
class ProtocolKafkaTransactionalProducer(Protocol):
    """
    Protocol for transactional Kafka producer operations.

    Supports exactly-once semantics with transaction management,
    atomic message production, and consumer-producer coordination.

    Example:
        ```python
        producer: ProtocolKafkaTransactionalProducer = get_transactional_producer()

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

    async def init_transactions(self, transaction_id: str) -> None:
        """
        Initialize transactional producer with transaction ID.

        Args:
            transaction_id: Unique transaction identifier

        Raises:
            OnexError: If transaction initialization fails
        """
        ...

    async def begin_transaction(self) -> None:
        """
        Begin a new transaction.

        All subsequent send operations will be part of this transaction
        until commit or abort is called.

        Raises:
            OnexError: If transaction begin fails
        """
        ...

    async def send_transactional(
        self,
        topic: str,
        value: bytes,
        key: Optional[bytes] = None,
        headers: Optional[dict[str, bytes]] = None,
    ) -> None:
        """
        Send message as part of current transaction.

        Args:
            topic: Target topic name
            value: Message value as bytes
            key: Optional message key
            headers: Optional message headers

        Raises:
            OnexError: If transactional send fails
        """
        ...

    async def commit_transaction(self) -> None:
        """
        Commit current transaction.

        Makes all messages sent in this transaction visible to consumers.

        Raises:
            OnexError: If transaction commit fails
        """
        ...

    async def abort_transaction(self) -> None:
        """
        Abort current transaction.

        Discards all messages sent in this transaction.

        Raises:
            OnexError: If transaction abort fails
        """
        ...


@runtime_checkable
class ProtocolKafkaExtendedClient(Protocol):
    """
    Protocol for comprehensive Kafka client with all operations.

    Combines producer, consumer, and administrative operations
    with advanced features like schema registry and monitoring.

    Example:
        ```python
        client: ProtocolKafkaExtendedClient = get_extended_kafka_client()

        # Create consumer and producer
        consumer = client.create_consumer()
        producer = client.create_batch_producer()

        # Administrative operations
        await client.create_topic("new_events", partitions=3, replication=2)
        topics = await client.list_topics()
        ```
    """

    def create_consumer(self) -> ProtocolKafkaConsumer:
        """
        Create Kafka consumer instance.

        Returns:
            Kafka consumer protocol implementation
        """
        ...

    def create_batch_producer(self) -> ProtocolKafkaBatchProducer:
        """
        Create batch Kafka producer instance.

        Returns:
            Batch producer protocol implementation
        """
        ...

    def create_transactional_producer(self) -> ProtocolKafkaTransactionalProducer:
        """
        Create transactional Kafka producer instance.

        Returns:
            Transactional producer protocol implementation
        """
        ...

    async def create_topic(
        self,
        topic_name: str,
        partitions: int,
        replication_factor: int,
        config: Optional[dict[str, str]] = None,
    ) -> None:
        """
        Create new Kafka topic.

        Args:
            topic_name: Name of the topic to create
            partitions: Number of partitions for the topic
            replication_factor: Replication factor for the topic
            config: Optional topic configuration

        Raises:
            OnexError: If topic creation fails
        """
        ...

    async def delete_topic(self, topic_name: str) -> None:
        """
        Delete Kafka topic.

        Args:
            topic_name: Name of the topic to delete

        Raises:
            OnexError: If topic deletion fails
        """
        ...

    async def list_topics(self) -> list[str]:
        """
        List all available Kafka topics.

        Returns:
            List of topic names

        Raises:
            OnexError: If topic listing fails
        """
        ...

    async def get_topic_metadata(self, topic_name: str) -> dict[str, str | int]:
        """
        Get metadata for specific topic.

        Args:
            topic_name: Name of the topic

        Returns:
            Dictionary with topic metadata (partitions, replication, etc.)

        Raises:
            OnexError: If metadata retrieval fails
        """
        ...

    async def health_check(self) -> bool:
        """
        Check if Kafka client is healthy and connected.

        Returns:
            True if client is healthy, False otherwise
        """
        ...

    async def close_client(self) -> None:
        """
        Close Kafka client and clean up resources.

        Properly closes all producers, consumers, and connections.

        Raises:
            OnexError: If client close encounters errors
        """
        ...
