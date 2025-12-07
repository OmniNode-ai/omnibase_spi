# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

**omnibase_spi** is the Service Provider Interface (SPI) for the ONEX platform. It defines protocol contracts and exceptions that concrete implementations (in `omnibase_infra`) must satisfy.

## Architecture: Dependency Direction

```text
Applications (omniagent, omniintelligence)
       │  use
       ▼
omnibase_spi (protocol contracts, adapter interfaces)
       │  imports at runtime
       ▼
omnibase_core (Pydantic models, core runtime contracts)
       ▲
       │  used by
omnibase_infra (handlers, I/O implementations)
```

**Key Rules**:
- SPI → Core: **allowed and required** (runtime imports of models and contract types)
- Core → SPI: **forbidden** (no imports)
- SPI → Infra: **forbidden** (no imports, even transitively)
- Infra → SPI + Core: **expected** (implements behavior)

## What SPI Contains

- **Protocol definitions** using Python `typing.Protocol`
- **Exception hierarchy** (`SPIError` and subclasses)
- **No Pydantic models** (those live in `omnibase_core`)
- **No business logic or I/O**
- **No state machines or workflow implementations**

All public protocols must be `@runtime_checkable`.

## Development Commands

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

## Directory Structure

```text
src/omnibase_spi/
├── protocols/
│   ├── nodes/           # ProtocolNode, ProtocolComputeNode, ProtocolEffectNode, etc.
│   │   └── legacy/      # Deprecated protocols (removal in v0.5.0)
│   ├── contracts/       # Contract compiler protocols
│   ├── handlers/        # ProtocolHandler and domain-specific handlers
│   ├── registry/        # ProtocolHandlerRegistry
│   ├── container/       # Service registry, DI protocols
│   ├── workflow_orchestration/  # Workflow protocols
│   ├── event_bus/       # Event bus protocols
│   ├── mcp/             # MCP integration protocols
│   └── [22 more domains]
├── exceptions.py        # SPIError hierarchy
└── py.typed
```

## Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Node protocols | `Protocol{Type}Node` | `ProtocolComputeNode` |
| Compiler protocols | `Protocol{Type}ContractCompiler` | `ProtocolEffectContractCompiler` |
| Handler protocols | `Protocol{Type}Handler` | `ProtocolHandler` |
| Exceptions | `{Type}Error` | `SPIError`, `RegistryError` |

## Protocol Requirements

Every protocol must:
1. Inherit from `typing.Protocol`
2. Have `@runtime_checkable` decorator
3. Use `...` (ellipsis) for method bodies
4. Import Core models for type hints (allowed at runtime)
5. Have docstrings with Args/Returns/Raises

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

## Cross-Repository Contract Rules

| Rule | Enforcement |
|------|-------------|
| SPI imports Core | Allowed at runtime |
| Core MUST NOT import SPI | CI failure |
| SPI MUST NOT define Pydantic models | All `BaseModel` in Core |
| SPI MUST NOT import Infra | CI failure |
| Circular imports | CI failure |

## Version Information

- **Current Version**: 0.3.0
- **Python Support**: 3.12+
- **Protocol Count**: 176+ protocols across 22 domains

## Validation Scripts

Standalone validators (Python stdlib only, no omnibase_core imports):

| Script | Purpose | Pre-commit Stage |
|--------|---------|------------------|
| `validate_naming_patterns.py` | Protocol/Error naming, `@runtime_checkable` | `pre-commit` |
| `validate_namespace_isolation.py` | No Infra imports, no Pydantic models | `pre-commit` |
| `validate_architecture.py` | One-protocol-per-file rule | `manual` (92 existing violations) |
| `run_all_validations.py` | Unified runner with JSON output | `manual` |

These validators will be replaced by `omnibase_core.validation` once the circular dependency is resolved.

## Key Documentation

- `docs/MVP_PLAN.md` - v0.3.0 work breakdown and architecture
- `docs/VALIDATION_INTEGRATION_PLAN.md` - Validation integration with omnibase_core

## See Also

- **[docs/README.md](docs/README.md)** - Complete documentation hub
- **[docs/api-reference/README.md](docs/api-reference/README.md)** - All 176+ protocols across 22 domains
- **[docs/GLOSSARY.md](docs/GLOSSARY.md)** - Terminology definitions (Protocol, Handler, Node, Contract)
- **[docs/QUICK-START.md](docs/QUICK-START.md)** - Get up and running quickly
- **[docs/developer-guide/README.md](docs/developer-guide/README.md)** - Development workflow
- **[docs/architecture/README.md](docs/architecture/README.md)** - Design principles and patterns
- **[docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)** - How to contribute

### v0.3.0 Core Protocols

- **[docs/api-reference/NODES.md](docs/api-reference/NODES.md)** - ProtocolNode, ProtocolComputeNode, etc.
- **[docs/api-reference/HANDLERS.md](docs/api-reference/HANDLERS.md)** - ProtocolHandler interface
- **[docs/api-reference/CONTRACTS.md](docs/api-reference/CONTRACTS.md)** - Effect, Workflow, FSM compilers
- **[docs/api-reference/REGISTRY.md](docs/api-reference/REGISTRY.md)** - ProtocolHandlerRegistry
- **[docs/api-reference/EXCEPTIONS.md](docs/api-reference/EXCEPTIONS.md)** - SPIError hierarchy

For term definitions, see the [Glossary](docs/GLOSSARY.md).
