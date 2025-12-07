"""
Event Bus Producer Handler Protocol - ONEX SPI Interface.

Protocol definition for event bus message production operations. This is a specialized
handler protocol that extends the ProtocolHandler pattern for backend-agnostic message
production (supports Kafka, Redis, RabbitMQ, and other message brokers).

The producer handler provides:
    - Single and batch message production
    - Transactional message delivery (when supported by backend)
    - Exactly-once semantics (when supported by backend)
    - Delivery confirmation callbacks
    - Health monitoring

Key Protocols:
    - ProtocolEventBusProducerHandler: Producer handler interface

Message Structure:
    Messages sent through the producer handler use the following structure:
        - topic (str): Target topic/queue name
        - key (bytes | None): Optional partition key for message ordering
        - value (bytes): Message payload (serialized data)
        - headers (dict[str, bytes] | None): Optional message headers/metadata
        - partition (int | None): Optional explicit partition assignment

Callback Pattern:
    The producer supports asynchronous delivery confirmation through callbacks:
        - on_success: Called when message is successfully delivered to broker
        - on_error: Called when message delivery fails

Example:
    ```python
    from omnibase_spi.protocols.event_bus import ProtocolEventBusProducerHandler

    # Get producer handler from dependency injection
    producer: ProtocolEventBusProducerHandler = get_producer_handler()

    # Send single message
    await producer.send(
        topic="user-events",
        value=b'{"event": "user_created", "user_id": "123"}',
        key=b"user:123",
        headers={"correlation_id": b"abc123"},
    )

    # Send batch of messages
    messages = [
        {"topic": "events", "value": b"msg1", "key": b"k1"},
        {"topic": "events", "value": b"msg2", "key": b"k2"},
    ]
    await producer.send_batch(messages)

    # Transactional send (if supported)
    if producer.supports_transactions:
        await producer.begin_transaction()
        try:
            await producer.send(topic="events", value=b"msg")
            await producer.commit_transaction()
        except Exception:
            await producer.abort_transaction()
            raise

    # Cleanup
    await producer.flush()
    await producer.close()
    ```

See Also:
    - ProtocolHandler: Base handler protocol
    - ProtocolEventPublisher: High-level event publishing with retry/circuit breaker
    - ProtocolKafkaAdapter: Kafka-specific adapter implementation
    - ProtocolEventBusService: Service layer for event bus operations
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    # Future Core models - using Any until models are defined
    # from omnibase_core.models.event_bus import (
    #     ModelProducerMessage,
    #     ModelDeliveryResult,
    # )
    pass


# Type aliases for message structure
ProducerMessage = dict[str, Any]
"""
Message structure for producer operations.

Expected keys:
    - topic (str): Target topic/queue name (required)
    - value (bytes): Message payload (required)
    - key (bytes | None): Optional partition key
    - headers (dict[str, bytes] | None): Optional headers
    - partition (int | None): Optional explicit partition
"""

DeliveryCallback = Callable[[str, bytes | None, bytes, Exception | None], None]
"""
Callback signature for delivery confirmation.

Args:
    topic: Target topic name
    key: Message key (if provided)
    value: Message payload
    error: Exception if delivery failed, None on success
