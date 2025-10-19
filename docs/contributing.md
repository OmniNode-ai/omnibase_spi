# Contributing Guide

## Overview

Welcome to the omnibase-spi project! This guide covers everything you need to know to contribute effectively to the Service Provider Interface layer of the ONEX ecosystem.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Protocol Design Guidelines](#protocol-design-guidelines)
- [Validation and Testing](#validation-and-testing)
- [Documentation Standards](#documentation-standards)
- [Code Review Process](#code-review-process)
- [Release Process](#release-process)

## Getting Started

### Prerequisites

- **Python**: 3.11, 3.12, or 3.13
- **Poetry**: For dependency management
- **Git**: For version control
- **IDE**: VS Code or PyCharm recommended

### Development Setup

#### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/omnibase-spi.git
cd omnibase-spi

# Add upstream remote
git remote add upstream https://github.com/OmniNode-ai/omnibase-spi.git
```

#### 2. Environment Setup

```bash
# Install dependencies
poetry install --with dev

# Setup pre-commit hooks
poetry run pre-commit install
poetry run pre-commit install --hook-type pre-push -c .pre-commit-config-push.yaml

# Verify setup
poetry run pytest tests/test_protocol_imports.py -v
```

#### 3. Validation Tools

```bash
# Validate SPI purity
poetry run python scripts/ast_spi_validator.py

# Check namespace isolation
./scripts/validate-namespace-isolation.sh

# Run type checking
poetry run mypy src/ --strict

# Run all validation
poetry run pytest && ./scripts/validate-spi-purity.sh
```

### Project Structure

```
omnibase-spi/
├── src/omnibase/protocols/        # Core protocol definitions
│   ├── core/                      # System-level protocols
│   ├── types/                     # Type definitions
│   ├── workflow_orchestration/    # Workflow protocols
│   ├── mcp/                       # MCP integration protocols
│   ├── event_bus/                 # Event messaging protocols
│   └── container/                 # DI and service location
├── tests/                         # Test suite
├── scripts/                       # Validation and utility scripts
├── docs/                          # Documentation
└── pyproject.toml                # Project configuration
```

## Development Workflow

### Branch Naming

```bash
# Feature branches
git checkout -b feature/protocol-user-management
git checkout -b feature/mcp-tool-validation

# Bug fixes  
git checkout -b fix/event-bus-memory-leak
git checkout -b fix/type-annotation-missing

# Documentation
git checkout -b docs/update-api-reference
git checkout -b docs/add-integration-examples

# Refactoring
git checkout -b refactor/consolidate-core-types
git checkout -b refactor/improve-error-handling
```

### Development Process

#### 1. Create Feature Branch

```bash
# Update main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name
```

#### 2. Make Changes

Follow the guidelines in [Protocol Design Guidelines](#protocol-design-guidelines).

#### 3. Validate Changes

```bash
# Run validation tools
poetry run python scripts/ast_spi_validator.py
./scripts/validate-namespace-isolation.sh
poetry run mypy src/ --strict

# Run tests
poetry run pytest

# Format code
poetry run black src/ tests/
poetry run isort src/ tests/
```

#### 4. Commit Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: add user management protocol with validation

- Add ProtocolUserService with CRUD operations
- Include comprehensive parameter validation  
- Add supporting User and UserFilter types
- Update package exports and documentation"
```

#### 5. Push and Create PR

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create pull request on GitHub
```

### Commit Message Convention

Use conventional commits format:

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature or protocol
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `test`: Test additions or changes
- `chore`: Build or tool changes

**Examples:**
```bash
feat(core): add cache service protocol with TTL support
fix(mcp): correct parameter validation in tool execution
docs(api): update workflow orchestration examples
refactor(types): consolidate error handling protocols
test(workflow): add comprehensive event sourcing tests
```

## Protocol Design Guidelines

### Core Principles

#### 1. Single Responsibility

```python
# ✅ Good - focused protocol
@runtime_checkable
class ProtocolUserService(Protocol):
    """Protocol for user management operations only."""
    async def create_user(self, email: str, name: str) -> User: ...
    async def get_user(self, user_id: UUID) -> Optional[User]: ...
    async def update_user(self, user_id: UUID, updates: dict) -> bool: ...

# ❌ Bad - mixed responsibilities
@runtime_checkable  
class ProtocolUserServiceWithLogging(Protocol):
    """Don't mix user operations with logging concerns."""
    async def create_user(self, email: str, name: str) -> User: ...
    async def log_user_action(self, action: str, user_id: UUID) -> None: ...
```

#### 2. Strong Typing

```python
# ✅ Good - specific types
async def process_workflow(
    self,
    workflow_type: str,
    context: dict[str, ContextValue],
    timeout_seconds: int = 300
) -> WorkflowState: ...

# ❌ Bad - generic types
async def process_workflow(self, data: Any) -> Any: ...
```

#### 3. Comprehensive Documentation

```python
@runtime_checkable
class ProtocolPaymentService(Protocol):
    """
    Payment processing service protocol.

    Handles secure payment transactions with support for multiple
    payment methods, comprehensive error handling, and audit trails.

    Key Features:
        - **Multiple Payment Methods**: Credit cards, digital wallets, bank transfers
        - **Security Compliance**: PCI DSS compliant transaction processing  
        - **Comprehensive Audit**: Full transaction audit trails
        - **Error Recovery**: Robust error handling with retry mechanisms
        - **Async Operations**: Non-blocking payment processing

    Security Considerations:
        - Never log sensitive payment information
        - Use tokenization for card data storage
        - Implement proper error messages to prevent information leakage

    Example:
        ```python
        async def process_payment(service: ProtocolPaymentService):
            result = await service.charge_card(
                amount=Decimal("99.99"),
                currency="USD",
                card_token="tok_secure123",
                description="Order #12345",
                idempotency_key="order-12345-payment"
            )

            if result.status == "completed":
                print(f"Payment successful: {result.transaction_id}")
            else:
                print(f"Payment failed: {result.error_message}")
        ```
    """

    async def charge_card(
        self,
        amount: Decimal,
        currency: str,
        card_token: str,
        description: str,
        idempotency_key: str,
        metadata: Optional[dict[str, str]] = None
    ) -> "PaymentResult":
        """
        Process credit card payment.

        Args:
            amount: Payment amount (must be positive)
            currency: ISO 4217 currency code (e.g., 'USD', 'EUR')
            card_token: Secure card token (never pass raw card data)
            description: Human-readable payment description
            idempotency_key: Unique key to prevent duplicate charges
            metadata: Optional metadata for tracking and reporting

        Returns:
            Payment result with transaction details

        Raises:
            ValueError: If amount is negative or currency invalid
            AuthenticationError: If card token is invalid
            InsufficientFundsError: If card has insufficient funds
            ProcessingError: If payment gateway fails
        """
        ...
```

#### 4. Runtime Checkable

```python
# ✅ Always include @runtime_checkable for isinstance() support
@runtime_checkable
class ProtocolEmailService(Protocol):
    async def send_email(self, to: str, subject: str, body: str) -> bool: ...

# ❌ Missing decorator prevents runtime checking
class ProtocolEmailService(Protocol):  # Can't use isinstance()
    async def send_email(self, to: str, subject: str, body: str) -> bool: ...
```

### Type Definition Guidelines

#### Use Literal Types for Enums

```python
# ✅ Good - use Literal for constrained values
UserStatus = Literal["active", "inactive", "suspended", "deleted"]
LogLevel = Literal["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

# ❌ Avoid - don't use Enum in SPI layer
from enum import Enum
class UserStatus(Enum):  # Breaks SPI purity
    ACTIVE = "active"
    INACTIVE = "inactive"
```

#### Constrain Generic Types

```python
# ✅ Good - constrained generic types
ContextValue = str | int | float | bool | list[str] | dict[str, str]
WorkflowData = Union[str, int, float, bool, list[str], dict[str, Union[str, int, float, bool]]]

# ❌ Bad - unconstrained generic types defeat type safety
ConfigValue = Any  # Too permissive
```

#### Use Forward References

```python
# ✅ Good - forward references prevent circular imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from omnibase_spi.protocols.types.user_types import User

@runtime_checkable
class ProtocolUserService(Protocol):
    async def get_user(self, user_id: UUID) -> Optional["User"]: ...

# ❌ Bad - direct imports can cause circular dependencies
from omnibase_spi.protocols.types.user_types import User  # May cause issues
```

### Error Handling Guidelines

```python
# ✅ Good - specific error types with context
@runtime_checkable
class ProtocolUserService(Protocol):
    async def create_user(self, email: str, name: str) -> "User":
        """
        Create a new user.

        Raises:
            ValueError: If email format is invalid or already exists
            ValidationError: If name is empty or contains invalid characters  
            RuntimeError: If database operation fails
        """
        ...

# ✅ Good - comprehensive error information protocol
class ProtocolErrorInfo(Protocol):
    error_type: str           # Classification of error
    message: str              # Human-readable message
    error_code: str           # Machine-readable code
    retryable: bool           # Whether operation can be retried
    context: dict[str, ContextValue]  # Additional error context
```

## Validation and Testing

### SPI Purity Validation

#### Namespace Isolation Rules

```python
# ✅ ALLOWED - SPI-only imports
from omnibase_spi.protocols.core import ProtocolLogger
from omnibase_spi.protocols.types.core_types import LogLevel, ContextValue

# ✅ ALLOWED - Standard library and typing
from typing import Protocol, Optional, runtime_checkable
from uuid import UUID
from datetime import datetime

# ✅ ALLOWED - Forward references with TYPE_CHECKING
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from omnibase_spi.protocols.types.workflow_types import WorkflowState

# ❌ FORBIDDEN - Implementation library imports
import redis                  # External implementation
import sqlalchemy            # Database implementation  
from omnibase_spi.core import Logger  # Implementation package

# ❌ FORBIDDEN - Concrete implementations
class ConcreteUserService:   # Implementation, not protocol
    pass

# ❌ FORBIDDEN - Hardcoded configurations
DEFAULT_TIMEOUT = 30         # Configuration belongs in implementation
```

#### Protocol Compliance Rules

```python
# ✅ Good - pure protocol definition
@runtime_checkable
class ProtocolCacheService(Protocol):
    """Cache service protocol with abstract methods only."""

    async def get(self, key: str) -> Optional[Any]:
        """Get cached value."""
        ...  # Only '...' allowed in protocol methods

    async def set(self, key: str, value: Any, ttl_seconds: int) -> bool:
        """Set cached value with TTL."""
        ...

# ❌ Bad - protocol with implementation
@runtime_checkable
class ProtocolCacheService(Protocol):
    """Don't include implementation in protocols."""

    def __init__(self):        # ❌ No __init__ in protocols
        self.cache = {}

    async def get(self, key: str) -> Optional[Any]:
        # ❌ No implementation code in protocols
        return self.cache.get(key)
```

### Testing Requirements

#### Protocol Compliance Tests

```python
# Create abstract test suites for protocol compliance
from abc import ABC
import pytest

class UserServiceComplianceTests(ABC):
    """Abstract test suite for user service protocol compliance."""

    @pytest.fixture
    def user_service(self) -> ProtocolUserService:
        """Override in subclasses to provide implementation."""
        raise NotImplementedError

    @pytest.mark.asyncio
    async def test_create_user_success(self, user_service: ProtocolUserService):
        """Test successful user creation."""
        user = await user_service.create_user("test@example.com", "Test User")

        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.id is not None
        assert isinstance(user.id, UUID)

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, user_service: ProtocolUserService):
        """Test duplicate email handling."""
        await user_service.create_user("test@example.com", "First User")

        with pytest.raises(ValueError, match="already exists"):
            await user_service.create_user("test@example.com", "Second User")

    @pytest.mark.asyncio
    async def test_get_user_nonexistent(self, user_service: ProtocolUserService):
        """Test retrieving non-existent user."""
        result = await user_service.get_user(uuid4())
        assert result is None

# Concrete implementations extend the abstract tests  
class TestInMemoryUserService(UserServiceComplianceTests):
    @pytest.fixture
    def user_service(self):
        return InMemoryUserService()

class TestDatabaseUserService(UserServiceComplianceTests):
    @pytest.fixture
    def user_service(self):
        return DatabaseUserService(connection_string="sqlite:///:memory:")
```

#### Protocol Import Tests

```python
# Test that protocols can be imported without implementation dependencies
def test_protocol_imports_no_implementation_dependencies():
    """Verify protocols don't import implementation packages."""
    # This test should pass if SPI purity is maintained
    from omnibase_spi.protocols.core import ProtocolLogger
    from omnibase_spi.protocols.workflow_orchestration import ProtocolWorkflowEventBus
    from omnibase_spi.protocols.mcp import ProtocolMCPRegistry

    # Verify protocols are runtime checkable
    assert hasattr(ProtocolLogger, '__runtime_checkable__')
    assert hasattr(ProtocolWorkflowEventBus, '__runtime_checkable__')
    assert hasattr(ProtocolMCPRegistry, '__runtime_checkable__')

def test_type_definitions_are_importable():
    """Verify type definitions can be imported."""
    from omnibase_spi.protocols.types.core_types import LogLevel, ContextValue
    from omnibase_spi.protocols.types.workflow_orchestration_types import WorkflowState
    from omnibase_spi.protocols.types.mcp_types import MCPToolType

    # Verify type constraints work
    assert "INFO" in LogLevel.__args__
    assert str in ContextValue.__args__
```

### Continuous Integration

#### Pre-commit Hooks

The project uses pre-commit hooks to ensure code quality:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: spi-purity-validation
        name: Validate SPI purity
        entry: poetry run python scripts/ast_spi_validator.py
        language: system
        pass_filenames: false

      - id: namespace-isolation
        name: Check namespace isolation
        entry: ./scripts/validate-namespace-isolation.sh
        language: system
        pass_filenames: false

      - id: mypy-type-checking
        name: mypy type checking
        entry: poetry run mypy src/ --strict
        language: system
        pass_filenames: false
```

#### GitHub Actions

```yaml
# .github/workflows/validation.yml
name: SPI Validation

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install Poetry
        uses: snok/install-poetry@v1

      - name: Install dependencies
        run: poetry install --with dev

      - name: Validate SPI purity
        run: |
          poetry run python scripts/ast_spi_validator.py
          ./scripts/validate-namespace-isolation.sh

      - name: Type checking
        run: poetry run mypy src/ --strict

      - name: Run tests
        run: poetry run pytest
```

## Documentation Standards

### Protocol Documentation

Every protocol must include:

1. **Clear Purpose Statement**
2. **Key Features List**
3. **Usage Example**
4. **Method Documentation with Args/Returns/Raises**

```python
@runtime_checkable
class ProtocolExampleService(Protocol):
    """
    Clear one-line description of the protocol's purpose.

    More detailed description explaining when and how to use this protocol.
    Include context about the problem it solves and integration patterns.

    Key Features:
        - **Feature 1**: Brief description of capability
        - **Feature 2**: Brief description of capability
        - **Feature 3**: Brief description of capability

    Example:
        ```python
        async def use_example_service(service: ProtocolExampleService):
            # Show typical usage pattern
            result = await service.primary_method("example_input")

            # Show error handling  
            try:
                await service.method_that_might_fail("input")
            except ValueError as e:
                print(f"Expected error: {e}")
        ```
    """

    async def primary_method(self, input_param: str) -> "ResultType":
        """
        Brief description of what this method does.

        More detailed description if needed, including any important
        behavioral notes, side effects, or performance considerations.

        Args:
            input_param: Description of the parameter, including
                constraints, expected format, or validation rules

        Returns:
            Description of the return value, including its structure
            and any important properties

        Raises:
            ValueError: When input_param is invalid or empty
            RuntimeError: When external service is unavailable
            TimeoutError: When operation exceeds configured timeout
        """
        ...
```

### API Reference Updates

When adding new protocols:

1. **Add to API Reference**: Create or update the appropriate API reference file
2. **Update README**: Add protocol to the main API reference README
3. **Cross-Reference**: Link from related protocols and types

### Code Examples

All examples must:

1. **Be Executable**: Examples should work as written
2. **Show Error Handling**: Demonstrate proper error handling
3. **Include Context**: Show realistic usage scenarios
4. **Follow Best Practices**: Demonstrate recommended patterns

## Code Review Process

### Review Checklist

#### SPI Purity
- [ ] No implementation imports in protocol files
- [ ] No concrete implementations in protocol layer
- [ ] No hardcoded configurations or defaults
- [ ] Proper namespace isolation maintained
- [ ] All protocols are `@runtime_checkable`

#### Type Safety
- [ ] All methods have proper type annotations
- [ ] No `Any` types in public interfaces
- [ ] Forward references used for circular dependencies
- [ ] Literal types used instead of Enums
- [ ] Generic types are properly constrained

#### Documentation
- [ ] All protocols have comprehensive docstrings
- [ ] Method documentation includes Args/Returns/Raises
- [ ] Usage examples are provided and tested
- [ ] API reference documentation updated

#### Testing
- [ ] Protocol compliance tests added
- [ ] Import tests pass
- [ ] All validation tools pass
- [ ] Test coverage is adequate

### Review Process

1. **Automated Checks**: CI must pass before review
2. **Peer Review**: At least one team member review required
3. **Maintainer Approval**: Core maintainer final approval
4. **Documentation Check**: Ensure documentation is complete
5. **Integration Test**: Verify changes work with implementations

### Common Review Comments

#### Type Safety Issues
```python
# ❌ Reviewer comment: "Use specific types instead of Any"
async def process_data(self, data: Any) -> Any:

# ✅ Resolution: Use constrained types
async def process_workflow_data(
    self, data: dict[str, ContextValue]
) -> WorkflowState:
```

#### Missing Documentation
```python
# ❌ Reviewer comment: "Missing comprehensive documentation"
class ProtocolNewService(Protocol):
    async def do_something(self) -> bool: ...

# ✅ Resolution: Add complete documentation
@runtime_checkable
class ProtocolNewService(Protocol):
    """
    Service for handling new functionality.

    Provides capabilities for X, Y, and Z with proper error handling
    and comprehensive validation.

    Key Features:
        - **Feature X**: Description
        - **Feature Y**: Description

    Example:
        ```python
        async def use_service(service: ProtocolNewService):
            result = await service.do_something()
        ```
    """

    async def do_something(self) -> bool:
        """
        Perform the primary operation.

        Returns:
            True if operation succeeded

        Raises:
            ValueError: If preconditions not met
        """
        ...
```

## Release Process

### Versioning

Follow semantic versioning (SemVer):

- **MAJOR**: Breaking changes to protocol interfaces
- **MINOR**: New protocols or backward-compatible additions
- **PATCH**: Bug fixes and documentation updates

### Release Steps

1. **Update Version**: Update version in `pyproject.toml`
2. **Update Changelog**: Document all changes
3. **Create Release Branch**: `release/v1.2.3`
4. **Final Testing**: Comprehensive validation
5. **Tag Release**: `git tag v1.2.3`
6. **Merge to Main**: Merge release branch
7. **Publish Package**: Publish to PyPI
8. **Update Documentation**: Deploy updated docs

### Breaking Changes

Breaking changes require:

1. **Deprecation Period**: Mark old interfaces as deprecated
2. **Migration Guide**: Provide clear migration instructions
3. **Version Compatibility**: Support multiple versions during transition
4. **Communication**: Announce breaking changes in advance

## Getting Help

### Resources

1. **Documentation**: Check existing docs first
2. **Examples**: Look at existing protocol implementations  
3. **Issues**: Search existing issues for similar questions
4. **Discussions**: Use GitHub Discussions for design questions

### Reporting Issues

When reporting issues:

1. **Search First**: Check if issue already exists
2. **Provide Context**: Include relevant environment details
3. **Minimal Reproduction**: Provide minimal code to reproduce
4. **Expected vs Actual**: Describe what you expected vs what happened

### Asking Questions

For questions:

1. **Be Specific**: Ask specific questions rather than general ones
2. **Show Code**: Include relevant code snippets
3. **Explain Context**: Describe what you're trying to achieve
4. **Share Research**: Show what you've already tried

## Recognition

Contributors are recognized through:

- **Contributor List**: Listed in project documentation
- **Release Notes**: Mentioned in release acknowledgments  
- **Code Attribution**: Git history provides full attribution
- **Special Recognition**: Outstanding contributions highlighted

---

Thank you for contributing to omnibase-spi! Your contributions help build a robust, type-safe foundation for the ONEX ecosystem.
