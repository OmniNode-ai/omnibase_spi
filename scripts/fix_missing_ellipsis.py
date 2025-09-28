#!/usr/bin/env python3
"""
Fix protocol methods missing ellipsis after docstrings.

This script finds protocol methods that have docstrings but are missing
the required '...' implementation and adds them.
"""

import re
import sys
from pathlib import Path


def fix_missing_ellipsis_in_file(file_path: Path) -> bool:
    """Fix missing ellipsis after docstrings in a single file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False

    original_content = content

    # Pattern 1: Single-line docstring without ellipsis
    # Example:
    # def method():
    #     """Docstring."""
    #
    # Should become:
    # def method():
    #     """Docstring."""
    #     ...

    pattern1 = re.compile(
        r'((?:async\s+)?def\s+\w+.*?:\s*\n\s*"""[^"]*?"""\s*)\n(?!\s*\.\.\.)',
        re.MULTILINE | re.DOTALL,
    )

    def replace1(match):
        return match.group(1) + "\n        ...\n"

    content = pattern1.sub(replace1, content)

    # Pattern 2: Multi-line docstring without ellipsis
    # Example:
    # def method():
    #     """
    #     Multi-line docstring.
    #     """
    #
    # Should become:
    # def method():
    #     """
    #     Multi-line docstring.
    #     """
    #     ...

    pattern2 = re.compile(
        r'((?:async\s+)?def\s+\w+.*?:\s*\n\s*"""\s*\n.*?\n\s*"""\s*)\n(?!\s*\.\.\.)',
        re.MULTILINE | re.DOTALL,
    )

    def replace2(match):
        return match.group(1) + "\n        ...\n"

    content = pattern2.sub(replace2, content)

    # Pattern 3: Single quotes version for single-line
    pattern3 = re.compile(
        r"((?:async\s+)?def\s+\w+.*?:\s*\n\s*'''[^']*?'''\s*)\n(?!\s*\.\.\.)",
        re.MULTILINE | re.DOTALL,
    )

    content = pattern3.sub(replace1, content)

    # Pattern 4: Single quotes version for multi-line
    pattern4 = re.compile(
        r"((?:async\s+)?def\s+\w+.*?:\s*\n\s*'''\s*\n.*?\n\s*'''\s*)\n(?!\s*\.\.\.)",
        re.MULTILINE | re.DOTALL,
    )

    content = pattern4.sub(replace2, content)

    if content != original_content:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            # Count how many fixes were made
            fixes = (
                len(pattern1.findall(original_content))
                + len(pattern2.findall(original_content))
                + len(pattern3.findall(original_content))
                + len(pattern4.findall(original_content))
            )

            print(f"  ✅ Fixed {fixes} missing ellipsis in {file_path.name}")
            return True
        except Exception as e:
            print(f"Error writing {file_path}: {e}")
            return False

    return False


def main():
    """Main function to fix missing ellipsis across all protocol files."""

    # Find all protocol files
    spi_root = Path(__file__).parent.parent / "src" / "omnibase_spi" / "protocols"

    if not spi_root.exists():
        print(f"❌ SPI protocols directory not found: {spi_root}")
        sys.exit(1)

    protocol_files = list(spi_root.rglob("protocol_*.py"))

    if not protocol_files:
        print(f"❌ No protocol files found in {spi_root}")
        sys.exit(1)

    print(f"🔍 Found {len(protocol_files)} protocol files to process")

    fixed_count = 0

    for file_path in sorted(protocol_files):
        print(f"📄 Processing {file_path.name}...")
        if fix_missing_ellipsis_in_file(file_path):
            fixed_count += 1

    print(f"\n✅ Successfully fixed ellipsis in {fixed_count} files")
    print(f"📊 Total files processed: {len(protocol_files)}")


if __name__ == "__main__":
    main()
