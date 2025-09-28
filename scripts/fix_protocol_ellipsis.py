#!/usr/bin/env python3
"""
Fix protocol methods missing ellipsis implementations.

This script identifies protocol methods with docstrings but missing ellipsis
implementations and adds the required '...' to complete the protocol contract.
"""

import re
import sys
from pathlib import Path
from typing import List


def fix_protocol_ellipsis_in_file(file_path: Path) -> bool:
    """Fix missing ellipsis in protocol methods for a single file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False

    modified = False
    new_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]
        new_lines.append(line)

        # Check if this line starts a method definition
        if re.match(r"^\s+def\s+\w+.*:\s*$", line.strip()) or re.match(
            r"^\s+async\s+def\s+\w+.*:\s*$", line.strip()
        ):
            method_indent = len(line) - len(line.lstrip())

            # Look ahead to see if there's a docstring
            j = i + 1
            found_docstring = False
            docstring_end = -1

            # Skip any empty lines immediately after method definition
            while j < len(lines) and lines[j].strip() == "":
                new_lines.append(lines[j])
                j += 1

            # Check if the next non-empty line starts a docstring
            if j < len(lines):
                next_line = lines[j].strip()
                if next_line.startswith('"""') or next_line.startswith("'''"):
                    found_docstring = True
                    quote_type = '"""' if next_line.startswith('"""') else "'''"

                    # Find the end of the docstring
                    if next_line.count(quote_type) >= 2:
                        # Single-line docstring
                        docstring_end = j
                    else:
                        # Multi-line docstring - find closing quotes
                        for k in range(j + 1, len(lines)):
                            if quote_type in lines[k]:
                                docstring_end = k
                                break

            # If we found a docstring, check if there's an ellipsis after it
            if found_docstring and docstring_end >= 0:
                # Add all lines from current position to end of docstring
                for k in range(i + 1, docstring_end + 1):
                    new_lines.append(lines[k])

                # Look for ellipsis after docstring
                ellipsis_found = False
                next_content_line = docstring_end + 1

                # Skip empty lines after docstring
                while (
                    next_content_line < len(lines)
                    and lines[next_content_line].strip() == ""
                ):
                    new_lines.append(lines[next_content_line])
                    next_content_line += 1

                # Check if the next non-empty line is ellipsis or another method/property
                if next_content_line < len(lines):
                    next_line = lines[next_content_line].strip()
                    if next_line == "...":
                        ellipsis_found = True
                    elif (
                        next_line.startswith("def ")
                        or next_line.startswith("async def ")
                        or next_line.startswith("@")
                        or next_line.startswith("class ")
                        or len(lines[next_content_line])
                        - len(lines[next_content_line].lstrip())
                        <= method_indent
                    ):
                        # Next line is another method/property or at same/higher level - missing ellipsis
                        ellipsis_found = False
                    else:
                        # Some other content - likely missing ellipsis
                        ellipsis_found = False

                # If no ellipsis found, add it
                if not ellipsis_found:
                    # Add ellipsis with proper indentation
                    ellipsis_line = " " * (method_indent + 4) + "...\n"
                    new_lines.append(ellipsis_line)
                    print(f"  Added missing ellipsis after method at line {i+1}")
                    modified = True

                # Continue from after the docstring
                i = next_content_line - 1
            else:
                # No docstring found, check if method already has ellipsis on same line
                if not line.rstrip().endswith("..."):
                    # Check next line for ellipsis
                    if i + 1 < len(lines) and lines[i + 1].strip() == "...":
                        # Ellipsis is on next line, that's fine
                        pass
                    else:
                        # Missing ellipsis for method without docstring
                        # This case should be rare since most should have ellipsis on same line
                        pass

        i += 1

    if modified:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            print(f"✅ Fixed ellipsis in {file_path}")
            return True
        except Exception as e:
            print(f"Error writing {file_path}: {e}")
            return False

    return False


def main():
    """Main function to fix protocol ellipsis across all protocol files."""

    # Find all protocol files
    spi_root = Path(__file__).parent.parent / "src" / "omnibase_spi" / "protocols"

    if not spi_root.exists():
        print(f"❌ SPI protocols directory not found: {spi_root}")
        sys.exit(1)

    protocol_files = list(spi_root.rglob("protocol_*.py"))

    if not protocol_files:
        print(f"❌ No protocol files found in {spi_root}")
        sys.exit(1)

    print(f"🔍 Found {len(protocol_files)} protocol files to fix")

    fixed_count = 0

    for file_path in sorted(protocol_files):
        print(f"📄 Processing {file_path.name}...")
        if fix_protocol_ellipsis_in_file(file_path):
            fixed_count += 1

    print(f"\n✅ Successfully fixed ellipsis in {fixed_count} files")
    print(f"📊 Total files processed: {len(protocol_files)}")


if __name__ == "__main__":
    main()
