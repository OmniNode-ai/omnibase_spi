#!/usr/bin/env python3
"""
AST-based typing modernization script for omnibase-spi project.

This script modernizes Python typing syntax to Python 3.10+ standards:
- Optional[T] → T | None
- Union[A, B] → A | B
- Remove quotes from forward references imported in TYPE_CHECKING blocks
- Fix type annotations for modern syntax

Features:
- Dry run by default (safe preview mode)
- Flexible file targeting (subset, pattern, or all files)
- Comprehensive reporting with before/after previews
- AST validation and safe execution
- Statistics and error handling

Usage:
    # Preview changes (dry run by default)
    python scripts/modernize_typing.py

    # Apply all transformations to all files
    python scripts/modernize_typing.py --apply --all

    # Apply specific transformations to specific files
    python scripts/modernize_typing.py --apply --optional --files src/omnibase_spi/protocols/core/

    # Preview Union transformations with verbose output
    python scripts/modernize_typing.py --union --verbose

Authors: Claude Code Agent
Version: 1.0.0
"""

import argparse
import ast
import shutil
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


@dataclass
class TransformationReport:
    """Report of transformations made to a file."""

    file_path: str
    original_content: str
    transformed_content: str
    transformations: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        """Check if file has any transformations."""
        return len(self.transformations) > 0

    @property
    def transformation_count(self) -> int:
        """Total number of transformations."""
        return len(self.transformations)


@dataclass
class OverallReport:
    """Overall report across all files processed."""

    files_processed: int = 0
    files_with_changes: int = 0
    total_transformations: int = 0
    transformation_counts: Dict[str, int] = field(
        default_factory=lambda: defaultdict(int)
    )
    errors: List[str] = field(default_factory=list)
    file_reports: List[TransformationReport] = field(default_factory=list)


class TypeCheckingImportsTracker:
    """Track imports from TYPE_CHECKING blocks for forward reference resolution."""

    def __init__(self) -> None:
        self.type_checking_imports: Set[str] = set()
        self.import_aliases: Dict[str, str] = {}  # alias -> real_name mapping

    def visit_type_checking_block(self, node: ast.If) -> None:
        """Extract imports from TYPE_CHECKING conditional blocks."""
        if not self._is_type_checking_block(node):
            return

        for stmt in node.body:
            if isinstance(stmt, ast.Import):
                for alias in stmt.names:
                    name = alias.asname if alias.asname else alias.name
                    self.type_checking_imports.add(name)
                    if alias.asname:
                        self.import_aliases[alias.asname] = alias.name

            elif isinstance(stmt, ast.ImportFrom):
                for alias in stmt.names:
                    name = alias.asname if alias.asname else alias.name
                    self.type_checking_imports.add(name)
                    if alias.asname:
                        self.import_aliases[alias.asname] = alias.name

    def _is_type_checking_block(self, node: ast.If) -> bool:
        """Check if an if statement is a TYPE_CHECKING block."""
        if isinstance(node.test, ast.Name):
            return node.test.id == "TYPE_CHECKING"
        elif isinstance(node.test, ast.Attribute):
            return (
                isinstance(node.test.value, ast.Name)
                and node.test.value.id == "typing"
                and node.test.attr == "TYPE_CHECKING"
            )
        return False

    def is_forward_reference(self, name: str) -> bool:
        """Check if a name should have quotes removed (is imported in TYPE_CHECKING)."""
        return name in self.type_checking_imports


