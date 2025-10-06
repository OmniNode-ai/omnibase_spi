#!/usr/bin/env python3
"""
Comprehensive Forward Reference Fixer for omnibase-spi

Properly fixes forward reference issues by:
1. Identifying types imported under TYPE_CHECKING
2. Finding unquoted usages (but not already quoted ones)
3. Converting them to quoted forward references
4. Fixing any mismatched quotes from previous runs
"""

import ast
import re
from pathlib import Path
from typing import Set


class ComprehensiveForwardReferenceFixer:
    """Fixes forward reference issues comprehensively."""

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.fixes_applied = 0
        self.files_fixed = 0

    def extract_type_checking_imports(self, content: str) -> Set[str]:
        """Extract all type names imported under TYPE_CHECKING blocks."""
        type_checking_imports = set()

        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.If):
                    # Check if this is a TYPE_CHECKING block
                    if self._is_type_checking_block(node):
                        # Extract imports from this block
                        for child in ast.walk(node):
                            if isinstance(child, ast.ImportFrom):
                                for alias in child.names:
                                    type_checking_imports.add(alias.name)

        except SyntaxError:
            # Fallback to regex if AST parsing fails
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
                # Handle "from x import A, B, C"
                names = [
                    name.strip().split(" as ")[0] for name in import_stmt.split(",")
                ]
                type_checking_imports.update(names)

        return type_checking_imports

    def fix_file(self, file_path: Path) -> int:
        """Fix forward reference issues in a single file. Returns number of fixes."""
        content = file_path.read_text()

        # First, fix any malformed quotes from previous runs
        # Pattern: "TypeName" | Something" -> "TypeName | Something"
        content = re.sub(
            r'"([A-Z][a-zA-Z0-9_]*?)"\s*\|\s*([^"]+?)"(?=\s*[=,\)])',
            r'"\1 | \2"',
            content,
        )

        # Extract TYPE_CHECKING imports
        type_checking_imports = self.extract_type_checking_imports(content)

        if not type_checking_imports:
            return 0

        fixes = 0
        lines = content.split("\n")
        new_lines = []

        for line in lines:
            # Skip import lines and comments
            stripped = line.strip()
            if (
                stripped.startswith("#")
                or stripped.startswith("import ")
                or stripped.startswith("from ")
            ):
                new_lines.append(line)
                continue

            new_line = line
            for type_name in type_checking_imports:
                # Escape special regex characters in type name
                escaped_type_name = re.escape(type_name)

                # Only fix if the type is not already quoted
                if (
                    f'"{type_name}"' not in new_line
                    and f"'{type_name}'" not in new_line
                ):
                    # Return type annotation: -> TypeName
                    pattern = r"(\s*->\s*)(" + escaped_type_name + r")(\s*[:\)])"
                    if re.search(pattern, new_line):
                        new_line = re.sub(pattern, r'\1"\2"\3', new_line)
                        fixes += 1
                        continue

                    # Return type annotation with Union: -> TypeName |
                    pattern = r"(\s*->\s*)(" + escaped_type_name + r")(\s*\|)"
                    if re.search(pattern, new_line):
                        new_line = re.sub(pattern, r'\1"\2"\3', new_line)
                        fixes += 1
                        continue

                    # Parameter type: param: TypeName
                    pattern = r"(\w+\s*:\s*)(" + escaped_type_name + r")(\s*[,=\)])"
                    if re.search(pattern, new_line):
                        new_line = re.sub(pattern, r'\1"\2"\3', new_line)
                        fixes += 1
                        continue

                    # Parameter type with Union: param: TypeName |
                    pattern = r"(\w+\s*:\s*)(" + escaped_type_name + r")(\s*\|)"
                    if re.search(pattern, new_line):
                        new_line = re.sub(pattern, r'\1"\2"\3', new_line)
                        fixes += 1
                        continue

                    # List/Dict types: list[TypeName]
                    pattern = r"(list\[)(" + escaped_type_name + r")(\])"
                    if re.search(pattern, new_line):
                        new_line = re.sub(pattern, r'\1"\2"\3', new_line)
                        fixes += 1
                        continue

                    # Dict value type: dict[str, TypeName]
                    pattern = r"(dict\[[^,]+,\s*)(" + escaped_type_name + r")(\])"
                    if re.search(pattern, new_line):
                        new_line = re.sub(pattern, r'\1"\2"\3', new_line)
                        fixes += 1
                        continue

                    # Union suffix: | TypeName
                    pattern = r"(\|\s*)(" + escaped_type_name + r")(\s*[,\)])"
                    if re.search(pattern, new_line):
                        new_line = re.sub(pattern, r'\1"\2"\3', new_line)
                        fixes += 1
                        continue

                    # Variable annotation: var: TypeName =
                    pattern = r"^(\s*\w+)\s*:\s*(" + escaped_type_name + r")(\s*=)"
                    if re.search(pattern, new_line):
                        new_line = re.sub(pattern, r'\1: "\2"\3', new_line)
                        fixes += 1
                        continue

            new_lines.append(new_line)

        if fixes > 0:
            file_path.write_text("\n".join(new_lines))
            self.files_fixed += 1
            self.fixes_applied += fixes

        return fixes

    def fix_all_files(self) -> None:
        """Fix all Python files in the protocols directory."""
        protocols_dir = self.root_dir / "src" / "omnibase_spi" / "protocols"

        files_processed = []
        for py_file in protocols_dir.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue

            fixes = self.fix_file(py_file)
            if fixes > 0:
                files_processed.append((py_file, fixes))
                print(
                    f"✓ Fixed {fixes:3d} issues in {py_file.relative_to(self.root_dir)}"
                )

        print(f"\n{'='*80}")
        print(f"COMPREHENSIVE FORWARD REFERENCE FIX COMPLETE")
        print(f"{'='*80}")
        print(f"✓ Files fixed: {self.files_fixed}")
        print(f"✓ Total fixes applied: {self.fixes_applied}")


def main():
    """Main entry point."""
    import sys

    if len(sys.argv) > 1:
        root_dir = Path(sys.argv[1])
    else:
        root_dir = Path(__file__).parent.parent

    print(f"Comprehensive Forward Reference Fixer")
    print(f"Root directory: {root_dir}")
    print(f"{'='*80}\n")

    fixer = ComprehensiveForwardReferenceFixer(root_dir)
    fixer.fix_all_files()


if __name__ == "__main__":
    main()
