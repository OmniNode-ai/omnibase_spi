# ONEX Service Provider Interface (omnibase-spi) Documentation

## Overview

Welcome to the comprehensive documentation for omnibase-spi, the Service Provider Interface package that provides protocol-based typing for the ONEX distributed orchestration framework. This documentation covers everything you need to know to use, implement, and extend ONEX protocols for event-driven workflow orchestration, MCP integration, and distributed service coordination.

## Documentation Structure

### Getting Started
- **[Quick Start Guide](quick-start.md)** - Fast onboarding with executable examples
- **[Installation & Setup](getting-started/installation.md)** - Detailed installation instructions  
- **[Core Concepts](getting-started/core-concepts.md)** - Understanding protocols and SPI design
- **[Your First Protocol](getting-started/first-protocol.md)** - Tutorial: implementing your first protocol

### Developer Resources
- **[Developer Guide](developer-guide/README.md)** - Complete development workflow and best practices
- **[Architecture Overview](architecture/README.md)** - Design patterns, principles, and architectural decisions
- **[Integration Guide](integration/README.md)** - Framework integration patterns and dependency injection
- **[Testing Guide](testing.md)** - Comprehensive testing strategies for protocol compliance
- **[Contributing Guide](contributing.md)** - Development workflow and validation requirements
- **[Migration Guide](migration.md)** - Protocol evolution and version management

### API Reference
- **[API Reference Overview](api-reference/README.md)** - Complete protocol and type documentation
- **[Core Types & Protocols](api-reference/core-types.md)** - Fundamental system types and contracts
- **[Workflow Orchestration](api-reference/workflow-orchestration.md)** - Event-driven FSM and orchestration protocols  
- **[MCP Integration](api-reference/mcp.md)** - Model Context Protocol multi-subsystem coordination
- **[Event Bus Protocols](api-reference/event-bus-protocols.md)** - Event-driven architecture contracts
- **[Container Protocols](api-reference/container-protocols.md)** - Dependency injection and service location

### Specialized Documentation
- **[SPI Architecture](architecture/spi-architecture.md)** - Service Provider Interface design principles
- **[Namespace Isolation](architecture/namespace-isolation.md)** - Understanding namespace separation
- **[Protocol Design Patterns](architecture/protocol-patterns.md)** - Common protocol design patterns
- **[Event Sourcing Patterns](architecture/event-sourcing.md)** - Event sourcing and workflow orchestration
- **[MCP Coordination](architecture/mcp-coordination.md)** - Multi-subsystem tool coordination patterns

### Implementation Guides
- **[Framework Integration](integration/framework-integration.md)** - FastAPI, Django, Flask integration patterns
- **[Dependency Injection](integration/dependency-injection.md)** - Service container and protocol binding
- **[Testing Integration](integration/testing-integration.md)** - Protocol compliance testing
- **[Performance Optimization](integration/performance.md)** - High-performance protocol implementations

### Reference Materials
- **[FAQ](reference/faq.md)** - Frequently asked questions
- **[Troubleshooting](reference/troubleshooting.md)** - Common issues and solutions
- **[Glossary](reference/glossary.md)** - Technical terms and definitions
- **[Best Practices](best-practices/)** - Protocol design and implementation guidelines

## Quick Navigation

### For New Users
1. Start with the [Quick Start Guide](quick-start.md) for immediate hands-on experience
2. Read [Core Concepts](getting-started/core-concepts.md) to understand SPI design
3. Follow the [Installation Guide](getting-started/installation.md) for setup
4. Try the [First Protocol Tutorial](getting-started/first-protocol.md)

### For Developers
1. Read the [Developer Guide](developer-guide/README.md) for complete workflow coverage
2. Check the [API Reference](api-reference/README.md) for detailed protocol documentation
3. Use the [Integration Guide](integration/README.md) for framework setup patterns
4. Review the [Testing Guide](testing.md) for protocol compliance strategies

### For Architects
1. Review [Architecture Overview](architecture/README.md) for design principles and patterns
2. Understand [Event Sourcing Patterns](architecture/event-sourcing.md) for workflow orchestration
3. Study [MCP Coordination](architecture/mcp-coordination.md) for multi-subsystem integration
4. Consider [Migration Strategies](migration.md) for protocol evolution

### Key Domains

#### Event-Driven Workflow Orchestration
- **[Workflow Orchestration API](api-reference/workflow-orchestration.md)** - FSM patterns and event sourcing
- **FSM States**: `pending` → `running` → `completed` with compensation actions
- **Event Sourcing**: Sequence numbers, causation tracking, and replay capabilities
- **Isolation**: `{workflowType, instanceId}` pattern for workflow separation

#### MCP Integration (Model Context Protocol)
- **[MCP Integration API](api-reference/mcp.md)** - Multi-subsystem tool coordination
- **Tool Registry**: Dynamic discovery and load balancing across subsystems
- **Health Monitoring**: TTL-based cleanup and subsystem status tracking
- **Execution Tracking**: Correlation IDs and performance metrics

#### Core Architecture
- **[Core Types API](api-reference/core-types.md)** - Fundamental system contracts
- **Protocol Purity**: Zero implementation dependencies, contracts only
- **Type Safety**: Strong typing with `typing.Protocol` and runtime checking
- **Namespace Isolation**: Complete separation from implementation packages

## Contributing

This documentation is maintained alongside the omnibase-spi codebase. See the **[Contributing Guide](contributing.md)** for complete development workflow including:

- **Development Setup**: Poetry environment and pre-commit hooks
- **Protocol Design Guidelines**: Standards for creating new protocols
- **Validation Requirements**: Namespace isolation and SPI purity checking
- **Testing Standards**: Protocol compliance and type safety verification
- **Documentation Standards**: Technical writing and code example guidelines

For quick contributions:
1. **Issues**: Report documentation issues on the main repository
2. **Pull Requests**: Follow the validation requirements in the contributing guide  
3. **Quality Gates**: All changes must pass `mypy --strict`, namespace isolation, and protocol compliance tests

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

## Version Information

- **Package Version**: 0.0.2  
- **Python Support**: 3.11, 3.12, 3.13
- **Architecture**: Protocol-first SPI with zero runtime dependencies
- **Documentation Updated**: 2025-01-26

## License

This documentation and the omnibase-spi package are provided under the MIT license.