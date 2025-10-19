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

## API Reference

- **[Core Protocols](api-reference/core.md)** - System fundamentals
- **[Container Protocols](api-reference/container.md)** - Dependency injection
- **[Workflow Orchestration](api-reference/workflow-orchestration.md)** - Event-driven FSM
- **[MCP Integration](api-reference/mcp.md)** - Multi-subsystem coordination

---

*For detailed protocol documentation, see the [API Reference](api-reference/README.md).*
