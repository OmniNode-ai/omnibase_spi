# Suggested Commands: omnibase-spi

## Development Environment Setup
```bash
# Install dependencies and create virtual environment
poetry install

# Activate virtual environment (optional - poetry run handles this)
poetry shell

# Install pre-commit hooks for code quality
poetry run pre-commit install

# Install pre-push hooks for namespace validation
poetry run pre-commit install --hook-type pre-push -c .pre-commit-config-push.yaml
```

## Code Quality and Validation
```bash
# Type checking (strict MyPy configuration)
poetry run mypy src/

# Code formatting
poetry run black src/ tests/

# Import sorting
poetry run isort src/ tests/

# Run all pre-commit hooks manually
poetry run pre-commit run --all-files

# Quick namespace isolation check
grep -r "from omnibase\." src/ | grep -v "from omnibase.protocols"
# Should return no results
```

## Testing and Validation
```bash
# Run all tests
poetry run pytest

# Run namespace isolation tests specifically
poetry run pytest tests/test_protocol_imports.py -v

# Validate namespace isolation with custom script
./scripts/validate-namespace-isolation.sh

# Validate SPI purity (if script exists)
./scripts/validate-spi-purity.sh
```

## Build and Package
```bash
# Build package for distribution
poetry build

# Check package contents
tar -tzf dist/omnibase_spi-*.tar.gz | head -20

# Install locally for testing
pip install dist/omnibase_spi-*.whl

# Install in development mode
pip install -e .
```

## Git Operations
```bash
# Check current status
git status

# Add changes
git add .

# Commit with validation hooks
git commit -m "Your commit message"

# Push with namespace validation
git push origin branch-name
```

## Quick Development Workflow
```bash
# Full validation before commit
poetry run mypy src/ && \
poetry run black src/ tests/ && \
poetry run isort src/ tests/ && \
poetry run pytest && \
./scripts/validate-namespace-isolation.sh

# One-liner for quick check
poetry run pre-commit run --all-files && poetry run pytest
```

## Debugging and Analysis
```bash
# Find protocol classes
grep -r "^class Protocol" src/ --include="*.py"

# Check for Any type usage (should be minimal)
grep -r "Any" src/ --include="*.py"

# List all protocol files
find src/ -name "protocol_*.py" -type f

# Check imports in specific file
python -c "import sys; sys.path.insert(0, 'src'); import omnibase.protocols"
```

## Package Information
```bash
# Show package info
poetry show

# Show dependency tree
poetry show --tree

# Check outdated packages
poetry show --outdated

# Update dependencies
poetry update
```

## System-Specific Commands (macOS Darwin)
```bash
# Find files (macOS find)
find src/ -name "*.py" -type f | head -10

# Search with ripgrep (if available)
rg "Protocol" src/ --type py

# List directory tree
ls -la src/omnibase/protocols/

# Check Python version
python3 --version
```