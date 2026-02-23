"""Unit tests for ProtocolEffect -- synchronous effect execution boundary.

Validates:
- ProtocolEffect is @runtime_checkable
- The synchronous_execution ClassVar is declared
- execute() is synchronous (not async)
- isinstance() checks work correctly for compliant/non-compliant classes
- Validator sync-flag detection correctly exempts methods from SPI005
"""

from __future__ import annotations

import ast
import os
import sys
import textwrap
from pathlib import Path
from typing import ClassVar

import pytest

from omnibase_spi.protocols.effects.protocol_effect import ProtocolEffect

# Path to the validation scripts directory
_SCRIPTS_DIR = Path(__file__).parent.parent.parent.parent.parent / "scripts" / "validation"


# ---------------------------------------------------------------------------
# Compliant/non-compliant implementations for isinstance tests
# ---------------------------------------------------------------------------


class CompliantEffect:
    """Minimal compliant implementation of ProtocolEffect."""

    synchronous_execution: ClassVar[bool] = True

    def execute(self, intent: object) -> bool:
        return True


class NonCompliantEffect:
    """Class missing both synchronous_execution and execute."""

    pass


class MissingExecuteEffect:
    """Has synchronous_execution but missing execute method."""

    synchronous_execution: ClassVar[bool] = True


class MissingSyncFlagEffect:
    """Has execute but missing synchronous_execution class var."""

    def execute(self, intent: object) -> bool:
        return True


# ---------------------------------------------------------------------------
# Tests: ProtocolEffect basic contract
# ---------------------------------------------------------------------------


class TestProtocolEffectBasics:
    """Test basic ProtocolEffect protocol properties."""

    @pytest.mark.unit
    def test_protocol_is_runtime_checkable(self) -> None:
        """ProtocolEffect must be @runtime_checkable."""
        effect = CompliantEffect()
        assert isinstance(effect, ProtocolEffect)

    @pytest.mark.unit
    def test_non_compliant_fails_isinstance(self) -> None:
        """Class missing both synchronous_execution and execute fails isinstance."""
        assert not isinstance(NonCompliantEffect(), ProtocolEffect)

    @pytest.mark.unit
    def test_missing_execute_fails_isinstance(self) -> None:
        """Class without execute() fails isinstance check."""
        assert not isinstance(MissingExecuteEffect(), ProtocolEffect)

    @pytest.mark.unit
    def test_missing_sync_flag_fails_isinstance(self) -> None:
        """Class without synchronous_execution class var fails isinstance check."""
        assert not isinstance(MissingSyncFlagEffect(), ProtocolEffect)

    @pytest.mark.unit
    def test_protocol_cannot_be_instantiated_directly(self) -> None:
        """Protocol cannot be instantiated directly."""
        with pytest.raises(TypeError):
            ProtocolEffect()  # type: ignore[misc]


class TestProtocolEffectSynchronousExecutionFlag:
    """Test the synchronous_execution contract flag."""

    @pytest.mark.unit
    def test_compliant_class_has_synchronous_execution(self) -> None:
        """Compliant implementation declares synchronous_execution."""
        assert hasattr(CompliantEffect, "synchronous_execution")
        assert CompliantEffect.synchronous_execution is True

    @pytest.mark.unit
    def test_execute_is_not_async(self) -> None:
        """execute() must be a regular (synchronous) function, not a coroutine."""
        import inspect

        effect = CompliantEffect()
        assert not inspect.iscoroutinefunction(effect.execute)

    @pytest.mark.unit
    def test_execute_returns_synchronously(self) -> None:
        """execute() returns a value without awaiting."""
        effect = CompliantEffect()
        result = effect.execute("test intent")
        assert result is True

    @pytest.mark.unit
    def test_protocol_declares_synchronous_execution_classvar(self) -> None:
        """ProtocolEffect itself declares synchronous_execution as ClassVar."""
        # The declaration must be present in the protocol so isinstance checks work
        # and the validator flag is present at AST parse time.
        assert "synchronous_execution" in ProtocolEffect.__protocol_attrs__


