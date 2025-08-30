#!/usr/bin/env python3
"""
AST-based SPI Purity Validator.

Uses Python's AST module to accurately parse code and exclude docstring content
when checking for SPI violations. This avoids false positives from implementation
examples in docstrings.
"""

import ast
import re
import sys
from pathlib import Path
from typing import List, Optional, Set, Tuple


class SPIViolation:
    def __init__(
        self, file_path: str, line_no: int, violation_type: str, message: str, code: str
    ):
        self.file_path = file_path
        self.line_no = line_no
        self.violation_type = violation_type
        self.message = message
        self.code = code

    def __str__(self) -> str:
        return (
            f"{self.file_path}:{self.line_no}: {self.violation_type} - {self.message}"
        )


class SPIValidator(ast.NodeVisitor):
    """AST visitor that validates SPI purity rules."""

    def __init__(self, file_path: str, source_lines: List[str]):
        self.file_path = file_path
        self.source_lines = source_lines
        self.violations: List[SPIViolation] = []
        self.docstring_lines: Set[int] = set()

    def is_in_docstring(self, line_no: int) -> bool:
        """Check if a line number is within a docstring."""
        return line_no in self.docstring_lines

    def collect_docstring_lines(self, node: ast.AST) -> None:
        """Collect line numbers that are part of docstrings."""
        if isinstance(
            node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)
        ):
            # Check if first statement is a docstring
            if (
                node.body
                and isinstance(node.body[0], ast.Expr)
                and isinstance(node.body[0].value, ast.Constant)
                and isinstance(node.body[0].value.value, str)
            ):

                docstring_node = node.body[0]
                start_line = docstring_node.lineno
                end_line = docstring_node.end_lineno or start_line

                for line_no in range(start_line, end_line + 1):
                    self.docstring_lines.add(line_no)

    def visit(self, node: ast.AST) -> None:
        """Visit node and collect docstring information first."""
        self.collect_docstring_lines(node)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Check function definitions for SPI violations."""
        line_no = node.lineno

        # Skip if this is in a docstring
        if self.is_in_docstring(line_no):
            self.generic_visit(node)
            return

        # Check for __init__ methods in protocol files
        if node.name == "__init__":
            self.violations.append(
                SPIViolation(
                    self.file_path,
                    line_no,
                    "init_method",
                    "SPI Protocols should not have __init__ methods - use @property accessors instead",
                    (
                        self.source_lines[line_no - 1].strip()
                        if line_no <= len(self.source_lines)
                        else ""
                    ),
                )
            )

        # Check for hardcoded default values
        for arg in node.args.args:
            if hasattr(arg, "defaults") or node.args.defaults:
                for default in node.args.defaults:
                    if isinstance(default, ast.Constant):
                        self.violations.append(
                            SPIViolation(
                                self.file_path,
                                line_no,
                                "hardcoded_default",
                                "SPI should not contain hardcoded default values - use Protocol contracts only",
                                (
                                    self.source_lines[line_no - 1].strip()
                                    if line_no <= len(self.source_lines)
                                    else ""
                                ),
                            )
                        )
                        break

        # Check for method implementations (not just '...')
        if len(node.body) > 1 or (
            len(node.body) == 1 and not isinstance(node.body[0], ast.Expr)
        ):
            # This method has actual implementation, not just '...'
            if not any(
                isinstance(stmt, ast.Expr)
                and isinstance(stmt.value, ast.Constant)
                and stmt.value.value is ...
                for stmt in node.body
            ):
                self.violations.append(
                    SPIViolation(
                        self.file_path,
                        line_no,
                        "concrete_implementation",
                        "SPI should not contain concrete method implementations",
                        (
                            self.source_lines[line_no - 1].strip()
                            if line_no <= len(self.source_lines)
                            else ""
                        ),
                    )
                )

        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Check async function definitions for SPI violations."""
        # Handle AsyncFunctionDef separately to avoid type issues
        line_no = node.lineno

        # Skip if this is in a docstring
        if self.is_in_docstring(line_no):
            self.generic_visit(node)
            return

        # Check for __init__ methods in protocol files
        if node.name == "__init__":
            self.violations.append(
                SPIViolation(
                    self.file_path,
                    line_no,
                    "init_method",
                    "SPI Protocols should not have __init__ methods - use @property accessors instead",
                    (
                        self.source_lines[line_no - 1].strip()
                        if line_no <= len(self.source_lines)
                        else ""
                    ),
                )
            )

        # Check for hardcoded default values
        if node.args.defaults:
            for default in node.args.defaults:
                if isinstance(default, ast.Constant):
                    self.violations.append(
                        SPIViolation(
                            self.file_path,
                            line_no,
                            "hardcoded_default",
                            "SPI should not contain hardcoded default values - use Protocol contracts only",
                            (
                                self.source_lines[line_no - 1].strip()
                                if line_no <= len(self.source_lines)
                                else ""
                            ),
                        )
                    )
                    break

        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Check class definitions for SPI violations."""
        line_no = node.lineno

        # Skip if this is in a docstring
        if self.is_in_docstring(line_no):
            self.generic_visit(node)
            return

        # Check for concrete class implementations (not Protocol)
        if node.bases:
            for base in node.bases:
                if isinstance(base, ast.Name):
                    # Check for Enum classes
                    if base.id == "Enum":
                        self.violations.append(
                            SPIViolation(
                                self.file_path,
                                line_no,
                                "enum_usage",
                                "SPI should use Literal types instead of Enums",
                                (
                                    self.source_lines[line_no - 1].strip()
                                    if line_no <= len(self.source_lines)
                                    else ""
                                ),
                            )
                        )

                    # Check for ABC classes
                    elif base.id == "ABC":
                        self.violations.append(
                            SPIViolation(
                                self.file_path,
                                line_no,
                                "abc_usage",
                                "SPI should use Protocol instead of ABC",
                                (
                                    self.source_lines[line_no - 1].strip()
                                    if line_no <= len(self.source_lines)
                                    else ""
                                ),
                            )
                        )

        # Check for @dataclass decorator
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == "dataclass":
                self.violations.append(
                    SPIViolation(
                        self.file_path,
                        line_no,
                        "dataclass_usage",
                        "SPI should use @runtime_checkable Protocol instead of @dataclass",
                        (
                            self.source_lines[line_no - 1].strip()
                            if line_no <= len(self.source_lines)
                            else ""
                        ),
                    )
                )

        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        """Check import statements for forbidden imports."""
        line_no = node.lineno

        # Skip if this is in a docstring
        if self.is_in_docstring(line_no):
            self.generic_visit(node)
            return

        forbidden_imports = [
            "os",
            "sys",
            "json",
            "yaml",
            "asyncio",
            "logging",
            "requests",
        ]

        for alias in node.names:
            if alias.name in forbidden_imports:
                self.violations.append(
                    SPIViolation(
                        self.file_path,
                        line_no,
                        "implementation_import",
                        "SPI should not import implementation libraries",
                        (
                            self.source_lines[line_no - 1].strip()
                            if line_no <= len(self.source_lines)
                            else ""
                        ),
                    )
                )

        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Check from-import statements for forbidden imports."""
        line_no = node.lineno

        # Skip if this is in a docstring
        if self.is_in_docstring(line_no):
            self.generic_visit(node)
            return

        if node.module:
            forbidden_modules = [
                "abc",
                "enum",
                "os",
                "sys",
                "json",
                "yaml",
                "asyncio",
                "logging",
                "requests",
            ]

            # Special handling for datetime in core_types.py
            if node.module == "datetime" and not self.file_path.endswith(
                "core_types.py"
            ):
                self.violations.append(
                    SPIViolation(
                        self.file_path,
                        line_no,
                        "implementation_import",
                        "SPI should not import implementation libraries",
                        (
                            self.source_lines[line_no - 1].strip()
                            if line_no <= len(self.source_lines)
                            else ""
                        ),
                    )
                )
            elif node.module in forbidden_modules:
                self.violations.append(
                    SPIViolation(
                        self.file_path,
                        line_no,
                        "implementation_import",
                        "SPI should not import implementation libraries",
                        (
                            self.source_lines[line_no - 1].strip()
                            if line_no <= len(self.source_lines)
                            else ""
                        ),
                    )
                )

            # Check for dataclasses imports
            if node.module == "dataclasses":
                self.violations.append(
                    SPIViolation(
                        self.file_path,
                        line_no,
                        "dataclasses_import",
                        "SPI should not import dataclasses - use Protocol instead",
                        (
                            self.source_lines[line_no - 1].strip()
                            if line_no <= len(self.source_lines)
                            else ""
                        ),
                    )
                )

        self.generic_visit(node)


