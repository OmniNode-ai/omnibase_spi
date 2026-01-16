"""Redpanda Event Bus Adapter Protocol - ONEX SPI Interface.

This module provides protocol definitions for Redpanda backend implementations in the
ONEX event bus system. Redpanda is a Kafka API compatible streaming platform built
in C++ with significantly lower latency and higher throughput than Apache Kafka.

The Redpanda adapter extends the Kafka adapter interface with Redpanda-specific
performance optimizations including reduced memory footprint, improved batch
processing, and optimized defaults for cloud-native deployments.

Key Features:
    - Full Kafka protocol compatibility
    - Redpanda-specific performance optimizations
    - Lower memory footprint than Kafka
    - Reduced end-to-end latency (<10ms p99)
    - Native cloud-native architecture
    - Built-in tiered storage support

Performance Characteristics:
    - Latency: <10ms p99 (vs 100ms+ in Kafka)
    - Throughput: 10GB/s+ per broker
    - Memory: 60% less than Kafka for same workload

Example:
    ```python
    from omnibase_spi.protocols.event_bus import ProtocolRedpandaAdapter

    # Get Redpanda adapter
    adapter: ProtocolRedpandaAdapter = get_redpanda_adapter()

    # Access Redpanda-specific optimizations (type-safe)
    config = adapter.redpanda_config
    print(f"Batch size: {config.batch_size_bytes} bytes")

    # Publish event (Kafka-compatible interface)
    await adapter.publish(
        topic="events",
        key=b"user:123",
        value=b'{"event": "created"}',
        headers={"correlation_id": "abc123"}
    )

    # Cleanup
    await adapter.close()
    ```

See Also:
    - ProtocolKafkaAdapter: Standard Kafka adapter protocol.
    - ProtocolEventBusService: Service layer for event bus operations.
    - ProtocolEventBusProvider: Factory for obtaining event bus instances.
"""

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from omnibase_core.types import JsonType
from omnibase_spi.protocols.event_bus.protocol_kafka_adapter import ProtocolKafkaConfig

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_event_bus_types import (
        ProtocolEventMessage,
    )

# Type aliases for event bus headers with proper type safety (PEP 695)
type EventBusHeaders = JsonType


@runtime_checkable
class ProtocolRedpandaConfig(Protocol):
    """Protocol for Redpanda-specific configuration with performance optimizations.

    Extends the Kafka configuration pattern with Redpanda-specific optimization
    parameters. Provides type-safe access to Redpanda tuning parameters that
    differ from standard Kafka defaults.

    Attributes:
        batch_size_bytes: Optimal batch size in bytes (1MB default for Redpanda)
        compression_type: Compression algorithm (lz4, snappy, zstd, none)
        linger_ms: Batch linger time in milliseconds for throughput optimization
        buffer_memory_bytes: Producer buffer memory in bytes
        fetch_min_bytes: Consumer minimum fetch size
        max_poll_records: Maximum records per poll operation
        acks: Acknowledgment level (0, 1, or 'all')
        enable_idempotence: Whether to enable idempotent producer
        max_in_flight_requests: Maximum in-flight requests per connection

    Example:
        ```python
        adapter: ProtocolRedpandaAdapter = get_redpanda_adapter()
        config = adapter.redpanda_config

        print(f"Batch size: {config.batch_size_bytes} bytes")
        print(f"Compression: {config.compression_type}")
        print(f"Linger: {config.linger_ms}ms")
        ```

    See Also:
        - ProtocolKafkaConfig: Base Kafka configuration protocol
        - ProtocolRedpandaAdapter: Redpanda adapter using this config
    """

    @property
    def batch_size_bytes(self) -> int:
        """Optimal batch size in bytes (1MB default for Redpanda).

        Returns:
            Batch size in bytes for producer batching optimization.
        """
        ...

    @property
    def compression_type(self) -> str:
        """Compression algorithm (lz4, snappy, zstd, none).

        Returns:
            Compression type string: "lz4", "snappy", "zstd", or "none".
        """
        ...

    @property
    def linger_ms(self) -> int:
        """Batch linger time in milliseconds for throughput optimization.

        Returns:
            Linger time in milliseconds before sending batched messages.
        """
        ...

    @property
    def buffer_memory_bytes(self) -> int:
        """Producer buffer memory in bytes.

        Returns:
            Total memory available to the producer for buffering.
        """
        ...

    @property
    def fetch_min_bytes(self) -> int:
        """Consumer minimum fetch size in bytes.

        Returns:
            Minimum bytes broker should accumulate before returning fetch response.
        """
        ...

    @property
    def max_poll_records(self) -> int:
        """Maximum records per poll operation.

        Returns:
            Maximum number of records returned in a single poll call.
        """
        ...

    @property
    def acks(self) -> str:
        """Acknowledgment level (0, 1, or 'all').

        Returns:
            Acknowledgment setting: "0" (none), "1" (leader), or "all" (replicas).
        """
        ...

    @property
    def enable_idempotence(self) -> bool:
        """Whether to enable idempotent producer for exactly-once semantics.

        Returns:
            True if idempotent producer is enabled, False otherwise.
        """
        ...

    @property
    def max_in_flight_requests(self) -> int:
        """Maximum in-flight requests per connection.

        Returns:
            int: Maximum number of unacknowledged requests the client will send
                per broker connection before blocking.

        Note:
            Lower values reduce memory usage but may impact throughput.
            Redpanda default is typically 5 for idempotent producers.
        """
        ...


