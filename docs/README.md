# ONEX Service Provider Interface (omnibase-spi) Documentation

## Overview

Welcome to the comprehensive documentation for **omnibase-spi**, the Service Provider Interface package that provides protocol-based typing for the ONEX distributed orchestration framework. This documentation covers everything you need to know to use, implement, and extend ONEX protocols for event-driven workflow orchestration, MCP integration, and distributed service coordination.

## Architecture Overview

The ONEX SPI follows a **protocol-first design** with **176+ protocols** across **22 specialized domains**. This enterprise-grade architecture provides:

- **Zero Implementation Dependencies**: Pure protocol contracts only
- **Runtime Type Safety**: Full `@runtime_checkable` protocol support
- **Dependency Injection**: Sophisticated service lifecycle management
- **Event-Driven Architecture**: Event sourcing and workflow orchestration
- **Multi-Subsystem Coordination**: MCP integration and distributed tooling
- **Enterprise Features**: Health monitoring, metrics, circuit breakers, and more

## Documentation Structure

### Getting Started
- **[API Reference Overview](api-reference/README.md)** - Complete protocol and type documentation
- **[Core Protocols](api-reference/CORE.md)** - System-level contracts and fundamentals
- **[Container Protocols](api-reference/CONTAINER.md)** - Dependency injection and service management

### Developer Resources
- **[API Reference Overview](api-reference/README.md)** - Complete protocol and type documentation
- **[Core Protocols](api-reference/CORE.md)** - System-level contracts and fundamentals
- **[Container Protocols](api-reference/CONTAINER.md)** - Dependency injection and service management
- **[Workflow Orchestration](api-reference/WORKFLOW-ORCHESTRATION.md)** - Event-driven FSM orchestration
- **[MCP Integration](api-reference/MCP.md)** - Model Context Protocol multi-subsystem coordination
- **[Event Bus](api-reference/EVENT-BUS.md)** - Distributed messaging and event streaming
- **[Memory Management](api-reference/MEMORY.md)** - Memory operations and workflow management
- **[Networking](api-reference/NETWORKING.md)** - HTTP, Kafka, and communication protocols
- **[File Handling](api-reference/FILE-HANDLING.md)** - File processing and type handling
- **[Validation](api-reference/VALIDATION.md)** - Input validation and schema checking

### API Reference
- **[API Reference Overview](api-reference/README.md)** - Complete protocol and type documentation
- **[Core Protocols](api-reference/CORE.md)** - System-level contracts and fundamentals
- **[Container Protocols](api-reference/CONTAINER.md)** - Dependency injection and service management
- **[Workflow Orchestration](api-reference/WORKFLOW-ORCHESTRATION.md)** - Event-driven FSM orchestration
- **[MCP Integration](api-reference/MCP.md)** - Model Context Protocol multi-subsystem coordination
- **[Event Bus](api-reference/EVENT-BUS.md)** - Distributed messaging and event streaming
- **[Memory Management](api-reference/MEMORY.md)** - Memory operations and workflow management
- **[Networking](api-reference/NETWORKING.md)** - HTTP, Kafka, and communication protocols
- **[File Handling](api-reference/FILE-HANDLING.md)** - File processing and type handling
- **[Validation](api-reference/VALIDATION.md)** - Input validation and schema checking

### Specialized Documentation
- **[Protocol Composition Patterns](patterns/PROTOCOL-COMPOSITION-PATTERNS.md)** - Advanced protocol design patterns
- **[Protocol Selection Guide](patterns/PROTOCOL-SELECTION-GUIDE.md)** - Decision framework for choosing protocols
- **[Memory Protocols Guide](examples/MEMORY_PROTOCOLS_GUIDE.md)** - Memory system implementation patterns
- **[Node Templates](templates/README.md)** - ONEX 4-node architecture templates

## Protocol Domains

### Core System (16 protocols)
**Foundation protocols for system operations**
- Logging, health monitoring, error handling
- Service discovery, performance metrics
- Serialization, URI parsing, version management

### Container Management (21 protocols)
**Enterprise-grade dependency injection**
- Service registry with lifecycle management
- Circular dependency detection
- Health monitoring and metrics collection
- Factory patterns and injection contexts

### Workflow Orchestration (14 protocols)
**Event-driven FSM coordination**
- Event sourcing with sequence numbers
- Workflow state management and projections
- Task scheduling and node coordination
- Distributed workflow execution

### MCP Integration (15 protocols)
**Model Context Protocol coordination**
- Multi-subsystem tool registration
- Load balancing and failover
- Health monitoring and metrics
- Tool execution tracking

### Event Bus (13 protocols)
**Distributed messaging infrastructure**
- Pluggable backend adapters (Kafka, Redis, in-memory)
- Async and sync event bus implementations
- Event message serialization and routing
- Dead letter queue handling

### Memory Management (15 protocols)
**Memory operations and workflow management**
- Key-value store operations
- Workflow state persistence
- Memory security and streaming
- Agent coordination and management

### Networking (6 protocols)
**Communication and resilience**
- HTTP client with extended features
- Kafka client with advanced capabilities
- Circuit breaker patterns
- Communication bridges

### File Handling (8 protocols)
**File processing and metadata**
- File type detection and processing
- ONEX metadata stamping
- Directory traversal and discovery
- File I/O operations

