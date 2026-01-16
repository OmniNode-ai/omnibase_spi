# ONEX Service Provider Interface (omnibase_spi)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](https://mypy.readthedocs.io/)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Protocols](https://img.shields.io/badge/protocols-176+-green.svg)](https://github.com/OmniNode-ai/omnibase_spi)
[![Domains](https://img.shields.io/badge/domains-22-blue.svg)](https://github.com/OmniNode-ai/omnibase_spi)
[![Version](https://img.shields.io/badge/version-0.3.0-blue.svg)](https://github.com/OmniNode-ai/omnibase_spi/releases)

**Pure protocol interfaces for the ONEX framework with zero implementation dependencies.**

## Table of Contents

- [Quick Start](#quick-start)
- [V0.3.0 Highlights](#v030-highlights)
- [Architecture](#architecture)
- [Repository Structure](#repository-structure)
- [Protocol Overview](#protocol-overview)
- [Key Features](#key-features)
- [Exception Hierarchy](#exception-hierarchy)
- [Protocol Design Guidelines](#protocol-design-guidelines)
- [Development](#development)
- [Namespace Isolation](#namespace-isolation)
- [Contributing](#contributing)
- [Documentation](#documentation)
- [See Also](#see-also)
- [License](#license)
- [Support](#support)

## Quick Start

```bash
# Install with poetry
poetry add omnibase-spi

# Or with pip
pip install omnibase-spi
```

```python
# Import node protocols
from omnibase_spi.protocols.nodes import (
    ProtocolNode,
    ProtocolComputeNode,
    ProtocolEffectNode,
    ProtocolReducerNode,
    ProtocolOrchestratorNode,
)

# Import handler protocol
from omnibase_spi.protocols.handlers import ProtocolHandler

# Import registry protocol
from omnibase_spi.protocols.registry import ProtocolHandlerRegistry

# Import contract compilers
from omnibase_spi.protocols.contracts import (
    ProtocolEffectContractCompiler,
    ProtocolWorkflowContractCompiler,
    ProtocolFSMContractCompiler,
)

# Import exception hierarchy
from omnibase_spi.exceptions import (
    SPIError,
    ProtocolHandlerError,
    ContractCompilerError,
    RegistryError,
)
```

## V0.3.0 Highlights

- **Node Protocols**: Complete node type hierarchy with `ProtocolNode`, `ProtocolComputeNode`, `ProtocolEffectNode`, `ProtocolReducerNode`, and `ProtocolOrchestratorNode`
- **Handler Protocol**: `ProtocolHandler` with full lifecycle management (initialize, execute, shutdown)
- **Contract Compilers**: Effect, Workflow, and FSM contract compilation protocols
- **Handler Registry**: `ProtocolHandlerRegistry` for dependency injection and handler lookup
- **Exception Hierarchy**: Structured `SPIError` base with specialized subclasses
- **180+ Protocols**: Comprehensive coverage across 23 specialized domains

## Architecture

```text
+-----------------------------------------------------------+
|                      Applications                          |
|               (omniagent, omniintelligence)                |
+-----------------------------+-----------------------------+
                              | uses
                              v
+-----------------------------------------------------------+
|                      omnibase_spi                          |
|            (Protocol Contracts, Exceptions)                |
|  - ProtocolNode, ProtocolComputeNode, ProtocolEffectNode   |
|  - ProtocolHandler, ProtocolHandlerRegistry                |
|  - Contract Compilers (Effect, Workflow, FSM)              |
+-----------------------------+-----------------------------+
                              | imports models
                              v
+-----------------------------------------------------------+
|                      omnibase_core                         |
|             (Pydantic Models, Core Types)                  |
+-----------------------------+-----------------------------+
                              | implemented by
                              v
+-----------------------------------------------------------+
|                      omnibase_infra                        |
|          (Handler Implementations, I/O)                    |
+-----------------------------------------------------------+
```

**Related Repositories**:

- [omnibase_spi](https://github.com/OmniNode-ai/omnibase_spi) - This repository (Protocol contracts)
- [omnibase_core](https://github.com/OmniNode-ai/omnibase_core) - Pydantic models and core types
- [omnibase_infra](https://github.com/OmniNode-ai/omnibase_infra) - Concrete implementations

**Dependency Rules**:

- SPI -> Core: **allowed** (runtime imports of models and contract types)
- Core -> SPI: **forbidden** (no imports)
- SPI -> Infra: **forbidden** (no imports, even transitively)
- Infra -> SPI + Core: **expected** (implements behavior)

## Repository Structure

```text
src/omnibase_spi/
+-- protocols/
|   +-- nodes/               # Node type protocols
|   |   +-- base.py          #   ProtocolNode
|   |   +-- compute.py       #   ProtocolComputeNode
|   |   +-- effect.py        #   ProtocolEffectNode
|   |   +-- reducer.py       #   ProtocolReducerNode
|   |   +-- orchestrator.py  #   ProtocolOrchestratorNode
|   |   +-- legacy/          #   Deprecated protocols (removal in v0.5.0)
|   +-- handlers/            # Handler protocol
|   |   +-- protocol_handler.py
|   +-- contracts/           # Contract compiler protocols
|   |   +-- effect_compiler.py
|   |   +-- workflow_compiler.py
|   |   +-- fsm_compiler.py
|   +-- registry/            # Handler registry protocol
|   |   +-- handler_registry.py
|   +-- container/           # DI and service registry
|   +-- event_bus/           # Event bus protocols
|   +-- workflow_orchestration/  # Workflow protocols
|   +-- mcp/                 # MCP integration protocols
|   +-- [14 more domains]
+-- exceptions.py            # SPIError hierarchy
+-- py.typed                 # PEP 561 marker
```

## Protocol Overview

The ONEX SPI provides **180+ protocols** across **23 specialized domains**:

| Domain | Protocols | Description |
|--------|-----------|-------------|
| Nodes | 5 | Node type hierarchy (Compute, Effect, Reducer, Orchestrator) |
| Handlers | 1 | Protocol handler with lifecycle management |
| Contracts | 3 | Contract compilers (Effect, Workflow, FSM) |
| Registry | 1 | Handler registry for DI |
| Container | 21 | Dependency injection, lifecycle management |
| Event Bus | 13 | Distributed messaging infrastructure |
| Workflow Orchestration | 14 | Event-driven FSM coordination |
| MCP Integration | 15 | Multi-subsystem tool coordination |
| Memory | 15 | Workflow state persistence |
| Core System | 16 | Logging, health monitoring, error handling |
| Plus 22 more domains | 76+ | Validation, networking, file handling, etc. |

## Key Features

- **Zero Implementation Dependencies** - Pure protocol contracts only
- **Runtime Type Safety** - Full `@runtime_checkable` protocol support
- **Dependency Injection** - Sophisticated service lifecycle management
- **Event-Driven Architecture** - Event sourcing and workflow orchestration
- **Multi-Subsystem Coordination** - MCP integration and distributed tooling
- **Enterprise Features** - Health monitoring, metrics, circuit breakers

## Exception Hierarchy

```python
SPIError                          # Base exception for all SPI errors
+-- ProtocolHandlerError          # Handler execution errors
|   +-- HandlerInitializationError  # Handler failed to initialize
+-- ContractCompilerError         # Contract compilation/validation errors
+-- RegistryError                 # Handler registry operation errors
+-- ProtocolNotImplementedError   # Missing protocol implementation
+-- InvalidProtocolStateError     # Lifecycle state violations
```

## Protocol Design Guidelines

### Protocol Definition Pattern

```python
from typing import Protocol, runtime_checkable
from omnibase_core.models.compute import ModelComputeInput, ModelComputeOutput

@runtime_checkable
class ProtocolComputeNode(Protocol):
    """Compute node for pure transformations."""

    @property
    def is_deterministic(self) -> bool:
        """Whether this node produces deterministic output."""
        ...

    async def execute(self, input_data: ModelComputeInput) -> ModelComputeOutput:
        """Execute the compute operation."""
        ...
```

### Protocol Requirements

Every protocol must:

1. Inherit from `typing.Protocol`
2. Have `@runtime_checkable` decorator
3. Use `...` (ellipsis) for method bodies
4. Import Core models for type hints (allowed at runtime)
5. Have docstrings with Args/Returns/Raises

## Development

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest

# Run single test file
poetry run pytest tests/path/to/test_file.py

# Run single test
poetry run pytest tests/path/to/test_file.py::test_name -v

# Type checking
poetry run mypy src/

# Strict type checking (target for CI)
poetry run mypy src/ --strict

# Format code
poetry run black src/ tests/
poetry run isort src/ tests/

# Lint
poetry run ruff check src/ tests/

# Build package
poetry build

# Run standalone validators (stdlib only, no dependencies)
python scripts/validation/run_all_validations.py
python scripts/validation/run_all_validations.py --strict --verbose

# Individual validators
python scripts/validation/validate_naming_patterns.py src/
python scripts/validation/validate_namespace_isolation.py
python scripts/validation/validate_architecture.py --verbose

# Pre-commit hooks
pre-commit run --all-files
pre-commit run validate-naming-patterns --all-files
pre-commit run validate-namespace-isolation-new --all-files
```

## Namespace Isolation

This SPI package maintains **complete namespace isolation** to prevent circular dependencies:

| Rule | Status |
|------|--------|
| `from omnibase_spi.protocols.* import ...` | Allowed |
| `from omnibase_core.* import ...` | Allowed |
| `from omnibase_infra.* import ...` | Forbidden |
| Pydantic models in SPI | Forbidden (use Core) |

## Contributing

We welcome contributions! Please see our [Contributing Guide](docs/CONTRIBUTING.md) for development guidelines.

```bash
# Clone the repository
git clone https://github.com/OmniNode-ai/omnibase_spi.git
cd omnibase_spi

# Install dependencies
poetry install

# Run validation
poetry run pre-commit run --all-files
```

## Documentation

- **[Complete Documentation](docs/README.md)** - Comprehensive protocol documentation
- **[API Reference](docs/api-reference/README.md)** - All 180+ protocols across 23 domains
- **[Quick Start Guide](docs/QUICK-START.md)** - Get up and running in minutes
- **[Developer Guide](docs/developer-guide/README.md)** - Development workflow and best practices
- **[Architecture Overview](docs/architecture/README.md)** - Design principles and patterns
- **[Protocol Sequence Diagrams](docs/PROTOCOL_SEQUENCE_DIAGRAMS.md)** - Interaction patterns
- **[Glossary](docs/GLOSSARY.md)** - Terminology and definitions
- **[Changelog](CHANGELOG.md)** - Version history and release notes

See the [Glossary](docs/GLOSSARY.md) for definitions of SPI-specific terms like Protocol, Handler, Node, and Contract.

## See Also

- **[Contributing Guide](docs/CONTRIBUTING.md)** - How to contribute to the project
- **[MVP Plan](docs/MVP_PLAN.md)** - v0.3.0 work breakdown and architecture
- **[CLAUDE.md](CLAUDE.md)** - AI assistant guidance for working with this repository

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [Complete Documentation](docs/README.md)
- **Issues**: [GitHub Issues](https://github.com/OmniNode-ai/omnibase_spi/issues)
- **Discussions**: [GitHub Discussions](https://github.com/OmniNode-ai/omnibase_spi/discussions)
- **Email**: [team@omninode.ai](mailto:team@omninode.ai)

---

**Made with care by the OmniNode Team**