class TypingModernizer(ast.NodeTransformer):
    """AST transformer for modernizing typing syntax."""

    def __init__(
        self,
        enable_optional: bool = True,
        enable_union: bool = True,
        enable_forward_refs: bool = True,
        verbose: bool = False,
    ):
        self.enable_optional = enable_optional
        self.enable_union = enable_union
        self.enable_forward_refs = enable_forward_refs
        self.verbose = verbose

        self.transformations: List[Dict[str, Any]] = []
        self.type_checking_tracker: TypeCheckingImportsTracker = (
            TypeCheckingImportsTracker()
        )
        self.imports_tracker_run = False

    def visit(self, node: ast.AST) -> Any:
        """Visit node and track TYPE_CHECKING imports on first pass."""
        if not self.imports_tracker_run:
            self._collect_type_checking_imports(node)
            self.imports_tracker_run = True
        return super().visit(node)

    def _collect_type_checking_imports(self, root: ast.AST) -> None:
        """Collect all TYPE_CHECKING imports from the AST."""
        for node in ast.walk(root):
            if isinstance(node, ast.If):
                self.type_checking_tracker.visit_type_checking_block(node)

    def visit_Subscript(self, node: ast.Subscript) -> Any:
        """Transform Optional[T] and Union[A, B] subscripts."""
        visited_node = self.generic_visit(node)

        # Handle type checking due to mypy AST visitor pattern
        if not isinstance(visited_node, ast.Subscript):
            return visited_node

        node = visited_node

        if isinstance(node.value, ast.Name):
            # Handle Optional[T] → T | None
            if self.enable_optional and node.value.id == "Optional":
                return self._transform_optional(node)

            # Handle Union[A, B] → A | B
            elif self.enable_union and node.value.id == "Union":
                return self._transform_union(node)

        elif isinstance(node.value, ast.Attribute):
            # Handle typing.Optional[T] and typing.Union[A, B]
            if (
                isinstance(node.value.value, ast.Name)
                and node.value.value.id == "typing"
            ):

                if self.enable_optional and node.value.attr == "Optional":
                    return self._transform_optional(node)
                elif self.enable_union and node.value.attr == "Union":
                    return self._transform_union(node)

        return node

    def visit_Constant(self, node: ast.Constant) -> Any:
        """Transform string forward references."""
        visited_node = self.generic_visit(node)

        # Handle type checking due to mypy AST visitor pattern
        if not isinstance(visited_node, ast.Constant):
            return visited_node

        node = visited_node

        if (
            self.enable_forward_refs
            and isinstance(node.value, str)
            and self._is_forward_reference_candidate(node.value)
        ):

            # Remove quotes if this is a known TYPE_CHECKING import
            if self.type_checking_tracker.is_forward_reference(node.value):
                return self._transform_forward_reference(node)

        return node

    def _transform_optional(self, node: ast.Subscript) -> ast.BinOp:
        """Transform Optional[T] to T | None."""
        # For Python 3.9+, slice is direct value
        inner_type = node.slice

        # Create T | None
        none_node = ast.Constant(value=None)
        binary_op = ast.BinOp(left=inner_type, op=ast.BitOr(), right=none_node)

        self.transformations.append(
            {
                "type": "optional_to_union",
                "line": getattr(node, "lineno", 0),
                "col": getattr(node, "col_offset", 0),
                "original": ast.unparse(node),
                "transformed": ast.unparse(binary_op),
            }
        )

        return binary_op

    def _transform_union(self, node: ast.Subscript) -> ast.BinOp:
        """Transform Union[A, B] to A | B."""
        if isinstance(node.slice, ast.Tuple):
            # Multiple union members: Union[A, B, C] → A | B | C
            elements = node.slice.elts
        else:
            # Single element (shouldn't happen, but handle gracefully)
            elements = [node.slice]

        if len(elements) < 2:
            # Not a valid union, return unchanged but as BinOp for type consistency
            if len(elements) == 1:
                none_node = ast.Constant(value=None)
                return ast.BinOp(left=elements[0], op=ast.BitOr(), right=none_node)
            return ast.BinOp(
                left=ast.Constant(value=None),
                op=ast.BitOr(),
                right=ast.Constant(value=None),
            )

        # Build chained binary operations: A | B | C
        result: ast.expr = elements[0]
        for element in elements[1:]:
            result = ast.BinOp(left=result, op=ast.BitOr(), right=element)

        # Ensure we return ast.BinOp as expected
        if not isinstance(result, ast.BinOp):
            # This shouldn't happen with len(elements) >= 2, but ensure type safety
            result = ast.BinOp(left=elements[0], op=ast.BitOr(), right=elements[1])

        self.transformations.append(
            {
                "type": "union_to_binary",
                "line": getattr(node, "lineno", 0),
                "col": getattr(node, "col_offset", 0),
                "original": ast.unparse(node),
                "transformed": ast.unparse(result),
            }
        )

        return result

    def _transform_forward_reference(self, node: ast.Constant) -> ast.Name:
        """Transform quoted forward reference to unquoted name."""
        # Ensure node.value is a string
        if not isinstance(node.value, str):
            return ast.Name(
                id="Any", ctx=ast.Load()
            )  # Fallback to Any for non-string values
        name_node = ast.Name(id=node.value, ctx=ast.Load())

        self.transformations.append(
            {
                "type": "forward_reference",
                "line": getattr(node, "lineno", 0),
                "col": getattr(node, "col_offset", 0),
                "original": f'"{str(node.value)}"',
                "transformed": str(node.value),
            }
        )

        return name_node

    def _is_forward_reference_candidate(self, value: str) -> bool:
        """Check if string looks like a type annotation."""
        # Basic heuristics for type annotations:
        # - Starts with capital letter (class name)
        # - Contains valid identifier characters
        # - Not too long (avoid false positives)
        return (
            len(value) > 0
            and value[0].isupper()
            and value.isidentifier()
            and len(value) < 100
        )


