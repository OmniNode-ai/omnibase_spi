"""Protocol for Event Bus Service.

This module defines the required interface that all event bus service implementations
must follow. It provides lifecycle management, cluster coordination, and service health
monitoring capabilities for distributed ONEX deployments.

The protocol ensures consistent service behavior including graceful startup/shutdown,
cluster topology management, and runtime status monitoring for production reliability.

Key Protocols:
    - ProtocolEventBusService: Main service protocol for lifecycle and cluster management.
    - ProtocolHttpEventBusAdapter: HTTP-based adapter for lightweight integrations.

Example:
    ```python
    from omnibase_spi.protocols.event_bus import ProtocolEventBusService

    # Get service from dependency injection
    service: ProtocolEventBusService = get_event_bus_service()

    # Access event bus for messaging
    event_bus = await service.get_event_bus()
    await event_bus.publish(topic="events", key=None, value=b"data", headers={})

    # Monitor cluster status
    if service.is_running:
        node_count = await service.get_node_count()
        print(f"Cluster has {node_count} active brokers")

    # Graceful shutdown
    service.shutdown()
    ```

See Also:
    - ProtocolEventBusBase: The base event bus interface from omnibase_spi.
    - ProtocolEventBusProvider: Factory for obtaining event bus instances.
    - ProtocolKafkaAdapter: Kafka-specific adapter protocol.
    - ProtocolRedpandaAdapter: Redpanda-specific adapter protocol.
"""

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_event_bus_types import ProtocolEventMessage

if TYPE_CHECKING:
    from omnibase_spi.protocols.event_bus.protocol_event_bus_mixin import (
        ProtocolEventBusBase,
    )


