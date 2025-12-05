#!/usr/bin/env python3
"""
SPI Empty Directory Detection

Detects directories that are empty or only contain an __init__.py file.
Such directories indicate incomplete refactoring, removed functionality,
or placeholder modules that should be cleaned up.

Examples of problematic directories:
- Empty directory (no files at all)
- Directory with only __init__.py (no actual implementation)
- Directory with only metadata files (.DS_Store, Thumbs.db, etc.)

This enforces clean directory structure across the SPI package.

Adapted from omnibase_core/scripts/validation/validate-no-empty-directories.py
"""

import argparse
import sys
from pathlib import Path
from typing import ClassVar


class EmptyDirectoryViolation:
    """Represents an empty or init-only directory violation."""

    def __init__(self, path: Path, has_init: bool):
        self.path = path
        self.has_init = has_init

    def __str__(self) -> str:
        if self.has_init:
            return f"Directory only contains __init__.py: {self.path}"
        else:
            return f"Empty directory: {self.path}"


class EmptyDirectoryValidator:
    """Validates that no directories are empty or contain only __init__.py."""

    # Directories to exclude from checks
    EXCLUDED_DIRS: ClassVar[set[str]] = {
        "__pycache__",
        ".git",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "node_modules",
        ".venv",
        "venv",
        "dist",
        "build",
        ".egg-info",
        ".tox",
        "htmlcov",
        ".coverage",
        ".hypothesis",
        "src",  # Top-level src directory (contains package folders only)
        "tmp",  # Workspace for custom commands (intentionally empty)
    }

    # Patterns to exclude (directories containing these strings)
    EXCLUDED_PATTERNS: ClassVar[set[str]] = {
        "__pycache__",
        ".egg-info",
        "archived",
        "archive",
    }

    # Metadata files to ignore when checking if directory is empty
    METADATA_FILES: ClassVar[set[str]] = {
        ".DS_Store",  # macOS metadata
        "Thumbs.db",  # Windows thumbnail cache
        "desktop.ini",  # Windows folder settings
        ".gitkeep",  # Git placeholder for empty directories
        ".directory",  # KDE folder settings
    }

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.violations: list[EmptyDirectoryViolation] = []

    def validate(self) -> bool:
        """
        Validate for empty directories or directories with only __init__.py.

        Returns:
            True if no empty directories found, False otherwise
        """
        self._scan_directories(self.repo_path)
        return len(self.violations) == 0

    def _should_exclude(self, dir_path: Path) -> bool:
        """Check if directory should be excluded from validation."""
        if dir_path.name in self.EXCLUDED_DIRS:
            return True

        path_str = str(dir_path)
        if any(pattern in path_str for pattern in self.EXCLUDED_PATTERNS):
            return True

        try:
            relative_path = dir_path.relative_to(self.repo_path)
            for part in relative_path.parts:
                if part.startswith(".") and part not in (".", ".."):
                    return True
        except ValueError:
            if dir_path.name.startswith(".") and dir_path.name not in (".", ".."):
                return True

        return False

    def _scan_directories(self, base_path: Path) -> None:
        """Recursively scan directories for empty or init-only violations."""
        for item in base_path.iterdir():
            if not item.is_dir():
                continue

            if self._should_exclude(item):
                continue

            self._scan_directories(item)

            all_files = [f for f in item.iterdir() if f.is_file()]
            files = [f for f in all_files if f.name not in self.METADATA_FILES]

            if len(files) == 0:
                self.violations.append(EmptyDirectoryViolation(item, has_init=False))
            elif len(files) == 1 and files[0].name == "__init__.py":
                init_file = files[0]
                if self._is_trivial_init(init_file):
                    self.violations.append(EmptyDirectoryViolation(item, has_init=True))

    def _is_trivial_init(self, init_file: Path) -> bool:
        """
        Check if __init__.py is trivial (empty or only comments/docstrings).
        """
        try:
            content = init_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return False

        content = content.strip()

        if not content:
            return True

        try:
            import ast

            tree = ast.parse(content)

            for stmt in tree.body:
                if isinstance(stmt, ast.Expr):
                    if isinstance(stmt.value, ast.Constant) and isinstance(
                        stmt.value.value, str
                    ):
                        continue

                if isinstance(stmt, ast.Pass):
                    continue

                return False

            return True

        except SyntaxError:
            return False

    def generate_report(self) -> str:
        """Generate a validation report."""
        if not self.violations:
            return "No empty directories found!"

        report = "SPI Empty Directory Violations\n"
        report += "=" * 60 + "\n\n"

        report += f"Found {len(self.violations)} empty or init-only director(ies):\n\n"

        empty_dirs = [v for v in self.violations if not v.has_init]
        init_only_dirs = [v for v in self.violations if v.has_init]

        if empty_dirs:
            report += "Empty Directories:\n"
            for violation in sorted(empty_dirs, key=lambda v: str(v.path)):
                report += f"   - {violation.path}\n"
            report += "\n"

        if init_only_dirs:
            report += "Directories with only __init__.py:\n"
            for violation in sorted(init_only_dirs, key=lambda v: str(v.path)):
                report += f"   - {violation.path}\n"
            report += "\n"

        report += "How to fix:\n"
        report += "  1. If directory is no longer needed: Delete it entirely\n"
        report += "  2. If functionality was moved: Remove the empty directory\n"
        report += "  3. If it's a placeholder: Add actual implementation or remove\n"
        report += "  4. If __init__.py is needed for namespace: Add a comment explaining why\n"

        return report


def main() -> int:
    """Main entry point for validation script."""
    parser = argparse.ArgumentParser(
        description="Detect empty directories or directories with only __init__.py"
    )
    parser.add_argument(
        "repo_path",
        nargs="?",
        default=".",
        help="Path to repository root (default: current directory)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output",
    )

    args = parser.parse_args()

    repo_path = Path(args.repo_path).resolve()
    if not repo_path.exists():
        print(f"Error: Repository path does not exist: {repo_path}")
        return 1

    validator = EmptyDirectoryValidator(repo_path)
    is_valid = validator.validate()

    if is_valid:
        if args.verbose:
            print("No empty directories found!")
        return 0
    else:
        report = validator.generate_report()
        print(report)
        print(f"\nFAILURE: {len(validator.violations)} empty director(ies) found!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
