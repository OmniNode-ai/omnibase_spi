# Event Bus API Reference

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

## Protocol Architecture

The event bus domain consists of **18+ specialized protocols** organized into these categories:

| Category | Protocols | Purpose |
|----------|-----------|---------|
| Provider & Factory | `ProtocolEventBusProvider` | Event bus instance creation and lifecycle |
| Context Management | `ProtocolEventBusContextManager` | Async context manager for resource lifecycle |
| Base Interfaces | `ProtocolEventBusBase`, `ProtocolSyncEventBus`, `ProtocolAsyncEventBus` | Core publish/subscribe patterns |
| Service & Registry | `ProtocolEventBusService`, `ProtocolEventBusRegistry` | Service operations and dependency injection |
| Event Envelope | `ProtocolEventEnvelope` | Generic envelope for breaking circular dependencies |
| Pub/Sub | `ProtocolEventPubSub`, `ProtocolEventBusCredentials` | Simple pub/sub and authentication |
| Backend Adapters | `ProtocolKafkaAdapter`, `ProtocolRedpandaAdapter` | Backend-specific implementations |
| Publishing | `ProtocolEventPublisher` | Batch publishing and compression |
| Error Handling | `ProtocolDLQHandler` | Dead letter queue management |
| Schema Management | `ProtocolSchemaRegistry` | Schema versioning and compatibility |
| Orchestration | `ProtocolEventOrchestrator` | Distributed workflow coordination |
| Logging | `ProtocolEventBusLogEmitter` | Structured log emission |

### Event Bus Provider Protocol

```python
from omnibase_spi.protocols.event_bus import ProtocolEventBusProvider
from omnibase_spi.protocols.types.protocol_event_bus_types import (
    ProtocolEventMessage,
    ProtocolEventHandler,
    LiteralEventBusBackend,
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

### Event Publisher Protocol

```python
@runtime_checkable
class ProtocolEventPublisher(Protocol):
    """
    Protocol for event publishing operations.

    Provides specialized event publishing with batching,
    compression, and performance optimization.

    Key Features:
        - Batch event publishing
        - Message compression
        - Retry mechanisms
        - Performance optimization
        - Error handling
    """

    async def publish_batch(
        self,
        topic: str,
        messages: list[ProtocolEventMessage],
        compression: LiteralCompressionType | None = None,
    ) -> ProtocolBatchPublishResult: ...

    async def publish_with_retry(
        self,
        topic: str,
        message: ProtocolEventMessage,
        max_retries: int = 3,
        backoff_ms: int = 1000,
    ) -> bool: ...

    async def publish_compressed(
        self,
        topic: str,
        message: ProtocolEventMessage,
        compression_type: LiteralCompressionType,
    ) -> bool: ...

    async def get_publisher_metrics(self) -> ProtocolPublisherMetrics: ...
```

### Dead Letter Queue Handler Protocol

```python
@runtime_checkable
class ProtocolDLQHandler(Protocol):
    """
    Protocol for dead letter queue handling.

    Manages failed message processing, retry logic,
    and dead letter queue operations.

    Key Features:
        - Failed message handling
        - Retry logic and backoff
        - Dead letter queue management
        - Message analysis and debugging
        - Recovery operations
    """

    async def handle_failed_message(
        self,
        message: ProtocolEventMessage,
        error: Exception,
        retry_count: int,
    ) -> ProtocolDLQResult: ...

    async def retry_failed_message(
        self, dlq_message_id: str
    ) -> bool: ...

    async def get_dlq_messages(
        self, topic: str, limit: int = 100
    ) -> list[ProtocolDLQMessage]: ...

    async def clear_dlq_messages(
        self, topic: str, older_than_hours: int
    ) -> int: ...

    async def analyze_failure_patterns(
        self, topic: str, time_range_hours: int
    ) -> ProtocolFailureAnalysis: ...
