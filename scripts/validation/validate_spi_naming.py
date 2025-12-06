#!/usr/bin/env python3
"""
SPI Naming Convention Validation - Adapted from omnibase_core

This script validates naming conventions specific to omnibase_spi:
1. Protocol classes must start with 'Protocol' prefix
2. Type definitions must follow SPI patterns
3. Module and file naming conventions
4. Consistent protocol naming across domains
5. Forward reference naming patterns

Adapted from omnibase_core naming validation for SPI architectural compliance.
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import timeout_utils
from timeout_utils import timeout_context


@dataclass
class NamingViolation:
    """Represents a naming convention violation."""

    file_path: str
    line_number: int
    class_name: str
    expected_pattern: str
    violation_type: str
    violation_code: str
    message: str
    severity: str = "error"
    suggestion: str = ""
    auto_fixable: bool = False


class SPINamingValidator(ast.NodeVisitor):
    """AST visitor for validating SPI naming conventions."""

    # SPI-specific naming patterns
    SPI_NAMING_PATTERNS = {
        "protocols": {
            "pattern": r"^Protocol[A-Z][A-Za-z0-9]*$",
            "file_prefix": "protocol_",
            "description": "Protocol classes must start with 'Protocol' (e.g., ProtocolEventBus)",
            "required": True,
        },
        "type_aliases": {
            "pattern": r"^[A-Z][A-Za-z0-9]*$",
            "file_prefix": None,
            "description": "Type aliases should use PascalCase (e.g., WorkflowState)",
            "required": False,
        },
        "literal_types": {
            "pattern": r"^[A-Z][A-Za-z0-9]*$",
            "file_prefix": None,
            "description": "Literal types should use PascalCase (e.g., EventType)",
            "required": False,
        },
    }

    # Domain-specific protocol prefixes for better organization
    DOMAIN_PREFIXES = {
        "workflow_orchestration": "WorkflowProtocol",
        "mcp": "MCPProtocol",
        "event_bus": "EventProtocol",
        "container": "ContainerProtocol",
        "core": "CoreProtocol",
    }

    # Exception patterns - names that don't need to follow strict patterns
    EXCEPTION_PATTERNS = [
        r"^_.*",  # Private classes/functions
        r".*Test$",  # Test classes
        r".*TestCase$",  # Test case classes
        r"^Test.*",  # Test classes
        r"^Mock.*",  # Mock classes
        r".*Fixture$",  # Test fixtures
    ]

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.violations: list[NamingViolation] = []
        self.domain = self._determine_domain(file_path)
        self.module_name = self._get_module_name(file_path)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Validate class naming conventions."""
        class_name = node.name

        # Skip exception patterns
        if self._is_exception_pattern(class_name):
            self.generic_visit(node)
            return

        # Check if this is a Protocol class
        if self._is_protocol_class(node):
            self._validate_protocol_naming(node)
        else:
            # Check for non-protocol classes in SPI (should be minimal)
            self._validate_non_protocol_class(node)

        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Validate function naming conventions."""
        # In SPI, we generally shouldn't have many standalone functions
        if not node.name.startswith("_") and node.name not in ["main"]:
            self.violations.append(
                NamingViolation(
                    file_path=self.file_path,
                    line_number=node.lineno,
                    class_name=node.name,
                    expected_pattern="Protocol method",
                    violation_type="standalone_function_in_spi",
                    violation_code="SPI-N001",
                    message=f"SPI should primarily contain Protocol definitions, not standalone function '{node.name}'",
                    severity="warning",
                    suggestion="Consider moving to Protocol method or implementation package",
                )
            )

        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        """Validate type alias and constant naming."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                self._validate_type_alias_naming(target, node)

        self.generic_visit(node)

    def _is_protocol_class(self, node: ast.ClassDef) -> bool:
        """Check if class is a Protocol class."""
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == "Protocol":
                return True
            if isinstance(base, ast.Attribute) and base.attr == "Protocol":
                return True
        return False

    def _validate_protocol_naming(self, node: ast.ClassDef) -> None:
        """Validate protocol class naming conventions."""
        class_name = node.name
        expected_pattern = self.SPI_NAMING_PATTERNS["protocols"]["pattern"]

        # Check basic Protocol prefix
        if not re.match(expected_pattern, class_name):
            self.violations.append(
                NamingViolation(
                    file_path=self.file_path,
                    line_number=node.lineno,
                    class_name=class_name,
                    expected_pattern=expected_pattern,
                    violation_type="protocol_naming_pattern",
                    violation_code="SPI-N002",
                    message=f"Protocol class '{class_name}' must start with 'Protocol' prefix",
                    severity="error",
                    suggestion=f"Rename to 'Protocol{class_name}' or follow domain pattern",
                    auto_fixable=False,
                )
            )

        # Check domain-specific naming recommendation
        if self.domain in self.DOMAIN_PREFIXES:
            suggested_prefix = self.DOMAIN_PREFIXES[self.domain]
            if not class_name.startswith(suggested_prefix) and class_name.startswith(
                "Protocol"
            ):
                self.violations.append(
                    NamingViolation(
                        file_path=self.file_path,
                        line_number=node.lineno,
                        class_name=class_name,
                        expected_pattern=f"{suggested_prefix}*",
                        violation_type="domain_specific_naming",
                        violation_code="SPI-N003",
                        message=f"Consider domain-specific naming: '{suggested_prefix}...' for {self.domain} protocols",
                        severity="info",
                        suggestion=f"For better organization, consider: {suggested_prefix}{class_name[8:]}",
                        auto_fixable=False,
                    )
                )

        # Check for common protocol naming anti-patterns
        self._check_protocol_antipatterns(node)

    def _validate_non_protocol_class(self, node: ast.ClassDef) -> None:
        """Validate non-protocol classes (should be minimal in SPI)."""
        class_name = node.name

        # Check if this might be a type alias class
        if self._is_type_alias_class(node):
            self._validate_type_alias_class(node)
        else:
            # Regular class in SPI is unusual
            self.violations.append(
                NamingViolation(
                    file_path=self.file_path,
                    line_number=node.lineno,
                    class_name=class_name,
                    expected_pattern="Protocol class",
                    violation_type="non_protocol_class_in_spi",
                    violation_code="SPI-N004",
                    message=f"SPI should primarily contain Protocol classes, not regular class '{class_name}'",
                    severity="warning",
                    suggestion="Convert to Protocol or move to implementation package",
                )
            )

    def _validate_type_alias_class(self, node: ast.ClassDef) -> None:
        """Validate type alias class naming."""
        class_name = node.name
        expected_pattern = self.SPI_NAMING_PATTERNS["type_aliases"]["pattern"]

        if not re.match(expected_pattern, class_name):
            self.violations.append(
                NamingViolation(
                    file_path=self.file_path,
                    line_number=node.lineno,
                    class_name=class_name,
                    expected_pattern=expected_pattern,
                    violation_type="type_alias_naming",
                    violation_code="SPI-N005",
                    message=f"Type alias class '{class_name}' should use PascalCase naming",
                    severity="warning",
                    suggestion="Use PascalCase for type alias classes",
                )
            )

    def _validate_type_alias_naming(self, target: ast.Name, node: ast.Assign) -> None:
        """Validate type alias variable naming."""
        name = target.id

        # Skip private variables and common patterns
        if name.startswith("_") or name in ["__all__", "__version__"]:
            return

        # Check if this looks like a type alias
        if isinstance(node.value, ast.Subscript) or self._is_literal_type_assignment(
            node
        ):
            expected_pattern = self.SPI_NAMING_PATTERNS["literal_types"]["pattern"]

            if not re.match(expected_pattern, name):
                self.violations.append(
                    NamingViolation(
                        file_path=self.file_path,
                        line_number=node.lineno,
                        class_name=name,
                        expected_pattern=expected_pattern,
                        violation_type="type_alias_variable_naming",
                        violation_code="SPI-N006",
                        message=f"Type alias '{name}' should use PascalCase naming",
                        severity="info",
                        suggestion="Use PascalCase for type aliases and Literal types",
                    )
                )

    def _check_protocol_antipatterns(self, node: ast.ClassDef) -> None:
        """Check for common protocol naming anti-patterns."""
        class_name = node.name

        # Anti-pattern: redundant naming
        redundant_patterns = [
            ("ProtocolProtocol", "Remove redundant 'Protocol' suffix"),
            (
                "ProtocolInterface",
                "Remove 'Interface' suffix - protocols are interfaces",
            ),
            ("ProtocolContract", "Remove 'Contract' suffix - protocols are contracts"),
            ("ProtocolSpec", "Remove 'Spec' suffix - protocols are specifications"),
        ]

        for pattern, suggestion in redundant_patterns:
            if pattern in class_name:
                self.violations.append(
                    NamingViolation(
                        file_path=self.file_path,
                        line_number=node.lineno,
                        class_name=class_name,
                        expected_pattern="Protocol*",
                        violation_type="redundant_protocol_naming",
                        violation_code="SPI-N007",
                        message=f"Protocol name '{class_name}' contains redundant naming",
                        severity="warning",
                        suggestion=suggestion,
                    )
                )

        # Anti-pattern: vague naming
        vague_names = [
            "ProtocolService",
            "ProtocolManager",
            "ProtocolHandler",
            "ProtocolHelper",
        ]
        if class_name in vague_names:
            self.violations.append(
                NamingViolation(
                    file_path=self.file_path,
                    line_number=node.lineno,
                    class_name=class_name,
                    expected_pattern="Protocol[SpecificPurpose]",
                    violation_type="vague_protocol_naming",
                    violation_code="SPI-N008",
                    message=f"Protocol name '{class_name}' is too vague",
                    severity="info",
                    suggestion="Use more specific naming that describes the protocol's purpose",
                )
            )

    def _is_exception_pattern(self, name: str) -> bool:
        """Check if name matches exception patterns."""
        return any(re.match(pattern, name) for pattern in self.EXCEPTION_PATTERNS)

    def _is_type_alias_class(self, node: ast.ClassDef) -> bool:
        """Check if class is actually a type alias definition."""
        return (
            len(node.bases) == 0
            and len(node.body) == 1
            and isinstance(node.body[0], ast.Assign)
        )

    def _is_literal_type_assignment(self, node: ast.Assign) -> bool:
        """Check if assignment is a Literal type definition."""
        if isinstance(node.value, ast.Call):
            if (
                isinstance(node.value.func, ast.Name)
                and node.value.func.id == "Literal"
            ):
                return True
        return False

    def _determine_domain(self, file_path: str) -> str:
        """Determine the domain from file path."""
        path_parts = Path(file_path).parts

        # Map file paths to domains
        if "workflow_orchestration" in path_parts:
            return "workflow_orchestration"
        elif "mcp" in path_parts:
            return "mcp"
        elif "event_bus" in path_parts:
            return "event_bus"
        elif "container" in path_parts:
            return "container"
        elif "core" in path_parts:
            return "core"
        elif "types" in path_parts:
            return "types"
        else:
            return "unknown"

    def _get_module_name(self, file_path: str) -> str:
        """Get module name from file path."""
        path = Path(file_path)
        return path.stem


