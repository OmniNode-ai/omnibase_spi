#!/usr/bin/env python3
"""
Find and fix ALL quote issues in forward references.

Handles patterns like:
- "Type | None: -> "Type | None":
- "Type" | None: -> "Type | None":
- "Type | Something" -> "Type | Something"
"""

import re
from pathlib import Path


def fix_all_quote_issues(content: str) -> tuple[str, int]:
    """Fix all quote-related issues. Returns (fixed_content, num_fixes)."""
    fixes = 0

    # Pattern 1: "Type | None: (missing closing quote before colon)
    pattern1 = r'"([A-Z][a-zA-Z0-9_]+\s*\|\s*[^"]+?):'

    def replace1(match):
        nonlocal fixes
        fixes += 1
        return f'"{match.group(1)}":'

    content = re.sub(pattern1, replace1, content)

    # Pattern 2: "Type" | None: (quote in wrong place)
    pattern2 = r'"([A-Z][a-zA-Z0-9_]+)"\s*(\|\s*[^:]+?):'

    def replace2(match):
        nonlocal fixes
        fixes += 1
        return f'"{match.group(1)} {match.group(2)}":'

    content = re.sub(pattern2, replace2, content)

    # Pattern 3: "Type" | None" (double quote at end, no colon)
    pattern3 = r'"([A-Z][a-zA-Z0-9_]+)"\s*(\|[^":]+?)"(?=\s*[,=\)])'

    def replace3(match):
        nonlocal fixes
        fixes += 1
        return f'"{match.group(1)} {match.group(2)}"'

    content = re.sub(pattern3, replace3, content)

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
        fixed, fixes = fix_all_quote_issues(original)

        if fixes > 0:
            py_file.write_text(fixed)
            total_files += 1
            total_fixes += fixes
            print(f"✓ Fixed {fixes:3d} quote issues in {py_file.relative_to(root_dir)}")

    print(f"\n{'='*80}")
    print(f"ALL QUOTE ISSUES FIXED")
    print(f"{'='*80}")
    print(f"✓ Files fixed: {total_files}")
    print(f"✓ Total fixes: {total_fixes}")


if __name__ == "__main__":
    main()
