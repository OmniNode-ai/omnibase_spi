# SPI Typing Pattern Fixer

AST-based tool to automatically fix SPI typing pattern violations in protocol files.

## Overview

This script analyzes Protocol classes and fixes three types of violations:

1. **Async Non-Awaitable Returns** (1318 warnings)
   - Pattern: `async def method() -> str:`
   - Fixed to: `async def method() -> Awaitable[str]:`

2. **Sync I/O Methods** (3 errors)
   - Pattern: `def read_text() -> str:`
   - Fixed to: `async def read_text() -> Awaitable[str]:`

3. **Missing TYPE_CHECKING Imports** (2 warnings)
   - Detects forward references outside TYPE_CHECKING blocks
   - (Currently analyzed but not auto-fixed)

## Usage

### Dry-Run (Recommended First Step)

Shows what would be changed without modifying files:

```bash
# Scan all protocols
python scripts/fix_spi_typing_patterns.py src/omnibase_spi/protocols --dry-run

# Scan single file
python scripts/fix_spi_typing_patterns.py src/omnibase_spi/protocols/core/protocol_logger.py --dry-run

# Scan specific domain
python scripts/fix_spi_typing_patterns.py src/omnibase_spi/protocols/workflow_orchestration --dry-run
```

### Apply Fixes

```bash
# Fix async return types only
python scripts/fix_spi_typing_patterns.py src/omnibase_spi/protocols --fix-async-returns

# Fix sync I/O methods only
python scripts/fix_spi_typing_patterns.py src/omnibase_spi/protocols --fix-sync-io

# Fix all violations
python scripts/fix_spi_typing_patterns.py src/omnibase_spi/protocols --fix-async-returns --fix-sync-io
```

### Options

- `--dry-run` - Show changes without applying (default if no fix flags)
- `--fix-async-returns` - Fix async methods with non-awaitable returns
- `--fix-sync-io` - Fix sync methods that should be async
- `--pattern` - File pattern to match (default: `protocol_*.py`)

## Example Output

### Dry-Run Output

```
🔍 DRY-RUN MODE - No files will be modified
================================================================================

================================================================================
File: src/omnibase_spi/protocols/file_handling/protocol_file_reader.py
================================================================================

[1/3] Line 64 - async_non_awaitable
Context: Class: ProtocolFileReader, Method: read_text

Current:
  async def read_text(self) -> str:

Proposed:
  async def read_text(self) -> Awaitable[str]:
--------------------------------------------------------------------------------

[2/3] Line 74 - async_non_awaitable
Context: Class: ProtocolFileReader, Method: read_bytes

Current:
  async def read_bytes(self) -> bytes:

Proposed:
  async def read_bytes(self) -> Awaitable[bytes]:
--------------------------------------------------------------------------------

================================================================================
SUMMARY
================================================================================
Total files with violations: 47
Total violations: 1321

Breakdown by type:
  Async non-awaitable returns: 1318
  Sync I/O methods: 3
  Missing TYPE_CHECKING imports: 0
================================================================================

💡 To apply fixes, use --fix-async-returns and/or --fix-sync-io
   Example: python scripts/fix_spi_typing_patterns.py src/omnibase_spi/protocols --fix-async-returns --fix-sync-io
```

### Apply Fixes Output

```
✓ Applied 27 fixes to src/omnibase_spi/protocols/core/protocol_logger.py
✓ Applied 15 fixes to src/omnibase_spi/protocols/file_handling/protocol_file_reader.py
✓ Applied 8 fixes to src/omnibase_spi/protocols/event_bus/protocol_event_bus.py

================================================================================
SUMMARY
================================================================================
Total files with violations: 47
Total violations: 1321

Breakdown by type:
  Async non-awaitable returns: 1318
  Sync I/O methods: 3
  Missing TYPE_CHECKING imports: 0
================================================================================
```

## Safety Features

1. **AST Parsing** - Accurate detection, no regex-based false positives
2. **Protocol-Only** - Only modifies classes that inherit from `Protocol`
3. **Preserves Formatting** - Maintains indentation and line structure
4. **Import Management** - Automatically adds `Awaitable` import when needed
5. **Dry-Run Default** - Won't modify files unless explicit fix flags provided
6. **Backup Recommended** - Always commit changes before running fixes

## I/O Method Detection

The script detects I/O methods by checking for these patterns in method names:

- `read`, `write`, `fetch`, `load`, `save`
- `send`, `receive`, `get`, `set`
- `update`, `delete`, `create`, `execute`
- `publish`, `subscribe`, `register`, `unregister`
- `open`, `close`, `connect`, `disconnect`, `query`
- `handle`, `process`, `can_handle`, `invoke`, `call`

## Post-Fix Validation

After applying fixes, run validation:

```bash
# Run comprehensive SPI validator
python scripts/validation/comprehensive_spi_validator.py src/omnibase_spi/protocols

# Run type checking
poetry run mypy src/omnibase_spi/protocols --strict

# Run tests
poetry run pytest tests/
```

## Known Limitations

1. **Multi-line signatures** - Complex multi-line method signatures may need manual review
2. **Complex type annotations** - Nested generics may need manual adjustment
3. **TYPE_CHECKING fixes** - Not yet implemented (manual fix required)
4. **Property methods** - `@property` decorated methods are not modified

## Workflow

Recommended workflow for fixing all violations:

```bash
# 1. Commit current changes
git add -A
git commit -m "checkpoint before SPI typing fixes"

# 2. Dry-run to review changes
python scripts/fix_spi_typing_patterns.py src/omnibase_spi/protocols --dry-run

# 3. Apply async return fixes
python scripts/fix_spi_typing_patterns.py src/omnibase_spi/protocols --fix-async-returns

# 4. Apply sync I/O fixes
python scripts/fix_spi_typing_patterns.py src/omnibase_spi/protocols --fix-sync-io

# 5. Validate fixes
python scripts/validation/comprehensive_spi_validator.py src/omnibase_spi/protocols
poetry run mypy src/omnibase_spi/protocols --strict

# 6. Run tests
poetry run pytest tests/

# 7. Commit fixes
git add -A
git commit -m "fix: resolve 1321 SPI typing pattern violations"
```

## Exit Codes

- `0` - No violations found
- `1` - Violations found (useful for CI/CD)
