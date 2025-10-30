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

```python
from omnibase_spi.protocols.event_bus import ProtocolEventBus

# Initialize event bus
event_bus: ProtocolEventBus = get_event_bus()

# Publish events
await event_bus.publish_event(
    topic="user-events",
    message=ProtocolEventMessage(
        topic="user-events",
        value=b'{"action": "user_created", "user_id": "12345"}',
        headers={"event_type": "user_created"}
    )
)

# Subscribe to events
subscription_id = await event_bus.subscribe_to_topic(
    topic="user-events",
    handler=user_event_handler
)
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

## API Reference

- **[Core Protocols](../api-reference/CORE.md)** - System fundamentals
- **[Container Protocols](../api-reference/CONTAINER.md)** - Dependency injection
- **[Workflow Orchestration](../api-reference/WORKFLOW-ORCHESTRATION.md)** - Event-driven FSM
- **[MCP Integration](../api-reference/MCP.md)** - Multi-subsystem coordination
- **[Event Bus](../api-reference/EVENT-BUS.md)** - Distributed messaging
- **[Memory Management](../api-reference/MEMORY.md)** - Memory operations

---

*For detailed protocol documentation, see the [API Reference](../api-reference/README.md).*
