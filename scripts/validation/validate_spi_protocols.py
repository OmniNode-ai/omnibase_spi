#!/usr/bin/env python3
"""
SPI Protocol Validation - omnibase_spi Architecture Compliance

Validates that all protocol definitions follow SPI architectural principles:
1. No __init__ methods in protocol definitions
2. No duplicate protocol definitions
3. All I/O operations must be async
4. Use proper Callable types instead of object
5. Consistent ContextValue usage patterns
6. Runtime checkable protocols
7. Protocol purity (no concrete implementations)

Usage:
    python scripts/validation/validate_spi_protocols.py src/
    python scripts/validation/validate_spi_protocols.py --fix-issues src/
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import timeout_utils
from timeout_utils import timeout_context


@dataclass
class ProtocolViolation:
    """Represents a protocol architecture violation."""

    file_path: str
    line_number: int
    column_offset: int
    violation_type: str
    violation_code: str
    message: str
    severity: str  # 'error', 'warning', 'info'
    suggestion: str = ""
    auto_fixable: bool = False


@dataclass
class ProtocolInfo:
    """Information about a discovered protocol."""

    name: str
    file_path: str
    methods: list[str]
    signature_hash: str
    line_number: int
    has_init: bool = False
    is_runtime_checkable: bool = False
    async_methods: list[str] = None
    sync_io_methods: list[str] = None
    properties: list[str] = None
    base_protocols: list[str] = None
    domain: str = "unknown"
    protocol_type: str = "functional"  # functional, marker, property_only, mixin
    docstring: str = ""

    def __post_init__(self):
        if self.async_methods is None:
            self.async_methods = []
        if self.sync_io_methods is None:
            self.sync_io_methods = []
        if self.properties is None:
            self.properties = []
        if self.base_protocols is None:
            self.base_protocols = []


class SPIProtocolValidator(ast.NodeVisitor):
    """AST visitor for validating SPI protocol compliance."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.violations: list[ProtocolViolation] = []
        self.protocols: list[ProtocolInfo] = []
        self.current_protocol: str = ""
        self.in_protocol_class: bool = False
        self.imports: dict[str, str] = {}
        self.in_type_checking_block: bool = False

    def visit_Import(self, node: ast.Import) -> None:
        """Track imports for validation."""
        for alias in node.names:
            self.imports[alias.asname or alias.name] = alias.name
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Track from imports for validation."""
        if node.module:
            for alias in node.names:
                full_name = f"{node.module}.{alias.name}"
                self.imports[alias.asname or alias.name] = full_name
        self.generic_visit(node)

    def visit_If(self, node: ast.If) -> None:
        """Track TYPE_CHECKING blocks to skip forward references."""
        # Check if this is a TYPE_CHECKING conditional
        is_type_checking = False
        if (
            isinstance(node.test, ast.Name)
            and node.test.id == "TYPE_CHECKING"
            or isinstance(node.test, ast.Attribute)
            and node.test.attr == "TYPE_CHECKING"
        ):
            is_type_checking = True

        if is_type_checking:
            # Mark that we're entering a TYPE_CHECKING block
            was_in_type_checking = self.in_type_checking_block
            self.in_type_checking_block = True

            # Visit children in TYPE_CHECKING context
            self.generic_visit(node)

            # Restore previous state
            self.in_type_checking_block = was_in_type_checking
        else:
            # Regular if block
            self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Validate protocol class definitions."""
        # Check if this is a Protocol class
        is_protocol = self._is_protocol_class(node)

        if is_protocol:
            self.current_protocol = node.name
            self.in_protocol_class = True

            # Skip protocols inside TYPE_CHECKING blocks - they're forward references for type hints only
            if not self.in_type_checking_block:
                # Validate protocol structure
                self._validate_protocol_class(node)

                # Extract protocol information
                protocol_info = self._extract_protocol_info(node)
                self.protocols.append(protocol_info)

            # Visit children
            self.generic_visit(node)

            self.in_protocol_class = False
            self.current_protocol = ""
        else:
            # Non-protocol classes - validate they're not implementations
            self._validate_non_protocol_class(node)
            self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Validate protocol method definitions."""
        if self.in_protocol_class:
            self._validate_protocol_method(node)
        else:
            self._validate_non_protocol_method(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Validate async protocol method definitions."""
        if self.in_protocol_class:
            self._validate_async_protocol_method(node)
        self.generic_visit(node)

    def _is_protocol_class(self, node: ast.ClassDef) -> bool:
        """Check if class is a Protocol class."""
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == "Protocol":
                return True
            if isinstance(base, ast.Attribute) and base.attr == "Protocol":
                return True
        return False

    def _validate_protocol_class(self, node: ast.ClassDef) -> None:
        """Validate protocol class structure and decorators."""
        # Check for @runtime_checkable decorator
        has_runtime_checkable = any(
            (isinstance(d, ast.Name) and d.id == "runtime_checkable")
            or (isinstance(d, ast.Attribute) and d.attr == "runtime_checkable")
            for d in node.decorator_list
        )

        if not has_runtime_checkable:
            self.violations.append(
                ProtocolViolation(
                    file_path=self.file_path,
                    line_number=node.lineno,
                    column_offset=node.col_offset,
                    violation_type="missing_runtime_checkable",
                    violation_code="SPI001",
                    message=f"Protocol '{node.name}' must be @runtime_checkable for isinstance() checks",
                    severity="error",
                    suggestion="Add @runtime_checkable decorator before the class definition",
                    auto_fixable=True,
                )
            )

        # Check protocol naming convention
        if not node.name.startswith("Protocol"):
            self.violations.append(
                ProtocolViolation(
                    file_path=self.file_path,
                    line_number=node.lineno,
                    column_offset=node.col_offset,
                    violation_type="protocol_naming",
                    violation_code="SPI002",
                    message=f"Protocol class '{node.name}' should start with 'Protocol' prefix",
                    severity="warning",
                    suggestion=f"Rename class to 'Protocol{node.name}'",
                    auto_fixable=False,
                )
            )

    def _validate_protocol_method(self, node: ast.FunctionDef) -> None:
        """Validate protocol method definition."""
        method_name = node.name

        # Check for __init__ method (SPI violation)
        if method_name == "__init__":
            self.violations.append(
                ProtocolViolation(
                    file_path=self.file_path,
                    line_number=node.lineno,
                    column_offset=node.col_offset,
                    violation_type="protocol_init_method",
                    violation_code="SPI003",
                    message=f"Protocol '{self.current_protocol}' should not have __init__ method",
                    severity="error",
                    suggestion="Use @property accessors or class attributes instead of __init__",
                    auto_fixable=False,
                )
            )

        # Check for concrete implementation (should have ... body)
        if not self._has_ellipsis_body(node):
            self.violations.append(
                ProtocolViolation(
                    file_path=self.file_path,
                    line_number=node.lineno,
                    column_offset=node.col_offset,
                    violation_type="concrete_implementation",
                    violation_code="SPI004",
                    message=f"Protocol method '{method_name}' should have '...' implementation, not concrete code",
                    severity="error",
                    suggestion="Replace method body with '...' for protocol definition",
                    auto_fixable=True,
                )
            )

        # Check for sync I/O operations
        if self._has_sync_io_operations(node):
            self.violations.append(
                ProtocolViolation(
                    file_path=self.file_path,
                    line_number=node.lineno,
                    column_offset=node.col_offset,
                    violation_type="sync_io_operation",
                    violation_code="SPI005",
                    message=f"Protocol method '{method_name}' contains synchronous I/O operations - use async def instead",
                    severity="error",
                    suggestion="Change to 'async def' for I/O operations",
                    auto_fixable=True,
                )
            )

        # Check for object type usage instead of proper Callable
        if self._uses_object_instead_of_callable(node):
            self.violations.append(
                ProtocolViolation(
                    file_path=self.file_path,
                    line_number=node.lineno,
                    column_offset=node.col_offset,
                    violation_type="object_instead_of_callable",
                    violation_code="SPI006",
                    message=f"Protocol method '{method_name}' uses 'object' type - use 'Callable' instead",
                    severity="error",
                    suggestion="Replace 'object' with appropriate 'Callable[[...], ...]' type",
                    auto_fixable=False,
                )
            )

    def _validate_async_protocol_method(self, node: ast.AsyncFunctionDef) -> None:
        """Validate async protocol method definition."""
        method_name = node.name

        # Check for concrete implementation (should have ... body)
        if not self._has_ellipsis_body(node):
            self.violations.append(
                ProtocolViolation(
                    file_path=self.file_path,
                    line_number=node.lineno,
                    column_offset=node.col_offset,
                    violation_type="concrete_implementation",
                    violation_code="SPI004",
                    message=f"Protocol async method '{method_name}' should have '...' implementation, not concrete code",
                    severity="error",
                    suggestion="Replace method body with '...' for protocol definition",
                    auto_fixable=True,
                )
            )

    def _validate_non_protocol_class(self, node: ast.ClassDef) -> None:
        """Validate that non-protocol classes are not implementations in SPI."""
        # In SPI, we should only have Protocol classes, not concrete implementations
        if not self._is_type_alias_class(node):
            self.violations.append(
                ProtocolViolation(
                    file_path=self.file_path,
                    line_number=node.lineno,
                    column_offset=node.col_offset,
                    violation_type="concrete_class_in_spi",
                    violation_code="SPI007",
                    message=f"SPI should not contain concrete class '{node.name}' - use Protocol instead",
                    severity="error",
                    suggestion="Convert to Protocol or move to implementation package",
                    auto_fixable=False,
                )
            )

    def _validate_non_protocol_method(self, node: ast.FunctionDef) -> None:
        """Validate methods outside of protocol classes."""
        # In SPI, we generally shouldn't have standalone functions
        if not node.name.startswith("_") and node.name not in ["main"]:
            self.violations.append(
                ProtocolViolation(
                    file_path=self.file_path,
                    line_number=node.lineno,
                    column_offset=node.col_offset,
                    violation_type="standalone_function_in_spi",
                    violation_code="SPI008",
                    message=f"SPI should not contain standalone function '{node.name}' - use Protocol methods instead",
                    severity="warning",
                    suggestion="Move function to appropriate Protocol class or implementation package",
                    auto_fixable=False,
                )
            )

    def _extract_protocol_info(self, node: ast.ClassDef) -> ProtocolInfo:
        """Extract protocol information for duplicate analysis."""
        methods = []
        properties = []
        has_init = False
        async_methods = []
        sync_io_methods = []
        base_protocols = []
        docstring = ""

        # Extract docstring
        if (
            node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        ):
            docstring = node.body[0].value.value

        # Extract base protocols
        for base in node.bases:
            if isinstance(base, ast.Name):
                if base.id != "Protocol":
                    base_protocols.append(base.id)
            elif isinstance(base, ast.Attribute):
                if base.attr != "Protocol":
                    base_protocols.append(ast.unparse(base))

        # Extract methods and properties
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_sig = self._get_method_signature(item)
                methods.append(method_sig)
                if item.name == "__init__":
                    has_init = True
                if self._has_sync_io_operations(item):
                    sync_io_methods.append(item.name)
            elif isinstance(item, ast.AsyncFunctionDef):
                method_sig = self._get_async_method_signature(item)
                methods.append(method_sig)
                async_methods.append(item.name)
            elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                # This is a property annotation
                prop_type = ast.unparse(item.annotation) if item.annotation else "Any"
                properties.append(f"{item.target.id}: {prop_type}")

        # Determine protocol type and domain
        protocol_type = self._determine_protocol_type(
            methods, properties, base_protocols, docstring
        )
        domain = self._determine_protocol_domain(self.file_path, node.name, docstring)

        # Create enhanced signature hash that considers more than just methods
        signature_components = []
        signature_components.extend(sorted(methods))
        signature_components.extend(sorted(properties))
        signature_components.extend(sorted(base_protocols))
        signature_components.append(domain)
        signature_components.append(protocol_type)

        signature_str = "|".join(signature_components)
        signature_hash = hashlib.md5(signature_str.encode()).hexdigest()[:12]

        is_runtime_checkable = any(
            (isinstance(d, ast.Name) and d.id == "runtime_checkable")
            or (isinstance(d, ast.Attribute) and d.attr == "runtime_checkable")
            for d in node.decorator_list
        )

        return ProtocolInfo(
            name=node.name,
            file_path=self.file_path,
            methods=methods,
            signature_hash=signature_hash,
            line_number=node.lineno,
            has_init=has_init,
            is_runtime_checkable=is_runtime_checkable,
            async_methods=async_methods,
            sync_io_methods=sync_io_methods,
            properties=properties,
            base_protocols=base_protocols,
            domain=domain,
            protocol_type=protocol_type,
            docstring=docstring,
        )

    def _has_ellipsis_body(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
        """Check if method body contains only ellipsis (...) or docstring + ellipsis."""
        if not node.body:
            return False

        # Check for single ellipsis
        if (
            len(node.body) == 1
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and node.body[0].value.value is ...
        ):
            return True

        # Check for docstring + ellipsis
        if len(node.body) == 2:
            if (
                isinstance(node.body[0], ast.Expr)
                and isinstance(node.body[0].value, ast.Constant)
                and isinstance(node.body[0].value.value, str)
                and isinstance(node.body[1], ast.Expr)
                and isinstance(node.body[1].value, ast.Constant)
                and node.body[1].value.value is ...
            ):
                return True

        return False

    def _has_sync_io_operations(self, node: ast.FunctionDef) -> bool:
        """Check if method contains synchronous I/O operations."""
        # Look for common sync I/O patterns in method signature or annotations
        if node.returns:
            return_type = ast.unparse(node.returns)
            # Check if method should be async based on return type
            if any(
                io_hint in return_type.lower()
                for io_hint in ["file", "open", "read", "write", "connection", "client"]
            ):
                return True

        # Check parameter types for I/O hints
        for arg in node.args.args:
            if arg.annotation:
                arg_type = ast.unparse(arg.annotation)
                if any(
                    io_hint in arg_type.lower()
                    for io_hint in ["file", "connection", "client", "reader", "writer"]
                ):
                    return True

        return False

    def _uses_object_instead_of_callable(self, node: ast.FunctionDef) -> bool:
        """Check if method uses 'object' type where 'Callable' would be more appropriate."""
        if node.returns:
            return_type = ast.unparse(node.returns)
            if "object" in return_type and "callable" in node.name.lower():
                return True

        for arg in node.args.args:
            if arg.annotation:
                arg_type = ast.unparse(arg.annotation)
                if "object" in arg_type and (
                    "callback" in arg.arg or "handler" in arg.arg or "func" in arg.arg
                ):
                    return True

        return False

    def _is_type_alias_class(self, node: ast.ClassDef) -> bool:
        """Check if class is actually a type alias definition."""
        # Type alias classes typically have specific patterns
        return (
            len(node.bases) == 0
            and len(node.body) == 1
            and isinstance(node.body[0], ast.Assign)
        )

    def _get_method_signature(self, node: ast.FunctionDef) -> str:
        """Get method signature string for comparison."""
        args = [arg.arg for arg in node.args.args if arg.arg != "self"]
        returns = ast.unparse(node.returns) if node.returns else "None"
        return f"{node.name}({', '.join(args)}) -> {returns}"

    def _get_async_method_signature(self, node: ast.AsyncFunctionDef) -> str:
        """Get async method signature string for comparison."""
        args = [arg.arg for arg in node.args.args if arg.arg != "self"]
        returns = ast.unparse(node.returns) if node.returns else "None"
        return f"async {node.name}({', '.join(args)}) -> {returns}"

    def _determine_protocol_type(
        self,
        methods: list[str],
        properties: list[str],
        base_protocols: list[str],
        docstring: str,
    ) -> str:
        """Determine the type of protocol based on its contents."""
        if not methods and not properties:
            return "marker"
        elif not methods and properties:
            return "property_only"
        elif methods and not properties and base_protocols:
            return "mixin"
        elif methods:
            return "functional"
        else:
            return "unknown"

    def _determine_protocol_domain(
        self, file_path: str, protocol_name: str, docstring: str
    ) -> str:
        """Determine protocol domain from file path, name, and docstring."""
        from pathlib import Path

        path_parts = Path(file_path).parts

        # Extract domain from file path
        if "workflow_orchestration" in path_parts:
            return "workflow"
        elif "mcp" in path_parts:
            return "mcp"
        elif "event_bus" in path_parts:
            return "events"
        elif "container" in path_parts:
            return "container"
        elif "core" in path_parts:
            return "core"
        elif "types" in path_parts:
            return "types"
        elif "file_handling" in path_parts:
            return "file_handling"

        # Extract domain from protocol name
        protocol_lower = protocol_name.lower()
        if "workflow" in protocol_lower:
            return "workflow"
        elif "mcp" in protocol_lower:
            return "mcp"
        elif "event" in protocol_lower:
            return "events"
        elif "file" in protocol_lower:
            return "file_handling"
        elif "node" in protocol_lower:
            return "core"

        # Extract domain from docstring
        if docstring:
            doc_lower = docstring.lower()
            if "workflow" in doc_lower:
                return "workflow"
            elif "mcp" in doc_lower:
                return "mcp"
            elif "event" in doc_lower:
                return "events"
            elif "file" in doc_lower:
                return "file_handling"

        return "unknown"


class ContextValueValidator:
    """Validates consistent ContextValue usage patterns."""

    def __init__(self):
        self.violations: list[ProtocolViolation] = []
        self.context_value_usage: dict[str, list[str]] = defaultdict(list)

    def validate_file(self, file_path: str) -> list[ProtocolViolation]:
        """Validate ContextValue usage in a file."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)
            self._analyze_context_value_usage(tree, file_path)

        except Exception as e:
            self.violations.append(
                ProtocolViolation(
                    file_path=file_path,
                    line_number=1,
                    column_offset=0,
                    violation_type="context_value_analysis_error",
                    violation_code="SPI009",
                    message=f"Error analyzing ContextValue usage: {e}",
                    severity="warning",
                    suggestion="Check file syntax and ContextValue imports",
                )
            )

        return self.violations

    def _analyze_context_value_usage(self, tree: ast.AST, file_path: str) -> None:
        """Analyze ContextValue usage patterns in AST."""

        class ContextValueVisitor(ast.NodeVisitor):
            def __init__(self, validator, file_path):
                self.validator = validator
                self.file_path = file_path

            def visit_Subscript(self, node):
                # Look for ContextValue[...] usage
                if isinstance(node.value, ast.Name) and node.value.id == "ContextValue":
                    if isinstance(node.slice, ast.Name):
                        type_arg = node.slice.id
                        self.validator.context_value_usage[type_arg].append(
                            self.file_path
                        )
                self.generic_visit(node)

        visitor = ContextValueVisitor(self, file_path)
        visitor.visit(tree)


def discover_python_files(base_path: Path) -> list[Path]:
    """Discover Python files in the protocols directory."""
    python_files = []

    try:
        for py_file in base_path.rglob("*.py"):
            # Skip test files and __pycache__
            if (
                py_file.name.startswith("test_")
                or "__pycache__" in str(py_file)
                or py_file.name.startswith("_")
            ):
                continue
            python_files.append(py_file)

    except OSError as e:
        print(f"Error discovering Python files: {e}", file=sys.stderr)
        raise

    return python_files


def validate_protocol_duplicates(
    protocols: list[ProtocolInfo], strict_mode: bool = False
) -> list[ProtocolViolation]:
    """Check for duplicate protocol definitions with smart duplicate detection."""
    violations = []

    # Group by signature hash for exact duplicates
    by_signature = defaultdict(list)
    for protocol in protocols:
        by_signature[protocol.signature_hash].append(protocol)

    # Group by name for name conflicts
    by_name = defaultdict(list)
    for protocol in protocols:
        by_name[protocol.name].append(protocol)

    # Check exact duplicates - but be smarter about what constitutes a duplicate
    for signature_hash, duplicate_protocols in by_signature.items():
        if len(duplicate_protocols) > 1:
            # Check if these are truly problematic duplicates
            real_duplicates = _filter_real_duplicates(duplicate_protocols, strict_mode)

            # Only report if there are actually multiple duplicates after filtering
            if len(real_duplicates) > 1:
                for protocol in real_duplicates[1:]:  # Skip first as reference
                    violations.append(
                        ProtocolViolation(
                            file_path=protocol.file_path,
                            line_number=protocol.line_number,
                            column_offset=0,
                            violation_type="duplicate_protocol",
                            violation_code="SPI010",
                            message=f"Protocol '{protocol.name}' appears to be a true duplicate (domain: {protocol.domain}, type: {protocol.protocol_type})",
                            severity="error",
                            suggestion=f"Remove duplicate protocol or merge with {real_duplicates[0].file_path}",
                            auto_fixable=False,
                        )
                    )

    # Check name conflicts (different signatures, same name) - also with smarter detection
    for name, conflicting_protocols in by_name.items():
        if len(conflicting_protocols) > 1:
            unique_signatures = set(p.signature_hash for p in conflicting_protocols)
            if len(unique_signatures) > 1:  # Different signatures
                # Check if these are legitimate variations or real conflicts
                real_conflicts = _filter_real_conflicts(
                    conflicting_protocols, strict_mode
                )

                if len(real_conflicts) > 1:
                    for protocol in real_conflicts[1:]:  # Skip first as reference
                        violations.append(
                            ProtocolViolation(
                                file_path=protocol.file_path,
                                line_number=protocol.line_number,
                                column_offset=0,
                                violation_type="protocol_name_conflict",
                                violation_code="SPI011",
                                message=f"Protocol '{protocol.name}' has naming conflict with different signature (domains: {[p.domain for p in real_conflicts]})",
                                severity="error",
                                suggestion="Rename protocol to be more domain-specific or merge interfaces",
                                auto_fixable=False,
                            )
                        )

    return violations


def _filter_real_duplicates(
    protocols: list[ProtocolInfo], strict_mode: bool
) -> list[ProtocolInfo]:
    """Filter out false positive duplicates based on protocol analysis."""
    if not protocols or len(protocols) < 2:
        return protocols

    # Group by domain and type
    by_domain_type = defaultdict(list)
    for protocol in protocols:
        key = (protocol.domain, protocol.protocol_type)
        by_domain_type[key].append(protocol)

    real_duplicates = []

    for (domain, protocol_type), domain_protocols in by_domain_type.items():
        if len(domain_protocols) > 1:
            # These are protocols in the same domain with the same type and signature
            # This is likely a real duplicate

            # Additional checks for property-only protocols
            if protocol_type == "property_only":
                # Check if they have identical properties
                property_groups = defaultdict(list)
                for protocol in domain_protocols:
                    prop_key = "|".join(sorted(protocol.properties))
                    property_groups[prop_key].append(protocol)

                for prop_protocols in property_groups.values():
                    if len(prop_protocols) > 1:
                        real_duplicates.extend(prop_protocols)
            else:
                # For other types, same domain + type + signature = duplicate
                real_duplicates.extend(domain_protocols)

    # In strict mode, any signature match is a duplicate
    if strict_mode and not real_duplicates:
        real_duplicates = protocols

    return real_duplicates


def _filter_real_conflicts(
    protocols: list[ProtocolInfo], strict_mode: bool
) -> list[ProtocolInfo]:
    """Filter out legitimate protocol variations from real naming conflicts."""
    if not protocols or len(protocols) < 2:
        return protocols

    # If protocols are in different domains, they might be legitimate variations
    domains = set(p.domain for p in protocols)
    protocol_types = set(p.protocol_type for p in protocols)

    # If all protocols are in different domains, this might be acceptable
    if len(domains) == len(protocols) and not strict_mode:
        return []  # No conflicts - they're domain-specific variations

    # If protocols have different purposes (types), might be acceptable
    if len(protocol_types) > 1 and not strict_mode:
        # Check if they're related (e.g., base protocol and specific implementations)
        base_protocols_overlap = False
        for p1 in protocols:
            for p2 in protocols:
                if p1 != p2 and (
                    p1.name in p2.base_protocols
                    or p2.name in p1.base_protocols
                    or any(base in p2.base_protocols for base in p1.base_protocols)
                ):
                    base_protocols_overlap = True
                    break
            if base_protocols_overlap:
                break

        if base_protocols_overlap:
            return []  # No conflicts - they're related protocols

    # In strict mode or when protocols are too similar, report as conflicts
    return protocols


def validate_file(
    file_path: Path,
) -> tuple[list[ProtocolViolation], list[ProtocolInfo]]:
    """Validate a single Python file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)
        validator = SPIProtocolValidator(str(file_path))
        validator.visit(tree)

        # Also validate ContextValue usage
        context_validator = ContextValueValidator()
        context_violations = context_validator.validate_file(str(file_path))

        all_violations = validator.violations + context_violations
        return all_violations, validator.protocols

    except SyntaxError as e:
        return [
            ProtocolViolation(
                file_path=str(file_path),
                line_number=e.lineno or 1,
                column_offset=e.offset or 0,
                violation_type="syntax_error",
                violation_code="SPI000",
                message=f"Syntax error: {e.msg}",
                severity="error",
                suggestion="Fix Python syntax errors",
                auto_fixable=False,
            )
        ], []

    except Exception as e:
        return [
            ProtocolViolation(
                file_path=str(file_path),
                line_number=1,
                column_offset=0,
                violation_type="validation_error",
                violation_code="SPI000",
                message=f"Validation error: {e}",
                severity="error",
                suggestion="Check file for parsing issues",
                auto_fixable=False,
            )
        ], []


