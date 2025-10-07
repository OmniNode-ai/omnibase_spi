#!/usr/bin/env python3
"""
Comprehensive script to fix all missing ellipsis in Protocol methods.
Handles various patterns including single-line and multi-line docstrings.
"""

import os
import re
from pathlib import Path


def fix_missing_ellipsis_in_file(file_path: Path) -> tuple[bool, int]:
    """Fix missing ellipsis in a single file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content
        fixes_applied = 0

        # Pattern 1: Methods with single-line docstrings missing ellipsis
        # Example: def method():\n    """Single line doc."""\n\n
        pattern1 = re.compile(
            r'((?:async\s+)?def\s+\w+.*?:\s*\n\s*"""[^"]*?"""\s*)\n(?!\s*\.\.\.)',
            re.MULTILINE | re.DOTALL,
        )

        def replace1(match):
            nonlocal fixes_applied
            fixes_applied += 1
            return match.group(1) + "\n        ...\n"

        content = pattern1.sub(replace1, content)

        # Pattern 2: Methods with multi-line docstrings missing ellipsis
        # Example: def method():\n    """\n    Multi line\n    docstring.\n    """\n\n
        pattern2 = re.compile(
            r'((?:async\s+)?def\s+\w+.*?:\s*\n\s*"""\s*\n.*?\n\s*"""\s*)\n(?!\s*\.\.\.)',
            re.MULTILINE | re.DOTALL,
        )

        def replace2(match):
            nonlocal fixes_applied
            fixes_applied += 1
            return match.group(1) + "\n        ...\n"

        content = pattern2.sub(replace2, content)

        # Pattern 3: Property methods missing ellipsis after docstrings
        # Example: @property\n    def prop(self):\n        """Property doc."""\n\n
        pattern3 = re.compile(
            r'(@property\s*\n\s*def\s+\w+.*?:\s*\n\s*"""[^"]*?"""\s*)\n(?!\s*\.\.\.)',
            re.MULTILINE | re.DOTALL,
        )

        def replace3(match):
            nonlocal fixes_applied
            fixes_applied += 1
            return match.group(1) + "\n        ...\n"

        content = pattern3.sub(replace3, content)

        # Pattern 4: Methods that end with docstring but have no following content
        # Look for methods that end a file or class without ellipsis
        pattern4 = re.compile(
            r'((?:async\s+)?def\s+\w+.*?:\s*\n\s*""".*?"""\s*)(\n\s*(?:def\s|class\s|@|\Z))',
            re.MULTILINE | re.DOTALL,
        )

        def replace4(match):
            nonlocal fixes_applied
            fixes_applied += 1
            return match.group(1) + "\n        ..." + match.group(2)

        content = pattern4.sub(replace4, content)

        # Only write if changes were made
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True, fixes_applied

        return False, 0

    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False, 0


def main():
    """Main function to fix all protocol files."""
    protocols_dir = Path("src/omnibase_spi/protocols")

    if not protocols_dir.exists():
        print(f"❌ Protocols directory not found: {protocols_dir}")
        return

    protocol_files = []
    for pattern in ["**/*.py"]:
        protocol_files.extend(protocols_dir.glob(pattern))

    protocol_files = [f for f in protocol_files if f.is_file()]

    print(f"🔍 Found {len(protocol_files)} protocol files to process")

    total_fixes = 0
    files_modified = 0

    for file_path in sorted(protocol_files):
        try:
            modified, fixes = fix_missing_ellipsis_in_file(file_path)
            if modified:
                files_modified += 1
                total_fixes += fixes
                print(f"✅ Fixed {fixes} ellipsis in {file_path.name}")
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")

    print(f"\n📊 Summary:")
    print(f"   Files processed: {len(protocol_files)}")
    print(f"   Files modified: {files_modified}")
    print(f"   Total ellipsis added: {total_fixes}")


if __name__ == "__main__":
    main()
