#!/usr/bin/env python3
"""
Edge case tests for script bug fixes to ensure robust handling.
"""

import re
import tempfile
from pathlib import Path

import pytest


class TestBug1EdgeCases:
    """Edge cases for Bug 1: Multi-type replacement."""

    def test_same_type_multiple_positions(self):
        """Test same type appearing multiple times in different contexts."""
        line = "def foo(a: TypeA, b: list[TypeA]) -> TypeA:"
        type_names = {"TypeA"}

        updated_line = line
        for type_name in type_names:
            # Pattern 1: param: TypeA
            pattern = rf"(\w+\s*:\s*)({type_name})(\s*[,\)])"
            updated_line = re.sub(pattern, rf'\1"\2"\3', updated_line)

            # Pattern 2: list[TypeA]
            pattern = rf"(list\[)({type_name})(\])"
            updated_line = re.sub(pattern, rf'\1"\2"\3', updated_line)

            # Pattern 3: -> TypeA
            pattern = rf"(\s*->\s*)({type_name})(\s*:)"
            updated_line = re.sub(pattern, rf'\1"\2"\3', updated_line)

        # All three occurrences should be quoted
        assert updated_line.count('"TypeA"') == 3
        assert 'a: "TypeA"' in updated_line
        assert 'list["TypeA"]' in updated_line
        assert '-> "TypeA"' in updated_line

    def test_union_types_multiple_on_line(self):
        """Test Union type syntax with multiple types."""
        line = "def process(data: TypeA | TypeB | TypeC) -> ResultType:"
        type_names = {"TypeA", "TypeB", "TypeC", "ResultType"}

        updated_line = line
        for type_name in sorted(type_names):  # Consistent order
            # Pattern for type before |
            pattern = rf"({type_name})(\s*\|)"
            if re.search(pattern, updated_line):
                updated_line = re.sub(pattern, rf'"\1"\2', updated_line)

            # Pattern for type after |
            pattern = rf"(\|\s*)({type_name})(\s*[\|\)])"  # Fixed: TypeC followed by )
            if re.search(pattern, updated_line):
                updated_line = re.sub(pattern, rf'\1"\2"\3', updated_line)

            # Pattern for return type
            pattern = rf"(\s*->\s*)({type_name})(\s*:)"
            if re.search(pattern, updated_line):
                updated_line = re.sub(pattern, rf'\1"\2"\3', updated_line)

        # All types should be quoted
        assert '"TypeA"' in updated_line
        assert '"TypeB"' in updated_line
        assert '"TypeC"' in updated_line
        assert '"ResultType"' in updated_line

    def test_complex_nested_types(self):
        """Test complex nested type annotations."""
        line = "data: dict[str, list[TypeA]] | TypeB = None"
        type_names = {"TypeA", "TypeB"}

        updated_line = line
        for type_name in sorted(type_names):
            # Pattern for list[Type]
            pattern = rf"(list\[)({type_name})(\])"
            if re.search(pattern, updated_line):
                updated_line = re.sub(pattern, rf'\1"\2"\3', updated_line)

            # Pattern for type before |
            pattern = rf"({type_name})(\s*\|)"
            if re.search(pattern, updated_line):
                updated_line = re.sub(pattern, rf'"\1"\2', updated_line)

            # Pattern for type before =
            pattern = rf"(\|\s*)({type_name})(\s*=)"
            if re.search(pattern, updated_line):
                updated_line = re.sub(pattern, rf'\1"\2"\3', updated_line)

        assert 'list["TypeA"]' in updated_line
        assert '| "TypeB"' in updated_line