# ---------------------------------------------------------------------------
# Helper: load validator via sys.modules to avoid dataclass module issues
# ---------------------------------------------------------------------------


def _load_comprehensive_validator() -> tuple[type, type]:
    """Load ComprehensiveSPIValidator and ValidationConfig from scripts/.

    Returns (ComprehensiveSPIValidator, ValidationConfig).
    Adds the scripts dir to sys.path so the module-level dataclasses resolve
    __module__ correctly.
    """
    import importlib.util

    scripts_dir_str = str(_SCRIPTS_DIR)
    if scripts_dir_str not in sys.path:
        sys.path.insert(0, scripts_dir_str)

    module_name = "comprehensive_spi_validator"
    if module_name not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            module_name,
            _SCRIPTS_DIR / "comprehensive_spi_validator.py",
        )
        assert spec is not None
        mod = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = mod
        assert spec.loader is not None
        spec.loader.exec_module(mod)  # type: ignore[union-attr]

    mod = sys.modules[module_name]
    return mod.ComprehensiveSPIValidator, mod.ValidationConfig  # type: ignore[return-value]


def _load_spi_typing_validator() -> type:
    """Load SPITypingValidator from scripts/."""
    import importlib.util

    scripts_dir_str = str(_SCRIPTS_DIR)
    if scripts_dir_str not in sys.path:
        sys.path.insert(0, scripts_dir_str)

    module_name = "validate_spi_typing_patterns"
    if module_name not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            module_name,
            _SCRIPTS_DIR / "validate_spi_typing_patterns.py",
        )
        assert spec is not None
        mod = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = mod
        assert spec.loader is not None
        spec.loader.exec_module(mod)  # type: ignore[union-attr]

    return sys.modules[module_name].SPITypingValidator  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Tests: Validator sync-flag detection (AST-level)
# ---------------------------------------------------------------------------


class TestSyncFlagASTDetection:
    """Test AST-level detection of synchronous_execution flag in validator helpers."""

    @pytest.mark.unit
    def test_class_with_annotated_sync_flag_detected(self) -> None:
        """_class_declares_synchronous_execution returns True for annotated flag."""
        ComprehensiveSPIValidator, ValidationConfig = _load_comprehensive_validator()
        config = ValidationConfig()

        source = textwrap.dedent("""
            from typing import ClassVar, Protocol, runtime_checkable

            @runtime_checkable
            class ProtocolSyncFlagged(Protocol):
                synchronous_execution: ClassVar[bool]
                def execute(self, intent: object) -> bool: ...
        """)

        tree = ast.parse(source)
        class_node = next(n for n in ast.walk(tree) if isinstance(n, ast.ClassDef))

        validator = ComprehensiveSPIValidator("test.py", config)
        assert validator._class_declares_synchronous_execution(class_node) is True

    @pytest.mark.unit
    def test_class_with_assigned_sync_flag_detected(self) -> None:
        """_class_declares_synchronous_execution returns True for assigned flag."""
        ComprehensiveSPIValidator, ValidationConfig = _load_comprehensive_validator()
        config = ValidationConfig()

        source = textwrap.dedent("""
            from typing import ClassVar, Protocol, runtime_checkable

            @runtime_checkable
            class ProtocolSyncAssigned(Protocol):
                synchronous_execution = True
                def execute(self, intent: object) -> bool: ...
        """)

        tree = ast.parse(source)
        class_node = next(n for n in ast.walk(tree) if isinstance(n, ast.ClassDef))

        validator = ComprehensiveSPIValidator("test.py", config)
        assert validator._class_declares_synchronous_execution(class_node) is True

    @pytest.mark.unit
    def test_class_without_sync_flag_not_detected(self) -> None:
        """_class_declares_synchronous_execution returns False for unflagged class."""
        ComprehensiveSPIValidator, ValidationConfig = _load_comprehensive_validator()
        config = ValidationConfig()

        source = textwrap.dedent("""
            from typing import Protocol, runtime_checkable

            @runtime_checkable
            class ProtocolAsyncEffect(Protocol):
                async def execute(self, intent: object) -> bool: ...
        """)

        tree = ast.parse(source)
        class_node = next(n for n in ast.walk(tree) if isinstance(n, ast.ClassDef))

        validator = ComprehensiveSPIValidator("test.py", config)
        assert validator._class_declares_synchronous_execution(class_node) is False


