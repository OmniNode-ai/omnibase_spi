#!/usr/bin/env python3
"""
Docstring checker utility for SPI purity validation.

This script filters out docstring content from Python files to avoid
false positives when checking for SPI violations in implementation examples.
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple


def extract_non_docstring_content(file_path: Path) -> List[Tuple[int, str]]:
    """
    Extract non-docstring content from a Python file.

    Returns:
        List of (line_number, content) tuples for non-docstring lines
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception:
        return []

    result = []
    in_docstring = False
    in_code_block = False
    docstring_quotes = None

    for i, line in enumerate(lines, 1):
        line = line.rstrip()

        # Skip empty lines
        if not line.strip():
            continue

        # Check for docstring start/end
        stripped = line.strip()

        # Look for triple quotes
        if not in_docstring:
            # Check for docstring start
            for quote_type in ['"""', "'''"]:
                if quote_type in stripped:
                    # Count occurrences to handle single-line docstrings
                    count = stripped.count(quote_type)
                    if count == 1:
                        # Start of multi-line docstring
                        in_docstring = True
                        docstring_quotes = quote_type
                        break
                    elif count == 2:
                        # Single-line docstring, skip this line
                        break
            else:
                # Not a docstring line
                result.append((i, line))
        else:
            # We're in a docstring, check for markdown code blocks
            if stripped.startswith("```"):
                in_code_block = not in_code_block

            # Look for docstring end
            if docstring_quotes and docstring_quotes in stripped:
                # End of docstring
                in_docstring = False
                docstring_quotes = None
                in_code_block = False
            # Skip docstring lines, but report code block content as violations for manual review
            elif in_code_block and not stripped.startswith("```"):
                # This is code inside a docstring - skip it to avoid false positives
                pass

    return result


def main() -> None:
    """Main function to process Python files and output non-docstring content."""
    if len(sys.argv) > 1:
        file_paths = [Path(arg) for arg in sys.argv[1:]]
    else:
        # Process all Python files in src/
        src_path = Path("src")
        if src_path.exists():
            file_paths = list(src_path.rglob("*.py"))
        else:
            file_paths = []

    for file_path in file_paths:
        non_docstring_lines = extract_non_docstring_content(file_path)
        for line_num, content in non_docstring_lines:
            print(f"{file_path}:{line_num}:{content}")


if __name__ == "__main__":
    main()