@runtime_checkable
class ProtocolRedpandaAdapter(Protocol):
    """Protocol for Redpanda event bus adapter with performance optimizations.

    Provides Redpanda-specific event bus adapter implementation maintaining full
    Kafka protocol compatibility while leveraging Redpanda's performance optimizations
    and enhanced defaults. Redpanda is a Kafka-compatible streaming platform built
    in C++ with significantly lower latency and higher throughput.

    This protocol extends the Kafka adapter interface with Redpanda-specific optimizations
    including reduced memory footprint, improved batch processing, and optimized defaults
    for cloud-native deployments.

    Attributes:
        redpanda_config: Type-safe Redpanda-specific configuration with optimization
            parameters including batch size, compression, and performance settings.
        redpanda_optimized_defaults: Deprecated alias for redpanda_config. Use
            redpanda_config for type-safe access to Redpanda optimizations.
        bootstrap_servers: Comma-separated list of Redpanda broker addresses.
        environment: Environment name (dev, staging, prod) for topic isolation.
        group: Consumer group identifier for coordination.
        config: Optional Kafka configuration overrides, or None for defaults.
        kafka_config: Complete Kafka configuration with Redpanda optimizations.

    Args:
        None: Protocol classes do not take constructor arguments. Implementations
            receive configuration through their own constructors.

    Returns:
        None: Protocol classes are type specifications, not instantiated directly.

    Raises:
        PublishError: When event publication fails (from publish method).
        SubscriptionError: When topic subscription fails (from subscribe method).
        ConnectionError: When broker connection cannot be established.
        TimeoutError: When operations exceed configured timeout (from close method).

    Example:
        ```python
        from omnibase_spi.protocols.event_bus import ProtocolRedpandaAdapter
        from uuid import uuid4

        # Create Redpanda adapter with optimized defaults
        adapter: ProtocolRedpandaAdapter = create_redpanda_adapter(
            bootstrap_servers="redpanda1:9092,redpanda2:9092,redpanda3:9092",
            environment="prod",
            group="workflow-group"
        )

        # Access Redpanda-specific optimizations
        optimizations = adapter.redpanda_optimized_defaults
        print(f"Batch size: {optimizations.get('batch_size')}")
        print(f"Compression: {optimizations.get('compression_type')}")

        # Publish events (Kafka-compatible interface)
        await adapter.publish(
            topic="workflow-events",
            key=b"workflow-123",
            value=b'{"type": "workflow.started", "id": "wf-123"}',
            headers={
                "correlation_id": str(uuid4()),
                "content_type": "application/json"
            }
        )

        # Subscribe to events with handler
        async def handle_event(message: "ProtocolEventMessage") -> None:
            print(f"Received: {message.value}")
            await message.ack()

        unsubscribe = await adapter.subscribe(
            topic="workflow-events",
            group_id="workflow-processors",
            on_message=handle_event
        )

        # Later cleanup
        await unsubscribe()
        await adapter.close()
        ```

    Key Features:
        - Full Kafka protocol compatibility
        - Redpanda-specific performance optimizations
        - Lower memory footprint than Kafka
        - Reduced end-to-end latency (<10ms p99)
        - Native cloud-native architecture
        - Built-in tiered storage support
        - Enhanced batch processing defaults
        - Optimized compression settings

    Redpanda Optimizations:
        - Default batch size: 1MB (vs 16KB in Kafka)
        - Compression: lz4 by default (fast compression)
        - Reduced replication lag through C++ zero-copy
        - Native vectorized processing
        - Reduced memory allocation overhead
        - Faster broker recovery times

    Performance Characteristics:
        - Latency: <10ms p99 (vs 100ms+ in Kafka)
        - Throughput: 10GB/s+ per broker
        - Memory: 60% less than Kafka for same workload
        - CPU: Lower utilization through vectorization

    Environment Isolation:
        Topics are automatically namespaced by environment:
        - dev-workflow-events
        - staging-workflow-events
        - prod-workflow-events

    See Also:
        - ProtocolKafkaAdapter: Standard Kafka adapter
        - ProtocolEventBusProvider: ONEX event bus interface
        - ProtocolEventMessage: Event message protocol
    """

    @property
    def redpanda_config(self) -> ProtocolRedpandaConfig:
        """Get Redpanda-specific configuration with type-safe access.

        Returns Redpanda-specific configuration with strongly-typed properties
        for optimization settings, compression, and performance tuning.

        Returns:
            ProtocolRedpandaConfig: Type-safe Redpanda configuration object

        Example:
            ```python
            config = adapter.redpanda_config

            # Type-safe access to optimization settings
            print(f"Batch size: {config.batch_size_bytes} bytes")
            print(f"Compression: {config.compression_type}")
            print(f"Linger: {config.linger_ms}ms")
            print(f"Idempotent: {config.enable_idempotence}")
            ```
        """
        ...

    @property
    def redpanda_optimized_defaults(self) -> ProtocolRedpandaConfig:
        """Get Redpanda-specific optimization defaults.

        Returns Redpanda-specific configuration optimizations including enhanced
        batch sizes, compression settings, and performance tuning parameters.

        .. deprecated:: 0.4.0
            Use :attr:`redpanda_config` instead for type-safe access.

        Returns:
            ProtocolRedpandaConfig: Redpanda optimization settings with typed properties

        Example:
            ```python
            # Preferred: use redpanda_config
            config = adapter.redpanda_config
            print(f"Batch size: {config.batch_size_bytes} bytes")

            # Deprecated: redpanda_optimized_defaults (same return type)
            defaults = adapter.redpanda_optimized_defaults
            print(f"Compression: {defaults.compression_type}")
            ```
        """
        ...

    # Kafka adapter interface methods and properties
    @property
    def bootstrap_servers(self) -> str:
        """Redpanda bootstrap servers connection string.

        Returns:
            Comma-separated list of broker addresses (e.g., "redpanda1:9092,redpanda2:9092")
        """
        ...

    @property
    def environment(self) -> str:
        """Environment name for topic isolation.

        Returns:
            Environment identifier (e.g., "dev", "staging", "prod")
        """
        ...

    @property
    def group(self) -> str:
        """Consumer group identifier.

        Returns:
            Group ID for consumer group coordination
        """
        ...

    @property
    def config(self) -> ProtocolKafkaConfig | None:
        """Optional Kafka configuration overrides.

        Returns:
            Kafka configuration object or None for defaults
        """
        ...

    @property
    def kafka_config(self) -> ProtocolKafkaConfig:
        """Complete Kafka configuration with Redpanda optimizations.

        Returns:
            Full Kafka configuration including Redpanda-specific settings
        """
        ...

    async def build_topic_name(self, topic: str) -> str:
        """Build environment-namespaced topic name.

        Constructs topic name with environment prefix for isolation.

        Args:
            topic: Base topic name (e.g., "workflow-events")

        Returns:
            Environment-prefixed topic (e.g., "prod-workflow-events")

        Example:
            ```python
            topic_name = await adapter.build_topic_name("user-events")
            # Returns: "prod-user-events" if environment is "prod"
            ```
        """
        ...

    # Core event bus adapter interface methods
    async def publish(
        self,
        topic: str,
        key: bytes | None,
        value: bytes,
        headers: "EventBusHeaders",
    ) -> None:
        """Publish event to Redpanda topic.

        Publishes event message to specified topic with optional key for partitioning
        and headers for metadata.

        Args:
            topic: Topic name (will be environment-namespaced)
            key: Optional partition key for ordering
            value: Event payload as bytes
            headers: Event headers dictionary

        Raises:
            PublishError: If publish fails
            ConnectionError: If broker connection fails

        Example:
            ```python
            await adapter.publish(
                topic="events",
                key=b"user-123",
                value=b'{"action": "created"}',
                headers={"correlation_id": "abc-123"}
            )
            ```
        """
        ...

    async def subscribe(
        self,
        topic: str,
        group_id: str,
        on_message: Callable[["ProtocolEventMessage"], Awaitable[None]],
    ) -> Callable[[], Awaitable[None]]:
        """Subscribe to Redpanda topic with message handler.

        Creates subscription to topic with consumer group coordination and
        returns unsubscribe function.

        Args:
            topic: Topic name to subscribe to
            group_id: Consumer group for load balancing
            on_message: Async handler for received messages

        Returns:
            Unsubscribe function to cancel subscription

        Raises:
            SubscriptionError: If subscription fails
            ConnectionError: If broker connection fails

        Example:
            ```python
            async def handler(msg: "ProtocolEventMessage") -> None:
                process_message(msg.value)
                await msg.ack()

            unsubscribe = await adapter.subscribe(
                topic="events",
                group_id="processors",
                on_message=handler
            )

            # Later: await unsubscribe()
            ```
        """
        ...

    async def close(self, timeout_seconds: float = 30.0) -> None:
        """Close Redpanda adapter and release resources.

        Cleanly shuts down producer and consumer connections, flushes
        pending messages, and releases network resources.

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