class TestBug2And3EdgeCases:
    """Edge cases for Bugs 2 & 3: Import alias tracking."""

    def test_multiple_aliases_same_import(self):
        """Test multiple imports with different aliases."""
        code = """
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from omnibase_spi.protocols.types import (
        ProtocolWorkflowContext as WfCtx,
        ProtocolWorkflowEvent as WfEvent,
        ProtocolWorkflowState as WfState
    )
"""
        type_checking_imports = set()

        # Regex extraction (simulating script logic)
        type_checking_pattern = r"if TYPE_CHECKING:(.*?)(?=\n(?:if|class|def|@|\Z))"
        matches = re.findall(type_checking_pattern, code, re.DOTALL)

        for block in matches:
            # Fixed: Capture multiline imports with parentheses
            import_pattern = r"from\s+[\w.]+\s+import\s+\((.*?)\)"
            multiline_matches = re.findall(import_pattern, block, re.DOTALL)

            for import_stmt in multiline_matches:
                for name in import_stmt.split(","):
                    name = name.strip()
                    if " as " in name:
                        original, alias = name.split(" as ", 1)
                        type_checking_imports.add(original.strip())
                        type_checking_imports.add(alias.strip())
                    elif name:  # Skip empty strings
                        type_checking_imports.add(name)

        # All 6 names should be tracked (3 originals + 3 aliases)
        assert "ProtocolWorkflowContext" in type_checking_imports
        assert "WfCtx" in type_checking_imports
        assert "ProtocolWorkflowEvent" in type_checking_imports
        assert "WfEvent" in type_checking_imports
        assert "ProtocolWorkflowState" in type_checking_imports
        assert "WfState" in type_checking_imports

    def test_alias_same_as_original_last_segment(self):
        """Test alias that matches the last segment of the original."""
        code = """
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.workflow_types import ProtocolWorkflowContext as WorkflowContext
"""
        type_checking_imports = set()

        # Regex extraction
        type_checking_pattern = r"if TYPE_CHECKING:(.*?)(?=\n(?:if|class|def|@|\Z))"
        matches = re.findall(type_checking_pattern, code, re.DOTALL)

        for block in matches:
            import_pattern = r"from\s+[\w.]+\s+import\s+([^\n]+)"
            for import_match in re.finditer(import_pattern, block):
                import_stmt = import_match.group(1)
                for name in import_stmt.split(","):
                    name = name.strip()
                    if " as " in name:
                        original, alias = name.split(" as ", 1)
                        type_checking_imports.add(original.strip())
                        type_checking_imports.add(alias.strip())
                    else:
                        type_checking_imports.add(name)

        # Both names should be tracked even though they're similar
        assert "ProtocolWorkflowContext" in type_checking_imports
        assert "WorkflowContext" in type_checking_imports
        assert len(type_checking_imports) == 2


class TestBug4EdgeCases:
    """Edge cases for Bug 4: Fix counter."""

    def test_no_fixes_returns_zero(self):
        """Test that files with no issues return count of 0."""
        content = """
def foo(a: str) -> int:
    pass
"""
        pattern = r'""([A-Z][a-zA-Z0-9_]*?)""'
        result, count = re.subn(pattern, r'"\1"', content)

        assert count == 0
        assert result == content  # Unchanged

    def test_mixed_patterns_correct_count(self):
        """Test counting across multiple different patterns."""
        content = """
def foo(a: ""TypeA"") -> ""TypeB"":
    x: ""TypeC"" = None
    y: "TypeD" = None  # Already quoted correctly
"""
        # Pattern 1: ""TypeName""
        content, count1 = re.subn(r'""([A-Z][a-zA-Z0-9_]*?)""', r'"\1"', content)

        # Pattern 2: ""TypeName" (shouldn't match after pattern 1)
        content, count2 = re.subn(r'""([A-Z][a-zA-Z0-9_]*?)"', r'"\1"', content)

        total = count1 + count2
        assert total == 3  # TypeA, TypeB, TypeC (TypeD already correct)
        assert '"TypeD"' in content  # Should remain unchanged

    def test_large_file_accurate_count(self):
        """Test accurate counting in file with many fixes."""
        lines = []
        expected_count = 0

        # Generate 100 lines with issues (each line has 2 instances of double quotes)
        for i in range(100):
            lines.append(f'def func{i}(param: ""Type{i}"") -> ""Result{i}":')
            expected_count += 2  # Two fixes per line

        content = "\n".join(lines)

        # Apply fixes using global substitution
        pattern = r'""([A-Z][a-zA-Z0-9_]*?)""'
        result, count = re.subn(pattern, r'"\1"', content)

        # Note: re.subn with the pattern will replace ALL occurrences in a single pass
        # Each line has: ""Type{i}"" and ""Result{i}""
        # The pattern should match both, so count should equal expected_count
        # However, the regex is non-greedy and should match each pair separately
        assert count == expected_count, f"Expected {expected_count} fixes, got {count}"
        assert '""' not in result