def print_validation_report(
    violations: list[ProtocolViolation],
    protocols: list[ProtocolInfo],
    show_protocol_info: bool = False,
) -> None:
    """Print comprehensive validation report."""
    print("\n" + "=" * 80)
    print("🔍 SPI PROTOCOL VALIDATION REPORT")
    print("=" * 80)

    # Summary statistics
    error_count = sum(1 for v in violations if v.severity == "error")
    warning_count = sum(1 for v in violations if v.severity == "warning")
    total_protocols = len(protocols)

    print("\n📊 VALIDATION SUMMARY:")
    print(f"   Total protocols found: {total_protocols}")
    print(f"   Total violations: {len(violations)}")
    print(f"   Errors: {error_count}")
    print(f"   Warnings: {warning_count}")

    if violations:
        print("\n🚨 VIOLATIONS FOUND:")

        # Group violations by type
        by_type = defaultdict(list)
        for violation in violations:
            by_type[violation.violation_type].append(violation)

        for violation_type, type_violations in by_type.items():
            print(
                f"\n   📋 {violation_type.replace('_', ' ').title()} ({len(type_violations)})"
            )

            for violation in type_violations[:3]:  # Show first 3 of each type
                severity_icon = "❌" if violation.severity == "error" else "⚠️"
                print(
                    f"      {severity_icon} {violation.file_path}:{violation.line_number}"
                )
                print(f"         {violation.message}")
                if violation.suggestion:
                    print(f"         💡 {violation.suggestion}")

            if len(type_violations) > 3:
                print(f"      ... and {len(type_violations) - 3} more")

    # Protocol statistics
    if protocols:
        print("\n📈 PROTOCOL STATISTICS:")
        runtime_checkable = sum(1 for p in protocols if p.is_runtime_checkable)
        with_init = sum(1 for p in protocols if p.has_init)
        with_async = sum(1 for p in protocols if p.async_methods)

        print(f"   @runtime_checkable: {runtime_checkable}/{total_protocols}")
        print(f"   With __init__ methods: {with_init}")
        print(f"   With async methods: {with_async}")

        # Enhanced statistics
        by_domain = defaultdict(int)
        by_type = defaultdict(int)
        for protocol in protocols:
            by_domain[protocol.domain] += 1
            by_type[protocol.protocol_type] += 1

        print("\n📊 PROTOCOL DISTRIBUTION:")
        print("   By Domain:")
        for domain, count in sorted(
            by_domain.items(), key=lambda x: x[1], reverse=True
        ):
            print(f"      {domain}: {count}")

        print("   By Type:")
        for ptype, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
            print(f"      {ptype}: {count}")

        if show_protocol_info:
            print("\n📋 DETAILED PROTOCOL INFORMATION:")
            for protocol in protocols[:10]:  # Show first 10 for brevity
                print(f"   • {protocol.name}")
                print(f"     Domain: {protocol.domain}, Type: {protocol.protocol_type}")
                print(
                    f"     Methods: {len(protocol.methods)}, Properties: {len(protocol.properties)}"
                )
                print(f"     Base protocols: {protocol.base_protocols}")
                if protocol.docstring:
                    print(f"     Description: {protocol.docstring[:100]}...")
            if len(protocols) > 10:
                print(f"   ... and {len(protocols) - 10} more protocols")

        if with_init > 0:
            print("   🚨 Protocols with __init__ should be refactored!")

    if error_count == 0:
        print("\n✅ VALIDATION PASSED: No critical errors found")
        if warning_count > 0:
            print(f"   ⚠️  {warning_count} warnings should be addressed")
    else:
        print(f"\n❌ VALIDATION FAILED: {error_count} errors must be fixed")


