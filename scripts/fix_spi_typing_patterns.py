#!/usr/bin/env python3
"""Fix SPI typing pattern violations using AST parsing.

This script analyzes Protocol classes and fixes common typing violations:
1. Async methods with non-awaitable return types
2. Sync methods that should be async (I/O operations)
3. Missing TYPE_CHECKING imports for forward references

Usage:
    # Dry-run (show what would change)
    python scripts/fix_spi_typing_patterns.py src/omnibase_spi/protocols --dry-run

    # Fix async return types
    python scripts/fix_spi_typing_patterns.py src/omnibase_spi/protocols --fix-async-returns

    # Fix sync I/O methods
    python scripts/fix_spi_typing_patterns.py src/omnibase_spi/protocols --fix-sync-io

    # Fix all violations
    python scripts/fix_spi_typing_patterns.py src/omnibase_spi/protocols --fix-async-returns --fix-sync-io
"""

import argparse
import ast
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Set


class ViolationType(Enum):
    """Types of SPI typing violations."""

    ASYNC_NON_AWAITABLE = "async_non_awaitable"
    SYNC_IO_METHOD = "sync_io_method"
    MISSING_TYPE_CHECKING = "missing_type_checking"


@dataclass
class Violation:
    """Represents a typing violation found in source code."""

    file_path: Path
    line_number: int
    violation_type: ViolationType
    current_code: str
    proposed_fix: str
    context: str


