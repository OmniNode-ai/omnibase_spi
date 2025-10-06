#!/usr/bin/env python3
"""
Fix all formatting issues in protocol_distributed_agent_orchestrator.py
"""

import re


def fix_orchestrator_formatting(file_path):
    """Fix all formatting issues in the distributed orchestrator file"""
    with open(file_path, "r") as f:
        content = f.read()

    # Fix pattern: """...def method_name(self):
    content = re.sub(
        r'"""\.\.\.(def|async def) ([^(]*)\(', r"...\n\n    \1 \2(", content
    )

    # Fix pattern: """...async def method_name(self):
    content = re.sub(
        r'"""\.\.\.(\s*)async def ([^(]*)\(', r"...\n\n\1async def \2(", content
    )

    # Fix pattern: """Some text"""...async def method_name
    content = re.sub(
        r'"""([^"]*)"""(\s*)\.\.\.(\s*)async def ([^(]*)\(',
        r'"""\1\2\2\2...\2\2async def \4(',
        content,
    )

    # Fix Task[Any]text patterns
    content = re.sub(r"Task\[Any\]([A-Za-z])", r"Task \1", content)

    # Fix missing method definitions after docstrings
    content = re.sub(
        r'Returns:\s*\n\s*([^\n"]*)\s*\n\s*"""([^"]*)"',
        r'Returns:\n            \1\n        """\n        ...',
        content,
    )

    # Fix the specific broken pattern we found
    content = re.sub(
        r'"""([^"]*)\.\.\.([^"]*)"""([^"]*)"', r'"""\1\2...\2\2"""', content
    )

    with open(file_path, "w") as f:
        f.write(content)

    print(f"Fixed formatting in {file_path}")


if __name__ == "__main__":
    fix_orchestrator_formatting(
        "/Volumes/PRO-G40/Code/omnibase_spi/src/omnibase_spi/protocols/memory/protocol_distributed_agent_orchestrator.py"
    )
