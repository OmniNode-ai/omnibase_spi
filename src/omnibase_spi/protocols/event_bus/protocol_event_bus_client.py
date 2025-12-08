"""
Protocol definitions for EventBus client abstraction.

Provides EventBus client protocols that can be implemented by different
message broker backends (Kafka, RedPanda, RabbitMQ, etc.) and injected via ONEXContainer.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class ProtocolEventBusClient(Protocol):
    """
    Protocol interface for EventBus client implementations.

    Provides standardized interface for event bus producer/consumer operations
    that can be implemented by different message broker libraries.

    Example:
        ```python
        # Implementation example (not part of SPI)
        # All methods defined in the protocol contract must be implemented

        # Usage in application
        event_bus_client: "ProtocolEventBusClient" = get_event_bus_client()

        # Start the client
        await event_bus_client.start()

        # Send messages with synchronous confirmation
        message_data = b'{"event": "user_created", "user_id": 123}'
        await event_bus_client.send_and_wait(
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
            await event_bus_client.send_and_wait("events", value, key)

        # Get configuration
        servers = event_bus_client.bootstrap_servers()
        print(f"Connected to event bus cluster: {servers}")

        # Graceful shutdown
        await event_bus_client.stop()
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
        Start the EventBus client and establish connections.

        Initializes the client, connects to the event bus cluster,
        and prepares for message production operations.

        Raises:
            ConnectionError: If unable to connect to event bus cluster
            ConfigurationError: If client configuration is invalid
        """
        ...

    async def stop(self, timeout_seconds: float = 30.0) -> None:
        """
        Stop the EventBus client and clean up resources.

        Gracefully shuts down the client, closes connections,
        and releases any allocated resources.

        Args:
            timeout_seconds: Maximum time to wait for shutdown to complete.
                Defaults to 30.0 seconds.

        Raises:
            ShutdownError: If shutdown process fails.
            TimeoutError: If shutdown does not complete within the specified timeout.
        """
        ...

    async def send_and_wait(
        self, topic: str, value: bytes, key: bytes | None = None
    ) -> None:
        """
        Send a message to the event bus and wait for acknowledgment.

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
            await event_bus_client.send_and_wait(
                topic="user-events",
                value=message,
                key=b"user:123"
            )
        """
        ...

    def bootstrap_servers(self) -> list[str]:
        """
        Get the list of bootstrap servers for the event bus cluster.

        Returns:
            List of server addresses in host:port format.
        """
        ...

    async def validate_connection(self) -> bool:
        """
        Validate the event bus connection is healthy.

        Performs a health check on the underlying connection to ensure
        the client can communicate with the event bus cluster.

        Returns:
            True if connection is valid and healthy, False otherwise.
        """
        ...

    async def validate_message(
        self, topic: str, value: bytes, key: bytes | None = None
    ) -> bool:
        """
        Validate a message before publishing.

        Performs validation checks on the message parameters to ensure
        they meet the requirements for successful publishing.

        Args:
            topic: Target topic for the message.
            value: Message payload as bytes.
            key: Optional message key for partitioning.

        Returns:
            True if message is valid, False otherwise.
        """
        ...


@runtime_checkable
class ProtocolEventBusClientProvider(Protocol):
    """
    Protocol for EventBus client factory and configuration provider.

    Provides centralized creation of EventBus client instances with
    consistent configuration, enabling dependency injection and
    test mocking of event bus connections.

    Example:
        ```python
        provider: ProtocolEventBusClientProvider = get_event_bus_provider()

        # Get EventBus configuration
        config = await provider.get_event_bus_configuration()
        print(f"Bootstrap servers: {config.get('bootstrap_servers')}")

        # Create a new EventBus client
        client = await provider.create_event_bus_client()
        await client.start()

        try:
            await client.send_and_wait("events", b'{"type": "test"}')
        finally:
            await client.stop()
        ```

    See Also:
        - ProtocolEventBusClient: Created client interface
        - ProtocolKafkaAdapter: Full adapter with subscriptions
    """

    async def create_event_bus_client(self) -> ProtocolEventBusClient:
        """
        Create a new EventBus client instance.

        Creates and returns a configured EventBus client ready for use.
        The client should be started via its start() method before
        sending messages.

        Returns:
            A configured ProtocolEventBusClient instance ready to be started.

        Raises:
            ConfigurationError: If client configuration is invalid.
            FactoryError: If client instantiation fails.
        """
        ...

    async def get_event_bus_configuration(self) -> dict[str, str | int | float | bool]:
        """
        Retrieve EventBus client configuration parameters.

        Returns:
            Configuration dictionary with EventBus client settings including
            bootstrap servers, security settings, and operational parameters.

        Raises:
            ConfigurationError: If configuration is invalid or unavailable.
        """
        ...
