# Task Completion Checklist: omnibase-spi

## Code Quality Validation (MANDATORY)
```bash
# 1. Type checking with strict MyPy
poetry run mypy src/
# Must pass with no errors

# 2. Code formatting check
poetry run black --check src/ tests/
# Must show "All done!"

# 3. Import sorting check  
poetry run isort --check-only src/ tests/
# Must pass with no changes needed

# 4. Run all tests
poetry run pytest
# All tests must pass
```

## Namespace Isolation Validation (CRITICAL)
```bash
# 5. Validate namespace isolation
./scripts/validate-namespace-isolation.sh
# Must pass all checks:
# ✅ No external omnibase imports
# ✅ Protocol naming conventions
# ✅ Namespace isolation tests pass

# 6. Manual namespace check
grep -r "from omnibase\." src/ | grep -v "from omnibase_spi.protocols"
# Must return NO results

# 7. Check for forbidden imports
grep -r "from omnibase\.core\|from omnibase\.model" src/
# Must return NO results
```

## Protocol Validation
```bash
# 8. Verify protocol completeness
python -c "from omnibase_spi.protocols import *; print('Import successful')"
# Must import without errors

# 9. Check protocol naming
grep -r "^class Protocol" src/ --include="*.py" | wc -l
# Should match expected protocol count

# 10. Validate strong typing (minimize Any usage)
grep -r "Any" src/ --include="*.py" | wc -l
# Should be minimal (prefer specific types)
```

## Documentation Updates (When Applicable)
```bash
# 11. Update version in pyproject.toml if needed
# Semantic versioning: MAJOR.MINOR.PATCH

# 12. Update CHANGELOG.md if it exists
# Document breaking changes, new features, fixes

# 13. Update README.md if protocol structure changed
# Keep examples and structure documentation current
```

## Pre-Commit Validation
```bash
# 14. Run all pre-commit hooks
poetry run pre-commit run --all-files
# All hooks must pass

# 15. Test pre-push validation
poetry run pre-commit run --hook-stage pre-push --all-files
# Must pass namespace isolation checks
```

## Build Validation (For Releases)
```bash
# 16. Build package successfully
poetry build
# Must create both .tar.gz and .whl files

# 17. Test installation
pip install dist/omnibase_spi-*.whl
python -c "import omnibase_spi.protocols; print('Package works')"
pip uninstall omnibase-spi -y
```

## Git Best Practices
```bash
# 18. Clean git status
git status
# Should show only intended changes

# 19. Descriptive commit message
git commit -m "feat: add new protocol for XYZ functionality

- Add ProtocolXYZ for handling XYZ operations
- Include comprehensive type annotations  
- Maintain namespace isolation
- Add tests for import validation"

# 20. Push with validation
git push origin branch-name
# Pre-push hooks will validate automatically
```

## CRITICAL FAILURE CONDITIONS
**Task MUST be marked as FAILED if:**
- ❌ MyPy type checking fails
- ❌ Namespace isolation validation fails  
- ❌ External omnibase imports found
- ❌ Tests fail
- ❌ Pre-commit hooks fail
- ❌ Protocol naming conventions violated
- ❌ Package cannot be imported cleanly

## SUCCESS CRITERIA
**Task can be marked as COMPLETE when:**
- ✅ All type checking passes
- ✅ All tests pass
- ✅ Namespace isolation maintained
- ✅ Code formatting compliant
- ✅ Protocol naming conventions followed
- ✅ No external dependencies introduced
- ✅ Pre-commit hooks pass
- ✅ Package builds successfully
- ✅ Clean import validation