#!/usr/bin/env python3
"""
Restore triple-quoted docstrings that were broken by double-quote removal.

Fixes patterns like:
- Two quotes at start of line should be three quotes
- Stand-alone two-quote lines should be three quotes
"""

import re
from pathlib import Path


def restore_docstrings(content: str) -> tuple[str, int]:
    """Restore broken docstrings. Returns (fixed_content, num_fixes)."""
    lines = content.split("\n")
    fixed_lines = []
    fixes = 0

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Case 1: Line is exactly "" (likely a docstring delimiter)
        if stripped == '""':
            # Check context to see if this should be a docstring
            if i > 0 or i < len(lines) - 1:
                # If previous line is empty, def, class, or this is first line
                # Or if next line has content, this is likely a docstring
                if (
                    i == 0
                    or not lines[i - 1].strip()
                    or "def " in lines[i - 1]
                    or "class " in lines[i - 1]
                    or (
                        i < len(lines) - 1
                        and lines[i + 1].strip()
                        and not lines[i + 1].strip().startswith("#")
                    )
                ):
                    fixed_lines.append(line.replace('""', '"""'))
                    fixes += 1
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)

    return "\n".join(fixed_lines), fixes


def main():
    """Fix all Python files in protocols directory."""
    root_dir = Path(__file__).parent.parent
    protocols_dir = root_dir / "src" / "omnibase_spi" / "protocols"

    total_files = 0
    total_fixes = 0

    for py_file in protocols_dir.rglob("*.py"):
        original = py_file.read_text()
        if '\n""\n' in original or original.startswith('""'):
            fixed, fixes = restore_docstrings(original)
            if fixes > 0:
                py_file.write_text(fixed)
                total_files += 1
                total_fixes += fixes
                print(
                    f"✓ Restored {fixes:3d} docstrings in {py_file.relative_to(root_dir)}"
                )

    print(f"\n{'='*80}")
    print(f"DOCSTRINGS RESTORED")
    print(f"{'='*80}")
    print(f"✓ Files fixed: {total_files}")
    print(f"✓ Total fixes: {total_fixes}")


if __name__ == "__main__":
    main()
