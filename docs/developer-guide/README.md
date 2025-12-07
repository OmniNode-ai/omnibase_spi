# Developer Guide

## Overview

Complete development workflow and best practices for working with ONEX SPI protocols.

## Development Setup

### Prerequisites

- Python 3.11, 3.12, or 3.13
- Poetry for dependency management
- Git for version control

### Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd omnibase-spi

# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Run validation
poetry run pytest && poetry build
```

## Development Workflow

### Protocol Development

1. **Create Protocol Files** - Define new protocols in appropriate domain directories
2. **Follow Naming Conventions** - Use `Protocol*` prefix for all protocols
3. **Add Type Hints** - Ensure all methods have proper type annotations
4. **Document Protocols** - Include comprehensive docstrings

### Validation Requirements

```bash
# Type safety validation
poetry run mypy src/ --strict --no-any-expr

# Protocol compliance checking
poetry run python scripts/ast_spi_validator.py --check-protocols

# Namespace isolation testing
./scripts/validate-namespace-isolation.sh
```

### Testing Standards

- **Protocol Compliance** - All protocols must be `@runtime_checkable`
- **Type Safety** - Full mypy compatibility with strict checking
- **Namespace Isolation** - Complete separation from implementation packages
- **Zero Dependencies** - No runtime implementation dependencies

## Best Practices

### Protocol Design

- Use `typing.Protocol` for all interfaces
- Include `@runtime_checkable` decorator
- Provide comprehensive docstrings
- Use type hints for all parameters and return values

### Error Handling

- Define specific exception types
- Provide clear error messages
- Include context information
- Follow consistent error patterns

### Performance

- Use async/await patterns
- Implement efficient data structures
- Consider memory usage
- Optimize for common use cases

## Framework Integration Patterns

This section covers integration patterns for incorporating ONEX SPI protocols into your applications.

### Dependency Injection Integration

#### Service Registration

```python
from omnibase_spi.protocols.container import ProtocolServiceRegistry

# Initialize service registry
registry: ProtocolServiceRegistry = get_service_registry()

# Register services with lifecycle management
await registry.register_service(
    interface=ProtocolLogger,
    implementation=ConsoleLogger,
    lifecycle="singleton",
    scope="global"
)

await registry.register_service(
    interface=ProtocolHttpClient,
    implementation=AsyncHttpClient,
    lifecycle="transient",
    scope="request"
)
```

#### Service Resolution

```python
# Resolve services
logger = await registry.resolve_service(ProtocolLogger)
http_client = await registry.resolve_service(ProtocolHttpClient)

# Resolve with context
context = {"user_id": "12345", "request_id": "req-abc123"}
scoped_service = await registry.resolve_service(
    ProtocolUserService,
    scope="request",
    context=context
)
```

### Event-Driven Architecture Integration

#### Workflow Orchestration

```python
from omnibase_spi.protocols.workflow_orchestration import ProtocolWorkflowOrchestrator

# Initialize orchestrator
orchestrator: ProtocolWorkflowOrchestrator = get_workflow_orchestrator()

# Start workflow
workflow = await orchestrator.start_workflow(
    workflow_type="order-processing",
    instance_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
    initial_data={"order_id": "ORD-12345"}
)

# Monitor workflow state
state = await orchestrator.get_workflow_state(
    "order-processing",
    UUID("123e4567-e89b-12d3-a456-426614174000")
)
```

#### Event Bus Integration

The event bus follows a layered architecture with Core interfaces, SPI providers, and Infra implementations.

```python
from omnibase_spi.protocols.event_bus import (
    ProtocolEventBusProvider,
    ProtocolEventBusContextManager,
)
from omnibase_spi.protocols.types.protocol_event_bus_types import ProtocolEventMessage

# Option 1: Provider pattern (recommended for production)
provider: ProtocolEventBusProvider = get_event_bus_provider()
event_bus = await provider.get_event_bus(environment="prod", group="order-service")

# Publish events
await event_bus.publish(
    topic="user-events",
    key=b"user-12345",
    value=b'{"action": "user_created", "user_id": "12345"}',
    headers={"event_type": "user_created", "correlation_id": str(uuid4())}
)

# Option 2: Context manager pattern (recommended for scoped operations)
context_manager: ProtocolEventBusContextManager = get_event_bus_context_manager()

async with context_manager as event_bus:
    # Connection established on enter
    await event_bus.publish(
        topic="order-events",
        key=None,
        value=b'{"order_id": "ORD-123"}',
        headers={"event_type": "order_created"}
    )
    # Cleanup handled on exit (even if exception occurs)
