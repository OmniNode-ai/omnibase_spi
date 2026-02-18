# Validation Integration Plan: omnibase_core 0.3.5 Integration

**Repository**: omnibase_spi
**Target**: Integrate omnibase_core validation system
**Created**: 2025-12-03
**Status**: PLAN (Corrected Architecture)

---

## Temporary Standalone Validators

**Note**: Until omnibase_core removes its SPI dependency, standalone validators have been
created in `scripts/validation/` using only Python stdlib (no omnibase_core imports):

| Script | Purpose | Status |
|--------|---------|--------|
| `validate_architecture.py` | One-protocol-per-file rule | Temporary |
| `validate_naming_patterns.py` | Naming conventions, @runtime_checkable | Temporary |
| `validate_namespace_isolation.py` | No Infra imports, no Pydantic models | Temporary |
| `run_all_validations.py` | Unified runner for all validators | Temporary |

**Usage**:
```bash
# Run all validations
python scripts/validation/run_all_validations.py

# Strict mode for CI (exits 1 on failure)
python scripts/validation/run_all_validations.py --strict

# Verbose output
python scripts/validation/run_all_validations.py --verbose

# JSON output
python scripts/validation/run_all_validations.py --json
```

These will be replaced by `omnibase_core.validation` imports once the circular dependency
is resolved.

---

## Correct Architectural Direction

**CRITICAL**: The dependency direction is:

```text
omnibase_spi DEPENDS ON omnibase_core (SPI → Core)
omnibase_core MUST NOT depend on omnibase_spi
```

### Role Definitions

| Package | Role | Owns |
|---------|------|------|
| **omnibase_core** | Platform kernel | Models, orchestration, policies, abstract interfaces, validation rules |
| **omnibase_spi** | Adapter/plugin layer | Concrete implementations of Core interfaces for specific infrastructure |

### What This Means

1. **SPI depends on Core** - This is correct and intentional
2. **Core defines contracts** - SPI implements them
3. **Core owns validation** - SPI uses Core's validators
4. **Adding omnibase_core as a dependency is CORRECT**

---

## Phase 1: Add omnibase_core Dependency

**Priority**: CRITICAL
**Estimated Effort**: Small

### 1.1 Add omnibase_core 0.3.5 Dependency

Update `pyproject.toml` to add omnibase_core as a **runtime dependency**.

**File**: `pyproject.toml`

```toml
[project]
dependencies = [
    "typing-extensions>=4.5.0",
    "pydantic>=2.11.7",
    "omnibase_core>=0.3.5",  # Platform kernel - SPI depends on Core
]
```

**Note**: This is a RUNTIME dependency because SPI implements Core's interfaces and uses Core's models.

**Acceptance Criteria**:
- [ ] omnibase_core 0.3.5+ added to dependencies
- [ ] `uv sync` succeeds
- [ ] `uv lock` regenerates lockfile
- [ ] Import `from omnibase_core.validation import ...` works

---

## Phase 2: Validation Script Integration

**Priority**: HIGH
**Estimated Effort**: Medium

### 2.1 Architecture Validation

Integrate the architecture validator to enforce ONEX one-model-per-file principle.

**Validator**: `validation/architecture.py`
**Purpose**: Ensures no multiple models/enums/protocols in single file

**Usage**:
```bash
# Via CLI
python -m omnibase_core.validation.cli architecture src/omnibase_spi/

# Via programmatic API
from omnibase_core.validation import validate_architecture
result = validate_architecture("src/omnibase_spi/", max_violations=10)
```

**Acceptance Criteria**:
- [ ] Script added to CI pipeline
- [ ] Validates all protocol files follow one-protocol-per-file
- [ ] Zero violations in existing codebase (or documented exceptions)

### 2.2 Union Type Validation

Integrate union type validator to check union usage patterns.

**Validator**: `validation/types.py`
**Purpose**: Checks union type complexity, repeated unions, overly broad types

**Usage**:
```bash
python -m omnibase_core.validation.cli union-usage src/omnibase_spi/
```

**Acceptance Criteria**:
- [ ] Script added to CI pipeline
- [ ] Validates union types in protocols
- [ ] Documents any intentional broad unions

### 2.3 Pattern Validation

Integrate pattern validator with sub-checkers.

