# CLAUDE.md

> Shared Python, Git, and testing standards are in `~/.claude/CLAUDE.md`.

This file provides repo-local context for Claude Code when working in
`omnibase_spi`.

## Repository Overview

`omnibase_spi` is the Service Provider Interface package for ONEX. It defines
protocol contracts, selected data-only wire contracts, and SPI exceptions that
implementation repos satisfy.

## Dependency Direction

```text
Application and product repos
        |
        v
omnibase_spi  ---- imports models/types ---->  omnibase_core
        ^                                      ^
        | implements protocols                 | uses models/types
        |
omnibase_infra and other implementation repos --+
```

Rules:

- SPI -> Core: allowed and required for canonical models and shared types.
- Core -> SPI: forbidden.
- SPI -> implementation repos: forbidden.
- Implementation repos -> SPI + Core: expected.

Canonical explanation: `docs/architecture/DEPENDENCY-DIRECTION.md`.

## What SPI Contains

- Protocol definitions using Python `typing.Protocol`.
- SPI exception hierarchy in `exceptions.py`.
- Wire-format contracts in `contracts/` for selected cross-boundary payloads.
- No general domain Pydantic models in protocol modules.
- No business logic, I/O, concrete clients, state machines, or workflow
  implementations.

All public protocols should be `@runtime_checkable`.

## Commands

```bash
uv sync --group dev
uv run pytest
uv run pytest tests/path/to/test_file.py
uv run pytest tests/path/to/test_file.py::test_name -v
uv run mypy src/ --strict
uv run ruff check src/ tests/
uv run ruff format src/ tests/
python scripts/validation/run_all_validations.py
python scripts/validation/validate_namespace_isolation.py
python scripts/validation/validate_no_empty_directories.py .
pre-commit run --all-files
uv build
```

## Directory Structure

```text
src/omnibase_spi/
├── contracts/          # Narrow data-only wire contracts
├── effects/            # Effect-related public SPI helpers
├── enums/              # SPI-local enums
├── factories/          # Factory helpers
├── protocols/          # Runtime-checkable protocol domains
├── registry/           # Lightweight registry utilities
├── exceptions.py       # SPIError hierarchy
└── py.typed
```

## Protocol Requirements

Every public protocol should:

1. Inherit from `typing.Protocol`.
2. Include `@runtime_checkable`.
3. Use `...` for method and property bodies.
4. Use Core models/types when signatures need canonical shared data shapes.
5. Avoid importing implementation repos.
6. Include docstrings for public methods and properties.

```python
from typing import Protocol, runtime_checkable

from omnibase_core.types import JsonType


@runtime_checkable
class ProtocolRenderer(Protocol):
    """Boundary for a renderer implementation."""

    async def render(self, payload: JsonType) -> str:
        """Render the payload."""
        ...
```

## Cross-Repository Rules

| Rule | Status |
|------|--------|
| SPI imports Core | Allowed |
| Core imports SPI | Forbidden |
| SPI imports implementation repos | Forbidden |
| Implementation repos import SPI | Allowed |
| General domain models in protocol modules | Forbidden |
| Data-only wire contracts under `contracts/` | Allowed when narrow |

## Current Source Facts

- Package version: `0.20.5`
- Python: 3.12+
- Protocol files: 248 `protocol_*.py` files across 37 protocol domains
- Package metadata: `pyproject.toml`

## See Also

- [Docs index](docs/README.md)
- [Dependency direction](docs/architecture/DEPENDENCY-DIRECTION.md)
- [Architecture](docs/architecture/README.md)
- [API reference](docs/api-reference/README.md)
- [Developer guide](docs/developer-guide/README.md)
- [Testing guide](docs/TESTING.md)
- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)