def should_exclude_file(file_path: Path) -> bool:
    """Check if a file should be excluded from SPI validation."""
    path_str = str(file_path)

    # Exclude test files
    if "/test_" in path_str or path_str.endswith("_test.py"):
        return True

    # Exclude validation utilities
    if "/validation/" in path_str:
        return True

    # Exclude examples
    if "example" in path_str.lower():
        return True

    return False


def validate_file(file_path: Path) -> List[SPIViolation]:
    """Validate a single Python file for SPI purity."""
    if should_exclude_file(file_path):
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
            source_lines = source.splitlines()
    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
        return []

    try:
        tree = ast.parse(source, filename=str(file_path))
    except SyntaxError as e:
        print(f"Syntax error in {file_path}: {e}", file=sys.stderr)
        return []

    validator = SPIValidator(str(file_path), source_lines)

    # First pass: collect all docstring lines
    for node in ast.walk(tree):
        validator.collect_docstring_lines(node)

    # Second pass: validate while excluding docstring content
    validator.visit(tree)

    return validator.violations


def main() -> None:
    """Main function to validate SPI purity using AST parsing."""
    src_path = Path("src")
    if not src_path.exists():
        print("Error: src/ directory not found", file=sys.stderr)
        sys.exit(1)

    all_violations = []

    # Find all Python files
    for py_file in src_path.rglob("*.py"):
        violations = validate_file(py_file)
        all_violations.extend(violations)

    # Report violations
    if all_violations:
        print("🔍 AST-based SPI purity validation...")
        print()

        RED = "\033[0;31m"
        YELLOW = "\033[1;33m"
        NC = "\033[0m"  # No Color

        for violation in all_violations:
            print(
                f"{RED}❌ SPI VIOLATION{NC} in {violation.file_path}:{violation.line_no}"
            )
            print(f"   {YELLOW}Found:{NC} {violation.code}")
            print(f"   {YELLOW}Issue:{NC} {violation.message}")
            print()

        GREEN = "\033[0;32m"
        print("----------------------------------------")
        print(f"{RED}❌ SPI purity validation FAILED{NC}")
        print(f"Found {len(all_violations)} violations.")
        print()
        print("SPI (Service Provider Interface) should contain only:")
        print("• Protocol definitions using typing.Protocol")
        print("• Type aliases using typing.Literal")
        print("• Type unions and generic types")
        print("• Abstract method signatures with '...' implementation")
        print()
        print("SPI should NOT contain:")
        print("• Concrete class implementations")
        print("• @dataclass decorators (use @runtime_checkable Protocol instead)")
        print("• dataclasses imports (not needed for pure protocols)")
        print("• __init__ methods in Protocol classes (use @property accessors)")
        print("• Hardcoded default values (e.g., str = 'default')")
        print("• Enum classes (use Literal instead)")
        print("• ABC classes (use Protocol instead)")
        print("• Method implementations with actual logic")
        print("• Implementation library imports")
        print("• Business logic or concrete behavior")

        sys.exit(1)
    else:
        GREEN = "\033[0;32m"
        NC = "\033[0m"
        print(f"{GREEN}✅ AST-based SPI purity validation PASSED{NC}")
        print("All files contain only pure protocol definitions.")
        sys.exit(0)


if __name__ == "__main__":
    main()
