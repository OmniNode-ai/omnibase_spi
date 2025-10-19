# Examples

## Overview

Practical examples demonstrating ONEX SPI protocol usage patterns.

> **Note**: Examples use implementation-specific factory functions like `get_service_registry()`, `get_workflow_orchestrator()`, etc. These are not part of the SPI protocols themselves but are provided by concrete implementations to demonstrate usage patterns.

## Basic Examples

### Service Registration and Resolution

```python
from omnibase_spi.protocols.container import ProtocolServiceRegistry
from omnibase_spi.protocols.core import ProtocolLogger

# Initialize service registry
# Note: get_service_registry() is an implementation-specific factory function
# that returns a concrete implementation of ProtocolServiceRegistry
registry: ProtocolServiceRegistry = get_service_registry()

# Register logger service
await registry.register_service(
    interface=ProtocolLogger,
    implementation=ConsoleLogger,
    lifecycle="singleton",
    scope="global"
)

# Resolve and use logger
logger = await registry.resolve_service(ProtocolLogger)
await logger.log("INFO", "Service registered successfully")
```

### Workflow Orchestration

```python
from omnibase_spi.protocols.workflow_orchestration import ProtocolWorkflowOrchestrator

# Initialize orchestrator
orchestrator: ProtocolWorkflowOrchestrator = get_workflow_orchestrator()

# Start workflow
workflow = await orchestrator.start_workflow(
    workflow_type="order-processing",
    instance_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
    initial_data={"order_id": "ORD-12345", "amount": 99.99}
)

# Monitor workflow state
state = await orchestrator.get_workflow_state(
    "order-processing",
    UUID("123e4567-e89b-12d3-a456-426614174000")
)
print(f"Workflow state: {state.current_state}")
```

### Event Bus Integration

```python
from omnibase_spi.protocols.event_bus import ProtocolEventBus

# Initialize event bus
event_bus: ProtocolEventBus = get_event_bus()

# Subscribe to events
subscription_id = await event_bus.subscribe_to_topic(
    topic="user-events",
    handler=user_event_handler
)

# Publish event
await event_bus.publish_event(
    topic="user-events",
    message=ProtocolEventMessage(
        topic="user-events",
        value=b'{"action": "user_created", "user_id": "12345"}',
        headers={"event_type": "user_created"}
    )
)

async def user_event_handler(message: ProtocolEventMessage, context: dict[str, ContextValue]):
    """Handle user events."""
    print(f"Received event: {message.value}")
```

## Advanced Examples

### MCP Integration

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
print(f"Tool result: {result}")
```

### Memory Operations

```python
from omnibase_spi.protocols.memory import ProtocolMemoryBase

# Initialize memory
memory: ProtocolMemoryBase = get_memory()

# Store data with TTL
await memory.store(
    key="user:12345",
    value={"name": "John Doe", "email": "john@example.com"},
    ttl_seconds=3600
)

# Retrieve data
user_data = await memory.retrieve("user:12345")
print(f"User data: {user_data}")

# Check existence
if await memory.exists("user:12345"):
    print("User exists")
```

### Validation

```python
from omnibase_spi.protocols.validation import ProtocolValidation

# Initialize validator
validator: ProtocolValidation = get_validator()

# Validate data
validation_result = await validator.validate_data(
    data={"name": "John Doe", "age": 30, "email": "john@example.com"},
    validation_schema=ProtocolValidationSchema(
        type="object",
        properties={
            "name": {"type": "string", "minLength": 1},
            "age": {"type": "integer", "minimum": 0, "maximum": 120},
            "email": {"type": "string", "format": "email"}
        },
        required=["name", "age", "email"]
    )
)

if validation_result.valid:
    print("Data is valid")
else:
    print(f"Validation errors: {validation_result.errors}")
```

## Integration Examples

### Complete Service Integration

```python
from omnibase_spi.protocols.container import ProtocolServiceRegistry
from omnibase_spi.protocols.workflow_orchestration import ProtocolWorkflowOrchestrator
from omnibase_spi.protocols.event_bus import ProtocolEventBus
from omnibase_spi.protocols.memory import ProtocolMemoryBase

