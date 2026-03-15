# AGENT.md -- omnibase_spi

> LLM navigation guide. Points to context sources -- does not duplicate them.

## Context

- **Protocol catalog**: `docs/api-reference/REGISTRY.md`
- **Architecture**: `docs/architecture/`
- **Conventions**: `CLAUDE.md`

## Commands

- Tests: `uv run pytest -m unit`
- Lint: `uv run ruff check src/ tests/`
- Type check: `uv run mypy src/ --strict`
- Pre-commit: `pre-commit run --all-files`

## Cross-Repo

- Shared platform standards: `~/.claude/CLAUDE.md`
- Core implementations: `omnibase_core/CLAUDE.md`

## Rules

- Protocol-only -- no concrete implementations in this repo
- All protocols must have `@runtime_checkable` decorator
- Single protocol per file, matching `protocol_*.py` naming
