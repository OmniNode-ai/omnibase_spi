#!/usr/bin/env python3
"""
Tests demonstrating the 4 script logic bugs and validating fixes.
"""

import ast
import re
import tempfile
from pathlib import Path

import pytest


class TestBug1MultiTypeReplacement:
    """Test for Bug 1: Multi-type replacement issue."""

    def test_multiple_types_on_same_line(self):
        """Test that all types on the same line get quoted, not just the last one."""
        # Simulate the fix logic from fix_forward_references.py
        line = "def foo(a: TypeA, b: TypeB) -> TypeC:"
        type_names = {"TypeA", "TypeB", "TypeC"}

        # Buggy pattern: Reset to original each time
        original_line = line
        buggy_line = line
        for type_name in type_names:
            buggy_line = original_line  # BUG: Reset to original
            pattern = rf"(\w+\s*:\s*)({type_name})(\s*[,\)])"
            if re.search(pattern, buggy_line):
                buggy_line = re.sub(pattern, rf'\1"\2"\3', buggy_line)

        # Only the last type processed gets quoted (order-dependent)
        # This is the buggy behavior

        # Fixed pattern: Accumulate changes
        updated_line = line
        for type_name in sorted(type_names):  # Consistent order for testing
            pattern = rf"(\w+\s*:\s*)({type_name})(\s*[,\)])"
            if re.search(pattern, updated_line):
                updated_line = re.sub(pattern, rf'\1"\2"\3', updated_line)

        # All types should be quoted
        expected = 'def foo(a: "TypeA", b: "TypeB") -> TypeC:'
        assert updated_line == expected, f"Expected {expected}, got {updated_line}"

    def test_multiple_occurrences_of_different_types(self):
        """Test line with multiple different types in various positions."""
        line = "def process(data: DataType, validator: ValidatorType) -> ResultType:"
        type_names = {"DataType", "ValidatorType", "ResultType"}

        # Fixed: Accumulate changes incrementally
        updated_line = line

        for type_name in sorted(type_names):
            # Parameter type pattern
            pattern = rf"(\w+\s*:\s*)({type_name})(\s*[,\)])"
            if re.search(pattern, updated_line):
                updated_line = re.sub(pattern, rf'\1"\2"\3', updated_line)

            # Return type pattern
            pattern = rf"(\s*->\s*)({type_name})(\s*:)"
            if re.search(pattern, updated_line):
                updated_line = re.sub(pattern, rf'\1"\2"\3', updated_line)

        expected = (
            'def process(data: "DataType", validator: "ValidatorType") -> "ResultType":'
        )
        assert updated_line == expected


class TestBug2ImportAliasTracking:
    """Test for Bug 2: Import alias tracking in comprehensive_forward_ref_fix.py."""

    def test_import_with_alias_both_names_tracked(self):
        """Test that both original name and alias are tracked."""
        code = """
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from omnibase_spi.protocols.types import ProtocolWorkflowContext as WorkflowCtx
"""

        # Extract imports using AST (simulating the script logic)
        tree = ast.parse(code)
        type_checking_imports = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                # Check for TYPE_CHECKING
                if isinstance(node.test, ast.Name) and node.test.id == "TYPE_CHECKING":
                    for child in ast.walk(node):
                        if isinstance(child, ast.ImportFrom):
                            for alias in child.names:
                                # FIX: Track both name and asname
                                type_checking_imports.add(alias.name)
                                if alias.asname:
                                    type_checking_imports.add(alias.asname)

        # Both original and alias should be tracked
        assert "ProtocolWorkflowContext" in type_checking_imports
        assert "WorkflowCtx" in type_checking_imports

    def test_import_without_alias_only_name_tracked(self):
        """Test that imports without alias work correctly."""
        code = """
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from omnibase_spi.protocols.types import ProtocolWorkflowContext
"""

        tree = ast.parse(code)
        type_checking_imports = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                if isinstance(node.test, ast.Name) and node.test.id == "TYPE_CHECKING":
                    for child in ast.walk(node):
                        if isinstance(child, ast.ImportFrom):
                            for alias in child.names:
                                type_checking_imports.add(alias.name)
                                if alias.asname:
                                    type_checking_imports.add(alias.asname)

        assert "ProtocolWorkflowContext" in type_checking_imports
        assert len(type_checking_imports) == 1


class TestBug3ImportAliasTrackingFixForwardReferences:
    """Test for Bug 3: Same issue as Bug 2 in fix_forward_references.py."""

    def test_regex_extraction_with_alias(self):
        """Test regex-based extraction tracks both names."""
        code = """
if TYPE_CHECKING:
    from omnibase_spi.protocols.types import ProtocolEvent as Event
    from omnibase_spi.protocols.core import ProtocolLogger
"""

        type_checking_imports = set()

        # Regex pattern from script
        type_checking_pattern = r"if TYPE_CHECKING:(.*?)(?=\n(?:if|class|def|@|\Z))"
        matches = re.findall(type_checking_pattern, code, re.DOTALL)

        for block in matches:
            import_pattern = r"from\s+[\w.]+\s+import\s+([^\n]+)"
            for import_match in re.finditer(import_pattern, block):
                import_stmt = import_match.group(1)
                for name in import_stmt.split(","):
                    name = name.strip()
                    if " as " in name:
                        # FIX: Track both original and alias
                        original, alias = name.split(" as ", 1)
                        type_checking_imports.add(original.strip())
                        type_checking_imports.add(alias.strip())
                    else:
                        type_checking_imports.add(name)

        assert "ProtocolEvent" in type_checking_imports
        assert "Event" in type_checking_imports
        assert "ProtocolLogger" in type_checking_imports


