#!/usr/bin/env python3
"""
Script to fix remaining \n escape sequences in method bodies.
"""

import os
import re
from pathlib import Path


def fix_escape_sequences(file_path: Path) -> int:
    """Fix remaining \n escape sequences."""
    fixes_count = 0

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # Fix any remaining \n        """ patterns
    content = re.sub(r'\\n\s*"""', '"""', content)

    # Fix any remaining \n        patterns
    content = re.sub(r"\\n\s*", "", content)

    # Fix any remaining \\n patterns
    content = re.sub(r"\\\\n", "", content)

    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Fixed escape sequences in {file_path.name}")
        fixes_count = 1

    return fixes_count


def main():
    """Process all Memory domain files."""
    # Use relative paths for portability
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent
    memory_dir = repo_root / "src" / "omnibase_spi" / "protocols" / "memory"

    total_fixes = 0

    print("Fixing escape sequences in Memory domain files...")

    for file_path in memory_dir.glob("*.py"):
        if file_path.name != "__init__.py":
            fixes = fix_escape_sequences(file_path)
            total_fixes += fixes

    print(f"\nTotal files with escape sequences fixed: {total_fixes}")


if __name__ == "__main__":
    main()
