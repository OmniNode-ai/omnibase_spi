# Event Bus API Reference

![Version](https://img.shields.io/badge/SPI-v0.3.0-blue) ![Status](https://img.shields.io/badge/status-stable-green) ![Since](https://img.shields.io/badge/since-v0.2.0-lightgrey)

> **SPI Version**: 0.3.0 | **Status**: Stable | **Since**: v0.2.0

---

## Overview

The ONEX event bus protocols provide comprehensive distributed messaging infrastructure with pluggable backend adapters, async/sync implementations, event serialization, and dead letter queue handling. These protocols enable sophisticated event-driven architectures across the ONEX ecosystem.

## Architecture Principles

The event bus domain follows a **layered architecture**:

1. **Core Interface Layer** (`omnibase_core`) - Base `ProtocolEventBus` and `ProtocolEventBusHeaders` interfaces
2. **SPI Provider Layer** (`omnibase_spi`) - Factory protocols, context managers, and ONEX-specific extensions
3. **Implementation Layer** (`omnibase_infra`) - Concrete implementations (Kafka, Redpanda, in-memory)

This separation ensures:
- **Clean dependency boundaries** - SPI depends only on Core, never on Infra
- **Pluggable backends** - Implementations can be swapped without changing application code
- **Testability** - In-memory implementations for testing, production backends for deployment

## Publisher Protocol Policy

### Canonical Interface

`ProtocolEventPublisher` is the **canonical publish interface** for all event publishing in the ONEX platform.

**Rule**: Handlers MUST depend on `ProtocolEventPublisher` from `omnibase_spi.protocols.event_bus`. Handler-local publish protocols (e.g., `ProtocolKafkaPublisher`) are **forbidden**.

```python
# CORRECT: Use the canonical SPI protocol
from omnibase_spi.protocols.event_bus import ProtocolEventPublisher

class MyHandler:
    def __init__(self, publisher: ProtocolEventPublisher) -> None:
        self._publisher = publisher

# FORBIDDEN: Do NOT define handler-local publish protocols
# class ProtocolKafkaPublisher(Protocol):  # NO! Use ProtocolEventPublisher
#     async def publish_to_kafka(self, ...) -> None: ...
```

### Architecture Layers

| Layer | Responsibility | Interface |
|-------|---------------|-----------|
| **Handler** | Business logic, event creation | Uses `ProtocolEventPublisher` |
| **SPI** | Semantic publishing contract | Defines `ProtocolEventPublisher` |
| **Infra** | Transport (bytes, connections) | Implements `ProtocolEventPublisher` |

```text
┌─────────────────────────────────────────────────────────────┐
│  Application Handlers (omniagent, omniintelligence)         │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  - Create events with business semantics              │  │
│  │  - Depend on ProtocolEventPublisher from SPI          │  │
│  │  - NO local publish protocol definitions              │  │
│  └───────────────────────────────────────────────────────┘  │
│                           │                                  │
│                           ▼ uses                             │
├─────────────────────────────────────────────────────────────┤
│  SPI (omnibase_spi)                                         │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  ProtocolEventPublisher                               │  │
│  │  - publish(event_type, payload, correlation_id, ...) │  │
│  │  - get_metrics()                                      │  │
│  │  - close()                                            │  │
│  └───────────────────────────────────────────────────────┘  │
│                           │                                  │
│                           ▼ implements                       │
├─────────────────────────────────────────────────────────────┤
│  Infra (omnibase_infra)                                     │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  KafkaEventPublisher, RedpandaEventPublisher, etc.    │  │
│  │  - Handle bytes, connections, retry, circuit breaker  │  │
│  │  - Backend-specific transport logic                   │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Why This Matters

Defining handler-local publish protocols creates the **3-interface problem**:

1. **Interface drift**: Each handler defines slightly different publish semantics
2. **Adapter proliferation**: Each local protocol needs its own test adapter
3. **Maintenance burden**: Changes to publishing logic must be replicated across handlers

By enforcing `ProtocolEventPublisher` as the single canonical interface:

- **One interface, one set of adapters**: Official implementations in `omnibase_infra`
- **Consistent semantics**: All handlers use identical publish behavior
- **Simplified testing**: One mock/fake publisher works everywhere
- **Clear dependency direction**: Handlers -> SPI -> Infra (never reversed)

### Correct Usage Pattern

```python
from omnibase_spi.protocols.event_bus import ProtocolEventPublisher

class AgentEventHandler:
    """Handler that publishes events using the canonical interface."""

    def __init__(self, publisher: ProtocolEventPublisher) -> None:
        self._publisher = publisher

    async def handle_agent_completed(
        self,
        agent_id: str,
        result: dict,
        correlation_id: str,
    ) -> None:
        """Publish agent completion event."""
        await self._publisher.publish(
            event_type="agent.completed.v1",
            payload={"agent_id": agent_id, "result": result},
            correlation_id=correlation_id,
            topic="agent-events",
        )
```

### Exceptions

If a handler truly needs raw Kafka bytes access (e.g., custom serialization, direct partition control, or low-level protocol manipulation), that handler IS infrastructure and belongs in `omnibase_infra`, not in application code.

**Examples of infra-level concerns** (belong in `omnibase_infra`):
- Custom binary serialization formats
- Direct partition assignment algorithms
- Protocol-specific header manipulation
- Raw bytes streaming

**Examples of application-level concerns** (use `ProtocolEventPublisher`):
- Publishing domain events (user created, order placed)
- Emitting telemetry and metrics
- Sending notifications and alerts
- Triggering downstream workflows

## Protocol Architecture

The event bus domain consists of **24 specialized protocols** organized into these categories:

| Category | Protocols | Purpose |
|----------|-----------|---------|
| Provider & Factory | `ProtocolEventBusProvider` | Event bus instance creation and lifecycle |
| Context Management | `ProtocolEventBusContextManager` | Async context manager for resource lifecycle |
| Base Interfaces | `ProtocolEventBusBase`, `ProtocolSyncEventBus`, `ProtocolAsyncEventBus` | Core publish/subscribe patterns |
| Service & Registry | `ProtocolEventBusService`, `ProtocolEventBusRegistry` | Service operations and dependency injection |
| Event Envelope | `ProtocolEventEnvelope` | Generic envelope for breaking circular dependencies |
| Client Protocols | `ProtocolEventBusClient`, `ProtocolEventBusClientProvider` | Event bus client abstraction for DI |
| Extended Client | `ProtocolEventBusExtendedClient`, `ProtocolEventBusConsumer` | Comprehensive client with consumer operations |
| Producer Protocols | `ProtocolEventBusProducerHandler`, `ProtocolEventBusBatchProducer`, `ProtocolEventBusTransactionalProducer` | Message production operations |
| Backend Adapters | `ProtocolKafkaAdapter`, `ProtocolRedpandaAdapter`, `ProtocolHttpEventBusAdapter` | Backend-specific implementations |
| Publishing | `ProtocolEventPublisher` | Reliable event publishing with retry/circuit breaker |
| Error Handling | `ProtocolDLQHandler` | Dead letter queue management |
| Schema Management | `ProtocolSchemaRegistry` | Schema versioning and compatibility |
| Message Types | `ProtocolEventBusMessage`, `ProtocolEventMessage` | Message data structures |
| Logging | `ProtocolEventBusLogEmitter` | Structured log emission |

### Event Bus Provider Protocol

```python
from omnibase_spi.protocols.event_bus import ProtocolEventBusProvider
from omnibase_spi.protocols.types.protocol_event_bus_types import (
    ProtocolEventMessage,
    LiteralEventPriority,
)

@runtime_checkable
class ProtocolEventBusProvider(Protocol):
    """
    ONEX event bus provider protocol for distributed messaging infrastructure.

    This is the SPI extension of the Core ProtocolEventBus protocol, providing
    additional ONEX-specific capabilities for distributed messaging infrastructure.

    Provides comprehensive event publishing, subscription management,
    and message routing across distributed systems.

    Key Features:
        - Event publishing and subscription
        - Message serialization and deserialization
        - Topic management and routing
        - Dead letter queue handling
        - Performance monitoring and metrics
        - Pluggable backend adapters
    """

    async def publish_event(
        self,
        topic: str,
        message: ProtocolEventMessage,
        partition_key: str | None = None,
    ) -> None: ...

    async def subscribe_to_topic(
        self,
        topic: str,
        handler: ProtocolEventHandler,
        group_id: str | None = None,
    ) -> str: ...

    async def unsubscribe_from_topic(self, subscription_id: str) -> None: ...

    async def create_topic(
        self, topic: str, partition_count: int = 1
    ) -> bool: ...

    async def delete_topic(self, topic: str) -> bool: ...

    async def get_topic_info(self, topic: str) -> ProtocolTopicInfo | None: ...

    async def get_subscription_info(
        self, subscription_id: str
    ) -> ProtocolSubscriptionInfo | None: ...

    async def pause_subscription(self, subscription_id: str) -> bool: ...

    async def resume_subscription(self, subscription_id: str) -> bool: ...

    async def get_bus_metrics(self) -> ProtocolEventBusMetrics: ...

    async def get_topic_metrics(self, topic: str) -> ProtocolTopicMetrics: ...
```


### Event Message Protocol

```python
@runtime_checkable
class ProtocolEventMessage(Protocol):
    """
    Protocol for event message structure.

    Defines the standard structure for event messages with
    metadata, headers, and payload information.
    """

    topic: str
    key: bytes | None
    value: bytes
    headers: dict[str, ContextValue]
    offset: str | None
    partition: int | None
    timestamp: ProtocolDateTime
    correlation_id: UUID | None
    causation_id: UUID | None
    message_id: UUID

    async def serialize(self) -> bytes: ...

    async def deserialize(self, data: bytes) -> None: ...

    async def ack(self) -> None: ...

    async def nack(self, requeue: bool = True) -> None: ...
```

### Event Handler Protocol

```python
@runtime_checkable
class ProtocolEventHandler(Protocol):
    """
    Protocol for event handler functions.

    Event handlers process incoming events and perform
    business logic based on event content.
    """

    async def __call__(
        self, message: ProtocolEventMessage, context: dict[str, ContextValue]
    ) -> None: ...
```

### Event Bus Service Protocol

```python
@runtime_checkable
class ProtocolEventBusService(Protocol):
    """
    Protocol for event bus service operations.

    Provides service-level operations for event bus management,
    configuration, and monitoring.
    """

    async def start_service(self) -> bool: ...

    async def stop_service(self) -> bool: ...

    async def is_service_running(self) -> bool: ...

    async def get_service_configuration(
        self,
    ) -> ProtocolEventBusConfiguration: ...

    async def update_service_configuration(
        self, configuration: ProtocolEventBusConfiguration
    ) -> bool: ...

    async def get_service_health(self) -> ProtocolEventBusHealth: ...

    async def get_service_metrics(self) -> ProtocolEventBusServiceMetrics: ...
```

### Kafka Adapter Protocol

```python
@runtime_checkable
class ProtocolKafkaAdapter(Protocol):
    """
    Protocol for Kafka event bus adapter.

    Provides Kafka-specific implementation for event bus
    operations with Kafka cluster integration.

    Key Features:
        - Kafka cluster connectivity
        - Partition management
        - Consumer group coordination
        - Offset management
        - Schema registry integration
    """

    async def connect_to_cluster(
        self, bootstrap_servers: list[str]
    ) -> bool: ...

    async def disconnect_from_cluster(self) -> bool: ...

    async def create_kafka_topic(
        self, topic: str, partitions: int, replication_factor: int
    ) -> bool: ...

    async def delete_kafka_topic(self, topic: str) -> bool: ...

    async def get_kafka_metadata(self) -> ProtocolKafkaMetadata: ...

    async def get_consumer_group_info(
        self, group_id: str
    ) -> ProtocolConsumerGroupInfo: ...

    async def reset_consumer_group_offset(
        self, group_id: str, topic: str, offset: int
    ) -> bool: ...
```

### Redpanda Adapter Protocol

```python
@runtime_checkable
class ProtocolRedpandaAdapter(Protocol):
    """
    Protocol for Redpanda event bus adapter.

    Provides Redpanda-specific implementation for event bus
    operations with Redpanda cluster integration.

    Key Features:
        - Redpanda cluster connectivity
        - High-performance messaging
        - Schema evolution support
        - Cloud-native integration
        - Performance optimization
    """

    async def connect_to_redpanda(
        self, brokers: list[str]
    ) -> bool: ...

    async def disconnect_from_redpanda(self) -> bool: ...

    async def create_redpanda_topic(
        self, topic: str, partitions: int
    ) -> bool: ...

    async def delete_redpanda_topic(self, topic: str) -> bool: ...

    async def get_redpanda_metrics(self) -> ProtocolRedpandaMetrics: ...

    async def optimize_redpanda_performance(
        self, topic: str, settings: dict[str, Any]
    ) -> bool: ...
```

### Event Bus Client Protocol

The `ProtocolEventBusClient` provides a standardized interface for event bus producer/consumer operations:

```python
from omnibase_spi.protocols.event_bus import ProtocolEventBusClient

@runtime_checkable
class ProtocolEventBusClient(Protocol):
    """
    Protocol interface for EventBus client implementations.

    Provides standardized interface for event bus producer/consumer operations
    that can be implemented by different message broker libraries.
    """

    async def start(self) -> None:
        """Start the EventBus client and establish connections."""
        ...

    async def stop(self, timeout_seconds: float = 30.0) -> None:
        """Stop the EventBus client and clean up resources."""
        ...

    async def send_and_wait(
        self, topic: str, value: bytes, key: bytes | None = None
    ) -> None:
        """Send a message to the event bus and wait for acknowledgment."""
        ...

    def bootstrap_servers(self) -> list[str]:
        """Get the list of bootstrap servers for the event bus cluster."""
        ...
```

### Event Bus Client Provider Protocol

The `ProtocolEventBusClientProvider` provides centralized creation of EventBus client instances:

```python
from omnibase_spi.protocols.event_bus import ProtocolEventBusClientProvider

@runtime_checkable
class ProtocolEventBusClientProvider(Protocol):
    """
    Protocol for EventBus client factory and configuration provider.

    Provides centralized creation of EventBus client instances with
    consistent configuration, enabling dependency injection and
    test mocking of event bus connections.
    """

    async def create_event_bus_client(self) -> ProtocolEventBusClient:
        """Create a new EventBus client instance."""
        ...

    async def get_event_bus_configuration(self) -> dict[str, str | int | float | bool]:
        """Retrieve EventBus client configuration parameters."""
        ...
```

### Event Bus Consumer Protocol

The `ProtocolEventBusConsumer` provides comprehensive consumer operations:

```python
from omnibase_spi.protocols.event_bus import ProtocolEventBusConsumer

@runtime_checkable
class ProtocolEventBusConsumer(Protocol):
    """
    Protocol for EventBus consumer operations.

    Supports topic subscription, message consumption, offset management,
    and consumer group coordination for distributed event processing.
    """

    async def subscribe_to_topics(self, topics: list[str], group_id: str) -> None:
        """Subscribe to one or more topics for message consumption."""
        ...

    async def unsubscribe_from_topics(self, topics: list[str]) -> None:
        """Unsubscribe from one or more topics."""
        ...

    async def consume_messages(
        self, timeout_ms: int, max_messages: int
    ) -> list[ProtocolEventBusMessage]:
        """Consume messages from subscribed topics."""
        ...

    async def consume_messages_stream(
        self, batch_timeout_ms: int
    ) -> list[ProtocolEventBusMessage]:
        """Consume a batch of messages with streaming semantics."""
        ...

    async def commit_offsets(self) -> None:
        """Commit current consumer offsets to the event bus."""
        ...

    async def seek_to_beginning(self, topic: str, partition: int) -> None:
        """Seek to the beginning of a topic partition."""
        ...

    async def seek_to_end(self, topic: str, partition: int) -> None:
        """Seek to the end of a topic partition."""
        ...

    async def seek_to_offset(self, topic: str, partition: int, offset: int) -> None:
        """Seek to a specific offset in a topic partition."""
        ...

    async def get_current_offsets(self) -> dict[str, dict[int, int]]:
        """Get current consumer offsets for all subscribed topic partitions."""
        ...

    async def close_consumer(self, timeout_seconds: float = 30.0) -> None:
        """Close the EventBus consumer and release resources."""
        ...
```

### Event Bus Batch Producer Protocol

The `ProtocolEventBusBatchProducer` provides high-throughput batch message production:

```python
from omnibase_spi.protocols.event_bus import ProtocolEventBusBatchProducer

@runtime_checkable
class ProtocolEventBusBatchProducer(Protocol):
    """
    Protocol for batch EventBus producer operations.

    Supports batching multiple messages, custom partitioning strategies,
    transaction management, and high-throughput message production.
    """

    async def send_batch(self, messages: list[ProtocolEventBusMessage]) -> None:
        """Send a batch of messages to the event bus."""
        ...

    async def send_to_partition(
        self,
        topic: str,
        partition: int,
        key: bytes | None,
        value: bytes,
        headers: dict[str, bytes] | None = None,
    ) -> None:
        """Send a message to a specific partition."""
        ...

    async def send_with_custom_partitioner(
        self,
        topic: str,
        key: bytes | None,
        value: bytes,
        partition_strategy: str,
        headers: dict[str, bytes] | None = None,
    ) -> None:
        """Send a message using a custom partitioning strategy."""
        ...

    async def flush_pending(self, timeout_ms: int) -> None:
        """Flush all pending messages to the event bus."""
        ...

    async def get_batch_metrics(self) -> dict[str, int]:
        """Get metrics for batch producer operations."""
        ...
```

### Event Bus Transactional Producer Protocol

The `ProtocolEventBusTransactionalProducer` provides exactly-once semantics with transaction management:

```python
from omnibase_spi.protocols.event_bus import ProtocolEventBusTransactionalProducer

@runtime_checkable
class ProtocolEventBusTransactionalProducer(Protocol):
    """
    Protocol for transactional EventBus producer operations.

    Supports exactly-once semantics with transaction management,
    atomic message production, and consumer-producer coordination.
    """

    async def init_transactions(self, transaction_id: str) -> None:
        """Initialize the transactional producer with a transaction ID."""
        ...

    async def begin_transaction(self) -> None:
        """Begin a new transaction."""
        ...

    async def send_transactional(
        self,
        topic: str,
        value: bytes,
        key: bytes | None = None,
        headers: dict[str, bytes] | None = None,
    ) -> None:
        """Send a message as part of the current transaction."""
        ...

    async def commit_transaction(self) -> None:
        """Commit the current transaction."""
        ...

    async def abort_transaction(self) -> None:
        """Abort the current transaction."""
        ...
```

### Event Bus Extended Client Protocol

The `ProtocolEventBusExtendedClient` provides comprehensive client operations:

```python
from omnibase_spi.protocols.event_bus import ProtocolEventBusExtendedClient

@runtime_checkable
class ProtocolEventBusExtendedClient(Protocol):
    """
    Protocol for comprehensive EventBus client with all operations.

    Combines producer, consumer, and administrative operations
    with advanced features like schema registry and monitoring.
    """

    async def create_consumer(self) -> ProtocolEventBusConsumer:
        """Create a new EventBus consumer instance."""
        ...

    async def create_batch_producer(self) -> ProtocolEventBusBatchProducer:
        """Create a new batch producer instance."""
        ...

    async def create_transactional_producer(self) -> ProtocolEventBusTransactionalProducer:
        """Create a new transactional producer instance."""
        ...

    async def create_topic(
        self,
        topic_name: str,
        partitions: int,
        replication_factor: int,
        config: dict[str, ContextValue] | None = None,
    ) -> None:
        """Create a new topic with the specified configuration."""
        ...

    async def delete_topic(self, topic_name: str) -> None:
        """Delete an existing topic."""
        ...

    async def list_topics(self) -> list[str]:
        """List all available topics."""
        ...

    async def get_topic_metadata(self, topic_name: str) -> dict[str, str | int]:
        """Get metadata for a specific topic."""
        ...

    async def health_check(self) -> bool:
        """Check the health of the EventBus connection."""
        ...

    async def close_client(self, timeout_seconds: float = 30.0) -> None:
        """Close the extended EventBus client and release all resources."""
        ...
```

### Event Bus Producer Handler Protocol

The `ProtocolEventBusProducerHandler` provides specialized handler for message production:

```python
from omnibase_spi.protocols.event_bus import ProtocolEventBusProducerHandler

@runtime_checkable
class ProtocolEventBusProducerHandler(Protocol):
    """
    Protocol for event bus message producer handlers.

    Defines the contract for backend-agnostic message production operations.
    This protocol extends the ProtocolHandler pattern for specialized
    event bus production operations.
    """

    @property
    def handler_type(self) -> str:
        """The type of handler as a string identifier."""
        ...

    @property
    def supports_transactions(self) -> bool:
        """Whether this producer supports transactional message delivery."""
        ...

    @property
    def supports_exactly_once(self) -> bool:
        """Whether this producer supports exactly-once delivery semantics."""
        ...

    async def send(
        self,
        topic: str,
        value: bytes,
        key: bytes | None = None,
        headers: dict[str, bytes] | None = None,
        partition: int | None = None,
        on_success: Callable | None = None,
        on_error: Callable | None = None,
    ) -> None:
        """Send a single message to the specified topic."""
        ...

    async def send_batch(
        self,
        messages: Sequence[dict],
        on_success: Callable | None = None,
        on_error: Callable | None = None,
    ) -> int:
        """Send multiple messages efficiently as a batch."""
        ...

    async def flush(self, timeout_seconds: float = 30.0) -> None:
        """Flush all pending messages to ensure delivery."""
        ...

    async def close(self, timeout_seconds: float = 30.0) -> None:
        """Close the producer and release all resources."""
        ...

    async def health_check(self) -> dict[str, Any]:
        """Check producer health and connectivity."""
        ...

    async def begin_transaction(self) -> None:
        """Begin a new transaction for atomic message delivery."""
        ...

    async def commit_transaction(self) -> None:
        """Commit the current transaction."""
        ...

    async def abort_transaction(self) -> None:
        """Abort the current transaction."""
        ...
```

### HTTP Event Bus Adapter Protocol

The `ProtocolHttpEventBusAdapter` provides HTTP-based event bus integration:

```python
from omnibase_spi.protocols.event_bus import ProtocolHttpEventBusAdapter

@runtime_checkable
class ProtocolHttpEventBusAdapter(Protocol):
    """
    Protocol for HTTP-based event bus adapters for lightweight integration.

    Provides lightweight event bus adapter for services that connect to external
    event bus systems over HTTP/REST APIs rather than native protocols.
    """

    async def publish(self, event: ProtocolEventMessage) -> bool:
        """Publish event via HTTP to the event bus."""
        ...

    async def subscribe(
        self, handler: Callable[[ProtocolEventMessage], Awaitable[bool]]
    ) -> bool:
        """Subscribe to events with HTTP-based handler."""
        ...

    async def unsubscribe(
        self, handler: Callable[[ProtocolEventMessage], Awaitable[bool]]
    ) -> bool:
        """Unsubscribe from events and stop receiving messages."""
        ...

    @property
    def is_healthy(self) -> bool:
        """Check if HTTP event bus adapter is healthy."""
        ...

    async def close(self, timeout_seconds: float = 30.0) -> None:
        """Close HTTP event bus adapter and release resources."""
        ...
```

### Event Bus Message Protocol

The `ProtocolEventBusMessage` provides message data structure for event bus operations:

```python
from omnibase_spi.protocols.event_bus import ProtocolEventBusMessage

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
```

### Event Publisher Protocol

The `ProtocolEventPublisher` provides reliable event publishing with retry logic and circuit breaker patterns:

```python
from omnibase_spi.protocols.event_bus import ProtocolEventPublisher
from omnibase_spi.protocols.types.protocol_core_types import ContextValue
from typing import Any

@runtime_checkable
class ProtocolEventPublisher(Protocol):
    """
    Protocol for event publishers with reliability features.

    Defines contract for publishing events with:
        - Retry logic with exponential backoff
        - Circuit breaker to prevent cascading failures
        - Event validation before publishing
        - Correlation ID tracking
        - Dead letter queue (DLQ) routing
        - Metrics tracking
    """

    async def publish(
        self,
        event_type: str,
        payload: Any,
        correlation_id: str | None = None,
        causation_id: str | None = None,
        metadata: dict[str, ContextValue] | None = None,
        topic: str | None = None,
        partition_key: str | None = None,
    ) -> bool:
        """Publish event to Kafka with retry and circuit breaker."""
        ...

    async def get_metrics(self) -> dict[str, Any]:
        """Get publisher metrics including success/failure counts."""
        ...

    async def close(self) -> None:
        """Close publisher and flush pending messages."""
        ...
```

### Dead Letter Queue Handler Protocol

The `ProtocolDLQHandler` provides DLQ monitoring, metrics, and reprocessing:

```python
from omnibase_spi.protocols.event_bus import ProtocolDLQHandler
from typing import Any

@runtime_checkable
class ProtocolDLQHandler(Protocol):
    """
    Protocol for Dead Letter Queue monitoring and reprocessing.

    Defines contract for DLQ management:
        - DLQ message consumption and monitoring
        - Metrics tracking (message count, error patterns, age)
        - Reprocessing with backoff strategy
        - Alert integration for DLQ overflow
    """

    async def start(self) -> None:
        """Start DLQ handler, subscribing to *.dlq topics."""
        ...

    async def stop(self) -> None:
        """Stop DLQ handler gracefully."""
        ...

    async def reprocess_dlq(
        self, dlq_topic: str, limit: int | None = None
    ) -> dict[str, Any]:
        """
        Reprocess messages from specific DLQ topic.

        Returns:
            Dict with messages_reprocessed, messages_failed, errors.
        """
        ...

    async def get_metrics(self) -> dict[str, Any]:
        """
        Get DLQ metrics.

        Returns:
            Dict with total_dlq_messages, messages_by_topic,
            messages_by_error_type, oldest_message_age_hours, etc.
        """
        ...

    async def get_dlq_summary(self) -> dict[str, Any]:
        """
        Get summary of DLQ status.

        Returns:
            Dict with total_messages, alert_status, top_failing_topics, etc.
        """
        ...
```

### Schema Registry Protocol

The `ProtocolSchemaRegistry` provides schema management for event validation:

```python
from omnibase_spi.protocols.event_bus import ProtocolSchemaRegistry
from typing import Any

@runtime_checkable
class ProtocolSchemaRegistry(Protocol):
    """
    Protocol for schema registry integration.

    Defines contract for schema management and validation:
        - Schema registration (JSON Schema, Avro)
        - Schema retrieval with versioning
        - Event validation against schemas
        - Schema caching for performance
        - Compatibility checking (backward, forward, full)
    """

    async def register_schema(
        self, subject: str, schema: dict[str, Any], schema_type: str
    ) -> int:
        """
        Register schema with Schema Registry.

        Args:
            subject: Schema subject (e.g., "topic-name-value")
            schema: JSON Schema definition
            schema_type: Schema type ("JSON", "AVRO", "PROTOBUF")

        Returns:
            Schema ID from registry
        """
        ...

    async def get_schema(
        self, subject: str, version: str
    ) -> dict[str, Any] | None:
        """
        Get schema from Schema Registry.

        Args:
            subject: Schema subject
            version: Schema version ("latest", "v1.0.0", etc.)

        Returns:
            JSON Schema definition or None if not found
        """
        ...

    async def validate_event(
        self, subject: str, event_data: dict[str, Any]
    ) -> tuple[bool, str | None]:
        """
        Validate event data against schema.

        Returns:
            Tuple of (is_valid, error_message)
        """
        ...

    async def close(self) -> None:
        """Close schema registry client and release resources."""
        ...
```

## Type Definitions

### Event Bus Types

The event bus protocols use several type aliases defined in `omnibase_spi.protocols.types.protocol_event_bus_types`:

```python
from omnibase_spi.protocols.types.protocol_event_bus_types import (
    LiteralEventPriority,
    LiteralAuthStatus,
    MessageKey,
    EventStatus,
)

LiteralEventPriority = Literal["low", "normal", "high", "critical"]
"""
Event priority levels for message routing and processing.

Values:
    low: Low priority - process when resources available
    normal: Normal priority - standard processing order
    high: High priority - process before normal priority
    critical: Critical priority - immediate processing required
"""

LiteralAuthStatus = Literal["authenticated", "unauthenticated", "expired", "invalid"]
"""
Authentication status for event bus credentials.

Values:
    authenticated: Credentials validated successfully
    unauthenticated: No credentials provided
    expired: Credentials have expired
    invalid: Credentials are invalid or rejected
"""

MessageKey = bytes | None
"""
Type alias for Kafka message keys.

Used for message partitioning and ordering. When set, messages with
the same key are guaranteed to be delivered to the same partition.
"""

EventStatus = LiteralBaseStatus
"""
Alias for base operation status used in event processing.
Re-exports LiteralBaseStatus for event-specific contexts.
"""
```

### Schema Registry Types

The `ProtocolSchemaRegistry` supports multiple schema formats passed as string parameters:

```python
# Supported schema_type values for register_schema():
# - "JSON": JSON Schema (draft-07)
# - "AVRO": Apache Avro schema format
# - "PROTOBUF": Protocol Buffers schema

await registry.register_schema(
    subject="my-topic-value",
    schema=schema_dict,
    schema_type="JSON"  # or "AVRO" or "PROTOBUF"
)
```

**Note**: Schema type is passed as a string parameter rather than a Literal type
to maintain flexibility for future schema format additions.

**Versioning Strategy**: When new schema types are added (e.g., "THRIFT", "FLATBUFFERS"):
1. New schema types are documented in this reference with their version of introduction
2. Implementations MUST handle unknown schema types gracefully with `InvalidProtocolStateError`
3. Backward compatibility is maintained - existing schema types are never removed
4. New types follow semantic versioning: minor version bump for new formats, patch for fixes

## 🚀 Usage Examples

### Basic Event Publishing

```python
from omnibase_spi.protocols.event_bus import ProtocolEventBusProvider

# Initialize event bus
event_bus: ProtocolEventBusProvider = get_event_bus()

# Publish event
await event_bus.publish_event(
    topic="user-events",
    message=ProtocolEventMessage(
        topic="user-events",
        key=b"user-12345",
        value=b'{"action": "user_created", "user_id": "12345"}',
        headers={"event_type": "user_created"},
        correlation_id=UUID("req-abc123")
    ),
    partition_key="user-12345"
)
```

### Event Subscription

```python
# Subscribe to events
subscription_id = await event_bus.subscribe_to_topic(
    topic="user-events",
    handler=user_event_handler,
    group_id="user-service"
)

# Event handler implementation
async def user_event_handler(
    message: ProtocolEventMessage, context: dict[str, ContextValue]
) -> None:
    print(f"Received event: {message.value.decode()}")
    print(f"Correlation ID: {message.correlation_id}")
    await message.ack()
```

### Kafka Integration

```python
from omnibase_spi.protocols.event_bus import ProtocolKafkaAdapter

# Initialize Kafka adapter
kafka_adapter: ProtocolKafkaAdapter = get_kafka_adapter()

# Connect to Kafka cluster
await kafka_adapter.connect_to_cluster([
    "kafka-1:9092",
    "kafka-2:9092",
    "kafka-3:9092"
])

# Create Kafka topic
await kafka_adapter.create_kafka_topic(
    topic="user-events",
    partitions=3,
    replication_factor=3
)

# Get Kafka metadata
metadata = await kafka_adapter.get_kafka_metadata()
print(f"Kafka cluster: {metadata.cluster_id}")
print(f"Brokers: {metadata.brokers}")
```

### Batch Publishing

```python
from omnibase_spi.protocols.event_bus import ProtocolEventPublisher

# Initialize event publisher
publisher: ProtocolEventPublisher = get_event_publisher()

# Publish batch of events
messages = [
    ProtocolEventMessage(topic="orders", value=b'{"order_id": "1"}'),
    ProtocolEventMessage(topic="orders", value=b'{"order_id": "2"}'),
    ProtocolEventMessage(topic="orders", value=b'{"order_id": "3"}')
]

batch_result = await publisher.publish_batch(
    topic="orders",
    messages=messages,
    compression="gzip"
)

print(f"Published {batch_result.success_count} messages")
print(f"Failed: {batch_result.failure_count}")
```

### Dead Letter Queue Handling

```python
from omnibase_spi.protocols.event_bus import ProtocolDLQHandler

# Initialize DLQ handler
dlq_handler: ProtocolDLQHandler = get_dlq_handler()

# Handle failed message
dlq_result = await dlq_handler.handle_failed_message(
    message=failed_message,
    error=ProcessingError("Invalid data format"),
    retry_count=3
)

if dlq_result.retry_eligible:
    print("Message eligible for retry")
else:
    print("Message sent to dead letter queue")

# Get DLQ messages for analysis
dlq_messages = await dlq_handler.get_dlq_messages("user-events", limit=50)
for dlq_msg in dlq_messages:
    print(f"Failed message: {dlq_msg.original_message.value}")
    print(f"Failure reason: {dlq_msg.failure_reason}")
```

### Schema Registry Integration

```python
from omnibase_spi.protocols.event_bus import ProtocolSchemaRegistry

# Initialize schema registry
schema_registry: ProtocolSchemaRegistry = get_schema_registry()

# Register schema
schema_version = await schema_registry.register_schema(
    subject="user-events-value",
    schema={
        "type": "record",
        "name": "UserEvent",
        "fields": [
            {"name": "user_id", "type": "string"},
            {"name": "action", "type": "string"},
            {"name": "timestamp", "type": "long"}
        ]
    },
    schema_type="AVRO"
)

# Check schema compatibility
compatibility_result = await schema_registry.check_compatibility(
    subject="user-events-value",
    schema=new_schema
)

if compatibility_result.compatible:
    print("Schema is compatible")
else:
    print(f"Schema incompatible: {compatibility_result.reason}")
```

## Error Handling

The event bus protocols use the SPI exception hierarchy for error handling. Implementations should catch and handle these exceptions appropriately.

### Exception Types

| Exception | Description | Common Causes |
|-----------|-------------|---------------|
| `SPIError` | Base exception for all SPI errors | Any protocol-related error |
| `ProtocolHandlerError` | Handler execution errors | Message serialization, delivery failures |
| `HandlerInitializationError` | Connection and setup errors | Broker unavailable, auth failure, timeout |
| `RegistryError` | Registry lookup errors | Unknown topic, missing handler |
| `InvalidProtocolStateError` | Lifecycle state violations | Publishing before connection established |

### Connection and Initialization Errors

```python
from omnibase_spi.exceptions import (
    SPIError,
    HandlerInitializationError,
    InvalidProtocolStateError,
)
import logging

logger = logging.getLogger(__name__)

async def initialize_event_bus() -> ProtocolEventBusProvider:
    """Initialize event bus with proper error handling."""
    try:
        event_bus = await create_event_bus(
            backend="kafka",
            bootstrap_servers=["kafka-1:9092", "kafka-2:9092"]
        )
        return event_bus
    except HandlerInitializationError as e:
        # Connection failed - broker unavailable, auth failed, etc.
        logger.error(
            f"Failed to connect to event bus: {e}",
            extra={"context": e.context}
        )
        raise
    except TimeoutError as e:
        # Connection timeout
        logger.error(f"Event bus connection timed out: {e}")
        raise HandlerInitializationError(
            "Event bus connection timed out",
            context={"timeout_seconds": 30, "backend": "kafka"}
        )
```

### Publishing Errors

```python
from omnibase_spi.exceptions import (
    ProtocolHandlerError,
    InvalidProtocolStateError,
)

async def publish_event_safely(
    event_bus: ProtocolEventBusProvider,
    topic: str,
    message: ProtocolEventMessage,
) -> bool:
    """Publish event with comprehensive error handling."""
    try:
        await event_bus.publish_event(
            topic=topic,
            message=message,
            partition_key=str(message.correlation_id)
        )
        return True

    except InvalidProtocolStateError as e:
        # Event bus not in valid state (not connected, shutting down)
        logger.error(
            f"Event bus not ready for publishing: {e}",
            extra={"current_state": e.context.get("current_state")}
        )
        return False

    except ProtocolHandlerError as e:
        # Publishing failed (serialization, network, broker error)
        logger.error(
            f"Failed to publish event to {topic}: {e}",
            extra={
                "topic": topic,
                "message_id": str(message.message_id),
                "context": e.context,
            }
        )
        return False

    except TimeoutError:
        # Publish operation timed out
        logger.warning(f"Publish to {topic} timed out, message may be queued")
        return False
```

### Context Manager Error Handling

```python
from omnibase_spi.protocols.event_bus import ProtocolEventBusContextManager
from omnibase_spi.exceptions import HandlerInitializationError, SPIError

async def process_with_event_bus(
    context_manager: ProtocolEventBusContextManager,
    events: list[ProtocolEventMessage],
) -> None:
    """Process events using context manager with error handling."""
    try:
        async with context_manager as event_bus:
            for event in events:
                await event_bus.publish(event)

    except HandlerInitializationError as e:
        # Failed to establish connection on context enter
        logger.error(f"Failed to connect to event bus: {e}")
        raise

    except SPIError as e:
        # Any other SPI-related error during processing
        logger.error(
            f"Event bus operation failed: {e}",
            extra={"context": e.context}
        )
        raise

    # Note: Context manager handles cleanup in __aexit__ even if exception occurs
```

### Subscription Error Handling

```python
from omnibase_spi.exceptions import RegistryError, ProtocolHandlerError

async def subscribe_with_retry(
    event_bus: ProtocolEventBusProvider,
    topic: str,
    handler: ProtocolEventHandler,
    max_retries: int = 3,
) -> str | None:
    """Subscribe to topic with retry logic."""
    for attempt in range(max_retries):
        try:
            subscription_id = await event_bus.subscribe_to_topic(
                topic=topic,
                handler=handler,
                group_id="my-consumer-group"
            )
            logger.info(f"Subscribed to {topic}: {subscription_id}")
            return subscription_id

        except RegistryError as e:
            # Topic doesn't exist or handler not compatible
            logger.error(f"Registry error subscribing to {topic}: {e}")
            raise  # Don't retry registry errors

        except ProtocolHandlerError as e:
            # Transient error - may be worth retrying
            logger.warning(
                f"Subscription attempt {attempt + 1} failed: {e}",
                extra={"context": e.context}
            )
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
            else:
                logger.error(f"Failed to subscribe after {max_retries} attempts")
                raise

    return None
```

### Dead Letter Queue Error Handling

```python
from omnibase_spi.protocols.event_bus import ProtocolDLQHandler
from omnibase_spi.exceptions import SPIError

async def handle_message_with_dlq(
    message: ProtocolEventMessage,
    dlq_handler: ProtocolDLQHandler,
    process_func: Callable,
) -> None:
    """Process message with automatic DLQ handling on failure."""
    retry_count = 0
    max_retries = 3

    while retry_count < max_retries:
        try:
            await process_func(message)
            await message.ack()
            return

        except Exception as processing_error:
            retry_count += 1
            logger.warning(
                f"Message processing failed (attempt {retry_count}): {processing_error}"
            )

            if retry_count >= max_retries:
                # Send to DLQ after exhausting retries
                try:
                    dlq_result = await dlq_handler.handle_failed_message(
                        message=message,
                        error=processing_error,
                        retry_count=retry_count,
                    )
                    logger.info(
                        f"Message sent to DLQ: {dlq_result.dlq_message_id}"
                    )
                except SPIError as dlq_error:
                    # DLQ handling itself failed - log and nack
                    logger.error(f"DLQ handling failed: {dlq_error}")
                    await message.nack(requeue=False)
```

## Implementation Notes

### Backend Adapter Patterns

The event bus supports multiple backend implementations:

```python
# Kafka backend
kafka_bus = KafkaEventBus(servers=["kafka:9092"])

# Redpanda backend
redpanda_bus = RedpandaEventBus(brokers=["redpanda:9092"])

# In-memory backend (for testing)
memory_bus = InMemoryEventBus()
```

### Message Serialization

Comprehensive serialization support:

```python
# JSON serialization
message = ProtocolEventMessage(
    topic="events",
    value=json.dumps(event_data).encode(),
    headers={"content_type": "application/json"}
)

# Avro serialization with schema registry
avro_message = await serialize_with_avro(
    data=event_data,
    schema_id=schema_version
)
```

### Performance Optimization

Advanced performance features:

```python
# Batch publishing for throughput
await publisher.publish_batch(topic, messages, compression="snappy")

# Retry with exponential backoff
await publisher.publish_with_retry(
    topic, message, max_retries=5, backoff_ms=1000
)
```

## Context Manager Protocol

The `ProtocolEventBusContextManager` provides async context management for event bus lifecycle:

```python
from omnibase_spi.protocols.event_bus import ProtocolEventBusContextManager

@runtime_checkable
class ProtocolEventBusContextManager(Protocol):
    """
    Protocol for async context managers that yield a ProtocolEventBusBase-compatible object.

    Provides lifecycle management for event bus resources with proper cleanup.
    Implementations must support async context management and return a ProtocolEventBusBase on enter.

    Key Features:
        - Async context manager support (__aenter__, __aexit__)
        - Configuration-based initialization
        - Resource lifecycle management
        - Proper cleanup and error handling
    """

    async def __aenter__(self) -> "ProtocolEventBusBase": ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None: ...
```

### Context Manager Usage

```python
from omnibase_spi.protocols.event_bus import ProtocolEventBusContextManager

# Get context manager from provider
context_manager: ProtocolEventBusContextManager = get_event_bus_context_manager()

# Usage with async context manager pattern
async with context_manager as event_bus:
    # event_bus is guaranteed to implement ProtocolEventBusBase
    await event_bus.publish(
        topic="user-events",
        key=None,
        value=b'{"action": "user_created"}',
        headers={"event_type": "user_created"}
    )

    # Context manager handles connection lifecycle automatically
    # - Establishes connection on enter
    # - Performs cleanup on exit (even if exception occurs)
```

## Event Envelope Protocol

The `ProtocolEventEnvelope` provides a generic wrapper for event payloads, breaking circular dependencies:

```python
from omnibase_spi.protocols.event_bus import ProtocolEventEnvelope

@runtime_checkable
class ProtocolEventEnvelope(Protocol, Generic[T]):
    """
    Protocol defining the minimal interface for event envelopes.

    This protocol allows mixins to type-hint envelope parameters without
    importing the concrete ModelEventEnvelope class, breaking circular dependencies.
    """

    async def get_payload(self) -> T:
        """Get the wrapped event payload."""
        ...
```

### Envelope Usage Pattern

```python
from omnibase_spi.protocols.event_bus import ProtocolEventEnvelope

# Handler that works with envelopes
async def handle_envelope_event(
    envelope: ProtocolEventEnvelope[UserCreatedPayload]
) -> None:
    # Extract payload from envelope
    payload = await envelope.get_payload()
    print(f"User created: {payload.user_id}")
```

## Event Bus Base Protocols

The base protocols define core event publishing patterns:

### ProtocolEventBusBase

```python
@runtime_checkable
class ProtocolEventBusBase(Protocol):
    """
    Base protocol for event bus operations.

    Defines common event publishing interface that both synchronous
    and asynchronous event buses must implement.
    """

    async def publish(self, event: ProtocolEventMessage) -> None: ...
```

### ProtocolSyncEventBus

```python
@runtime_checkable
class ProtocolSyncEventBus(ProtocolEventBusBase, Protocol):
    """
    Protocol for synchronous event bus operations.
    Inherits from ProtocolEventBusBase for unified interface.
    """

    async def publish_sync(self, event: ProtocolEventMessage) -> None: ...
```

### ProtocolAsyncEventBus

```python
@runtime_checkable
class ProtocolAsyncEventBus(ProtocolEventBusBase, Protocol):
    """
    Protocol for asynchronous event bus operations.
    Inherits from ProtocolEventBusBase for unified interface.
    """

    async def publish_async(self, event: ProtocolEventMessage) -> None: ...
```

## Event Bus Registry Protocol

The `ProtocolEventBusRegistry` provides dependency injection for event bus access:

```python
@runtime_checkable
class ProtocolEventBusRegistry(Protocol):
    """
    Protocol for registry that provides event bus access.

    Defines interface for service registries that provide
    access to event bus instances for dependency injection.
    """

    event_bus: ProtocolEventBusBase | None

    async def validate_registry_bus(self) -> bool: ...

    def has_bus_access(self) -> bool: ...
```

### Registry Integration

```python
from omnibase_spi.protocols.event_bus import ProtocolEventBusRegistry

# Service that uses registry for event bus access
class OrderService:
    def __init__(self, registry: ProtocolEventBusRegistry):
        self.registry = registry

    async def process_order(self, order_data: dict) -> None:
        # Check if event bus is available
        if not self.registry.has_bus_access():
            raise RuntimeError("Event bus not available")

        # Validate bus before use
        await self.registry.validate_registry_bus()

        # Use event bus from registry
        event_bus = self.registry.event_bus
        if event_bus:
            await event_bus.publish(create_order_event(order_data))
```

## Event Bus Log Emitter Protocol

The `ProtocolEventBusLogEmitter` enables structured log emission:

```python
@runtime_checkable
class ProtocolEventBusLogEmitter(Protocol):
    """
    Protocol for structured log emission.

    Defines interface for components that can emit structured
    log events with typed data and log levels.
    """

    def emit_log_event(
        self,
        level: LiteralLogLevel,
        message: str,
        data: dict[str, str | int | float | bool],
    ) -> None: ...
```

### Log Emission Example

```python
from omnibase_spi.protocols.event_bus import ProtocolEventBusLogEmitter

class EventProcessor:
    def __init__(self, log_emitter: ProtocolEventBusLogEmitter):
        self.log_emitter = log_emitter

    async def process_event(self, event: ProtocolEventMessage) -> None:
        self.log_emitter.emit_log_event(
            level="INFO",
            message="Processing event",
            data={
                "topic": event.topic,
                "partition": event.partition or 0,
                "offset": event.offset or "unknown"
            }
        )

        # Process event...

        self.log_emitter.emit_log_event(
            level="DEBUG",
            message="Event processed successfully",
            data={"processing_time_ms": 45}
        )
```

## Event Orchestrator Protocol

The `ProtocolEventOrchestrator` provides comprehensive workflow coordination:

```python
@runtime_checkable
class ProtocolEventOrchestrator(Protocol):
    """
    Protocol for event orchestration and workflow coordination in ONEX systems.

    Key Features:
        - Agent lifecycle management (spawn, terminate, health monitoring)
        - Work ticket assignment and load balancing
        - Event-driven coordination with async patterns
        - Comprehensive error handling and recovery
        - Performance metrics and monitoring
    """

    async def handle_work_ticket_created(self, ticket: "ProtocolWorkTicket") -> bool: ...

    async def assign_work_to_agent(
        self,
        ticket: "ProtocolWorkTicket",
        agent_id: str | None = None,
    ) -> str: ...

    async def handle_agent_progress_update(
        self, update: "ProtocolProgressUpdate"
    ) -> bool: ...

    async def handle_work_completion(self, result: "ProtocolWorkResult") -> bool: ...

    async def handle_agent_error(self, error_event: "ProtocolAgentEvent") -> bool: ...

    async def monitor_agent_health(self) -> dict[str, "ProtocolEventBusAgentStatus"]: ...

    async def rebalance_workload(self) -> bool: ...

    async def handle_agent_spawn_request(self, agent_config_template: str) -> str: ...

    async def handle_agent_termination_request(
        self, agent_id: str, reason: str
    ) -> bool: ...

    async def get_workflow_metrics(self) -> dict[str, float]: ...

    async def subscribe_to_orchestration_events(
        self,
    ) -> AsyncIterator["ProtocolOnexEvent"]: ...

    # Additional methods for priority, capacity, pause/resume, etc.
```

### Orchestrator Usage

```python
from omnibase_spi.protocols.event_bus import ProtocolEventOrchestrator

# Initialize orchestrator
orchestrator: ProtocolEventOrchestrator = get_orchestrator()

# Handle work ticket creation
ticket = create_work_ticket(task_type="data_processing")
success = await orchestrator.handle_work_ticket_created(ticket)

# Monitor agent health
health_status = await orchestrator.monitor_agent_health()
for agent_id, status in health_status.items():
    print(f"Agent {agent_id}: {status}")

# Subscribe to orchestration events
async for event in orchestrator.subscribe_to_orchestration_events():
    print(f"Event: {event.event_type}")
    await process_orchestration_event(event)

# Get workflow metrics
metrics = await orchestrator.get_workflow_metrics()
print(f"Throughput: {metrics['throughput_per_second']}")
print(f"Average latency: {metrics['avg_latency_ms']}ms")
```

## Event Pub/Sub Protocol

The `ProtocolEventPubSub` provides simple pub/sub operations:

```python
@runtime_checkable
class ProtocolEventPubSub(Protocol):
    """
    Canonical protocol for simple event pub/sub operations.
    Supports both synchronous and asynchronous methods for maximum flexibility.
    All event bus implementations must expose a unique, stable bus_id for diagnostics.
    """

    @property
    def credentials(self) -> ProtocolEventBusCredentials | None: ...

    async def publish(self, event: "ProtocolEvent") -> None: ...

    async def publish_async(self, event: "ProtocolEvent") -> None: ...

    async def subscribe(self, callback: Callable[[ProtocolEvent], None]) -> None: ...

    async def subscribe_async(
        self, callback: Callable[[ProtocolEvent], None]
    ) -> None: ...

    async def unsubscribe(self, callback: Callable[[ProtocolEvent], None]) -> None: ...

    async def unsubscribe_async(
        self, callback: Callable[[ProtocolEvent], None]
    ) -> None: ...

    def clear(self) -> None: ...

    @property
    def bus_id(self) -> str: ...
```

### Event Bus Credentials Protocol

```python
@runtime_checkable
class ProtocolEventBusCredentials(Protocol):
    """
    Canonical credentials protocol for event bus authentication/authorization.
    Supports token, username/password, and TLS certs for future event bus support.
    """

    token: str | None
    username: str | None
    password: str | None
    cert: str | None
    key: str | None
    ca: str | None
    extra: dict[str, ContextValue] | None

    async def validate_credentials(self) -> bool: ...

    def is_secure(self) -> bool: ...
```

## Event Type Protocols

The event bus includes comprehensive type protocols for event data:

### ProtocolEventMessage

```python
@runtime_checkable
class ProtocolEventMessage(Protocol):
    """
    Protocol for ONEX event bus message objects.
    Kafka/RedPanda compatible following ONEX Messaging Design.
    """

    topic: str
    key: bytes | None
    value: bytes
    headers: ProtocolEventHeaders
    offset: str | None
    partition: int | None

    async def ack(self) -> None: ...
```

### ProtocolEventHeaders

```python
@runtime_checkable
class ProtocolEventHeaders(Protocol):
    """
    Standardized headers for ONEX event bus messages.
    Includes tracing, routing, and retry configuration.
    """

    content_type: str
    correlation_id: UUID
    message_id: UUID
    timestamp: ProtocolDateTime
    source: str
    event_type: str
    schema_version: ProtocolSemVer
    destination: str | None
    trace_id: str | None
    span_id: str | None
    parent_span_id: str | None
    operation_name: str | None
    priority: LiteralEventPriority | None
    routing_key: str | None
    partition_key: str | None
    retry_count: int | None
    max_retries: int | None
    ttl_seconds: int | None

    async def validate_headers(self) -> bool: ...
```

### ProtocolOnexEvent

```python
@runtime_checkable
class ProtocolOnexEvent(Protocol):
    """
    Extended event protocol with full metadata support for ONEX platform events.
    """

    event_id: UUID
    event_type: str
    timestamp: ProtocolDateTime
    source: str
    payload: dict[str, ProtocolEventData]
    correlation_id: UUID
    metadata: dict[str, ProtocolEventData]

    async def validate_onex_event(self) -> bool: ...
```

## Protocol Statistics

| Metric | Value |
|--------|-------|
| **Total Protocols** | 24 event bus protocols |
| **Backend Support** | Kafka, Redpanda, HTTP, in-memory |
| **Message Features** | Serialization, compression, batching, envelopes, transactions |
| **Reliability** | Dead letter queues, retry logic, circuit breakers, exactly-once semantics |
| **Schema Management** | Avro, JSON, Protobuf schema support |
| **Performance** | High-throughput batch messaging with optimization |
| **Monitoring** | Comprehensive metrics and health tracking |
| **Consumer Features** | Topic subscription, offset management, consumer groups |
| **Producer Features** | Batch production, transactions, custom partitioning |

## Import Reference

```python
# Provider and context management
from omnibase_spi.protocols.event_bus import (
    ProtocolEventBusProvider,
    ProtocolEventBusContextManager,
)

# Base interfaces
from omnibase_spi.protocols.event_bus import (
    ProtocolEventBusBase,
    ProtocolSyncEventBus,
    ProtocolAsyncEventBus,
    ProtocolEventBusRegistry,
    ProtocolEventBusLogEmitter,
)

# Service and envelope
from omnibase_spi.protocols.event_bus import (
    ProtocolEventBusService,
    ProtocolEventEnvelope,
)

# Client protocols
from omnibase_spi.protocols.event_bus import (
    ProtocolEventBusClient,
    ProtocolEventBusClientProvider,
)

# Extended client and consumer
from omnibase_spi.protocols.event_bus import (
    ProtocolEventBusExtendedClient,
    ProtocolEventBusConsumer,
    ProtocolEventBusMessage,
)

# Producer protocols
from omnibase_spi.protocols.event_bus import (
    ProtocolEventBusProducerHandler,
    ProtocolEventBusBatchProducer,
    ProtocolEventBusTransactionalProducer,
)

# Backend adapters
from omnibase_spi.protocols.event_bus import (
    ProtocolKafkaAdapter,
    ProtocolRedpandaAdapter,
    ProtocolHttpEventBusAdapter,
)

# Publishing and error handling
from omnibase_spi.protocols.event_bus import (
    ProtocolEventPublisher,
    ProtocolDLQHandler,
    ProtocolSchemaRegistry,
)

# Event types (from types module)
from omnibase_spi.protocols.types.protocol_event_bus_types import (
    ProtocolEventMessage,
    ProtocolEventHeaders,
    ProtocolEvent,
    ProtocolOnexEvent,
    LiteralEventPriority,
    LiteralAuthStatus,
)
```

## See Also

- **[WORKFLOW-ORCHESTRATION.md](./WORKFLOW-ORCHESTRATION.md)** - Workflow-specific event bus extensions
- **[HANDLERS.md](./HANDLERS.md)** - Handler protocols, which differ from event bus (request-response vs fire-and-forget)
- **[NODES.md](./NODES.md)** - Node protocols including effect nodes that may publish events
- **[EXCEPTIONS.md](./EXCEPTIONS.md)** - Exception hierarchy for event bus error handling
- **[README.md](./README.md)** - Complete API reference index

---

*This API reference documents the event bus protocols defined in `omnibase_spi`. For the base `ProtocolEventBus` interface, see `omnibase_core` documentation.*
