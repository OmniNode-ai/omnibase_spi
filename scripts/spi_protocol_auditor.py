#!/usr/bin/env python3
"""
SPI Protocol Auditor

Comprehensive validation script for omnibase_spi protocol compliance.
Validates namespace isolation, protocol purity, type safety, timeout parameters,
security enhancements, and architectural compliance across all memory protocols.

Features:
- Enhanced error handling with detailed context
- Path validation and existence checks
- Comprehensive timeout parameter validation
- Security protocol compliance verification
- Performance pattern detection
"""

import argparse
import ast
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


class SPIProtocolAuditor:
    """Main auditor class for SPI protocol validation."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.src_path = repo_root / "src" / "omnibase_spi"
        self.protocols_path = self.src_path / "protocols"
        self.memory_protocols_path = self.protocols_path / "memory"
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
        self.info: List[Dict[str, Any]] = []

        # Validate paths exist
        self._validate_paths()

    def audit_all(self) -> bool:
        """Run all audits and return True if all pass."""
        print("🔍 Starting SPI Protocol Audit...")

        success = True

        # Run all audit checks
        checks = [
            ("namespace_isolation", self.audit_namespace_isolation),
            ("protocol_purity", self.audit_protocol_purity),
            ("type_safety", self.audit_type_safety),
            ("memory_protocols", self.audit_memory_protocols),
            ("timeout_parameters", self.audit_timeout_parameters),
            ("security_enhancements", self.audit_security_enhancements),
            ("documentation", self.audit_documentation),
            ("import_structure", self.audit_import_structure),
        ]

        for check_name, check_func in checks:
            print(f"\n📋 Running {check_name} audit...")
            try:
                if not check_func():
                    success = False
                    print(f"❌ {check_name} audit failed")
                else:
                    print(f"✅ {check_name} audit passed")
            except Exception as e:
                self.add_error(
                    "audit_execution",
                    f"Failed to execute {check_name} audit: {e}",
                    file_path=None,
                    context={"audit_name": check_name, "exception": str(e)},
                )
                success = False
                print(f"💥 {check_name} audit crashed: {e}")

        # Print summary
        self.print_summary()

        return success

    def audit_namespace_isolation(self) -> bool:
        """Audit namespace isolation compliance."""
        success = True

        # Check all Python files in protocols directory
        for py_file in self.protocols_path.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue

            success &= self._check_file_namespace_isolation(py_file)

        return success

    def _check_file_namespace_isolation(self, file_path: Path) -> bool:
        """Check a single file for namespace isolation violations."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            # Check imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if self._is_forbidden_import(alias.name):
                            self.add_error(
                                "namespace_isolation",
                                f"Forbidden import in {file_path}: {alias.name}",
                            )
                            return False

                elif isinstance(node, ast.ImportFrom):
                    if node.module and self._is_forbidden_import(node.module):
                        self.add_error(
                            "namespace_isolation",
                            f"Forbidden import in {file_path}: from {node.module}",
                        )
                        return False

            return True

        except Exception as e:
            self.add_error("namespace_isolation", f"Failed to parse {file_path}: {e}")
            return False

    def _is_forbidden_import(self, module_name: str) -> bool:
        """Check if an import violates namespace isolation."""
        if not module_name.startswith("omnibase_spi"):
            return False  # Standard library imports are allowed

        forbidden_namespaces = [
            "omnibase_spi.model",
            "omnibase_spi.core",
            "omnibase_spi.implementation",
            "omnibase_spi.services",
        ]

        return any(
            module_name.startswith(forbidden) for forbidden in forbidden_namespaces
        )

    def audit_protocol_purity(self) -> bool:
        """Audit protocol purity (no concrete implementations)."""
        success = True

        for py_file in self.protocols_path.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue

            success &= self._check_protocol_purity(py_file)

        return success

    def _check_protocol_purity(self, file_path: Path) -> bool:
        """Check that a file contains only protocol definitions."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            # Only check top-level nodes (module level), not nested nodes
            for node in tree.body:
                # Check for concrete class definitions (not protocols)
                if isinstance(node, ast.ClassDef):
                    # Check if it's a protocol
                    has_protocol_base = any(
                        (isinstance(base, ast.Name) and base.id == "Protocol")
                        or (isinstance(base, ast.Attribute) and base.attr == "Protocol")
                        for base in node.bases
                    )

                    if not has_protocol_base:
                        # Check if it's a literal type or data class
                        decorators = [
                            d.id if isinstance(d, ast.Name) else str(d)
                            for d in node.decorator_list
                        ]
                        if (
                            "dataclass" in decorators
                            or "runtime_checkable" in decorators
                        ):
                            continue  # These are acceptable

                        self.add_error(
                            "protocol_purity",
                            f"Non-protocol class found in {file_path}: {node.name}",
                        )
                        return False

                # Check for function definitions at module level (outside classes)
                elif isinstance(node, ast.FunctionDef):
                    # Module-level functions are not allowed in protocol files
                    self.add_error(
                        "protocol_purity",
                        f"Function definition found outside protocol in {file_path}: {node.name}",
                    )
                    return False

            return True

        except Exception as e:
            self.add_error("protocol_purity", f"Failed to parse {file_path}: {e}")
            return False

    def audit_type_safety(self) -> bool:
        """Audit type safety using mypy."""
        try:
            # Run mypy on the protocols directory using poetry
            result = subprocess.run(
                [
                    "poetry",
                    "run",
                    "mypy",
                    str(self.protocols_path),
                    "--strict",
                    "--no-error-summary",
                ],
                capture_output=True,
                text=True,
                cwd=self.repo_root,
            )

            if result.returncode != 0:
                self.add_error(
                    "type_safety",
                    f"MyPy type checking failed:\n{result.stdout}\n{result.stderr}",
                )
                return False

            return True

        except FileNotFoundError:
            self.add_warning(
                "type_safety", "MyPy not available, skipping type safety check"
            )
            return True
        except Exception as e:
            self.add_error("type_safety", f"Type safety check failed: {e}")
            return False

    def audit_memory_protocols(self) -> bool:
        """Audit memory-specific protocol requirements."""
        success = True

        # Check that all required memory protocols exist
        required_files = [
            "protocol_memory_operations.py",
            "protocol_memory_base.py",
            "protocol_memory_requests.py",
            "protocol_memory_responses.py",
            "protocol_memory_errors.py",
            "protocol_memory_security.py",
            "protocol_memory_streaming.py",
            "protocol_memory_error_handling.py",
        ]

        for required_file in required_files:
            file_path = self.memory_protocols_path / required_file
            if not file_path.exists():
                self.add_error(
                    "memory_protocols", f"Required file missing: {required_file}"
                )
                success = False

        # Check timeout parameters in operations
        success &= self._check_timeout_parameters()

        # Check security enhancements
        success &= self._check_security_enhancements()

        return success

    def _check_timeout_parameters(self) -> bool:
        """Check that critical operations have timeout parameters."""
        operations_file = self.memory_protocols_path / "protocol_memory_operations.py"
        if not operations_file.exists():
            return False

        try:
            with open(operations_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Check for timeout parameters in critical methods
            critical_methods = [
                "batch_store_memories",
                "batch_retrieve_memories",
                "optimize_storage",
                "execute_workflow",
                "analyze_patterns",
                "consolidate_memories",
            ]

            for method in critical_methods:
                if method in content and "timeout_seconds" not in content:
                    self.add_error(
                        "memory_protocols",
                        f"Method {method} missing timeout_seconds parameter",
                    )
                    return False

            return True

        except Exception as e:
            self.add_error(
                "memory_protocols", f"Failed to check timeout parameters: {e}"
            )
            return False

    def _check_security_enhancements(self) -> bool:
        """Check that security enhancements are properly implemented."""
        security_file = self.memory_protocols_path / "protocol_memory_security.py"
        if not security_file.exists():
            self.add_error("memory_protocols", "Security protocols file missing")
            return False

        try:
            with open(security_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Check for required security protocols
            required_protocols = [
                "ProtocolSecurityContext",
                "ProtocolAuditTrail",
                "ProtocolRateLimitConfig",
                "ProtocolMemorySecurityNode",
            ]

            for protocol in required_protocols:
                if protocol not in content:
                    self.add_error(
                        "memory_protocols",
                        f"Required security protocol missing: {protocol}",
                    )
                    return False

            return True

        except Exception as e:
            self.add_error(
                "memory_protocols", f"Failed to check security enhancements: {e}"
            )
            return False

    def audit_documentation(self) -> bool:
        """Audit documentation completeness."""
        success = True

        # Check that all protocol files have proper docstrings
        for py_file in self.memory_protocols_path.glob("protocol_*.py"):
            success &= self._check_file_documentation(py_file)

        return success

    def _check_file_documentation(self, file_path: Path) -> bool:
        """Check documentation quality for a single file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            # Check module docstring
            if not ast.get_docstring(tree):
                self.add_warning(
                    "documentation", f"Module {file_path.name} missing docstring"
                )

            # Check protocol docstrings
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name.startswith("Protocol"):
                    if not ast.get_docstring(node):
                        self.add_warning(
                            "documentation",
                            f"Protocol {node.name} in {file_path.name} missing docstring",
                        )

                    # Check method docstrings
                    for item in node.body:
                        if isinstance(item, ast.AsyncFunctionDef):
                            if not ast.get_docstring(item):
                                self.add_warning(
                                    "documentation",
                                    f"Method {item.name} in {node.name} missing docstring",
                                )

            return True

        except Exception as e:
            self.add_error(
                "documentation", f"Failed to check documentation for {file_path}: {e}"
            )
            return False

    def audit_import_structure(self) -> bool:
        """Audit import structure and __all__ completeness."""
        init_file = self.memory_protocols_path / "__init__.py"
        if not init_file.exists():
            self.add_error("import_structure", "Memory protocols __init__.py missing")
            return False

        try:
            with open(init_file, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            # Extract __all__ contents
            all_exports = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == "__all__":
                            if isinstance(node.value, ast.List):
                                for elt in node.value.elts:
                                    if isinstance(elt, ast.Constant):
                                        all_exports.add(elt.value)

            # Check that all new protocols are exported
            required_exports = {
                "ProtocolSecurityContext",
                "ProtocolMemorySecurityNode",
                "ProtocolStreamingMemoryNode",
                "ProtocolMemoryErrorHandler",
                "ProtocolMemoryCache",
            }

            missing_exports = required_exports - all_exports
            if missing_exports:
                self.add_error(
                    "import_structure", f"Missing exports in __all__: {missing_exports}"
                )
                return False

            return True

        except Exception as e:
            self.add_error("import_structure", f"Failed to check import structure: {e}")
            return False

    def add_error(
        self,
        category: str,
        message: str,
        file_path: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add an error to the audit results."""
        error = {
            "category": category,
            "message": message,
            "file_path": file_path,
            "context": context or {},
        }
        self.errors.append(error)

    def add_warning(
        self,
        category: str,
        message: str,
        file_path: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a warning to the audit results."""
        warning = {
            "category": category,
            "message": message,
            "file_path": file_path,
            "context": context or {},
        }
        self.warnings.append(warning)

    def print_summary(self) -> None:
        """Print audit summary."""
        print(f"\n{'='*60}")
        print("📊 SPI Protocol Audit Summary")
        print(f"{'='*60}")

        if not self.errors and not self.warnings:
            print("✅ All audits passed! No issues found.")
            return

        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. [{error['category']}] {error['message']}")

        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. [{warning['category']}] {warning['message']}")

        print(f"\n📈 Summary: {len(self.errors)} errors, {len(self.warnings)} warnings")

    def _validate_paths(self) -> None:
        """Validate that required paths exist."""
        required_paths = [
            self.src_path,
            self.protocols_path,
            self.memory_protocols_path,
        ]

        for path in required_paths:
            if not path.exists():
                self.add_error(
                    "path_validation",
                    f"Required path does not exist: {path}",
                    file_path=None,
                    context={"missing_path": str(path)},
                )
                raise FileNotFoundError(f"Required path missing: {path}")

    def audit_timeout_parameters(self) -> bool:
        """Audit timeout parameter coverage in memory protocols."""
        success = True

        # Critical methods that must have timeout parameters
        required_timeout_methods = {
            "ProtocolMemoryEffectNode": [
                "batch_store_memories",
                "batch_retrieve_memories",
            ],
            "ProtocolMemoryComputeNode": [
                "generate_embedding",
                "extract_insights",
                "compare_semantics",
            ],
            "ProtocolMemoryReducerNode": [
                "deduplicate_memories",
                "aggregate_data",
                "compress_memories",
                "optimize_storage",
            ],
            "ProtocolMemoryOrchestratorNode": [
                "coordinate_agents",
                "broadcast_update",
                "synchronize_state",
                "manage_lifecycle",
                "execute_workflow",
            ],
        }

        # Check memory operations file
        operations_file = self.memory_protocols_path / "protocol_memory_operations.py"
        if not operations_file.exists():
            self.add_error(
                "timeout_parameters",
                f"Memory operations file not found: {operations_file}",
                file_path=str(operations_file),
            )
            return False

        try:
            with open(operations_file, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            # Find all protocol classes and their methods
            for node in ast.walk(tree):
                if (
                    isinstance(node, ast.ClassDef)
                    and node.name in required_timeout_methods
                ):
                    class_methods = required_timeout_methods[node.name]

                    for method_node in node.body:
                        if isinstance(method_node, ast.AsyncFunctionDef):
                            method_name = method_node.name

                            if method_name in class_methods:
                                # Check if method has timeout_seconds parameter
                                has_timeout = any(
                                    arg.arg == "timeout_seconds"
                                    for arg in method_node.args.args
                                )

                                if not has_timeout:
                                    self.add_error(
                                        "timeout_parameters",
                                        f"Method {node.name}.{method_name} missing timeout_seconds parameter",
                                        file_path=str(operations_file),
                                        context={
                                            "class": node.name,
                                            "method": method_name,
                                            "line": method_node.lineno,
                                        },
                                    )
                                    success = False
                                else:
                                    self.info.append(
                                        {
                                            "category": "timeout_parameters",
                                            "message": f"✅ {node.name}.{method_name} has timeout parameter",
                                            "context": {
                                                "class": node.name,
                                                "method": method_name,
                                            },
                                        }
                                    )

            return success

        except Exception as e:
            self.add_error(
                "timeout_parameters",
                f"Failed to analyze timeout parameters: {e}",
                file_path=str(operations_file),
                context={"exception": str(e)},
            )
            return False

    def audit_security_enhancements(self) -> bool:
        """Audit security enhancement compliance."""
        success = True

        # Check security protocol file exists and has required protocols
        security_file = self.memory_protocols_path / "protocol_memory_security.py"
        if not security_file.exists():
            self.add_error(
                "security_enhancements",
                f"Security protocol file not found: {security_file}",
                file_path=str(security_file),
            )
            return False

        required_security_protocols = [
            "ProtocolSecurityContext",
            "ProtocolAuditTrail",
            "ProtocolRateLimitConfig",
            "ProtocolInputValidation",
            "ProtocolMemorySecurityNode",
            "ProtocolMemoryComplianceNode",
        ]

        try:
            with open(security_file, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)
            found_protocols = set()

            # Find all protocol class definitions
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    found_protocols.add(node.name)

            # Check for missing security protocols
            missing_protocols = set(required_security_protocols) - found_protocols
            if missing_protocols:
                for protocol in missing_protocols:
                    self.add_error(
                        "security_enhancements",
                        f"Missing required security protocol: {protocol}",
                        file_path=str(security_file),
                        context={"missing_protocol": protocol},
                    )
                    success = False

            # Check that security_context parameters are used in operations
            operations_file = (
                self.memory_protocols_path / "protocol_memory_operations.py"
            )
            if operations_file.exists():
                with open(operations_file, "r", encoding="utf-8") as f:
                    ops_content = f.read()

                security_context_usage = ops_content.count("security_context")
                if security_context_usage < 10:  # Should be used in many methods
                    self.add_warning(
                        "security_enhancements",
                        f"Low security_context parameter usage: {security_context_usage} occurrences",
                        file_path=str(operations_file),
                        context={"usage_count": security_context_usage},
                    )

            return success

        except Exception as e:
            self.add_error(
                "security_enhancements",
                f"Failed to analyze security enhancements: {e}",
                file_path=str(security_file),
                context={"exception": str(e)},
            )
            return False

    def export_results(self, output_file: Path) -> None:
        """Export audit results to JSON."""
        results = {
            "success": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "summary": {
                "error_count": len(self.errors),
                "warning_count": len(self.warnings),
            },
        }

        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)

        print(f"📄 Results exported to {output_file}")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="SPI Protocol Auditor")
    parser.add_argument(
        "--repo-root", type=Path, default=Path.cwd(), help="Repository root directory"
    )
    parser.add_argument("--output", type=Path, help="Output file for JSON results")
    parser.add_argument(
        "--fail-on-warnings", action="store_true", help="Treat warnings as failures"
    )

    args = parser.parse_args()

    auditor = SPIProtocolAuditor(args.repo_root)
    success = auditor.audit_all()

    if args.output:
        auditor.export_results(args.output)

    # Exit with appropriate code
    if not success:
        sys.exit(1)
    elif args.fail_on_warnings and auditor.warnings:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
