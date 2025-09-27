# Migration Guide: omnibase-spi → omnibase_spi

This guide helps external packages migrate from the old `omnibase-spi` package name to the new `omnibase_spi` Python-compliant naming.

## Overview

The package has been renamed to follow Python naming conventions:
- **Old**: `omnibase-spi` (kebab-case, non-standard for Python)
- **New**: `omnibase_spi` (snake_case, Python standard)

**Important**: This is a **breaking change** for import paths only. All protocol interfaces and APIs remain identical.

## What Changed

### Package Name
```toml
# pyproject.toml - OLD
name = "omnibase-spi"

# pyproject.toml - NEW  
name = "omnibase_spi"
```

### Directory Structure
```
# OLD structure
src/omnibase/protocols/

# NEW structure  
src/omnibase_spi/protocols/
```

### Import Paths
All protocol imports need updating:

```python
# OLD imports ❌
from omnibase.protocols.core import ProtocolWorkflowReducer
from omnibase.protocols.types.workflow_orchestration_types import WorkflowState
from omnibase.protocols.mcp import ProtocolMCPRegistry

# NEW imports ✅
from omnibase_spi.protocols.core import ProtocolWorkflowReducer
from omnibase_spi.protocols.types.workflow_orchestration_types import WorkflowState
from omnibase_spi.protocols.mcp import ProtocolMCPRegistry
```

## Migration Steps for Downstream Packages

### Step 1: Update Dependencies

Update your `pyproject.toml` or `requirements.txt`:

```toml
# OLD dependency
dependencies = [
    "omnibase-spi>=0.1.0",
]

# NEW dependency
dependencies = [
    "omnibase_spi>=0.1.0",
]
```

### Step 2: Update Import Statements

Use find-and-replace to update all imports:

**Linux/macOS:**
```bash
# Update Python imports
find . -name "*.py" -exec sed -i 's/from omnibase\./from omnibase_spi\./g' {} \;
find . -name "*.py" -exec sed -i 's/import omnibase\./import omnibase_spi\./g' {} \;

# Update quoted references
find . -name "*.py" -exec sed -i 's/"omnibase\./"omnibase_spi\./g' {} \;
```

**Manual Updates:**
```python
# Protocol imports
from omnibase.protocols.core import ProtocolCanonicalSerializer
from omnibase_spi.protocols.core import ProtocolCanonicalSerializer

# Type imports  
from omnibase.protocols.types import LogLevel, WorkflowState
from omnibase_spi.protocols.types import LogLevel, WorkflowState

# Module imports
import omnibase.protocols.mcp as mcp
import omnibase_spi.protocols.mcp as mcp
```

### Step 3: Update Documentation

Update any documentation references:

```markdown
<!-- OLD -->
Install omnibase-spi for protocol definitions
Import from omnibase.protocols.core

<!-- NEW -->
Install omnibase_spi for protocol definitions  
Import from omnibase_spi.protocols.core
```

### Step 4: Update CI/CD and Scripts

Update any build scripts, CI workflows, or tooling:

```yaml
# OLD workflow
- name: Install protocols
  run: pip install omnibase-spi

# NEW workflow  
- name: Install protocols
  run: pip install omnibase_spi
```

### Step 5: Test Migration

Validate your migration:

```python
# Test script to validate migration
def test_migration():
    try:
        # Test core protocol imports
        from omnibase_spi.protocols.core import ProtocolWorkflowReducer
        from omnibase_spi.protocols.types import LogLevel
        from omnibase_spi.protocols.mcp import ProtocolMCPRegistry

        print("✅ Migration successful: All imports working")
        return True
    except ImportError as e:
        print(f"❌ Migration incomplete: {e}")
        return False

if __name__ == "__main__":
    test_migration()
```

## Common Migration Issues

### Issue 1: Mixed Import Paths
**Problem**: Some imports updated, others not
```python
from omnibase.protocols.core import ProtocolLogger  # OLD
from omnibase_spi.protocols.types import LogLevel   # NEW
```

**Solution**: Use comprehensive search-and-replace across entire codebase

### Issue 2: Dependency Version Conflicts  
**Problem**: Both old and new packages installed
```bash
pip list | grep omnibase
# omnibase-spi    0.1.0
# omnibase_spi    0.1.0  
```

**Solution**: Uninstall old package first
```bash
pip uninstall omnibase-spi
pip install omnibase_spi
```

### Issue 3: String References in Configuration
**Problem**: Configuration files still reference old package
```yaml
# config.yaml
protocol_package: "omnibase.protocols"
```

**Solution**: Update configuration strings
```yaml
# config.yaml
protocol_package: "omnibase_spi.protocols"
```

## Validation Checklist

After migration, verify:

- [ ] All imports use `omnibase_spi.*` paths
- [ ] Package builds successfully  
- [ ] Tests pass with new imports
- [ ] No references to `omnibase-spi` or `omnibase.` remain
- [ ] CI/CD pipelines updated
- [ ] Documentation updated
- [ ] Dependencies updated in all environments

## Breaking Changes Summary

| Component | Old Reference | New Reference | Impact |
|-----------|--------------|---------------|---------|
| Package Name | `omnibase-spi` | `omnibase_spi` | Dependency declarations |
| Import Paths | `omnibase.protocols.*` | `omnibase_spi.protocols.*` | All Python imports |
| Directory | `src/omnibase/` | `src/omnibase_spi/` | Internal structure only |
| Protocol APIs | **No Change** | **No Change** | ✅ Fully compatible |

## Timeline Recommendations

For coordinated migration across omnibase ecosystem:

1. **Phase 1**: Update omnibase-spi package (✅ Complete)
2. **Phase 2**: Update omnibase-core and other primary consumers  
3. **Phase 3**: Update dependent applications and services
4. **Phase 4**: Deprecate old package references

## Support

If you encounter migration issues:

1. Check this guide for common solutions
2. Validate your import paths match the new structure
3. Test in isolated environment before full deployment
4. Create issues in omnibase-spi repository for package-specific problems

## Example: Complete Migration

**Before (omnibase-spi):**
```python
# requirements.txt
omnibase-spi>=0.1.0

# main.py  
from omnibase.protocols.core import ProtocolWorkflowReducer
from omnibase.protocols.types.workflow_orchestration_types import WorkflowState

class MyWorkflowHandler(ProtocolWorkflowReducer):
    def reduce_state(self, state: WorkflowState) -> WorkflowState:
        return "completed"
```

**After (omnibase_spi):**
```python
# requirements.txt
omnibase_spi>=0.1.0

# main.py
from omnibase_spi.protocols.core import ProtocolWorkflowReducer  
from omnibase_spi.protocols.types.workflow_orchestration_types import WorkflowState

class MyWorkflowHandler(ProtocolWorkflowReducer):
    def reduce_state(self, state: WorkflowState) -> WorkflowState:
        return "completed"
```

The migration preserves all functionality while ensuring Python package compliance. 🐍✨
