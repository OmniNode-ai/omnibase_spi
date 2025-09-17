# omnibase_spi Protocol Validation

SPI-specific validation scripts that ensure protocol quality and consistency within omnibase_spi.

## Why SPI Needs Its Own Validation?

Since omnibase_spi cannot depend on omnibase_core (to avoid circular dependencies), it needs standalone validation scripts. These are specialized copies of the omnibase_core validation framework.

## Scripts

### `spi_protocol_auditor.py`
Comprehensive SPI protocol validation:
- Internal duplicate detection
- Naming convention compliance
- Category organization validation
- SPI self-containment checks

**Usage:**
```bash
# Audit all SPI protocols
python scripts/validation/spi_protocol_auditor.py

# Audit with custom SPI path
python scripts/validation/spi_protocol_auditor.py --spi-path /path/to/omnibase_spi
```

### `spi-pre-commit-config.yaml`
Pre-commit configuration template for SPI-specific validation.

**Setup:**
```bash
# Copy pre-commit config to repository root
cp scripts/validation/spi-pre-commit-config.yaml .pre-commit-config.yaml

# Install pre-commit hooks
pre-commit install
```

## Validation Rules

### Protocol Organization
- All protocols must be in `src/omnibase_spi/protocols/`
- Organized by category: `core`, `agent`, `workflow`, `file_handling`, `event_bus`, etc.
- File names follow `protocol_*.py` pattern
- Class names start with `Protocol`

### Self-Containment
- SPI protocols cannot import from `omniagent` or `omnibase_core`
- Must be completely self-contained
- Can only import from standard library or other SPI modules

### Quality Standards
- No empty protocols (protocols must have methods)
- No overly complex protocols (>15 methods suggests splitting needed)
- No internal duplicates within SPI

## CI Integration

Add to your CI pipeline:

```yaml
# Example GitHub Actions
- name: Validate SPI Protocols
  run: |
    cd omnibase_spi
    python scripts/validation/spi_protocol_auditor.py
```

## Maintenance

These scripts are copies from `omnibase_core/src/omnibase_core/validation/` and need manual synchronization when the core validation logic changes.

**Last Synchronized**: 2024-11-XX
**Source Version**: omnibase_core v0.1.0

## Integration with Other Repositories

Other repositories should use the centralized validation from omnibase_core:

```python
# In other omni* repositories (not SPI)
from omnibase_core.validation import audit_protocols, check_against_spi

# Quick audit
result = audit_protocols(".")
if not result.success:
    print("Protocol violations found!")

# Check against SPI for duplicates
duplication_report = check_against_spi(".", "../omnibase_spi")
```

Only omnibase_spi needs these standalone copies due to dependency constraints.