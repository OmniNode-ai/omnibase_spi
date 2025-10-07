#!/usr/bin/env python3
"""
Comprehensive Forward Reference Fixer for omnibase-spi

Scans all protocol files and fixes forward reference issues by:
1. Identifying types imported under TYPE_CHECKING
2. Finding all unquoted usages of those types
3. Converting them to quoted forward references
4. Generating comprehensive fix report
"""

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set, Tuple


@dataclass
class ForwardReferenceFix:
    """Represents a fix for a forward reference issue."""

    file_path: Path
    line_number: int
    original_line: str
    fixed_line: str
    type_name: str


@dataclass
class FileAnalysis:
    """Analysis results for a single file."""

    file_path: Path
    type_checking_imports: Set[str] = field(default_factory=set)
    fixes: List[ForwardReferenceFix] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class ForwardReferenceFixer:
    """Fixes forward reference issues in protocol files."""

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.analyses: List[FileAnalysis] = []

    def analyze_file(self, file_path: Path) -> FileAnalysis:
        """Analyze a single file for forward reference issues."""
        analysis = FileAnalysis(file_path=file_path)

        try:
            content = file_path.read_text()
            analysis.type_checking_imports = self._extract_type_checking_imports(
                content
            )

            if analysis.type_checking_imports:
                # Find and fix unquoted usages
                lines = content.split("\n")
                for i, line in enumerate(lines, 1):
                    fixes = self._find_unquoted_usages(
                        line, analysis.type_checking_imports, i
                    )
                    for fix in fixes:
                        fix.file_path = file_path
                        analysis.fixes.append(fix)

        except Exception as e:
            analysis.errors.append(f"Error analyzing file: {e}")

        return analysis

    def _extract_type_checking_imports(self, content: str) -> Set[str]:
        """Extract all type names imported under TYPE_CHECKING blocks."""
        type_checking_imports = set()

        try:
            tree = ast.parse(content)

            # Find TYPE_CHECKING blocks
            for node in ast.walk(tree):
                if isinstance(node, ast.If):
                    # Check if this is a TYPE_CHECKING block
                    if self._is_type_checking_block(node):
                        # Extract imports from this block
                        for child in ast.walk(node):
                            if isinstance(child, ast.ImportFrom):
                                for alias in child.names:
                                    # Track both original name and alias (if any)
                                    type_checking_imports.add(alias.name)
                                    if alias.asname:
                                        type_checking_imports.add(alias.asname)
                            elif isinstance(child, ast.Import):
                                for alias in child.names:
                                    # Handle "import module" - extract module name
                                    type_checking_imports.add(alias.name.split(".")[-1])
                                    if alias.asname:
                                        type_checking_imports.add(alias.asname)

        except SyntaxError as e:
            # If AST parsing fails, use regex fallback
            type_checking_imports = self._extract_type_checking_imports_regex(content)

        return type_checking_imports

    def _is_type_checking_block(self, node: ast.If) -> bool:
        """Check if an If node is a TYPE_CHECKING block."""
        if isinstance(node.test, ast.Name):
            return node.test.id == "TYPE_CHECKING"
        elif isinstance(node.test, ast.Attribute):
            return node.test.attr == "TYPE_CHECKING"
        return False

    def _extract_type_checking_imports_regex(self, content: str) -> Set[str]:
        """Fallback regex-based extraction of TYPE_CHECKING imports."""
        type_checking_imports = set()

        # Find TYPE_CHECKING block
        type_checking_pattern = r"if TYPE_CHECKING:(.*?)(?=\n(?:if|class|def|@|\Z))"
        matches = re.findall(type_checking_pattern, content, re.DOTALL)

        for block in matches:
            # Extract import statements
            import_pattern = r"from\s+[\w.]+\s+import\s+([^\n]+)"
            for import_match in re.finditer(import_pattern, block):
                import_stmt = import_match.group(1)
                # Handle "from x import A, B, C" and "from x import A as B"
                for name in import_stmt.split(","):
                    name = name.strip()
                    if " as " in name:
                        # Track both original and alias: "Foo as Bar"
                        original, alias = name.split(" as ", 1)
                        type_checking_imports.add(original.strip())
                        type_checking_imports.add(alias.strip())
                    else:
                        type_checking_imports.add(name)

        return type_checking_imports

    def _find_unquoted_usages(
        self, line: str, type_names: Set[str], line_number: int
    ) -> List[ForwardReferenceFix]:
        """Find unquoted usages of TYPE_CHECKING imports in a line."""
        fixes = []

        # Skip comment lines and import lines
        stripped = line.strip()
        if (
            stripped.startswith("#")
            or stripped.startswith("import ")
            or stripped.startswith("from ")
        ):
            return fixes

        # Build updated line incrementally to handle multiple types on same line
        original_line = line
        updated_line = line
        types_fixed = []

        for type_name in type_names:
            # Patterns to detect unquoted type usage
            patterns = [
                # Return type annotations: -> TypeName
                (rf"(\s*->\s*)({type_name})(\s*[:\)])", rf'\1"\2"\3'),
                # Parameter type annotations: param: TypeName
                (rf"(\w+\s*:\s*)({type_name})(\s*[,=\)])", rf'\1"\2"\3'),
                # List/Dict type annotations: list[TypeName]
                (rf"(list\[)({type_name})(\])", rf'\1"\2"\3'),
                (rf"(dict\[[^,]+,\s*)({type_name})(\])", rf'\1"\2"\3'),
                # Union type annotations: TypeName |
                (rf"(\|\s*)({type_name})(\s*[,\)])", rf'\1"\2"\3'),
                (rf"({type_name})(\s*\|)", rf'"\1"\2'),
                # Literal attribute: attribute: TypeName
                (rf"^\s*(\w+)\s*:\s*({type_name})\s*$", rf'\1: "\2"'),
            ]

            # Check if type is already quoted in current version of line
            if f'"{type_name}"' in updated_line or f"'{type_name}'" in updated_line:
                continue

            for pattern, replacement in patterns:
                match = re.search(pattern, updated_line)
                if match:
                    # Apply fix to updated_line (not original)
                    updated_line = re.sub(pattern, replacement, updated_line)
                    types_fixed.append(type_name)
                    # Continue to check other patterns for this type
                    break

        # Only create a fix if we actually changed something
        if updated_line != original_line:
            fix = ForwardReferenceFix(
                file_path=Path(),  # Will be set by caller
                line_number=line_number,
                original_line=original_line,
                fixed_line=updated_line,
                type_name=", ".join(types_fixed),  # Record all types fixed
            )
            fixes.append(fix)

        return fixes

    def apply_fixes(self, analysis: FileAnalysis) -> bool:
        """Apply fixes to a file."""
        if not analysis.fixes:
            return True

        try:
            content = analysis.file_path.read_text()
            lines = content.split("\n")

            # Apply fixes (in reverse order to maintain line numbers)
            for fix in sorted(
                analysis.fixes, key=lambda f: f.line_number, reverse=True
            ):
                if fix.line_number <= len(lines):
                    lines[fix.line_number - 1] = fix.fixed_line

            # Write back
            analysis.file_path.write_text("\n".join(lines))
            return True

        except Exception as e:
            analysis.errors.append(f"Error applying fixes: {e}")
            return False

    def scan_all_files(self) -> None:
        """Scan all Python files in the protocols directory."""
        protocols_dir = self.root_dir / "src" / "omnibase_spi" / "protocols"

        for py_file in protocols_dir.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue

            analysis = self.analyze_file(py_file)
            self.analyses.append(analysis)

    def generate_report(self) -> str:
        """Generate comprehensive fix report."""
        total_files = len(self.analyses)
        files_with_fixes = sum(1 for a in self.analyses if a.fixes)
        total_fixes = sum(len(a.fixes) for a in self.analyses)
        files_with_errors = sum(1 for a in self.analyses if a.errors)

        report = [
            "=" * 80,
            "FORWARD REFERENCE REMEDIATION REPORT",
            "=" * 80,
            "",
            f"Total files scanned: {total_files}",
            f"Files with fixes: {files_with_fixes}",
            f"Total fixes applied: {total_fixes}",
            f"Files with errors: {files_with_errors}",
            "",
        ]

        if files_with_fixes > 0:
            report.append("=" * 80)
            report.append("FILES WITH FIXES")
            report.append("=" * 80)
            report.append("")

            for analysis in self.analyses:
                if analysis.fixes:
                    report.append(f"\n{analysis.file_path.relative_to(self.root_dir)}")
                    report.append(
                        f"  Type-checking imports: {', '.join(sorted(analysis.type_checking_imports))}"
                    )
                    report.append(f"  Fixes applied: {len(analysis.fixes)}")

                    for fix in analysis.fixes:
                        report.append(
                            f"\n  Line {fix.line_number} - Fixed type: {fix.type_name}"
                        )
                        report.append(f"    Before: {fix.original_line.strip()}")
                        report.append(f"    After:  {fix.fixed_line.strip()}")

        if files_with_errors > 0:
            report.append("\n" + "=" * 80)
            report.append("FILES WITH ERRORS")
            report.append("=" * 80)
            report.append("")

            for analysis in self.analyses:
                if analysis.errors:
                    report.append(f"\n{analysis.file_path.relative_to(self.root_dir)}")
                    for error in analysis.errors:
                        report.append(f"  - {error}")

        report.append("\n" + "=" * 80)
        report.append("SUMMARY")
        report.append("=" * 80)
        report.append(f"✓ Scanned {total_files} files")
        report.append(f"✓ Applied {total_fixes} fixes across {files_with_fixes} files")

        if files_with_errors == 0:
            report.append("✓ No errors encountered")
        else:
            report.append(f"⚠ {files_with_errors} files had errors")

        return "\n".join(report)


def main():
    """Main entry point."""
    import sys

    if len(sys.argv) > 1:
        root_dir = Path(sys.argv[1])
    else:
        root_dir = Path(__file__).parent.parent

    print(f"Scanning protocols in: {root_dir}")
    print(f"Looking for TYPE_CHECKING forward reference issues...")
    print()

    fixer = ForwardReferenceFixer(root_dir)
    fixer.scan_all_files()

    # Apply fixes
    print(f"Found {sum(len(a.fixes) for a in fixer.analyses)} potential fixes")
    print("Applying fixes...")

    for analysis in fixer.analyses:
        if analysis.fixes:
            fixer.apply_fixes(analysis)

    # Generate report
    report = fixer.generate_report()
    print("\n" + report)

    # Save report
    report_path = root_dir / "FORWARD_REFERENCE_FIXES_REPORT.md"
    report_path.write_text(report)
    print(f"\nReport saved to: {report_path}")

    # Return exit code based on errors
    errors = sum(1 for a in fixer.analyses if a.errors)
    sys.exit(1 if errors > 0 else 0)


if __name__ == "__main__":
    main()
