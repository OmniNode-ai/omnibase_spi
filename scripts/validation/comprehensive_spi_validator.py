#!/usr/bin/env python3
"""
Comprehensive SPI Protocol Validation Framework - omnibase_spi Architecture Compliance

The definitive SPI compliance checker providing comprehensive architectural validation,
configurable rule engine, detailed reporting, and CI/CD integration capabilities.

Key Features:
1. No __init__ methods in protocol definitions
2. No duplicate protocol definitions with conflict resolution
3. All I/O operations must be async by default
4. Proper typing constraints (ContextValue, Callable patterns)
5. Namespace isolation compliance validation
6. @runtime_checkable decorator enforcement
7. Protocol naming convention validation
8. Type safety and forward reference validation
9. Configurable validation rules engine
10. Comprehensive reporting with fix suggestions
11. Pre-commit hooks and CI/CD integration ready
12. Performance optimization with caching

Usage:
    # Basic validation with comprehensive checks
    python scripts/validation/comprehensive_spi_validator.py src/

    # Validation with configuration file
    python scripts/validation/comprehensive_spi_validator.py src/ --config validation_config.yaml

    # Auto-fix mode for supported violations
    python scripts/validation/comprehensive_spi_validator.py src/ --fix

    # Generate JSON report for CI/CD integration
    python scripts/validation/comprehensive_spi_validator.py src/ --json-report

    # Pre-commit integration mode
    python scripts/validation/comprehensive_spi_validator.py --pre-commit

Author: Claude Code Agent (ONEX Framework)
Version: 2.0.0
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

# Import existing timeout utilities
import timeout_utils
import yaml
from timeout_utils import timeout_context

# ============================================================================
# Core Data Structures
# ============================================================================


@dataclass
class ValidationRule:
    """Configuration for a validation rule."""

    rule_id: str
    name: str
    description: str
    severity: str  # 'error', 'warning', 'info'
    enabled: bool = True
    auto_fixable: bool = False
    category: str = "general"
    priority: int = 1
    dependencies: List[str] = field(default_factory=list)
    configuration: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProtocolViolation:
    """Enhanced violation tracking with fix suggestions and context."""

    file_path: str
    line_number: int
    column_offset: int
    rule_id: str
    violation_type: str
    message: str
    severity: str
    suggestion: str = ""
    auto_fix_available: bool = False
    context_lines: List[str] = field(default_factory=list)
    related_violations: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    performance_impact: str = "none"  # 'none', 'low', 'medium', 'high'

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "file_path": self.file_path,
            "line_number": self.line_number,
            "column_offset": self.column_offset,
            "rule_id": self.rule_id,
            "violation_type": self.violation_type,
            "message": self.message,
            "severity": self.severity,
            "suggestion": self.suggestion,
            "auto_fix_available": self.auto_fix_available,
            "context_lines": self.context_lines,
            "related_violations": self.related_violations,
            "tags": self.tags,
            "performance_impact": self.performance_impact,
        }


@dataclass
class ProtocolInfo:
    """Enhanced protocol information with dependency tracking."""

    name: str
    file_path: str
    module_path: str
    line_number: int
    methods: List[str] = field(default_factory=list)
    properties: List[str] = field(default_factory=list)
    signature_hash: str = ""
    is_runtime_checkable: bool = False
    has_init: bool = False
    async_methods: List[str] = field(default_factory=list)
    sync_io_methods: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    forward_references: List[str] = field(default_factory=list)
    protocol_dependencies: List[str] = field(default_factory=list)
    domain: str = "unknown"
    complexity_score: int = 0
    line_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "file_path": self.file_path,
            "module_path": self.module_path,
            "line_number": self.line_number,
            "methods": self.methods,
            "properties": self.properties,
            "signature_hash": self.signature_hash,
            "is_runtime_checkable": self.is_runtime_checkable,
            "has_init": self.has_init,
            "async_methods": self.async_methods,
            "sync_io_methods": self.sync_io_methods,
            "imports": self.imports,
            "forward_references": self.forward_references,
            "protocol_dependencies": self.protocol_dependencies,
            "domain": self.domain,
            "complexity_score": self.complexity_score,
            "line_count": self.line_count,
        }


@dataclass
class ValidationReport:
    """Comprehensive validation report with metrics and insights."""

    total_files: int = 0
    total_protocols: int = 0
    violations: List[ProtocolViolation] = field(default_factory=list)
    protocols: List[ProtocolInfo] = field(default_factory=list)
    execution_time: float = 0.0
    validation_rules_applied: int = 0
    auto_fixes_applied: int = 0
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)

    @property
    def error_count(self) -> int:
        """Count of error-level violations."""
        return sum(1 for v in self.violations if v.severity == "error")

    @property
    def warning_count(self) -> int:
        """Count of warning-level violations."""
        return sum(1 for v in self.violations if v.severity == "warning")

    @property
    def info_count(self) -> int:
        """Count of info-level violations."""
        return sum(1 for v in self.violations if v.severity == "info")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "summary": {
                "total_files": self.total_files,
                "total_protocols": self.total_protocols,
                "error_count": self.error_count,
                "warning_count": self.warning_count,
                "info_count": self.info_count,
                "execution_time": self.execution_time,
                "validation_rules_applied": self.validation_rules_applied,
                "auto_fixes_applied": self.auto_fixes_applied,
            },
            "violations": [v.to_dict() for v in self.violations],
            "protocols": [p.to_dict() for p in self.protocols],
            "performance_metrics": self.performance_metrics,
            "recommendations": self.recommendations,
        }


# ============================================================================
# Configuration Management
# ============================================================================


class ValidationConfig:
    """Configuration manager for validation rules and settings."""

    def __init__(self, config_file: Optional[str] = None):
        self.rules: Dict[str, ValidationRule] = {}
        self.global_settings: Dict[str, Any] = {}
        self._load_default_config()

        if config_file and Path(config_file).exists():
            self._load_config_file(config_file)

    def _load_default_config(self) -> None:
        """Load default validation rules configuration."""
        default_rules = [
            ValidationRule(
                rule_id="SPI001",
                name="No Protocol __init__ Methods",
                description="Protocols should not have __init__ methods - use properties or class attributes instead",
                severity="error",
                auto_fixable=False,
                category="protocol_structure",
                priority=1,
            ),
            ValidationRule(
                rule_id="SPI002",
                name="Protocol Naming Convention",
                description="Protocol classes should start with 'Protocol' prefix for consistency",
                severity="warning",
                auto_fixable=False,
                category="naming",
                priority=2,
            ),
            ValidationRule(
                rule_id="SPI003",
                name="Runtime Checkable Decorator",
                description="All protocols must be @runtime_checkable for isinstance() support",
                severity="error",
                auto_fixable=True,
                category="decorators",
                priority=1,
            ),
            ValidationRule(
                rule_id="SPI004",
                name="Protocol Method Bodies",
                description="Protocol methods should have '...' implementation, not concrete code",
                severity="error",
                auto_fixable=True,
                category="protocol_structure",
                priority=1,
            ),
            ValidationRule(
                rule_id="SPI005",
                name="Async I/O Operations",
                description="I/O operations should use async def instead of synchronous patterns",
                severity="error",
                auto_fixable=True,
                category="async_patterns",
                priority=1,
            ),
            ValidationRule(
                rule_id="SPI006",
                name="Proper Callable Types",
                description="Use 'Callable' types instead of generic 'object' for function parameters",
                severity="error",
                auto_fixable=False,
                category="typing",
                priority=1,
            ),
            ValidationRule(
                rule_id="SPI007",
                name="No Concrete Classes in SPI",
                description="SPI should only contain Protocol definitions, not concrete implementations",
                severity="error",
                auto_fixable=False,
                category="spi_purity",
                priority=1,
            ),
            ValidationRule(
                rule_id="SPI008",
                name="No Standalone Functions",
                description="SPI should not contain standalone functions - use Protocol methods instead",
                severity="warning",
                auto_fixable=False,
                category="spi_purity",
                priority=2,
            ),
            ValidationRule(
                rule_id="SPI009",
                name="ContextValue Usage Patterns",
                description="Consistent ContextValue usage for type-safe context data",
                severity="warning",
                auto_fixable=False,
                category="typing",
                priority=2,
            ),
            ValidationRule(
                rule_id="SPI010",
                name="Duplicate Protocol Detection",
                description="No duplicate protocol definitions with identical signatures",
                severity="error",
                auto_fixable=False,
                category="duplicates",
                priority=1,
            ),
            ValidationRule(
                rule_id="SPI011",
                name="Protocol Name Conflicts",
                description="No naming conflicts between protocols with different signatures",
                severity="error",
                auto_fixable=False,
                category="duplicates",
                priority=1,
            ),
            ValidationRule(
                rule_id="SPI012",
                name="Namespace Isolation",
                description="Maintain strict namespace isolation with omnibase_spi.protocols.* imports only",
                severity="error",
                auto_fixable=False,
                category="namespace",
                priority=1,
            ),
            ValidationRule(
                rule_id="SPI013",
                name="Forward Reference Typing",
                description="Use proper forward references with TYPE_CHECKING for model types",
                severity="warning",
                auto_fixable=False,
                category="typing",
                priority=2,
            ),
            ValidationRule(
                rule_id="SPI014",
                name="Protocol Documentation",
                description="All protocols should have comprehensive docstrings with examples",
                severity="warning",
                auto_fixable=False,
                category="documentation",
                priority=3,
            ),
            ValidationRule(
                rule_id="SPI015",
                name="Method Type Annotations",
                description="All protocol methods must have complete type annotations",
                severity="error",
                auto_fixable=False,
                category="typing",
                priority=1,
            ),
            ValidationRule(
                rule_id="SPI016",
                name="SPI Implementation Purity",
                description="SPI files must not contain implementation logic (if/else, assignments, function calls)",
                severity="error",
                auto_fixable=False,
                category="purity",
                priority=1,
            ),
        ]

        for rule in default_rules:
            self.rules[rule.rule_id] = rule

        # Global settings
        self.global_settings = {
            "max_file_size": 1024 * 1024,  # 1MB max file size
            "timeout_seconds": 300,  # 5 minute timeout
            "parallel_processing": True,
            "enable_caching": True,
            "cache_ttl_seconds": 3600,  # 1 hour cache TTL
            "max_violations_per_file": 100,
            "enable_performance_metrics": True,
        }

    def _load_config_file(self, config_file: str) -> None:
        """Load configuration from YAML file."""
        try:
            with open(config_file, "r") as f:
                config_data = yaml.safe_load(f)

            # Update global settings
            if "global_settings" in config_data:
                self.global_settings.update(config_data["global_settings"])

            # Update rules
            if "rules" in config_data:
                for rule_config in config_data["rules"]:
                    rule_id = rule_config.get("rule_id")
                    if rule_id in self.rules:
                        # Update existing rule
                        rule = self.rules[rule_id]
                        for key, value in rule_config.items():
                            if hasattr(rule, key):
                                setattr(rule, key, value)

        except Exception as e:
            print(f"Warning: Failed to load config file {config_file}: {e}")

    def get_enabled_rules(self) -> List[ValidationRule]:
        """Get all enabled validation rules sorted by priority."""
        enabled_rules = [rule for rule in self.rules.values() if rule.enabled]
        return sorted(enabled_rules, key=lambda r: (r.priority, r.rule_id))

    def get_rule(self, rule_id: str) -> Optional[ValidationRule]:
        """Get a specific validation rule by ID."""
        return self.rules.get(rule_id)


# ============================================================================
# Enhanced Protocol Analyzer with Comprehensive Validation
# ============================================================================


class ComprehensiveSPIValidator(ast.NodeVisitor):
    """
    Advanced AST-based SPI protocol validator with comprehensive rule engine.

    Provides deep analysis of Python protocol files with configurable validation
    rules, performance optimization, and detailed reporting capabilities.
    """

    def __init__(self, file_path: str, config: ValidationConfig):
        self.file_path = file_path
        self.config = config
        self.violations: List[ProtocolViolation] = []
        self.protocols: List[ProtocolInfo] = []

        # Analysis state
        self.current_protocol: Optional[ProtocolInfo] = None
        self.in_protocol_class: bool = False
        self.imports: Dict[str, str] = {}
        self.type_checking_imports: Set[str] = set()
        self.forward_references: Set[str] = set()
        self.current_class_decorators: List[str] = []

        # Performance metrics
        self.analysis_start_time = time.time()
        self.node_count = 0

        # Context tracking
        self.source_lines: List[str] = []
        self._load_source_lines()

    def _load_source_lines(self) -> None:
        """Load source file lines for context extraction."""
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                self.source_lines = f.readlines()
        except Exception:
            self.source_lines = []

    def _get_context_lines(self, line_number: int, context_size: int = 2) -> List[str]:
        """Get context lines around the specified line number."""
        start = max(0, line_number - context_size - 1)
        end = min(len(self.source_lines), line_number + context_size)
        return [line.rstrip() for line in self.source_lines[start:end]]

    def _add_violation(
        self,
        node: ast.AST,
        rule_id: str,
        message: str,
        suggestion: str = "",
        tags: Optional[List[str]] = None,
        performance_impact: str = "none",
    ) -> None:
        """Add a validation violation with enhanced context."""
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
        """Override visit to track performance metrics."""
        self.node_count += 1
        super().visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        """Enhanced import tracking with namespace validation."""
        for alias in node.names:
            import_name = alias.name
            as_name = alias.asname or alias.name
            self.imports[as_name] = import_name

            # Check namespace isolation
            if not self._is_allowed_import(import_name):
                self._add_violation(
                    node,
                    "SPI012",
                    f"Import '{import_name}' violates namespace isolation - use omnibase_spi.protocols.* only",
                    "Replace with appropriate omnibase_spi.protocols import",
                    tags=["namespace", "isolation"],
                )

        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Enhanced from import tracking with TYPE_CHECKING detection."""
        if node.module:
            # Track TYPE_CHECKING imports
            if node.module == "typing" and any(
                alias.name == "TYPE_CHECKING" for alias in node.names
            ):
                self.type_checking_imports.add("TYPE_CHECKING")

            for alias in node.names:
                full_name = f"{node.module}.{alias.name}"
                as_name = alias.asname or alias.name
                self.imports[as_name] = full_name

                # Check namespace isolation for SPI modules
                if not self._is_allowed_import(node.module):
                    self._add_violation(
                        node,
                        "SPI012",
                        f"Import from '{node.module}' violates namespace isolation",
                        "Use omnibase_spi.protocols imports or typing imports only",
                        tags=["namespace", "isolation"],
                    )

        self.generic_visit(node)

    def visit_If(self, node: ast.If) -> None:
        """Track TYPE_CHECKING blocks for forward reference validation."""
        if (
            isinstance(node.test, ast.Name)
            and node.test.id == "TYPE_CHECKING"
            and "TYPE_CHECKING" in self.type_checking_imports
        ):

            # Inside TYPE_CHECKING block - track imports
            for child in ast.walk(node):
                if isinstance(child, ast.ImportFrom) and child.module:
                    for alias in child.names:
                        self.forward_references.add(alias.asname or alias.name)

        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Enhanced protocol class validation with comprehensive checks."""
        is_protocol = self._is_protocol_class(node)

        if is_protocol:
            self._validate_protocol_class_comprehensive(node)
        else:
            self._validate_non_protocol_class(node)

        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Enhanced function validation with typing and async checks."""
        if self.in_protocol_class:
            self._validate_protocol_method_comprehensive(node)
        else:
            self._validate_standalone_function(node)

        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Enhanced async function validation."""
        if self.in_protocol_class:
            self._validate_async_protocol_method(node)

        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        """Detect assignment statements that violate SPI purity."""
        if self._is_spi_implementation_violation(node):
            self._add_violation(
                node,
                "SPI016",
                "SPI files must not contain assignment logic - use type annotations only",
                "Remove assignment logic or move to implementation package",
                tags=["spi", "purity", "assignment"],
            )
        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        """Detect augmented assignment statements (+=, -=, etc.)."""
        self._add_violation(
            node,
            "SPI016",
            "SPI files must not contain augmented assignment logic",
            "Remove assignment logic or move to implementation package",
            tags=["spi", "purity", "assignment"],
        )
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        """Detect for loops that violate SPI purity."""
        self._add_violation(
            node,
            "SPI016",
            "SPI files must not contain for loops - protocols define contracts only",
            "Remove loop logic or move to implementation package",
            tags=["spi", "purity", "control_flow"],
        )
        self.generic_visit(node)

    def visit_While(self, node: ast.While) -> None:
        """Detect while loops that violate SPI purity."""
        self._add_violation(
            node,
            "SPI016",
            "SPI files must not contain while loops - protocols define contracts only",
            "Remove loop logic or move to implementation package",
            tags=["spi", "purity", "control_flow"],
        )
        self.generic_visit(node)

    def visit_Try(self, node: ast.Try) -> None:
        """Detect try/except blocks that violate SPI purity."""
        self._add_violation(
            node,
            "SPI016",
            "SPI files must not contain try/except blocks - protocols define contracts only",
            "Remove exception handling or move to implementation package",
            tags=["spi", "purity", "control_flow"],
        )
        self.generic_visit(node)

    def visit_With(self, node: ast.With) -> None:
        """Detect with statements that violate SPI purity."""
        self._add_violation(
            node,
            "SPI016",
            "SPI files must not contain with statements - protocols define contracts only",
            "Remove context manager logic or move to implementation package",
            tags=["spi", "purity", "control_flow"],
        )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Detect function calls that violate SPI purity."""
        if self._is_implementation_function_call(node):
            self._add_violation(
                node,
                "SPI016",
                f"SPI files must not contain function calls - found call to '{self._get_call_name(node)}'",
                "Remove function calls or move to implementation package",
                tags=["spi", "purity", "function_call"],
            )
        self.generic_visit(node)

    def _is_protocol_class(self, node: ast.ClassDef) -> bool:
        """Enhanced protocol class detection."""
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == "Protocol":
                return True
            if isinstance(base, ast.Attribute) and base.attr == "Protocol":
                return True
        return False

    def _is_allowed_import(self, import_name: str) -> bool:
        """Check if import is allowed under namespace isolation rules."""
        allowed_prefixes = [
            "typing",
            "typing_extensions",
            "omnibase_spi.protocols",
            "datetime",
            "uuid",
            "__future__",
            "collections.abc",  # Standard library abstract base classes
        ]

        return any(import_name.startswith(prefix) for prefix in allowed_prefixes)

    def _validate_protocol_class_comprehensive(self, node: ast.ClassDef) -> None:
        """Comprehensive protocol class validation."""
        self.current_protocol = ProtocolInfo(
            name=node.name,
            file_path=self.file_path,
            module_path=self._get_module_path(self.file_path),
            line_number=node.lineno,
            domain=self._determine_domain(self.file_path),
        )

        self.in_protocol_class = True
        self.current_class_decorators = [
            d.id if hasattr(d, "id") else str(d) for d in node.decorator_list
        ]

        # Check @runtime_checkable decorator
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

        # Check protocol naming convention
        if not node.name.startswith("Protocol"):
            self._add_violation(
                node,
                "SPI002",
                f"Protocol class '{node.name}' should start with 'Protocol' prefix",
                f"Rename class to 'Protocol{node.name[8:] if node.name.startswith('Protocol') else node.name}'",
                tags=["naming", "convention"],
            )

        # Check documentation
        docstring = ast.get_docstring(node)
        if not docstring or len(docstring.strip()) < 50:
            self._add_violation(
                node,
                "SPI014",
                f"Protocol '{node.name}' needs comprehensive docstring with examples",
                "Add detailed docstring explaining protocol purpose and usage examples",
                tags=["documentation", "examples"],
            )

        # Analyze protocol methods and properties
        self._analyze_protocol_members(node)

        # Calculate complexity score
        self.current_protocol.complexity_score = self._calculate_complexity_score(node)
        self.current_protocol.line_count = self._count_protocol_lines(node)

        # Generate signature hash for duplicate detection
        self.current_protocol.signature_hash = self._generate_signature_hash()

        self.protocols.append(self.current_protocol)

    def _validate_protocol_method_comprehensive(self, node: ast.FunctionDef) -> None:
        """Comprehensive protocol method validation."""
        method_name = node.name

        # Check for __init__ method (major SPI violation)
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

        # Check for concrete implementation
        if not self._has_ellipsis_body(node):
            self._add_violation(
                node,
                "SPI004",
                f"Protocol method '{method_name}' should have '...' implementation, not concrete code",
                "Replace method body with '...' for protocol definition",
                tags=["protocol", "implementation"],
            )

        # Check type annotations
        if not self._has_complete_type_annotations(node):
            self._add_violation(
                node,
                "SPI015",
                f"Protocol method '{method_name}' needs complete type annotations",
                "Add type annotations to all parameters and return type",
                tags=["typing", "annotations"],
            )

        # Check for sync I/O operations that should be async
        if self._should_be_async_method(node):
            self.current_protocol.sync_io_methods.append(method_name)
            self._add_violation(
                node,
                "SPI005",
                f"Method '{method_name}' contains I/O operations - should be async def",
                "Change to 'async def' for I/O operations",
                tags=["async", "io"],
                performance_impact="medium",
            )

        # Check for improper object usage instead of Callable
        if self._uses_object_instead_of_callable(node):
            self._add_violation(
                node,
                "SPI006",
                f"Method '{method_name}' uses 'object' type - use 'Callable' instead",
                "Replace 'object' with appropriate 'Callable[[...], ...]' type",
                tags=["typing", "callable"],
            )

        # Track method for protocol analysis
        method_signature = self._get_method_signature(node)
        self.current_protocol.methods.append(method_signature)

    def _validate_async_protocol_method(self, node: ast.AsyncFunctionDef) -> None:
        """Validate async protocol methods."""
        method_name = node.name
        self.current_protocol.async_methods.append(method_name)

        # Check for concrete implementation
        if not self._has_ellipsis_body(node):
            self._add_violation(
                node,
                "SPI004",
                f"Async protocol method '{method_name}' should have '...' implementation",
                "Replace method body with '...' for protocol definition",
                tags=["protocol", "async", "implementation"],
            )

        # Track async method
        method_signature = self._get_async_method_signature(node)
        self.current_protocol.methods.append(method_signature)

    def _validate_non_protocol_class(self, node: ast.ClassDef) -> None:
        """Validate non-protocol classes in SPI context."""
        # Skip type alias classes and enum-like classes
        if self._is_type_alias_class(node) or self._is_literal_class(node):
            return

        self._add_violation(
            node,
            "SPI007",
            f"SPI should not contain concrete class '{node.name}' - use Protocol instead",
            "Convert to Protocol class or move to implementation package",
            tags=["spi", "purity", "concrete"],
        )

    def _validate_standalone_function(self, node: ast.FunctionDef) -> None:
        """Validate standalone functions in SPI context."""
        if (
            not node.name.startswith("_")
            and node.name not in ["main"]
            and not self._is_utility_function(node)
        ):

            self._add_violation(
                node,
                "SPI008",
                f"SPI should not contain standalone function '{node.name}'",
                "Move function to appropriate Protocol class or implementation package",
                tags=["spi", "purity", "function"],
            )

    def _analyze_protocol_members(self, node: ast.ClassDef) -> None:
        """Analyze protocol members for comprehensive reporting."""
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Already handled in visit methods
                pass
            elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                # Property annotation
                prop_name = item.target.id
                self.current_protocol.properties.append(prop_name)

    def _calculate_complexity_score(self, node: ast.ClassDef) -> int:
        """Calculate protocol complexity score for analysis."""
        score = 0

        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                score += 2
                # Add complexity for parameters
                score += len(item.args.args) - 1  # Subtract 1 for 'self'
                # Add complexity for generic types
                if item.returns:
                    score += self._count_generic_complexity(item.returns)
            elif isinstance(item, ast.AnnAssign):
                score += 1

        return score

    def _count_protocol_lines(self, node: ast.ClassDef) -> int:
        """Count effective lines of code in protocol."""
        if hasattr(node, "end_lineno") and node.end_lineno:
            return node.end_lineno - node.lineno + 1
        return len([item for item in node.body if not isinstance(item, ast.Expr)])

    def _generate_signature_hash(self) -> str:
        """Generate signature hash for duplicate detection with collision resistance."""
        # Include protocol name and file path to prevent false collisions
        protocol_name = self.current_protocol.name
        file_path = self.current_protocol.file_path
        module_path = self.current_protocol.module_path

        # Sort methods and properties for consistency
        methods_str = "|".join(sorted(self.current_protocol.methods))
        props_str = "|".join(sorted(self.current_protocol.properties))

        # Include additional identifying information to prevent false collisions
        combined = f"name:{protocol_name}|module:{module_path}|methods:{methods_str}|props:{props_str}|file:{Path(file_path).name}"

        # Use SHA256 for better collision resistance and longer hash
        return hashlib.sha256(combined.encode()).hexdigest()[:16]

    def _has_ellipsis_body(
        self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]
    ) -> bool:
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
            first_is_docstring = (
                isinstance(node.body[0], ast.Expr)
                and isinstance(node.body[0].value, ast.Constant)
                and isinstance(node.body[0].value.value, str)
            )
            second_is_ellipsis = (
                isinstance(node.body[1], ast.Expr)
                and isinstance(node.body[1].value, ast.Constant)
                and node.body[1].value.value is ...
            )
            return first_is_docstring and second_is_ellipsis

        return False

    def _is_spi_implementation_violation(self, node: ast.Assign) -> bool:
        """Check if assignment violates SPI purity (not a type annotation)."""
        # Allow legitimate module-level assignments
        for target in node.targets:
            if isinstance(target, ast.Name):
                # Allow __all__, __version__, __author__, etc.
                if target.id.startswith("__") and target.id.endswith("__"):
                    return False

                # Allow module-level constants (all caps)
                if target.id.isupper():
                    return False

                # Allow type aliases and type definitions
                if self._is_type_alias_assignment(target.id, node.value):
                    return False

                # Allow common module-level patterns
                if self._is_allowed_module_assignment(target.id, node.value):
                    return False

        # Only flag if this looks like implementation logic inside protocols
        return self._is_implementation_logic(node)

    def _is_type_alias_assignment(self, var_name: str, value_node: ast.AST) -> bool:
        """Check if this looks like a type alias assignment."""
        # Type alias patterns
        type_alias_patterns = [
            "Literal",
            "Protocol",
            "Union",
            "Optional",
            "Dict",
            "List",
            "Tuple",
            "Set",
            "Type",
            "Callable",
            "Generic",
            "TypeVar",
            "Final",
            "ClassVar",
            "Any",
            "NoReturn",
            "TypeAlias",
        ]

        # Check if variable name follows type alias conventions
        if var_name.startswith(("Literal", "Protocol", "Type")):
            return True

        # Common type alias naming patterns
        if var_name.endswith(
            ("Type", "Types", "Value", "Values", "State", "States", "Status")
        ):
            return True

        # CamelCase names that look like type definitions
        if var_name[0].isupper() and any(c.isupper() for c in var_name[1:]):
            return True

        # Check if the value is a typing construct
        if isinstance(value_node, ast.Subscript):
            if isinstance(value_node.value, ast.Name):
                return value_node.value.id in type_alias_patterns
            elif isinstance(value_node.value, ast.Attribute):
                return value_node.value.attr in type_alias_patterns

        # Check if it's a direct reference to a type
        if isinstance(value_node, ast.Name):
            return value_node.id in type_alias_patterns or value_node.id[0].isupper()

        if isinstance(value_node, ast.Attribute):
            return (
                value_node.attr in type_alias_patterns or value_node.attr[0].isupper()
            )

        return False

    def _is_allowed_module_assignment(self, var_name: str, value_node: ast.AST) -> bool:
        """Check if this is an allowed module-level assignment."""
        # Allow common module-level patterns
        allowed_patterns = {
            # Version and metadata
            "version",
            "VERSION",
            "__version__",
            "SCHEMA_VERSION",
            "API_VERSION",
            # Module exports
            "__all__",
            "__author__",
            "__email__",
            "__license__",
            "__copyright__",
            # Configuration constants
            "DEFAULT_",
            "MAX_",
            "MIN_",
            "TIMEOUT_",
            "CONFIG_",
            # Type definitions that don't follow strict patterns
            "_T",
            "_P",
            "_V",
            "_K",
            "_Return",
            "_Args",
            "_Self",
        }

        # Check exact matches
        if var_name in allowed_patterns:
            return True

        # Check prefix matches
        if any(
            var_name.startswith(pattern)
            for pattern in allowed_patterns
            if pattern.endswith("_")
        ):
            return True

        # Allow simple string/number literals for constants
        if isinstance(value_node, ast.Constant):
            if isinstance(value_node.value, (str, int, float, bool)):
                return True

        # Allow None assignments for optional module attributes
        if isinstance(value_node, ast.Constant) and value_node.value is None:
            return True

        return False

    def _is_implementation_logic(self, node: ast.Assign) -> bool:
        """Check if this assignment contains implementation logic."""
        # Only flag assignments that contain obvious implementation logic
        for target in node.targets:
            if isinstance(target, ast.Attribute):
                # self.something = ... inside a protocol is definitely implementation
                if (
                    isinstance(target.value, ast.Name)
                    and target.value.id == "self"
                    and self.in_protocol_class
                ):
                    return True

            elif isinstance(target, ast.Subscript):
                # dict[key] = value type assignments are implementation
                return True

        # Check if value involves function calls (implementation logic)
        if self._contains_function_calls(node.value):
            return True

        # Check for complex expressions that look like implementation
        if self._is_complex_implementation_expression(node.value):
            return True

        return False

    def _contains_function_calls(self, node: ast.AST) -> bool:
        """Check if node contains function calls (implementation logic)."""
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                # Allow specific typing-related calls
                allowed_calls = {
                    "TypeVar",
                    "Generic",
                    "Union",
                    "Optional",
                    "Literal",
                    "Final",
                    "ClassVar",
                    "runtime_checkable",
                    "Protocol",
                }
                call_name = self._get_call_name(child)
                if call_name not in allowed_calls:
                    return True
        return False

    def _is_complex_implementation_expression(self, node: ast.AST) -> bool:
        """Check if expression is complex implementation logic."""
        # Flag complex expressions that involve computation
        if isinstance(node, (ast.BinOp, ast.BoolOp, ast.Compare, ast.IfExp)):
            return True

        # Flag comprehensions (implementation logic)
        if isinstance(
            node, (ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)
        ):
            return True

        return False

    def _is_implementation_function_call(self, node: ast.Call) -> bool:
        """Check if function call violates SPI purity."""
        call_name = self._get_call_name(node)

        # Allow these specific calls that are common in protocols and typing
        allowed_calls = {
            "hasattr",  # Often used incorrectly in protocols
            "isinstance",
            "getattr",
            "setattr",
            "len",
            # Typing system constructs
            "TypeVar",
            "Generic",
            "Union",
            "Optional",
            "Literal",
            "get_args",
            "get_origin",
            "runtime_checkable",
            "Protocol",
            "overload",
            "cast",
            "TYPE_CHECKING",
            "ForwardRef",
            "_GenericAlias",
            "_SpecialForm",
        }

        # Allow ellipsis and type checking utilities
        if call_name in ["...", "Ellipsis", "TYPE_CHECKING"]:
            return False

        # Allow typing and validation calls, disallow implementation logic
        return call_name not in allowed_calls

    def _get_call_name(self, node: ast.Call) -> str:
        """Extract function call name for reporting."""
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            return node.func.attr
        else:
            return "unknown_call"

    def _has_complete_type_annotations(self, node: ast.FunctionDef) -> bool:
        """Check if method has complete type annotations."""
        # Check return annotation
        if not node.returns:
            return False

        # Check parameter annotations (excluding 'self')
        for arg in node.args.args[1:]:  # Skip 'self'
            if not arg.annotation:
                return False

        return True

    def _should_be_async_method(self, node: ast.FunctionDef) -> bool:
        """Determine if method should be async based on naming and types."""
        method_name = node.name.lower()
        io_indicators = [
            "read",
            "write",
            "open",
            "close",
            "connect",
            "disconnect",
            "send",
            "receive",
            "get",
            "post",
            "put",
            "delete",
            "fetch",
            "load",
            "save",
            "store",
            "query",
            "execute",
        ]

        # Check method name patterns
        if any(indicator in method_name for indicator in io_indicators):
            return True

        # Check return type annotations for async patterns
        if node.returns:
            return_type = ast.unparse(node.returns)
            if any(
                async_hint in return_type.lower()
                for async_hint in ["response", "connection", "client", "result", "data"]
            ):
                return True

        return False

    def _uses_object_instead_of_callable(self, node: ast.FunctionDef) -> bool:
        """Check for object type usage where Callable would be more appropriate."""
        if node.returns:
            return_type = ast.unparse(node.returns)
            if "object" in return_type and any(
                word in node.name.lower()
                for word in ["callback", "handler", "func", "callable"]
            ):
                return True

        # Check parameter types
        for arg in node.args.args:
            if arg.annotation:
                arg_type = ast.unparse(arg.annotation)
                if "object" in arg_type and any(
                    word in arg.arg for word in ["callback", "handler", "func"]
                ):
                    return True

        return False

    def _is_type_alias_class(self, node: ast.ClassDef) -> bool:
        """Check if class is a type alias definition."""
        return (
            len(node.bases) == 0
            and len(node.body) <= 2  # Allow for docstring + assignment
            and any(isinstance(item, ast.Assign) for item in node.body)
        )

    def _is_literal_class(self, node: ast.ClassDef) -> bool:
        """Check if class is a Literal-style constant definition."""
        return len(node.bases) == 0 and all(
            isinstance(item, (ast.Assign, ast.AnnAssign, ast.Expr))
            for item in node.body
        )

    def _is_utility_function(self, node: ast.FunctionDef) -> bool:
        """Check if function is a utility function that's acceptable in SPI."""
        utility_patterns = ["_", "get_", "create_", "build_", "make_"]
        return any(node.name.startswith(pattern) for pattern in utility_patterns)

    def _count_generic_complexity(self, annotation: ast.AST) -> int:
        """Count complexity of generic type annotations."""
        complexity = 0
        for node in ast.walk(annotation):
            if isinstance(node, ast.Subscript):
                complexity += 1
        return complexity

    def _get_method_signature(self, node: ast.FunctionDef) -> str:
        """Get detailed method signature for comparison."""
        args = []
        for arg in node.args.args:
            if arg.arg != "self":
                arg_type = ast.unparse(arg.annotation) if arg.annotation else "Any"
                args.append(f"{arg.arg}: {arg_type}")

        returns = ast.unparse(node.returns) if node.returns else "None"
        return f"{node.name}({', '.join(args)}) -> {returns}"

    def _get_async_method_signature(self, node: ast.AsyncFunctionDef) -> str:
        """Get async method signature for comparison."""
        args = []
        for arg in node.args.args:
            if arg.arg != "self":
                arg_type = ast.unparse(arg.annotation) if arg.annotation else "Any"
                args.append(f"{arg.arg}: {arg_type}")

        returns = ast.unparse(node.returns) if node.returns else "None"
        return f"async {node.name}({', '.join(args)}) -> {returns}"

    def _get_module_path(self, file_path: str) -> str:
        """Get Python module path from file path."""
        path = Path(file_path)
        parts = list(path.parts)

        # Remove src/ prefix and convert to module path
        if "src" in parts:
            src_idx = parts.index("src")
            module_parts = parts[src_idx + 1 :]
        else:
            module_parts = parts

        # Remove .py extension
        if module_parts and module_parts[-1].endswith(".py"):
            module_parts[-1] = module_parts[-1][:-3]

        return ".".join(module_parts)

    def _determine_domain(self, file_path: str) -> str:
        """Determine protocol domain from file path."""
        path_parts = Path(file_path).parts

        domain_mapping = {
            "workflow_orchestration": "workflow",
            "mcp": "mcp",
            "event_bus": "events",
            "container": "container",
            "core": "core",
            "types": "types",
            "file_handling": "files",
            "discovery": "discovery",
        }

        for part in path_parts:
            if part in domain_mapping:
                return domain_mapping[part]

        return "unknown"

    def get_analysis_metrics(self) -> Dict[str, Any]:
        """Get performance and analysis metrics."""
        analysis_time = time.time() - self.analysis_start_time

        return {
            "analysis_time_seconds": analysis_time,
            "nodes_processed": self.node_count,
            "violations_found": len(self.violations),
            "protocols_analyzed": len(self.protocols),
            "performance_score": self._calculate_performance_score(),
        }

    def _calculate_performance_score(self) -> float:
        """Calculate performance score for the file."""
        if not self.protocols:
            return 1.0

        total_complexity = sum(p.complexity_score for p in self.protocols)
        violation_penalty = len(
            [v for v in self.violations if v.performance_impact != "none"]
        )

        # Higher complexity and violations lower the score
        base_score = 1.0
        complexity_penalty = min(0.3, total_complexity * 0.01)
        violation_penalty_score = min(0.4, violation_penalty * 0.05)

        return max(0.1, base_score - complexity_penalty - violation_penalty_score)