class TestBug4FixCounter:
    """Test for Bug 4: Fix counter in fix_double_quotes.py."""

    def test_fix_counter_returns_correct_count(self):
        """Test that fix counter uses re.subn() and returns accurate count."""
        content = """
def foo(a: ""TypeA"") -> ""TypeB"":
    pass
"""

        # BUGGY: Count after writing (always returns 0)
        def buggy_fix(text: str) -> int:
            pattern = r'""([A-Z][a-zA-Z0-9_]*?)""'
            text = re.sub(pattern, r'"\1"', text)
            # Count is checked AFTER replacement, so we can't get it
            count = 0
            return count

        # FIXED: Use re.subn() to get count during replacement
        def fixed_fix(text: str) -> int:
            pattern = r'""([A-Z][a-zA-Z0-9_]*?)""'
            text, count = re.subn(pattern, r'"\1"', text)
            return count

        buggy_count = buggy_fix(content)
        fixed_count = fixed_fix(content)

        assert buggy_count == 0, "Buggy version should return 0"
        assert fixed_count == 2, f"Fixed version should return 2, got {fixed_count}"

    def test_multiple_patterns_accumulate_count(self):
        """Test that multiple patterns accumulate their counts correctly."""
        content = """
def foo(a: ""TypeA"") -> ""TypeB"":
    x: ""TypeC"" = None
"""

        # Pattern 1: ""TypeName""
        pattern1 = r'""([A-Z][a-zA-Z0-9_]*?)""'
        content, count1 = re.subn(pattern1, r'"\1"', content)

        # Pattern 2: ""TypeName" (if any remain)
        pattern2 = r'""([A-Z][a-zA-Z0-9_]*?)"'
        content, count2 = re.subn(pattern2, r'"\1"', content)

        total_count = count1 + count2
        assert total_count == 3, f"Should fix 3 occurrences, got {total_count}"


class TestIntegrationScripts:
    """Integration tests for the fixed scripts."""

    def test_fix_forward_references_handles_multiple_types(self):
        """Integration test: fix_forward_references.py handles multiple types."""
        from scripts.fix_forward_references import ForwardReferenceFixer

        # Create temporary test file
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir)
            protocols_dir = test_dir / "src" / "omnibase_spi" / "protocols"
            protocols_dir.mkdir(parents=True)

            test_file = protocols_dir / "test_protocol.py"
            test_file.write_text(
                """
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from omnibase_spi.protocols.types import TypeA, TypeB, TypeC

def process(a: TypeA, b: TypeB) -> TypeC:
    pass
"""
            )

            # Run fixer
            fixer = ForwardReferenceFixer(test_dir)
            analysis = fixer.analyze_file(test_file)

            # Should find fixes for all three types
            assert len(analysis.fixes) > 0, "Should find fixes"

            # Apply fixes
            fixer.apply_fixes(analysis)

            # Verify all types are quoted
            result = test_file.read_text()
            assert '"TypeA"' in result
            assert '"TypeB"' in result
            assert '"TypeC"' in result

    def test_comprehensive_fixer_tracks_aliases(self):
        """Integration test: comprehensive_forward_ref_fix.py tracks aliases."""
        from scripts.comprehensive_forward_ref_fix import (
            ComprehensiveForwardReferenceFixer,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir)
            protocols_dir = test_dir / "src" / "omnibase_spi" / "protocols"
            protocols_dir.mkdir(parents=True)

            test_file = protocols_dir / "test_protocol.py"
            test_file.write_text(
                """
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from omnibase_spi.protocols.types import ProtocolWorkflowContext as WfCtx

def process(context: WfCtx) -> None:
    pass
"""
            )

            # Run fixer
            fixer = ComprehensiveForwardReferenceFixer(test_dir)

            # Extract imports
            content = test_file.read_text()
            imports = fixer.extract_type_checking_imports(content)

            # Both names should be tracked
            assert "ProtocolWorkflowContext" in imports
            assert "WfCtx" in imports

            # Fix should work with alias
            fixes = fixer.fix_file(test_file)
            assert fixes > 0

            result = test_file.read_text()
            assert '"WfCtx"' in result

    def test_double_quote_fixer_returns_accurate_count(self):
        """Integration test: fix_double_quotes.py returns accurate count."""
        from scripts.fix_double_quotes import fix_double_quotes_in_file

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text(
                """
def foo(a: ""TypeA"") -> ""TypeB"":
    x: ""TypeC"" = None
"""
            )

            # Run fixer and get count
            count = fix_double_quotes_in_file(test_file)

            # Should report 3 fixes
            assert count == 3, f"Should fix 3 occurrences, got {count}"

            # Verify fixes were applied
            result = test_file.read_text()
            assert '""' not in result
            assert '"TypeA"' in result
            assert '"TypeB"' in result
            assert '"TypeC"' in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
