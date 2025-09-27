# Technology Stack: omnibase-spi

## Core Technologies
- **Python**: 3.11+ (supports 3.11, 3.12, 3.13)
- **Poetry**: Dependency management and packaging
- **Pydantic**: 2.11.7+ for model validation and serialization
- **typing-extensions**: 4.5.0+ for advanced typing features

## Development Tools
- **MyPy**: 1.0.0+ for static type checking with strict settings
- **Black**: 23.0.0+ for code formatting (88 character line length)
- **isort**: 5.12.0+ for import sorting (Black profile)
- **pre-commit**: 3.0.0+ for automated code quality checks
- **pytest**: 8.4.1+ for testing and validation

## Build System
- **poetry-core**: Build backend for packaging
- **setuptools**: Not used - pure Poetry build
- **wheel**: Generated automatically by Poetry

## Type System Features
- **Protocols**: Python typing.Protocol for interface definition
- **TYPE_CHECKING**: Runtime-free forward references  
- **Literal Types**: String literal types for constants
- **Union Types**: Type unions for flexible parameters
- **Generic Types**: TypeVar for generic protocol definitions

## Validation Tools
- **Custom Scripts**: `validate-namespace-isolation.sh`, `validate-spi-purity.sh`
- **Pre-commit Hooks**: Automatic validation on commit
- **Pre-push Hooks**: Namespace isolation validation before push
- **GitHub Actions**: CI/CD with multi-Python testing

## Package Architecture
- **Zero Runtime Dependencies**: Only typing-extensions and pydantic
- **Namespace Isolation**: Complete separation from omnibase-core
- **Protocol-Only**: No concrete implementations
- **Pure Python**: No C extensions or compiled components
