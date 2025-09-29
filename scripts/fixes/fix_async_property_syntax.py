#!/usr/bin/env python3
"""
Fix invalid @property async def syntax created by auto-fix engine.

The auto-fix engine incorrectly combined @property with async def, which is invalid Python syntax.
This script fixes these issues by deciding whether to:
1. Remove @property and keep async def (for I/O operations)
2. Remove async and keep @property (for simple getters)
"""
import re
import sys
from pathlib import Path
from typing import List, Tuple


def fix_invalid_property_async_syntax(file_path: Path) -> Tuple[bool, List[str]]:
    """
    Fix invalid @property async def syntax in a file.

    Returns:
        (changed, fixes_applied): Boolean indicating if file was changed, list of fixes
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content
        fixes_applied = []

        # Find pattern: @property followed by async def
        # This is invalid syntax that needs to be fixed
        lines = content.split("\n")
        i = 0

        while i < len(lines) - 1:
            line = lines[i].strip()
            next_line = lines[i + 1].strip() if i + 1 < len(lines) else ""

            # Look for @property followed by async def
            if (
                line == "@property"
                and next_line.startswith("async def ")
                and next_line.endswith(": ...")
            ):

                # Extract method name for analysis
                method_match = re.search(r"async def (\w+)", next_line)
                if method_match:
                    method_name = method_match.group(1)

                    # Decide whether this should be async or property based on method name
                    if should_be_async_method(method_name):
                        # Remove @property, keep async def
                        lines[i] = ""  # Remove @property line
                        fixes_applied.append(
                            f"Removed @property from async method {method_name}"
                        )
                    else:
                        # Remove async, keep @property
                        lines[i + 1] = next_line.replace("async def ", "def ")
                        fixes_applied.append(
                            f"Removed async from property {method_name}"
                        )

                    i += 2  # Skip both lines we just processed
                    continue

            i += 1

        # Clean up empty lines that might have been created
        content = "\n".join(lines)
        content = re.sub(
            r"\n\n\n+", "\n\n", content
        )  # Replace multiple newlines with double

        # Write back if changed
        if content != original_content and fixes_applied:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True, fixes_applied

        return False, []

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False, []


def should_be_async_method(method_name: str) -> bool:
    """
    Determine if a method should be async based on its name and purpose.

    Returns True if method should be async, False if it should be a property.
    """
    # Methods that typically involve I/O or complex operations (should be async)
    async_indicators = [
        "get_",
        "fetch_",
        "load_",
        "save_",
        "store_",
        "read_",
        "write_",
        "connect_",
        "disconnect_",
        "send_",
        "receive_",
        "query_",
        "execute_",
        "process_",
        "validate_",
        "calculate_",
        "analyze_",
        "compute_",
    ]

    # Simple property getters (should remain properties)
    property_indicators = [
        "threshold",
        "timeout",
        "max_",
        "min_",
        "limit",
        "count",
        "size",
        "name",
        "id",
        "type",
        "status",
        "state",
        "level",
        "rate",
    ]

    method_lower = method_name.lower()

    # Check for async indicators
    if any(method_lower.startswith(indicator) for indicator in async_indicators):
        return True

    # Check for property indicators
    if any(indicator in method_lower for indicator in property_indicators):
        return False

    # Default: if it looks like a simple getter, make it a property
    # If it has complex words, make it async
    complex_indicators = ["coordination", "metadata", "responses"]
    if any(indicator in method_lower for indicator in complex_indicators):
        return True

    return False  # Default to property for simple getters


def find_protocol_files(directory: Path) -> List[Path]:
    """Find all protocol files that might have the invalid syntax."""
    protocol_files = []

    for py_file in directory.rglob("*.py"):
        if (
            py_file.name.startswith("protocol_")
            and not py_file.name.startswith("test_")
            and "__pycache__" not in str(py_file)
        ):
            protocol_files.append(py_file)

    return sorted(protocol_files)


def main():
    """Main function to fix async property syntax issues."""
    if len(sys.argv) != 2:
        print("Usage: python fix_async_property_syntax.py <src_directory>")
        sys.exit(1)

    src_dir = Path(sys.argv[1])
    if not src_dir.exists():
        print(f"Directory {src_dir} does not exist")
        sys.exit(1)

    print("🔧 Fixing invalid @property async def syntax...")

    protocol_files = find_protocol_files(src_dir)
    total_files_changed = 0
    total_fixes = 0

    for py_file in protocol_files:
        changed, fixes = fix_invalid_property_async_syntax(py_file)
        if changed:
            total_files_changed += 1
            total_fixes += len(fixes)
            print(f"✅ Fixed {py_file.name}: {len(fixes)} fixes")
            for fix in fixes:
                print(f"   • {fix}")

    print(f"\n📊 Summary:")
    print(f"   Files processed: {len(protocol_files)}")
    print(f"   Files changed: {total_files_changed}")
    print(f"   Total fixes applied: {total_fixes}")

    if total_fixes > 0:
        print("\n✅ Invalid syntax has been fixed!")
        print("   Run the validator again to check for remaining issues.")
    else:
        print("\n✅ No invalid syntax found.")


if __name__ == "__main__":
    main()
