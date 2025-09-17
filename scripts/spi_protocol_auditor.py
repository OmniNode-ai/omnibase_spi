#!/usr/bin/env python3
"""
SPI Protocol Auditor

Comprehensive validation script for omnibase_spi protocol compliance.
Validates namespace isolation, protocol purity, type safety, and
architectural compliance across all memory protocols.
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
                self.add_error(check_name, f"Audit check failed: {e}")
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

    def add_error(self, category: str, message: str) -> None:
        """Add an error to the audit results."""
        self.errors.append({"category": category, "message": message})

    def add_warning(self, category: str, message: str) -> None:
        """Add a warning to the audit results."""
        self.warnings.append({"category": category, "message": message})

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
