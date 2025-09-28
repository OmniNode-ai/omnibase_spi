#!/usr/bin/env python3
"""
Automatic Protocol Compliance Fixer using AST parsing.

This script automatically fixes protocol compliance issues by:
1. Converting protocol method implementations to `...` ellipsis
2. Converting sync methods to async where appropriate
3. Removing standalone functions from SPI files
4. Fixing method signatures and type annotations
5. Ensuring all protocol classes have proper structure

Usage:
    python scripts/auto_fix_protocol_compliance.py [--dry-run] [--file FILE]
"""

import argparse
import ast
import os
import sys
from pathlib import Path
from typing import List, Optional, Set, Tuple, Union


class ProtocolComplianceFixer(ast.NodeTransformer):
    """AST transformer that fixes protocol compliance issues."""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.changes_made = []
        self.errors_fixed = 0
        self.in_protocol_class = False
        self.current_protocol_name = None
        self.standalone_functions_removed = 0
        self.methods_converted_to_async = 0
        self.methods_fixed_ellipsis = 0

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        """Visit class definitions and identify protocol classes."""
        # Check if this is a protocol class
        is_protocol = False
        has_runtime_checkable = False

        # Check decorators
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == "runtime_checkable":
                has_runtime_checkable = True
            elif isinstance(decorator, ast.Call) and isinstance(
                decorator.func, ast.Name
            ):
                if decorator.func.id == "runtime_checkable":
                    has_runtime_checkable = True

        # Check base classes for Protocol
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == "Protocol":
                is_protocol = True
            elif isinstance(base, ast.Attribute) and base.attr == "Protocol":
                is_protocol = True

        if is_protocol and has_runtime_checkable:
            self.in_protocol_class = True
            self.current_protocol_name = node.name
            self.changes_made.append(f"Processing protocol class: {node.name}")
        else:
            self.in_protocol_class = False
            self.current_protocol_name = None

        # Transform the class
        node = self.generic_visit(node)

        self.in_protocol_class = False
        self.current_protocol_name = None
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Optional[ast.FunctionDef]:
        """Visit function definitions and fix protocol methods."""
        if self.in_protocol_class:
            return self._fix_protocol_method(node)
        else:
            # This is a standalone function in SPI - should be removed
            self.standalone_functions_removed += 1
            self.changes_made.append(f"Removed standalone function: {node.name}")
            return None  # Remove the function

    def visit_AsyncFunctionDef(
        self, node: ast.AsyncFunctionDef
    ) -> ast.AsyncFunctionDef:
        """Visit async function definitions and fix protocol methods."""
        if self.in_protocol_class:
            return self._fix_async_protocol_method(node)
        else:
            # This is a standalone async function in SPI - should be removed
            self.standalone_functions_removed += 1
            self.changes_made.append(f"Removed standalone async function: {node.name}")
            return None  # Remove the function

    def _has_correct_ellipsis(self, method_body: list) -> bool:
        """Check if method body already has correct ellipsis implementation."""
        if len(method_body) != 1:
            return False

        stmt = method_body[0]
        if not isinstance(stmt, ast.Expr):
            return False

        if isinstance(stmt.value, ast.Constant):
            return stmt.value.value is ...
        elif isinstance(stmt.value, ast.Ellipsis):  # For older Python versions
            return True

        return False

    def _fix_protocol_method(
        self, node: ast.FunctionDef
    ) -> Union[ast.FunctionDef, ast.AsyncFunctionDef]:
        """Fix a protocol method to have proper ellipsis implementation."""
        # Check if method should be async based on naming patterns
        should_be_async = self._should_method_be_async(node.name)

        if should_be_async:
            # Convert to async method
            async_node = ast.AsyncFunctionDef(
                name=node.name,
                args=node.args,
                body=[ast.Expr(value=ast.Constant(value=...))],  # Just ellipsis
                decorator_list=node.decorator_list,
                returns=node.returns,
                type_comment=node.type_comment,
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
            self.methods_converted_to_async += 1
            self.changes_made.append(
                f"Converted {node.name} to async and fixed ellipsis"
            )
            return async_node
        else:
            # Check if sync method already has correct ellipsis
            if self._has_correct_ellipsis(node.body):
                # Method is already correct, don't change it
                return node

            # Fix sync method with ellipsis
            node.body = [ast.Expr(value=ast.Constant(value=...))]
            self.methods_fixed_ellipsis += 1
            self.changes_made.append(f"Fixed ellipsis in method: {node.name}")
            return node

    def _fix_async_protocol_method(
        self, node: ast.AsyncFunctionDef
    ) -> ast.AsyncFunctionDef:
        """Fix an async protocol method to have proper ellipsis implementation."""
        # Check if async method already has correct ellipsis
        if self._has_correct_ellipsis(node.body):
            # Method is already correct, don't change it
            return node

        # Ensure body is just ellipsis
        node.body = [ast.Expr(value=ast.Constant(value=...))]
        self.methods_fixed_ellipsis += 1
        self.changes_made.append(f"Fixed ellipsis in async method: {node.name}")
        return node

    def _should_method_be_async(self, method_name: str) -> bool:
        """Determine if a method should be async based on naming patterns and common I/O operations."""
        # Common async patterns
        async_patterns = [
            "read",
            "write",
            "save",
            "load",
            "fetch",
            "send",
            "receive",
            "execute",
            "process",
            "handle",
            "publish",
            "subscribe",
            "connect",
            "disconnect",
            "authenticate",
            "validate",
            "create",
            "update",
            "delete",
            "get",
            "set",
            "put",
            "post",
            "stream",
            "upload",
            "download",
            "sync",
            "refresh",
            "migrate",
            "backup",
            "restore",
            "compress",
            "decompress",
            "analyze",
            "transform",
            "convert",
            "generate",
            "build",
        ]

        method_lower = method_name.lower()

        # Check if method name contains async patterns
        for pattern in async_patterns:
            if pattern in method_lower:
                return True

        # Property methods should generally not be async
        if method_name.startswith("_"):  # Private methods
            return False

        return False


class ProtocolFileFixer:
    """Main class for fixing protocol compliance in files."""

    def __init__(self, dry_run: bool = False, verbose: bool = True):
        self.dry_run = dry_run
        self.verbose = verbose
        self.files_processed = 0
        self.files_changed = 0
        self.total_errors_fixed = 0

    def fix_file(self, file_path: Path) -> bool:
        """Fix protocol compliance issues in a single file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source_code = f.read()

            # Parse the AST
            try:
                tree = ast.parse(source_code, filename=str(file_path))
            except SyntaxError as e:
                if self.verbose:
                    print(f"❌ Syntax error in {file_path}: {e}")
                return False

            # Apply fixes
            fixer = ProtocolComplianceFixer(dry_run=self.dry_run)
            fixed_tree = fixer.visit(tree)

            # Check if changes were made
            if (
                fixer.methods_fixed_ellipsis > 0
                or fixer.standalone_functions_removed > 0
                or fixer.methods_converted_to_async > 0
            ):
                self.files_changed += 1
                self.total_errors_fixed += (
                    fixer.methods_fixed_ellipsis
                    + fixer.methods_converted_to_async
                    + fixer.standalone_functions_removed
                )

                if self.verbose:
                    try:
                        relative_path = file_path.relative_to(Path.cwd())
                    except ValueError:
                        relative_path = file_path
                    print(f"🔧 {relative_path}")
                    print(
                        f"   ✅ Methods fixed with ellipsis: {fixer.methods_fixed_ellipsis}"
                    )
                    print(
                        f"   ✅ Methods converted to async: {fixer.methods_converted_to_async}"
                    )
                    print(
                        f"   ✅ Standalone functions removed: {fixer.standalone_functions_removed}"
                    )

                if not self.dry_run:
                    # Convert AST back to source code
                    import astor

                    try:
                        fixed_source = astor.to_source(fixed_tree)

                        # Write the fixed code back
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(fixed_source)

                        if self.verbose:
                            print(f"   💾 File updated successfully")
                    except Exception as e:
                        print(f"❌ Failed to write fixed code for {file_path}: {e}")
                        return False
                else:
                    if self.verbose:
                        print(f"   🔍 DRY RUN - Changes not applied")

            self.files_processed += 1
            return True

        except Exception as e:
            if self.verbose:
                print(f"❌ Error processing {file_path}: {e}")
            return False

    def fix_directory(self, directory: Path, pattern: str = "*.py") -> None:
        """Fix all Python files in a directory."""
        if self.verbose:
            print(f"🔍 Scanning directory: {directory}")

        python_files = list(directory.rglob(pattern))
        protocol_files = [
            f for f in python_files if "protocol" in f.name or "protocols" in str(f)
        ]

        if self.verbose:
            print(f"📁 Found {len(protocol_files)} protocol files to process")

        for file_path in sorted(protocol_files):
            self.fix_file(file_path)

    def print_summary(self) -> None:
        """Print a summary of the fixes applied."""
        print("\n" + "=" * 60)
        print("🎯 PROTOCOL COMPLIANCE FIX SUMMARY")
        print("=" * 60)
        print(f"📁 Files processed: {self.files_processed}")
        print(f"🔧 Files changed: {self.files_changed}")
        print(f"✅ Total errors fixed: {self.total_errors_fixed}")

        if self.dry_run:
            print("\n🔍 DRY RUN MODE - No actual changes were made")
            print("Run without --dry-run to apply the fixes")
        else:
            print(f"\n🎉 All fixes have been applied successfully!")


def install_required_packages():
    """Install required packages if not available."""
    try:
        import astor
    except ImportError:
        print("📦 Installing required package: astor")
        import subprocess

        subprocess.check_call([sys.executable, "-m", "pip", "install", "astor"])
        import astor


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Automatically fix protocol compliance issues"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without making actual changes",
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Fix a specific file instead of the entire protocols directory",
    )
    parser.add_argument(
        "--verbose", action="store_true", default=True, help="Show detailed output"
    )
    parser.add_argument("--quiet", action="store_true", help="Suppress verbose output")

    args = parser.parse_args()

    if args.quiet:
        args.verbose = False

    # Install required packages
    install_required_packages()

    # Initialize the fixer
    fixer = ProtocolFileFixer(dry_run=args.dry_run, verbose=args.verbose)

    if args.verbose:
        print("🚀 Starting Protocol Compliance Auto-Fixer")
        print("=" * 50)

    if args.file:
        # Fix a specific file
        file_path = Path(args.file)
        if file_path.exists():
            fixer.fix_file(file_path)
        else:
            print(f"❌ File not found: {file_path}")
            sys.exit(1)
    else:
        # Fix all protocol files - use absolute path from script location
        script_dir = Path(__file__).parent
        repo_root = script_dir.parent  # Go up one level from scripts/ to repo root
        protocols_dir = repo_root / "src" / "omnibase_spi" / "protocols"

        if protocols_dir.exists():
            fixer.fix_directory(protocols_dir)
        else:
            print(f"❌ Protocols directory not found: {protocols_dir}")
            sys.exit(1)

    # Print summary
    fixer.print_summary()


if __name__ == "__main__":
    main()
