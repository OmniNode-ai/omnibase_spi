# Event Bus Protocols API Reference

## Overview

The ONEX event bus protocols provide comprehensive, type-safe event messaging and streaming capabilities for distributed systems. This system enables environment isolation, pluggable messaging backends (Kafka/Redpanda), and sophisticated event sourcing patterns with complete audit trails.

## Protocol Architecture

The event bus domain consists of multiple specialized protocols that work together to provide a complete messaging solution:

### Core Event Bus Protocol

```python
from omnibase_spi.protocols.event_bus import ProtocolEventBus
from omnibase_spi.protocols.types.event_bus_types import EventMessage, EventMetadata

@runtime_checkable
class ProtocolEventBus(Protocol):
    """
    Core event bus protocol for distributed messaging.

    Provides environment isolation, pluggable backends, and
    comprehensive event streaming capabilities.

    Features:
        - Environment isolation (dev/staging/prod)
        - Multiple messaging backend support
        - Consumer group coordination
        - Event filtering and routing
        - OpenTelemetry integration
    """

    async def publish_event(
        self,
        event_message: EventMessage,
        target_topic: Optional[str] = None
    ) -> bool:
        """
        Publish event to the event bus.

        Args:
            event_message: Event to publish with metadata
            target_topic: Optional topic override

        Returns:
            Success status of publish operation

        Raises:
            PublishError: If event publishing fails
            ValidationError: If event message is invalid
        """
        ...

    async def subscribe_to_topic(
        self,
        topic: str,
        group_id: str,
        handler: Callable[[EventMessage], Awaitable[None]],
        message_filter: Optional[Callable[[EventMessage], bool]] = None
    ) -> Callable[[], Awaitable[None]]:
        """
        Subscribe to topic with consumer group and optional filtering.

        Args:
            topic: Topic to subscribe to
            group_id: Consumer group identifier for load balancing
            handler: Async message handler function
            message_filter: Optional filter predicate

        Returns:
            Unsubscribe function to stop consuming

        Raises:
            SubscriptionError: If subscription setup fails
        """
        ...

    async def get_topic_info(self, topic: str) -> Dict[str, Any]:
        """
        Get metadata about a specific topic.

        Returns partition count, consumer groups, and other metadata.
        """
        ...
```

### Kafka Adapter Protocol

```python
from omnibase_spi.protocols.event_bus import ProtocolKafkaAdapter

@runtime_checkable
class ProtocolKafkaAdapter(Protocol):
    """
    Kafka-specific event bus adapter with advanced features.

    Provides Kafka-native features like partitioning,
    consumer groups, and transactional messaging.

    Features:
        - Partition management
        - Transactional messaging
        - Consumer group coordination
        - Offset management
        - Dead letter queues
    """

    async def create_topic(
        self,
        topic_name: str,
        partition_count: int = 3,
        replication_factor: int = 1,
        config: Optional[Dict[str, str]] = None
    ) -> bool:
        """Create Kafka topic with specified configuration."""
        ...

    async def publish_to_partition(
        self,
        topic: str,
        partition: int,
        event_message: EventMessage,
        transaction_id: Optional[str] = None
    ) -> bool:
        """Publish event to specific partition with optional transaction."""
        ...

    async def consume_from_partition(
        self,
        topic: str,
        partition: int,
        offset: int,
        max_messages: int = 100
    ) -> List[EventMessage]:
        """Consume messages from specific partition starting at offset."""
        ...
```

### Redpanda Adapter Protocol

```python
from omnibase_spi.protocols.event_bus import ProtocolRedpandaAdapter

@runtime_checkable
class ProtocolRedpandaAdapter(Protocol):
    """
    Redpanda-specific event bus adapter optimized for performance.

    Provides Redpanda-native optimizations and features
    while maintaining Kafka compatibility.

    Features:
        - High-performance streaming
        - Built-in schema registry
        - WebAssembly transforms
        - HTTP proxy support
    """

    async def create_materialized_view(
        self,
        view_name: str,
        source_topic: str,
        transform_function: str
    ) -> bool:
        """Create materialized view with WebAssembly transform."""
        ...

    async def register_schema(
        self,
        subject: str,
        schema_definition: Dict[str, Any],
        schema_type: str = "JSON"
    ) -> int:
        """Register schema in built-in schema registry."""
        ...
```

## Type Definitions

### Core Event Types

