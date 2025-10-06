#!/usr/bin/env python3
"""
Remove double quotes in type annotations.

Fixes patterns like:
- ""TypeName" -> "TypeName"
- ""datetime" | None" -> "datetime | None"
"""

import re
from pathlib import Path


def remove_double_quotes(content: str) -> tuple[str, int]:
    """Remove double quotes. Returns (fixed_content, num_fixes)."""
    # Pattern: ""anything"
    original = content
    content = content.replace('""', '"')

    fixes = original.count('""')
    return content, fixes


def main():
    """Fix all Python files in protocols directory."""
    root_dir = Path(__file__).parent.parent
    protocols_dir = root_dir / "src" / "omnibase_spi" / "protocols"

    total_files = 0
    total_fixes = 0

    for py_file in protocols_dir.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue

        original = py_file.read_text()
        if '""' in original:
            fixed, fixes = remove_double_quotes(original)
            py_file.write_text(fixed)
            total_files += 1
            total_fixes += fixes
            print(
                f"✓ Removed {fixes:3d} double quotes in {py_file.relative_to(root_dir)}"
            )

    print(f"\n{'='*80}")
    print(f"DOUBLE QUOTES REMOVED")
    print(f"{'='*80}")
    print(f"✓ Files fixed: {total_files}")
    print(f"✓ Total fixes: {total_fixes}")


if __name__ == "__main__":
    main()
