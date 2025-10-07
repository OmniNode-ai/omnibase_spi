#!/usr/bin/env python3
"""
Test cases for script bug fixes.

Tests:
1. Multi-type replacement (Bug 1)
2. Import alias tracking (Bug 2)
3. Fix counter accuracy (Bug 3)
"""

import sys
import tempfile
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from comprehensive_forward_ref_fix import ComprehensiveForwardReferenceFixer
from fix_double_quotes import fix_double_quotes_in_file
from fix_forward_references import ForwardReferenceFixer


def test_multi_type_replacement() -> bool:
    """Test Bug 1: Multiple types on same line get quoted."""
    print("\n" + "=" * 80)
    print("TEST 1: Multi-type replacement")
    print("=" * 80)

    test_content = '''from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from omnibase_spi.protocols.types import TypeA, TypeB, TypeC

def foo(x: TypeA, y: TypeB) -> TypeC:
    """Function with multiple type annotations."""
    ...
'''

    with tempfile.TemporaryDirectory() as tmpdir_str:
        tmpdir = Path(tmpdir_str)
        src_dir = tmpdir / "src" / "omnibase_spi" / "protocols"
        src_dir.mkdir(parents=True)

        test_file = src_dir / "test_protocol.py"
        test_file.write_text(test_content)

        # Run fixer
        fixer = ForwardReferenceFixer(tmpdir)
        analysis = fixer.analyze_file(test_file)

        print(f"\nFound {len(analysis.fixes)} fix(es)")
        for fix in analysis.fixes:
            print(f"\nLine {fix.line_number}:")
            print(f"  Before: {fix.original_line.strip()}")
            print(f"  After:  {fix.fixed_line.strip()}")
            print(f"  Types:  {fix.type_name}")

        # Apply fixes
        fixer.apply_fixes(analysis)

        # Read result
        result = test_file.read_text()
        print("\nFinal result:")
        print(result)

        # Verify all types are quoted
        assert '"TypeA"' in result, "TypeA should be quoted"
        assert '"TypeB"' in result, "TypeB should be quoted"
        assert '"TypeC"' in result, "TypeC should be quoted"

        print("\n✓ All types correctly quoted on multi-type line")
        return True


def test_import_alias_tracking() -> bool:
    """Test Bug 2: Import aliases are tracked."""
    print("\n" + "=" * 80)
    print("TEST 2: Import alias tracking")
    print("=" * 80)

    test_content = '''from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from omnibase_spi.protocols.types import ProtocolWorkflowEvent as WorkflowEvent

def handle_event(event: WorkflowEvent) -> None:
    """Function using aliased type."""
    ...
'''

    with tempfile.TemporaryDirectory() as tmpdir_str:
        tmpdir = Path(tmpdir_str)
        src_dir = tmpdir / "src" / "omnibase_spi" / "protocols"
        src_dir.mkdir(parents=True)

        test_file = src_dir / "test_protocol.py"
        test_file.write_text(test_content)

        # Test AST-based extraction
        fixer = ForwardReferenceFixer(tmpdir)
        analysis = fixer.analyze_file(test_file)

        print(f"\nExtracted types: {analysis.type_checking_imports}")
        print(f"Found {len(analysis.fixes)} fix(es)")

        for fix in analysis.fixes:
            print(f"\nLine {fix.line_number}:")
            print(f"  Before: {fix.original_line.strip()}")
            print(f"  After:  {fix.fixed_line.strip()}")

        # Verify both original and alias are tracked
        assert (
            "ProtocolWorkflowEvent" in analysis.type_checking_imports
        ), "Original name should be tracked"
        assert (
            "WorkflowEvent" in analysis.type_checking_imports
        ), "Alias name should be tracked"

        # Apply fixes
        fixer.apply_fixes(analysis)
        result = test_file.read_text()

        print("\nFinal result:")
        print(result)

        # Verify alias is quoted
        assert '"WorkflowEvent"' in result, "Alias should be quoted"

        print("\n✓ Import alias correctly tracked and quoted")
        return True


