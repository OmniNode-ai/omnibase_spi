# Protocol Patterns: Handler vs Event Bus

This document explains when to use `ProtocolHandler` versus `ProtocolEventBus` patterns in the ONEX SPI.

## Overview

The ONEX platform provides two distinct communication patterns for external interactions:

| Pattern | Purpose | Communication Style |
|---------|---------|---------------------|
| **ProtocolHandler** | Request-response I/O operations | Synchronous, direct response expected |
| **ProtocolEventBus** | Async message passing and pub/sub | Fire-and-forget, decoupled |

### ProtocolHandler

Request-response pattern for direct I/O operations where a response is expected. Used within effect nodes to perform external calls like HTTP requests, database queries, or protocol-specific operations.

**Key Characteristics:**
- Synchronous request-response semantics
- Connection pooling and resource management
- Health checks and retry handling
- Tight request-response coupling

### ProtocolEventBus

Asynchronous publish-subscribe pattern for decoupled inter-service communication. Used for event-driven architectures, event sourcing, and workflows where services communicate without direct coupling.

**Key Characteristics:**
- Fire-and-forget publishing
- Multiple subscribers per topic
- Correlation ID propagation for distributed tracing
- Dead letter queue (DLQ) support for failed messages

## Comparison Table

| Aspect | ProtocolHandler | ProtocolEventBus |
|--------|-----------------|------------------|
| **Use Case** | HTTP/REST, DB queries, API calls | Event sourcing, inter-service messaging |
| **Communication** | Request-response | Publish-subscribe |
| **Coupling** | Direct (caller waits for response) | Decoupled (fire-and-forget) |
| **Response** | Immediate, structured response | No direct response expected |
| **Failure Handling** | Retries, circuit breakers | DLQ routing, reprocessing |
| **Scalability** | Connection pooling | Topic partitioning |
| **Tracing** | Request/response correlation | Envelope correlation IDs |
| **Examples** | `HttpRestHandler`, `PostgresHandler` | `KafkaAdapter`, `RedpandaAdapter` |

## When to Use Each Pattern

### Use ProtocolHandler When:

1. **Direct Response Required** - You need an immediate response from an external system
2. **Synchronous Workflow** - The calling code must wait for the result before continuing
3. **Connection Pooling** - Managing persistent connections to databases or services
4. **Protocol Translation** - Converting between internal models and external protocols
5. **Health Monitoring** - Need real-time health status of external dependencies

**Typical scenarios:**
- REST API calls to external services
- Database CRUD operations
- GraphQL queries
- Cache operations (Redis, Memcached)
- File storage operations (S3, GCS)

### Use ProtocolEventBus When:

1. **Decoupled Services** - Services should not depend on each other's availability
2. **Event Sourcing** - Recording domain events for audit/replay
3. **Async Workflows** - Long-running processes that don't need immediate response
4. **Fan-out Patterns** - One event triggers multiple downstream processes
5. **Cross-Service Communication** - Inter-service messaging in microservices

**Typical scenarios:**
- Domain event publishing (e.g., "OrderCreated", "UserRegistered")
- Audit logging
- Analytics event streaming
- Workflow orchestration
- Change data capture (CDC)

## Code Examples

### ProtocolHandler Example

```python
from typing import Protocol, runtime_checkable
from omnibase_core.models.protocol import (
    ModelConnectionConfig,
    ModelOperationConfig,
    ModelProtocolRequest,
    ModelProtocolResponse,
)

@runtime_checkable
class ProtocolHandler(Protocol):
    """Request-response handler for external I/O."""

    async def initialize(self, config: ModelConnectionConfig) -> None:
        """Initialize connection pool and resources."""
        ...

    async def execute(
        self,
        request: ModelProtocolRequest,
        operation_config: ModelOperationConfig,
    ) -> ModelProtocolResponse:
        """Execute operation and return response."""
        ...

    async def shutdown(self, timeout_seconds: float = 30.0) -> None:
        """Release resources gracefully."""
        ...

    async def health_check(self) -> dict[str, Any]:
        """Check connectivity and health status."""
        ...


# Usage in an effect node
class UserServiceEffectNode:
    def __init__(self, http_handler: ProtocolHandler):
        self._handler = http_handler

    async def fetch_user(self, user_id: str) -> User:
        request = ModelProtocolRequest(
            method="GET",
            path=f"/users/{user_id}",
        )
        response = await self._handler.execute(request, self._config)
        return User.model_validate(response.data)
```

### ProtocolEventBus Example

