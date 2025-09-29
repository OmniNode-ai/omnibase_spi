#!/usr/bin/env python3
"""Simple SPI validation script."""

import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple


def check_namespace_violations(src_dir: Path) -> List[str]:
    """Check for namespace violations."""
    violations = []

    for py_file in src_dir.rglob("*.py"):
        if "__pycache__" in str(py_file) or "__init__.py" in str(py_file):
            continue

        with open(py_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Get the current namespace from file path
        rel_path = py_file.relative_to(src_dir)
        parts = rel_path.parts[:-1]  # Remove file name
        if len(parts) >= 1:
            current_namespace = parts[0]
        else:
            continue

        # Check for cross-namespace imports (not in TYPE_CHECKING)
        lines = content.split("\n")
        in_type_checking = False

        for i, line in enumerate(lines, 1):
            # Track TYPE_CHECKING blocks
            if "if TYPE_CHECKING:" in line:
                in_type_checking = True
            elif in_type_checking and line and not line.startswith(" ") and not line.startswith("\t"):
                in_type_checking = False

            # Skip if in TYPE_CHECKING block
            if in_type_checking:
                continue

            # Check for cross-namespace imports
            if line.strip().startswith("from omnibase_spi.protocols."):
                match = re.match(r"from omnibase_spi\.protocols\.(\w+)", line)
                if match:
                    imported_namespace = match.group(1)
                    # Allow types imports and same-namespace imports
                    if imported_namespace not in ["types", current_namespace]:
                        violations.append(f"{py_file}:{i} - Import from '{imported_namespace}' violates namespace isolation")

    return violations


def check_async_properties(src_dir: Path) -> List[str]:
    """Check for invalid @property async def patterns."""
    violations = []

    for py_file in src_dir.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue

        with open(py_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Simple regex to find @property followed by async def
        pattern = r"@property\s*\n\s*async\s+def"
        matches = re.finditer(pattern, content)

        for match in matches:
            line_num = content[:match.start()].count("\n") + 1
            violations.append(f"{py_file}:{line_num} - Invalid '@property async def' pattern")

    return violations


def check_unquoted_forward_refs(src_dir: Path) -> List[str]:
    """Check for unquoted forward references when using TYPE_CHECKING."""
    violations = []

    for py_file in src_dir.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue

        with open(py_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Find TYPE_CHECKING imports
        type_checking_imports = set()
        if "if TYPE_CHECKING:" in content:
            # Extract imports from TYPE_CHECKING block
            lines = content.split("\n")
            in_type_checking = False

            for line in lines:
                if "if TYPE_CHECKING:" in line:
                    in_type_checking = True
                elif in_type_checking and line and not line.startswith(" ") and not line.startswith("\t"):
                    in_type_checking = False
                elif in_type_checking and "import" in line:
                    # Extract imported names
                    if "from" in line and "import" in line:
                        match = re.search(r"import\s+(.+)", line)
                        if match:
                            imports = match.group(1)
                            # Handle multiple imports
                            for imp in imports.split(","):
                                imp = imp.strip()
                                if "(" in imp:  # Multi-line import start
                                    imp = imp.replace("(", "").strip()
                                if ")" in imp:  # Multi-line import end
                                    imp = imp.replace(")", "").strip()
                                if imp:
                                    type_checking_imports.add(imp)

        # Check for unquoted usage
        if type_checking_imports:
            lines = content.split("\n")
            for i, line in enumerate(lines, 1):
                for imported in type_checking_imports:
                    # Look for unquoted usage in type hints
                    pattern = rf":\s*{re.escape(imported)}(?:\[|,|\s|$)"
                    if re.search(pattern, line):
                        # Check if it's already quoted
                        quoted_pattern = rf'["\'].*{re.escape(imported)}.*["\']'
                        if not re.search(quoted_pattern, line):
                            violations.append(f"{py_file}:{i} - Unquoted TYPE_CHECKING import '{imported}'")

    return violations


def main():
    src_dir = Path("src/omnibase_spi/protocols")

    print("Running SPI Validation...")
    print("=" * 60)

    # Check namespace violations
    print("\nChecking namespace violations...")
    namespace_violations = check_namespace_violations(src_dir)
    if namespace_violations:
        print(f"Found {len(namespace_violations)} namespace violations:")
        for v in namespace_violations[:10]:  # Show first 10
            print(f"  {v}")
        if len(namespace_violations) > 10:
            print(f"  ... and {len(namespace_violations) - 10} more")
    else:
        print("✓ No namespace violations found")

    # Check async properties
    print("\nChecking async property patterns...")
    async_violations = check_async_properties(src_dir)
    if async_violations:
        print(f"Found {len(async_violations)} async property violations:")
        for v in async_violations[:10]:
            print(f"  {v}")
        if len(async_violations) > 10:
            print(f"  ... and {len(async_violations) - 10} more")
    else:
        print("✓ No async property violations found")

    # Check forward references
    print("\nChecking forward reference quotes...")
    ref_violations = check_unquoted_forward_refs(src_dir)
    if ref_violations:
        print(f"Found {len(ref_violations)} unquoted forward references:")
        for v in ref_violations[:10]:
            print(f"  {v}")
        if len(ref_violations) > 10:
            print(f"  ... and {len(ref_violations) - 10} more")
    else:
        print("✓ All forward references properly quoted")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY:")
    total_violations = len(namespace_violations) + len(async_violations) + len(ref_violations)
    print(f"Total violations: {total_violations}")

    if total_violations == 0:
        print("✅ All validation checks passed!")
    else:
        print(f"❌ Found {total_violations} issues that need fixing")


if __name__ == "__main__":
    main()