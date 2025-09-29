# Task Completion Workflow for omnibase-spi

## Pre-Commit Checklist

### 1. Code Quality Validation
```bash
# Run complete validation suite
./scripts/validate-namespace-isolation.sh
poetry run python scripts/ast_spi_validator.py
poetry run pytest tests/test_protocol_imports.py -v
```

### 2. Type Checking and Formatting
```bash
# Type checking with mypy (strict mode)
poetry run mypy src/

# Code formatting with Black
poetry run black src/ tests/

# Import sorting with isort
poetry run isort src/ tests/

# Linting with Ruff
poetry run ruff check src/ tests/
```

### 3. Pre-commit Hook Validation
```bash
# Run all pre-commit hooks manually
poetry run pre-commit run --all-files

# If hooks fail, fix issues and re-run
# Pre-commit hooks will run automatically on git commit
```

## Development Workflow Steps

### 1. Before Starting Work
```bash
# Ensure clean state
git status
git pull origin main  # or development branch

# Activate development environment
poetry shell  # or use poetry run for individual commands
```

### 2. During Development
```bash
# Run type checking frequently
poetry run mypy src/

# Test protocol imports regularly
poetry run pytest tests/test_protocol_imports.py

# Check specific validation
poetry run python scripts/ast_spi_validator.py
```

### 3. Before Committing Changes
```bash
# Complete validation sequence
./scripts/validate-namespace-isolation.sh
poetry run python scripts/ast_spi_validator.py
poetry run mypy src/
poetry run pytest

# Format code
poetry run black src/ tests/
poetry run isort src/ tests/
```

### 4. Commit Process
```bash
# Stage changes
git add .

# Commit (pre-commit hooks run automatically)
git commit -m "descriptive commit message"

# Push (pre-push hooks validate namespace isolation)
git push origin branch-name
```

## Validation Requirements

### 1. Namespace Isolation Validation
- ✅ No external omnibase imports (only omnibase_spi.protocols.* allowed)
- ✅ All protocol imports self-contained
- ✅ No circular dependencies
- ✅ Package can be installed independently

### 2. SPI Purity Validation
- ✅ Only Protocol definitions (no concrete classes)
- ✅ No @dataclass usage (use @runtime_checkable Protocol)
- ✅ No __init__ methods in protocols
- ✅ No hardcoded default values
- ✅ No concrete method implementations
- ✅ No implementation library imports

### 3. Type System Validation
- ✅ Strict mypy compliance
- ✅ All functions have type hints
- ✅ Minimal use of Any types
- ✅ Proper forward references with TYPE_CHECKING

### 4. Code Quality Validation
- ✅ Black formatting compliance
- ✅ isort import organization
- ✅ Ruff linting compliance
- ✅ All tests passing

## Error Resolution Patterns

### 1. Namespace Isolation Violations
```bash
# Check for forbidden imports
grep -r "from omnibase\." src/ | grep -v "from omnibase_spi.protocols"

# Fix by changing to protocol imports
# WRONG: from omnibase_spi.core import SomeClass
# RIGHT: from omnibase_spi.protocols.core.protocol_name import ProtocolName
```

### 2. SPI Purity Violations
```bash
# Run AST validator to identify issues
poetry run python scripts/ast_spi_validator.py

# Common fixes:
# - Remove @dataclass, use @runtime_checkable Protocol
# - Remove __init__ methods, use @property accessors
# - Remove method implementations, use ... (ellipsis)
# - Remove implementation imports
```

### 3. Type Checking Errors
```bash
# Run mypy with verbose output
poetry run mypy src/ --show-error-codes

# Common fixes:
# - Add TYPE_CHECKING imports for forward references
# - Add return type annotations
# - Fix Any usage with specific types
# - Add proper protocol inheritance
```

### 4. Test Failures
```bash
# Run tests with verbose output
poetry run pytest tests/test_protocol_imports.py -v -s

# Common issues:
# - Protocol import failures (check namespace isolation)
# - External dependencies loaded (check imports)
# - Package structure issues (check __init__.py files)
```

## CI/CD Validation Process

### 1. GitHub Actions Checks
- **Namespace isolation validation**: Automated on PRs
- **Package build verification**: Ensures clean build
- **Installation isolation test**: Verifies no external deps
- **Documentation validation**: Checks README consistency

### 2. Local CI Simulation
```bash
# Simulate full CI pipeline locally
poetry run pytest
poetry build

# Test installation isolation (like CI does)
python -m venv /tmp/test-env
source /tmp/test-env/bin/activate
pip install dist/*.whl
python -c "
import sys
from omnibase_spi.protocols.types import LogLevel
external_modules = [name for name in sys.modules.keys()
                   if name.startswith('omnibase_spi.') and not name.startswith('omnibase_spi.protocols')]
assert len(external_modules) == 0, f'External modules: {external_modules}'
print('✅ Installation isolation test passed!')
"
```

## Definition of Done

### For Protocol Changes
- [ ] Protocol follows naming conventions (starts with "Protocol")
- [ ] Uses @runtime_checkable decorator
- [ ] All methods have ... (ellipsis) implementation
- [ ] Proper type hints with forward references
- [ ] Documentation explains protocol contract
- [ ] Namespace isolation maintained
- [ ] All validation scripts pass
- [ ] Tests updated if needed

### For Type Definition Changes  
- [ ] Uses Literal types instead of Enum
- [ ] Proper TypedDict structure
- [ ] No implementation dependencies
- [ ] Forward references use TYPE_CHECKING
- [ ] All validation scripts pass

### For Repository Changes
- [ ] pyproject.toml consistency maintained
- [ ] Pre-commit hooks updated if needed  
- [ ] CI/CD configuration validated
- [ ] Documentation updated
- [ ] Version compatibility maintained
- [ ] All tests pass locally and in CI