```python
from omnibase_spi.protocols.types.event_bus_types import (
    EventMessage,
    EventMetadata,
    SecurityContext,
    EventType
)

@dataclass
class EventMessage:
    """
    Core event message with metadata and payload.

    Attributes:
        event_id: Unique event identifier
        event_type: Type/category of event
        payload: Event data as JSON-serializable dict
        metadata: Event metadata and routing information
        timestamp: ISO timestamp when event was created
        security_context: Authentication and authorization context
    """
    event_id: str
    event_type: EventType
    payload: Dict[str, Any]
    metadata: EventMetadata
    timestamp: str
    security_context: Optional[SecurityContext] = None

@dataclass
class EventMetadata:
    """
    Event metadata for routing and processing.

    Attributes:
        source: Source service/component that produced event
        correlation_id: Request correlation identifier
        causation_id: Previous event that caused this event
        environment: Target environment (dev/staging/prod)
        priority: Event priority level (0-10, 10=highest)
        ttl_seconds: Time-to-live for event processing
        headers: Additional routing headers
    """
    source: str
    correlation_id: str
    causation_id: Optional[str] = None
    environment: str = "dev"
    priority: int = 5
    ttl_seconds: Optional[int] = None
    headers: Optional[Dict[str, str]] = None
```

### Event Types

```python
# Event type definitions for type safety
EventType = Literal[
    "system.started", "system.stopped", "system.health_check",
    "workflow.created", "workflow.started", "workflow.completed",
    "workflow.failed", "workflow.cancelled", "workflow.paused",
    "task.scheduled", "task.started", "task.completed", "task.failed",
    "mcp.tool_registered", "mcp.subsystem_registered", "mcp.health_check",
    "node.registered", "node.deregistered", "node.health_update",
    "artifact.created", "artifact.updated", "artifact.deleted",
    "user.created", "user.updated", "user.deleted",
    "data.ingested", "data.processed", "data.exported"
]
```

### Security Context

```python
@dataclass
class SecurityContext:
    """
    Security context for event authentication and authorization.

    Attributes:
        user_id: Authenticated user identifier
        tenant_id: Multi-tenant isolation identifier
        permissions: List of granted permissions
        token: Authentication token (JWT, API key, etc.)
        ip_address: Source IP address for audit logging
    """
    user_id: str
    tenant_id: str
    permissions: List[str]
    token: Optional[str] = None
    ip_address: Optional[str] = None
```

## Usage Patterns

### Basic Event Publishing

```python
from omnibase_spi.protocols.event_bus import ProtocolEventBus
from omnibase_spi.protocols.types.event_bus_types import EventMessage, EventMetadata

async def publish_user_created_event(
    event_bus: ProtocolEventBus,
    user_id: str,
    user_data: Dict[str, Any]
) -> None:
    """Publish user creation event."""

    event = EventMessage(
        event_id=str(uuid4()),
        event_type="user.created",
        payload={
            "user_id": user_id,
            "email": user_data["email"],
            "created_at": datetime.utcnow().isoformat()
        },
        metadata=EventMetadata(
            source="user_service",
            correlation_id=str(uuid4()),
            environment="prod",
            priority=7
        ),
        timestamp=datetime.utcnow().isoformat()
    )

    success = await event_bus.publish_event(event, target_topic="user_events")
    if not success:
        raise RuntimeError("Failed to publish user created event")
```

### Event Subscription with Filtering

```python
async def setup_workflow_event_processing(
    event_bus: ProtocolEventBus
) -> None:
    """Set up workflow event processing with filtering."""

    def workflow_filter(event: EventMessage) -> bool:
        """Only process high-priority workflow events."""
        return (
            event.event_type.startswith("workflow.") and
            event.metadata.priority >= 8
        )

    async def handle_workflow_event(event: EventMessage) -> None:
        """Handle high-priority workflow events."""
        if event.event_type == "workflow.failed":
            await send_alert_notification(event)
        elif event.event_type == "workflow.completed":
            await update_workflow_metrics(event)

    # Subscribe with filtering
    unsubscribe = await event_bus.subscribe_to_topic(
        topic="workflow_events",
        group_id="workflow_processor_group",
        handler=handle_workflow_event,
        message_filter=workflow_filter
    )

    # Store unsubscribe function for cleanup
    return unsubscribe
```

### Multi-Environment Event Routing

```python
async def setup_environment_routing(
    event_bus: ProtocolEventBus
) -> None:
    """Set up environment-specific event routing."""

    async def route_by_environment(event: EventMessage) -> None:
        """Route events based on environment metadata."""
        env = event.metadata.environment

        if env == "prod":
            # Production events go to monitoring systems
            await forward_to_monitoring(event)
        elif env == "staging":
            # Staging events go to test validation
            await forward_to_validation(event)
        elif env == "dev":
            # Dev events go to debugging systems
            await forward_to_debug_logs(event)

    # Subscribe to all environments but route differently
    await event_bus.subscribe_to_topic(
        topic="system_events",
        group_id="environment_router",
        handler=route_by_environment
    )
```

