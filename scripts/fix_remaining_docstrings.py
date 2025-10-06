#!/usr/bin/env python3
"""
Fix remaining docstring issues where closing delimiter is wrong.

Handles cases where double-quote appears at end of docstring line instead of triple-quote.
"""

import re
from pathlib import Path


def fix_docstring_delimiters(content: str) -> tuple[str, int]:
    """Fix docstring delimiters that use double-quote instead of triple-quote. Returns (fixed_content, num_fixes)."""
    fixes = 0

    # Pattern 1: Lines ending with double-quote (likely docstring closers)
    # Match lines that have content before double-quote and nothing after except whitespace
    pattern1 = r'(^.+)""(\s*)$'

    lines = content.split("\n")
    fixed_lines = []

    for i, line in enumerate(lines):
        # Check if line ends with double-quote (but not triple-quote)
        if line.rstrip().endswith('""') and not line.rstrip().endswith('"""'):
            # Check if this is likely a docstring closer (not in the middle of code)
            # Look at previous lines to see if we're in a docstring context
            if i > 0:
                # If previous line has docstring content or is part of multi-line string
                prev_line = lines[i - 1].strip()
                if prev_line and not prev_line.startswith("#"):
                    # This looks like a docstring closer
                    fixed_line = line.rstrip()[:-2] + '"""'
                    if line != fixed_line:
                        fixed_lines.append(fixed_line)
                        fixes += 1
                        continue

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
            fixed, fixes = fix_docstring_delimiters(original)

            if fixes > 0:
                py_file.write_text(fixed)
                total_files += 1
                total_fixes += fixes
                print(
                    f"✓ Fixed {fixes:3d} docstring delimiters in {py_file.relative_to(root_dir)}"
                )
        except Exception as e:
            print(f"✗ Error processing {py_file.relative_to(root_dir)}: {e}")

    print(f"\n{'='*80}")
    print(f"DOCSTRING DELIMITERS FIXED")
    print(f"{'='*80}")
    print(f"✓ Files fixed: {total_files}")
    print(f"✓ Total fixes: {total_fixes}")


if __name__ == "__main__":
    main()
