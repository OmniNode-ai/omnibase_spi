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

# Run all protocol import tests
poetry run pytest tests/test_protocol_imports.py -v

# Type checking with mypy
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

# Test specific hook
poetry run pre-commit run validate-spi-purity --all-files
poetry run pre-commit run validate-namespace-isolation --all-files
```

## Testing Commands
```bash
# Run all tests
poetry run pytest

# Run specific test file
poetry run pytest tests/test_protocol_imports.py -v

# Run tests with coverage
poetry run pytest --cov=src/omnibase/protocols
```

## Build & Distribution
```bash
# Build package
poetry build

# Install package locally for testing
pip install dist/*.whl

# Test package installation in isolation
python -m venv /tmp/test-env
source /tmp/test-env/bin/activate
pip install dist/*.whl
python -c "from omnibase.protocols import ProtocolSimpleSerializer; print('Success!')"
```

## Development Workflow Commands
```bash
# Check what's changed
git status
git diff

# Add and commit (pre-commit hooks will run automatically)
git add .
git commit -m "Description of changes"

# Push (pre-push hooks will run namespace validation)
git push origin feature-branch
```

## Package Management
```bash
# Add development dependency
poetry add --group dev package-name

# Update dependencies
poetry update

# Show dependency tree
poetry show --tree

# Check for outdated packages
poetry show --outdated
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

## macOS-Specific Commands
```bash
# List files
ls -la

# Find files
find . -name "*.py" -type f

# Search in files
grep -r "pattern" src/

# Change directory
cd path/to/directory

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
from omnibase.protocols import ProtocolSimpleSerializer
external_modules = [name for name in sys.modules.keys() 
                   if name.startswith('omnibase.') and not name.startswith('omnibase.protocols')]
if external_modules:
    print(f'FAILURE: External omnibase modules loaded: {external_modules}')
    sys.exit(1)
else:
    print('SUCCESS: No external omnibase dependencies loaded!')
"
```