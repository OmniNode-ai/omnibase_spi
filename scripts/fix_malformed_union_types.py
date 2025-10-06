#!/usr/bin/env python3
"""
Fix malformed union type annotations.

Fixes patterns like: expires_at: "datetime" | None"
Should be: expires_at: "datetime | None"
"""

import re
from pathlib import Path


def fix_malformed_unions(content: str) -> tuple[str, int]:
    """Fix malformed union types. Returns (fixed_content, num_fixes)."""
    fixes = 0

    # Pattern: Captures type annotations like: "TypeName" | None"
    # Should be: "TypeName | None"
    pattern = r':\s*"([^"]+)"\s*\|\s*None"'

    def replace_union(match):
        nonlocal fixes
        fixes += 1
        type_name = match.group(1)
        return f': "{type_name} | None"'

    fixed_content = re.sub(pattern, replace_union, content)

    return fixed_content, fixes


def main():
    """Fix all Python files in protocols directory."""
    root_dir = Path(__file__).parent.parent
    protocols_dir = root_dir / "src" / "omnibase_spi" / "protocols"

    total_files = 0
    total_fixes = 0

    for py_file in protocols_dir.rglob("*.py"):
        try:
            original = py_file.read_text()
            fixed, fixes = fix_malformed_unions(original)

            if fixes > 0:
                py_file.write_text(fixed)
                total_files += 1
                total_fixes += fixes
                print(
                    f"✓ Fixed {fixes:3d} malformed unions in {py_file.relative_to(root_dir)}"
                )
        except Exception as e:
            print(f"✗ Error processing {py_file.relative_to(root_dir)}: {e}")

    print(f"\n{'='*80}")
    print(f"MALFORMED UNION TYPES FIXED")
    print(f"{'='*80}")
    print(f"✓ Files fixed: {total_files}")
    print(f"✓ Total fixes: {total_fixes}")


if __name__ == "__main__":
    main()