"""


@runtime_checkable
class ProtocolEventBusProducerHandler(Protocol):
    """
    Protocol for event bus message producer handlers.

    Defines the contract for backend-agnostic message production operations.
    Implementations provide adapters for specific message brokers (Kafka, Redis,
    RabbitMQ, etc.) while maintaining a consistent interface.

    This protocol extends the ProtocolHandler pattern for specialized
    event bus production operations, supporting:

        - Single and batch message sending
        - Transaction support (Kafka transactions, Redis pipelines, etc.)
        - Exactly-once delivery semantics (when backend supports)
        - Asynchronous delivery confirmation via callbacks
        - Resource management (flush, close)
        - Health monitoring

    Handler Type:
        Implementations should return ``"event_bus_producer"`` from the
        ``handler_type`` property.

    Backend Support:
        - Kafka: Full transaction support, exactly-once semantics, partitioning
        - Redis Streams: Basic transactions via pipelines, at-least-once delivery
        - RabbitMQ: Publisher confirms, transactions via channels
        - In-Memory: Testing and development, no durability guarantees

    Example:
        ```python
        from omnibase_spi.protocols.event_bus import ProtocolEventBusProducerHandler

        async def publish_user_event(
            producer: ProtocolEventBusProducerHandler,
            user_id: str,
            event_data: dict,
        ) -> None:
            # Serialize payload
            payload = json.dumps(event_data).encode("utf-8")

            # Send with partition key for ordering
            await producer.send(
                topic="user-events",
                value=payload,
                key=user_id.encode("utf-8"),
                headers={"event_type": b"user_updated"},
            )

            # Ensure delivery
            await producer.flush()
        ```

    Transactional Example:
        ```python
        async def transactional_publish(
            producer: ProtocolEventBusProducerHandler,
            messages: list[dict],
        ) -> None:
            if not producer.supports_transactions:
                raise RuntimeError("Backend does not support transactions")

            await producer.begin_transaction()
            try:
                for msg in messages:
                    await producer.send(
                        topic=msg["topic"],
                        value=msg["value"],
                        key=msg.get("key"),
                    )
                await producer.commit_transaction()
            except Exception:
                await producer.abort_transaction()
                raise
        ```

    See Also:
        - ProtocolHandler: Base handler protocol pattern
        - ProtocolEventPublisher: High-level publishing with retry/circuit breaker
        - ProtocolKafkaAdapter: Kafka-specific implementation details
    """

    @property
    def handler_type(self) -> str:
        """
        The type of handler as a string identifier.

        Used for handler identification, routing, and metrics collection.
        Producer handlers should return ``"event_bus_producer"``.

        Returns:
            String identifier ``"event_bus_producer"``.

        Example:
            ```python
            producer: ProtocolEventBusProducerHandler = get_producer()
            assert producer.handler_type == "event_bus_producer"
            ```
        """
        ...

    @property
    def supports_transactions(self) -> bool:
        """
        Whether this producer supports transactional message delivery.

        Transactional delivery ensures that a batch of messages is either
        fully delivered or fully rolled back, providing atomicity guarantees.

        Backend support:
            - Kafka: True (requires transactional.id configuration)
            - Redis: True (via MULTI/EXEC pipelines)
            - RabbitMQ: True (via channel transactions)
            - In-Memory: False (typically)

        Returns:
            True if transactions are supported, False otherwise.

        Example:
            ```python
            if producer.supports_transactions:
                await producer.begin_transaction()
                # ... send messages ...
                await producer.commit_transaction()
            else:
                # Fall back to non-transactional send
                await producer.send(topic="events", value=payload)
            ```
        """
        ...

    @property
    def supports_exactly_once(self) -> bool:
        """
        Whether this producer supports exactly-once delivery semantics.

        Exactly-once semantics guarantee that each message is delivered
        exactly once, with no duplicates even in failure scenarios.

        Backend support:
            - Kafka: True (requires enable.idempotence=true)
            - Redis: False (at-least-once only)
            - RabbitMQ: False (at-least-once with confirms)
            - In-Memory: True (within process lifetime)

        Note:
            Exactly-once semantics typically require both producer and
            consumer cooperation. This property indicates producer-side
            support only.

        Returns:
            True if exactly-once delivery is supported, False otherwise.

        Example:
            ```python
            if producer.supports_exactly_once:
                print("Producer provides exactly-once guarantees")
            else:
                print("Producer provides at-least-once delivery")
                # Consider idempotent message handling on consumer side
            ```
        """
        ...

    async def send(
        self,
        topic: str,
        value: bytes,
        key: bytes | None = None,
        headers: dict[str, bytes] | None = None,
        partition: int | None = None,
        on_success: DeliveryCallback | None = None,
        on_error: DeliveryCallback | None = None,
    ) -> None:
        """
        Send a single message to the specified topic.

        Publishes a message to the message broker. The message may be
        buffered internally and sent asynchronously. Use ``flush()`` to
        ensure delivery before shutdown.

        Args:
            topic: Target topic/queue name. Must be a valid topic identifier
                for the underlying message broker.
            value: Message payload as bytes. The caller is responsible for
                serialization (JSON, Avro, Protobuf, etc.).
            key: Optional partition key for message ordering. Messages with
                the same key are guaranteed to be delivered to the same
                partition (and thus processed in order).
            headers: Optional message headers as a dictionary of string keys
                to bytes values. Used for metadata like correlation IDs,
                content types, or tracing information.
            partition: Optional explicit partition assignment. Overrides
                key-based partitioning. Use with caution as it may affect
                load balancing.
            on_success: Optional callback invoked when the message is
                successfully delivered to the broker. Receives (topic, key,
                value, None).
            on_error: Optional callback invoked when message delivery fails.
                Receives (topic, key, value, exception).

        Raises:
            ProducerError: If the message cannot be queued for delivery.
            ProducerNotInitializedError: If the producer has not been initialized.
            TopicNotFoundError: If the topic does not exist and auto-creation
                is disabled.

        Example:
            ```python
            # Simple send
            await producer.send(
                topic="user-events",
                value=b'{"user_id": "123", "action": "login"}',
            )

            # Send with key for ordering
            await producer.send(
                topic="user-events",
                value=b'{"action": "update"}',
                key=b"user:123",
            )

            # Send with delivery callback
            def on_delivered(topic, key, value, error):
                if error:
                    logger.error(f"Delivery failed: {error}")
                else:
                    logger.info(f"Message delivered to {topic}")

            await producer.send(
                topic="events",
                value=payload,
                on_success=on_delivered,
                on_error=on_delivered,
            )
            ```

        Note:
            The send operation may be asynchronous depending on the backend.
            The method returns when the message is queued, not necessarily
            when it is delivered. Use callbacks or ``flush()`` to confirm
            delivery.
        """
        ...

    async def send_batch(
        self,
        messages: Sequence[ProducerMessage],
        on_success: DeliveryCallback | None = None,
        on_error: DeliveryCallback | None = None,
    ) -> int:
        """
        Send multiple messages efficiently as a batch.

        Optimized for high-throughput scenarios where many messages need
        to be sent. The batch may be sent atomically if transactions are
        supported and active.

        Args:
            messages: Sequence of messages to send. Each message is a
                dictionary with keys:
                    - topic (str): Target topic (required)
                    - value (bytes): Message payload (required)
                    - key (bytes | None): Optional partition key
                    - headers (dict[str, bytes] | None): Optional headers
                    - partition (int | None): Optional explicit partition
            on_success: Optional callback invoked for each successfully
                delivered message.
            on_error: Optional callback invoked for each failed delivery.

        Returns:
            Number of messages successfully queued for delivery.

        Raises:
            ProducerError: If the batch cannot be queued for delivery.
            ProducerNotInitializedError: If the producer has not been initialized.
            ValidationError: If any message in the batch is malformed.

        Example:
            ```python
            messages = [
                {
                    "topic": "user-events",
                    "value": b'{"user_id": "1", "action": "create"}',
                    "key": b"user:1",
                },
                {
                    "topic": "user-events",
                    "value": b'{"user_id": "2", "action": "create"}',
                    "key": b"user:2",
                },
                {
                    "topic": "audit-log",
                    "value": b'{"action": "batch_create", "count": 2}',
                },
            ]

            sent_count = await producer.send_batch(messages)
            print(f"Queued {sent_count} messages")
            await producer.flush()
            ```

        Performance:
            Batch sending is significantly more efficient than individual
            sends for high-throughput scenarios. Consider using batch sizes
            of 100-1000 messages depending on message size and latency
            requirements.
        """
        ...

    async def flush(self, timeout_seconds: float = 30.0) -> None:
        """
        Flush all pending messages to ensure delivery.

        Blocks until all buffered messages have been delivered to the
        broker or the timeout expires. Use this before shutdown to ensure
        no messages are lost.

        Args:
            timeout_seconds: Maximum time to wait for pending messages to
                be delivered. Defaults to 30.0 seconds.

        Raises:
            TimeoutError: If flush does not complete within the timeout.
            ProducerNotInitializedError: If the producer has not been initialized.

        Example:
            ```python
            # Send multiple messages
            for msg in messages:
                await producer.send(topic="events", value=msg)

            # Ensure all are delivered
            await producer.flush()
            print("All messages delivered")
            ```

        Note:
            This method is idempotent. Calling flush when there are no
            pending messages returns immediately.
        """
        ...

    async def close(self, timeout_seconds: float = 30.0) -> None:
        """
        Close the producer and release all resources.

        Flushes any pending messages, closes connections to the broker,
        and releases allocated resources. After close, the producer
        cannot be used.

        Args:
            timeout_seconds: Maximum time to wait for cleanup to complete.
                Defaults to 30.0 seconds.

        Raises:
            TimeoutError: If cleanup does not complete within the timeout.

        Example:
            ```python
            try:
                await producer.send(topic="events", value=payload)
            finally:
                await producer.close()
            ```

        Note:
            Always call close during graceful shutdown to ensure proper
            resource cleanup and message delivery.
        """
        ...

    async def health_check(self) -> dict[str, Any]:
        """
        Check producer health and connectivity.

        Performs a lightweight check to verify the producer is operational
        and can communicate with the message broker.

        Returns:
            Dictionary containing health status:
                - healthy (bool): Overall health status
                - latency_ms (float | None): Broker response time in milliseconds
                - connected (bool): Whether connected to broker
                - pending_messages (int): Number of messages awaiting delivery
                - details (dict | None): Additional diagnostic information
                - last_error (str | None): Most recent error if unhealthy

        Example:
            ```python
            health = await producer.health_check()

            if health["healthy"]:
                print(f"Producer OK, latency: {health.get('latency_ms')}ms")
                print(f"Pending: {health.get('pending_messages', 0)} messages")
            else:
                print(f"Producer unhealthy: {health.get('last_error')}")
            ```

        Security:
            The ``last_error`` field may contain sensitive information.
            Implementations should sanitize error messages to remove:
                - Credentials and authentication details
                - Internal file paths and system configuration
                - PII or sensitive business data

        Caching:
            Implementations should cache health check results for 5-30
            seconds to avoid overwhelming the broker with health probes.
        """
        ...

    async def begin_transaction(self) -> None:
        """
        Begin a new transaction for atomic message delivery.

        Starts a transaction scope where all subsequent ``send()`` calls
        are part of the transaction. The transaction must be completed
        with ``commit_transaction()`` or ``abort_transaction()``.

        Raises:
            TransactionNotSupportedError: If the backend does not support
                transactions (check ``supports_transactions`` first).
            TransactionInProgressError: If a transaction is already active.
            ProducerNotInitializedError: If the producer has not been initialized.

        Example:
            ```python
            if producer.supports_transactions:
                await producer.begin_transaction()
                try:
                    await producer.send(topic="events", value=msg1)
                    await producer.send(topic="events", value=msg2)
                    await producer.commit_transaction()
                except Exception:
                    await producer.abort_transaction()
                    raise
            ```

        Note:
            Transaction support varies by backend. Kafka requires the
            ``transactional.id`` configuration. Redis uses MULTI/EXEC
            pipelines. RabbitMQ uses channel transactions.
        """
        ...

    async def commit_transaction(self) -> None:
        """
        Commit the current transaction.

        Commits all messages sent since ``begin_transaction()`` was called.
        After commit, messages are visible to consumers and the producer
        returns to non-transactional mode.

        Raises:
            TransactionNotSupportedError: If the backend does not support
                transactions.
            NoActiveTransactionError: If no transaction is active.
            TransactionCommitError: If the commit fails (messages may need
                to be resent).
            ProducerNotInitializedError: If the producer has not been initialized.

        Example:
            ```python
            await producer.begin_transaction()
            await producer.send(topic="orders", value=order_data)
            await producer.send(topic="inventory", value=inventory_update)
            await producer.commit_transaction()  # Both or neither
            ```

        Note:
            After commit, the producer is ready for the next transaction
            or non-transactional sends.
        """
        ...

    async def abort_transaction(self) -> None:
        """
        Abort the current transaction.

        Discards all messages sent since ``begin_transaction()`` was called.
        Use this to rollback on error conditions.

        Raises:
            TransactionNotSupportedError: If the backend does not support
                transactions.
            NoActiveTransactionError: If no transaction is active.
            ProducerNotInitializedError: If the producer has not been initialized.

        Example:
            ```python
            await producer.begin_transaction()
            try:
                await producer.send(topic="orders", value=order_data)
                # Validation fails
                if not validate(order_data):
                    raise ValueError("Invalid order")
                await producer.commit_transaction()
            except Exception:
                await producer.abort_transaction()  # Discard all messages
                raise
            ```

        Note:
            After abort, the producer is ready for the next transaction
            or non-transactional sends.
        """
        ...
