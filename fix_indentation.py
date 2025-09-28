#!/usr/bin/env python3
"""
Fix indentation issues in protocol files that may have been created during auto-fixing.
"""
import re
from pathlib import Path
from typing import List, Tuple

def fix_indentation_issues(file_path: Path) -> Tuple[bool, List[str]]:
    """
    Fix common indentation issues in protocol files.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        fixes_applied = []
        lines = content.split('\n')

        # Look for functions/properties that are not properly indented
        for i, line in enumerate(lines):
            stripped = line.strip()

            # Look for function definitions that should be indented (inside a class)
            if (stripped.startswith('def ') or stripped.startswith('async def ')) and not line.startswith('    '):
                # Check if we're inside a class (look backwards for class definition)
                in_class = False
                for j in range(i-1, max(0, i-20), -1):
                    prev_line = lines[j].strip()
                    if prev_line.startswith('class ') and prev_line.endswith(':'):
                        in_class = True
                        break
                    elif prev_line.startswith('class ') or prev_line.startswith('def ') or prev_line.startswith('async def '):
                        break

                if in_class:
                    lines[i] = '    ' + stripped
                    fixes_applied.append(f"Fixed indentation for {stripped.split('(')[0]}")

            # Look for @property decorators that should be indented
            elif stripped == '@property' and not line.startswith('    '):
                # Check if we're inside a class
                in_class = False
                for j in range(i-1, max(0, i-10), -1):
                    prev_line = lines[j].strip()
                    if prev_line.startswith('class ') and prev_line.endswith(':'):
                        in_class = True
                        break
                    elif prev_line.startswith('class ') or prev_line.startswith('def ') or prev_line.startswith('async def '):
                        break

                if in_class:
                    lines[i] = '    @property'
                    fixes_applied.append(f"Fixed indentation for @property decorator")

        if fixes_applied:
            content = '\n'.join(lines)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, fixes_applied

        return False, []

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False, []

def main():
    """Fix indentation issues in protocol files."""
    src_dir = Path("src")

    protocol_files = []
    for py_file in src_dir.rglob("*.py"):
        if (py_file.name.startswith("protocol_") and
            not py_file.name.startswith("test_") and
            "__pycache__" not in str(py_file)):
            protocol_files.append(py_file)

    print("🔧 Fixing indentation issues...")

    total_files_changed = 0
    total_fixes = 0

    for py_file in protocol_files:
        changed, fixes = fix_indentation_issues(py_file)
        if changed:
            total_files_changed += 1
            total_fixes += len(fixes)
            print(f"✅ Fixed {py_file.name}: {len(fixes)} indentation fixes")

    print(f"\n📊 Summary:")
    print(f"   Files processed: {len(protocol_files)}")
    print(f"   Files changed: {total_files_changed}")
    print(f"   Total fixes applied: {total_fixes}")

if __name__ == "__main__":
    main()