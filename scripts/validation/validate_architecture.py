#!/usr/bin/env python3
"""
Architecture Validator for ONEX SPI.

Enforces ONEX domain cohesion principle for protocol files. Instead of strict
one-protocol-per-file, we allow multiple protocols in a single file if they:
1. Are in the same domain/bounded context
2. Have strong cohesion (reference each other)
3. Are typically imported/used together

Files with more than MAX_PROTOCOLS_PER_FILE are flagged as violations, as they
likely indicate poor domain separation.

This is a STANDALONE validator using only Python stdlib to avoid circular
dependencies with omnibase_core.

Usage:
    python scripts/validation/validate_architecture.py [options]

Options:
    --path PATH       Path to scan (default: src/omnibase_spi/protocols)
    --verbose         Show all files checked, not just violations
    --json            Output results as JSON
    --strict          Fail on any violation (exit code 1)
    --exclude-init    Exclude __init__.py files from validation
    --max-protocols N Maximum protocols per file before warning (default: 15)

Exit Codes:
    0 - Success (no violations or --strict not set)
    1 - Violations found (with --strict)
    2 - Script error
"""

import argparse
import ast
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import TypeAlias

# Type aliases for clarity
LineNumber: TypeAlias = int
ClassName: TypeAlias = str

# Default maximum protocols per file before flagging as a violation
# This allows domain-cohesive groupings while catching overly large files
DEFAULT_MAX_PROTOCOLS = 15


@dataclass
class ProtocolDefinition:
    """Represents a Protocol class definition found in a file."""

    name: str
    line_number: int
    is_runtime_checkable: bool = False
    docstring: str | None = None


@dataclass
class FileViolation:
    """Represents a file that violates the domain cohesion rule."""

    file_path: Path
    protocols: list[ProtocolDefinition] = field(default_factory=list)
    max_allowed: int = DEFAULT_MAX_PROTOCOLS

    @property
    def protocol_count(self) -> int:
        """Return the number of protocols in this file."""
        return len(self.protocols)

    def format_error(self) -> str:
        """Format the violation as a human-readable error message."""
        lines = [
            f"\n{self.file_path}:",
            f"  VIOLATION: {self.protocol_count} Protocol definitions (max allowed: {self.max_allowed})",
            "  Consider splitting into multiple domain-specific files.",
        ]
        for proto in self.protocols:
            checkable = " [@runtime_checkable]" if proto.is_runtime_checkable else ""
            lines.append(f"    Line {proto.line_number}: {proto.name}{checkable}")
        return "\n".join(lines)


@dataclass
class ValidationResult:
    """Result of architecture validation."""

    files_checked: int = 0
    files_with_violations: int = 0
    total_protocols_found: int = 0
    violations: list[FileViolation] = field(default_factory=list)
    compliant_files: list[Path] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        """Return True if no violations were found."""
        return len(self.violations) == 0

    def to_dict(self) -> dict:
        """Convert result to dictionary for JSON output."""
        return {
            "valid": self.is_valid,
            "files_checked": self.files_checked,
            "files_with_violations": self.files_with_violations,
            "total_protocols_found": self.total_protocols_found,
            "violations": [
                {
                    "file": str(v.file_path),
                    "protocol_count": v.protocol_count,
                    "protocols": [
                        {
                            "name": p.name,
                            "line": p.line_number,
                            "runtime_checkable": p.is_runtime_checkable,
                        }
                        for p in v.protocols
                    ],
                }
                for v in self.violations
            ],
        }


class ProtocolVisitor(ast.NodeVisitor):
    """AST visitor that extracts Protocol class definitions."""

    def __init__(self) -> None:
        self.protocols: list[ProtocolDefinition] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit a class definition and check if it's a Protocol."""
        # Check if this class inherits from Protocol
        is_protocol = self._is_protocol_class(node)

        if is_protocol:
            # Check for @runtime_checkable decorator
            is_runtime_checkable = any(
                self._get_decorator_name(dec) == "runtime_checkable"
                for dec in node.decorator_list
            )

            # Extract docstring if present
            docstring = ast.get_docstring(node)

            self.protocols.append(
                ProtocolDefinition(
                    name=node.name,
                    line_number=node.lineno,
                    is_runtime_checkable=is_runtime_checkable,
                    docstring=docstring[:100] if docstring else None,
                )
            )

        # Continue visiting nested classes (though protocols shouldn't have them)
        self.generic_visit(node)

    def _is_protocol_class(self, node: ast.ClassDef) -> bool:
        """Check if a class definition inherits from Protocol."""
        for base in node.bases:
            base_name = self._get_base_name(base)
            if base_name in ("Protocol", "typing.Protocol"):
                return True
        return False

    def _get_base_name(self, node: ast.expr) -> str:
        """Extract the name from a base class expression."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_base_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Subscript):
            # Handle Generic[T] style bases
            return self._get_base_name(node.value)
        return ""

    def _get_decorator_name(self, node: ast.expr) -> str:
        """Extract the name from a decorator expression."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        elif isinstance(node, ast.Call):
            return self._get_decorator_name(node.func)
        return ""


