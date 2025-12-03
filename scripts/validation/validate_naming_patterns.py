#!/usr/bin/env python3
"""
Standalone Naming Convention and Pattern Validator for omnibase_spi.

This is a TEMPORARY standalone copy of validation logic until Core removes
its SPI dependency. Uses only Python stdlib (no omnibase_core imports).

Validates:
1. Protocol classes must start with "Protocol" prefix
2. Exception classes must end with "Error" suffix
3. All protocols must have @runtime_checkable decorator
4. Protocol methods must have ... (ellipsis) bodies, not implementations

Naming Rules Enforced:
- Node protocols: Protocol{Type}Node (e.g., ProtocolComputeNode)
- Compiler protocols: Protocol{Type}ContractCompiler
- Handler protocols: Protocol{Type} or Protocol{Type}Handler
- Exceptions: {Type}Error (e.g., SPIError, RegistryError)

Usage:
    python scripts/validation/validate_naming_patterns.py [path]
    python scripts/validation/validate_naming_patterns.py src/
    python scripts/validation/validate_naming_patterns.py --verbose src/

Exit codes:
    0 - Success (no violations)
    1 - Failure (violations found)
"""
from __future__ import annotations

import argparse
import ast
import sys
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Violation:
    """Represents a naming or pattern violation."""

    file_path: str
    line_number: int
    name: str
    violation_type: str
    violation_code: str
    message: str
    severity: str = "error"  # error, warning, info
    suggestion: str = ""

    def __str__(self) -> str:
        """Format violation for display."""
        return f"{self.file_path}:{self.line_number}: [{self.violation_code}] {self.message}"


@dataclass
class ValidationResult:
    """Aggregated validation result."""

    violations: list[Violation] = field(default_factory=list)
    protocols_found: int = 0
    exceptions_found: int = 0
    files_scanned: int = 0

    @property
    def error_count(self) -> int:
        """Count of error-level violations."""
        return sum(1 for v in self.violations if v.severity == "error")

    @property
    def warning_count(self) -> int:
        """Count of warning-level violations."""
        return sum(1 for v in self.violations if v.severity == "warning")

    @property
    def passed(self) -> bool:
        """Returns True if no error-level violations."""
        return self.error_count == 0


