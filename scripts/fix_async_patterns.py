#!/usr/bin/env python3
"""
Script to identify and fix async patterns in ONEX SPI protocols.

This script adds 'async' keyword to methods that clearly should be async
based on their names and functionality patterns.
"""

import ast
import os
import re
from pathlib import Path
from typing import List, Tuple


class AsyncPatternFixer:
    """Fixes async patterns in protocol files."""

    # Methods that should definitely be async based on their names
    ASYNC_METHOD_PATTERNS = [
        r"execute_",
        r"publish",
        r"subscribe",
        r"unsubscribe",
        r"connect",
        r"disconnect",
        r"register_",
        r"unregister_",
        r"validate_",
        r"discover_",
        r"save_",
        r"load_",
        r"persist_",
        r"fetch_",
        r"send_",
        r"receive_",
        r"process_",
        r"monitor_",
        r"health_check",
        r"create_",
        r"delete_",
        r"update_",
        r"query_",
        r"search_",
        r"start_",
        r"stop_",
        r"perform_",
        r"analyze_",
        r"scan_",
        r"check_",
        r"restore_",
        r"backup_",
        r"migrate_",
        r"import_",
        r"export_",
    ]

    def __init__(self, src_dir: str):
        self.src_dir = Path(src_dir)
        self.fixes_applied = 0
        self.files_modified = 0

    def should_be_async(
        self, method_name: str, file_content: str, line_number: int
    ) -> bool:
        """Determine if a method should be async based on patterns."""
        # Check if method name matches async patterns
        for pattern in self.ASYNC_METHOD_PATTERNS:
            if re.search(pattern, method_name):
                return True

        # Check if method is in certain protocol types that should be async
        if any(
            x in file_content
            for x in [
                "ProtocolMCP",
                "ProtocolWorkflow",
                "ProtocolEvent",
                "ProtocolValidation",
                "ProtocolKafka",
                "ProtocolDiscovery",
                "ProtocolRegistry",
                "ProtocolMonitor",
            ]
        ):
            # Methods in these protocols are likely I/O operations
            if any(
                x in method_name
                for x in ["get_", "set_", "list_", "find_", "read_", "write_", "apply_"]
            ):
                return True

        return False

    def fix_file(self, file_path: Path) -> Tuple[int, List[str]]:
        """Fix async patterns in a single file."""
        fixes_in_file = 0
        changes = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            original_content = content
            lines = content.split("\n")
            modified = False

            for i, line in enumerate(lines):
                # Match method definitions that are not already async
                method_match = re.match(r"^(\s*)def (\w+)\(", line.strip())
                if method_match and "async def" not in line:
                    indent = method_match.group(1)
                    method_name = method_match.group(2)

                    # Skip magic methods and properties
                    if (
                        method_name.startswith("_")
                        or "@property" in lines[max(0, i - 2) : i]
                    ):
                        continue

                    if self.should_be_async(method_name, content, i):
                        # Replace 'def' with 'async def'
                        old_line = lines[i]
                        new_line = line.replace("def ", "async def ", 1)
                        lines[i] = new_line

                        fixes_in_file += 1
                        changes.append(f"Line {i+1}: {method_name}() -> async")
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
        print("🔧 Fixing async patterns in ONEX SPI protocols...")
        print(f"📂 Scanning: {self.src_dir}")

        protocol_files = list(self.src_dir.rglob("protocol_*.py"))
        print(f"📄 Found {len(protocol_files)} protocol files")

        total_changes = []

        for file_path in protocol_files:
            if file_path.name.endswith("_types.py"):
                continue  # Skip type files

            fixes, changes = self.fix_file(file_path)
            self.fixes_applied += fixes

            if changes:
                print(f"\n✅ {file_path.relative_to(self.src_dir)}")
                for change in changes[:5]:  # Show first 5 changes
                    print(f"   • {change}")
                if len(changes) > 5:
                    print(f"   • ... and {len(changes) - 5} more")

                total_changes.extend(changes)

        print(f"\n📊 Summary:")
        print(f"   • Files modified: {self.files_modified}")
        print(f"   • Methods made async: {self.fixes_applied}")

        if self.fixes_applied > 0:
            print(f"\n✨ Successfully fixed {self.fixes_applied} async patterns!")
        else:
            print("\n💡 No async patterns needed fixing.")


def main() -> int:
    """Main entry point."""
    script_dir = Path(__file__).parent
    src_dir = script_dir.parent / "src" / "omnibase_spi" / "protocols"

    if not src_dir.exists():
        print(f"❌ Source directory not found: {src_dir}")
        return 1

    fixer = AsyncPatternFixer(str(src_dir))
    fixer.fix_protocols()

    return 0


if __name__ == "__main__":
    exit(main())
