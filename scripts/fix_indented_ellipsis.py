#!/usr/bin/env python3
"""
Fix incorrectly indented ellipsis statements in protocol files.

This script finds and removes ellipsis statements that are incorrectly indented
(more than 4 spaces) which are causing syntax errors.
"""
import os
import re
from pathlib import Path


def fix_indented_ellipsis(file_path: Path) -> bool:
    """
    Fix incorrectly indented ellipsis statements in a file.

    Args:
        file_path: Path to the Python file to fix

    Returns:
        True if file was modified, False otherwise
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Pattern to match lines with only whitespace + ellipsis that are incorrectly indented
        # We want to remove lines that have more than 4 spaces followed by only ...
        lines = content.split("\n")
        fixed_lines = []

        for i, line in enumerate(lines):
            # Check if line is only whitespace + ellipsis with more than 4 spaces of indentation
            if re.match(r"^\s{5,}\.\.\.?\s*$", line):
                # Skip this line (remove it) as it's incorrectly indented
                print(
                    f"  Removing incorrectly indented ellipsis at line {i+1}: '{line}'"
                )
                continue
            fixed_lines.append(line)

        content = "\n".join(fixed_lines)

        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True

        return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main():
    """Fix indented ellipsis in all protocol files."""
    protocol_dir = Path("src/omnibase_spi/protocols")

    if not protocol_dir.exists():
        print(f"Protocol directory not found: {protocol_dir}")
        return

    python_files = list(protocol_dir.rglob("*.py"))
    modified_count = 0

    print(f"Processing {len(python_files)} Python files...")

    for file_path in python_files:
        if fix_indented_ellipsis(file_path):
            print(f"Fixed: {file_path}")
            modified_count += 1

    print(f"\nCompleted! Modified {modified_count} files.")


if __name__ == "__main__":
    main()