**Validator**: `validation/patterns.py`
**Sub-checkers**:
- `checker_pydantic_pattern.py` - Pydantic usage patterns
- `checker_naming_convention.py` - Naming conventions
- `checker_generic_pattern.py` - Generic type patterns

**Usage**:
```bash
python -m omnibase_core.validation.cli patterns src/omnibase_spi/
```

**Acceptance Criteria**:
- [ ] All three sub-checkers integrated
- [ ] SPI-specific naming convention rules (Protocol* prefix)
- [ ] Generic type pattern validation for protocols

### 2.4 Circular Import Detection

Integrate circular import validator.

**Validator**: `validation/circular_import_validator.py`
**Purpose**: Detects circular import issues

**Usage**:
```bash
python -m omnibase_core.validation.cli circular-imports src/omnibase_spi/
```

**Acceptance Criteria**:
- [ ] Script added to CI pipeline
- [ ] Zero circular imports in SPI
- [ ] Detection includes TYPE_CHECKING imports

---

## Phase 3: CI Pipeline Integration

**Priority**: HIGH
**Estimated Effort**: Medium

### 3.1 Create Unified Validation Script

Create a script that runs all validators with SPI-specific configuration.

**File**: `scripts/run_validations.py`

```python
#!/usr/bin/env python3
"""Run all omnibase_core validations on SPI codebase."""

from omnibase_core.validation import (
    validate_architecture,
    validate_union_usage,
    validate_patterns,
    validate_all,
)

def main():
    # Run all validations with SPI-specific settings
    results = validate_all(
        "src/omnibase_spi/",
        strict=True,
        max_violations=0,  # Zero tolerance for violations
    )

    if not results.is_valid:
        for error in results.errors:
            print(f"ERROR: {error}")
        return 1

    print("All validations passed!")
    return 0

if __name__ == "__main__":
    exit(main())
```

### 3.2 GitHub Actions Integration

Add validation to CI workflow.

**File**: `.github/workflows/validate.yml`

```yaml
name: Validation

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with:
          enable-cache: true
          cache-dependency-glob: '**/uv.lock'

      - name: Install dependencies
        run: uv sync --group dev

      - name: Run Architecture Validation
        run: uv run python -m omnibase_core.validation.cli architecture src/omnibase_spi/ --strict

      - name: Run Union Usage Validation
        run: uv run python -m omnibase_core.validation.cli union-usage src/omnibase_spi/ --strict

      - name: Run Pattern Validation
        run: uv run python -m omnibase_core.validation.cli patterns src/omnibase_spi/ --strict

      - name: Run Circular Import Detection
        run: uv run python -m omnibase_core.validation.cli circular-imports src/omnibase_spi/ --strict

      - name: Run All Validations
        run: uv run python -m omnibase_core.validation.cli all src/omnibase_spi/ --strict
```

**Acceptance Criteria**:
- [ ] CI workflow created
- [ ] All validators run on every PR
- [ ] Failures block merge
- [ ] Clear error messages on failure

---

## Phase 4: SPI-Specific Validation Configuration

**Priority**: MEDIUM
**Estimated Effort**: Medium

### 4.1 Create SPI Validation Configuration

Create configuration file for SPI-specific validation rules.

**File**: `validation_config.yaml`

```yaml
# SPI Validation Configuration
# Uses omnibase_core validation framework
validation:
  architecture:
    enabled: true
    strict: true
    rules:
      - one_protocol_per_file: true

  naming:
    enabled: true
    rules:
      - protocol_prefix: "Protocol"
      - exception_suffix: "Error"

  patterns:
    enabled: true
    rules:
      - runtime_checkable: true  # All protocols must have @runtime_checkable
```

### 4.2 SPI-Specific Extensions

If needed, create SPI-specific validation extensions that build on Core's validators.

**File**: `scripts/validation/spi_validators.py`

```python
"""SPI-specific validation extensions using omnibase_core."""

from omnibase_core.validation import (
    ValidationResult,
    validate_architecture,
)

def validate_spi_protocols(path: str) -> ValidationResult:
    """
    SPI-specific protocol validation.

    Extends Core's architecture validation with SPI-specific rules:
    - All protocols must use @runtime_checkable
    - Protocol methods must have ellipsis bodies
    - No concrete implementations in protocol files
    """
    # Start with Core's validation
    result = validate_architecture(path)

    # Add SPI-specific checks
    # ... additional validation logic ...

    return result
```

