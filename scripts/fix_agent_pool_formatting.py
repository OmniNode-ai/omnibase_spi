#!/usr/bin/env python3
"""
Fix docstring formatting issues in protocol_agent_pool.py
"""

import re


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
    fix_docstring_formatting(
        "/Volumes/PRO-G40/Code/omnibase_spi/src/omnibase_spi/protocols/memory/protocol_agent_pool.py"
    )