class OrderProcessingService:
    """Complete order processing service."""

    def __init__(
        self,
        registry: ProtocolServiceRegistry,
        orchestrator: ProtocolWorkflowOrchestrator,
        event_bus: ProtocolEventBus,
        memory: ProtocolMemoryBase
    ):
        self.registry = registry
        self.orchestrator = orchestrator
        self.event_bus = event_bus
        self.memory = memory

    async def process_order(self, order_data: dict[str, ContextValue]) -> str:
        """Process order with full integration."""
        # Start workflow
        workflow = await self.orchestrator.start_workflow(
            workflow_type="order-processing",
            instance_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
            initial_data=order_data
        )

        # Store order data
        await self.memory.store(
            key=f"order:{workflow.instance_id}",
            value=order_data,
            ttl_seconds=86400
        )

        # Publish event
        await self.event_bus.publish_event(
            topic="order-events",
            message=ProtocolEventMessage(
                topic="order-events",
                value=json.dumps(order_data).encode(),
                headers={"event_type": "order_created"}
            )
        )

        return str(workflow.instance_id)

# Initialize service
service = OrderProcessingService(
    registry=await get_service_registry(),
    orchestrator=await get_workflow_orchestrator(),
    event_bus=await get_event_bus(),
    memory=await get_memory()
)

# Process order
order_id = await service.process_order({
    "order_id": "ORD-12345",
    "amount": 99.99,
    "customer_id": "12345"
})
print(f"Order processed: {order_id}")
```

### Health Monitoring Integration

```python
from omnibase_spi.protocols.core import ProtocolHealthMonitor
from omnibase_spi.protocols.container import ProtocolServiceRegistry

class HealthAwareService:
    """Service with health monitoring."""

    def __init__(
        self,
        health_monitor: ProtocolHealthMonitor,
        registry: ProtocolServiceRegistry
    ):
        self.health_monitor = health_monitor
        self.registry = registry

    async def perform_operation(self, data: ContextValue) -> ContextValue:
        """Perform operation with health checking."""
        # Check service health
        health_status = await self.health_monitor.get_current_health_status()
        if health_status != "healthy":
            raise ServiceUnavailableError("Service unhealthy")

        # Perform operation
        result = await self._execute_operation(data)

        # Record health metrics
        await self.health_monitor.record_health_metric(
            metric_name="operation_success",
            value=1.0,
            tags={"service": "health_aware_service"}
        )

        return result

    async def _execute_operation(self, data: ContextValue) -> ContextValue:
        """Execute the actual operation."""
        # Implementation here
        return data

# Initialize service
service = HealthAwareService(
    health_monitor=await get_health_monitor(),
    registry=await get_service_registry()
)

# Use service
result = await service.perform_operation({"test": "data"})
print(f"Operation result: {result}")
```

## Best Practices

### Error Handling

```python
try:
    result = await service.perform_operation(data)
    return result
except ServiceUnavailableError as e:
    logger.error(f"Service unavailable: {e}")
    raise
except ValidationError as e:
    logger.error(f"Validation failed: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise
```

### Performance Optimization

```python
# Use async/await patterns
async def process_data(data: list[ContextValue]) -> list[ContextValue]:
    """Process data efficiently."""
    tasks = []
    for item in data:
        task = asyncio.create_task(process_item(item))
        tasks.append(task)

    results = await asyncio.gather(*tasks)
    return results
```

### Monitoring and Logging

```python
# Include comprehensive logging
async def process_workflow(workflow_data: dict[str, ContextValue]) -> str:
    """Process workflow with monitoring."""
    logger.info(f"Starting workflow: {workflow_data}")

    try:
        result = await orchestrator.start_workflow(
            workflow_type="data-processing",
            instance_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
            initial_data=workflow_data
        )

        logger.info(f"Workflow started: {result.instance_id}")
        return str(result.instance_id)

    except Exception as e:
        logger.error(f"Workflow failed: {e}")
        raise
```

## API Reference

- **[Core Protocols](api-reference/core.md)** - System fundamentals
- **[Container Protocols](api-reference/container.md)** - Dependency injection
- **[Workflow Orchestration](api-reference/workflow-orchestration.md)** - Event-driven FSM
- **[MCP Integration](api-reference/mcp.md)** - Multi-subsystem coordination
- **[Event Bus](api-reference/event-bus.md)** - Distributed messaging
- **[Memory Management](api-reference/memory.md)** - Memory operations

---

*For detailed protocol documentation, see the [API Reference](api-reference/README.md).*
