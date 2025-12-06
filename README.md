# ONEX Service Provider Interface (omnibase_spi)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](https://mypy.readthedocs.io/)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Protocols](https://img.shields.io/badge/protocols-165-green.svg)](https://github.com/OmniNode-ai/omnibase_spi)
[![Domains](https://img.shields.io/badge/domains-22-blue.svg)](https://github.com/OmniNode-ai/omnibase_spi)

> **📦 Package Renamed**: This package has been renamed from `omnibase-spi` to `omnibase_spi` to follow Python naming conventions.

**Pure protocol interfaces for the ONEX framework with zero implementation dependencies.**

## 🚀 Quick Start

```bash
# Install the package
pip install omnibase-spi

# Or with poetry
poetry add omnibase-spi
```

## 📖 Documentation

- **[Complete Documentation](docs/README.md)** - Comprehensive protocol documentation
- **[API Reference](docs/api-reference/README.md)** - All 165 protocols across 22 domains
- **[Protocol Sequence Diagrams](docs/PROTOCOL_SEQUENCE_DIAGRAMS.md)** - Interaction patterns for Handler and EventBus protocols
- **[Quick Start Guide](docs/quick-start.md)** - Get started in minutes
- **[Developer Guide](docs/developer-guide/README.md)** - Development workflow and best practices
- **[Changelog](CHANGELOG.md)** - Version history and release notes

## 🌟 Overview

This repository contains all protocol definitions that define the contracts for ONEX services. These protocols enable duck typing and dependency injection without requiring concrete implementations.

## 🏗️ Architecture

The ONEX SPI follows a **protocol-first design** with **165 protocol files** across **22 specialized domains**:

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

## 🔧 Key Features

- **Zero Implementation Dependencies** - Pure protocol contracts only
- **Runtime Type Safety** - Full `@runtime_checkable` protocol support
- **Dependency Injection** - Sophisticated service lifecycle management
- **Event-Driven Architecture** - Event sourcing and workflow orchestration
- **Multi-Subsystem Coordination** - MCP integration and distributed tooling
- **Enterprise Features** - Health monitoring, metrics, circuit breakers, and more

## Architecture Principles

- **Zero Dependencies**: No implementation dependencies, only typing imports
- **Protocol-First Design**: All services defined through Python protocols
- **Domain Organization**: Protocols organized by functional domain
- **Forward References**: Uses `TYPE_CHECKING` imports to avoid circular dependencies

## Repository Structure

```
src/omnibase/
├── protocols/
│   ├── core/                    # Core system protocols
│   │   ├── protocol_canonical_serializer.py
│   │   ├── protocol_schema_loader.py
│   │   └── protocol_workflow_reducer.py
│   ├── event_bus/              # Event system protocols
│   │   ├── protocol_event_bus.py
│   │   ├── protocol_event_publisher.py
│   │   └── protocol_event_subscriber.py
│   ├── container/              # Dependency injection protocols
│   │   └── protocol_container.py
│   ├── discovery/              # Service discovery protocols
│   │   └── protocol_handler_discovery.py
│   └── file_handling/          # File processing protocols
│       ├── protocol_file_type_handler.py
│       └── protocol_file_writer.py
```

## Setup Tasks

### 1. Initialize Git Repository
```bash
cd /Volumes/PRO-G40/Code/omnibase-spi
git init
git add .
git commit -m "Initial commit: ONEX protocol interfaces"
```

### 2. Python Packaging with Poetry
The project uses Poetry for dependency management. The `pyproject.toml` is already configured with:
- Runtime dependencies: `typing-extensions`
- Development dependencies: `mypy`, `ruff`, `pre-commit`
- Package configuration for publishing

### 3. Create Package Structure
```bash
# Create __init__.py files for proper package structure
touch src/omnibase/__init__.py
touch src/omnibase/protocols/__init__.py
touch src/omnibase/protocols/core/__init__.py
touch src/omnibase/protocols/event_bus/__init__.py
touch src/omnibase/protocols/container/__init__.py
touch src/omnibase/protocols/discovery/__init__.py
touch src/omnibase/protocols/file_handling/__init__.py
```

### 4. Set Up Development Environment with Poetry
```bash
# Install dependencies and create virtual environment
poetry install

# Activate virtual environment (optional - poetry run handles this)
poetry shell

# Install pre-commit hooks (includes SPI validation)
poetry run pre-commit install

# Install pre-push hooks for namespace validation
poetry run pre-commit install --hook-type pre-push -c .pre-commit-config-push.yaml

# Test pre-commit hooks
poetry run pre-commit run --all-files
```

### 5. Configure Type Checking
Create `.mypy.ini`:
```ini
[mypy]
python_version = 3.11
strict = True
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
```

### 6. Configure Code Formatting
Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: local
    hooks:
      - id: ruff-format
        name: ruff format
        entry: poetry run ruff format
        language: system
        types: [python]
      - id: ruff-fix
        name: ruff check
        entry: poetry run ruff check --fix
        language: system
        types: [python]
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.0
    hooks:
      - id: mypy
```

## Namespace Isolation & Validation

### Critical: Complete Namespace Isolation
This SPI package maintains **complete namespace isolation** to prevent circular dependencies when installed by omnibase-core. All imports must use `omnibase_spi.protocols.*` paths only.

### Validation Tools

#### 1. Comprehensive SPI Protocol Validation
The repository includes a comprehensive validation framework with configurable rules:

```bash
# Run comprehensive validation with default configuration
python scripts/validation/comprehensive_spi_validator.py src/

# Run with custom configuration file
python scripts/validation/comprehensive_spi_validator.py src/ --config validation_config.yaml

# Apply automatic fixes for supported violations
python scripts/validation/comprehensive_spi_validator.py src/ --fix

# Generate JSON report for CI/CD integration
python scripts/validation/comprehensive_spi_validator.py src/ --json-report

# Pre-commit integration mode (faster)
python scripts/validation/comprehensive_spi_validator.py --pre-commit
```

**Validation Rules** (16 comprehensive rules):
- **SPI001**: No Protocol `__init__` methods
- **SPI002**: Protocol naming conventions  
- **SPI003**: `@runtime_checkable` decorator enforcement
- **SPI004**: Protocol method bodies (ellipsis only)
- **SPI005**: Async I/O operations
- **SPI006**: Proper Callable types
- **SPI007**: No concrete classes in SPI
- **SPI008**: No standalone functions
- **SPI009**: ContextValue usage patterns
- **SPI010**: Duplicate protocol detection
- **SPI011**: Protocol name conflicts
- **SPI012**: Namespace isolation
- **SPI013**: Forward reference typing
- **SPI014**: Protocol documentation
- **SPI015**: Method type annotations
- **SPI016**: SPI implementation purity

**Configuration File** (`validation_config.yaml`):
- Customize rule severity levels (error/warning/info)
- Enable/disable specific rules
- Environment-specific overrides (pre_commit, ci_cd, development, production)
- Performance optimization settings
- Output format configuration

#### 2. Pre-Push Hook Validation
```bash
# Manual validation
./scripts/validate-namespace-isolation.sh

# Validates:
# ✅ No external omnibase imports (only omnibase_spi.protocols.* allowed)  
# ✅ Protocol naming conventions (must start with "Protocol")
# ✅ Strong typing (no Any usage)
# ✅ Namespace isolation tests pass
```

#### 2. CI/CD Validation
- **GitHub Actions**: Automatic validation on all pushes and PRs
- **Multi-Python**: Tests on Python 3.11, 3.12, 3.13
- **Isolation Testing**: Verifies package can be installed without external dependencies
- **Cross-compatibility**: Validates with strict mypy settings

#### 3. Development Checks
```bash
# Quick namespace check
grep -r "from omnibase\." src/ | grep -v "from omnibase_spi.protocols"
# Should return no results

# Run namespace isolation tests
poetry run pytest tests/test_protocol_imports.py -v

# Full validation suite
poetry run pytest && poetry build
```

### Namespace Rules
1. **✅ ALLOWED**: `from omnibase_spi.protocols.types import ...`
2. **✅ ALLOWED**: `from omnibase_spi.protocols.core import ...`  
3. **❌ FORBIDDEN**: `from omnibase_spi.model import ...`
4. **❌ FORBIDDEN**: `from omnibase_spi.core import ...`
5. **❌ FORBIDDEN**: Any imports from external omnibase modules

## Protocol Design Guidelines

### 1. Protocol Definition Pattern
```python
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from some.model import SomeModel

class ProtocolExample(Protocol):
    """Protocol description with clear contract definition."""

    def method_name(self, param: str) -> "SomeModel":
        """Method documentation with clear expectations."""
        ...
```

### 2. Zero Implementation Rule
- Never import concrete implementations
- Use `TYPE_CHECKING` imports for model types
- All methods must be abstract (`...` body)

### 3. Forward Reference Pattern
```python
# Good: Forward reference with TYPE_CHECKING
if TYPE_CHECKING:
    from omnibase_spi.model.core.model_node_metadata import NodeMetadataBlock

def process(self, block: "NodeMetadataBlock") -> str: ...

# Bad: Direct import creates dependency
from omnibase_spi.model.core.model_node_metadata import NodeMetadataBlock
```

## Integration with omnibase-core

This repository provides the protocol contracts that `omnibase-infra` implements:

```python
# In omnibase-infra implementations
from omnibase_core.protocols.event_bus import ProtocolEventBus
from omnibase_spi.protocols.event_bus import ProtocolEventBusProvider

class EventBusImplementation(ProtocolEventBus):
    """Concrete implementation of the event bus interface (defined in Core)."""
    pass

class EventBusProviderImplementation(ProtocolEventBusProvider):
    """Factory for creating event bus instances (defined in SPI)."""
    async def get_event_bus(self, environment=None, group=None) -> ProtocolEventBus:
        return EventBusImplementation()
```

## Pre-commit Validation Hooks

The repository includes comprehensive pre-commit hooks adapted from omnibase_core for SPI-specific validation:

### Core SPI Validation
- **Protocol Architecture Validation**: Ensures protocols follow SPI patterns
- **Protocol Duplicate Detection**: Prevents duplicate protocol definitions
- **Namespace Isolation**: Validates strict SPI namespace boundaries
- **SPI Purity**: Ensures only protocol definitions (no implementations)

### Enhanced Validation (New)
- **Typing Pattern Validation**: Modern typing syntax enforcement (T | None vs Optional[T])
- **Naming Convention Validation**: SPI-specific naming patterns
- **Async-by-Default Validation**: Ensures I/O operations use async patterns
- **Callable vs Object Validation**: Prevents object type where Callable is appropriate

### Running Validation
```bash
# Run all pre-commit hooks
poetry run pre-commit run --all-files

# Run specific validation
poetry run pre-commit run validate-spi-protocols --all-files
poetry run pre-commit run validate-spi-typing-patterns --all-files
poetry run pre-commit run validate-spi-naming-conventions --all-files

# Run individual validators directly
poetry run python scripts/validation/validate_spi_protocols.py src/
poetry run python scripts/validation/validate_spi_typing_patterns.py src/
poetry run python scripts/validation/validate_spi_naming.py src/
```

## Development Workflow

### Testing Protocols
Protocols should be validated through:
1. **Type checking**: `poetry run mypy src/`
2. **Code formatting**: `poetry run ruff format src/`
3. **Linting & import sorting**: `poetry run ruff check --fix src/`
4. **Import testing**: Ensure no circular dependencies
5. **Contract validation**: Verify protocol completeness

### Using the Package
Install from source:
```bash
# Install from local source
pip install /path/to/omnibase-spi

# Or install in development mode
pip install -e /path/to/omnibase-spi
```

Import protocols in other packages:
```python
# Interface protocols from Core
from omnibase_core.protocols.event_bus import ProtocolEventBus, ProtocolEventBusHeaders

# Factory protocols from SPI
from omnibase_spi.protocols.event_bus import ProtocolEventBusProvider

# Other SPI protocols
from omnibase_spi.protocols.core.protocol_canonical_serializer import ProtocolCanonicalSerializer
```

## Next Steps

1. **Complete packaging setup** (pyproject.toml, __init__.py files)
2. **Initialize git repository** and commit initial state
3. **Set up CI/CD pipeline** for type checking and validation
4. **Create protocol documentation** with usage examples
5. **Establish release process** for protocol versioning

## Dependencies

This repository has **zero runtime dependencies** by design. The only dependencies are:
- `typing-extensions` for modern typing features
- Development tools (mypy, ruff) for code quality

## Protocol Categories

- **Core Protocols**: System-level contracts (serialization, schema loading, workflow)
- **Event Bus Protocols**: Event-driven architecture contracts
- **Container Protocols**: Dependency injection contracts  
- **Discovery Protocols**: Service and handler discovery contracts
- **File Handling Protocols**: File processing and writing contracts

This repository serves as the foundation for the entire ONEX ecosystem's type safety and architectural contracts.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/contributing.md) for development guidelines and validation requirements.

### Development Setup
```bash
# Clone the repository
git clone https://github.com/OmniNode-ai/omnibase_spi.git
cd omnibase_spi

# Install dependencies
poetry install

# Run validation
poetry run pre-commit run --all-files
```

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

The MIT License is a permissive open source license that allows you to:
- ✅ Use the software for any purpose
- ✅ Modify and distribute the software
- ✅ Include the software in proprietary applications
- ✅ Distribute copies of the software

## 🌟 Open Source

This project is **completely open source** and community-driven. We believe in:

- **Transparency** - All development happens in the open
- **Community** - Contributions from developers worldwide
- **Quality** - Rigorous testing and validation standards
- **Innovation** - Cutting-edge protocol design patterns

## 📞 Support

- **Documentation**: [Complete Documentation](docs/README.md)
- **Issues**: [GitHub Issues](https://github.com/OmniNode-ai/omnibase_spi/issues)
- **Discussions**: [GitHub Discussions](https://github.com/OmniNode-ai/omnibase_spi/discussions)
- **Email**: team@omninode.ai

---

**Made with ❤️ by the OmniNode Team**