# ============================================================================
# Duplicate Detection and Conflict Resolution
# ============================================================================


class DuplicateProtocolAnalyzer:
    """Advanced duplicate protocol detection with conflict resolution strategies."""

    def __init__(self, config: ValidationConfig):
        self.config = config

    def analyze_duplicates(
        self, protocols: List[ProtocolInfo]
    ) -> List[ProtocolViolation]:
        """Comprehensive duplicate analysis with multiple detection strategies."""
        violations = []

        # Group protocols by various criteria
        by_signature = defaultdict(list)
        by_name = defaultdict(list)
        by_semantic_similarity = defaultdict(list)

        for protocol in protocols:
            by_signature[protocol.signature_hash].append(protocol)
            by_name[protocol.name].append(protocol)

            # Semantic similarity grouping
            semantic_key = self._get_semantic_key(protocol)
            by_semantic_similarity[semantic_key].append(protocol)

        # Detect exact duplicates
        violations.extend(self._find_exact_duplicates(by_signature))

        # Detect name conflicts
        violations.extend(self._find_name_conflicts(by_name))

        # Detect semantic duplicates
        violations.extend(self._find_semantic_duplicates(by_semantic_similarity))

        return violations

    def _find_exact_duplicates(
        self, by_signature: Dict[str, List[ProtocolInfo]]
    ) -> List[ProtocolViolation]:
        """Find protocols with identical signatures."""
        violations = []

        for signature_hash, duplicate_protocols in by_signature.items():
            if len(duplicate_protocols) > 1:
                # Verify these are truly duplicates, not just hash collisions
                truly_duplicate_groups = self._group_truly_identical_protocols(
                    duplicate_protocols
                )

                for duplicate_group in truly_duplicate_groups:
                    if len(duplicate_group) > 1:
                        # Keep the first one, mark others as duplicates
                        primary = duplicate_group[0]

                        for duplicate in duplicate_group[1:]:
                            # Only flag if protocols have same name AND same signatures
                            if (
                                duplicate.name == primary.name
                                and self._are_protocols_truly_identical(
                                    duplicate, primary
                                )
                            ):
                                violation = ProtocolViolation(
                                    file_path=duplicate.file_path,
                                    line_number=duplicate.line_number,
                                    column_offset=0,
                                    rule_id="SPI010",
                                    violation_type="Exact Duplicate Protocol",
                                    message=f"Protocol '{duplicate.name}' is identical to '{primary.name}' in {primary.file_path}",
                                    severity="error",
                                    suggestion=f"Remove duplicate or merge with {primary.file_path}:{primary.line_number}",
                                    tags=["duplicate", "exact", "signature"],
                                    performance_impact="medium",
                                )
                                violations.append(violation)

        return violations

    def _group_truly_identical_protocols(
        self, protocols: List[ProtocolInfo]
    ) -> List[List[ProtocolInfo]]:
        """Group protocols that are truly identical, not just hash collisions."""
        groups = []
        processed = set()

        for i, protocol in enumerate(protocols):
            if i in processed:
                continue

            group = [protocol]
            processed.add(i)

            for j, other_protocol in enumerate(protocols[i + 1 :], i + 1):
                if j in processed:
                    continue

                if self._are_protocols_truly_identical(protocol, other_protocol):
                    group.append(other_protocol)
                    processed.add(j)

            if len(group) > 1:  # Only add groups with actual duplicates
                groups.append(group)

        return groups

    def _are_protocols_truly_identical(
        self, protocol1: ProtocolInfo, protocol2: ProtocolInfo
    ) -> bool:
        """Check if two protocols are truly identical."""
        # Must have same name
        if protocol1.name != protocol2.name:
            return False

        # Must have identical method signatures
        if set(protocol1.methods) != set(protocol2.methods):
            return False

        # Must have identical properties
        if set(protocol1.properties) != set(protocol2.properties):
            return False

        # Must have same async method patterns
        if set(protocol1.async_methods) != set(protocol2.async_methods):
            return False

        return True

    def _find_name_conflicts(
        self, by_name: Dict[str, List[ProtocolInfo]]
    ) -> List[ProtocolViolation]:
        """Find protocols with same name but different signatures."""
        violations = []

        for name, conflicting_protocols in by_name.items():
            if len(conflicting_protocols) > 1:
                unique_signatures = set(p.signature_hash for p in conflicting_protocols)

                if len(unique_signatures) > 1:  # Different signatures
                    primary = conflicting_protocols[0]

                    for conflict in conflicting_protocols[1:]:
                        violation = ProtocolViolation(
                            file_path=conflict.file_path,
                            line_number=conflict.line_number,
                            column_offset=0,
                            rule_id="SPI011",
                            violation_type="Protocol Name Conflict",
                            message=f"Protocol '{conflict.name}' conflicts with different protocol in {primary.file_path}",
                            severity="error",
                            suggestion=f"Rename to 'Protocol{conflict.domain.title()}{name[8:]}' or merge interfaces",
                            tags=["conflict", "naming", "signature"],
                            performance_impact="low",
                        )
                        violations.append(violation)

        return violations

    def _find_semantic_duplicates(
        self, by_semantic: Dict[str, List[ProtocolInfo]]
    ) -> List[ProtocolViolation]:
        """Find protocols that are semantically similar but not identical."""
        violations = []

        # Get exclusions from rule configuration
        exclusions = self._get_rule_exclusions("SPI010")

        for semantic_key, similar_protocols in by_semantic.items():
            if len(similar_protocols) > 1:
                # Check if they're actually different enough to warrant separation
                similarity_score = self._calculate_similarity_score(similar_protocols)

                if similarity_score > 0.8:  # Very similar
                    primary = similar_protocols[0]

                    for similar in similar_protocols[1:]:
                        # Check if this pair matches any exclusion pattern
                        if self._matches_exclusion_pattern(
                            primary.name, similar.name, exclusions
                        ):
                            continue  # Skip this violation - it's excluded

                        violation = ProtocolViolation(
                            file_path=similar.file_path,
                            line_number=similar.line_number,
                            column_offset=0,
                            rule_id="SPI010",
                            violation_type="Semantic Duplicate Protocol",
                            message=f"Protocol '{similar.name}' is very similar to '{primary.name}' (similarity: {similarity_score:.1%})",
                            severity="warning",
                            suggestion="Consider merging similar protocols or making differences more explicit",
                            tags=["duplicate", "semantic", "similarity"],
                            performance_impact="low",
                        )
                        violations.append(violation)

        return violations

    def _get_semantic_key(self, protocol: ProtocolInfo) -> str:
        """Generate semantic similarity key for protocol."""
        # Extract semantic components
        domain_key = protocol.domain
        method_patterns = []

        for method in protocol.methods:
            # Extract method name without parameters for pattern matching
            method_name = method.split("(")[0].strip()
            method_patterns.append(method_name.lower())

        # Create semantic signature
        method_patterns.sort()
        return f"{domain_key}:{':'.join(method_patterns[:5])}"  # First 5 methods

    def _calculate_similarity_score(self, protocols: List[ProtocolInfo]) -> float:
        """Calculate semantic similarity score between protocols."""
        if len(protocols) < 2:
            return 0.0

        # Compare method signatures
        all_methods = set()
        for protocol in protocols:
            all_methods.update(protocol.methods)

        # Calculate Jaccard similarity
        similarities = []
        for i in range(len(protocols)):
            for j in range(i + 1, len(protocols)):
                methods_i = set(protocols[i].methods)
                methods_j = set(protocols[j].methods)

                intersection = len(methods_i.intersection(methods_j))
                union = len(methods_i.union(methods_j))

                similarity = intersection / union if union > 0 else 0
                similarities.append(similarity)

        return sum(similarities) / len(similarities) if similarities else 0.0

    def _get_rule_exclusions(self, rule_id: str) -> List[Dict[str, Any]]:
        """Get exclusion patterns from rule configuration."""
        if rule_id not in self.config.rules:
            return []

        rule = self.config.rules[rule_id]
        config_data = rule.configuration if hasattr(rule, "configuration") else {}

        return config_data.get("exclusions", [])

    def _matches_exclusion_pattern(
        self, protocol1_name: str, protocol2_name: str, exclusions: List[Dict[str, Any]]
    ) -> bool:
        """Check if protocol pair matches any exclusion pattern."""
        import re

        for exclusion in exclusions:
            pattern = exclusion.get("pattern", "")
            if not pattern:
                continue

            # Try matching both orderings
            comparison1 = f"{protocol1_name} vs {protocol2_name}"
            comparison2 = f"{protocol2_name} vs {protocol1_name}"

            try:
                if re.match(pattern, comparison1) or re.match(pattern, comparison2):
                    return True
            except re.error:
                # Invalid regex pattern, skip
                continue

        return False