class NamingPatternValidator(ast.NodeVisitor):
    """AST visitor for validating SPI naming conventions and patterns."""

    # Naming pattern rules
    PROTOCOL_PREFIX = "Protocol"
    ERROR_SUFFIX = "Error"

    # Valid exception base classes
    EXCEPTION_BASES = {"Exception", "BaseException", "SPIError"}

    # Skip patterns for testing/private
    SKIP_PATTERNS = {"_", "Test", "Mock", "Fixture"}

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.violations: list[Violation] = []
        self.protocols_found = 0
        self.exceptions_found = 0
        self.in_protocol_class = False
        self.current_class_name = ""
        self.in_type_checking_block = False

    def visit_If(self, node: ast.If) -> None:
        """Track TYPE_CHECKING blocks to skip forward references."""
        is_type_checking = False
        if isinstance(node.test, ast.Name) and node.test.id == "TYPE_CHECKING":
            is_type_checking = True
        elif isinstance(node.test, ast.Attribute) and node.test.attr == "TYPE_CHECKING":
            is_type_checking = True

        if is_type_checking:
            was_in_type_checking = self.in_type_checking_block
            self.in_type_checking_block = True
            self.generic_visit(node)
            self.in_type_checking_block = was_in_type_checking
        else:
            self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Validate class definitions."""
        class_name = node.name

        # Skip private/test patterns
        if self._should_skip(class_name):
            self.generic_visit(node)
            return

        # Skip classes in TYPE_CHECKING blocks (forward references)
        if self.in_type_checking_block:
            self.generic_visit(node)
            return

        # Check if Protocol class
        if self._is_protocol_class(node):
            self.protocols_found += 1
            self._validate_protocol_class(node)

            # Set context and visit children for method validation
            self.in_protocol_class = True
            self.current_class_name = class_name
            self.generic_visit(node)
            self.in_protocol_class = False
            self.current_class_name = ""
        # Check if Exception class
        elif self._is_exception_class(node):
            self.exceptions_found += 1
            self._validate_exception_class(node)
            self.generic_visit(node)
        else:
            self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Validate function definitions within protocols."""
        if self.in_protocol_class:
            self._validate_protocol_method(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Validate async function definitions within protocols."""
        if self.in_protocol_class:
            self._validate_protocol_method(node)
        self.generic_visit(node)

    def _should_skip(self, name: str) -> bool:
        """Check if name should be skipped."""
        return any(name.startswith(p) or name.endswith(p) for p in self.SKIP_PATTERNS)

    def _is_protocol_class(self, node: ast.ClassDef) -> bool:
        """Check if class inherits from Protocol."""
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == "Protocol":
                return True
            if isinstance(base, ast.Attribute) and base.attr == "Protocol":
                return True
            # Also check for classes that extend other protocols
            if isinstance(base, ast.Name) and base.id.startswith("Protocol"):
                # Check if it also has Protocol in bases (mixed inheritance)
                for other_base in node.bases:
                    if isinstance(other_base, ast.Name) and other_base.id == "Protocol":
                        return True
                    if (
                        isinstance(other_base, ast.Attribute)
                        and other_base.attr == "Protocol"
                    ):
                        return True
        return False

    def _is_exception_class(self, node: ast.ClassDef) -> bool:
        """Check if class inherits from Exception or known error base."""
        for base in node.bases:
            if isinstance(base, ast.Name):
                if base.id in self.EXCEPTION_BASES:
                    return True
                # Check if inheriting from another Error class
                if base.id.endswith(self.ERROR_SUFFIX):
                    return True
            if isinstance(base, ast.Attribute):
                if base.attr in self.EXCEPTION_BASES:
                    return True
                if base.attr.endswith(self.ERROR_SUFFIX):
                    return True
        return False

    def _validate_protocol_class(self, node: ast.ClassDef) -> None:
        """Validate protocol class naming and decorators."""
        class_name = node.name

        # Rule 1: Protocol prefix
        if not class_name.startswith(self.PROTOCOL_PREFIX):
            self.violations.append(
                Violation(
                    file_path=self.file_path,
                    line_number=node.lineno,
                    name=class_name,
                    violation_type="protocol_naming",
                    violation_code="SPI-NP001",
                    message=f"Protocol class '{class_name}' must start with 'Protocol' prefix",
                    severity="error",
                    suggestion=f"Rename to 'Protocol{class_name}'",
                )
            )

        # Rule 2: @runtime_checkable decorator
        has_runtime_checkable = self._has_runtime_checkable_decorator(node)
        if not has_runtime_checkable:
            self.violations.append(
                Violation(
                    file_path=self.file_path,
                    line_number=node.lineno,
                    name=class_name,
                    violation_type="missing_runtime_checkable",
                    violation_code="SPI-NP002",
                    message=f"Protocol '{class_name}' must have @runtime_checkable decorator",
                    severity="error",
                    suggestion="Add '@runtime_checkable' decorator before class definition",
                )
            )

        # Validate specific naming patterns
        self._validate_protocol_specific_naming(node)

    def _validate_protocol_specific_naming(self, node: ast.ClassDef) -> None:
        """Validate domain-specific protocol naming patterns."""
        class_name = node.name

        # Node protocols: Protocol{Type}Node
        if "Node" in class_name and class_name.startswith("Protocol"):
            # Valid patterns: ProtocolNode, ProtocolComputeNode, ProtocolEffectNode, etc.
            if not class_name.endswith("Node"):
                self.violations.append(
                    Violation(
                        file_path=self.file_path,
                        line_number=node.lineno,
                        name=class_name,
                        violation_type="node_naming",
                        violation_code="SPI-NP003",
                        message=f"Node protocol '{class_name}' should end with 'Node'",
                        severity="warning",
                        suggestion="Node protocols follow pattern: Protocol{Type}Node",
                    )
                )

        # Compiler protocols: Protocol{Type}ContractCompiler
        if "Compiler" in class_name and class_name.startswith("Protocol"):
            if not class_name.endswith("ContractCompiler") and not class_name.endswith(
                "Compiler"
            ):
                self.violations.append(
                    Violation(
                        file_path=self.file_path,
                        line_number=node.lineno,
                        name=class_name,
                        violation_type="compiler_naming",
                        violation_code="SPI-NP004",
                        message=f"Compiler protocol '{class_name}' should end with 'ContractCompiler' or 'Compiler'",
                        severity="warning",
                        suggestion="Compiler protocols follow pattern: Protocol{Type}ContractCompiler",
                    )
                )

    def _validate_exception_class(self, node: ast.ClassDef) -> None:
        """Validate exception class naming."""
        class_name = node.name

        # Rule: Exception classes must end with "Error"
        if not class_name.endswith(self.ERROR_SUFFIX):
            self.violations.append(
                Violation(
                    file_path=self.file_path,
                    line_number=node.lineno,
                    name=class_name,
                    violation_type="exception_naming",
                    violation_code="SPI-NP005",
                    message=f"Exception class '{class_name}' must end with 'Error' suffix",
                    severity="error",
                    suggestion=f"Rename to '{class_name}Error'",
                )
            )

    def _validate_protocol_method(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> None:
        """Validate protocol method has ellipsis body."""
        method_name = node.name

        # Skip dunder methods except for explicit protocol methods
        if method_name.startswith("__") and method_name.endswith("__"):
            # __init__ in protocols is a violation
            if method_name == "__init__":
                self.violations.append(
                    Violation(
                        file_path=self.file_path,
                        line_number=node.lineno,
                        name=f"{self.current_class_name}.{method_name}",
                        violation_type="protocol_init",
                        violation_code="SPI-NP006",
                        message=f"Protocol '{self.current_class_name}' should not have __init__ method",
                        severity="warning",
                        suggestion="Use @property accessors instead of __init__",
                    )
                )
            return

        # Check for ellipsis body
        if not self._has_ellipsis_body(node):
            self.violations.append(
                Violation(
                    file_path=self.file_path,
                    line_number=node.lineno,
                    name=f"{self.current_class_name}.{method_name}",
                    violation_type="non_ellipsis_body",
                    violation_code="SPI-NP007",
                    message=f"Protocol method '{method_name}' must have '...' (ellipsis) body, not implementation",
                    severity="error",
                    suggestion="Replace method body with '...' for protocol definition",
                )
            )

    def _has_runtime_checkable_decorator(self, node: ast.ClassDef) -> bool:
        """Check if class has @runtime_checkable decorator."""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == "runtime_checkable":
                return True
            if (
                isinstance(decorator, ast.Attribute)
                and decorator.attr == "runtime_checkable"
            ):
                return True
        return False

    def _has_ellipsis_body(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
        """Check if method body contains only ellipsis (with optional docstring)."""
        if not node.body:
            return False

        body = node.body

        # Single ellipsis
        if len(body) == 1:
            item = body[0]
            if isinstance(item, ast.Expr) and isinstance(item.value, ast.Constant):
                return item.value.value is ...
            # Also accept ast.Ellipsis for older Python versions
            if isinstance(item, ast.Expr) and isinstance(item.value, ast.Ellipsis):
                return True

        # Docstring + ellipsis
        if len(body) == 2:
            first, second = body[0], body[1]
            # First should be docstring
            is_docstring = (
                isinstance(first, ast.Expr)
                and isinstance(first.value, ast.Constant)
                and isinstance(first.value.value, str)
            )
            # Second should be ellipsis
            is_ellipsis = (
                isinstance(second, ast.Expr)
                and isinstance(second.value, ast.Constant)
                and second.value.value is ...
            )
            if is_docstring and is_ellipsis:
                return True

        # Check for 'pass' statement which is also acceptable
        if len(body) == 1 and isinstance(body[0], ast.Pass):
            return True

        # Docstring + pass
        if len(body) == 2:
            first, second = body[0], body[1]
            is_docstring = (
                isinstance(first, ast.Expr)
                and isinstance(first.value, ast.Constant)
                and isinstance(first.value.value, str)
            )
            if is_docstring and isinstance(second, ast.Pass):
                return True

        return False


def validate_file(file_path: Path) -> tuple[list[Violation], int, int]:
    """
    Validate a single Python file.

    Returns:
        Tuple of (violations, protocols_found, exceptions_found)
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)
        validator = NamingPatternValidator(str(file_path))
        validator.visit(tree)

        return validator.violations, validator.protocols_found, validator.exceptions_found

    except SyntaxError as e:
        violation = Violation(
            file_path=str(file_path),
            line_number=e.lineno or 1,
            name="<syntax_error>",
            violation_type="syntax_error",
            violation_code="SPI-NP000",
            message=f"Syntax error: {e.msg}",
            severity="error",
        )
        return [violation], 0, 0

    except Exception as e:
        violation = Violation(
            file_path=str(file_path),
            line_number=1,
            name="<validation_error>",
            violation_type="validation_error",
            violation_code="SPI-NP000",
            message=f"Validation error: {e}",
            severity="error",
        )
        return [violation], 0, 0