class TypingModernizationEngine:
    """Main engine for typing modernization."""

    def __init__(self, dry_run: bool = True, verbose: bool = False):
        self.dry_run = dry_run
        self.verbose = verbose
        self.overall_report = OverallReport()

    def process_files(
        self,
        file_paths: List[Path],
        enable_optional: bool = True,
        enable_union: bool = True,
        enable_forward_refs: bool = True,
    ) -> OverallReport:
        """Process multiple files for typing modernization."""

        for file_path in file_paths:
            try:
                if self.verbose:
                    print(f"Processing: {file_path}")

                report = self._process_single_file(
                    file_path, enable_optional, enable_union, enable_forward_refs
                )

                self.overall_report.file_reports.append(report)
                self.overall_report.files_processed += 1

                if report.has_changes:
                    self.overall_report.files_with_changes += 1
                    self.overall_report.total_transformations += (
                        report.transformation_count
                    )

                    # Count transformations by type
                    for transform in report.transformations:
                        transform_type = transform["type"]
                        self.overall_report.transformation_counts[transform_type] += 1

            except Exception as e:
                error_msg = f"Error processing {file_path}: {str(e)}"
                self.overall_report.errors.append(error_msg)
                if self.verbose:
                    print(f"ERROR: {error_msg}")

        return self.overall_report

    def _process_single_file(
        self,
        file_path: Path,
        enable_optional: bool,
        enable_union: bool,
        enable_forward_refs: bool,
    ) -> TransformationReport:
        """Process a single file for modernization."""

        # Read original content
        with open(file_path, "r", encoding="utf-8") as f:
            original_content = f.read()

        report = TransformationReport(
            file_path=str(file_path),
            original_content=original_content,
            transformed_content=original_content,
        )

        try:
            # Parse AST
            tree = ast.parse(original_content)

            # Transform
            modernizer = TypingModernizer(
                enable_optional=enable_optional,
                enable_union=enable_union,
                enable_forward_refs=enable_forward_refs,
                verbose=self.verbose,
            )

            transformed_tree = modernizer.visit(tree)

            # Generate transformed content
            try:
                transformed_content = ast.unparse(transformed_tree)
                report.transformed_content = transformed_content
                report.transformations = modernizer.transformations

                # Write changes if not dry run
                if not self.dry_run and report.has_changes:
                    self._backup_file(file_path)
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(transformed_content)

            except Exception as e:
                report.errors.append(
                    f"Failed to generate transformed content: {str(e)}"
                )

        except SyntaxError as e:
            report.errors.append(f"Syntax error parsing file: {str(e)}")
        except Exception as e:
            report.errors.append(f"Unexpected error: {str(e)}")

        return report

    def _backup_file(self, file_path: Path) -> None:
        """Create backup of original file."""
        backup_path = file_path.with_suffix(file_path.suffix + ".backup")
        shutil.copy2(file_path, backup_path)


def collect_python_files(paths: List[str], pattern: Optional[str] = None) -> List[Path]:
    """Collect Python files from given paths."""
    files = []

    for path_str in paths:
        path = Path(path_str)

        if path.is_file() and path.suffix == ".py":
            files.append(path)
        elif path.is_dir():
            if pattern:
                files.extend(path.rglob(pattern))
            else:
                files.extend(path.rglob("*.py"))

    return sorted(files)


def print_file_report(report: TransformationReport, verbose: bool = False) -> None:
    """Print report for a single file."""
    if not report.has_changes and not report.errors:
        if verbose:
            print(f"  {report.file_path}: No changes needed")
        return

    print(f"\n📁 {report.file_path}")

    if report.errors:
        print(f"  ❌ Errors: {len(report.errors)}")
        for error in report.errors:
            print(f"     {error}")

    if report.has_changes:
        print(f"  ✅ Transformations: {report.transformation_count}")

        # Group by type
        by_type = defaultdict(list)
        for transform in report.transformations:
            by_type[transform["type"]].append(transform)

        for transform_type, transforms in by_type.items():
            print(f"     {transform_type}: {len(transforms)} changes")

            if verbose:
                for transform in transforms[:3]:  # Show first 3 examples
                    line = transform.get("line", "?")
                    original = transform.get("original", "")
                    transformed = transform.get("transformed", "")
                    print(f"       Line {line}: {original} → {transformed}")

                if len(transforms) > 3:
                    print(f"       ... and {len(transforms) - 3} more")


