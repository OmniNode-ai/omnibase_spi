#!/usr/bin/env python3
"""
Fix malformed quotes from forward reference fixer.

Fixes pattern: "TypeName" | None" -> "TypeName | None"
Fixes pattern: "TypeName" | SomethingElse" -> "TypeName | SomethingElse"
"""

import re
from pathlib import Path


def fix_malformed_quotes(content: str) -> tuple[str, int]:
    """Fix malformed quote patterns. Returns (fixed_content, num_fixes)."""
    fixes = 0

    # Pattern 1: "TypeName" | None" -> "TypeName | None"
    # This matches: "SomeType" followed by | and something, then another "
    pattern1 = r'"([A-Z][a-zA-Z0-9_]*?)"\s*(\|[^"]*?)"'

    def replace1(match):
        nonlocal fixes
        fixes += 1
        return f'"{match.group(1)} {match.group(2)}"'

    content = re.sub(pattern1, replace1, content)

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
        fixed, fixes = fix_malformed_quotes(original)

        if fixes > 0:
            py_file.write_text(fixed)
            total_files += 1
            total_fixes += fixes
            print(
                f"✓ Fixed {fixes:3d} malformed quotes in {py_file.relative_to(root_dir)}"
            )

    print(f"\n{'='*80}")
    print(f"MALFORMED QUOTE FIX COMPLETE")
    print(f"{'='*80}")
    print(f"✓ Files fixed: {total_files}")
    print(f"✓ Total fixes: {total_fixes}")


if __name__ == "__main__":
    main()
