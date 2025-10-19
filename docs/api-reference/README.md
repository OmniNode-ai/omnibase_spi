# ONEX SPI API Reference

## Overview

Complete API reference documentation for all **165 protocols** across **22 specialized domains** in the omnibase-spi package. This reference provides detailed documentation for every public interface in the Service Provider Interface layer.

## 🏗️ Protocol Architecture

The ONEX SPI follows a **protocol-first design** with enterprise-grade features:

- **Zero Implementation Dependencies**: Pure protocol contracts only
- **Runtime Type Safety**: Full `@runtime_checkable` protocol support  
- **Dependency Injection**: Sophisticated service lifecycle management
- **Event-Driven Architecture**: Event sourcing and workflow orchestration
- **Multi-Subsystem Coordination**: MCP integration and distributed tooling

## 📚 Domain Organization

The API reference is organized by domain, matching the package structure:

### 🔧 Core System Protocols
- **[Core Protocols](core.md)** - System-level contracts and fundamentals (16 protocols)
- **[Container Protocols](container.md)** - Dependency injection and service management (21 protocols)
- **[Discovery Protocols](discovery.md)** - Service and handler discovery (3 protocols)

### 🚀 Workflow & Event Processing
- **[Workflow Orchestration](workflow-orchestration.md)** - Event-driven FSM orchestration (14 protocols)
- **[Event Bus](event-bus.md)** - Distributed messaging infrastructure (13 protocols)
- **[Memory Management](memory.md)** - Memory operations and workflow management (15 protocols)

### 🔗 Integration & Communication
- **[MCP Integration](mcp.md)** - Model Context Protocol coordination (15 protocols)
- **[Networking](networking.md)** - HTTP, Kafka, and communication protocols (6 protocols)
- **[File Handling](file-handling.md)** - File processing and type handling (8 protocols)

### 🛠️ Advanced & Specialized
- **[Advanced Protocols](advanced.md)** - Sophisticated system capabilities (14 protocols)
- **[Analytics](analytics.md)** - Data collection and reporting (1 protocol)
- **[CLI](cli.md)** - Command line interface operations (7 protocols)
- **[LLM](llm.md)** - Large Language Model integration (4 protocols)
- **[Node Management](node.md)** - Node configuration and registry (4 protocols)
- **[ONEX Platform](onex.md)** - Platform-specific protocols (11 protocols)
- **[Schema](schema.md)** - Schema loading and validation (10 protocols)
- **[Semantic](semantic.md)** - Advanced text processing (3 protocols)
- **[Storage](storage.md)** - Data persistence and backends (3 protocols)
- **[Test](test.md)** - Testing frameworks and utilities (3 protocols)
- **[Validation](validation.md)** - Input validation and compliance (11 protocols)

### 📋 Type System
- **[Core Types](core-types.md)** - Fundamental type definitions
- **[Container Types](container-types.md)** - Dependency injection types
- **[Event Bus Types](event-bus-types.md)** - Event messaging types
- **[MCP Types](mcp-types.md)** - Model Context Protocol types
- **[Workflow Types](workflow-types.md)** - Workflow orchestration types
- **[And 8+ more specialized type modules...](types.md)**

## 🔍 Protocol Documentation Standards

### Protocol Documentation Format

Each protocol is documented with:

```python
@runtime_checkable
class ProtocolExample(Protocol):
    """
    Brief description of the protocol's purpose.

    Detailed description covering:
    - Primary use cases and scenarios
    - Key features and capabilities
    - Integration patterns and usage
    - Implementation requirements

    Key Features:
        - **Feature 1**: Description of key feature
        - **Feature 2**: Description of another feature

    Example:
        ```python
        # Usage example
        async def example_usage(service: ProtocolExample):
            result = await service.method_name(param="value")
            return result
        ```
    """

    # Properties are documented with type annotations
    property_name: str
    """Description of the property."""

    async def method_name(
        self,
        param: str,
        optional_param: Optional[int] = None
    ) -> str:
        """
        Method description with clear purpose.

        Args:
            param: Description of required parameter
            optional_param: Description of optional parameter

        Returns:
            Description of return value

        Raises:
            ValueError: When parameter validation fails
            TimeoutError: When operation times out
        """
        ...
```

