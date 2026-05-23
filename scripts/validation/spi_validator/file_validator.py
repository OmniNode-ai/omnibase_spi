# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""AST visitor that validates a single SPI protocol file."""

from __future__ import annotations

import ast
import time
from typing import Any

from .ast_checks import (
    class_declares_synchronous_execution,
    count_generic_complexity,
    determine_domain,
    generate_signature_hash,
    get_async_method_signature,
    get_call_name,
    get_method_signature,
    get_module_path,
    has_complete_type_annotations,
    has_ellipsis_body,
    is_allowed_import,
    is_implementation_function_call,
    is_literal_class,
    is_protocol_class,
    is_spi_implementation_violation,
    is_type_alias_class,
    is_utility_function,
    should_be_async_method,
    uses_object_instead_of_callable,
)
from .config import ValidationConfig
from .models import ProtocolInfo, ProtocolViolation


class ComprehensiveSPIValidator(ast.NodeVisitor):
    def __init__(self, file_path: str, config: ValidationConfig):
        self.file_path = file_path
        self.config = config
        self.violations: list[ProtocolViolation] = []
        self.protocols: list[ProtocolInfo] = []

        self.current_protocol: ProtocolInfo | None = None
        self.in_protocol_class: bool = False
        # True when the current class declares synchronous_execution = True,
        # exempting all its methods from the async-by-default rule (SPI005).
        self.current_class_synchronous: bool = False
        self.imports: dict[str, str] = {}
        self.type_checking_imports: set[str] = set()
        self.forward_references: set[str] = set()

        self.analysis_start_time = time.time()
        self.node_count = 0
        self.source_lines: list[str] = []
        self._load_source_lines()

    def _load_source_lines(self) -> None:
        try:
            with open(self.file_path, encoding="utf-8") as f:
                self.source_lines = f.readlines()
        except Exception:
            self.source_lines = []

    def _get_context_lines(self, line_number: int, context_size: int = 2) -> list[str]:
        start = max(0, line_number - context_size - 1)
        end = min(len(self.source_lines), line_number + context_size)
        return [line.rstrip() for line in self.source_lines[start:end]]

    def _add_violation(
        self,
        node: ast.AST,
        rule_id: str,
        message: str,
        suggestion: str = "",
        tags: list[str] | None = None,
        performance_impact: str = "none",
    ) -> None:
        rule = self.config.get_rule(rule_id)
        if not rule or not rule.enabled:
            return
        violation = ProtocolViolation(
            file_path=self.file_path,
            line_number=getattr(node, "lineno", 1),
            column_offset=getattr(node, "col_offset", 0),
            rule_id=rule_id,
            violation_type=rule.name,
            message=message,
            severity=rule.severity,
            suggestion=suggestion or rule.description,
            auto_fix_available=rule.auto_fixable,
            context_lines=self._get_context_lines(getattr(node, "lineno", 1)),
            tags=tags or [],
            performance_impact=performance_impact,
        )
        self.violations.append(violation)

    def visit(self, node: ast.AST) -> None:
        self.node_count += 1
        super().visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            import_name = alias.name
            as_name = alias.asname or alias.name
            self.imports[as_name] = import_name
            if not is_allowed_import(import_name):
                self._add_violation(
                    node,
                    "SPI012",
                    f"Import '{import_name}' violates namespace isolation - use omnibase_spi.protocols.* only",
                    "Replace with appropriate omnibase_spi.protocols import",
                    tags=["namespace", "isolation"],
                )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            if node.module == "typing" and any(
                alias.name == "TYPE_CHECKING" for alias in node.names
            ):
                self.type_checking_imports.add("TYPE_CHECKING")
            for alias in node.names:
                full_name = f"{node.module}.{alias.name}"
                as_name = alias.asname or alias.name
                self.imports[as_name] = full_name
                if not is_allowed_import(node.module):
                    self._add_violation(
                        node,
                        "SPI012",
                        f"Import from '{node.module}' violates namespace isolation",
                        "Use omnibase_spi.protocols imports or typing imports only",
                        tags=["namespace", "isolation"],
                    )
        self.generic_visit(node)

    def visit_If(self, node: ast.If) -> None:
        if (
            isinstance(node.test, ast.Name)
            and node.test.id == "TYPE_CHECKING"
            and "TYPE_CHECKING" in self.type_checking_imports
        ):
            for child in ast.walk(node):
                if isinstance(child, ast.ImportFrom) and child.module:
                    for alias in child.names:
                        self.forward_references.add(alias.asname or alias.name)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        if is_protocol_class(node):
            self._validate_protocol_class(node)
        else:
            self._validate_non_protocol_class(node)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if self.in_protocol_class:
            self._validate_protocol_method(node)
        else:
            self._validate_standalone_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        if self.in_protocol_class:
            self._validate_async_protocol_method(node)
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        if is_spi_implementation_violation(node, self.in_protocol_class):
            self._add_violation(
                node,
                "SPI016",
                "SPI files must not contain assignment logic - use type annotations only",
                "Remove assignment logic or move to implementation package",
                tags=["spi", "purity", "assignment"],
            )
        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        self._add_violation(
            node,
            "SPI016",
            "SPI files must not contain augmented assignment logic",
            "Remove assignment logic or move to implementation package",
            tags=["spi", "purity", "assignment"],
        )
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        self._add_violation(
            node,
            "SPI016",
            "SPI files must not contain for loops - protocols define contracts only",
            "Remove loop logic or move to implementation package",
            tags=["spi", "purity", "control_flow"],
        )
        self.generic_visit(node)

    def visit_While(self, node: ast.While) -> None:
        self._add_violation(
            node,
            "SPI016",
            "SPI files must not contain while loops - protocols define contracts only",
            "Remove loop logic or move to implementation package",
            tags=["spi", "purity", "control_flow"],
        )
        self.generic_visit(node)

    def visit_Try(self, node: ast.Try) -> None:
        self._add_violation(
            node,
            "SPI016",
            "SPI files must not contain try/except blocks - protocols define contracts only",
            "Remove exception handling or move to implementation package",
            tags=["spi", "purity", "control_flow"],
        )
        self.generic_visit(node)

    def visit_With(self, node: ast.With) -> None:
        self._add_violation(
            node,
            "SPI016",
            "SPI files must not contain with statements - protocols define contracts only",
            "Remove context manager logic or move to implementation package",
            tags=["spi", "purity", "control_flow"],
        )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if is_implementation_function_call(node):
            self._add_violation(
                node,
                "SPI016",
                f"SPI files must not contain function calls - found call to '{get_call_name(node)}'",
                "Remove function calls or move to implementation package",
                tags=["spi", "purity", "function_call"],
            )
        self.generic_visit(node)

    # -------------------------------------------------------------------------
    # Protocol class validation
    # -------------------------------------------------------------------------

    def _validate_protocol_class(self, node: ast.ClassDef) -> None:
        self.current_protocol = ProtocolInfo(
            name=node.name,
            file_path=self.file_path,
            module_path=get_module_path(self.file_path),
            line_number=node.lineno,
            domain=determine_domain(self.file_path),
        )
        self.in_protocol_class = True
        self.current_class_synchronous = class_declares_synchronous_execution(node)

        has_runtime_checkable = any(
            (isinstance(d, ast.Name) and d.id == "runtime_checkable")
            or (isinstance(d, ast.Attribute) and d.attr == "runtime_checkable")
            for d in node.decorator_list
        )
        self.current_protocol.is_runtime_checkable = has_runtime_checkable

        if not has_runtime_checkable:
            self._add_violation(
                node,
                "SPI003",
                f"Protocol '{node.name}' must be @runtime_checkable for isinstance() checks",
                "Add @runtime_checkable decorator above class definition",
                tags=["decorator", "runtime"],
            )

        if not node.name.startswith("Protocol"):
            self._add_violation(
                node,
                "SPI002",
                f"Protocol class '{node.name}' should start with 'Protocol' prefix",
                f"Rename class to 'Protocol{node.name[8:] if node.name.startswith('Protocol') else node.name}'",
                tags=["naming", "convention"],
            )

        docstring = ast.get_docstring(node)
        if not docstring or len(docstring.strip()) < 50:
            self._add_violation(
                node,
                "SPI014",
                f"Protocol '{node.name}' needs comprehensive docstring with examples",
                "Add detailed docstring explaining protocol purpose and usage examples",
                tags=["documentation", "examples"],
            )

        self._analyze_protocol_members(node)
        self.current_protocol.complexity_score = self._calculate_complexity_score(node)
        self.current_protocol.line_count = self._count_protocol_lines(node)
        self.current_protocol.signature_hash = generate_signature_hash(
            self.current_protocol.name,
            self.current_protocol.module_path,
            self.current_protocol.file_path,
            self.current_protocol.methods,
            self.current_protocol.properties,
        )
        self.protocols.append(self.current_protocol)

    def _validate_non_protocol_class(self, node: ast.ClassDef) -> None:
        if is_type_alias_class(node) or is_literal_class(node):
            return
        self._add_violation(
            node,
            "SPI007",
            f"SPI should not contain concrete class '{node.name}' - use Protocol instead",
            "Convert to Protocol class or move to implementation package",
            tags=["spi", "purity", "concrete"],
        )

    # -------------------------------------------------------------------------
    # Protocol method validation
    # -------------------------------------------------------------------------

    def _validate_protocol_method(self, node: ast.FunctionDef) -> None:
        method_name = node.name

        if method_name == "__init__":
            self.current_protocol.has_init = True
            self._add_violation(
                node,
                "SPI001",
                f"Protocol '{self.current_protocol.name}' should not have __init__ method",
                "Use @property accessors or class attributes instead of __init__",
                tags=["protocol", "init", "structure"],
                performance_impact="high",
            )

        if not has_ellipsis_body(node):
            self._add_violation(
                node,
                "SPI004",
                f"Protocol method '{method_name}' should have '...' implementation, not concrete code",
                "Replace method body with '...' for protocol definition",
                tags=["protocol", "implementation"],
            )

        if not has_complete_type_annotations(node):
            self._add_violation(
                node,
                "SPI015",
                f"Protocol method '{method_name}' needs complete type annotations",
                "Add type annotations to all parameters and return type",
                tags=["typing", "annotations"],
            )

        if should_be_async_method(node, self.current_class_synchronous):
            self.current_protocol.sync_io_methods.append(method_name)
            self._add_violation(
                node,
                "SPI005",
                f"Method '{method_name}' contains I/O operations - should be async def",
                "Change to 'async def' for I/O operations",
                tags=["async", "io"],
                performance_impact="medium",
            )

        if uses_object_instead_of_callable(node):
            self._add_violation(
                node,
                "SPI006",
                f"Method '{method_name}' uses 'object' type - use 'Callable' instead",
                "Replace 'object' with appropriate 'Callable[[...], ...]' type",
                tags=["typing", "callable"],
            )

        self.current_protocol.methods.append(get_method_signature(node))

    def _validate_async_protocol_method(self, node: ast.AsyncFunctionDef) -> None:
        method_name = node.name
        self.current_protocol.async_methods.append(method_name)

        if not has_ellipsis_body(node):
            self._add_violation(
                node,
                "SPI004",
                f"Async protocol method '{method_name}' should have '...' implementation",
                "Replace method body with '...' for protocol definition",
                tags=["protocol", "async", "implementation"],
            )

        self.current_protocol.methods.append(get_async_method_signature(node))

    def _validate_standalone_function(self, node: ast.FunctionDef) -> None:
        if (
            not node.name.startswith("_")
            and node.name not in ["main"]
            and not is_utility_function(node)
        ):
            self._add_violation(
                node,
                "SPI008",
                f"SPI should not contain standalone function '{node.name}'",
                "Move function to appropriate Protocol class or implementation package",
                tags=["spi", "purity", "function"],
            )

    def _class_declares_synchronous_execution(self, node: ast.ClassDef) -> bool:
        """Instance-method shim so tests can call this directly on the validator."""
        return class_declares_synchronous_execution(node)

    # -------------------------------------------------------------------------
    # Protocol analysis helpers
    # -------------------------------------------------------------------------

    def _analyze_protocol_members(self, node: ast.ClassDef) -> None:
        for item in node.body:
            if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                pass  # handled in visit methods
            elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                self.current_protocol.properties.append(item.target.id)

    def _calculate_complexity_score(self, node: ast.ClassDef) -> int:
        score = 0
        for item in node.body:
            if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                score += 2
                score += len(item.args.args) - 1
                if item.returns:
                    score += count_generic_complexity(item.returns)
            elif isinstance(item, ast.AnnAssign):
                score += 1
        return score

    def _count_protocol_lines(self, node: ast.ClassDef) -> int:
        if hasattr(node, "end_lineno") and node.end_lineno:
            return node.end_lineno - node.lineno + 1
        return len([item for item in node.body if not isinstance(item, ast.Expr)])

    def get_analysis_metrics(self) -> dict[str, Any]:
        analysis_time = time.time() - self.analysis_start_time
        return {
            "analysis_time_seconds": analysis_time,
            "nodes_processed": self.node_count,
            "violations_found": len(self.violations),
            "protocols_analyzed": len(self.protocols),
            "performance_score": self._calculate_performance_score(),
        }

    def _calculate_performance_score(self) -> float:
        if not self.protocols:
            return 1.0
        total_complexity = sum(p.complexity_score for p in self.protocols)
        violation_penalty = len(
            [v for v in self.violations if v.performance_impact != "none"]
        )
        base_score = 1.0
        complexity_penalty = min(0.3, total_complexity * 0.01)
        violation_penalty_score = min(0.4, violation_penalty * 0.05)
        return max(0.1, base_score - complexity_penalty - violation_penalty_score)
