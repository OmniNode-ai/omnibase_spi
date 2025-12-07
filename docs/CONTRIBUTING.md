# Contributing Guide

## Development Workflow

Complete development workflow and validation requirements for contributing to ONEX SPI.

## Development Setup

### Prerequisites

- Python 3.12+
- Poetry for dependency management
- Git for version control
- Pre-commit hooks for code quality

### Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd omnibase-spi

# Install dependencies
poetry install

# Install pre-commit hooks
poetry run pre-commit install

# Activate virtual environment
poetry shell
```

## Development Workflow

### 1. Create Feature Branch

```bash
# Create and checkout feature branch
git checkout -b feature/new-protocol

# Make changes
# ... implement new protocol ...

# Stage changes
git add .

# Commit with descriptive message
git commit -m "Add new protocol for advanced data processing"
```

### 2. Run Validation

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

### 3. Create Pull Request

```bash
# Push feature branch
git push origin feature/new-protocol

# Create pull request with:
# - Clear description of changes
# - Reference to related issues
# - Validation results
```

## Protocol Development Guidelines

### Protocol Design Standards

1. **Naming Conventions**
   - Use `Protocol*` prefix for all protocols
   - Use descriptive names that indicate purpose
   - Follow Python naming conventions

2. **Protocol Structure**
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
   - Zero runtime dependencies

4. **Documentation**
   - Comprehensive docstrings for all protocols
   - Clear parameter and return descriptions
   - Usage examples where appropriate
   - Integration notes for complex protocols

## Validation Requirements

### Automated Validation

All changes must pass automated validation:

```bash
# Run complete validation suite
poetry run pytest && poetry build

# Type safety validation
poetry run mypy src/ --strict --no-any-expr

# Protocol compliance checking
poetry run python scripts/ast_spi_validator.py --check-protocols

# Namespace isolation testing
./scripts/validate-namespace-isolation.sh
```

### Manual Validation

1. **Protocol Compliance**
   - Verify all protocols are `@runtime_checkable`
   - Test `isinstance(obj, Protocol)` validation
   - Ensure proper type annotations

2. **Documentation Quality**
   - Review all docstrings for clarity
   - Verify parameter descriptions
   - Check return type documentation
   - Validate usage examples

3. **Integration Testing**
   - Test protocol interactions
   - Verify error handling
   - Check performance characteristics

## Code Quality Standards

### Code Style

1. **Formatting**
   - Use ruff for code formatting and linting
   - Follow PEP 8 style guidelines
   - Maintain consistent indentation

2. **Imports**
   - Use absolute imports
   - Group imports logically
   - Remove unused imports

3. **Comments**
   - Use clear, concise comments
   - Explain complex logic
   - Document non-obvious decisions

### Testing Standards

1. **Unit Tests**
   - Test individual protocol methods
   - Cover edge cases and error conditions
   - Verify type safety and compliance

2. **Integration Tests**
   - Test protocol interactions
   - Verify end-to-end workflows
   - Check performance characteristics

3. **Documentation Tests**
   - Verify code examples work
   - Test usage patterns
   - Validate integration examples

## Pull Request Process

### Pull Request Requirements

1. **Description**
   - Clear description of changes
   - Reference to related issues
   - Breaking changes documentation

2. **Validation Results**
   - All automated tests passing
   - Type safety validation complete
   - Protocol compliance verified

3. **Documentation Updates**
   - Update relevant documentation
   - Add usage examples
   - Update API reference if needed

### Review Process

1. **Automated Review**
   - All validation checks must pass
   - Code quality metrics must meet standards
   - Documentation must be complete

2. **Manual Review**
   - Code review by maintainers
   - Protocol design review
   - Integration testing review

3. **Approval Requirements**
   - At least one maintainer approval
   - All validation checks passing
   - Documentation updates complete

## Quality Gates

### Pre-commit Validation

```bash
# Install pre-commit hooks
poetry run pre-commit install

# Run pre-commit validation
poetry run pre-commit run --all-files
```

### Continuous Integration

All pull requests must pass:

1. **Type Safety** - mypy strict mode validation
2. **Protocol Compliance** - AST-based protocol validation
3. **Namespace Isolation** - Implementation dependency checking
4. **Documentation** - Docstring and example validation
5. **Performance** - Basic performance regression testing

### Release Validation

Before release:

1. **Full Test Suite** - All tests passing
2. **Documentation** - Complete and accurate
3. **Performance** - No regressions
4. **Compatibility** - Backward compatibility maintained

## Best Practices

### Protocol Development

1. **Start Simple** - Begin with basic functionality
2. **Add Complexity** - Gradually add advanced features
3. **Test Thoroughly** - Comprehensive testing coverage
4. **Document Well** - Clear documentation and examples

### Collaboration

1. **Communication** - Clear communication in issues and PRs
2. **Feedback** - Constructive feedback and suggestions
3. **Learning** - Continuous learning and improvement
4. **Sharing** - Share knowledge and best practices

## API Reference

- **[Core Protocols](api-reference/CORE.md)** - System fundamentals
- **[Container Protocols](api-reference/CONTAINER.md)** - Dependency injection
- **[Workflow Orchestration](api-reference/WORKFLOW-ORCHESTRATION.md)** - Event-driven FSM
- **[MCP Integration](api-reference/MCP.md)** - Multi-subsystem coordination

---

*For detailed protocol documentation, see the [API Reference](api-reference/README.md).*
