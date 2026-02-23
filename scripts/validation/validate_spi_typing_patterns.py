#!/usr/bin/env python3
"""
SPI Typing Pattern Validation - Adapted from omnibase_core

This script validates typing patterns specific to omnibase_spi protocols:
1. Modern typing syntax enforcement (Type | None vs Optional[Type])
2. SPI-specific type patterns validation
3. Protocol type annotation consistency
4. Forward reference validation in SPI context
5. Callable vs object type validation
6. Async-by-default typing validation

Adapted from omnibase_core validation patterns for SPI architectural compliance.
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
class TypingViolation:
    """Represents a typing pattern violation."""

    file_path: str
    line_number: int
    column_offset: int
    violation_type: str
    violation_code: str
    message: str
    severity: str  # 'error', 'warning', 'info'
    suggestion: str = ""
    old_pattern: str = ""
    new_pattern: str = ""
    auto_fixable: bool = False


class SPITypingValidator(ast.NodeVisitor):
    """AST visitor for validating SPI-specific typing patterns."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.violations: list[TypingViolation] = []
        self.typing_imports: set[str] = set()
        self.protocol_imports: set[str] = set()
        self.in_protocol_class: bool = False
        self.current_protocol: str = ""
        self.protocol_classes_in_file: set[str] = set()  # Track protocols in this file
        self.has_type_checking_import: bool = (
            False  # Track TYPE_CHECKING import at module level
        )
        # Set to True when visiting a class that declares synchronous_execution.
        # Exempts all methods in that class from the async-by-default check (SPI-T003).
        self.current_class_synchronous: bool = False

    def visit_Import(self, node: ast.Import) -> None:
        """Track imports for validation context."""
        for alias in node.names:
            if alias.name == "typing":
                self.typing_imports.add(alias.asname or alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Track from imports for validation context."""
        if node.module == "typing":
            for alias in node.names:
                if alias.name == "TYPE_CHECKING":
                    self.has_type_checking_import = True
                if alias.name in ("Optional", "Union", "Callable", "Any", "Protocol"):
                    self.typing_imports.add(alias.asname or alias.name)
        elif node.module and "protocol" in node.module.lower():
            for alias in node.names:
                self.protocol_imports.add(alias.asname or alias.name)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Validate protocol class typing patterns."""
        is_protocol = self._is_protocol_class(node)

        if is_protocol:
            self.protocol_classes_in_file.add(node.name)  # Track protocol in this file
            self.current_protocol = node.name
            self.in_protocol_class = True
            self.current_class_synchronous = self._class_declares_synchronous_execution(
                node
            )
            self._validate_protocol_class_typing(node)

        self.generic_visit(node)

        if is_protocol:
            self.in_protocol_class = False
            self.current_protocol = ""
            self.current_class_synchronous = False

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Validate function typing patterns."""
        if self.in_protocol_class:
            self._validate_protocol_method_typing(node)
        else:
            self._validate_function_typing(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Validate async function typing patterns."""
        if self.in_protocol_class:
            self._validate_async_protocol_method_typing(node)
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        """Check for typing pattern violations."""
        if isinstance(node.value, ast.Name):
            # Check for old-style Optional usage
            if node.value.id == "Optional":
                self.violations.append(
                    TypingViolation(
                        file_path=self.file_path,
                        line_number=node.lineno,
                        column_offset=node.col_offset,
                        violation_type="old_optional_syntax",
                        violation_code="SPI-T001",
                        message="Use modern union syntax 'Type | None' instead of 'Optional[Type]'",
                        severity="warning",
                        old_pattern=ast.unparse(node),
                        new_pattern=f"{ast.unparse(node.slice)} | None",
                        suggestion="Replace Optional[T] with T | None for Python 3.10+ compatibility",
                        auto_fixable=True,
                    )
                )

            # Check for old-style Union usage
            elif node.value.id == "Union":
                self._validate_union_usage(node)

            # Check for inappropriate Any usage in SPI
            elif node.value.id == "Any":
                self._validate_any_usage(node)

            # Check for object type where Callable should be used
            elif node.value.id == "object" and self.in_protocol_class:
                self._validate_object_vs_callable(node)

        self.generic_visit(node)

    def _is_protocol_class(self, node: ast.ClassDef) -> bool:
        """Check if class is a Protocol class."""
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == "Protocol":
                return True
            if isinstance(base, ast.Attribute) and base.attr == "Protocol":
                return True
        return False

    def _validate_protocol_class_typing(self, node: ast.ClassDef) -> None:
        """Validate typing patterns in protocol class definition."""
        # Check if forward references are used without TYPE_CHECKING import at module level
        if not self.has_type_checking_import:
            # Check if forward references are used without TYPE_CHECKING
            for item in node.body:
                if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                    if self._has_string_annotations(item):
                        self.violations.append(
                            TypingViolation(
                                file_path=self.file_path,
                                line_number=item.lineno,
                                column_offset=item.col_offset,
                                violation_type="missing_type_checking_import",
                                violation_code="SPI-T002",
                                message="Forward references should use TYPE_CHECKING imports",
                                severity="warning",
                                suggestion="Import forward reference types under 'if TYPE_CHECKING:' block",
                                auto_fixable=False,
                            )
                        )

    def _validate_protocol_method_typing(self, node: ast.FunctionDef) -> None:
        """Validate typing patterns in protocol method."""
        # Check return type annotation
        if node.returns:
            return_type = ast.unparse(node.returns)

            # Check for sync methods that should be async (I/O operations)
            if self._should_be_async_method(node, return_type):
                self.violations.append(
                    TypingViolation(
                        file_path=self.file_path,
                        line_number=node.lineno,
                        column_offset=node.col_offset,
                        violation_type="sync_io_method",
                        violation_code="SPI-T003",
                        message=f"Method '{node.name}' appears to perform I/O but is not async",
                        severity="error",
                        suggestion="Change to 'async def' for I/O operations",
                        auto_fixable=True,
                    )
                )

        # Check parameter annotations
        for arg in node.args.args:
            if arg.annotation:
                self._validate_parameter_annotation(arg, node.name)

    def _validate_async_protocol_method_typing(
        self, node: ast.AsyncFunctionDef
    ) -> None:
        """Validate typing patterns in async protocol method."""
        if node.returns:
            return_type = ast.unparse(node.returns)

            # Async methods should typically not return plain values without awaitable
            if not self._is_awaitable_return_type(return_type):
                self.violations.append(
                    TypingViolation(
                        file_path=self.file_path,
                        line_number=node.lineno,
                        column_offset=node.col_offset,
                        violation_type="non_awaitable_async_return",
                        violation_code="SPI-T004",
                        message=f"Async method '{node.name}' should return awaitable type",
                        severity="warning",
                        suggestion="Consider if this method really needs to be async",
                        auto_fixable=False,
                    )
                )

    def _validate_function_typing(self, node: ast.FunctionDef) -> None:
        """Validate typing patterns in non-protocol functions."""
        # In SPI, we generally shouldn't have many standalone functions
        if not node.name.startswith("_") and node.name not in ["main"]:
            self.violations.append(
                TypingViolation(
                    file_path=self.file_path,
                    line_number=node.lineno,
                    column_offset=node.col_offset,
                    violation_type="standalone_function_in_spi",
                    violation_code="SPI-T005",
                    message=f"SPI should primarily contain Protocol definitions, not standalone function '{node.name}'",
                    severity="info",
                    suggestion="Consider moving to Protocol method or implementation package",
                    auto_fixable=False,
                )
            )

    def _validate_union_usage(self, node: ast.Subscript) -> None:
        """Validate Union type usage patterns."""
        union_types = []

        if isinstance(node.slice, ast.Tuple):
            union_types = [ast.unparse(elt) for elt in node.slice.elts]
        else:
            union_types = [ast.unparse(node.slice)]

        # Check for Union that could be simplified to modern syntax
        if len(union_types) >= 2:
            new_pattern = " | ".join(union_types)
            self.violations.append(
                TypingViolation(
                    file_path=self.file_path,
                    line_number=node.lineno,
                    column_offset=node.col_offset,
                    violation_type="old_union_syntax",
                    violation_code="SPI-T006",
                    message="Use modern union syntax 'Type1 | Type2' instead of 'Union[Type1, Type2]'",
                    severity="warning",
                    old_pattern=ast.unparse(node),
                    new_pattern=new_pattern,
                    suggestion="Replace Union[...] with modern | syntax for Python 3.10+ compatibility",
                    auto_fixable=True,
                )
            )

    def _validate_any_usage(self, node: ast.Subscript) -> None:
        """Validate Any type usage (should be minimal in SPI)."""
        self.violations.append(
            TypingViolation(
                file_path=self.file_path,
                line_number=node.lineno,
                column_offset=node.col_offset,
                violation_type="any_type_usage",
                violation_code="SPI-T007",
                message="Avoid 'Any' type in SPI - use specific types for strong typing",
                severity="warning",
                suggestion="Replace Any with specific type annotation",
                auto_fixable=False,
            )
        )

    def _validate_object_vs_callable(self, node: ast.Subscript) -> None:
        """Validate object type usage where Callable might be more appropriate."""
        # This is already handled in the main SPI validator, but we can enhance it
        pass

    def _validate_parameter_annotation(self, arg: ast.arg, method_name: str) -> None:
        """Validate parameter type annotations."""
        if arg.annotation:
            annotation = ast.unparse(arg.annotation)

            # Check for object type in callback parameters
            if "object" in annotation and any(
                callback_hint in arg.arg
                for callback_hint in ["callback", "handler", "func", "callable"]
            ):
                self.violations.append(
                    TypingViolation(
                        file_path=self.file_path,
                        line_number=arg.lineno if hasattr(arg, "lineno") else 0,
                        column_offset=(
                            arg.col_offset if hasattr(arg, "col_offset") else 0
                        ),
                        violation_type="object_instead_of_callable",
                        violation_code="SPI-T008",
                        message=f"Parameter '{arg.arg}' in method '{method_name}' uses 'object' type - use 'Callable' instead",
                        severity="error",
                        suggestion="Replace 'object' with appropriate 'Callable[[...], ...]' type",
                        auto_fixable=False,
                    )
                )

    def _class_declares_synchronous_execution(self, node: ast.ClassDef) -> bool:
        """Return True if the class body declares ``synchronous_execution``.

        Matches both annotation-only declarations (``synchronous_execution:
        ClassVar[bool]``) and annotated assignments.  The presence of the name
        is sufficient — the validator does not evaluate the value.
        """
        for item in node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                if item.target.id == "synchronous_execution":
                    return True
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if (
                        isinstance(target, ast.Name)
                        and target.id == "synchronous_execution"
                    ):
                        return True
        return False

    def _should_be_async_method(self, node: ast.FunctionDef, return_type: str) -> bool:
        """Check if method should be async based on patterns."""
        # Skip @property methods - they should never be async
        if self._has_property_decorator(node):
            return False

        # If the enclosing class declares synchronous_execution, all its methods
        # are intentionally synchronous — skip the async-by-default check.
        if self.current_class_synchronous:
            return False

        # Synchronous method exceptions - these are sync by design in protocol definitions
        # Note: Many registry methods (list_keys, is_registered, register) are async in
        # protocol_versioned_registry.py and protocol_service_discovery.py, so NOT listed here.
        # Only methods that are truly sync in all protocol definitions belong in this list.
        sync_exceptions = [
            "get_handler_descriptor",  # Sync in ProtocolHandlerSource (protocol_handler_source.py)
            "list_handler_descriptors",  # Sync in ProtocolHandlerSource (protocol_handler_source.py)
            "get_available_capability_ids",  # Sync in ProtocolProviderRegistry (protocol_provider_registry.py)
            "get_supported_effects",  # Sync in ProtocolPrimitiveEffectExecutor (protocol_primitive_effect_executor.py)
            "execute",  # Sync in ProtocolEffect / ProtocolNodeProjectionEffect (OMN-2508) — synchronous ordering guarantee
        ]

        if node.name in sync_exceptions:
            return False

        # Check method name patterns
        async_patterns = [
            "connect",
            "disconnect",
            "send",
            "receive",
            "read",
            "write",
            "fetch",
            "load",
            "save",
            "execute",
            "process",
            "handle",
        ]

        if any(pattern in node.name.lower() for pattern in async_patterns):
            return True

        # Check return type patterns
        io_return_types = ["connection", "client", "response", "result", "stream"]

        return bool(any(io_type in return_type.lower() for io_type in io_return_types))

    def _has_property_decorator(self, node: ast.FunctionDef) -> bool:
        """Check if function has @property decorator."""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == "property":
                return True
            if isinstance(decorator, ast.Attribute) and decorator.attr == "property":
                return True
        return False

    def _is_awaitable_return_type(self, return_type: str) -> bool:
        """Check if return type is awaitable."""
        awaitable_patterns = [
            "Awaitable",
            "Coroutine",
            "Future",
            "Task",
            "AsyncGenerator",
            "AsyncIterator",
        ]
        return any(pattern in return_type for pattern in awaitable_patterns)

    def _is_cross_file_reference(self, type_str: str) -> bool:
        """Check if a forward reference type is from a different file.

        Args:
            type_str: Forward reference string like "ProtocolFoo" or "ProtocolFoo | None"

        Returns:
            True if this is a cross-file reference, False if same-file reference
        """
        # Extract all Protocol class names from the forward reference string
        # Handle cases like: "ProtocolFoo", "ProtocolFoo | None", "list[ProtocolFoo]"
        protocol_names = re.findall(r"Protocol\w+", type_str)

        if not protocol_names:
            # No protocol references found, consider it cross-file to be safe
            return True

        # Check if any of the referenced protocols are defined in the current file
        for proto_name in protocol_names:
            if proto_name in self.protocol_classes_in_file:
                # At least one protocol is in the same file
                # If ALL protocols are in the same file, it's not cross-file
                pass
            else:
                # Found a protocol not in this file
                return True

        # All referenced protocols are in this file
        return False

    def _has_string_annotations(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> bool:
        """Check if function has string annotations (forward references) that are cross-file.

        Only returns True for forward references that point to types in other files,
        not for same-file forward references which are acceptable.
        """
        # Check return annotation
        if (
            node.returns
            and isinstance(node.returns, ast.Constant)
            and isinstance(node.returns.value, str)
        ):
            # Check if this is a cross-file reference
            if self._is_cross_file_reference(node.returns.value):
                return True

        # Check parameter annotations
        for arg in node.args.args:
            if (
                arg.annotation
                and isinstance(arg.annotation, ast.Constant)
                and isinstance(arg.annotation.value, str)
            ):
                # Check if this is a cross-file reference
                if self._is_cross_file_reference(arg.annotation.value):
                    return True

        return False


def validate_file(file_path: Path) -> list[TypingViolation]:
    """Validate typing patterns in a single Python file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)
        validator = SPITypingValidator(str(file_path))
        validator.visit(tree)

        return validator.violations

    except SyntaxError as e:
        return [
            TypingViolation(
                file_path=str(file_path),
                line_number=e.lineno or 1,
                column_offset=e.offset or 0,
                violation_type="syntax_error",
                violation_code="SPI-T000",
                message=f"Syntax error: {e.msg}",
                severity="error",
                suggestion="Fix Python syntax errors",
            )
        ]

    except Exception as e:
        return [
            TypingViolation(
                file_path=str(file_path),
                line_number=1,
                column_offset=0,
                violation_type="validation_error",
                violation_code="SPI-T000",
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


def print_typing_report(violations: list[TypingViolation]) -> None:
    """Print comprehensive typing validation report."""
    print("\n" + "=" * 80)
    print("📝 SPI TYPING PATTERN VALIDATION REPORT")
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
        print("\n🔍 TYPING VIOLATIONS FOUND:")

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
                print(f"         {violation.message}")

                if violation.old_pattern and violation.new_pattern:
                    print(f"         📝 Replace: {violation.old_pattern}")
                    print(f"         📝 With: {violation.new_pattern}")

                if violation.suggestion:
                    print(f"         💡 {violation.suggestion}")

            if len(type_violations) > 3:
                print(f"      ... and {len(type_violations) - 3} more")

    # Auto-fixable suggestions
    auto_fixable = [v for v in violations if v.auto_fixable]
    if auto_fixable:
        print(f"\n🔧 AUTO-FIXABLE ISSUES: {len(auto_fixable)}")
        print("   Consider implementing auto-fix functionality for these violations")

    if error_count == 0:
        print("\n✅ TYPING VALIDATION PASSED: No critical errors found")
        if warning_count > 0:
            print(
                f"   ⚠️  {warning_count} warnings should be addressed for better typing"
            )
    else:
        print(f"\n❌ TYPING VALIDATION FAILED: {error_count} errors must be fixed")


def main():
    """Main validation function."""
    parser = argparse.ArgumentParser(description="Validate SPI typing patterns")
    parser.add_argument("path", nargs="?", default="src/", help="Path to validate")
    parser.add_argument(
        "--auto-fix",
        action="store_true",
        help="Attempt to auto-fix violations (future feature)",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    try:
        base_path = Path(args.path)

        if not base_path.exists():
            print(f"❌ Path does not exist: {base_path}")
            return 1

        print(f"📝 Validating SPI typing patterns in: {base_path}")

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
        print_typing_report(all_violations)

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