### Advanced Features (14 protocols)
**Sophisticated system capabilities**
- Adaptive chunking and AST building
- Contract analysis and coverage
- Multi-vector indexing
- Output formatting and stamping

### Plus 10+ More Specialized Domains
- **Analytics**: Data collection and reporting
- **CLI**: Command line interface operations
- **Discovery**: Service and handler discovery
- **LLM**: Large Language Model integration
- **Node**: Node management and configuration
- **ONEX**: Platform-specific protocols
- **Schema**: Schema loading and validation
- **Semantic**: Advanced text processing
- **Storage**: Data persistence and backends
- **Test**: Testing frameworks and utilities
- **Types**: Comprehensive type definitions
- **Validation**: Input validation and compliance

## Project Information

- **[Changelog](../CHANGELOG.md)** - Version history and release notes
- **[Deprecations](DEPRECATIONS.md)** - Deprecated APIs and migration guides
- **[Contributing Guide](CONTRIBUTING.md)** - Development workflow and validation requirements

## Quick Navigation

### For New Users
1. Start with the [Quick Start Guide](QUICK-START.md) for immediate hands-on experience
2. Read the [Developer Guide](developer-guide/README.md) for setup and workflow
3. Review the [Architecture Overview](architecture/README.md) to understand SPI design
4. Try the protocol examples in the API Reference

### For Developers
1. Read the [Developer Guide](developer-guide/README.md) for complete workflow coverage
2. Check the [API Reference](api-reference/README.md) for detailed protocol documentation
3. Review the [Testing Guide](TESTING.md) for protocol compliance strategies
4. Try the [Examples](examples/README.md) for practical usage patterns

### For Architects
1. Review [Architecture Overview](architecture/README.md) for design principles and patterns
2. Study [Protocol Composition Patterns](patterns/PROTOCOL-COMPOSITION-PATTERNS.md) for advanced protocol design
3. Review [Container Protocols](api-reference/CONTAINER.md) for dependency injection patterns
4. Study [Memory Management](api-reference/MEMORY.md) for workflow state persistence

## Key Features

### Event-Driven Workflow Orchestration
- **FSM States**: `pending` → `running` → `completed` with compensation actions
- **Event Sourcing**: Sequence numbers, causation tracking, and replay capabilities
- **Isolation**: `{workflowType, instanceId}` pattern for workflow separation
- **Projections**: Real-time state derivation from events

### MCP Integration (Model Context Protocol)
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

### Core Architecture
- **Protocol Purity**: Zero implementation dependencies, contracts only
- **Type Safety**: Strong typing with `typing.Protocol` and runtime checking
- **Namespace Isolation**: Complete separation from implementation packages
- **Runtime Validation**: `@runtime_checkable` protocols for duck typing

## Development Workflow

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

## Protocol Statistics

- **Total Protocols**: 176+ protocol files
- **Domain Coverage**: 22 specialized domains
- **Type Definitions**: 14 comprehensive type modules
- **Enterprise Features**: Health monitoring, metrics, circuit breakers
- **Architecture Patterns**: Event sourcing, dependency injection, distributed coordination

## Validation and Quality Assurance

The omnibase-spi maintains strict architectural purity through automated validation:

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

## Contributing

This documentation is maintained alongside the omnibase-spi codebase. See the **[Contributing Guide](CONTRIBUTING.md)** for complete development workflow including:

- **Development Setup**: Poetry environment and pre-commit hooks
- **Protocol Design Guidelines**: Standards for creating new protocols
- **Validation Requirements**: Namespace isolation and SPI purity checking
- **Testing Standards**: Protocol compliance and type safety verification
- **Documentation Standards**: Technical writing and code example guidelines

For quick contributions:
1. **Issues**: Report documentation issues on the main repository
2. **Pull Requests**: Follow the validation requirements in the contributing guide  
3. **Quality Gates**: All changes must pass `mypy --strict`, namespace isolation, and protocol compliance tests

## Version Information

- **Package Version**: 0.3.0
- **Python Support**: 3.12+
- **Architecture**: Protocol-first SPI with zero runtime dependencies
- **Documentation Updated**: 2025-12-06
- **Protocol Count**: 176+ protocols across 22 domains

## ONEX Ecosystem

This SPI package is part of the ONEX platform ecosystem:

| Repository | Description | Role |
|------------|-------------|------|
| [omnibase_spi](https://github.com/OmniNode-ai/omnibase_spi) | Service Provider Interface | Protocol contracts and exceptions |
| [omnibase_core](https://github.com/OmniNode-ai/omnibase_core) | Core Models | Pydantic models and runtime contracts |
| [omnibase_infra](https://github.com/OmniNode-ai/omnibase_infra) | Infrastructure | Concrete implementations |

## See Also

- **[Main README](../README.md)** - Repository overview and quick start
- **[CLAUDE.md](../CLAUDE.md)** - AI assistant guidance for working with this codebase
- **[Glossary](GLOSSARY.md)** - Definitions of SPI-specific terminology
- **[Deprecations](DEPRECATIONS.md)** - Deprecated APIs, removal timelines, and migration guides
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute to the project
- **[MVP Plan](MVP_PLAN.md)** - v0.3.0 work breakdown and architecture

For term definitions used throughout this documentation, see the [Glossary](GLOSSARY.md).

## License

This documentation and the omnibase-spi package are provided under the MIT license.

---

*This documentation is automatically generated from protocol definitions and maintained alongside the codebase.*