```

#### Event Bus Provider Implementation

When implementing a custom event bus provider:

```python
from omnibase_spi.protocols.event_bus import ProtocolEventBusProvider
from omnibase_core.protocols.event_bus import ProtocolEventBus

class KafkaEventBusProvider:
    """Kafka implementation of the event bus provider."""

    def __init__(self, bootstrap_servers: list[str]):
        self._servers = bootstrap_servers
        self._instances: dict[str, ProtocolEventBus] = {}
        self._default_env = "local"
        self._default_group = "default"

    async def get_event_bus(
        self,
        environment: str | None = None,
        group: str | None = None,
    ) -> ProtocolEventBus:
        env = environment or self._default_env
        grp = group or self._default_group
        key = f"{env}:{grp}"

        if key not in self._instances:
            self._instances[key] = await self.create_event_bus(env, grp)
        return self._instances[key]

    async def create_event_bus(
        self,
        environment: str,
        group: str,
        config: dict[str, object] | None = None,
    ) -> ProtocolEventBus:
        # Create new Kafka client with configuration
        return KafkaEventBus(
            bootstrap_servers=self._servers,
            group_id=group,
            environment=environment,
            **(config or {})
        )

    async def close_all(self) -> None:
        for bus in self._instances.values():
            await bus.close()
        self._instances.clear()

    @property
    def default_environment(self) -> str:
        return self._default_env

    @property
    def default_group(self) -> str:
        return self._default_group

# Verify protocol compliance
provider = KafkaEventBusProvider(["kafka:9092"])
assert isinstance(provider, ProtocolEventBusProvider)
```

#### Context Manager Implementation

```python
from omnibase_spi.protocols.event_bus import ProtocolEventBusContextManager
from omnibase_core.protocols.event_bus import ProtocolEventBus

class KafkaEventBusContextManager:
    """Context manager for Kafka event bus lifecycle."""

    def __init__(self, config: dict[str, str]):
        self._config = config
        self._event_bus: ProtocolEventBus | None = None

    async def __aenter__(self) -> ProtocolEventBus:
        # Initialize and connect
        self._event_bus = KafkaEventBus(
            bootstrap_servers=self._config["bootstrap_servers"].split(","),
            group_id=self._config.get("group_id", "default"),
        )
        await self._event_bus.connect()
        return self._event_bus

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        # Cleanup on exit
        if self._event_bus:
            await self._event_bus.close()
            self._event_bus = None

# Verify protocol compliance
cm = KafkaEventBusContextManager({"bootstrap_servers": "kafka:9092"})
assert isinstance(cm, ProtocolEventBusContextManager)
```

#### Event Envelope Pattern

Use the envelope protocol to break circular dependencies:

```python
from omnibase_spi.protocols.event_bus import ProtocolEventEnvelope
from typing import Generic, TypeVar

T = TypeVar("T")

class EventEnvelope(Generic[T]):
    """Envelope implementation for event payloads."""

    def __init__(self, payload: T, metadata: dict[str, str]):
        self._payload = payload
        self._metadata = metadata

    async def get_payload(self) -> T:
        return self._payload

# Handler that works with any envelope type
async def process_envelope(
    envelope: ProtocolEventEnvelope[UserCreatedPayload]
) -> None:
    payload = await envelope.get_payload()
    print(f"Processing user: {payload.user_id}")

# Verify protocol compliance
envelope = EventEnvelope(user_payload, {"correlation_id": "abc"})
assert isinstance(envelope, ProtocolEventEnvelope)
```

### MCP Integration

#### Tool Registration and Execution

```python
from omnibase_spi.protocols.mcp import ProtocolMCPRegistry

# Initialize MCP registry
mcp_registry: ProtocolMCPRegistry = get_mcp_registry()

# Register subsystem
registration_id = await mcp_registry.register_subsystem(
    subsystem_metadata=ProtocolMCPSubsystemMetadata(
        subsystem_id="llm-subsystem-1",
        subsystem_type="llm",
        host="192.168.1.100",
        port=8080
    ),
    tools=[
        ProtocolMCPToolDefinition(
            tool_name="text_generation",
            tool_type="function",
            description="Generate text using LLM"
        )
    ],
    api_key="mcp-api-key-12345"
)

# Execute tool
result = await mcp_registry.execute_tool(
    tool_name="text_generation",
    parameters={"prompt": "Hello world"},
    correlation_id=UUID("req-abc123")
)
```

### Memory Management Integration

#### Memory Operations

```python
from omnibase_spi.protocols.memory import ProtocolMemoryBase

# Initialize memory
memory: ProtocolMemoryBase = get_memory()

# Store data
await memory.store(
    key="user:12345",
    value={"name": "John Doe", "email": "john@example.com"},
    ttl_seconds=3600
)