```python
from typing import Awaitable, Callable, Protocol, runtime_checkable
from omnibase_core.models.runtime import ModelOnexEnvelope

@runtime_checkable
class ProtocolEventBusBase(Protocol):
    """Pub/sub event bus for async messaging."""

    async def publish_envelope(
        self,
        envelope: ModelOnexEnvelope,
        topic: str,
    ) -> None:
        """Publish envelope to topic (fire-and-forget)."""
        ...

    async def subscribe(
        self,
        topic: str,
        handler: Callable[[ModelOnexEnvelope], Awaitable[None]],
    ) -> None:
        """Subscribe to topic with handler callback."""
        ...

    async def start_consuming(self) -> None:
        """Start consuming from subscribed topics."""
        ...

    async def health_check(self) -> bool:
        """Check broker connectivity."""
        ...


# Usage for event publishing
class OrderService:
    def __init__(self, event_bus: ProtocolEventBusBase):
        self._bus = event_bus

    async def create_order(self, order: Order) -> None:
        # Save order to database
        await self._repository.save(order)

        # Publish event (fire-and-forget)
        envelope = ModelOnexEnvelope(
            event_type="omninode.orders.event.order_created.v1",
            payload=order.model_dump(),
            correlation_id=str(uuid4()),
        )
        await self._bus.publish_envelope(envelope, "orders.events")


# Usage for event consumption
class InventoryService:
    def __init__(self, event_bus: ProtocolEventBusBase):
        self._bus = event_bus

    async def start(self) -> None:
        await self._bus.subscribe("orders.events", self._handle_order_event)
        await self._bus.start_consuming()

    async def _handle_order_event(self, envelope: ModelOnexEnvelope) -> None:
        if envelope.event_type == "omninode.orders.event.order_created.v1":
            await self._reserve_inventory(envelope.payload)
```

### Combined Usage Pattern

Many systems use both patterns together:

```python
class PaymentService:
    """Uses both handler (for payment gateway) and event bus (for notifications)."""

    def __init__(
        self,
        payment_handler: ProtocolHandler,  # Direct calls to payment gateway
        event_bus: ProtocolEventBusBase,   # Publish payment events
    ):
        self._handler = payment_handler
        self._bus = event_bus

    async def process_payment(self, payment: Payment) -> PaymentResult:
        # 1. Call payment gateway via handler (need response)
        request = ModelProtocolRequest(
            method="POST",
            path="/charges",
            data=payment.model_dump(),
        )
        response = await self._handler.execute(request, self._config)
        result = PaymentResult.model_validate(response.data)

        # 2. Publish event via event bus (notify other services)
        envelope = ModelOnexEnvelope(
            event_type="omninode.payments.event.payment_processed.v1",
            payload={"payment_id": payment.id, "status": result.status},
            correlation_id=payment.correlation_id,
        )
        await self._bus.publish_envelope(envelope, "payments.events")

        return result
```

## Cross-References

### ProtocolHandler

- **Definition**: [`handlers/protocol_handler.py`](handlers/protocol_handler.py)
- **Exports**: [`handlers/__init__.py`](handlers/__init__.py)

### ProtocolEventBus

- **Base Protocol**: [`event_bus/protocol_event_bus_mixin.py`](event_bus/protocol_event_bus_mixin.py)
- **Event Publisher**: [`event_bus/protocol_event_publisher.py`](event_bus/protocol_event_publisher.py)
- **DLQ Handler**: [`event_bus/protocol_dlq_handler.py`](event_bus/protocol_dlq_handler.py)
- **Kafka Adapter**: [`event_bus/protocol_kafka_adapter.py`](event_bus/protocol_kafka_adapter.py)
- **Redpanda Adapter**: [`event_bus/protocol_redpanda_adapter.py`](event_bus/protocol_redpanda_adapter.py)
- **Schema Registry**: [`event_bus/protocol_schema_registry.py`](event_bus/protocol_schema_registry.py)
- **Exports**: [`event_bus/__init__.py`](event_bus/__init__.py)

### Related Protocols

| Protocol | Location | Purpose |
|----------|----------|---------|
| `ProtocolEventEnvelope` | `event_bus/` | Envelope wrapper for events |
| `ProtocolEventBusProvider` | `event_bus/` | Factory for event bus instances |
| `ProtocolDLQHandler` | `event_bus/` | Dead letter queue management |
| `ProtocolSchemaRegistry` | `event_bus/` | Schema validation for events |

## Decision Flowchart

```
Need external communication?
          |
          v
    Need response? ----YES----> Use ProtocolHandler
          |
          NO
          |
          v
    Fire-and-forget? --YES----> Use ProtocolEventBus
          |
          NO
          |
          v
    Use both patterns
```

## Summary

- **ProtocolHandler**: Use for direct, request-response I/O where you need a result
- **ProtocolEventBus**: Use for decoupled, async messaging where services should not block
- **Combined**: Many real-world systems use both - handlers for external APIs, event bus for internal coordination