# ---------------------------------------------------------------------------
# Tests: SPI005 suppression via sync flag
# ---------------------------------------------------------------------------


class TestComprehensiveValidatorSPI005Suppression:
    """Test that SPI005 is not raised when synchronous_execution flag is present."""

    @pytest.mark.unit
    def test_execute_not_flagged_as_spi005_when_sync_flag_present(self) -> None:
        """execute() in a class with synchronous_execution must not generate SPI005."""
        ComprehensiveSPIValidator, ValidationConfig = _load_comprehensive_validator()
        config = ValidationConfig()

        # This source mirrors ProtocolEffect
        source = textwrap.dedent("""
            from typing import ClassVar, Protocol, runtime_checkable

            @runtime_checkable
            class ProtocolSyncEffect(Protocol):
                \"\"\"Synchronous effect execution contract with a longer docstring that meets length.

                This class executes effects synchronously before the caller proceeds.
                \"\"\"
                synchronous_execution: ClassVar[bool]
                def execute(self, intent: object) -> bool: ...
        """)

        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(source)
            tmp_path = f.name

        try:
            validator = ComprehensiveSPIValidator(tmp_path, config)
            tree = ast.parse(source)
            validator.visit(tree)

            spi005_violations = [v for v in validator.violations if v.rule_id == "SPI005"]
            assert spi005_violations == [], (
                f"Expected no SPI005 violations for synchronous_execution-flagged class, "
                f"but got: {[v.message for v in spi005_violations]}"
            )
        finally:
            os.unlink(tmp_path)

    @pytest.mark.unit
    def test_execute_flagged_as_spi005_when_no_sync_flag(self) -> None:
        """execute() without synchronous_execution flag generates SPI005."""
        ComprehensiveSPIValidator, ValidationConfig = _load_comprehensive_validator()
        config = ValidationConfig()

        source = textwrap.dedent("""
            from typing import Protocol, runtime_checkable

            @runtime_checkable
            class ProtocolBadEffect(Protocol):
                \"\"\"Effect without sync flag. This docstring is long enough to pass SPI014.

                More details here so the validator does not complain about length.
                \"\"\"
                def execute(self, intent: object) -> bool: ...
        """)

        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(source)
            tmp_path = f.name

        try:
            validator = ComprehensiveSPIValidator(tmp_path, config)
            tree = ast.parse(source)
            validator.visit(tree)

            spi005_violations = [v for v in validator.violations if v.rule_id == "SPI005"]
            assert len(spi005_violations) >= 1, (
                "Expected at least one SPI005 violation for unflagged synchronous execute()"
            )
        finally:
            os.unlink(tmp_path)


# ---------------------------------------------------------------------------
# Tests: SPI-T003 suppression via sync flag (validate_spi_typing_patterns.py)
# ---------------------------------------------------------------------------