---

## Phase 5: Existing Script Migration

**Priority**: LOW
**Estimated Effort**: Small

### 5.1 Audit Existing Scripts

Review existing validation scripts in `scripts/validation/` and migrate to use Core validators where applicable:

| Script | Status | Action |
|--------|--------|--------|
| `comprehensive_spi_validator.py` | Migrate | Use omnibase_core validators |
| `validate_spi_protocols.py` | Migrate | Wrap Core's validate_architecture |
| `validate_spi_naming.py` | Migrate | Use Core's naming checker |
| `validate_spi_typing_patterns.py` | Migrate | Use Core's patterns checker |
| `validate_protocol_duplicates.py` | Keep | May not exist in Core |
| `protocol_signature_hasher.py` | Keep | Unique SPI functionality |
| `compare_protocols.py` | Keep | Unique SPI functionality |

---

## Phase 6: Documentation

**Priority**: MEDIUM
**Estimated Effort**: Small

### 6.1 Update Developer Documentation

Update CLAUDE.md and README with validation information.

**Sections to add**:
- How to run validations locally
- CI validation requirements
- Using omnibase_core validators
- SPI-specific validation rules

### 6.2 Validation Results Models

Document the validation result models from Core:

| Model | Purpose |
|-------|---------|
| `ModelValidationResult` | Primary result container |
| `EnumValidationSeverity` | INFO, WARNING, ERROR, CRITICAL |
| `EnumValidationResult` | PASS, FAIL, SKIP, ERROR |
| `EnumValidationType` | Validation category enum |

---

## Implementation Order

```text
Phase 1: Add Dependency
    └── 1.1: Add omnibase_core 0.3.5 to dependencies
            |
            v
Phase 2: Validation Script Integration
    ├── 2.1: Architecture validation
    ├── 2.2: Union type validation
    ├── 2.3: Pattern validation
    └── 2.4: Circular import detection
            |
            v
Phase 3: CI Pipeline Integration
    ├── 3.1: Unified validation script
    └── 3.2: GitHub Actions workflow
            |
            v
Phase 4: SPI-Specific Configuration
    ├── 4.1: Configuration file
    └── 4.2: SPI extensions
            |
            v
Phase 5: Existing Script Migration
    └── Migrate to Core validators
            |
            v
Phase 6: Documentation
    └── Update docs
```

---

## Success Criteria

### Technical
- [ ] omnibase_core 0.3.5+ added as runtime dependency
- [ ] All validators run successfully on codebase
- [ ] CI blocks PRs with validation failures
- [ ] Zero validation errors in current codebase

### Architectural
- [ ] SPI correctly depends on Core
- [ ] SPI uses Core's validation framework
- [ ] No circular dependencies

### Quality
- [ ] Clear error messages for all validation failures
- [ ] Documentation for running validations locally
- [ ] Suppressions mechanism for intentional exceptions

---

## Architecture Diagram

```text
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
│         (omniagent, omniintelligence, etc.)                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ uses
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     omnibase_spi                             │
│     (Service Provider Interface - Adapter Layer)            │
│                                                             │
│  - Concrete implementations of Core interfaces              │
│  - Bus providers (Kafka, Redpanda, in-memory)              │
│  - Storage providers (S3, local filesystem)                 │
│  - Registry backends (Postgres, etc.)                       │
│  - Uses Core's validation framework                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ depends on
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     omnibase_core                            │
│           (Platform Kernel - Foundation)                     │
│                                                             │
│  - Canonical data models and contracts                      │
│  - Orchestration primitives (DAG/FSM engines)              │
│  - Abstract interfaces (bus, storage, registry)            │
│  - Validation framework                                     │
│  - System policies and rules                                │
└─────────────────────────────────────────────────────────────┘
```

---

## Note on MVP_PLAN.md

The `docs/MVP_PLAN.md` document contains an **incorrect dependency direction**. It states:

> SPI MAY import Core | Under `TYPE_CHECKING` only, never at runtime

This is **WRONG**. The correct rule is:

> SPI DEPENDS ON Core at runtime. SPI imports Core models, interfaces, and utilities.

The MVP_PLAN.md needs to be corrected to reflect the actual architecture.

---

**Document Owner**: OmniNode Architecture Team
**Last Updated**: 2025-12-03
