#!/usr/bin/env python3
"""
Fix hardcoded default values in SPI protocols.
Converts patterns like `param: int = 72` to `param: int | None = None`
"""

import re
import sys
from pathlib import Path


def fix_hardcoded_defaults(file_path: Path) -> tuple[bool, int]:
    """
    Fix hardcoded default values in a protocol file.

    Returns:
        (changed, num_fixes) - whether file was modified and number of fixes
    """
    with open(file_path, "r") as f:
        content = f.read()

    original_content = content
    fixes = 0

    # Pattern 1: param: int = <number>
    pattern1 = r"(\w+:\s*int)\s*=\s*\d+"

    def replace1(match):
        nonlocal fixes
        fixes += 1
        return f"{match.group(1)} | None = None"

    content = re.sub(pattern1, replace1, content)

    # Pattern 2: param: str = "string"
    pattern2 = r'(\w+:\s*str)\s*=\s*["\'][^"\']*["\']'

    def replace2(match):
        nonlocal fixes
        fixes += 1
        return f"{match.group(1)} | None = None"

    content = re.sub(pattern2, replace2, content)

    # Pattern 3: param: float = <number>
    pattern3 = r"(\w+:\s*float)\s*=\s*[\d.]+"

    def replace3(match):
        nonlocal fixes
        fixes += 1
        return f"{match.group(1)} | None = None"

    content = re.sub(pattern3, replace3, content)

    # Pattern 4: param: bool = True/False
    pattern4 = r"(\w+:\s*bool)\s*=\s*(True|False)"

    def replace4(match):
        nonlocal fixes
        fixes += 1
        return f"{match.group(1)} | None = None"

    content = re.sub(pattern4, replace4, content)

    if content != original_content:
        with open(file_path, "w") as f:
            f.write(content)
        return True, fixes

    return False, 0


def main():
    src_dir = Path("src/omnibase_spi/protocols")

    if not src_dir.exists():
        print(f"Error: {src_dir} not found")
        sys.exit(1)

    total_files = 0
    total_fixes = 0

    # Process all protocol files
    for proto_file in src_dir.rglob("protocol_*.py"):
        changed, fixes = fix_hardcoded_defaults(proto_file)
        if changed:
            total_files += 1
            total_fixes += fixes
            print(
                f"✓ Fixed {fixes} violations in {proto_file.relative_to(src_dir.parent.parent)}"
            )

    print(f"\n✅ Fixed {total_fixes} hardcoded defaults across {total_files} files")


if __name__ == "__main__":
    main()