def validate_file(file_path: Path) -> list[NamingViolation]:
    """Validate naming conventions in a single Python file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)
        validator = SPINamingValidator(str(file_path))
        validator.visit(tree)

        return validator.violations

    except SyntaxError as e:
        return [
            NamingViolation(
                file_path=str(file_path),
                line_number=e.lineno or 1,
                class_name="<syntax_error>",
                expected_pattern="valid_python",
                violation_type="syntax_error",
                violation_code="SPI-N000",
                message=f"Syntax error: {e.msg}",
                severity="error",
                suggestion="Fix Python syntax errors",
            )
        ]

    except Exception as e:
        return [
            NamingViolation(
                file_path=str(file_path),
                line_number=1,
                class_name="<validation_error>",
                expected_pattern="valid_analysis",
                violation_type="validation_error",
                violation_code="SPI-N000",
                message=f"Validation error: {e}",
                severity="error",
                suggestion="Check file for parsing issues",
            )
        ]


def discover_python_files(base_path: Path) -> list[Path]:
    """Discover Python files for validation."""
    python_files = []

    try:
        for py_file in base_path.rglob("*.py"):
            # Skip test files, __pycache__, and validation scripts
            if (
                py_file.name.startswith("test_")
                or "__pycache__" in str(py_file)
                or py_file.name.startswith("_")
                or "validation" in str(py_file)
            ):
                continue
            python_files.append(py_file)

    except OSError as e:
        print(f"Error discovering Python files: {e}", file=sys.stderr)
        raise

    return python_files


def print_naming_report(violations: list[NamingViolation]) -> None:
    """Print comprehensive naming validation report."""
    print("\n" + "=" * 80)
    print("🏷️  SPI NAMING CONVENTION VALIDATION REPORT")
    print("=" * 80)

    # Summary statistics
    error_count = sum(1 for v in violations if v.severity == "error")
    warning_count = sum(1 for v in violations if v.severity == "warning")
    info_count = sum(1 for v in violations if v.severity == "info")

    print("\n📊 VALIDATION SUMMARY:")
    print(f"   Total violations: {len(violations)}")
    print(f"   Errors: {error_count}")
    print(f"   Warnings: {warning_count}")
    print(f"   Info: {info_count}")

    if violations:
        print("\n🏷️  NAMING VIOLATIONS FOUND:")

        # Group violations by type
        by_type = defaultdict(list)
        for violation in violations:
            by_type[violation.violation_type].append(violation)

        for violation_type, type_violations in by_type.items():
            print(
                f"\n   📋 {violation_type.replace('_', ' ').title()} ({len(type_violations)})"
            )

            for violation in type_violations[:3]:  # Show first 3 of each type
                severity_icon = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}[
                    violation.severity
                ]
                print(
                    f"      {severity_icon} {violation.file_path}:{violation.line_number}"
                )
                print(f"         Class: {violation.class_name}")
                print(f"         {violation.message}")

                if violation.suggestion:
                    print(f"         💡 {violation.suggestion}")

            if len(type_violations) > 3:
                print(f"      ... and {len(type_violations) - 3} more")

    # Domain-specific analysis
    domain_violations = defaultdict(list)
    for violation in violations:
        # Extract domain from file path for analysis
        if "workflow_orchestration" in violation.file_path:
            domain_violations["workflow"].append(violation)
        elif "mcp" in violation.file_path:
            domain_violations["mcp"].append(violation)
        elif "event_bus" in violation.file_path:
            domain_violations["events"].append(violation)
        elif "container" in violation.file_path:
            domain_violations["container"].append(violation)
        elif "core" in violation.file_path:
            domain_violations["core"].append(violation)

    if domain_violations:
        print("\n📁 VIOLATIONS BY DOMAIN:")
        for domain, domain_viols in domain_violations.items():
            print(f"   {domain}: {len(domain_viols)} violations")

    # Best practices recommendations
    print("\n💡 NAMING BEST PRACTICES:")
    print("   📝 Use 'Protocol' prefix for all protocol classes")
    print("   📝 Consider domain-specific prefixes (e.g., WorkflowProtocol...)")
    print("   📝 Use PascalCase for type aliases and Literal types")
    print("   📝 Avoid redundant naming (ProtocolInterface → Protocol)")
    print("   📝 Use specific, descriptive names over vague terms")

    if error_count == 0:
        print("\n✅ NAMING VALIDATION PASSED: No critical errors found")
        if warning_count > 0:
            print(f"   ⚠️  {warning_count} warnings should be addressed for consistency")
    else:
        print(f"\n❌ NAMING VALIDATION FAILED: {error_count} errors must be fixed")


def main():
    """Main validation function."""
    parser = argparse.ArgumentParser(description="Validate SPI naming conventions")
    parser.add_argument("path", nargs="?", default="src/", help="Path to validate")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    try:
        base_path = Path(args.path)

        if not base_path.exists():
            print(f"❌ Path does not exist: {base_path}")
            return 1

        print(f"🏷️  Validating SPI naming conventions in: {base_path}")

        # Discover Python files
        with timeout_context("file_discovery"):
            python_files = discover_python_files(base_path)

        if not python_files:
            print("✅ No Python files to validate")
            return 0

        print(f"📁 Found {len(python_files)} Python files to validate")

        all_violations = []

        # Validate each file
        with timeout_context("validation"):
            for py_file in python_files:
                if args.verbose:
                    print(f"   Validating {py_file}")

                violations = validate_file(py_file)
                all_violations.extend(violations)

        # Print report
        print_naming_report(all_violations)

        # Exit with error code if critical violations found
        error_count = sum(1 for v in all_violations if v.severity == "error")
        return 1 if error_count > 0 else 0

    except timeout_utils.TimeoutError:
        print("❌ Validation timeout")
        return 1
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
