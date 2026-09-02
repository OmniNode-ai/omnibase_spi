# Contributing

Full documentation → https://github.com/OmniNode-ai/knowledge-base

Start with the [developer guide](https://github.com/OmniNode-ai/knowledge-base/blob/main/guides/omnibase-spi-developer-guide.md)
in the knowledge base.

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
[Dependency Direction](https://github.com/OmniNode-ai/knowledge-base/blob/main/architecture/omnibase-spi-dependency-direction.md). The most
important rule is that SPI may import Core models and types, but Core must not
import SPI and SPI must not import implementation repos.