class SPITypingAnalyzer(ast.NodeVisitor):
    """Analyze Protocol classes for typing violations."""

    # Method name patterns that suggest I/O operations
    IO_METHOD_PATTERNS = {
        "read",
        "write",
        "fetch",
        "load",
        "save",
        "send",
        "receive",
        "get",
        "set",
        "update",
        "delete",
        "create",
        "execute",
        "publish",
        "subscribe",
        "register",
        "unregister",
        "open",
        "close",
        "connect",
        "disconnect",
        "query",
        "handle",
        "process",
        "can_handle",
        "invoke",
        "call",
    }

    def __init__(self, file_path: Path, source_code: str):
        self.file_path = file_path
        self.source_code = source_code
        self.source_lines = source_code.splitlines()
        self.violations: List[Violation] = []
        self.in_protocol_class = False
        self.current_class_name = None
        self.has_type_checking_import = False
        self.type_checking_imports: Set[str] = set()
        self.regular_imports: Set[str] = set()

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Track imports to detect TYPE_CHECKING usage."""
        if node.module == "typing":
            for alias in node.names:
                if alias.name == "TYPE_CHECKING":
                    self.has_type_checking_import = True
        self.generic_visit(node)

    def visit_If(self, node: ast.If) -> None:
        """Track imports inside TYPE_CHECKING blocks."""
        # Check if this is a TYPE_CHECKING conditional
        if isinstance(node.test, ast.Name) and node.test.id == "TYPE_CHECKING":
            # Track imports in this block
            for stmt in node.body:
                if isinstance(stmt, (ast.Import, ast.ImportFrom)):
                    self._extract_import_names(stmt, is_type_checking=True)
        else:
            # Track regular imports
            for stmt in ast.walk(node):
                if isinstance(stmt, (ast.Import, ast.ImportFrom)):
                    self._extract_import_names(stmt, is_type_checking=False)

        self.generic_visit(node)

    def _extract_import_names(self, node, is_type_checking: bool):
        """Extract imported names from import statements."""
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                name = alias.asname if alias.asname else alias.name
                if is_type_checking:
                    self.type_checking_imports.add(name)
                else:
                    self.regular_imports.add(name)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Track when we're inside a Protocol class."""
        # Check if this is a Protocol class
        is_protocol = False
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == "Protocol":
                is_protocol = True
                break

        if is_protocol:
            self.in_protocol_class = True
            self.current_class_name = node.name
            self.generic_visit(node)
            self.in_protocol_class = False
            self.current_class_name = None
        else:
            self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Check async methods for non-awaitable return types."""
        if not self.in_protocol_class:
            self.generic_visit(node)
            return

        # Check if method has a return annotation
        if node.returns:
            # Check if return type is wrapped in Awaitable
            if not self._is_awaitable_return(node.returns):
                # This is a violation - async method with non-awaitable return
                line_num = node.lineno
                current_code = self._get_method_signature(node)
                proposed_fix = self._wrap_in_awaitable(node)

                self.violations.append(
                    Violation(
                        file_path=self.file_path,
                        line_number=line_num,
                        violation_type=ViolationType.ASYNC_NON_AWAITABLE,
                        current_code=current_code,
                        proposed_fix=proposed_fix,
                        context=f"Class: {self.current_class_name}, Method: {node.name}",
                    )
                )

        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Check sync methods that should be async based on I/O patterns."""
        if not self.in_protocol_class:
            self.generic_visit(node)
            return

        # Skip special methods
        if node.name.startswith("__") and node.name.endswith("__"):
            self.generic_visit(node)
            return

        # Check if method name suggests I/O operation
        method_name = node.name.lower()
        is_io_method = any(
            pattern in method_name for pattern in self.IO_METHOD_PATTERNS
        )

        if is_io_method:
            # This is a violation - I/O method that's not async
            line_num = node.lineno
            current_code = self._get_method_signature(node)
            proposed_fix = self._make_async(node)

            self.violations.append(
                Violation(
                    file_path=self.file_path,
                    line_number=line_num,
                    violation_type=ViolationType.SYNC_IO_METHOD,
                    current_code=current_code,
                    proposed_fix=proposed_fix,
                    context=f"Class: {self.current_class_name}, Method: {node.name}",
                )
            )

        self.generic_visit(node)

    def _is_awaitable_return(self, returns_node) -> bool:
        """Check if return annotation is already wrapped in Awaitable."""
        annotation_str = ast.unparse(returns_node)
        return (
            annotation_str.startswith("Awaitable[")
            or annotation_str.startswith("typing.Awaitable[")
            or annotation_str.startswith("collections.abc.Awaitable[")
        )

    def _get_method_signature(self, node) -> str:
        """Extract method signature from source code."""
        try:
            # Get the actual line from source
            line_idx = node.lineno - 1
            if line_idx < len(self.source_lines):
                line = self.source_lines[line_idx].strip()
                # Handle multi-line signatures
                if not line.endswith(":"):
                    # Look ahead for continuation
                    for i in range(
                        line_idx + 1, min(line_idx + 10, len(self.source_lines))
                    ):
                        next_line = self.source_lines[i].strip()
                        line += " " + next_line
                        if next_line.endswith(":"):
                            break
                return line.rstrip(":") + ":"
        except Exception:
            pass

        # Fallback to unparsing the node
        return ast.unparse(node).split("\n")[0]

    def _wrap_in_awaitable(self, node: ast.AsyncFunctionDef) -> str:
        """Create proposed fix with Awaitable wrapper."""
        # Get current signature
        current_sig = self._get_method_signature(node)

        # Parse return annotation
        if node.returns:
            return_type = ast.unparse(node.returns)

            # Check if it's a string annotation (forward reference)
            is_string_annotation = isinstance(
                node.returns, ast.Constant
            ) and isinstance(node.returns.value, str)

            if is_string_annotation:
                # Forward reference - wrap the string content
                original_type = node.returns.value
                new_return = f'Awaitable["{original_type}"]'
            else:
                # Regular type - wrap it
                new_return = f"Awaitable[{return_type}]"

            # Replace return type in signature
            # Handle various return annotation formats
            if f" -> {return_type}:" in current_sig:
                proposed = current_sig.replace(
                    f" -> {return_type}:", f" -> {new_return}:"
                )
            elif f"-> {return_type}:" in current_sig:
                proposed = current_sig.replace(
                    f"-> {return_type}:", f"-> {new_return}:"
                )
            else:
                # Fallback - add at the end
                proposed = current_sig.rstrip(":") + f" -> {new_return}:"

            return proposed

        return current_sig

    def _make_async(self, node: ast.FunctionDef) -> str:
        """Create proposed fix making method async."""
        current_sig = self._get_method_signature(node)

        # Add async keyword
        if current_sig.strip().startswith("def "):
            proposed = current_sig.replace("def ", "async def ", 1)

            # If method has return annotation, wrap it in Awaitable
            if node.returns:
                return_type = ast.unparse(node.returns)
                is_string_annotation = isinstance(
                    node.returns, ast.Constant
                ) and isinstance(node.returns.value, str)

                if is_string_annotation:
                    original_type = node.returns.value
                    new_return = f'Awaitable["{original_type}"]'
                else:
                    new_return = f"Awaitable[{return_type}]"

                # Replace return type
                if f" -> {return_type}:" in proposed:
                    proposed = proposed.replace(
                        f" -> {return_type}:", f" -> {new_return}:"
                    )
                elif f"-> {return_type}:" in proposed:
                    proposed = proposed.replace(
                        f"-> {return_type}:", f"-> {new_return}:"
                    )

            return proposed

        return current_sig