@runtime_checkable
class ProtocolEventBusService(Protocol):
    """Protocol for event bus service lifecycle and cluster management.

    Defines the standard interface for event bus service implementations providing
    lifecycle management, cluster coordination, and service health monitoring across
    distributed ONEX deployments.

    This protocol ensures consistent service behavior including graceful startup/shutdown,
    cluster topology management, and runtime status monitoring for production reliability.

    Example:
        ```python
        from omnibase_spi.protocols.event_bus import ProtocolEventBusService

        # Initialize event bus service
        service: ProtocolEventBusService = create_event_bus_service(
            broker_config={"bootstrap.servers": "kafka1:9092,kafka2:9092"}
        )

        # Access event bus for messaging
        event_bus = await service.get_event_bus()
        await event_bus.publish(
            topic="events",
            key=b"key",
            value=b"data",
            headers={"correlation_id": "abc-123"}
        )

        # Monitor cluster status
        if service.is_running:
            node_count = await service.get_node_count()
            nodes = await service.list_nodes()
            print(f"Cluster: {node_count} nodes - {nodes}")

        # Graceful shutdown
        service.shutdown()
        ```

    Key Features:
        - Event bus instance management and lifecycle
        - Graceful startup and shutdown coordination
        - Cluster topology discovery and monitoring
        - Service health status tracking
        - Resource cleanup and connection management
        - Runtime configuration access

    Lifecycle Stages:
        1. Initialization: Service created with configuration
        2. Running: Event bus active, accepting operations
        3. Shutdown: Graceful cleanup, connection closure
        4. Terminated: All resources released

    Cluster Management:
        - Node discovery and health monitoring
        - Topology changes detection
        - Load balancing across nodes
        - Failover coordination

    See Also:
        - ProtocolEventBusBase: Base event bus interface (from omnibase_spi)
        - ProtocolKafkaAdapter: Kafka broker adapter
        - ProtocolRedpandaAdapter: Redpanda broker adapter
    """

    async def get_event_bus(self) -> "ProtocolEventBusBase":
        """Get the managed event bus instance.

        Returns the active event bus for publishing and subscribing to events.
        Event bus instance is initialized and ready for use.

        Returns:
            Event bus instance for messaging operations

        Raises:
            ServiceNotRunningError: If service is not running
            InitializationError: If event bus initialization failed

        Example:
            ```python
            service: ProtocolEventBusService = get_service()
            event_bus = await service.get_event_bus()

            # Use event bus for messaging
            await event_bus.publish(topic="events", key=None, value=b"data")
            ```
        """
        ...

    def shutdown(self) -> None:
        """Shutdown the event bus service gracefully.

        Performs graceful shutdown by:
        - Flushing pending messages
        - Closing producer and consumer connections
        - Releasing network resources
        - Cleaning up internal state

        This is a synchronous operation that blocks until shutdown completes.

        Example:
            ```python
            service: ProtocolEventBusService = get_service()

            # Perform graceful shutdown
            service.shutdown()

            # Service is now stopped
            assert not service.is_running
            ```
        """
        ...

    @property
    def is_running(self) -> bool:
        """Check if the event bus service is currently running.

        Returns:
            True if service is running and accepting operations, False otherwise

        Example:
            ```python
            service: ProtocolEventBusService = get_service()

            if service.is_running:
                # Service is operational
                event_bus = await service.get_event_bus()
            else:
                # Service needs to be started
                await service.start()
            ```
        """
        ...

    async def get_node_count(self) -> int:
        """Get the number of broker nodes in the cluster.

        Returns the current count of active broker nodes for monitoring
        cluster topology and availability.

        Returns:
            Number of active broker nodes

        Raises:
            ServiceNotRunningError: If service is not running
            ClusterQueryError: If cluster query fails

        Example:
            ```python
            service: ProtocolEventBusService = get_service()

            node_count = await service.get_node_count()
            print(f"Cluster has {node_count} active brokers")

            # Check minimum cluster size
            if node_count < 3:
                logger.warning("Cluster below minimum size")
            ```
        """
        ...

    async def list_nodes(self) -> list[str]:
        """List all broker nodes in the cluster.

        Returns identifiers for all active broker nodes for cluster
        monitoring and topology visualization.

        Returns:
            List of broker node identifiers (e.g., ["broker-1", "broker-2", "broker-3"])

        Raises:
            ServiceNotRunningError: If service is not running
            ClusterQueryError: If cluster query fails

        Example:
            ```python
            service: ProtocolEventBusService = get_service()

            nodes = await service.list_nodes()
            print(f"Active brokers: {', '.join(nodes)}")

            # Monitor node availability
            for node in nodes:
                health = await check_node_health(node)
                print(f"{node}: {health}")
            ```
        """
        ...


