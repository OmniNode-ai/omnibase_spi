"""
Extended EventBus protocol definitions for comprehensive event streaming.

Provides enhanced EventBus protocols with consumer operations, batch processing,
transactions, partitioning strategies, and advanced configuration.

These protocols are backend-agnostic; concrete implementations (e.g., Kafka,
Redpanda, RabbitMQ) live in omnibase_infra.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.event_bus.protocol_event_bus_types import (
        ProtocolTopicConfig,
    )


@runtime_checkable
class ProtocolEventBusMessage(Protocol):
    """
    Protocol for EventBus message data.

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
class ProtocolEventBusConsumer(Protocol):
    """
    Protocol for EventBus consumer operations.

    Supports topic subscription, message consumption, offset management,
    and consumer group coordination for distributed event processing.

    Example:
        ```python
        consumer: "ProtocolEventBusConsumer" = get_event_bus_consumer()

        # Subscribe to topics
        await consumer.subscribe_to_topics(
            topics=["events", "notifications"],
            group_id="service_processor"
        )

        # Consume messages in batches
        messages = await consumer.consume_messages_stream(batch_timeout_ms=1000)
        for message in messages:
            await process_message(message)
        await consumer.commit_offsets()
        ```
    """

    async def subscribe_to_topics(self, topics: list[str], group_id: str) -> None:
        """Subscribe to one or more topics for message consumption.

        Args:
            topics: List of topic names to subscribe to.
            group_id: Consumer group identifier for coordinated consumption.

        Raises:
            EventBusConnectionError: If the connection to the event bus is lost.
            EventBusSubscriptionError: If subscription to any topic fails.
        """
        ...

    async def unsubscribe_from_topics(self, topics: list[str]) -> None:
        """Unsubscribe from one or more topics.

        Args:
            topics: List of topic names to unsubscribe from.

        Raises:
            EventBusConnectionError: If the connection to the event bus is lost.
        """
        ...

    async def consume_messages(
        self, timeout_ms: int, max_messages: int
    ) -> list["ProtocolEventBusMessage"]:
        """Consume messages from subscribed topics.

        Args:
            timeout_ms: Maximum time in milliseconds to wait for messages.
            max_messages: Maximum number of messages to return in a single call.

        Returns:
            List of consumed messages, may be empty if timeout expires.

        Raises:
            EventBusConnectionError: If the connection to the event bus is lost.
            EventBusConsumerError: If message consumption fails.
        """
        ...

    async def consume_messages_stream(
        self, batch_timeout_ms: int
    ) -> list["ProtocolEventBusMessage"]:
        """Consume a batch of messages with streaming semantics.

        Args:
            batch_timeout_ms: Maximum time in milliseconds to wait for a batch.

        Returns:
            List of consumed messages for the batch, may be empty if timeout expires.

        Raises:
            EventBusConnectionError: If the connection to the event bus is lost.
            EventBusConsumerError: If message consumption fails.
        """
        ...

    async def commit_offsets(self) -> None:
        """Commit current consumer offsets to the event bus.

        Raises:
            EventBusConnectionError: If the connection to the event bus is lost.
            EventBusCommitError: If offset commit fails.
        """
        ...

    async def seek_to_beginning(self, topic: str, partition: int) -> None:
        """Seek to the beginning of a topic partition.

        Args:
            topic: Name of the topic.
            partition: Partition number to seek.

        Raises:
            EventBusConnectionError: If the connection to the event bus is lost.
            EventBusSeekError: If the seek operation fails.
        """
        ...

    async def seek_to_end(self, topic: str, partition: int) -> None:
        """Seek to the end of a topic partition.

        Args:
            topic: Name of the topic.
            partition: Partition number to seek.

        Raises:
            EventBusConnectionError: If the connection to the event bus is lost.
            EventBusSeekError: If the seek operation fails.
        """
        ...

    async def seek_to_offset(self, topic: str, partition: int, offset: int) -> None:
        """Seek to a specific offset in a topic partition.

        Args:
            topic: Name of the topic.
            partition: Partition number to seek.
            offset: Specific offset to seek to.

        Raises:
            EventBusConnectionError: If the connection to the event bus is lost.
            EventBusSeekError: If the seek operation fails or offset is invalid.
        """
        ...

    async def get_current_offsets(self) -> dict[str, dict[int, int]]:
        """Get current consumer offsets for all subscribed topic partitions.

        Returns:
            Dictionary mapping topic names to partition-offset mappings.
            Format: {topic_name: {partition_id: offset}}.

        Raises:
            EventBusConnectionError: If the connection to the event bus is lost.
        """
        ...

    async def close_consumer(self, timeout_seconds: float = 30.0) -> None:
        """Close the EventBus consumer and release resources.

        Args:
            timeout_seconds: Maximum time to wait for cleanup to complete.
                Defaults to 30.0 seconds.

        Raises:
            TimeoutError: If cleanup does not complete within the specified timeout.
        """
        ...

    async def validate_connection(self) -> bool:
        """Validate the event bus consumer connection is healthy.

        Performs a health check on the underlying connection to ensure
        the consumer can communicate with the event bus cluster.

        Returns:
            True if connection is valid and healthy, False otherwise.
        """
        ...