# ============================================================================
# Auto-Fix Engine
# ============================================================================


class AutoFixEngine:
    """Intelligent auto-fix engine for supported SPI violations."""

    def __init__(self, config: ValidationConfig):
        self.config = config
        self.fixes_applied = 0

    def apply_auto_fixes(
        self, violations: List[ProtocolViolation]
    ) -> Tuple[List[ProtocolViolation], int]:
        """Apply automatic fixes to supported violations."""
        fixed_violations = []
        fixes_applied = 0

        # Group violations by file for efficient processing
        violations_by_file = defaultdict(list)
        for violation in violations:
            if violation.auto_fix_available:
                violations_by_file[violation.file_path].append(violation)
            else:
                fixed_violations.append(violation)

        # Apply fixes file by file
        for file_path, file_violations in violations_by_file.items():
            try:
                file_fixes_applied = self._apply_file_fixes(file_path, file_violations)
                fixes_applied += file_fixes_applied

                # Remove fixed violations
                if file_fixes_applied > 0:
                    # Only keep violations that weren't fixed
                    remaining_violations = file_violations[file_fixes_applied:]
                    fixed_violations.extend(remaining_violations)
                else:
                    fixed_violations.extend(file_violations)

            except Exception as e:
                print(f"Warning: Failed to apply auto-fixes to {file_path}: {e}")
                fixed_violations.extend(file_violations)

        self.fixes_applied = fixes_applied
        return fixed_violations, fixes_applied

    def _apply_file_fixes(
        self, file_path: str, violations: List[ProtocolViolation]
    ) -> int:
        """Apply fixes to a specific file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            original_content = content
            fixes_applied = 0

            # Sort violations by line number (descending) to avoid line number shifts
            sorted_violations = sorted(
                violations, key=lambda v: v.line_number, reverse=True
            )

            for violation in sorted_violations:
                if violation.rule_id == "SPI003":  # Missing @runtime_checkable
                    content, fixed = self._fix_missing_runtime_checkable(
                        content, violation
                    )
                elif violation.rule_id == "SPI004":  # Concrete implementation
                    content, fixed = self._fix_concrete_implementation(
                        content, violation
                    )
                elif violation.rule_id == "SPI005":  # Sync to async
                    content, fixed = self._fix_sync_to_async(content, violation)
                else:
                    fixed = False

                if fixed:
                    fixes_applied += 1

            # Write back only if changes were made
            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

            return fixes_applied

        except Exception as e:
            print(f"Error applying fixes to {file_path}: {e}")
            return 0

    def _fix_missing_runtime_checkable(
        self, content: str, violation: ProtocolViolation
    ) -> Tuple[str, bool]:
        """Fix missing @runtime_checkable decorator."""
        lines = content.split("\n")
        target_line = violation.line_number - 1  # Convert to 0-based

        if target_line < len(lines):
            line = lines[target_line]
            if "class " in line and "Protocol" in line:
                # Find the indentation
                indent = len(line) - len(line.lstrip())
                decorator_line = " " * indent + "@runtime_checkable"

                # Insert decorator before class definition
                lines.insert(target_line, decorator_line)
                return "\n".join(lines), True

        return content, False

    def _fix_concrete_implementation(
        self, content: str, violation: ProtocolViolation
    ) -> Tuple[str, bool]:
        """Fix concrete method implementation to use ellipsis."""
        lines = content.split("\n")
        target_line = violation.line_number - 1

        if target_line < len(lines):
            # Find method definition and its body
            method_start = target_line

            # Find the method body
            indent_level = None
            body_start = method_start + 1

            # Skip docstring if present
            if body_start < len(lines):
                line = lines[body_start].strip()
                if line.startswith('"""') or line.startswith("'''"):
                    # Skip to end of docstring
                    quote = line[:3]
                    if not line.endswith(quote) or len(line) <= 3:
                        body_start += 1
                        while body_start < len(lines) and not lines[
                            body_start
                        ].strip().endswith(quote):
                            body_start += 1
                        body_start += 1

            # Replace method body with ellipsis
            if body_start < len(lines):
                body_indent = (
                    len(lines[method_start]) - len(lines[method_start].lstrip()) + 4
                )
                ellipsis_line = " " * body_indent + "..."

                # Find end of method (next method or class end)
                body_end = body_start
                while body_end < len(lines) and (
                    not lines[body_end].strip()
                    or len(lines[body_end]) - len(lines[body_end].lstrip())
                    > body_indent
                    or lines[body_end].strip().startswith("#")
                ):
                    body_end += 1

                # Replace body with ellipsis
                lines[body_start:body_end] = [ellipsis_line]

                return "\n".join(lines), True

        return content, False

    def _fix_sync_to_async(
        self, content: str, violation: ProtocolViolation
    ) -> Tuple[str, bool]:
        """Fix synchronous method to async."""
        lines = content.split("\n")
        target_line = violation.line_number - 1

        if target_line < len(lines):
            line = lines[target_line]
            if "def " in line and "async def " not in line:
                # Replace 'def ' with 'async def '
                lines[target_line] = line.replace("def ", "async def ")
                return "\n".join(lines), True

        return content, False