@runtime_checkable
class ProtocolHttpEventBusAdapter(Protocol):
    """Protocol for HTTP-based event bus adapters for lightweight integration.

    Provides lightweight event bus adapter for services that connect to external
    event bus systems over HTTP/REST APIs rather than native protocols. Useful
    for serverless functions, edge computing, and language-agnostic integrations.

    This adapter pattern supports event bus integration without requiring native
    Kafka/Redpanda client libraries, enabling broader deployment scenarios.

    Example:
        ```python
        from omnibase_spi.protocols.event_bus import ProtocolHttpEventBusAdapter

        # Create HTTP event bus adapter
        adapter: ProtocolHttpEventBusAdapter = create_http_adapter(
            endpoint="https://eventbus.example.com/api/v1",
            api_key="your-api-key"
        )

        # Publish events via HTTP
        event = create_event_message(
            topic="events",
            key=b"key-123",
            value=b'{"type": "user.created", "id": "user-456"}'
        )
        success = await adapter.publish(event)

        # Subscribe to events via HTTP polling or webhooks
        async def event_handler(message: "ProtocolEventMessage") -> bool:
            print(f"Received: {message.value}")
            return True  # Acknowledge processing

        await adapter.subscribe(event_handler)

        # Check adapter health
        if adapter.is_healthy:
            print("HTTP adapter is healthy")

        # Cleanup
        await adapter.unsubscribe(event_handler)
        await adapter.close()
        ```

    Key Features:
        - HTTP/REST API based event bus integration
        - Language-agnostic protocol (any HTTP client)
        - Serverless and edge computing support
        - Simplified client dependencies
        - Health monitoring and connection management
        - Subscription lifecycle management

    Use Cases:
        - Serverless functions (AWS Lambda, Azure Functions)
        - Edge computing nodes
        - Polyglot microservices
        - Browser-based applications
        - Environments with restricted network protocols
        - Development and testing scenarios

    Transport Mechanisms:
        - Publish: HTTP POST with event payload
        - Subscribe: HTTP long polling or webhooks
        - Health: HTTP GET for status checks
        - Unsubscribe: HTTP DELETE for subscription removal

    See Also:
        - ProtocolEventBusService: Full event bus service protocol
        - ProtocolKafkaAdapter: Native Kafka protocol adapter
        - ProtocolRedpandaAdapter: Native Redpanda adapter
    """

    async def publish(self, event: "ProtocolEventMessage") -> bool:
        """Publish event via HTTP to the event bus.

        Sends event to the event bus service using HTTP POST request with
        event payload and returns success status.

        Args:
            event: Event message to publish

        Returns:
            True if publish succeeded, False if failed

        Raises:
            PublishError: If HTTP request fails
            AuthenticationError: If API credentials are invalid
            TimeoutError: If request times out

        Example:
            ```python
            event = create_event_message(
                topic="user-events",
                key=b"user-123",
                value=b'{"action": "created"}'
            )

            success = await adapter.publish(event)
            if success:
                print("Event published successfully")
            ```
        """
        ...

    async def subscribe(
        self, handler: Callable[["ProtocolEventMessage"], Awaitable[bool]]
    ) -> bool:
        """Subscribe to events with HTTP-based handler.

        Establishes subscription to receive events via HTTP polling or webhooks,
        invoking handler for each received event.

        Args:
            handler: Async function to handle received events

        Returns:
            True if subscription succeeded, False if failed

        Raises:
            SubscriptionError: If subscription setup fails
            AuthenticationError: If API credentials are invalid

        Example:
            ```python
            async def handler(message: "ProtocolEventMessage") -> bool:
                process_event(message.value)
                return True  # Acknowledge

            success = await adapter.subscribe(handler)
            if success:
                print("Subscription active")
            ```
        """
        ...

    async def unsubscribe(
        self, handler: Callable[["ProtocolEventMessage"], Awaitable[bool]]
    ) -> bool:
        """Unsubscribe from events and stop receiving messages.

        Removes subscription for the specified handler, stopping event delivery.

        Args:
            handler: Handler function to unsubscribe

        Returns:
            True if unsubscribe succeeded, False if failed

        Raises:
            UnsubscribeError: If unsubscribe operation fails

        Example:
            ```python
            success = await adapter.unsubscribe(handler)
            if success:
                print("Unsubscribed successfully")
            ```
        """
        ...

    @property
    def is_healthy(self) -> bool:
        """Check if HTTP event bus adapter is healthy.

        Returns:
            True if adapter connection is healthy, False otherwise

        Example:
            ```python
            if adapter.is_healthy:
                # Adapter is operational
                await adapter.publish(event)
            else:
                # Adapter needs reconnection
                await adapter.reconnect()
            ```
        """
        ...

    async def close(self, timeout_seconds: float = 30.0) -> None:
        """Close HTTP event bus adapter and release resources.

        Cleanly shuts down HTTP connections and releases resources.

        Args:
            timeout_seconds: Maximum time to wait for cleanup to complete.
                Defaults to 30.0 seconds.

        Raises:
            TimeoutError: If cleanup does not complete within the specified timeout.

        Example:
            ```python
            # Close with default timeout
            await adapter.close()

            # Close with custom timeout
            await adapter.close(timeout_seconds=60.0)
            ```
        """
        ...