@runtime_checkable
class ProtocolEventBusBatchProducer(Protocol):
    """
    Protocol for batch EventBus producer operations.

    Supports batching multiple messages, custom partitioning strategies,
    transaction management, and high-throughput message production.

    Example:
        ```python
        producer: "ProtocolEventBusBatchProducer" = get_batch_producer()

        # Prepare batch of messages
        messages = [
            create_event_bus_message("user.created", user_data),
            create_event_bus_message("notification.sent", notification_data)
        ]

        # Send batch
        await producer.send_batch(messages)
        await producer.flush_pending(timeout_ms=5000)
        ```
    """

    async def send_batch(self, messages: list["ProtocolEventBusMessage"]) -> None:
        """Send a batch of messages to the event bus.

        Args:
            messages: List of messages to send in a single batch operation.

        Raises:
            EventBusConnectionError: If the connection to the event bus is lost.
            EventBusProducerError: If batch sending fails.
        """
        ...

    async def send_to_partition(
        self,
        topic: str,
        partition: int,
        key: bytes | None,
        value: bytes,
        headers: dict[str, bytes] | None = None,
    ) -> None:
        """Send a message to a specific partition.

        Args:
            topic: Name of the topic to send to.
            partition: Target partition number.
            key: Optional message key for ordering.
            value: Message payload as bytes.
            headers: Optional message headers.

        Raises:
            EventBusConnectionError: If the connection to the event bus is lost.
            EventBusProducerError: If sending fails.
            EventBusPartitionError: If the specified partition does not exist.
        """
        ...

    async def send_with_custom_partitioner(
        self,
        topic: str,
        key: bytes | None,
        value: bytes,
        partition_strategy: str,
        headers: dict[str, bytes] | None = None,
    ) -> None:
        """Send a message using a custom partitioning strategy.

        Args:
            topic: Name of the topic to send to.
            key: Optional message key for partitioning.
            value: Message payload as bytes.
            partition_strategy: Name of the partitioning strategy to use
                (e.g., "round_robin", "hash", "sticky").
            headers: Optional message headers.

        Raises:
            EventBusConnectionError: If the connection to the event bus is lost.
            EventBusProducerError: If sending fails.
            EventBusPartitionError: If the partition strategy is invalid.
        """
        ...

    async def flush_pending(self, timeout_ms: int) -> None:
        """Flush all pending messages to the event bus.

        Args:
            timeout_ms: Maximum time in milliseconds to wait for flush completion.

        Raises:
            EventBusConnectionError: If the connection to the event bus is lost.
            TimeoutError: If flush does not complete within the specified timeout.
        """
        ...

    async def get_batch_metrics(self) -> dict[str, int]:
        """Get metrics for batch producer operations.

        Returns:
            Dictionary containing batch metrics such as messages_sent,
            bytes_sent, batches_completed, and errors_count.

        Raises:
            EventBusConnectionError: If the connection to the event bus is lost.
        """
        ...

    async def validate_connection(self) -> bool:
        """Validate the event bus producer connection is healthy.

        Performs a health check on the underlying connection to ensure
        the producer can communicate with the event bus cluster.

        Returns:
            True if connection is valid and healthy, False otherwise.
        """
        ...

    async def validate_message(self, message: "ProtocolEventBusMessage") -> bool:
        """Validate a message before publishing.

        Performs validation checks on the message to ensure it meets
        the requirements for successful publishing, including topic
        validity, payload size limits, and header format.

        Args:
            message: The message to validate.

        Returns:
            True if message is valid, False otherwise.
        """
        ...