class TestSPITypingValidatorSPI_T003Suppression:
    """Test that SPI-T003 is not raised when synchronous_execution flag is present."""

    @pytest.mark.unit
    def test_execute_not_flagged_as_spi_t003_when_sync_flag_present(self) -> None:
        """execute() in a class with synchronous_execution must not generate SPI-T003."""
        import tempfile

        SPITypingValidator = _load_spi_typing_validator()

        source = textwrap.dedent("""
            from typing import ClassVar, Protocol, runtime_checkable

            @runtime_checkable
            class ProtocolSyncEffect(Protocol):
                \"\"\"Synchronous effect.\"\"\"
                synchronous_execution: ClassVar[bool]
                def execute(self, intent: object) -> bool: ...
        """)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(source)
            tmp_path = f.name

        try:
            validator = SPITypingValidator(tmp_path)
            tree = ast.parse(source)
            validator.visit(tree)

            spi_t003_violations = [
                v for v in validator.violations if v.violation_code == "SPI-T003"
            ]
            assert spi_t003_violations == [], (
                f"Expected no SPI-T003 violations for synchronous_execution-flagged class, "
                f"but got: {[v.message for v in spi_t003_violations]}"
            )
        finally:
            os.unlink(tmp_path)

    @pytest.mark.unit
    def test_execute_flagged_as_spi_t003_when_no_sync_flag(self) -> None:
        """execute() without synchronous_execution flag generates SPI-T003."""
        import tempfile

        SPITypingValidator = _load_spi_typing_validator()

        # No synchronous_execution flag -- execute should be flagged as needing async
        source = textwrap.dedent("""
            from typing import Protocol, runtime_checkable

            @runtime_checkable
            class ProtocolBadEffect(Protocol):
                \"\"\"Effect without sync flag.\"\"\"
                def execute(self, intent: object) -> bool: ...
        """)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(source)
            tmp_path = f.name

        try:
            validator = SPITypingValidator(tmp_path)
            tree = ast.parse(source)
            validator.visit(tree)

            spi_t003_violations = [
                v for v in validator.violations if v.violation_code == "SPI-T003"
            ]
            # execute() matches "execute" in async_patterns, so it should be flagged
            assert len(spi_t003_violations) >= 1, (
                "Expected at least one SPI-T003 violation for unflagged synchronous execute()"
            )
        finally:
            os.unlink(tmp_path)

    @pytest.mark.unit
    def test_current_class_synchronous_reset_after_class(self) -> None:
        """current_class_synchronous is reset to False after visiting a flagged class."""
        import tempfile

        SPITypingValidator = _load_spi_typing_validator()

        # Two classes: first has sync flag, second does not.
        # The second class's execute() should still be flagged.
        source = textwrap.dedent("""
            from typing import ClassVar, Protocol, runtime_checkable

            @runtime_checkable
            class ProtocolSync(Protocol):
                \"\"\"Sync protocol.\"\"\"
                synchronous_execution: ClassVar[bool]
                def execute(self, intent: object) -> bool: ...

            @runtime_checkable
            class ProtocolAsync(Protocol):
                \"\"\"Async protocol.\"\"\"
                def execute(self, intent: object) -> bool: ...
        """)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(source)
            tmp_path = f.name

        try:
            validator = SPITypingValidator(tmp_path)
            tree = ast.parse(source)
            validator.visit(tree)

            spi_t003_violations = [
                v for v in validator.violations if v.violation_code == "SPI-T003"
            ]
            # Only ProtocolAsync.execute() should be flagged (1 violation)
            assert len(spi_t003_violations) == 1, (
                f"Expected exactly 1 SPI-T003 violation (for ProtocolAsync.execute), "
                f"but got: {[v.message for v in spi_t003_violations]}"
            )
        finally:
            os.unlink(tmp_path)


# ---------------------------------------------------------------------------
# Tests: ProtocolEffect import
# ---------------------------------------------------------------------------


class TestProtocolEffectImport:
    """Test that ProtocolEffect can be imported from expected locations."""

    @pytest.mark.unit
    def test_import_from_effects_module(self) -> None:
        """ProtocolEffect can be imported from effects module."""
        from omnibase_spi.protocols.effects import ProtocolEffect as PE

        assert PE is not None

    @pytest.mark.unit
    def test_import_from_protocols_module(self) -> None:
        """ProtocolEffect can be imported from top-level protocols module."""
        from omnibase_spi.protocols import ProtocolEffect as PE

        assert PE is not None