# Retrieve data
user_data = await memory.retrieve("user:12345")
```

### Validation Integration

#### Input Validation

```python
from omnibase_spi.protocols.validation import ProtocolValidation

# Initialize validator
validator: ProtocolValidation = get_validator()

# Validate data
validation_result = await validator.validate_data(
    data={"name": "John Doe", "age": 30},
    validation_schema=ProtocolValidationSchema(
        type="object",
        properties={
            "name": {"type": "string", "minLength": 1},
            "age": {"type": "integer", "minimum": 0, "maximum": 120}
        },
        required=["name", "age"]
    )
)
```

## Integration Best Practices

### Protocol Compliance

- Use `isinstance(obj, Protocol)` for runtime validation
- Implement all required protocol methods
- Follow type hints and return types
- Handle errors appropriately

### Performance Optimization

- Use async/await patterns consistently
- Implement connection pooling
- Cache frequently accessed data
- Monitor and profile performance

### Error Handling

- Define specific exception types
- Provide clear error messages
- Include context information
- Implement retry mechanisms

#### Event Bus Error Handling

The event bus provides comprehensive error handling through the DLQ (Dead Letter Queue) protocol:

```python
from omnibase_spi.protocols.event_bus import ProtocolDLQHandler

# Get DLQ handler
dlq_handler: ProtocolDLQHandler = get_dlq_handler()

async def process_event_with_error_handling(
    message: ProtocolEventMessage
) -> None:
    try:
        # Process the event
        await process_business_logic(message)
        await message.ack()

    except ValidationError as e:
        # Non-retryable error - send directly to DLQ
        await dlq_handler.handle_failed_message(
            message=message,
            error=e,
            retry_count=0,  # Skip retries
        )

    except TransientError as e:
        # Retryable error - handle with retry logic
        result = await dlq_handler.handle_failed_message(
            message=message,
            error=e,
            retry_count=message.retry_count or 0,
        )

        if result.retry_eligible:
            # Will be retried automatically
            await message.nack(requeue=True)
        else:
            # Max retries exceeded, sent to DLQ
            await message.ack()

# Analyze failure patterns for monitoring
failure_analysis = await dlq_handler.analyze_failure_patterns(
    topic="order-events",
    time_range_hours=24
)
print(f"Top failure reason: {failure_analysis.top_failure_reason}")
print(f"Failure rate: {failure_analysis.failure_rate}%")
```

#### Retry with Exponential Backoff

```python
from omnibase_spi.protocols.event_bus import ProtocolEventPublisher

publisher: ProtocolEventPublisher = get_event_publisher()

# Publish with automatic retry and exponential backoff
success = await publisher.publish_with_retry(
    topic="critical-events",
    message=critical_message,
    max_retries=5,
    backoff_ms=1000,  # Initial backoff, doubles each retry
)

if not success:
    # All retries exhausted, handle failure
    await handle_publish_failure(critical_message)
```

## API Reference

- **[Core Protocols](../api-reference/CORE.md)** - System fundamentals
- **[Container Protocols](../api-reference/CONTAINER.md)** - Dependency injection
- **[Workflow Orchestration](../api-reference/WORKFLOW-ORCHESTRATION.md)** - Event-driven FSM
- **[MCP Integration](../api-reference/MCP.md)** - Multi-subsystem coordination
- **[Event Bus](../api-reference/EVENT-BUS.md)** - Distributed messaging
- **[Memory Management](../api-reference/MEMORY.md)** - Memory operations

## See Also

- **[Glossary](../GLOSSARY.md)** - Definitions of SPI-specific terms (Protocol, Handler, Node, Contract, etc.)
- **[Quick Start Guide](../QUICK-START.md)** - Get up and running quickly
- **[Architecture Overview](../architecture/README.md)** - Design principles and patterns
- **[Contributing Guide](../CONTRIBUTING.md)** - How to contribute to the project
- **[MVP Plan](../MVP_PLAN.md)** - v0.3.0 work breakdown and roadmap
- **[Main README](../../README.md)** - Repository overview

### v0.3.0 Core Protocols

- **[Node Protocols](../api-reference/NODES.md)** - ONEX 4-node architecture
- **[Handler Protocols](../api-reference/HANDLERS.md)** - I/O handler interfaces
- **[Contract Compilers](../api-reference/CONTRACTS.md)** - Contract compilation
- **[Registry Protocols](../api-reference/REGISTRY.md)** - Handler registry
- **[Exception Hierarchy](../api-reference/EXCEPTIONS.md)** - Error handling

For term definitions, see the [Glossary](../GLOSSARY.md).

---

*For detailed protocol documentation, see the [API Reference](../api-reference/README.md).*
