#!/usr/bin/env python3
"""
Final comprehensive docstring delimiter fix.

Finds and fixes all patterns of double-quote where triple-quote should be used.
"""

import re
from pathlib import Path


def fix_all_docstring_issues(content: str) -> tuple[str, int]:
    """Fix all docstring delimiter issues. Returns (fixed_content, num_fixes)."""
    fixes = 0
    lines = content.split("\n")
    fixed_lines = []

    for i, line in enumerate(lines):
        original_line = line

        # Pattern 1: Line ends with "" but not """
        if '""' in line and '"""' not in line:
            # Count quotes in line
            quote_count = line.count('"')

            # If line ends with "" (double quote), likely needs triple quote
            if line.rstrip().endswith('""'):
                # Replace the trailing "" with """
                line = line.rstrip()[:-2] + '"""'
                if line != original_line:
                    fixes += 1
            # If line starts with stripped "" (likely docstring opener)
            elif line.strip().startswith('""') and len(line.strip()) > 2:
                # This is a docstring opener
                line = line.replace('""', '"""', 1)
                if line != original_line:
                    fixes += 1

        fixed_lines.append(line)

    return "\n".join(fixed_lines), fixes


def main():
    """Fix all Python files in protocols directory."""
    root_dir = Path(__file__).parent.parent
    protocols_dir = root_dir / "src" / "omnibase_spi" / "protocols"

    total_files = 0
    total_fixes = 0

    for py_file in protocols_dir.rglob("*.py"):
        try:
            original = py_file.read_text()
            fixed, fixes = fix_all_docstring_issues(original)

            if fixes > 0:
                py_file.write_text(fixed)
                total_files += 1
                total_fixes += fixes
                print(
                    f"✓ Fixed {fixes:3d} docstring issues in {py_file.relative_to(root_dir)}"
                )
        except Exception as e:
            print(f"✗ Error processing {py_file.relative_to(root_dir)}: {e}")

    print(f"\n{'='*80}")
    print(f"FINAL DOCSTRING FIXES")
    print(f"{'='*80}")
    print(f"✓ Files fixed: {total_files}")
    print(f"✓ Total fixes: {total_fixes}")


if __name__ == "__main__":
    main()
