#!/usr/bin/env python3
"""
Script to fix missing runtime_checkable imports in protocol files.

Scans protocol files for @runtime_checkable decorators and ensures the import is present.
"""

import re
from pathlib import Path
from typing import List, Tuple


class RuntimeCheckableImportFixer:
    """Fixes missing runtime_checkable imports in protocol files."""

    def __init__(self, src_dir: str):
        self.src_dir = Path(src_dir)
        self.fixes_applied = 0
        self.files_modified = 0

    def fix_file(self, file_path: Path) -> Tuple[int, List[str]]:
        """Fix runtime_checkable imports in a single file."""
        fixes_in_file = 0
        changes = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check if file has @runtime_checkable decorators
            if "@runtime_checkable" not in content:
                return 0, []

            # Check if runtime_checkable is already imported
            if "runtime_checkable" in content and "from typing import" in content:
                # Check if it's already in the typing import
                typing_import_pattern = r"from typing import ([^\\n]*)"
                typing_match = re.search(typing_import_pattern, content)
                if typing_match:
                    imports = typing_match.group(1)
                    if "runtime_checkable" in imports:
                        return 0, []  # Already imported

            # Find the typing import line and add runtime_checkable
            lines = content.split("\n")
            modified = False

            for i, line in enumerate(lines):
                # Look for typing import lines
                if (
                    line.strip().startswith("from typing import")
                    and "runtime_checkable" not in line
                ):
                    # Add runtime_checkable to the import
                    if line.endswith("\\"):
                        # Multi-line import, add it to the list
                        old_line = line
                        new_line = line.replace(
                            "from typing import",
                            "from typing import runtime_checkable, ",
                        )
                        lines[i] = new_line
                        fixes_in_file += 1
                        changes.append(
                            f"Line {i+1}: Added runtime_checkable to typing import"
                        )
                        modified = True
                        break
                    else:
                        # Single line import
                        old_line = line
                        # Add runtime_checkable to the import list
                        if ", " in line:
                            new_line = line.replace(
                                "from typing import ",
                                "from typing import runtime_checkable, ",
                            )
                        else:
                            new_line = line.replace(
                                "from typing import ",
                                "from typing import runtime_checkable, ",
                            )
                        lines[i] = new_line
                        fixes_in_file += 1
                        changes.append(
                            f"Line {i+1}: Added runtime_checkable to typing import"
                        )
                        modified = True
                        break

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
        print("🔧 Fixing missing runtime_checkable imports...")
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

        print("\n📊 Summary:")
        print(f"   • Files modified: {self.files_modified}")
        print(f"   • Import fixes applied: {self.fixes_applied}")

        if self.fixes_applied > 0:
            print(f"\n✨ Successfully fixed {self.fixes_applied} import issues!")
        else:
            print("\n💡 No runtime_checkable import issues found.")


def main() -> int:
    """Main entry point."""
    script_dir = Path(__file__).parent
    src_dir = script_dir.parent / "src" / "omnibase_spi" / "protocols"

    if not src_dir.exists():
        print(f"❌ Source directory not found: {src_dir}")
        return 1

    fixer = RuntimeCheckableImportFixer(str(src_dir))
    fixer.fix_protocols()

    return 0


if __name__ == "__main__":
    exit(main())
