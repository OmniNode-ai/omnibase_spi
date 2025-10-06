"""
Protocol definitions for Kafka client abstraction.

Provides Kafka client protocols that can be implemented by different
Kafka client backends (aiokafka, confluent-kafka-python, etc.) and injected via ONEXContainer.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class ProtocolKafkaClient(Protocol):
    """
    Protocol interface for Kafka client implementations.

    Provides standardized interface for Kafka producer/consumer operations
    that can be implemented by different Kafka client libraries.

    Example:
        ```python
        # Implementation example (not part of SPI)
        # All methods defined in the protocol contract must be implemented

        # Usage in application
        kafka_client: "ProtocolKafkaClient" = get_kafka_client()

        # Start the client
        await kafka_client.start()

        # Send messages with synchronous confirmation
        message_data = b'{"event": "user_created", "user_id": 123}'
        await kafka_client.send_and_wait(
            topic="user-events",
            value=message_data,
            key=b"user:123"
        )

        # Send multiple messages
        messages = [
            (b'{"event": "order_created", "order_id": 456}', b"order:456"),
            (b'{"event": "payment_processed", "payment_id": 789}', b"payment:789")
        ]

        for value, key in messages:
            await kafka_client.send_and_wait("events", value, key)

        # Get configuration
        servers = kafka_client.bootstrap_servers()
        print(f"Connected to Kafka cluster: {servers}")

        # Graceful shutdown
        await kafka_client.stop()
        ```

    Producer Operations:
        - Simple message sending with topic, value, and optional key
        - Synchronous acknowledgment of message delivery
        - Automatic connection management and error handling
        - Support for message keys for partitioning

    Key Features:
        - Connection lifecycle management (start/stop)
        - Synchronous message production with acknowledgment
        - Automatic broker discovery and connection management
        - Error handling and retry mechanisms
        - Integration with ONEX monitoring and metrics

    Configuration:
        - Bootstrap servers for cluster connection
        - Authentication and security settings
        - Producer-specific configurations
        - Error handling and retry policies
    """

    async def start(self) -> None:
        """
        Start the Kafka client and establish connections.

        Initializes the client, connects to the Kafka cluster,
        and prepares for message production operations.

        Raises:
            ConnectionError: If unable to connect to Kafka cluster
            ConfigurationError: If client configuration is invalid
        """
        ...

    async def stop(self) -> None:
        """
        Stop the Kafka client and clean up resources.

        Gracefully shuts down the client, closes connections,
        and releases any allocated resources.

        Raises:
            ShutdownError: If shutdown process fails
        """
        ...

    async def send_and_wait(
        self, topic: str, value: bytes, key: bytes | None = None
    ) -> None:
        """
        Send a message to Kafka and wait for acknowledgment.

        Args:
            topic: Target topic for the message
            value: Message payload as bytes
            key: Optional message key for partitioning (default: None)

        Raises:
            ProducerError: If message production fails
            TimeoutError: If acknowledgment times out
            SerializationError: If message serialization fails

        Example:
            message = b'{"event": "user_created", "user_id": 123}'
            await kafka_client.send_and_wait(
                topic="user-events",
                value=message,
                key=b"user:123"
            )
        """
        ...

    def bootstrap_servers(self) -> list[str]: ...
@runtime_checkable
class ProtocolKafkaClientProvider(Protocol):
    """Protocol for Kafka client provider."""

    async def create_kafka_client(self) -> ProtocolKafkaClient: ...

    async def get_kafka_configuration(self) -> dict[str, str | int | float | bool]: ...