## Integration with Other Domains

### Workflow Orchestration Integration

```python
from omnibase_spi.protocols.workflow_orchestration import ProtocolWorkflowEventBus

# Workflow-specific event bus extends the base event bus
class WorkflowEventBusIntegration:
    """Integration pattern for workflow orchestration."""

    def __init__(
        self,
        base_event_bus: ProtocolEventBus,
        workflow_event_bus: ProtocolWorkflowEventBus
    ):
        self.base_event_bus = base_event_bus
        self.workflow_event_bus = workflow_event_bus

    async def coordinate_workflow_events(self) -> None:
        """Coordinate between base and workflow event buses."""

        # Subscribe to base events that affect workflows
        await self.base_event_bus.subscribe_to_topic(
            topic="system_events",
            group_id="workflow_coordinator",
            handler=self._handle_system_event
        )

    async def _handle_system_event(self, event: EventMessage) -> None:
        """Convert system events to workflow events when relevant."""
        if event.event_type in ["node.deregistered", "system.stopped"]:
            # Convert to workflow event for orchestration
            workflow_event = self._convert_to_workflow_event(event)
            await self.workflow_event_bus.publish_workflow_event(workflow_event)
```

### MCP Integration

```python
from omnibase_spi.protocols.mcp import ProtocolMCPRegistry

async def integrate_mcp_events(
    event_bus: ProtocolEventBus,
    mcp_registry: ProtocolMCPRegistry
) -> None:
    """Integrate MCP tool events with the event bus."""

    async def handle_mcp_events(event: EventMessage) -> None:
        """Handle MCP-related events."""
        if event.event_type == "mcp.tool_registered":
            # Notify other services of new tool availability
            await notify_tool_availability(event)
        elif event.event_type == "mcp.subsystem_registered":
            # Update service discovery with new subsystem
            await update_service_registry(event)

    await event_bus.subscribe_to_topic(
        topic="mcp_events",
        group_id="mcp_integration",
        handler=handle_mcp_events
    )
```

## Advanced Features

### Event Sourcing and Replay

```python
async def implement_event_sourcing(
    event_bus: ProtocolEventBus
) -> None:
    """Implement event sourcing pattern for audit and replay."""

    # All events are stored with sequence numbers for ordering
    async def store_event_for_sourcing(event: EventMessage) -> None:
        """Store event in event store with sequence number."""
        await event_store.append_event(
            stream_id=event.metadata.correlation_id,
            event_data=event.payload,
            event_type=event.event_type,
            metadata=event.metadata
        )

    # Subscribe to all events for event sourcing
    await event_bus.subscribe_to_topic(
        topic="all_events",
        group_id="event_sourcing",
        handler=store_event_for_sourcing
    )

async def replay_events(
    correlation_id: str,
    from_sequence: int = 0
) -> List[EventMessage]:
    """Replay events from event store for recovery or debugging."""
    stored_events = await event_store.read_stream(
        stream_id=correlation_id,
        from_sequence=from_sequence
    )

    return [reconstruct_event_message(stored_event) for stored_event in stored_events]
```

### Performance Optimization

```python
async def optimize_event_performance(
    event_bus: ProtocolEventBus
) -> None:
    """Implement performance optimizations for high-throughput scenarios."""

    # Batch publishing for high-throughput scenarios
    async def batch_publish_events(
        events: List[EventMessage],
        batch_size: int = 100
    ) -> List[bool]:
        """Publish events in batches for better performance."""
        results = []

        for i in range(0, len(events), batch_size):
            batch = events[i:i + batch_size]
            batch_results = await asyncio.gather(
                *[event_bus.publish_event(event) for event in batch],
                return_exceptions=True
            )
            results.extend(batch_results)

        return results

    # Consumer group load balancing
    async def setup_load_balanced_consumers(
        topic: str,
        handler: Callable[[EventMessage], Awaitable[None]],
        consumer_count: int = 3
    ) -> List[Callable[[], Awaitable[None]]]:
        """Set up multiple consumers for load balancing."""
        unsubscribe_functions = []

        for i in range(consumer_count):
            unsubscribe = await event_bus.subscribe_to_topic(
                topic=topic,
                group_id=f"load_balanced_group",  # Same group for load balancing
                handler=handler
            )
            unsubscribe_functions.append(unsubscribe)

        return unsubscribe_functions
```

## Error Handling and Resilience

### Retry and Dead Letter Patterns

