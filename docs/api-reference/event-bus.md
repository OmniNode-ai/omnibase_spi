# Event Bus API Reference

## Overview

The ONEX event bus protocols provide comprehensive distributed messaging infrastructure with pluggable backend adapters, async/sync implementations, event serialization, and dead letter queue handling. These protocols enable sophisticated event-driven architectures across the ONEX ecosystem.

## 🏗️ Protocol Architecture

The event bus domain consists of **13 specialized protocols** that provide complete messaging infrastructure:

### Event Bus Protocol

```python
from omnibase_spi.protocols.event_bus import ProtocolEventBus
from omnibase_spi.protocols.types.protocol_event_bus_types import (
    ProtocolEventMessage,
    ProtocolEventHandler,
    LiteralEventBusBackend,
)

@runtime_checkable
class ProtocolEventBus(Protocol):
    """
    Core event bus protocol for distributed messaging.

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

### In-Memory Event Bus Protocol

```python
@runtime_checkable
class ProtocolEventBusInMemory(Protocol):
    """
    Protocol for in-memory event bus implementation.

    Provides lightweight in-memory event bus for testing,
    development, and single-node deployments.

    Key Features:
        - In-memory message storage
        - Synchronous and asynchronous processing
        - Topic-based message routing
        - Subscription management
        - Performance monitoring
    """

    async def initialize_memory_store(self) -> bool: ...

    async def clear_memory_store(self) -> None: ...

    async def get_memory_usage(self) -> ProtocolMemoryUsage: ...

    async def get_message_count(self, topic: str) -> int: ...

    async def get_subscription_count(self, topic: str) -> int: ...

    async def simulate_network_delay(
        self, delay_ms: int
    ) -> None: ...
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
from omnibase_spi.protocols.event_bus import ProtocolEventBus

# Initialize event bus
event_bus: ProtocolEventBus = get_event_bus()

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

## 📊 Protocol Statistics

- **Total Protocols**: 13 event bus protocols
- **Backend Support**: Kafka, Redpanda, Redis, in-memory, RabbitMQ
- **Message Features**: Serialization, compression, batching
- **Reliability**: Dead letter queues, retry logic, error handling
- **Schema Management**: Avro, JSON, Protobuf schema support
- **Performance**: High-throughput messaging with optimization
- **Monitoring**: Comprehensive metrics and health tracking

---

*This API reference is automatically generated from protocol definitions and maintained alongside the codebase.*
