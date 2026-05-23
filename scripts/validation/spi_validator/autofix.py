# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""Auto-fix engine for supported SPI violations."""

from __future__ import annotations

from collections import defaultdict

from .config import ValidationConfig
from .models import ProtocolViolation


class AutoFixEngine:
    def __init__(self, config: ValidationConfig):
        self.config = config
        self.fixes_applied = 0

    def apply_auto_fixes(
        self, violations: list[ProtocolViolation]
    ) -> tuple[list[ProtocolViolation], int]:
        fixed_violations: list[ProtocolViolation] = []
        fixes_applied = 0

        violations_by_file: dict[str, list[ProtocolViolation]] = defaultdict(list)
        for violation in violations:
            if violation.auto_fix_available:
                violations_by_file[violation.file_path].append(violation)
            else:
                fixed_violations.append(violation)

        for file_path, file_violations in violations_by_file.items():
            try:
                file_fixes = self._apply_file_fixes(file_path, file_violations)
                fixes_applied += file_fixes
                if file_fixes > 0:
                    fixed_violations.extend(file_violations[file_fixes:])
                else:
                    fixed_violations.extend(file_violations)
            except Exception as e:
                print(f"Warning: Failed to apply auto-fixes to {file_path}: {e}")
                fixed_violations.extend(file_violations)

        self.fixes_applied = fixes_applied
        return fixed_violations, fixes_applied

    def _apply_file_fixes(
        self, file_path: str, violations: list[ProtocolViolation]
    ) -> int:
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
            original = content
            fixes_applied = 0

            for violation in sorted(
                violations, key=lambda v: v.line_number, reverse=True
            ):
                if violation.rule_id == "SPI003":
                    content, fixed = self._fix_missing_runtime_checkable(
                        content, violation
                    )
                elif violation.rule_id == "SPI004":
                    content, fixed = self._fix_concrete_implementation(
                        content, violation
                    )
                elif violation.rule_id == "SPI005":
                    content, fixed = self._fix_sync_to_async(content, violation)
                else:
                    fixed = False
                if fixed:
                    fixes_applied += 1

            if content != original:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
            return fixes_applied
        except Exception as e:
            print(f"Error applying fixes to {file_path}: {e}")
            return 0

    def _fix_missing_runtime_checkable(
        self, content: str, violation: ProtocolViolation
    ) -> tuple[str, bool]:
        lines = content.split("\n")
        target_line = violation.line_number - 1
        if target_line < len(lines):
            line = lines[target_line]
            if "class " in line and "Protocol" in line:
                indent = len(line) - len(line.lstrip())
                lines.insert(target_line, " " * indent + "@runtime_checkable")
                return "\n".join(lines), True
        return content, False

    def _fix_concrete_implementation(
        self, content: str, violation: ProtocolViolation
    ) -> tuple[str, bool]:
        lines = content.split("\n")
        target_line = violation.line_number - 1
        if target_line >= len(lines):
            return content, False

        body_start = target_line + 1
        if body_start < len(lines):
            line = lines[body_start].strip()
            if line.startswith('"""') or line.startswith("'''"):
                quote = line[:3]
                if not line.endswith(quote) or len(line) <= 3:
                    body_start += 1
                    while body_start < len(lines) and not lines[
                        body_start
                    ].strip().endswith(quote):
                        body_start += 1
                    body_start += 1

        if body_start < len(lines):
            body_indent = len(lines[target_line]) - len(lines[target_line].lstrip()) + 4
            ellipsis_line = " " * body_indent + "..."
            body_end = body_start
            while body_end < len(lines) and (
                not lines[body_end].strip()
                or len(lines[body_end]) - len(lines[body_end].lstrip()) > body_indent
                or lines[body_end].strip().startswith("#")
            ):
                body_end += 1
            lines[body_start:body_end] = [ellipsis_line]
            return "\n".join(lines), True
        return content, False

    def _fix_sync_to_async(
        self, content: str, violation: ProtocolViolation
    ) -> tuple[str, bool]:
        lines = content.split("\n")
        target_line = violation.line_number - 1
        if target_line < len(lines):
            line = lines[target_line]
            if "def " in line and "async def " not in line:
                lines[target_line] = line.replace("def ", "async def ")
                return "\n".join(lines), True
        return content, False