# ============================================================================
# Report Generation
# ============================================================================


class ReportGenerator:
    """Advanced report generation with multiple output formats."""

    def __init__(self, config: ValidationConfig):
        self.config = config

    def generate_console_report(self, report: ValidationReport) -> None:
        """Generate detailed console report."""
        print("\n" + "=" * 90)
        print("🔍 COMPREHENSIVE SPI PROTOCOL VALIDATION REPORT")
        print("=" * 90)

        # Executive summary
        self._print_executive_summary(report)

        # Violations by category
        if report.violations:
            self._print_violations_by_category(report)

        # Protocol statistics
        self._print_protocol_statistics(report)

        # Performance metrics
        self._print_performance_metrics(report)

        # Recommendations
        if report.recommendations:
            self._print_recommendations(report)

        # Final status
        self._print_final_status(report)

    def generate_json_report(
        self, report: ValidationReport, output_file: str = None
    ) -> None:
        """Generate JSON report for CI/CD integration."""
        # Generate timestamped filename if not provided
        if output_file is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S", time.gmtime())
            output_file = f"comprehensive_spi_validation_{timestamp}.json"

        json_data = report.to_dict()

        # Add metadata
        json_data["metadata"] = {
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "validator_version": "2.0.0",
            "config_rules": len(self.config.rules),
            "format_version": "1.0",
        }

        with open(output_file, "w") as f:
            json.dump(json_data, f, indent=2, default=str)

        print(f"📊 JSON report saved to: {output_file}")

    def generate_html_report(
        self, report: ValidationReport, output_file: str = "spi_validation_report.html"
    ) -> None:
        """Generate HTML report with interactive features."""
        html_content = self._generate_html_content(report)

        with open(output_file, "w") as f:
            f.write(html_content)

        print(f"🌐 HTML report saved to: {output_file}")

    def _print_executive_summary(self, report: ValidationReport) -> None:
        """Print executive summary."""
        print("\n📊 EXECUTIVE SUMMARY:")
        print(f"   Files analyzed: {report.total_files}")
        print(f"   Protocols found: {report.total_protocols}")
        print(f"   Total violations: {len(report.violations)}")
        print(f"   ❌ Errors: {report.error_count}")
        print(f"   ⚠️  Warnings: {report.warning_count}")
        print(f"   ℹ️  Info: {report.info_count}")
        print(f"   🔧 Auto-fixes applied: {report.auto_fixes_applied}")
        print(f"   ⏱️  Execution time: {report.execution_time:.2f}s")

    def _print_violations_by_category(self, report: ValidationReport) -> None:
        """Print violations grouped by category."""
        print("\n🚨 VIOLATIONS BY CATEGORY:")

        # Group violations by rule category and severity
        by_category = defaultdict(lambda: defaultdict(list))

        for violation in report.violations:
            rule = self.config.get_rule(violation.rule_id)
            category = rule.category if rule else "unknown"
            by_category[category][violation.severity].append(violation)

        for category, severity_groups in sorted(by_category.items()):
            total_in_category = sum(
                len(violations) for violations in severity_groups.values()
            )
            print(
                f"\n   📁 {category.title().replace('_', ' ')} ({total_in_category} violations)"
            )

            for severity in ["error", "warning", "info"]:
                violations = severity_groups.get(severity, [])
                if violations:
                    icon = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}[severity]
                    print(
                        f"      {icon} {severity.title()}: {len(violations)} violations"
                    )

                    # Show top 3 violations in this category
                    for violation in violations[:3]:
                        print(
                            f"         • {Path(violation.file_path).name}:{violation.line_number} - {violation.message}"
                        )

                    if len(violations) > 3:
                        print(f"         ... and {len(violations) - 3} more")

    def _print_protocol_statistics(self, report: ValidationReport) -> None:
        """Print protocol analysis statistics."""
        if not report.protocols:
            return

        print("\n📈 PROTOCOL STATISTICS:")

        # Basic statistics
        runtime_checkable = sum(1 for p in report.protocols if p.is_runtime_checkable)
        with_init = sum(1 for p in report.protocols if p.has_init)
        with_async = sum(1 for p in report.protocols if p.async_methods)

        print(
            f"   @runtime_checkable: {runtime_checkable}/{len(report.protocols)} ({runtime_checkable/len(report.protocols)*100:.1f}%)"
        )
        print(f"   With __init__ methods: {with_init} (should be 0)")
        print(f"   With async methods: {with_async}")

        # Domain distribution
        domain_counts = defaultdict(int)
        for protocol in report.protocols:
            domain_counts[protocol.domain] += 1

        print("\n   📁 Domain Distribution:")
        for domain, count in sorted(
            domain_counts.items(), key=lambda x: x[1], reverse=True
        ):
            percentage = count / len(report.protocols) * 100
            print(f"      {domain}: {count} protocols ({percentage:.1f}%)")

        # Complexity analysis
        complexities = [p.complexity_score for p in report.protocols]
        if complexities:
            avg_complexity = sum(complexities) / len(complexities)
            max_complexity = max(complexities)
            print("\n   🧮 Complexity Analysis:")
            print(f"      Average complexity: {avg_complexity:.1f}")
            print(f"      Maximum complexity: {max_complexity}")

            # Find most complex protocols
            complex_protocols = sorted(
                report.protocols, key=lambda p: p.complexity_score, reverse=True
            )[:3]

            print("      Most complex protocols:")
            for protocol in complex_protocols:
                print(
                    f"         • {protocol.name} (score: {protocol.complexity_score})"
                )

    def _print_performance_metrics(self, report: ValidationReport) -> None:
        """Print performance analysis metrics."""
        if not report.performance_metrics:
            return

        print("\n⚡ PERFORMANCE METRICS:")

        for metric, value in report.performance_metrics.items():
            if isinstance(value, float):
                print(f"   {metric.replace('_', ' ').title()}: {value:.2f}")
            else:
                print(f"   {metric.replace('_', ' ').title()}: {value}")

    def _print_recommendations(self, report: ValidationReport) -> None:
        """Print actionable recommendations."""
        print("\n💡 RECOMMENDATIONS:")

        for i, recommendation in enumerate(report.recommendations, 1):
            print(f"   {i}. {recommendation}")

    def _print_final_status(self, report: ValidationReport) -> None:
        """Print final validation status."""
        print("\n" + "=" * 90)

        if report.error_count == 0:
            print("✅ VALIDATION PASSED")
            if report.warning_count > 0:
                print(
                    f"   ⚠️  {report.warning_count} warnings should be addressed for optimal code quality"
                )
            if report.info_count > 0:
                print(
                    f"   ℹ️  {report.info_count} informational items for continuous improvement"
                )
        else:
            print("❌ VALIDATION FAILED")
            print(f"   {report.error_count} errors must be fixed before merging")
            if report.auto_fixes_applied > 0:
                print(
                    f"   🔧 {report.auto_fixes_applied} issues were automatically fixed"
                )

        print(f"   📊 Code quality score: {self._calculate_quality_score(report):.1%}")

    def _calculate_quality_score(self, report: ValidationReport) -> float:
        """Calculate overall code quality score."""
        if report.total_protocols == 0:
            return 1.0

        # Base score
        base_score = 1.0

        # Deduct for violations
        error_penalty = min(0.5, report.error_count * 0.05)
        warning_penalty = min(0.3, report.warning_count * 0.02)

        # Bonus for good practices
        runtime_checkable_bonus = 0
        if report.protocols:
            checkable_ratio = sum(
                1 for p in report.protocols if p.is_runtime_checkable
            ) / len(report.protocols)
            runtime_checkable_bonus = checkable_ratio * 0.1

        return max(
            0.0, base_score - error_penalty - warning_penalty + runtime_checkable_bonus
        )

    def _generate_html_content(self, report: ValidationReport) -> str:
        """Generate HTML report content."""
        # This would generate a full HTML report with CSS and JavaScript
        # For brevity, returning a simple HTML template
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>SPI Validation Report</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f8f9fa; padding: 20px; border-radius: 5px; }}
        .summary {{ display: flex; justify-content: space-around; margin: 20px 0; }}
        .metric {{ text-align: center; padding: 10px; }}
        .violations {{ margin: 20px 0; }}
        .violation {{ margin: 10px 0; padding: 10px; border-left: 4px solid #dc3545; background: #f8f9fa; }}
        .error {{ border-color: #dc3545; }}
        .warning {{ border-color: #ffc107; }}
        .info {{ border-color: #17a2b8; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>SPI Protocol Validation Report</h1>
        <p>Generated: {time.strftime("%Y-%m-%d %H:%M:%S")}</p>
    </div>

    <div class="summary">
        <div class="metric">
            <h3>{report.total_files}</h3>
            <p>Files Analyzed</p>
        </div>
        <div class="metric">
            <h3>{report.total_protocols}</h3>
            <p>Protocols Found</p>
        </div>
        <div class="metric">
            <h3>{report.error_count}</h3>
            <p>Errors</p>
        </div>
        <div class="metric">
            <h3>{report.warning_count}</h3>
            <p>Warnings</p>
        </div>
    </div>

    <div class="violations">
        <h2>Violations</h2>
        {"".join(f'<div class="violation {v.severity}"><strong>{v.rule_id}: {v.violation_type}</strong><br>{v.file_path}:{v.line_number}<br>{v.message}</div>' for v in report.violations[:50])}
    </div>
</body>
</html>"""


# ============================================================================
# Main Validation Engine
# ============================================================================


class ComprehensiveSPIValidationEngine:
    """Main validation engine orchestrating all validation components."""

    def __init__(self, config: ValidationConfig):
        self.config = config
        self.duplicate_analyzer = DuplicateProtocolAnalyzer(config)
        self.auto_fix_engine = AutoFixEngine(config)
        self.report_generator = ReportGenerator(config)

    def validate_directory(
        self,
        directory: Path,
        apply_fixes: bool = False,
        generate_json: bool = False,
        generate_html: bool = False,
    ) -> ValidationReport:
        """Validate all protocol files in directory."""
        start_time = time.time()

        # Discover files to validate
        python_files = self._discover_protocol_files(directory)

        if not python_files:
            print("✅ No protocol files found to validate")
            return ValidationReport()

        print(f"🔍 Found {len(python_files)} protocol files to validate")

        # Initialize report
        report = ValidationReport()
        report.total_files = len(python_files)

        # Validate each file
        all_violations = []
        all_protocols = []

        with timeout_context(
            "validation", self.config.global_settings.get("timeout_seconds", 300)
        ):
            for py_file in python_files:
                print(f"   📄 Validating {py_file.name}...")

                violations, protocols = self._validate_file(py_file)
                all_violations.extend(violations)
                all_protocols.extend(protocols)

        # Analyze duplicates across all protocols
        duplicate_violations = self.duplicate_analyzer.analyze_duplicates(all_protocols)
        all_violations.extend(duplicate_violations)

        # Apply auto-fixes if requested
        if apply_fixes:
            print("🔧 Applying automatic fixes...")
            all_violations, fixes_applied = self.auto_fix_engine.apply_auto_fixes(
                all_violations
            )
            report.auto_fixes_applied = fixes_applied

        # Populate report
        report.violations = all_violations
        report.protocols = all_protocols
        report.total_protocols = len(all_protocols)
        report.execution_time = time.time() - start_time
        report.validation_rules_applied = len(self.config.get_enabled_rules())

        # Generate performance metrics
        report.performance_metrics = self._generate_performance_metrics(report)

        # Generate recommendations
        report.recommendations = self._generate_recommendations(report)

        # Generate reports
        self.report_generator.generate_console_report(report)

        if generate_json:
            self.report_generator.generate_json_report(report)

        if generate_html:
            self.report_generator.generate_html_report(report)

        return report

    def validate_single_file(self, file_path: Path) -> ValidationReport:
        """Validate a single protocol file."""
        start_time = time.time()

        print(f"🔍 Validating single file: {file_path}")

        violations, protocols = self._validate_file(file_path)

        # Create report
        report = ValidationReport()
        report.total_files = 1
        report.violations = violations
        report.protocols = protocols
        report.total_protocols = len(protocols)
        report.execution_time = time.time() - start_time
        report.validation_rules_applied = len(self.config.get_enabled_rules())

        # Generate recommendations
        report.recommendations = self._generate_recommendations(report)

        # Generate console report
        self.report_generator.generate_console_report(report)

        return report

    def _discover_protocol_files(self, directory: Path) -> List[Path]:
        """Discover Python protocol files to validate."""
        protocol_files = []

        try:
            for py_file in directory.rglob("*.py"):
                # Skip excluded files
                if (
                    py_file.name.startswith("test_")
                    or py_file.name.startswith("__")
                    or "__pycache__" in str(py_file)
                    or "/.git/" in str(py_file)
                ):
                    continue

                # Check if file contains protocol definitions
                try:
                    with open(py_file, "r", encoding="utf-8") as f:
                        content = f.read(2048)  # Read first 2KB

                    if self._looks_like_protocol_file(content):
                        protocol_files.append(py_file)

                except Exception:
                    continue  # Skip files that can't be read

        except Exception as e:
            print(f"❌ Error discovering files in {directory}: {e}")

        return sorted(protocol_files)

    def _looks_like_protocol_file(self, content: str) -> bool:
        """Quick check if file likely contains protocol definitions."""
        indicators = [
            "Protocol",
            "@runtime_checkable",
            "class Protocol",
            "from typing import Protocol",
        ]

        return any(indicator in content for indicator in indicators)

    def _validate_file(
        self, file_path: Path
    ) -> Tuple[List[ProtocolViolation], List[ProtocolInfo]]:
        """Validate a single file comprehensively."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check file size limits
            max_size = self.config.global_settings.get("max_file_size", 1024 * 1024)
            if len(content) > max_size:
                return [
                    ProtocolViolation(
                        file_path=str(file_path),
                        line_number=1,
                        column_offset=0,
                        rule_id="SPI000",
                        violation_type="File Too Large",
                        message=f"File size {len(content)} bytes exceeds limit {max_size} bytes",
                        severity="error",
                    )
                ], []

            # Parse and validate
            tree = ast.parse(content)
            validator = ComprehensiveSPIValidator(str(file_path), self.config)
            validator.visit(tree)

            return validator.violations, validator.protocols

        except SyntaxError as e:
            return [
                ProtocolViolation(
                    file_path=str(file_path),
                    line_number=e.lineno or 1,
                    column_offset=e.offset or 0,
                    rule_id="SPI000",
                    violation_type="Syntax Error",
                    message=f"Python syntax error: {e.msg}",
                    severity="error",
                    suggestion="Fix Python syntax before validation",
                )
            ], []

        except Exception as e:
            return [
                ProtocolViolation(
                    file_path=str(file_path),
                    line_number=1,
                    column_offset=0,
                    rule_id="SPI000",
                    violation_type="Validation Error",
                    message=f"Failed to validate file: {str(e)}",
                    severity="error",
                    suggestion="Check file for parsing issues",
                )
            ], []

    def _generate_performance_metrics(self, report: ValidationReport) -> Dict[str, Any]:
        """Generate performance analysis metrics."""
        metrics = {
            "files_per_second": (
                report.total_files / report.execution_time
                if report.execution_time > 0
                else 0
            ),
            "protocols_per_second": (
                report.total_protocols / report.execution_time
                if report.execution_time > 0
                else 0
            ),
            "average_protocols_per_file": (
                report.total_protocols / report.total_files
                if report.total_files > 0
                else 0
            ),
            "violation_density": (
                len(report.violations) / report.total_files
                if report.total_files > 0
                else 0
            ),
        }

        return metrics

    def _generate_recommendations(self, report: ValidationReport) -> List[str]:
        """Generate actionable recommendations based on validation results."""
        recommendations = []

        # Error-based recommendations
        if report.error_count > 0:
            recommendations.append(
                f"Fix {report.error_count} critical errors before merging code"
            )

        # Protocol-specific recommendations
        if report.protocols:
            non_checkable = sum(
                1 for p in report.protocols if not p.is_runtime_checkable
            )
            if non_checkable > 0:
                recommendations.append(
                    f"Add @runtime_checkable decorator to {non_checkable} protocols"
                )

            with_init = sum(1 for p in report.protocols if p.has_init)
            if with_init > 0:
                recommendations.append(
                    f"Remove __init__ methods from {with_init} protocols - use properties instead"
                )

        # Performance recommendations
        if report.execution_time > 60:
            recommendations.append(
                "Consider splitting large files for better validation performance"
            )

        # Quality recommendations
        if report.warning_count > report.error_count * 2:
            recommendations.append(
                "Address warnings to improve code quality and maintainability"
            )

        return recommendations


# ============================================================================
# Command Line Interface
# ============================================================================


def create_sample_config_file(config_path: str) -> None:
    """Create a sample configuration file."""
    sample_config = {
        "global_settings": {
            "timeout_seconds": 300,
            "max_file_size": 1048576,
            "enable_caching": True,
            "max_violations_per_file": 100,
        },
        "rules": [
            {"rule_id": "SPI001", "enabled": True, "severity": "error"},
            {"rule_id": "SPI002", "enabled": True, "severity": "warning"},
            {"rule_id": "SPI003", "enabled": True, "severity": "error"},
            {"rule_id": "SPI004", "enabled": True, "severity": "error"},
            {"rule_id": "SPI005", "enabled": True, "severity": "warning"},
            {"rule_id": "SPI006", "enabled": True, "severity": "error"},
            {"rule_id": "SPI007", "enabled": True, "severity": "error"},
            {"rule_id": "SPI008", "enabled": True, "severity": "error"},
            {"rule_id": "SPI009", "enabled": True, "severity": "warning"},
            {"rule_id": "SPI010", "enabled": True, "severity": "error"},
            {"rule_id": "SPI011", "enabled": True, "severity": "error"},
            {"rule_id": "SPI012", "enabled": True, "severity": "error"},
            {"rule_id": "SPI013", "enabled": True, "severity": "warning"},
            {"rule_id": "SPI014", "enabled": True, "severity": "warning"},
            {"rule_id": "SPI015", "enabled": True, "severity": "error"},
            {"rule_id": "SPI016", "enabled": True, "severity": "error"},
        ],
    }

    with open(config_path, "w") as f:
        yaml.dump(sample_config, f, default_flow_style=False)

    print(f"📝 Sample configuration created: {config_path}")


def main():
    """Main entry point for comprehensive SPI validation."""
    parser = argparse.ArgumentParser(
        description="Comprehensive SPI Protocol Validation Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s src/                                    # Basic validation
  %(prog)s src/ --config validation.yaml          # Custom configuration
  %(prog)s src/ --fix                             # Apply auto-fixes
  %(prog)s src/ --json-report                     # Generate JSON report
  %(prog)s --create-config validation.yaml        # Create sample config
  %(prog)s --pre-commit                           # Pre-commit mode
        """,
    )

    parser.add_argument(
        "path", nargs="?", default="src/", help="Path to validate (file or directory)"
    )
    parser.add_argument("--config", "-c", help="Configuration file path (YAML format)")
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Apply automatic fixes for supported violations",
    )
    parser.add_argument(
        "--json-report",
        action="store_true",
        help="Generate JSON report for CI/CD integration",
    )
    parser.add_argument(
        "--html-report",
        action="store_true",
        help="Generate HTML report with interactive features",
    )
    parser.add_argument(
        "--create-config", help="Create sample configuration file at specified path"
    )
    parser.add_argument(
        "--pre-commit",
        action="store_true",
        help="Pre-commit integration mode (faster validation)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output with detailed progress",
    )

    args = parser.parse_args()

    try:
        # Handle special commands
        if args.create_config:
            create_sample_config_file(args.create_config)
            return 0

        # Load configuration
        config = ValidationConfig(args.config)

        # Adjust configuration for pre-commit mode
        if args.pre_commit:
            config.global_settings["timeout_seconds"] = 60  # Shorter timeout
            config.global_settings["max_violations_per_file"] = (
                20  # Fewer violations shown
            )

            # Disable some time-intensive checks
            for rule in config.rules.values():
                if rule.category in ["documentation", "performance"]:
                    rule.enabled = False

        # Initialize validation engine
        engine = ComprehensiveSPIValidationEngine(config)

        # Validate path
        target_path = Path(args.path)
        if not target_path.exists():
            print(f"❌ Path does not exist: {target_path}")
            return 1

        if args.verbose:
            print("🔍 Starting comprehensive SPI validation")
            print(f"   Target: {target_path}")
            print(f"   Config: {args.config or 'built-in defaults'}")
            print(f"   Auto-fix: {'enabled' if args.fix else 'disabled'}")
            print(f"   Mode: {'pre-commit' if args.pre_commit else 'standard'}")

        # Run validation
        if target_path.is_file():
            report = engine.validate_single_file(target_path)
        else:
            report = engine.validate_directory(
                target_path,
                apply_fixes=args.fix,
                generate_json=args.json_report,
                generate_html=args.html_report,
            )

        # Return appropriate exit code
        return 1 if report.error_count > 0 else 0

    except timeout_utils.TimeoutError:
        print("❌ Validation timed out")
        return 1
    except KeyboardInterrupt:
        print("\n❌ Validation interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Validation failed with error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
