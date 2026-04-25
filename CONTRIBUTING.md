# Contributing

Start with the repo-local guide at [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md).

For most changes:

```bash
uv sync --group dev
uv run pytest
uv run mypy src/ --strict
uv run ruff check src/ tests/
python scripts/validation/run_all_validations.py
pre-commit run --all-files
```

Before adding a protocol, read
[Dependency Direction](docs/architecture/DEPENDENCY-DIRECTION.md). The most
important rule is that SPI may import Core models and types, but Core must not
import SPI and SPI must not import implementation repos.
