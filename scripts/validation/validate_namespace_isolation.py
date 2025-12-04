#!/usr/bin/env python3
"""
Standalone Namespace Isolation Validator for omnibase_spi.

This is a STANDALONE validator using only Python stdlib (ast, pathlib, sys, argparse).
It does NOT import from omnibase_core to avoid circular dependency issues.

Purpose:
    Enforces strict namespace isolation rules for the SPI package to ensure
    architectural purity and prevent circular dependencies.

Rules Enforced:
    1. NO imports from omnibase_infra (anywhere, even TYPE_CHECKING)
    2. NO Pydantic BaseModel/BaseSettings subclass definitions
    3. Protocol files should only contain Protocol definitions (protocol purity)

Usage:
    python scripts/validation/validate_namespace_isolation.py
    python scripts/validation/validate_namespace_isolation.py --path src/omnibase_spi
    python scripts/validation/validate_namespace_isolation.py --verbose

Exit Codes:
    0: Success - no violations found
    1: Failure - violations found or error occurred

Author: ONEX Framework
Version: 1.0.0 (Temporary - until Core removes SPI dependency)
"""
from __future__ import annotations

import argparse
import ast
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar, List, Optional, Set, Tuple

# ============================================================================
# Data Structures
# ============================================================================


@dataclass
class NamespaceViolation:
    """Represents a namespace isolation violation."""

    file_path: str
    line_number: int
    column_offset: int
    rule_id: str
    violation_type: str
    message: str
    severity: str  # 'error', 'warning', 'info'
    suggestion: str = ""

    def format_message(self) -> str:
        """Format violation for display."""
        return (
            f"  [{self.rule_id}] {self.severity.upper()}: {self.file_path}:{self.line_number}:{self.column_offset}\n"
            f"    {self.message}\n"
            f"    Suggestion: {self.suggestion}"
        )


@dataclass
class ValidationReport:
    """Validation results report."""

    violations: List[NamespaceViolation] = field(default_factory=list)
    files_scanned: int = 0
    errors: List[str] = field(default_factory=list)

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
        """Check if validation passed (no errors)."""
        return self.error_count == 0 and len(self.errors) == 0


# ============================================================================
# AST Visitor for Namespace Isolation Validation
# ============================================================================


