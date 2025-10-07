#!/usr/bin/env python3
"""
Fix docstring formatting issues in protocol_agent_pool.py
"""

import re
from pathlib import Path


def fix_docstring_formatting(file_path):
    """Fix malformed docstring formatting"""
    with open(file_path, "r") as f:
        content = f.read()

    # Fix the pattern where docstring end is missing quotes and newline before next method
    # Pattern: """...async def method_name
    fixed_content = re.sub(
        r'"""([^"]*)\.\.\.(\s*)async def ([^(]*)\(',
        r'"""\1\2...\2\2async def \3(',
        content,
    )

    # Fix pattern where docstring content is directly concatenated
    # Pattern: """Some text"""...async def
    fixed_content = re.sub(
        r'"""([^"]*)"""(\s*)\.\.\.(\s*)async def ([^(]*)\(',
        r'"""\1\2\2...\2\2async def \4(',
        fixed_content,
    )

    # Fix missing triple quotes at end of docstring
    # Pattern: Some text"""...async def
    fixed_content = re.sub(
        r'([^\n]*)"""(\s*)\.\.\.(\s*)async def ([^(]*)\(',
        r"\1\2\2\2...\2\2async def \4(",
        fixed_content,
    )

    with open(file_path, "w") as f:
        f.write(fixed_content)

    print(f"Fixed docstring formatting in {file_path}")


if __name__ == "__main__":
    # Use relative paths for portability
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent.parent.parent  # Go up from scripts/archive/fixes to repo root
    target_file = (
        repo_root
        / "src"
        / "omnibase_spi"
        / "protocols"
        / "memory"
        / "protocol_agent_pool.py"
    )
    fix_docstring_formatting(target_file)