def print_overall_report(report: OverallReport, verbose: bool = False) -> None:
    """Print overall summary report."""

    print("\n📊 MODERNIZATION SUMMARY")
    print(f"{'=' * 50}")
    print(f"Files processed: {report.files_processed}")
    print(f"Files with changes: {report.files_with_changes}")
    print(f"Total transformations: {report.total_transformations}")

    if report.transformation_counts:
        print("\nTransformations by type:")
        for transform_type, count in sorted(report.transformation_counts.items()):
            print(f"  {transform_type}: {count}")

    if report.errors:
        print(f"\n❌ Errors encountered: {len(report.errors)}")
        for error in report.errors:
            print(f"  {error}")

    # Print individual file reports if verbose or if there are changes
    if verbose or report.files_with_changes > 0:
        print("\n📋 FILE DETAILS")
        print(f"{'=' * 50}")
        for file_report in report.file_reports:
            print_file_report(file_report, verbose=verbose)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Modernize Python typing syntax for Python 3.10+",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview all changes (dry run)
  python scripts/modernize_typing.py

  # Apply all transformations to all files
  python scripts/modernize_typing.py --apply --all

  # Apply only Optional transformations to specific files
  python scripts/modernize_typing.py --apply --optional --files src/omnibase_spi/protocols/core/

  # Preview Union transformations with verbose output
  python scripts/modernize_typing.py --union --verbose

  # Apply all transformations to files matching pattern
  python scripts/modernize_typing.py --apply --pattern "protocol_*.py" --all
        """,
    )

    # Execution mode
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Preview changes without applying them (default)",
    )
    parser.add_argument(
        "--apply", action="store_true", help="Actually apply the transformations"
    )

    # File targeting
    parser.add_argument(
        "--files",
        nargs="+",
        default=[],
        help="Specific files or directories to process",
    )
    parser.add_argument(
        "--pattern", type=str, help='File pattern to match (e.g., "protocol_*.py")'
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Process all Python files in src/omnibase_spi/protocols/",
    )

    # Transformation selection
    parser.add_argument(
        "--optional",
        action="store_true",
        help="Enable Optional[T] → T | None transformation",
    )
    parser.add_argument(
        "--union", action="store_true", help="Enable Union[A, B] → A | B transformation"
    )
    parser.add_argument(
        "--type-checking",
        action="store_true",
        help="Enable TYPE_CHECKING forward reference transformation",
    )
    parser.add_argument(
        "--all-transforms",
        action="store_true",
        help="Enable all transformations (default if none specified)",
    )

    # Output control
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output with detailed change previews",
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Minimal output (only summary)"
    )

    args = parser.parse_args()

    # Resolve execution mode
    dry_run = not args.apply  # Default to dry run unless --apply is specified

    # Resolve file targeting
    if args.all:
        target_paths = ["src/omnibase_spi/protocols/"]
    elif args.files:
        target_paths = args.files
    else:
        # Default to protocols directory
        target_paths = ["src/omnibase_spi/protocols/"]

    # Resolve transformations
    if args.all_transforms or not any([args.optional, args.union, args.type_checking]):
        # Enable all if none specified or --all-transforms
        enable_optional = True
        enable_union = True
        enable_forward_refs = True
    else:
        enable_optional = args.optional
        enable_union = args.union
        enable_forward_refs = args.type_checking

    # Collect files
    try:
        files = collect_python_files(target_paths, args.pattern)

        if not files:
            print("❌ No Python files found matching criteria")
            return 1

        if not args.quiet:
            mode = "DRY RUN" if dry_run else "APPLYING CHANGES"
            print(f"🔧 TYPING MODERNIZATION - {mode}")
            print(f"{'=' * 50}")
            print(f"Target files: {len(files)}")
            print("Transformations enabled:")
            print(f"  Optional[T] → T | None: {enable_optional}")
            print(f"  Union[A, B] → A | B: {enable_union}")
            print(f"  TYPE_CHECKING forward refs: {enable_forward_refs}")

            if dry_run:
                print("\n💡 This is a preview. Use --apply to make changes.")

    except Exception as e:
        print(f"❌ Error collecting files: {e}")
        return 1

    # Process files
    try:
        engine = TypingModernizationEngine(dry_run=dry_run, verbose=args.verbose)

        report = engine.process_files(
            files,
            enable_optional=enable_optional,
            enable_union=enable_union,
            enable_forward_refs=enable_forward_refs,
        )

        # Print results
        if not args.quiet:
            print_overall_report(report, verbose=args.verbose)

        # Return appropriate exit code
        if report.errors:
            return 1
        elif report.total_transformations > 0:
            if dry_run:
                print(
                    f"\n💡 {report.total_transformations} changes ready. Use --apply to execute."
                )
            else:
                print(
                    f"\n✅ Successfully applied {report.total_transformations} transformations."
                )
        else:
            print("\n✨ No changes needed - code is already modernized!")

        return 0

    except KeyboardInterrupt:
        print("\n❌ Interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
