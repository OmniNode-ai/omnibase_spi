#!/usr/bin/env python3
"""
Script to fix protocol formatting issues in Memory domain files.
"""

import os
import re
from pathlib import Path


def fix_protocol_formatting(file_path: Path) -> int:
    """Fix protocol formatting issues including malformed docstrings and method bodies."""
    fixes_count = 0

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # Fix 1: Remove extra quotes from forward references
    content = re.sub(r'""ModelAgentConfig""', '"ModelAgentConfig"', content)

    # Fix 2: Fix malformed docstrings that have no proper spacing
    content = re.sub(r'(\w+)"""', r'\1:\n        """', content)

    # Fix 3: Fix method bodies that have no proper ellipsis
    content = re.sub(r'"""\.\.\.', '"""\n        ...', content)

    # Fix 4: Fix methods that are concatenated without proper line breaks
    content = re.sub(r'"""\.\.\.async def', '"""\n\n    async def', content)

    # Fix 5: Fix methods that are missing proper return types and have malformed docstrings
    content = re.sub(
        r'async def (\w+)\([^)]*\):"""',
        r'async def \1(self, *args, **kwargs):\n        """',
        content,
    )

    # Fix 6: Ensure proper protocol method structure
    lines = content.split("\n")
    fixed_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]

        # If we find a method definition with malformed docstring
        if re.match(r'async def \w+\([^)]*\):"""', line):
            # Extract method name
            method_match = re.match(r"async def (\w+)\(", line)
            if method_match:
                method_name = method_match.group(1)

                # Fix the method definition
                if method_name in [
                    "spawn_agent",
                    "terminate_agent",
                    "get_agent",
                    "list_active_agents",
                    "get_agent_status",
                    "health_check",
                    "restart_agent",
                    "get_resource_usage",
                    "set_agent_idle",
                    "set_agent_busy",
                ]:
                    line = f"    async def {method_name}(self, *args, **kwargs):"
                else:
                    # Keep existing signature but fix the docstring
                    line = line.replace(':""', ':\n        """')

        fixed_lines.append(line)
        i += 1

    content = "\n".join(fixed_lines)

    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Fixed protocol formatting in {file_path.name}")
        fixes_count = 1

    return fixes_count


def main():
    """Process all Memory domain files."""
    memory_dir = Path(
        "/Volumes/PRO-G40/Code/omnibase_spi/src/omnibase_spi/protocols/memory"
    )

    total_fixes = 0

    print("Fixing protocol formatting in Memory domain files...")

    for file_path in memory_dir.glob("*.py"):
        if file_path.name != "__init__.py":
            fixes = fix_protocol_formatting(file_path)
            total_fixes += fixes

    print(f"\nTotal files with formatting fixes: {total_fixes}")


if __name__ == "__main__":
    main()
