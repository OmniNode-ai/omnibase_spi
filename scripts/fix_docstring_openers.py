#!/usr/bin/env python3
"""
Fix docstrings that start with double-quote instead of triple-quote.

Handles cases where docstring starts with double-quote but should be triple-quote.
"""

from pathlib import Path


def fix_docstring_openers(content: str) -> tuple[str, int]:
    """Fix docstring openers. Returns (fixed_content, num_fixes)."""
    fixes = 0
    lines = content.split("\n")
    fixed_lines = []

    for line in lines:
        stripped = line.strip()

        # Check if line starts with "" followed by text (likely docstring opener)
        if stripped.startswith('""') and not stripped.startswith('"""'):
            # Make sure it's not just closing quotes
            if len(stripped) > 2 and stripped[2] not in ('"', " ", "\n", "\r"):
                # This is a docstring opener, fix it
                fixed_line = line.replace('""', '"""', 1)
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
            fixed, fixes = fix_docstring_openers(original)

            if fixes > 0:
                py_file.write_text(fixed)
                total_files += 1
                total_fixes += fixes
                print(
                    f"✓ Fixed {fixes:3d} docstring openers in {py_file.relative_to(root_dir)}"
                )
        except Exception as e:
            print(f"✗ Error processing {py_file.relative_to(root_dir)}: {e}")

    print(f"\n{'='*80}")
    print(f"DOCSTRING OPENERS FIXED")
    print(f"{'='*80}")
    print(f"✓ Files fixed: {total_files}")
    print(f"✓ Total fixes: {total_fixes}")


if __name__ == "__main__":
    main()
