# Architecture Overview

## Design Principles

The ONEX SPI follows a **protocol-first design** with enterprise-grade features:

### Core Principles

1. **Protocol-First Design** - All services defined through Python `Protocol` interfaces
2. **Namespace Isolation** - Complete separation from implementation packages
3. **Zero Implementation Dependencies** - Pure protocol contracts only
4. **Runtime Type Safety** - Full `@runtime_checkable` protocol support
5. **Event Sourcing** - Sequence numbers, causation tracking, replay capabilities

### Protocol Architecture

**165 protocols** across **22 specialized domains**:

- **Core System** (16 protocols) - Logging, health monitoring, error handling
- **Container Management** (21 protocols) - Dependency injection, lifecycle management
- **Workflow Orchestration** (14 protocols) - Event-driven FSM coordination
- **MCP Integration** (15 protocols) - Multi-subsystem tool coordination
- **Event Bus** (13 protocols) - Distributed messaging infrastructure
- **Memory Management** (15 protocols) - Workflow state persistence
- **Networking** (6 protocols) - HTTP, Kafka, circuit breakers
- **File Handling** (8 protocols) - File processing and type detection
- **Validation** (11 protocols) - Input validation and compliance
- **Plus 13 more specialized domains**

### Key Features

#### Event-Driven Workflow Orchestration
- **FSM States**: `pending` → `running` → `completed` with compensation actions
- **Event Sourcing**: Sequence numbers, causation tracking, replay capabilities
- **Isolation**: `{workflowType, instanceId}` pattern for workflow separation
- **Projections**: Real-time state derivation from events

#### MCP Integration
- **Tool Registry**: Dynamic discovery and load balancing across subsystems
- **Health Monitoring**: TTL-based cleanup and subsystem status tracking
- **Execution Tracking**: Correlation IDs and performance metrics
- **Multi-Subsystem Coordination**: Seamless tool routing and execution

#### Enterprise Dependency Injection
- **Lifecycle Management**: Singleton, transient, scoped, pooled patterns
- **Circular Dependency Detection**: Automatic detection and prevention
- **Health Monitoring**: Service health tracking and validation
- **Performance Metrics**: Resolution time tracking and optimization
- **Scoped Injection**: Request, session, thread-based scoping

## Protocol Compliance

All protocols are designed to be:

- **Runtime Checkable**: Use `isinstance(obj, Protocol)` for validation
- **Type Safe**: Full mypy compatibility with strict checking
- **Framework Agnostic**: No dependencies on specific implementations
- **Forward Compatible**: Extensible design for future enhancements

## SPI Purity

The API documents pure protocol definitions that:

- Contain no concrete implementations
- Use only abstract method signatures with `...`
- Employ type hints for all parameters and return values
- Follow namespace isolation rules
- Maintain zero runtime dependencies

## API Reference

- **[Core Protocols](../api-reference/CORE.md)** - System fundamentals
- **[Container Protocols](../api-reference/CONTAINER.md)** - Dependency injection
- **[Workflow Orchestration](../api-reference/WORKFLOW-ORCHESTRATION.md)** - Event-driven FSM
- **[MCP Integration](../api-reference/MCP.md)** - Multi-subsystem coordination

---

*For detailed protocol documentation, see the [API Reference](../api-reference/README.md).*