def test_fix_counter_accuracy() -> bool:
    """Test Bug 3: Fix counter reports accurate numbers."""
    print("\n" + "=" * 80)
    print("TEST 3: Fix counter accuracy")
    print("=" * 80)

    test_content = '''from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from omnibase_spi.protocols.types import TypeName

# This has double quotes from a previous buggy run
def foo(x: ""TypeName"") -> ""TypeName"":
    """Function with double-quoted types."""
    var: ""TypeName"" = None
'''

    with tempfile.TemporaryDirectory() as tmpdir_str:
        tmpdir = Path(tmpdir_str)
        test_file = tmpdir / "test.py"
        test_file.write_text(test_content)

        # Run double quote fixer
        count = fix_double_quotes_in_file(test_file)

        print(f"\nFixes reported: {count}")

        # Read result
        result = test_file.read_text()
        print("\nFinal result:")
        print(result)

        # Verify counter is accurate (should be 3: one in param, one in return, one in var)
        assert count == 3, f"Expected 3 fixes, got {count}"

        # Verify no double quotes remain in type annotations (check the function definition line)
        import re

        # Look for double-quoted type names in annotations
        double_quote_pattern = r'""[A-Z][a-zA-Z0-9_]*?""'
        matches = re.findall(double_quote_pattern, result)
        assert (
            len(matches) == 0
        ), f"Double quotes should not remain in type annotations, found: {matches}"

        # Verify single quotes are present
        assert '"TypeName"' in result, "Single quotes should be present"

        print(f"\n✓ Fix counter correctly reported {count} fixes")
        return True


def test_comprehensive_fixer_alias() -> bool:
    """Test Bug 2 in comprehensive fixer."""
    print("\n" + "=" * 80)
    print("TEST 4: Comprehensive fixer import alias")
    print("=" * 80)

    test_content = '''from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from omnibase_spi.protocols.types import TypeA as AliasA, TypeB

def process(a: AliasA, b: TypeB) -> AliasA:
    """Function using both alias and original."""
    ...
'''

    with tempfile.TemporaryDirectory() as tmpdir_str:
        tmpdir = Path(tmpdir_str)
        src_dir = tmpdir / "src" / "omnibase_spi" / "protocols"
        src_dir.mkdir(parents=True)

        test_file = src_dir / "test_protocol.py"
        test_file.write_text(test_content)

        # Run comprehensive fixer
        fixer = ComprehensiveForwardReferenceFixer(tmpdir)
        imports = fixer.extract_type_checking_imports(test_content)

        print(f"\nExtracted types: {imports}")

        # Verify all names are tracked
        assert "TypeA" in imports, "Original TypeA should be tracked"
        assert "AliasA" in imports, "Alias AliasA should be tracked"
        assert "TypeB" in imports, "TypeB should be tracked"

        # Apply fixes
        count = fixer.fix_file(test_file)

        print(f"\nFixes applied: {count}")

        result = test_file.read_text()
        print("\nFinal result:")
        print(result)

        # Verify types are quoted
        assert '"AliasA"' in result, "Alias should be quoted"
        assert '"TypeB"' in result, "TypeB should be quoted"

        print("\n✓ Comprehensive fixer correctly handles aliases")
        return True


def main() -> int:
    """Run all tests."""
    print("=" * 80)
    print("SCRIPT BUG FIX VALIDATION TESTS")
    print("=" * 80)

    tests = [
        ("Multi-type replacement", test_multi_type_replacement),
        ("Import alias tracking (AST)", test_import_alias_tracking),
        ("Fix counter accuracy", test_fix_counter_accuracy),
        ("Comprehensive fixer aliases", test_comprehensive_fixer_alias),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except AssertionError as e:
            print(f"\n✗ TEST FAILED: {name}")
            print(f"  Error: {e}")
            failed += 1
        except Exception as e:
            print(f"\n✗ TEST ERROR: {name}")
            print(f"  Error: {e}")
            import traceback

            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")

    if failed == 0:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
