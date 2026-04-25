# AGENT.md -- omnibase_spi

LLM navigation guide. Points to current context sources; does not duplicate
them.

## Context

- Docs index: `docs/README.md`
- Dependency direction: `docs/architecture/DEPENDENCY-DIRECTION.md`
- Architecture: `docs/architecture/README.md`
- API reference: `docs/api-reference/README.md`
- Repo conventions: `CLAUDE.md`

## Commands

- Tests: `uv run pytest`
- Lint: `uv run ruff check src/ tests/`
- Type check: `uv run mypy src/ --strict`
- SPI validators: `python scripts/validation/run_all_validations.py`
- Empty directory check: `python scripts/validation/validate_no_empty_directories.py .`
- Pre-commit: `pre-commit run --all-files`

## Cross-Repo

- Core models and shared types: `omnibase_core`
- Implementations: `omnibase_infra` and product repos
- Evidence and definition of done: `onex_change_control`

## Rules

- Protocol-only; no concrete implementations in this repo.
- SPI may import Core models/types.
- Core must not import SPI.
- SPI must not import implementation repos.
- All public protocols should have `@runtime_checkable`.
- Protocol files should use `protocol_*.py` naming.
- Do not add ticket numbers, private repo links, or private workspace paths to
  public docs.
