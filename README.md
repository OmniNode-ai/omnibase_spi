# ONEX Service Provider Interface (omnibase_spi)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](https://mypy.readthedocs.io/)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Protocols](https://img.shields.io/badge/protocols-176+-green.svg)](https://github.com/OmniNode-ai/omnibase_spi)
[![Domains](https://img.shields.io/badge/domains-22-blue.svg)](https://github.com/OmniNode-ai/omnibase_spi)

**Pure protocol interfaces for the ONEX framework with zero implementation dependencies.**

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

## v0.3.0 Highlights

- **Node Protocols**: Complete node type hierarchy with `ProtocolNode`, `ProtocolComputeNode`, `ProtocolEffectNode`, `ProtocolReducerNode`, and `ProtocolOrchestratorNode`
- **Handler Protocol**: `ProtocolHandler` with full lifecycle management (initialize, execute, shutdown)
- **Contract Compilers**: Effect, Workflow, and FSM contract compilation protocols
- **Handler Registry**: `ProtocolHandlerRegistry` for dependency injection and handler lookup
- **Exception Hierarchy**: Structured `SPIError` base with specialized subclasses
- **176+ Protocols**: Comprehensive coverage across 22 specialized domains

## Architecture

```
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

**Dependency Rules**:
- SPI -> Core: **allowed** (runtime imports of models and contract types)
- Core -> SPI: **forbidden** (no imports)
- SPI -> Infra: **forbidden** (no imports, even transitively)
- Infra -> SPI + Core: **expected** (implements behavior)

## Repository Structure

```
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
|   +-- [18 more domains]
+-- exceptions.py            # SPIError hierarchy
+-- py.typed                 # PEP 561 marker
```

## Protocol Overview

The ONEX SPI provides **176+ protocols** across **22 specialized domains**:

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
| Plus 12 more domains | 72+ | Validation, networking, file handling, etc. |

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

# Type checking
poetry run mypy src/

# Format code
poetry run black src/ tests/
poetry run isort src/ tests/

# Lint
poetry run ruff check src/ tests/

# Run validation
poetry run pre-commit run --all-files

# Build package
poetry build
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

We welcome contributions! Please see our [Contributing Guide](docs/contributing.md) for development guidelines.

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
- **[API Reference](docs/api-reference/README.md)** - All 176+ protocols across 22 domains
- **[Protocol Sequence Diagrams](docs/PROTOCOL_SEQUENCE_DIAGRAMS.md)** - Interaction patterns
- **[Developer Guide](docs/developer-guide/README.md)** - Development workflow and best practices
- **[Changelog](CHANGELOG.md)** - Version history and release notes

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [Complete Documentation](docs/README.md)
- **Issues**: [GitHub Issues](https://github.com/OmniNode-ai/omnibase_spi/issues)
- **Discussions**: [GitHub Discussions](https://github.com/OmniNode-ai/omnibase_spi/discussions)
- **Email**: team@omninode.ai

---

**Made with care by the OmniNode Team**
