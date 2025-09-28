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
        # Basic usage
        kafka_client: "ProtocolKafkaClient" = get_kafka_client()
        await kafka_client.start()

        # Send messages
        message_data = b'{"event": "user_created", "user_id": 123}'
        await kafka_client.send_and_wait("user-events", message_data, key=b"user:123")

        # Get configuration
        servers = kafka_client.bootstrap_servers()
        print(f"Connected to: {servers}")

        # Cleanup
        await kafka_client.stop()
        ```
    """

    async def start(self) -> None: ...

    async def stop(self) -> None: ...

    async def send_and_wait(
        self, topic: str, value: bytes, key: bytes | None = None
    ) -> None: ...

    def bootstrap_servers(self) -> list[str]: ...


@runtime_checkable
class ProtocolKafkaClientProvider(Protocol):
    """Protocol for Kafka client provider."""

    async def create_kafka_client(self) -> ProtocolKafkaClient: ...

    async def get_kafka_configuration(self) -> dict[str, str | int | float | bool]: ...
