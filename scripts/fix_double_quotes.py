#!/usr/bin/env python3
"""
Fix double-quoting issues from forward reference fixer.

Replaces:
- ""TypeName"" with "TypeName"
- ""TypeName" with "TypeName"
"""

import re
from pathlib import Path


def fix_double_quotes_in_file(file_path: Path) -> int:
    """Fix double quotes in a single file. Returns number of fixes."""
    content = file_path.read_text()

    # Pattern 1: ""TypeName""  -> "TypeName"
    pattern1 = r'""([A-Z][a-zA-Z0-9_]*?)""'
    content, count1 = re.subn(pattern1, r'"\1"', content)

    # Pattern 2: ""TypeName" -> "TypeName"
    pattern2 = r'""([A-Z][a-zA-Z0-9_]*?)"'
    content, count2 = re.subn(pattern2, r'"\1"', content)

    # Calculate total fixes
    total_fixes = count1 + count2

    # Only write if we made changes
    if total_fixes > 0:
        file_path.write_text(content)

    return total_fixes


def main():
    """Fix all Python files in protocols directory."""
    root_dir = Path(__file__).parent.parent
    protocols_dir = root_dir / "src" / "omnibase_spi" / "protocols"

    total_files = 0
    total_fixes = 0

    for py_file in protocols_dir.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue

        # Read original
        original = py_file.read_text()

        # Check for double quotes
        if '""' in original:
            fixes = fix_double_quotes_in_file(py_file)
            if fixes > 0:
                total_files += 1
                total_fixes += fixes
                print(f"Fixed {py_file.relative_to(root_dir)}")

    print(f"\n✓ Fixed {total_fixes} double-quote issues in {total_files} files")


if __name__ == "__main__":
    main()