```

### Schema Registry Protocol

```python
@runtime_checkable
class ProtocolSchemaRegistry(Protocol):
    """
    Protocol for event schema registry operations.

    Manages event schemas, versioning, and compatibility
    across distributed systems.

    Key Features:
        - Schema registration and versioning
        - Schema compatibility checking
        - Schema evolution support
        - Serialization/deserialization
        - Schema discovery
    """

    async def register_schema(
        self,
        subject: str,
        schema: dict[str, Any],
        schema_type: LiteralSchemaType = "AVRO",
    ) -> int: ...

    async def get_schema(
        self, subject: str, version: int | None = None
    ) -> ProtocolSchemaInfo: ...

    async def check_compatibility(
        self, subject: str, schema: dict[str, Any]
    ) -> ProtocolCompatibilityResult: ...

    async def get_schema_versions(
        self, subject: str
    ) -> list[int]: ...

    async def delete_schema(
        self, subject: str, version: int
    ) -> bool: ...

    async def get_subjects(self) -> list[str]: ...
```

## 🔧 Type Definitions

### Event Bus Types

```python
LiteralEventBusBackend = Literal["kafka", "redpanda", "redis", "in_memory", "rabbitmq"]
"""
Event bus backend implementations.

Values:
    kafka: Apache Kafka cluster
    redpanda: Redpanda streaming platform
    redis: Redis pub/sub
    in_memory: In-memory implementation
    rabbitmq: RabbitMQ message broker
"""

LiteralCompressionType = Literal["none", "gzip", "snappy", "lz4", "zstd"]
"""
Message compression types.

Values:
    none: No compression
    gzip: GZIP compression
    snappy: Snappy compression
    lz4: LZ4 compression
    zstd: Zstandard compression
"""

LiteralSchemaType = Literal["AVRO", "JSON", "PROTOBUF"]
"""
Schema types for event serialization.

Values:
    AVRO: Apache Avro schema
    JSON: JSON schema
    PROTOBUF: Protocol Buffers schema
"""
```

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

## 🔍 Implementation Notes

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
    Protocol for async context managers that yield a ProtocolEventBus-compatible object.

    Provides lifecycle management for event bus resources with proper cleanup.
    Implementations must support async context management and return a ProtocolEventBus on enter.

    Key Features:
        - Async context manager support (__aenter__, __aexit__)
        - Configuration-based initialization
        - Resource lifecycle management
        - Proper cleanup and error handling
    """

    async def __aenter__(self) -> "ProtocolEventBus": ...

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
    # event_bus is guaranteed to implement ProtocolEventBus
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
| **Total Protocols** | 18+ event bus protocols |
| **Backend Support** | Kafka, Redpanda, Redis, in-memory, RabbitMQ |
| **Message Features** | Serialization, compression, batching, envelopes |
| **Reliability** | Dead letter queues, retry logic, error handling |
| **Schema Management** | Avro, JSON, Protobuf schema support |
| **Performance** | High-throughput messaging with optimization |
| **Monitoring** | Comprehensive metrics and health tracking |
| **Orchestration** | Agent lifecycle, work distribution, load balancing |

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

# Backend adapters
from omnibase_spi.protocols.event_bus import (
    ProtocolKafkaAdapter,
    ProtocolRedpandaAdapter,
)

# Publishing and error handling
from omnibase_spi.protocols.event_bus import (
    ProtocolEventPublisher,
    ProtocolDLQHandler,
    ProtocolSchemaRegistry,
)

# Event types
from omnibase_spi.protocols.types.protocol_event_bus_types import (
    ProtocolEventMessage,
    ProtocolEventHeaders,
    ProtocolEvent,
    ProtocolOnexEvent,
    ProtocolEventPubSub,
    ProtocolEventBusCredentials,
)
```

## See Also

- **[Workflow Event Bus](WORKFLOW-ORCHESTRATION.md)** - Workflow-specific event bus extensions
- **[Developer Guide](../developer-guide/README.md)** - Implementation patterns and best practices
- **[Examples](../examples/README.md)** - Working code examples

---

*This API reference documents the event bus protocols defined in `omnibase_spi`. For the base `ProtocolEventBus` interface, see `omnibase_core` documentation.*
