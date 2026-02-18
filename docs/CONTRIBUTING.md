# Contributing to omnibase_spi

Thank you for your interest in contributing to omnibase_spi! This document provides guidelines for contributing to the ONEX (OmniNode Execution System) Service Provider Interface.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Code Standards](#code-standards)
- [Protocol Development Guidelines](#protocol-development-guidelines)
- [Testing Requirements](#testing-requirements)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Code of Conduct](#code-of-conduct)
- [Getting Help](#getting-help)
- [License](#license)

## Getting Started

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (for package management)
- Git
- Basic understanding of ONEX architecture and Python protocols

### First Steps

1. **Read the documentation**:
   - [API Reference](api-reference/README.md) - Protocol documentation
   - [MVP Plan](MVP_PLAN.md) - Architecture and work breakdown
   - [Validation Integration Plan](VALIDATION_INTEGRATION_PLAN.md) - Validation approach

2. **Explore the codebase**:
   - Review protocol definitions in `src/omnibase_spi/protocols/`
   - Study the exception hierarchy in `src/omnibase_spi/exceptions.py`
   - Check domain-specific protocols (nodes, handlers, contracts, etc.)

3. **Understand the dependency direction**:
   - SPI imports Core: allowed and required (runtime imports of models)
   - Core imports SPI: forbidden
   - SPI imports Infra: forbidden
   - Infra imports SPI + Core: expected (implements behavior)

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/YOUR_USERNAME/omnibase_spi.git
cd omnibase_spi
```

### 2. Install Dependencies

```bash
# Install with uv
uv sync --group dev
```

### 3. Set Up Git Hooks

```bash
# Install pre-commit hooks (formatting, linting, type checking, validation)
uv run pre-commit install
```

**What do these hooks do?**

- **Pre-commit**: Runs before every commit
  - Code formatting (ruff format)
  - Linting (ruff check)
  - Type checking (mypy)
  - Protocol naming validation
  - Namespace isolation checks
  - Fast feedback on code quality

### 4. Verify Setup

```bash
# Run tests
uv run pytest tests/

# Run type checking
uv run mypy src/

# Run linting
uv run ruff check src/

# Run all validations
python scripts/validation/run_all_validations.py

# Run pre-commit hooks
uv run pre-commit run --all-files
```

## Contributing Guidelines

### Types of Contributions

We welcome:

- **New protocols** - Add new protocol definitions for ONEX capabilities
- **Protocol refinements** - Improve existing protocol signatures and contracts
- **Bug fixes** - Fix issues in existing code
- **Documentation** - Improve docs, examples, tutorials
- **Tests** - Add test coverage
- **Validation improvements** - Enhance validation scripts and checks

### Before You Start

1. **Check existing issues** - Look for related issues or discussions
2. **Open an issue first** - For significant changes, discuss before implementing
3. **Get feedback early** - Share your approach before investing too much time
4. **Review naming conventions** - All protocols must follow SPI naming standards

## Code Standards

### SPI Naming Conventions

**Files**:

- Protocols: `protocol_<name>.py`
- Exceptions: `exceptions.py` (centralized)

**Classes**:

- Protocols: `Protocol<Name>` (e.g., `ProtocolComputeNode`, `ProtocolHandler`)
- Exceptions: `<Type>Error` (e.g., `SPIError`, `RegistryError`)

**Methods**:

- Use `snake_case` for all methods and functions
- Use descriptive names that explain intent

### Code Quality Standards

1. **Type Annotations**: All functions must have type hints
   ```python
   def process_data(input_data: dict, config: ModelConfig) -> dict:
       pass
   ```

2. **Runtime Checkable**: All protocols must use `@runtime_checkable`
   ```python
   from typing import Protocol, runtime_checkable

   @runtime_checkable
   class ProtocolExample(Protocol):
       """Protocol description."""
       ...
   ```

3. **No Pydantic Models**: All `BaseModel` definitions belong in `omnibase_core`
   - SPI may import Core models for type hints
   - SPI must not define its own Pydantic models

4. **Documentation**: All public APIs must have docstrings
   ```python
   async def my_method(data: dict) -> dict:
       """
       Process input data and return result.

       Args:
           data: Input data dictionary

       Returns:
           Processed result dictionary

       Raises:
           SPIError: When operation fails
       """
       ...
   ```

## Protocol Development Guidelines

### Protocol Design Standards

1. **Naming Conventions**
   - Use `Protocol*` prefix for all protocols
   - Use descriptive names that indicate purpose
   - Follow Python naming conventions

2. **Protocol Structure**
   ```python
   from typing import Protocol, runtime_checkable, Optional

   @runtime_checkable
   class ProtocolExample(Protocol):
       """
       Brief description of the protocol's purpose.

       Detailed description covering:
       - Primary use cases and scenarios
       - Key features and capabilities
       - Integration patterns and usage
       - Implementation requirements
       """

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
           """
           ...
   ```

3. **Type Annotations**
   - Use proper type hints for all parameters
   - Include return type annotations
   - Use `Optional` for optional parameters
   - Use `Union` for multiple possible types

### Protocol Implementation Requirements

1. **Runtime Checkable**
   - All protocols must use `@runtime_checkable` decorator
   - Support `isinstance(obj, Protocol)` validation
   - Enable duck typing patterns

2. **Type Safety**
   - Full mypy compatibility with strict checking
   - No `Any` types in public interfaces
   - Comprehensive type coverage

3. **Namespace Isolation**
   - Complete separation from implementation packages
   - No concrete implementations in protocol files
   - No imports from `omnibase_infra`
   - Runtime imports from `omnibase_core` allowed

4. **Documentation**
   - Comprehensive docstrings for all protocols
   - Clear parameter and return descriptions
   - Usage examples where appropriate
   - Integration notes for complex protocols

## Testing Requirements

### Test Coverage

- **Minimum**: 80% code coverage
- **Target**: 90% code coverage
- **Critical paths**: 100% coverage

### Writing Tests

```python
import pytest
from typing import Protocol

@pytest.mark.asyncio
async def test_protocol_compliance():
    """Test that implementation satisfies protocol."""
    # Arrange
    class MockImplementation:
        async def method_name(self, param: str) -> str:
            return f"processed: {param}"

    # Act & Assert
    assert isinstance(MockImplementation(), ProtocolExample)
```

### Running Tests

```bash
# Run all tests
uv run pytest tests/

# Run with coverage
uv run pytest tests/ --cov=src --cov-report=html

# Run specific test
uv run pytest tests/unit/test_protocols.py -v
```

### Validation Suite

```bash
# Run all validation checks
python scripts/validation/run_all_validations.py

# Run with strict mode and verbose output
python scripts/validation/run_all_validations.py --strict --verbose

# Individual validators
python scripts/validation/validate_naming_patterns.py src/
python scripts/validation/validate_namespace_isolation.py
python scripts/validation/validate_architecture.py --verbose
```

## Documentation

### Documentation Standards

1. **Docstrings**: All public APIs
2. **Type hints**: All function signatures
3. **Examples**: Include usage examples
4. **Updates**: Update docs with code changes

### Adding Documentation

- Place API docs in `docs/api-reference/`
- Place guides in `docs/`
- Follow existing documentation structure

### API Reference Structure

- **[Core Protocols](api-reference/CORE.md)** - System fundamentals
- **[Container Protocols](api-reference/CONTAINER.md)** - Dependency injection
- **[Workflow Orchestration](api-reference/WORKFLOW-ORCHESTRATION.md)** - Event-driven FSM
- **[MCP Integration](api-reference/MCP.md)** - Multi-subsystem coordination

## Pull Request Process

### 1. Create a Branch

```bash
# Create feature branch
git checkout -b feature/my-new-protocol

# Or fix branch
git checkout -b fix/protocol-issue
```

### 2. Make Changes

- Follow code standards
- Add tests
- Update documentation
- Keep commits focused and atomic

### 3. Test Everything

```bash
# Run all quality checks
uv run pytest tests/
uv run mypy src/
uv run ruff check src/
uv run ruff format src/ --check

# Run validation suite
python scripts/validation/run_all_validations.py
uv run pre-commit run --all-files
```

### 4. Commit Changes

```bash
# Use semantic commit messages
git commit -m "feat(spi): add new protocol for data processing"
git commit -m "fix(spi): resolve protocol signature issue"
git commit -m "docs(spi): update protocol documentation"
```

**Commit Types**:

- `feat:` - New feature or protocol
- `fix:` - Bug fix
- `docs:` - Documentation only
- `style:` - Code style changes (formatting)
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Build process or auxiliary tool changes

### 5. Push and Create PR

```bash
# Push to your fork
git push origin feature/my-new-protocol

# Create pull request on GitHub
```

### 6. PR Requirements

Your PR must:

- Pass all CI checks
- Include tests for new protocols
- Update relevant documentation
- Follow code standards
- Have a clear description
- Pass all validation checks

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] New protocol
- [ ] Protocol refinement
- [ ] Bug fix
- [ ] Documentation update
- [ ] Refactoring

## Testing
- [ ] Tests added/updated
- [ ] All tests passing
- [ ] Validation suite passing
- [ ] Manual testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-reviewed code
- [ ] Documented changes
- [ ] No breaking changes (or documented)
- [ ] Protocol naming conventions followed
- [ ] @runtime_checkable decorator present
```

## Code of Conduct

### Our Standards

- **Be respectful** - Treat everyone with respect
- **Be collaborative** - Work together effectively
- **Be professional** - Maintain professionalism
- **Be inclusive** - Welcome diverse perspectives

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or inflammatory comments
- Personal attacks
- Unprofessional conduct

## Getting Help

### Resources

- [API Reference](api-reference/README.md)
- [MVP Plan](MVP_PLAN.md)
- [GitHub Issues](https://github.com/OmniNode-ai/omnibase_spi/issues)

### Questions

- **General questions**: Open a GitHub discussion
- **Bug reports**: Open a GitHub issue
- **Feature requests**: Open a GitHub issue with "enhancement" label
- **Protocol design**: Discuss in issue before implementing

## See Also

- **[Glossary](GLOSSARY.md)** - Definitions of SPI-specific terms (Protocol, Handler, Node, etc.)
- **[Architecture Overview](architecture/README.md)** - Design principles and patterns
- **[Quick Start Guide](QUICK-START.md)** - Get up and running quickly
- **[Developer Guide](developer-guide/README.md)** - Complete development workflow
- **[Main README](../README.md)** - Repository overview

### API Reference by Domain

- **[Node Protocols](api-reference/NODES.md)** - ONEX 4-node architecture
- **[Handler Protocols](api-reference/HANDLERS.md)** - I/O handler interfaces
- **[Contract Compilers](api-reference/CONTRACTS.md)** - Contract compilation
- **[Registry Protocols](api-reference/REGISTRY.md)** - Handler registry
- **[Exception Hierarchy](api-reference/EXCEPTIONS.md)** - Error handling

For term definitions, see the [Glossary](GLOSSARY.md).

## License

By contributing to omnibase_spi, you agree that your contributions will be licensed under the same license as the project.

---

**Thank you for contributing to omnibase_spi!**

Your contributions help make ONEX better for everyone.
