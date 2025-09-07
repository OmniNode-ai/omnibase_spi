# ONEX SPI API Reference

## Overview

Complete API reference documentation for all protocols, types, and interfaces in the omnibase-spi package. This reference provides detailed documentation for every public interface in the Service Provider Interface layer.

## Organization

The API reference is organized by domain, matching the package structure:

### Core Protocols and Types
- **[Core Types](core-types.md)** - Fundamental type definitions and base protocols
- **[Core Protocols](core-protocols.md)** - System-level protocol interfaces

### Domain-Specific Protocols
- **[Workflow Orchestration](workflow-orchestration.md)** - Event-driven FSM orchestration protocols
- **[MCP Integration](mcp.md)** - Model Context Protocol integration interfaces
- **[Event Bus](event-bus.md)** - Event messaging and streaming protocols
- **[Container](container.md)** - Dependency injection and service location protocols
- **[Discovery](discovery.md)** - Service discovery and handler discovery protocols
- **[File Handling](file-handling.md)** - File processing and type handling protocols
- **[Validation](validation.md)** - Input validation and schema validation protocols

## Documentation Conventions

### Protocol Documentation

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

### Type Documentation

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

### Navigation

Use the sidebar or table of contents to navigate between different protocol domains. Each page includes:

- **Overview** - Domain purpose and key concepts
- **Types** - Type definitions and aliases
- **Protocols** - Protocol interface definitions
- **Usage Examples** - Practical usage patterns
- **Integration Notes** - Implementation guidance

## Quick Reference

### Core System Interfaces
| Protocol | Purpose | Usage |
|----------|---------|-------|
| `ProtocolLogger` | Structured logging | System-wide logging |
| `ProtocolNodeRegistry` | Node discovery | Service registration |
| `ProtocolCacheService` | Caching abstraction | Performance optimization |

### Workflow Orchestration
| Protocol | Purpose | Usage |
|----------|---------|-------|
| `ProtocolWorkflowEventBus` | Event-driven orchestration | Workflow coordination |
| `ProtocolWorkflowPersistence` | State management | Workflow state storage |
| `ProtocolWorkflowNodeRegistry` | Node coordination | Distributed execution |

### MCP Integration
| Protocol | Purpose | Usage |
|----------|---------|-------|
| `ProtocolMCPRegistry` | Tool coordination | Multi-subsystem management |
| `ProtocolMCPToolProxy` | Tool execution | Distributed tool calls |
| `ProtocolMCPMonitor` | Health monitoring | System health tracking |

### Event Processing
| Protocol | Purpose | Usage |
|----------|---------|-------|
| `ProtocolEventBus` | Event messaging | Distributed communication |
| `ProtocolKafkaAdapter` | Kafka integration | Event streaming |

## Implementation Notes

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

## Version Information

- **API Version**: 0.0.2
- **Python Compatibility**: 3.11, 3.12, 3.13
- **Type Checking**: mypy strict mode compatible
- **Runtime Checking**: All protocols are `@runtime_checkable`

---

*This API reference is automatically generated from protocol definitions and maintained alongside the codebase.*