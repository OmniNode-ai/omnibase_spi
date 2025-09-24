#!/usr/bin/env python3
"""
Validate and optionally fix alphabetical ordering of __all__ lists in Python files.

This script checks that __all__ lists are alphabetically ordered (case-insensitive)
and can optionally fix the ordering automatically.

Usage:
    python validate_alphabetical_all.py [--fix] [file1 file2 ...]

    --fix: Automatically fix ordering issues

If no files specified, checks all Python files in src/omnibase_spi/protocols/
"""

import argparse
import ast
import sys
from pathlib import Path
from typing import List, Optional, Tuple


def extract_all_list(file_path: Path) -> Optional[Tuple[ast.List, int]]:
    """Extract __all__ list from Python file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            tree = ast.parse(content)
    except (OSError, SyntaxError) as e:
        print(f"Error parsing {file_path}: {e}")
        return None

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    if isinstance(node.value, ast.List):
                        return node.value, node.lineno
    return None


def get_string_items(list_node: ast.List) -> List[str]:
    """Extract string items from AST List node."""
    items = []
    for elt in list_node.elts:
        if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
            items.append(elt.value)
        elif isinstance(elt, ast.Str):  # For Python < 3.8 compatibility
            items.append(elt.s)
    return items


def check_alphabetical_order(file_path: Path, fix: bool = False) -> bool:
    """
    Check if __all__ list is alphabetically ordered.

    Args:
        file_path: Path to Python file
        fix: If True, fix ordering issues automatically

    Returns:
        True if ordered (or fixed), False if not ordered
    """
    result = extract_all_list(file_path)
    if result is None:
        return True  # No __all__ list found, nothing to check

    list_node, line_no = result
    items = get_string_items(list_node)

    if not items:
        return True  # Empty __all__ list

    # Case-insensitive alphabetical sorting
    sorted_items = sorted(items, key=str.lower)

    if items == sorted_items:
        try:
            rel_path = file_path.relative_to(Path.cwd())
        except ValueError:
            rel_path = file_path
        print(f"✅ {rel_path}: __all__ is alphabetically ordered")
        return True

    if not fix:
        try:
            rel_path = file_path.relative_to(Path.cwd())
        except ValueError:
            rel_path = file_path
        print(f"❌ {rel_path}: __all__ is NOT alphabetically ordered")

        # Show first few differences
        differences = []
        for i, (actual, expected) in enumerate(zip(items, sorted_items)):
            if actual != expected:
                differences.append(
                    f"  Position {i+1}: got '{actual}', expected '{expected}'"
                )
            if len(differences) >= 3:  # Show max 3 differences
                break

        for diff in differences:
            print(diff)
        if len(items) - len([a for a, e in zip(items, sorted_items) if a == e]) > 3:
            print(
                f"  ... and {len(items) - len([a for a, e in zip(items, sorted_items) if a == e]) - 3} more differences"
            )

        return False

    # Fix the ordering
    try:
        rel_path = file_path.relative_to(Path.cwd())
    except ValueError:
        rel_path = file_path
    print(f"🔧 {rel_path}: Fixing __all__ alphabetical ordering")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Find the __all__ list in the file
        in_all_list = False
        all_start_line = None
        all_end_line = None
        indent_level = ""

        for i, line in enumerate(lines):
            if "__all__ = [" in line:
                in_all_list = True
                all_start_line = i
                # Detect indentation level from the line
                indent_level = line[: len(line) - len(line.lstrip())]
                continue

            if in_all_list:
                if "]" in line and not line.strip().startswith("#"):
                    all_end_line = i
                    break

        if all_start_line is None or all_end_line is None:
            print(f"  Error: Could not find __all__ list boundaries")
            return False

        # Generate new __all__ list with proper formatting
        new_lines = []
        new_lines.append(f"{indent_level}__all__ = [\n")

        for item in sorted_items:
            new_lines.append(f'{indent_level}    "{item}",\n')

        new_lines.append(f"{indent_level}]\n")

        # Replace the old __all__ list
        updated_lines = lines[:all_start_line] + new_lines + lines[all_end_line + 1 :]

        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(updated_lines)

        print(f"  ✅ Fixed: reordered {len(items)} items")
        return True

    except Exception as e:
        print(f"  Error fixing {file_path}: {e}")
        return False


def find_python_files(root_dir: Path) -> List[Path]:
    """Find all Python __init__.py files in protocols directory."""
    python_files = []
    if root_dir.is_file() and root_dir.suffix == ".py":
        python_files.append(root_dir)
    else:
        # Find all __init__.py files in protocols directory
        protocols_dir = root_dir / "src" / "omnibase_spi" / "protocols"
        if protocols_dir.exists():
            python_files.extend(protocols_dir.rglob("__init__.py"))

    return sorted(python_files)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate alphabetical ordering of __all__ lists",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Check all protocol __init__.py files
    python scripts/validate_alphabetical_all.py

    # Check specific files
    python scripts/validate_alphabetical_all.py src/omnibase_spi/protocols/types/__init__.py

    # Fix ordering issues automatically
    python scripts/validate_alphabetical_all.py --fix

    # Fix specific file
    python scripts/validate_alphabetical_all.py --fix src/omnibase_spi/protocols/__init__.py
        """,
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically fix alphabetical ordering issues",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Python files to check (default: all protocol __init__.py files)",
    )

    args = parser.parse_args()

    # Determine files to check
    if args.files:
        files_to_check = [Path(f) for f in args.files]
    else:
        files_to_check = find_python_files(Path.cwd())

    if not files_to_check:
        print("No Python files found to check")
        return 1

    print(f"Checking {len(files_to_check)} files for __all__ alphabetical ordering...")
    print()

    all_ordered = True
    files_processed = 0

    for file_path in files_to_check:
        if not file_path.exists():
            print(f"⚠️  File not found: {file_path}")
            continue

        is_ordered = check_alphabetical_order(file_path, fix=args.fix)
        if not is_ordered:
            all_ordered = False
        files_processed += 1

    print()
    print(f"Processed {files_processed} files")

    if all_ordered:
        print("✅ All __all__ lists are alphabetically ordered!")
        return 0
    else:
        if args.fix:
            print("🔧 Fixed alphabetical ordering issues")
            return 0
        else:
            print("❌ Found files with non-alphabetical __all__ lists")
            print("Run with --fix to automatically correct the ordering")
            return 1


if __name__ == "__main__":
    sys.exit(main())