@runtime_checkable
class ProtocolEventBusTransactionalProducer(Protocol):
    """
    Protocol for transactional EventBus producer operations.

    Supports exactly-once semantics with transaction management,
    atomic message production, and consumer-producer coordination.

    Example:
        ```python
        producer: "ProtocolEventBusTransactionalProducer" = get_transactional_producer()

        # Initialize transactions
        await producer.init_transactions("my-transaction-id")

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
        """Initialize the transactional producer with a transaction ID.

        Must be called before any transactional operations. The transaction ID
        must be unique across all producer instances to ensure exactly-once
        semantics.

        Args:
            transaction_id: Unique identifier for this transactional producer.

        Raises:
            EventBusConnectionError: If the connection to the event bus is lost.
            EventBusTransactionError: If transaction initialization fails.
        """
        ...

    async def begin_transaction(self) -> None:
        """Begin a new transaction.

        Must be called after init_transactions and before sending any
        transactional messages.

        Raises:
            EventBusConnectionError: If the connection to the event bus is lost.
            EventBusTransactionError: If a transaction is already in progress
                or if begin fails.
        """
        ...

    async def send_transactional(
        self,
        topic: str,
        value: bytes,
        key: bytes | None = None,
        headers: dict[str, bytes] | None = None,
    ) -> None:
        """Send a message as part of the current transaction.

        The message will only be visible to consumers after commit_transaction
        is called successfully.

        Args:
            topic: Name of the topic to send to.
            value: Message payload as bytes.
            key: Optional message key for ordering and partitioning.
            headers: Optional message headers.

        Raises:
            EventBusConnectionError: If the connection to the event bus is lost.
            EventBusTransactionError: If no transaction is in progress.
            EventBusProducerError: If sending fails.
        """
        ...

    async def commit_transaction(self) -> None:
        """Commit the current transaction.

        All messages sent since begin_transaction will become visible
        to consumers atomically.

        Raises:
            EventBusConnectionError: If the connection to the event bus is lost.
            EventBusTransactionError: If no transaction is in progress
                or if commit fails.
        """
        ...

    async def abort_transaction(self) -> None:
        """Abort the current transaction.

        All messages sent since begin_transaction will be discarded
        and will never be visible to consumers.

        Raises:
            EventBusConnectionError: If the connection to the event bus is lost.
            EventBusTransactionError: If no transaction is in progress
                or if abort fails.
        """
        ...


@runtime_checkable
class ProtocolEventBusExtendedClient(Protocol):
    """
    Protocol for comprehensive EventBus client with all operations.

    Combines producer, consumer, and administrative operations
    with advanced features like schema registry and monitoring.

    Example:
        ```python
        client: "ProtocolEventBusExtendedClient" = get_extended_event_bus_client()

        # Create consumer and producer
        consumer = await client.create_consumer()
        producer = await client.create_batch_producer()

        # Administrative operations
        await client.create_topic("new_events", partitions=3, replication_factor=2)
        topics = await client.list_topics()
        ```
    """

    async def create_consumer(self) -> ProtocolEventBusConsumer:
        """Create a new EventBus consumer instance.

        Returns:
            A configured consumer ready for subscription and message consumption.

        Raises:
            EventBusConnectionError: If the connection to the event bus is lost.
            EventBusClientError: If consumer creation fails.
        """
        ...

    async def create_batch_producer(self) -> ProtocolEventBusBatchProducer:
        """Create a new batch producer instance.

        Returns:
            A configured batch producer ready for message production.

        Raises:
            EventBusConnectionError: If the connection to the event bus is lost.
            EventBusClientError: If producer creation fails.
        """
        ...

    async def create_transactional_producer(
        self,
    ) -> ProtocolEventBusTransactionalProducer:
        """Create a new transactional producer instance.

        Returns:
            A configured transactional producer ready for exactly-once
            message production.

        Raises:
            EventBusConnectionError: If the connection to the event bus is lost.
            EventBusClientError: If transactional producer creation fails.
        """
        ...

    async def create_topic(
        self,
        topic_name: str,
        partitions: int,
        replication_factor: int,
        topic_config: "ProtocolTopicConfig | None" = None,
    ) -> None:
        """Create a new topic with the specified configuration.

        Args:
            topic_name: Name of the topic to create.
            partitions: Number of partitions for the topic.
            replication_factor: Replication factor for the topic.
            topic_config: Optional topic-specific configuration parameters
                including retention, compression, and cleanup policies.

        Raises:
            EventBusConnectionError: If the connection to the event bus is lost.
            EventBusAdminError: If topic creation fails or topic already exists.
        """
        ...

    async def delete_topic(self, topic_name: str) -> None:
        """Delete an existing topic.

        Args:
            topic_name: Name of the topic to delete.

        Raises:
            EventBusConnectionError: If the connection to the event bus is lost.
            EventBusAdminError: If topic deletion fails or topic does not exist.
        """
        ...

    async def list_topics(self) -> list[str]:
        """List all available topics.

        Returns:
            List of topic names available in the event bus.

        Raises:
            EventBusConnectionError: If the connection to the event bus is lost.
        """
        ...

    async def get_topic_metadata(self, topic_name: str) -> dict[str, str | int]:
        """Get metadata for a specific topic.

        Args:
            topic_name: Name of the topic to get metadata for.

        Returns:
            Dictionary containing topic metadata including partition count,
            replication factor, and configuration settings.

        Raises:
            EventBusConnectionError: If the connection to the event bus is lost.
            EventBusAdminError: If the topic does not exist.
        """
        ...

    async def health_check(self) -> bool:
        """Check the health of the EventBus connection.

        Returns:
            True if the connection is healthy, False otherwise.
        """
        ...

    async def validate_connection(self) -> bool:
        """Validate the event bus connection is healthy.

        Performs a comprehensive health check on the underlying connection
        to ensure the client can communicate with the event bus cluster.
        This includes verifying broker connectivity and metadata availability.

        Returns:
            True if connection is valid and healthy, False otherwise.
        """
        ...

    async def validate_message(self, message: ProtocolEventBusMessage) -> bool:
        """Validate a message before publishing.

        Performs validation checks on the message to ensure it meets
        the requirements for successful publishing, including topic
        validity, payload size limits, and header format.

        Args:
            message: The message to validate.

        Returns:
            True if message is valid, False otherwise.
        """
        ...

    async def close_client(self, timeout_seconds: float = 30.0) -> None:
        """Close the extended EventBus client and release all resources.

        Args:
            timeout_seconds: Maximum time to wait for cleanup to complete.
                Defaults to 30.0 seconds.

        Raises:
            TimeoutError: If cleanup does not complete within the specified timeout.
        """
        ...