def analyze_file(file_path: Path) -> list[ProtocolDefinition]:
    """
    Analyze a Python file for Protocol class definitions.

    Args:
        file_path: Path to the Python file to analyze

    Returns:
        List of ProtocolDefinition objects found in the file

    Raises:
        SyntaxError: If the file contains invalid Python syntax
        IOError: If the file cannot be read
    """
    source = file_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(file_path))

    visitor = ProtocolVisitor()
    visitor.visit(tree)

    return visitor.protocols


def validate_directory(
    path: Path,
    exclude_init: bool = False,
    verbose: bool = False,
    max_protocols: int = DEFAULT_MAX_PROTOCOLS,
) -> ValidationResult:
    """
    Validate all Python files in a directory for domain cohesion compliance.

    Instead of strict one-protocol-per-file, this allows multiple protocols
    in a single file as long as they don't exceed the max_protocols threshold.
    This supports domain-cohesive groupings (e.g., a service registry file
    containing related protocols like ProtocolServiceRegistry,
    ProtocolServiceRegistration, ProtocolDependencyGraph, etc.)

    Args:
        path: Directory path to scan
        exclude_init: Whether to exclude __init__.py files
        verbose: Whether to print progress information
        max_protocols: Maximum protocols per file before flagging (default: 15)

    Returns:
        ValidationResult containing all findings
    """
    result = ValidationResult()

    # Find all Python files (excluding symlinks for security)
    python_files = sorted(f for f in path.rglob("*.py") if not f.is_symlink())

    for file_path in python_files:
        # Skip __init__.py if requested
        if exclude_init and file_path.name == "__init__.py":
            continue

        # Skip non-protocol files (those not starting with protocol_)
        if not file_path.name.startswith("protocol_"):
            continue

        try:
            protocols = analyze_file(file_path)
            result.files_checked += 1
            result.total_protocols_found += len(protocols)

            if len(protocols) > max_protocols:
                # Violation: exceeds max threshold (likely poor domain separation)
                violation = FileViolation(
                    file_path=file_path,
                    protocols=protocols,
                    max_allowed=max_protocols,
                )
                result.violations.append(violation)
                result.files_with_violations += 1
            else:
                # Compliant file (within threshold)
                result.compliant_files.append(file_path)

            if verbose:
                status = "VIOLATION" if len(protocols) > max_protocols else "OK"
                print(f"  [{status}] {file_path}: {len(protocols)} protocol(s)")

        except SyntaxError as e:
            print(f"  [SYNTAX ERROR] {file_path}: {e}", file=sys.stderr)
        except IOError as e:
            print(f"  [IO ERROR] {file_path}: {e}", file=sys.stderr)

    return result


def main() -> int:
    """
    Main entry point for the architecture validator.

    Returns:
        Exit code (0 for success, 1 for violations in strict mode, 2 for errors)
    """
    parser = argparse.ArgumentParser(
        description="Validate ONEX domain cohesion for protocol files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=Path("src/omnibase_spi/protocols"),
        help="Path to scan (default: src/omnibase_spi/protocols)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show all files checked, not just violations",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on any violation (exit code 1)",
    )
    parser.add_argument(
        "--exclude-init",
        action="store_true",
        help="Exclude __init__.py files from validation",
    )
    parser.add_argument(
        "--max-protocols",
        type=int,
        default=DEFAULT_MAX_PROTOCOLS,
        help=f"Maximum protocols per file before flagging (default: {DEFAULT_MAX_PROTOCOLS})",
    )

    args = parser.parse_args()

    # Resolve path relative to script location if not absolute
    if not args.path.is_absolute():
        # Find the repo root (look for pyproject.toml)
        script_dir = Path(__file__).resolve().parent
        repo_root = script_dir.parent.parent  # scripts/validation -> repo root
        args.path = repo_root / args.path

    if not args.path.exists():
        print(f"Error: Path does not exist: {args.path}", file=sys.stderr)
        return 2

    if not args.path.is_dir():
        print(f"Error: Path is not a directory: {args.path}", file=sys.stderr)
        return 2

    # Run validation
    if not args.json:
        print(f"Validating ONEX domain cohesion in: {args.path}")
        print(f"Max protocols per file: {args.max_protocols}")
        print("-" * 60)

    result = validate_directory(
        path=args.path,
        exclude_init=args.exclude_init,
        verbose=args.verbose,
        max_protocols=args.max_protocols,
    )

    # Output results
    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print("-" * 60)
        print(f"Files checked:      {result.files_checked}")
        print(f"Protocols found:    {result.total_protocols_found}")
        print(f"Compliant files:    {len(result.compliant_files)}")
        print(f"Files w/violations: {result.files_with_violations}")

        if result.violations:
            print("\n" + "=" * 60)
            print("DOMAIN COHESION VIOLATIONS:")
            print("=" * 60)
            for violation in result.violations:
                print(violation.format_error())
            print()
            print(
                f"Found {result.files_with_violations} file(s) exceeding "
                f"max protocols threshold ({args.max_protocols})."
            )
            print("Consider splitting large files into domain-specific modules.")
        else:
            print("\nAll files comply with domain cohesion architecture.")

    # Determine exit code
    if result.violations and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