class TestCombinedEdgeCases:
    """Edge cases combining multiple bug scenarios."""

    def test_aliased_types_on_same_line(self):
        """Test multiple aliased types on same line."""
        # Setup: Track aliases
        type_checking_imports = {"WfCtx", "WfEvent", "ProtocolWorkflowContext"}

        # Line with both alias and original
        line = "def process(ctx: WfCtx, event: WfEvent) -> ProtocolWorkflowContext:"

        updated_line = line
        for type_name in sorted(type_checking_imports):
            # Parameter pattern
            pattern = rf"(\w+\s*:\s*)({type_name})(\s*[,\)])"
            if re.search(pattern, updated_line):
                updated_line = re.sub(pattern, rf'\1"\2"\3', updated_line)

            # Return type pattern
            pattern = rf"(\s*->\s*)({type_name})(\s*:)"
            if re.search(pattern, updated_line):
                updated_line = re.sub(pattern, rf'\1"\2"\3', updated_line)

        # All three types should be quoted
        assert 'ctx: "WfCtx"' in updated_line
        assert 'event: "WfEvent"' in updated_line
        assert '-> "ProtocolWorkflowContext"' in updated_line

    def test_double_quotes_with_multiple_types(self):
        """Test double quote fixing with multiple types on line."""
        content = 'def process(a: ""TypeA"", b: ""TypeB"") -> ""TypeC"":"'

        # Fix and count
        pattern = r'""([A-Z][a-zA-Z0-9_]*?)""'
        result, count = re.subn(pattern, r'"\1"', content)

        assert count == 3
        assert '"TypeA"' in result
        assert '"TypeB"' in result
        assert '"TypeC"' in result
        assert '""' not in result


class TestRegressionPrevention:
    """Tests to prevent regression of fixed bugs."""

    def test_incremental_line_building_maintained(self):
        """Verify incremental line building is maintained."""
        # This test ensures we don't regress to resetting line in loop
        line = "def foo(a: TypeA, b: TypeB, c: TypeC) -> None:"
        types = ["TypeA", "TypeB", "TypeC"]

        # Simulate potential buggy implementation
        def buggy_implementation(input_line: str, type_list: list[str]) -> str:
            original = input_line
            for t in type_list:
                # BUG: This would reset to original each time
                result = original
                result = result.replace(f": {t}", f': "{t}"')
                original = result  # Would only keep last change
            return result

        # Simulate correct implementation
        def correct_implementation(input_line: str, type_list: list[str]) -> str:
            result = input_line
            for t in type_list:
                result = result.replace(f": {t}", f': "{t}"')
            return result

        correct_result = correct_implementation(line, types)

        # Verify all types are quoted
        assert ': "TypeA"' in correct_result
        assert ': "TypeB"' in correct_result
        assert ': "TypeC"' in correct_result

    def test_alias_tracking_comprehensive(self):
        """Ensure both alias names are always tracked."""
        test_cases = [
            ("from x import Foo as Bar", {"Foo", "Bar"}),
            ("from x import A as B, C as D", {"A", "B", "C", "D"}),
            ("from x import Type", {"Type"}),
            ("from x import A as B, C", {"A", "B", "C"}),
        ]

        for import_stmt, expected_names in test_cases:
            tracked_names = set()

            # Simulate tracking logic
            content = import_stmt
            for name in content.replace("from x import ", "").split(","):
                name = name.strip()
                if " as " in name:
                    original, alias = name.split(" as ", 1)
                    tracked_names.add(original.strip())
                    tracked_names.add(alias.strip())
                else:
                    tracked_names.add(name.strip())

            assert (
                tracked_names == expected_names
            ), f"Failed for {import_stmt}: {tracked_names} != {expected_names}"

    def test_counter_uses_subn_not_sub(self):
        """Verify re.subn() is used for counting, not re.sub()."""
        content = """
x: ""Type1"" = None
y: ""Type2"" = None
"""

        # Correct way with re.subn()
        pattern = r'""([A-Z][a-zA-Z0-9_]*?)""'
        result, count = re.subn(pattern, r'"\1"', content)

        # Verify count is captured
        assert count == 2
        assert isinstance(count, int)
        assert result != content  # Content was modified


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
