# Essential Development Commands for omnibase-spi

## Initial Setup
```bash
# Clone and enter repository
cd /Volumes/PRO-G40/Code/omnibase-spi

# Install Poetry dependencies and create virtual environment
poetry install

# Install pre-commit hooks (essential for validation)
poetry run pre-commit install
poetry run pre-commit install --hook-type pre-push -c .pre-commit-config-push.yaml

# Activate virtual environment (optional - poetry run handles this)
poetry shell
```

## Code Quality & Validation Commands

### Essential Validation (run before commits)
```bash
# Complete namespace isolation validation
./scripts/validate-namespace-isolation.sh

# AST-based SPI purity validation
poetry run python scripts/ast_spi_validator.py

# Deprecated code validation
./scripts/validate-no-deprecated.sh

# Run all protocol import tests
poetry run pytest tests/test_protocol_imports.py -v

# Type checking with mypy (strict configuration)
poetry run mypy src/

# Code formatting
poetry run black src/ tests/
poetry run isort src/ tests/

# Linting
poetry run ruff check src/ tests/
```

### Pre-commit Validation
```bash
# Run all pre-commit hooks manually
poetry run pre-commit run --all-files

# Test specific hooks
poetry run pre-commit run validate-spi-purity --all-files
poetry run pre-commit run validate-namespace-isolation --all-files
poetry run pre-commit run validate-no-deprecated --all-files

# Quick namespace isolation check
grep -r "from omnibase\." src/ | grep -v "from omnibase_spi.protocols"
# Should return no results
```

## Testing Commands
```bash
# Run all tests
poetry run pytest

# Run specific test file with verbose output
poetry run pytest tests/test_protocol_imports.py -v

# Run tests with coverage
poetry run pytest --cov=src/omnibase/protocols

# Run namespace isolation tests specifically
poetry run pytest tests/test_protocol_imports.py -v

# Validate SPI purity
./scripts/validate-spi-purity.sh
```

## Build & Distribution
```bash
# Build package for distribution
poetry build

# Check package contents
tar -tzf dist/omnibase_spi-*.tar.gz | head -20

# Install locally for testing
pip install dist/omnibase_spi-*.whl

# Install in development mode
pip install -e .

# Test package installation in isolation
python -m venv /tmp/test-env
source /tmp/test-env/bin/activate
pip install dist/*.whl
python -c "from omnibase_spi.protocols.types import LogLevel; print('Success!')"
```

## Git Operations & Development Workflow
```bash
# Check current status
git status
git diff

# Add and commit (pre-commit hooks will run automatically)
git add .
git commit -m "Description of changes"

# Push with namespace validation (pre-push hooks will run)
git push origin feature-branch

# Merge main into feature branch
git fetch origin
git merge origin/main
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

## Package Management
```bash
# Show package info
poetry show

# Show dependency tree
poetry show --tree

# Check for outdated packages
poetry show --outdated

# Update dependencies
poetry update

# Add development dependency
poetry add --group dev package-name
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
python -c "import sys; sys.path.insert(0, 'src'); import omnibase_spi.protocols"
```

## Troubleshooting Commands
```bash
# Check Python version
python --version  # Should be 3.12+

# Reinstall dependencies
poetry install --no-cache

# Clear Poetry cache
poetry cache clear . --all

# Reset virtual environment
poetry env remove python
poetry install
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

# View file content
cat filename.py
head -n 20 filename.py
tail -n 10 filename.py
```

## CI/CD Validation (Local Testing)
```bash
# Simulate GitHub Actions validation locally
poetry run pytest
poetry build

# Test package installation like CI does
python -m venv /tmp/test-env
source /tmp/test-env/bin/activate
pip install dist/*.whl
python -c "
import sys
from omnibase_spi.protocols.types import LogLevel
external_modules = [name for name in sys.modules.keys()
                   if name.startswith('omnibase_spi.') and not name.startswith('omnibase_spi.protocols')]
if external_modules:
    print(f'FAILURE: External omnibase modules loaded: {external_modules}')
    sys.exit(1)
else:
    print('SUCCESS: No external omnibase dependencies loaded!')
"
```