def discover_python_files(base_path: Path) -> list[Path]:
    """
    Discover Python files for validation.

    Skips:
    - Files starting with underscore (except __init__.py)
    - Files in __pycache__ directories
    - Test files (test_*.py)
    - Validation scripts
    """
    python_files = []

    # Handle single file
    if base_path.is_file():
        if base_path.suffix == ".py":
            return [base_path]
        return []

    for py_file in base_path.rglob("*.py"):
        # Skip __pycache__
        if "__pycache__" in str(py_file):
            continue
        # Skip test files
        if py_file.name.startswith("test_"):
            continue
        # Skip validation scripts (to avoid self-validation issues)
        if "validation" in str(py_file.parent) and py_file.name.startswith("validate"):
            continue
        # Skip private files (except __init__.py)
        if py_file.name.startswith("_") and py_file.name != "__init__.py":
            continue

        python_files.append(py_file)

    return sorted(python_files)


def print_report(result: ValidationResult, verbose: bool = False) -> None:
    """Print validation report."""
    print()
    print("=" * 80)
    print("SPI NAMING PATTERN VALIDATION REPORT")
    print("=" * 80)

    # Summary
    print()
    print("SUMMARY:")
    print(f"  Files scanned:      {result.files_scanned}")
    print(f"  Protocols found:    {result.protocols_found}")
    print(f"  Exceptions found:   {result.exceptions_found}")
    print(f"  Total violations:   {len(result.violations)}")
    print(f"  Errors:             {result.error_count}")
    print(f"  Warnings:           {result.warning_count}")

    if result.violations:
        print()
        print("VIOLATIONS:")
        print("-" * 80)

        # Group by violation type
        by_type: dict[str, list[Violation]] = {}
        for v in result.violations:
            by_type.setdefault(v.violation_type, []).append(v)

        for vtype, violations in sorted(by_type.items()):
            print(f"\n  {vtype.replace('_', ' ').upper()} ({len(violations)}):")

            display_violations = violations if verbose else violations[:5]
            for v in display_violations:
                severity_marker = "[ERROR]" if v.severity == "error" else "[WARN]"
                print(f"    {severity_marker} {v.file_path}:{v.line_number}")
                print(f"           {v.message}")
                if v.suggestion:
                    print(f"           -> {v.suggestion}")

            if not verbose and len(violations) > 5:
                print(f"    ... and {len(violations) - 5} more")

    print()
    print("-" * 80)
    if result.passed:
        print("RESULT: PASSED - No error-level violations found")
        if result.warning_count > 0:
            print(f"        ({result.warning_count} warnings should be addressed)")
    else:
        print(f"RESULT: FAILED - {result.error_count} error(s) must be fixed")
    print("=" * 80)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate SPI naming conventions and patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python validate_naming_patterns.py src/
    python validate_naming_patterns.py --verbose src/omnibase_spi/protocols/

