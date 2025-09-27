#!/usr/bin/env python3
"""
Script to fix missing Path imports in protocol files.

Scans protocol files for Path usage and ensures the import is present.
"""

import os
import re
from pathlib import Path as PathlibPath
from typing import List, Tuple


class PathImportFixer:
    """Fixes missing Path imports in protocol files."""

    def __init__(self, src_dir: str):
        self.src_dir = PathlibPath(src_dir)
        self.fixes_applied = 0
        self.files_modified = 0

    def fix_file(self, file_path: PathlibPath) -> Tuple[int, List[str]]:
        """Fix Path imports in a single file."""
        fixes_in_file = 0
        changes = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check if file uses Path but doesn't import it
            if (
                ": Path" not in content
                and "-> Path" not in content
                and "Path |" not in content
            ):
                return 0, []

            # Check if pathlib.Path is already imported
            if "from pathlib import Path" in content:
                return 0, []  # Already imported

            # Find appropriate place to add the import
            lines = content.split("\n")
            modified = False

            # Find the first import line or after the docstring
            import_line_index = -1

            for i, line in enumerate(lines):
                if line.strip().startswith(
                    "from typing import"
                ) or line.strip().startswith("import "):
                    import_line_index = i
                    break
                elif line.strip().startswith('"""') and '"""' in line[3:]:
                    # Single line docstring
                    import_line_index = i + 1
                    break
                elif line.strip().startswith('"""'):
                    # Multi-line docstring, find the end
                    for j in range(i + 1, len(lines)):
                        if '"""' in lines[j]:
                            import_line_index = j + 1
                            break
                    break

            if import_line_index >= 0:
                # Insert Path import before the first import or after docstring
                lines.insert(import_line_index, "from pathlib import Path")
                fixes_in_file += 1
                changes.append(f"Added: from pathlib import Path")
                modified = True

            if modified:
                new_content = "\n".join(lines)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                self.files_modified += 1

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

        return fixes_in_file, changes

    def fix_protocols(self) -> None:
        """Fix all protocol files in the source directory."""
        print("🔧 Fixing missing Path imports...")
        print(f"📂 Scanning: {self.src_dir}")

        protocol_files = list(self.src_dir.rglob("protocol_*.py"))
        print(f"📄 Found {len(protocol_files)} protocol files")

        total_changes = []

        for file_path in protocol_files:
            fixes, changes = self.fix_file(file_path)
            self.fixes_applied += fixes

            if changes:
                print(f"\n✅ {file_path.relative_to(self.src_dir)}")
                for change in changes:
                    print(f"   • {change}")

                total_changes.extend(changes)

        print(f"\n📊 Summary:")
        print(f"   • Files modified: {self.files_modified}")
        print(f"   • Path imports added: {self.fixes_applied}")

        if self.fixes_applied > 0:
            print(f"\n✨ Successfully fixed {self.fixes_applied} Path import issues!")
        else:
            print("\n💡 No Path import issues found.")


def main() -> int:
    """Main entry point."""
    script_dir = PathlibPath(__file__).parent
    src_dir = script_dir.parent / "src" / "omnibase_spi" / "protocols"

    if not src_dir.exists():
        print(f"❌ Source directory not found: {src_dir}")
        return 1

    fixer = PathImportFixer(str(src_dir))
    fixer.fix_protocols()

    return 0


if __name__ == "__main__":
    exit(main())