def main():
    """Main validation function."""
    parser = argparse.ArgumentParser(description="Validate SPI protocol compliance")
    parser.add_argument("path", nargs="?", default="src/", help="Path to validate")
    parser.add_argument(
        "--fix-issues", action="store_true", help="Attempt to auto-fix violations"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Strict mode - report all potential duplicates and conflicts",
    )
    parser.add_argument(
        "--sensitivity",
        choices=["low", "medium", "high"],
        default="medium",
        help="Validation sensitivity level (default: medium)",
    )
    parser.add_argument(
        "--show-protocol-info",
        action="store_true",
        help="Show detailed protocol information in output",
    )

    args = parser.parse_args()

    try:
        base_path = Path(args.path)

        if not base_path.exists():
            print(f"❌ Path does not exist: {base_path}")
            return 1

        print(f"🔍 Validating SPI protocols in: {base_path}")

        # Discover Python files
        with timeout_context("file_discovery"):
            python_files = discover_python_files(base_path)

        if not python_files:
            print("✅ No Python files to validate")
            return 0

        print(f"📁 Found {len(python_files)} Python files to validate")

        all_violations = []
        all_protocols = []

        # Validate each file
        with timeout_context("validation"):
            for py_file in python_files:
                if args.verbose:
                    print(f"   Validating {py_file}")

                violations, protocols = validate_file(py_file)
                all_violations.extend(violations)
                all_protocols.extend(protocols)

        # Determine strict mode based on arguments
        strict_mode = args.strict or args.sensitivity == "high"

        # Check for protocol duplicates with improved logic
        duplicate_violations = validate_protocol_duplicates(all_protocols, strict_mode)
        all_violations.extend(duplicate_violations)

        # Print report
        print_validation_report(all_violations, all_protocols, args.show_protocol_info)

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