class SPITypingFixer:
    """Apply fixes to SPI typing violations."""

    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.violations_by_file: Dict[Path, List[Violation]] = {}
        self.stats = {
            ViolationType.ASYNC_NON_AWAITABLE: 0,
            ViolationType.SYNC_IO_METHOD: 0,
            ViolationType.MISSING_TYPE_CHECKING: 0,
        }

    def scan_file(self, file_path: Path) -> List[Violation]:
        """Scan a single file for violations."""
        try:
            source_code = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source_code, filename=str(file_path))

            analyzer = SPITypingAnalyzer(file_path, source_code)
            analyzer.visit(tree)

            return analyzer.violations

        except Exception as e:
            print(f"Error scanning {file_path}: {e}", file=sys.stderr)
            return []

    def scan_directory(self, directory: Path, pattern: str = "protocol_*.py") -> None:
        """Scan all protocol files in directory."""
        for file_path in directory.rglob(pattern):
            if file_path.is_file():
                violations = self.scan_file(file_path)
                if violations:
                    self.violations_by_file[file_path] = violations
                    for violation in violations:
                        self.stats[violation.violation_type] += 1

    def apply_fixes(
        self, fix_async_returns: bool = False, fix_sync_io: bool = False
    ) -> None:
        """Apply fixes to files (or show dry-run)."""
        if not self.violations_by_file:
            print("✨ No violations found!")
            return

        for file_path, violations in sorted(self.violations_by_file.items()):
            # Filter violations based on what we want to fix
            violations_to_fix = []
            for v in violations:
                if (
                    v.violation_type == ViolationType.ASYNC_NON_AWAITABLE
                    and fix_async_returns
                ):
                    violations_to_fix.append(v)
                elif v.violation_type == ViolationType.SYNC_IO_METHOD and fix_sync_io:
                    violations_to_fix.append(v)

            if not violations_to_fix:
                continue

            if self.dry_run:
                self._show_dry_run(file_path, violations_to_fix)
            else:
                self._apply_file_fixes(file_path, violations_to_fix)

    def _show_dry_run(self, file_path: Path, violations: List[Violation]) -> None:
        """Show what would be changed without applying."""
        print(f"\n{'='*80}")
        print(
            f"File: {file_path.relative_to(Path.cwd()) if file_path.is_relative_to(Path.cwd()) else file_path}"
        )
        print(f"{'='*80}")

        for i, violation in enumerate(violations, 1):
            print(
                f"\n[{i}/{len(violations)}] Line {violation.line_number} - {violation.violation_type.value}"
            )
            print(f"Context: {violation.context}")
            print(f"\nCurrent:")
            print(f"  {violation.current_code}")
            print(f"\nProposed:")
            print(f"  {violation.proposed_fix}")
            print(f"{'-'*80}")

    def _apply_file_fixes(self, file_path: Path, violations: List[Violation]) -> None:
        """Apply fixes to a file."""
        # Read file content
        lines = file_path.read_text(encoding="utf-8").splitlines(keepends=True)

        # Sort violations by line number (reverse) to apply from bottom up
        violations_sorted = sorted(
            violations, key=lambda v: v.line_number, reverse=True
        )

        # Track if we need to add Awaitable import
        needs_awaitable_import = any(
            v.violation_type
            in (ViolationType.ASYNC_NON_AWAITABLE, ViolationType.SYNC_IO_METHOD)
            for v in violations
        )

        # Apply fixes
        for violation in violations_sorted:
            line_idx = violation.line_number - 1
            if line_idx < len(lines):
                # Get indentation
                original_line = lines[line_idx]
                indent = len(original_line) - len(original_line.lstrip())
                # Replace line
                lines[line_idx] = " " * indent + violation.proposed_fix.strip() + "\n"

        # Add Awaitable import if needed
        if needs_awaitable_import:
            lines = self._ensure_awaitable_import(lines)

        # Write back
        file_path.write_text("".join(lines), encoding="utf-8")
        print(
            f"✓ Applied {len(violations)} fixes to {file_path.relative_to(Path.cwd())}"
        )

    def _ensure_awaitable_import(self, lines: List[str]) -> List[str]:
        """Ensure Awaitable is imported from typing."""
        # Check if already imported
        for i, line in enumerate(lines):
            if "from typing import" in line and "Awaitable" in line:
                return lines
            if line.strip().startswith("from typing import"):
                if "(" in line:
                    # Multi-line import - check if Awaitable is already there
                    import_block = [line]
                    j = i + 1
                    while j < len(lines) and ")" not in lines[j - 1]:
                        import_block.append(lines[j])
                        j += 1
                    if any("Awaitable" in l for l in import_block):
                        return lines
                    # Add Awaitable to multi-line import
                    # Find first import item and add Awaitable before it
                    for k in range(i, min(i + 10, len(lines))):
                        if "(" in lines[k]:
                            lines[k] = lines[k].rstrip() + "\n"
                            lines.insert(k + 1, "    Awaitable,\n")
                            return lines
                else:
                    # Single line import - add Awaitable
                    if "Awaitable" not in line:
                        imports = line.replace("from typing import", "").strip()
                        lines[i] = f"from typing import Awaitable, {imports}\n"
                    return lines

        # No typing import found - add one after last import
        import_end_idx = 0
        for i, line in enumerate(lines):
            if line.strip().startswith(
                ("import ", "from ")
            ) and not line.strip().startswith("from __future__"):
                import_end_idx = i + 1

        # Add import after existing imports
        if import_end_idx > 0:
            lines.insert(import_end_idx, "from typing import Awaitable\n")
        else:
            # No imports found - add after module docstring or at top
            insert_idx = 0
            if lines and lines[0].strip().startswith('"""'):
                # Skip docstring
                for i in range(1, len(lines)):
                    if '"""' in lines[i]:
                        insert_idx = i + 1
                        break
            lines.insert(insert_idx, "from typing import Awaitable\n")

        return lines

    def print_summary(self) -> None:
        """Print summary of violations found."""
        print(f"\n{'='*80}")
        print("SUMMARY")
        print(f"{'='*80}")
        print(f"Total files with violations: {len(self.violations_by_file)}")
        print(f"Total violations: {sum(self.stats.values())}")
        print(f"\nBreakdown by type:")
        print(
            f"  Async non-awaitable returns: {self.stats[ViolationType.ASYNC_NON_AWAITABLE]}"
        )
        print(f"  Sync I/O methods: {self.stats[ViolationType.SYNC_IO_METHOD]}")
        print(
            f"  Missing TYPE_CHECKING imports: {self.stats[ViolationType.MISSING_TYPE_CHECKING]}"
        )
        print(f"{'='*80}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Fix SPI typing pattern violations using AST parsing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry-run (show what would change)
  python scripts/fix_spi_typing_patterns.py src/omnibase_spi/protocols --dry-run

  # Fix async return types only
  python scripts/fix_spi_typing_patterns.py src/omnibase_spi/protocols --fix-async-returns

  # Fix sync I/O methods only
  python scripts/fix_spi_typing_patterns.py src/omnibase_spi/protocols --fix-sync-io

  # Fix all violations
  python scripts/fix_spi_typing_patterns.py src/omnibase_spi/protocols --fix-async-returns --fix-sync-io

  # Scan single file
  python scripts/fix_spi_typing_patterns.py src/omnibase_spi/protocols/core/protocol_logger.py --dry-run
        """,
    )

    parser.add_argument("path", type=Path, help="Path to scan (file or directory)")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show changes without applying them (default: True if no fix flags)",
    )
    parser.add_argument(
        "--fix-async-returns",
        action="store_true",
        help="Fix async methods with non-awaitable return types",
    )
    parser.add_argument(
        "--fix-sync-io",
        action="store_true",
        help="Fix sync methods that perform I/O operations",
    )
    parser.add_argument(
        "--pattern",
        default="protocol_*.py",
        help="File pattern to match (default: protocol_*.py)",
    )

    args = parser.parse_args()

    # Determine dry-run mode
    has_fix_flag = args.fix_async_returns or args.fix_sync_io
    dry_run = args.dry_run or not has_fix_flag

    if dry_run:
        print("🔍 DRY-RUN MODE - No files will be modified")
        print("=" * 80)

    # Create fixer
    fixer = SPITypingFixer(dry_run=dry_run)

    # Scan files
    if args.path.is_file():
        violations = fixer.scan_file(args.path)
        if violations:
            fixer.violations_by_file[args.path] = violations
            for v in violations:
                fixer.stats[v.violation_type] += 1
    else:
        fixer.scan_directory(args.path, args.pattern)

    # Apply fixes or show dry-run
    fixer.apply_fixes(
        fix_async_returns=args.fix_async_returns or dry_run,
        fix_sync_io=args.fix_sync_io or dry_run,
    )

    # Print summary
    fixer.print_summary()

    if dry_run and has_fix_flag:
        print(
            "\n⚠️  Note: Dry-run was enabled. Re-run without --dry-run to apply changes."
        )
    elif dry_run and not has_fix_flag:
        print("\n💡 To apply fixes, use --fix-async-returns and/or --fix-sync-io")
        print(
            "   Example: python scripts/fix_spi_typing_patterns.py src/omnibase_spi/protocols --fix-async-returns --fix-sync-io"
        )

    # Return exit code based on violations found
    sys.exit(0 if not fixer.violations_by_file else 1)


if __name__ == "__main__":
    main()