### Type Documentation Format

Type aliases and protocol classes are documented with:

```python
WorkflowState = Literal[
    "pending", "running", "completed", "failed"
]
"""
Workflow execution states.

Values:
    pending: Workflow is waiting to start
    running: Workflow is currently executing
    completed: Workflow finished successfully
    failed: Workflow encountered an error
"""
```

## 🚀 Quick Reference

### Core System Interfaces
| Protocol | Purpose | Usage |
|----------|---------|-------|
| `ProtocolLogger` | Structured logging | System-wide logging |
| `ProtocolHealthMonitor` | Health monitoring | Service health tracking |
| `ProtocolServiceRegistry` | Dependency injection | Service lifecycle management |
| `ProtocolCacheService` | Caching abstraction | Performance optimization |

### Workflow Orchestration
| Protocol | Purpose | Usage |
|----------|---------|-------|
| `ProtocolWorkflowEventBus` | Event-driven orchestration | Workflow coordination |
| `ProtocolWorkflowOrchestrator` | Workflow management | Distributed execution |
| `ProtocolWorkQueue` | Task scheduling | Work distribution |
| `ProtocolWorkflowPersistence` | State management | Workflow state storage |

### MCP Integration
| Protocol | Purpose | Usage |
|----------|---------|-------|
| `ProtocolMCPRegistry` | Tool coordination | Multi-subsystem management |
| `ProtocolMCPToolProxy` | Tool execution | Distributed tool calls |
| `ProtocolMCPMonitor` | Health monitoring | System health tracking |
| `ProtocolMCPSubsystemClient` | Subsystem communication | Tool routing |

### Event Processing
| Protocol | Purpose | Usage |
|----------|---------|-------|
| `ProtocolEventBus` | Event messaging | Distributed communication |
| `ProtocolKafkaAdapter` | Kafka integration | Event streaming |
| `ProtocolEventOrchestrator` | Event coordination | Event routing |
| `ProtocolEventPublisher` | Event publishing | Message distribution |

### Container Management
| Protocol | Purpose | Usage |
|----------|---------|-------|
| `ProtocolServiceRegistry` | Service registration | Dependency injection |
| `ProtocolServiceFactory` | Service creation | Instance management |
| `ProtocolDependencyGraph` | Dependency analysis | Circular dependency detection |
| `ProtocolInjectionContext` | Injection tracking | Context management |

## 🔧 Implementation Notes

### Protocol Compliance

All protocols in the API reference are designed to be:

- **Runtime Checkable**: Use `isinstance(obj, Protocol)` for validation
- **Type Safe**: Full mypy compatibility with strict checking
- **Framework Agnostic**: No dependencies on specific implementations
- **Forward Compatible**: Extensible design for future enhancements

### SPI Purity

The API reference documents pure protocol definitions that:

- Contain no concrete implementations
- Use only abstract method signatures with `...`
- Employ type hints for all parameters and return values
- Follow namespace isolation rules
- Maintain zero runtime dependencies

### Usage Patterns

Common patterns documented throughout:

- **Dependency Injection**: Using protocols as service contracts
- **Event Sourcing**: Building event-driven architectures
- **Distributed Coordination**: Multi-node service coordination
- **Type Safety**: Leveraging strong typing for reliability

## 📊 Protocol Statistics

- **Total Protocols**: 165 protocol files
- **Domain Coverage**: 22 specialized domains
- **Type Definitions**: 13 comprehensive type modules
- **Enterprise Features**: Health monitoring, metrics, circuit breakers
- **Architecture Patterns**: Event sourcing, dependency injection, distributed coordination

## 🔍 Navigation

Use the sidebar or table of contents to navigate between different protocol domains. Each page includes:

- **Overview** - Domain purpose and key concepts
- **Types** - Type definitions and aliases
- **Protocols** - Protocol interface definitions
- **Usage Examples** - Practical usage patterns
- **Integration Notes** - Implementation guidance

## 📄 Version Information

- **API Version**: 0.1.0
- **Python Compatibility**: 3.11, 3.12, 3.13
- **Type Checking**: mypy strict mode compatible
- **Runtime Checking**: All protocols are `@runtime_checkable`

---

*This API reference is automatically generated from protocol definitions and maintained alongside the codebase.*