Naming Rules:
    - Protocol classes: Must start with "Protocol" prefix
    - Exception classes: Must end with "Error" suffix
    - Node protocols: Protocol{Type}Node (e.g., ProtocolComputeNode)
    - Compiler protocols: Protocol{Type}ContractCompiler
    - Handler protocols: Protocol{Type} or Protocol{Type}Handler

Pattern Rules:
    - All protocols must have @runtime_checkable decorator
    - Protocol methods must have ... (ellipsis) body, not implementations
        """,
    )
    parser.add_argument(
        "path",
        nargs="?",
        default="src/",
        help="Path to validate (default: src/)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show all violations (not just first 5 per type)",
    )

    args = parser.parse_args()

    base_path = Path(args.path)

    if not base_path.exists():
        print(f"Error: Path does not exist: {base_path}")
        return 1

    print(f"Validating SPI naming patterns in: {base_path}")

    # Discover files
    python_files = discover_python_files(base_path)

    if not python_files:
        print("No Python files found to validate")
        return 0

    print(f"Found {len(python_files)} Python files to validate")

    # Validate
    result = ValidationResult()
    result.files_scanned = len(python_files)

    for py_file in python_files:
        violations, protocols, exceptions = validate_file(py_file)
        result.violations.extend(violations)
        result.protocols_found += protocols
        result.exceptions_found += exceptions

    # Report
    print_report(result, verbose=args.verbose)

    return 0 if result.passed else 1


if __name__ == "__main__":
    sys.exit(main())