```python
async def implement_resilient_processing(
    event_bus: ProtocolEventBus
) -> None:
    """Implement resilient event processing with retries and dead letter queues."""

    async def resilient_event_handler(event: EventMessage) -> None:
        """Event handler with retry logic and dead letter queue."""
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                await process_event(event)
                return  # Success, exit retry loop
            except RetryableError as e:
                retry_count += 1
                if retry_count < max_retries:
                    await asyncio.sleep(2 ** retry_count)  # Exponential backoff
                else:
                    # Max retries exceeded, send to dead letter queue
                    await send_to_dead_letter_queue(event, str(e))
            except NonRetryableError as e:
                # Immediate failure, send to dead letter queue
                await send_to_dead_letter_queue(event, str(e))
                return

    await event_bus.subscribe_to_topic(
        topic="critical_events",
        group_id="resilient_processor",
        handler=resilient_event_handler
    )

async def send_to_dead_letter_queue(
    event: EventMessage,
    error_message: str
) -> None:
    """Send failed event to dead letter queue for manual investigation."""
    dead_letter_event = EventMessage(
        event_id=str(uuid4()),
        event_type="system.dead_letter",
        payload={
            "original_event": event.payload,
            "error_message": error_message,
            "failed_at": datetime.utcnow().isoformat()
        },
        metadata=EventMetadata(
            source="error_handler",
            correlation_id=event.metadata.correlation_id,
            causation_id=event.event_id
        ),
        timestamp=datetime.utcnow().isoformat()
    )

    await event_bus.publish_event(dead_letter_event, target_topic="dead_letter_queue")
```

## Testing Strategies

### Protocol Compliance Testing

```python
from omnibase_spi.protocols.event_bus import ProtocolEventBus

class TestEventBusCompliance:
    """Test suite for event bus protocol compliance."""

    @pytest.fixture
    def event_bus(self) -> ProtocolEventBus:
        """Provide event bus implementation for testing."""
        return MockEventBusImplementation()

    async def test_publish_event_success(self, event_bus: ProtocolEventBus):
        """Test successful event publishing."""
        event = create_test_event()
        result = await event_bus.publish_event(event)
        assert result is True

    async def test_subscription_and_delivery(self, event_bus: ProtocolEventBus):
        """Test event subscription and message delivery."""
        received_events = []

        async def test_handler(event: EventMessage) -> None:
            received_events.append(event)

        unsubscribe = await event_bus.subscribe_to_topic(
            topic="test_topic",
            group_id="test_group",
            handler=test_handler
        )

        # Publish test event
        test_event = create_test_event()
        await event_bus.publish_event(test_event, target_topic="test_topic")

        # Wait for delivery
        await asyncio.sleep(0.1)

        assert len(received_events) == 1
        assert received_events[0].event_id == test_event.event_id

        await unsubscribe()
```

## Configuration and Deployment

### Environment Configuration

```python
@dataclass
class EventBusConfiguration:
    """Configuration for event bus deployment."""

    # Backend configuration
    backend_type: Literal["kafka", "redpanda"] = "kafka"
    broker_urls: List[str] = field(default_factory=lambda: ["localhost:9092"])

    # Environment settings
    environment: str = "dev"
    topic_prefix: str = "onex"

    # Performance settings
    batch_size: int = 100
    max_poll_records: int = 500
    session_timeout_ms: int = 30000

    # Security settings
    security_protocol: str = "PLAINTEXT"
    sasl_mechanism: Optional[str] = None

    # Monitoring settings
    enable_metrics: bool = True
    metrics_port: int = 8081

async def create_event_bus_from_config(
    config: EventBusConfiguration
) -> ProtocolEventBus:
    """Create event bus implementation from configuration."""
    if config.backend_type == "kafka":
        return KafkaEventBusImplementation(
            broker_urls=config.broker_urls,
            environment=config.environment,
            # ... other config
        )
    elif config.backend_type == "redpanda":
        return RedpandaEventBusImplementation(
            broker_urls=config.broker_urls,
            environment=config.environment,
            # ... other config
        )
```

## Best Practices

### Protocol Implementation Guidelines

1. **Environment Isolation**: Always include environment metadata in events
2. **Correlation Tracking**: Use correlation IDs for request tracing
3. **Event Versioning**: Include schema version in event metadata
4. **Security Context**: Always validate security context before processing
5. **Error Handling**: Implement comprehensive retry and dead letter patterns
6. **Performance**: Use batching for high-throughput scenarios
7. **Monitoring**: Include OpenTelemetry tracing in all operations

### Type Safety

1. **Strong Typing**: Use specific event types rather than generic messages
2. **Protocol Compliance**: Always use `@runtime_checkable` protocols
3. **Validation**: Validate event structure before processing
4. **Type Hints**: Include comprehensive type hints in all implementations

The event bus protocols provide a robust foundation for distributed messaging in the ONEX ecosystem, supporting complex event-driven architectures while maintaining type safety and architectural purity.
