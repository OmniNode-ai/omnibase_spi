# ONEX Service Provider Interface (omnibase-spi)

Pure protocol interface repository defining service contracts for the ONEX distributed orchestration framework. Maintains strict architectural purity with zero implementation dependencies.

## Architecture

**165 protocols** across **22 specialized domains** providing:

- **Event-Driven Workflow Orchestration** - FSM states, event sourcing, workflow isolation
- **MCP Integration** - Multi-subsystem tool coordination, load balancing, health monitoring  
- **Enterprise Dependency Injection** - Service registry, lifecycle management, circular dependency detection
- **Distributed Messaging** - Event bus, Kafka integration, dead letter queue handling
- **Memory Management** - Workflow state persistence, agent coordination, security

## Core Principles

1. **Protocol-First Design** - All services defined through Python `Protocol` interfaces
2. **Namespace Isolation** - Complete separation from implementation packages
3. **Zero Implementation Dependencies** - Pure contracts only
4. **Runtime Type Safety** - Full `@runtime_checkable` protocol support
5. **Event Sourcing** - Sequence numbers, causation tracking, replay capabilities

## Protocol Domains

### Core System (16 protocols)
- Logging, health monitoring, error handling
- Service discovery, performance metrics
- Serialization, URI parsing, version management

### Container Management (21 protocols)
- Service registry with lifecycle management
- Circular dependency detection
- Health monitoring and metrics collection
- Factory patterns and injection contexts

### Workflow Orchestration (14 protocols)
- Event sourcing with sequence numbers
- Workflow state management and projections
- Task scheduling and node coordination
- Distributed workflow execution

### MCP Integration (15 protocols)
- Multi-subsystem tool registration
- Load balancing and failover
- Health monitoring and metrics
- Tool execution tracking

### Event Bus (13 protocols)
- Pluggable backend adapters (Kafka, Redis, in-memory)
- Async and sync event bus implementations
- Event message serialization and routing
- Dead letter queue handling

### Memory Management (15 protocols)
- Key-value store operations
- Workflow state persistence
- Memory security and streaming
- Agent coordination and management

### Plus 16 More Specialized Domains
- **Networking** (6 protocols) - HTTP, Kafka, circuit breakers
- **File Handling** (8 protocols) - File processing, type detection
- **Advanced** (14 protocols) - Adaptive chunking, AST building, contract analysis
- **Analytics, CLI, Discovery, LLM, Node, ONEX, Schema, Semantic, Storage, Test, Types, Validation**

## Key Features

### Event-Driven Workflow Orchestration
- **FSM States**: `pending` → `running` → `completed` with compensation actions
- **Event Sourcing**: Sequence numbers, causation tracking, replay capabilities
- **Isolation**: `{workflowType, instanceId}` pattern for workflow separation
- **Projections**: Real-time state derivation from events

### MCP Integration
- **Tool Registry**: Dynamic discovery and load balancing across subsystems
- **Health Monitoring**: TTL-based cleanup and subsystem status tracking
- **Execution Tracking**: Correlation IDs and performance metrics
- **Multi-Subsystem Coordination**: Seamless tool routing and execution

### Enterprise Dependency Injection
- **Lifecycle Management**: Singleton, transient, scoped, pooled patterns
- **Circular Dependency Detection**: Automatic detection and prevention
- **Health Monitoring**: Service health tracking and validation
- **Performance Metrics**: Resolution time tracking and optimization
- **Scoped Injection**: Request, session, thread-based scoping

## Development Workflow

### Protocol Compliance
- **Runtime Checkable**: Use `isinstance(obj, Protocol)` for validation
- **Type Safe**: Full mypy compatibility with strict checking
- **Framework Agnostic**: No dependencies on specific implementations
- **Forward Compatible**: Extensible design for future enhancements

### SPI Purity
- Contain no concrete implementations
- Use only abstract method signatures with `...`
- Employ type hints for all parameters and return values
- Follow namespace isolation rules
- Maintain zero runtime dependencies

## Validation

```bash
# Run all validation checks
poetry run pytest && poetry build

# Type safety validation
poetry run mypy src/ --strict --no-any-expr

# Protocol compliance checking
poetry run python scripts/ast_spi_validator.py --check-protocols

# Namespace isolation testing
./scripts/validate-namespace-isolation.sh
```

## Quick Start

```python
from omnibase_spi.protocols.container import ProtocolServiceRegistry
from omnibase_spi.protocols.workflow_orchestration import ProtocolWorkflowOrchestrator
from omnibase_spi.protocols.mcp import ProtocolMCPRegistry

# Service registration
registry: ProtocolServiceRegistry = get_service_registry()
await registry.register_service(
    interface=ProtocolLogger,
    implementation=ConsoleLogger,
    lifecycle="singleton",
    scope="global"
)

# Workflow orchestration
orchestrator: ProtocolWorkflowOrchestrator = get_workflow_orchestrator()
workflow = await orchestrator.start_workflow(
    workflow_type="order-processing",
    instance_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
    initial_data={"order_id": "ORD-12345"}
)

# MCP tool execution
mcp_registry: ProtocolMCPRegistry = get_mcp_registry()
result = await mcp_registry.execute_tool(
    tool_name="text_generation",
    parameters={"prompt": "Hello world"},
    correlation_id=UUID("req-abc123")
)
```

## Documentation

- **[API Reference](docs/api-reference/README.md)** - Complete protocol documentation
- **[Container Protocols](docs/api-reference/container.md)** - Dependency injection patterns
- **[Workflow Orchestration](docs/api-reference/workflow-orchestration.md)** - Event-driven FSM
- **[MCP Integration](docs/api-reference/mcp.md)** - Multi-subsystem coordination
- **[Core Protocols](docs/api-reference/core.md)** - System fundamentals

## Statistics

- **Total Protocols**: 165 protocol files
- **Domain Coverage**: 22 specialized domains
- **Type Definitions**: 13 comprehensive type modules
- **Enterprise Features**: Health monitoring, metrics, circuit breakers
- **Architecture Patterns**: Event sourcing, dependency injection, distributed coordination

## Version Information

- **Package Version**: 0.1.0
- **Python Support**: 3.11, 3.12, 3.13
- **Architecture**: Protocol-first SPI with zero runtime dependencies
- **Protocol Count**: 165 protocols across 22 domains

---

*This SPI maintains strict architectural purity through automated validation and comprehensive protocol coverage.*
