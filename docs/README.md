# omnibase_spi Docs

This is the documentation index for `omnibase_spi`, the ONEX protocol contract
package.

Use this index to decide where to start, which docs are current, and where each
kind of repo truth belongs.

## Start Here

| Need | Start With |
|------|------------|
| Understand the repo role | [Repository README](../README.md) |
| Understand the import graph | [Dependency Direction](architecture/DEPENDENCY-DIRECTION.md) |
| Add or change a protocol | [Developer Guide](developer-guide/README.md) |
| Find protocol domains | [API Reference](api-reference/README.md) |
| Validate changes | [Testing Guide](TESTING.md) |
| Contribute safely | [Contributing](../CONTRIBUTING.md) |
| Report a security or compatibility issue | [Security](../SECURITY.md) |

## Current Truth Boundary

Current docs in this repo describe the package as it exists now:

- SPI owns protocol contracts, selected data-only wire contracts, and SPI
  exceptions.
- Core owns general platform models, enums, validators, and runtime-neutral data
  shapes used by protocol signatures.
- Infra and product repos own implementations.
- Historical design reviews and PR-specific analysis are not primary docs in
  this public repo. They are archived outside the public docs tree when they no
  longer describe current usage.

## Architecture

- [Architecture Overview](architecture/README.md)
- [Dependency Direction](architecture/DEPENDENCY-DIRECTION.md)
- [Glossary](GLOSSARY.md)
- [Protocol Sequence Diagrams](PROTOCOL_SEQUENCE_DIAGRAMS.md)

## Development

- [Quick Start](QUICK-START.md)
- [Developer Guide](developer-guide/README.md)
- [Testing Guide](TESTING.md)
- [Contributing](../CONTRIBUTING.md)
- [Repo-local contributing detail](CONTRIBUTING.md)

## API Reference

- [API Reference Overview](api-reference/README.md)
- [Core Protocols](api-reference/CORE.md)
- [Container Protocols](api-reference/CONTAINER.md)
- [Workflow Orchestration](api-reference/WORKFLOW-ORCHESTRATION.md)
- [Event Bus](api-reference/EVENT-BUS.md)
- [MCP](api-reference/MCP.md)
- [Memory](api-reference/MEMORY.md)
- [Handlers](api-reference/HANDLERS.md)
- [Nodes](api-reference/NODES.md)
- [Contracts](api-reference/CONTRACTS.md)
- [Validation](api-reference/VALIDATION.md)

## Patterns And Examples

- [Protocol Composition Patterns](patterns/PROTOCOL-COMPOSITION-PATTERNS.md)
- [Protocol Selection Guide](patterns/PROTOCOL-SELECTION-GUIDE.md)
- [Examples](examples/README.md)
- [Implementation Examples](examples/IMPLEMENTATION-EXAMPLES.md)
- [Templates](templates/README.md)

## Validation Commands

```bash
uv run pytest
uv run mypy src/ --strict
uv run ruff check src/ tests/
python scripts/validation/run_all_validations.py
python scripts/validation/validate_namespace_isolation.py
python scripts/validation/validate_no_empty_directories.py .
pre-commit run --all-files
uv build
```

## Documentation Maintenance

- Keep root `README.md` and this docs index aligned on the dependency graph.
- Do not link private workspace paths or private repository URLs from public
  docs.
- Do not use ticket numbers as public documentation anchors.
- Move stale design reviews, one-time analysis, and PR-specific historical files
  out of the public docs tree after any still-current guidance has been
  promoted into stable docs.
