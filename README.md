# ONEX Service Provider Interface (omnibase-spi)

Pure protocol interfaces for the ONEX framework with zero implementation dependencies.

## Overview

This repository contains all protocol definitions that define the contracts for ONEX services. These protocols enable duck typing and dependency injection without requiring concrete implementations.

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

### 2. Create Python Packaging
Create `pyproject.toml`:
```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "omnibase-spi"
version = "0.1.0"
description = "ONEX Service Provider Interface - Protocol definitions"
authors = [{name = "OmniNode Team", email = "team@omninode.ai"}]
license = {text = "MIT"}
requires-python = ">=3.11"
dependencies = [
    "typing-extensions>=4.5.0",
]

[project.optional-dependencies]
dev = [
    "mypy>=1.0.0",
    "black>=23.0.0",
    "isort>=5.12.0",
]

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-dir]
"" = "src"
```

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

### 4. Set Up Development Environment
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .[dev]
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
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.0
    hooks:
      - id: mypy
```

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
    from omnibase.model.core.model_node_metadata import NodeMetadataBlock

def process(self, block: "NodeMetadataBlock") -> str: ...

# Bad: Direct import creates dependency
from omnibase.model.core.model_node_metadata import NodeMetadataBlock
```

## Integration with omnibase-core

This repository provides the protocol contracts that `omnibase-core` implements:

```python
# In omnibase-core implementations
from omnibase.protocols.event_bus.protocol_event_bus import ProtocolEventBus

class EventBusImplementation(ProtocolEventBus):
    """Concrete implementation of the protocol."""
    pass
```

## Testing Protocols

Protocols should be validated through:
1. **Type checking**: `mypy src/`
2. **Import testing**: Ensure no circular dependencies
3. **Contract validation**: Verify protocol completeness

## Next Steps

1. **Complete packaging setup** (pyproject.toml, __init__.py files)
2. **Initialize git repository** and commit initial state
3. **Set up CI/CD pipeline** for type checking and validation
4. **Create protocol documentation** with usage examples
5. **Establish release process** for protocol versioning

## Dependencies

This repository has **zero runtime dependencies** by design. The only dependencies are:
- `typing-extensions` for modern typing features
- Development tools (mypy, black, isort) for code quality

## Protocol Categories

- **Core Protocols**: System-level contracts (serialization, schema loading, workflow)
- **Event Bus Protocols**: Event-driven architecture contracts
- **Container Protocols**: Dependency injection contracts  
- **Discovery Protocols**: Service and handler discovery contracts
- **File Handling Protocols**: File processing and writing contracts

This repository serves as the foundation for the entire ONEX ecosystem's type safety and architectural contracts.