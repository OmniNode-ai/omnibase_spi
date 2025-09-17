#!/usr/bin/env python3
"""
AST-based Forbidden Pattern Validator for SPI Code Standards.

Uses Python AST parsing to check only actual code patterns, not comments or docstrings.
This prevents false positives from documentation while enforcing SPI standards.
"""

import ast
import sys
from pathlib import Path
from typing import List, NamedTuple, Set, Union


class Violation(NamedTuple):
    """Represents a validation violation."""

    file_path: str
    line_number: int
    description: str
    code_snippet: str


class ForbiddenPatternValidator(ast.NodeVisitor):
    """AST visitor that checks for forbidden patterns in actual code only."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.violations: List[Violation] = []
        self.source_lines: List[str] = []

    def validate_file(self, content: str) -> List[Violation]:
        """Validate a Python file's AST for forbidden patterns."""
        self.source_lines = content.splitlines()

        try:
            tree = ast.parse(content, filename=self.file_path)
            self.visit(tree)
        except SyntaxError as e:
            self.violations.append(
                Violation(
                    self.file_path,
                    e.lineno or 1,
                    f"Syntax error: {e.msg}",
                    self.get_line(e.lineno or 1),
                )
            )

        return self.violations

    def get_line(self, line_no: int) -> str:
        """Get source code line by number."""
        if 1 <= line_no <= len(self.source_lines):
            return self.source_lines[line_no - 1].strip()
        return ""

    def add_violation(self, node: ast.AST, description: str) -> None:
        """Add a violation for an AST node."""
        line_no = getattr(node, "lineno", 1)
        self.violations.append(
            Violation(self.file_path, line_no, description, self.get_line(line_no))
        )

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Check class definitions for forbidden patterns."""
        # Check for "Model" prefix in class names (real classes, not in comments)
        if node.name.startswith("Model") and len(node.name) > 5:
            self.add_violation(
                node,
                '"Model" prefix in class names (use descriptive names without "Model")',
            )

        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        """Check name references for forbidden patterns."""
        # Check for standalone "model" usage in variable names or identifiers
        if node.id == "model":
            # Only flag if it's being used as a variable/identifier, not in annotations
            if isinstance(node.ctx, (ast.Store, ast.Load)):
                self.add_violation(
                    node,
                    '"model" terminology (use "data", "object", or specific type names)',
                )

        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        """Check subscript expressions like Union[...], Optional[...]."""
        # Check for Union types with protocols
        if (
            isinstance(node.value, ast.Name)
            and node.value.id == "Union"
            and isinstance(node.slice, ast.Tuple)
        ):

            # Check if any element in Union contains "Protocol"
            for elt in node.slice.elts:
                if self._contains_protocol_reference(elt):
                    self.add_violation(
                        node,
                        "Union types with protocols (create a common protocol instead)",
                    )
                    break

        self.generic_visit(node)

    def _contains_protocol_reference(self, node: ast.AST) -> bool:
        """Check if AST node contains a Protocol reference."""
        if isinstance(node, ast.Name):
            return "Protocol" in node.id
        elif isinstance(node, ast.Attribute):
            return "Protocol" in node.attr or self._contains_protocol_reference(
                node.value
            )
        elif isinstance(node, ast.Subscript):
            return self._contains_protocol_reference(node.value) or (
                hasattr(node.slice, "value")
                and self._contains_protocol_reference(node.slice.value)
            )
        return False

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Check function definitions for problematic Any usage."""
        # For SPI protocols, Any is often legitimate for generic contracts
        # Only flag Any usage in non-protocol contexts or suspicious patterns

        # Skip if this is in a protocol file (legitimate usage)
        if "/protocols/" in self.file_path:
            # Allow Any in protocol methods - they define generic contracts
            pass
        else:
            # In implementation files, be stricter about Any usage
            for arg in node.args.args:
                if (
                    hasattr(arg, "annotation")
                    and arg.annotation
                    and isinstance(arg.annotation, ast.Name)
                    and arg.annotation.id == "Any"
                ):
                    # Allow Any in **kwargs and *args
                    if not (arg.arg.startswith("kwargs") or arg.arg.startswith("args")):
                        self.add_violation(
                            arg,
                            "Problematic Any usage in function parameters (use specific types)",
                        )

        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Check imports for external dependencies."""
        if node.module:
            forbidden_imports = {
                "requests",
                "numpy",
                "pandas",
                "fastapi",
                "flask",
                "django",
                "sqlalchemy",
                "redis",
                "boto3",
                "celery",
            }

            if node.module in forbidden_imports or (
                "." in node.module and node.module.split(".")[0] in forbidden_imports
            ):
                self.add_violation(
                    node,
                    f"external dependencies (SPI should be dependency-free): {node.module}",
                )

        self.generic_visit(node)


def validate_python_files(src_dir: Path) -> List[Violation]:
    """Validate all Python files in the source directory."""
    all_violations: List[Violation] = []

    python_files = list(src_dir.rglob("*.py"))

    if not python_files:
        print("No Python files found in src/")
        return all_violations

    print(f"Checking files: {len(python_files)} Python files")

    for file_path in python_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            validator = ForbiddenPatternValidator(str(file_path))
            violations = validator.validate_file(content)
            all_violations.extend(violations)

        except Exception as e:
            all_violations.append(
                Violation(str(file_path), 1, f"File processing error: {e}", "")
            )

    return all_violations


def main() -> None:
    """Main validation function."""
    print("🔍 Validating forbidden patterns in SPI codebase (AST-based)...")

    # Get source directory
    src_dir = Path("src")
    if not src_dir.exists():
        print("❌ src/ directory not found")
        sys.exit(1)

    # Validate files
    violations = validate_python_files(src_dir)

    # Group violations by type
    violation_groups: dict[str, List[Violation]] = {}
    for violation in violations:
        category = violation.description.split("(")[0].strip().strip('"')
        if category not in violation_groups:
            violation_groups[category] = []
        violation_groups[category].append(violation)

    print("\n🚫 Checking for forbidden patterns...")

    # Report results
    total_violations = 0
    for category, group_violations in violation_groups.items():
        print(f"  Checking for: {category}")
        if group_violations:
            total_violations += len(group_violations)
            print(f"\033[0;31m❌ Found forbidden pattern: {category}\033[0m")
            for violation in group_violations[:5]:  # Limit output
                print(
                    f"    {violation.file_path}:{violation.line_number}: {violation.code_snippet}"
                )
            if len(group_violations) > 5:
                print(f"    ... and {len(group_violations) - 5} more")
        else:
            print(f"\033[0;32m✅ No issues found: {category}\033[0m")

    # Check for missing patterns (ensure all expected checks ran)
    expected_patterns = {
        "model",
        "Union types with protocols",
        "Model",
        "Problematic Any usage",
        "external dependencies",
    }

    found_patterns = set(violation_groups.keys())
    for pattern in expected_patterns:
        if not any(pattern in category for category in found_patterns):
            print(f"  Checking for: {pattern}")
            print(f"\033[0;32m✅ No issues found: {pattern}\033[0m")

    # Summary
    print()
    if total_violations == 0:
        print("\033[0;32m✅ All validation checks passed!\033[0m")
        print("SPI codebase follows forbidden pattern standards.")
        sys.exit(0)
    else:
        print(
            f"\033[0;31m❌ Found {total_violations} forbidden pattern violation(s)\033[0m"
        )
        print("\nTo fix these issues:")
        print("  1. Replace 'model' with 'data', 'object', or specific type names")
        print("  2. Replace Union types of protocols with common protocol interfaces")
        print("  3. Remove 'Model' prefixes from class names")
        print("  4. Replace Any with specific types or object")
        print("  5. Remove external dependencies from SPI")
        sys.exit(1)


if __name__ == "__main__":
    main()