class NamespaceIsolationValidator(ast.NodeVisitor):
    """
    AST-based validator for namespace isolation rules.

    Uses only Python stdlib - no external dependencies.
    """

    # Forbidden import prefixes
    FORBIDDEN_IMPORTS: ClassVar[Set[str]] = {
        "omnibase_infra",
    }

    # Forbidden base classes (Pydantic models)
    FORBIDDEN_BASE_CLASSES: ClassVar[Set[str]] = {
        "BaseModel",
        "BaseSettings",
        "GenericModel",
    }

    # Direct I/O operations that should not be in protocol files
    FORBIDDEN_IO_CALLS: ClassVar[Set[str]] = {
        "open",
        "read",
        "write",
        "mkdir",
        "makedirs",
        "remove",
        "rmdir",
        "unlink",
        "rename",
        "socket",
        "connect",
        "urlopen",
        "request",
    }

    def __init__(self, file_path: str, is_protocol_file: bool = False):
        self.file_path = file_path
        self.is_protocol_file = is_protocol_file
        self.violations: List[NamespaceViolation] = []
        self.in_type_checking_block = False
        self.in_class_definition = False
        self.current_class_name: Optional[str] = None
        self.current_class_bases: List[str] = []

    def visit_If(self, node: ast.If) -> None:
        """Track TYPE_CHECKING blocks."""
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

    def visit_Import(self, node: ast.Import) -> None:
        """Check import statements for forbidden imports."""
        for alias in node.names:
            import_name = alias.name
            self._check_forbidden_import(node, import_name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Check from imports for forbidden imports."""
        if node.module:
            self._check_forbidden_import(node, node.module)
        self.generic_visit(node)

    def _check_forbidden_import(self, node: ast.AST, import_name: str) -> None:
        """Check if an import is forbidden."""
        for forbidden in self.FORBIDDEN_IMPORTS:
            if import_name.startswith(forbidden) or import_name == forbidden:
                context = (
                    " (inside TYPE_CHECKING)" if self.in_type_checking_block else ""
                )
                self.violations.append(
                    NamespaceViolation(
                        file_path=self.file_path,
                        line_number=getattr(node, "lineno", 1),
                        column_offset=getattr(node, "col_offset", 0),
                        rule_id="NSI001",
                        violation_type="forbidden_import",
                        message=f"Forbidden import from '{import_name}'{context}",
                        severity="error",
                        suggestion=f"Remove import from '{forbidden}' - SPI must not depend on infrastructure layer",
                    )
                )

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Check class definitions for Pydantic models and other violations."""
        self.current_class_name = node.name
        self.in_class_definition = True
        self.current_class_bases = []

        # Collect base class names
        for base in node.bases:
            base_name = self._get_base_class_name(base)
            if base_name:
                self.current_class_bases.append(base_name)

        # Check for Pydantic model inheritance
        self._check_pydantic_inheritance(node)

        # Visit children
        self.generic_visit(node)

        # Reset state
        self.in_class_definition = False
        self.current_class_name = None
        self.current_class_bases = []

    def _get_base_class_name(self, base: ast.AST) -> Optional[str]:
        """Extract base class name from AST node."""
        if isinstance(base, ast.Name):
            return base.id
        elif isinstance(base, ast.Attribute):
            return base.attr
        elif isinstance(base, ast.Subscript):
            # Handle Generic[T] style bases
            if isinstance(base.value, ast.Name):
                return base.value.id
            elif isinstance(base.value, ast.Attribute):
                return base.value.attr
        return None

    def _check_pydantic_inheritance(self, node: ast.ClassDef) -> None:
        """Check if class inherits from Pydantic BaseModel or BaseSettings."""
        for base in node.bases:
            base_name = self._get_base_class_name(base)
            if base_name in self.FORBIDDEN_BASE_CLASSES:
                self.violations.append(
                    NamespaceViolation(
                        file_path=self.file_path,
                        line_number=node.lineno,
                        column_offset=node.col_offset,
                        rule_id="NSI002",
                        violation_type="pydantic_model",
                        message=f"Class '{node.name}' inherits from Pydantic '{base_name}'",
                        severity="error",
                        suggestion="SPI must contain only Protocol definitions, not Pydantic models. "
                        "Move to omnibase_core.models or define as Protocol interface.",
                    )
                )

    def visit_Call(self, node: ast.Call) -> None:
        """Check for direct I/O operations in protocol files."""
        if self.is_protocol_file and not self.in_class_definition:
            call_name = self._get_call_name(node)
            if call_name in self.FORBIDDEN_IO_CALLS:
                self.violations.append(
                    NamespaceViolation(
                        file_path=self.file_path,
                        line_number=node.lineno,
                        column_offset=node.col_offset,
                        rule_id="NSI003",
                        violation_type="direct_io",
                        message=f"Direct I/O operation '{call_name}()' in protocol file",
                        severity="warning",
                        suggestion="Protocol files should not contain direct I/O operations. "
                        "Move to implementation or use abstract protocol methods.",
                    )
                )
        self.generic_visit(node)

    def _get_call_name(self, node: ast.Call) -> str:
        """Extract function name from Call node."""
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            return node.func.attr
        return ""


# ============================================================================
# File Discovery and Validation
# ============================================================================


def discover_python_files(base_path: Path) -> List[Path]:
    """Discover Python files in the given path."""
    python_files = []

    if base_path.is_file():
        if base_path.suffix == ".py":
            return [base_path]
        return []

    for py_file in base_path.rglob("*.py"):
        # Skip test files, __pycache__, and hidden directories
        path_str = str(py_file)
        if any(
            skip in path_str
            for skip in ["__pycache__", ".git", ".venv", "venv", "node_modules"]
        ):
            continue
        python_files.append(py_file)

    return sorted(python_files)


def is_protocol_file(file_path: Path) -> bool:
    """Check if file is a protocol definition file."""
    path_str = str(file_path)
    return "protocols" in path_str and file_path.name.startswith("protocol_")


def validate_file(file_path: Path) -> Tuple[List[NamespaceViolation], Optional[str]]:
    """
    Validate a single Python file for namespace isolation.

    Returns:
        Tuple of (violations list, error message or None)
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)
        validator = NamespaceIsolationValidator(
            str(file_path),
            is_protocol_file=is_protocol_file(file_path),
        )
        validator.visit(tree)

        return validator.violations, None

    except SyntaxError as e:
        return [], f"Syntax error in {file_path}: {e}"
    except (OSError, IOError) as e:
        return [], f"Failed to read {file_path}: {e}"
    except Exception as e:
        return [], f"Unexpected error validating {file_path}: {e}"


def validate_directory(
    base_path: Path,
    verbose: bool = False,
) -> ValidationReport:
    """Validate all Python files in directory for namespace isolation."""
    report = ValidationReport()

    # Discover files
    python_files = discover_python_files(base_path)

    if not python_files:
        if verbose:
            print(f"No Python files found in {base_path}")
        return report

    if verbose:
        print(f"Found {len(python_files)} Python files to validate")

    # Validate each file
    for py_file in python_files:
        report.files_scanned += 1

        if verbose:
            print(f"  Validating: {py_file}")

        violations, error = validate_file(py_file)

        if error:
            report.errors.append(error)
        else:
            report.violations.extend(violations)

    return report


# ============================================================================
# Report Generation
# ============================================================================


def print_report(report: ValidationReport, verbose: bool = False) -> None:
    """Print validation report.

    Args:
        report: The validation report to print.
        verbose: If True, show all violations. If False, limit to first 5 per rule.
    """
    print("\n" + "=" * 80)
    print("NAMESPACE ISOLATION VALIDATION REPORT")
    print("=" * 80)

    print(f"\nFiles scanned: {report.files_scanned}")
    print(f"Total violations: {len(report.violations)}")
    print(f"  Errors: {report.error_count}")
    print(f"  Warnings: {report.warning_count}")

    if report.errors:
        print(f"\nParse errors: {len(report.errors)}")
        for error in report.errors:
            print(f"  - {error}")

    if report.violations:
        print("\n" + "-" * 80)
        print("VIOLATIONS:")
        print("-" * 80)

        # Group by rule
        by_rule: dict = {}
        for v in report.violations:
            if v.rule_id not in by_rule:
                by_rule[v.rule_id] = []
            by_rule[v.rule_id].append(v)

        for rule_id in sorted(by_rule.keys()):
            violations = by_rule[rule_id]
            print(
                f"\n{rule_id}: {violations[0].violation_type} ({len(violations)} occurrences)"
            )
            # Limit output unless verbose mode
            display_violations = violations if verbose else violations[:5]
            for v in display_violations:
                print(v.format_message())
            if not verbose and len(violations) > 5:
                print(f"    ... and {len(violations) - 5} more violations")

    print("\n" + "=" * 80)
    if report.passed:
        print("VALIDATION PASSED")
    else:
        print("VALIDATION FAILED")
    print("=" * 80)


# ============================================================================
# CLI Entry Point
# ============================================================================


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate namespace isolation for omnibase_spi",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Rules Enforced:
  NSI001  No imports from omnibase_infra (including TYPE_CHECKING blocks)
  NSI002  No Pydantic BaseModel/BaseSettings class definitions
  NSI003  No direct I/O operations in protocol files

Examples:
  %(prog)s
  %(prog)s --path src/omnibase_spi
  %(prog)s --verbose
""",
    )

    parser.add_argument(
        "--path",
        "-p",
        type=Path,
        default=Path("src/omnibase_spi"),
        help="Path to validate (default: src/omnibase_spi)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output",
    )

    args = parser.parse_args()

    # Validate path exists
    if not args.path.exists():
        print(f"ERROR: Path does not exist: {args.path}")
        return 1

    print(f"Validating namespace isolation in: {args.path}")

    # Run validation
    report = validate_directory(args.path, verbose=args.verbose)

    # Print report
    print_report(report, verbose=args.verbose)

    # Return exit code
    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main())
