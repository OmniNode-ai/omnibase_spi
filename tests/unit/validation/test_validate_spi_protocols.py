# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""Unit tests for the SPI protocol validation script."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

SCRIPTS_VALIDATION_ROOT = Path(__file__).resolve().parents[3] / "scripts" / "validation"
sys.path.insert(0, str(SCRIPTS_VALIDATION_ROOT))

from scripts.validation.validate_spi_protocols import (
    ProtocolInfo,
    SPIProtocolValidator,
    discover_python_files,
    validate_file,
    validate_protocol_duplicates,
)


def _write_python_file(path: Path, source: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source.strip() + "\n", encoding="utf-8")
    return path


def _validate_source(tmp_path: Path, source: str) -> SPIProtocolValidator:
    protocol_file = _write_python_file(tmp_path / "protocol_sample.py", source)
    tree = ast.parse(protocol_file.read_text(encoding="utf-8"))
    validator = SPIProtocolValidator(str(protocol_file))
    validator.visit(tree)
    return validator


@pytest.mark.unit
class TestProtocolInfo:
    def test_collection_fields_default_to_empty_lists(self) -> None:
        info = ProtocolInfo(
            name="ProtocolExample",
            file_path="src/omnibase_spi/protocols/protocol_example.py",
            methods=[],
            signature_hash="hash",
            line_number=1,
        )

        assert info.async_methods == []
        assert info.sync_io_methods == []
        assert info.properties == []
        assert info.base_protocols == []


@pytest.mark.unit
class TestSPIProtocolValidator:
    def test_reports_protocol_structure_and_typing_violations(
        self, tmp_path: Path
    ) -> None:
        validator = _validate_source(
            tmp_path,
            """
from typing import Protocol


class Widget(Protocol):
    def __init__(self) -> None:
        ...

    def read_file(self, source: FileReader) -> FileResult:
        ...

    def register_callback(self, callback: object) -> None:
        ...

    def concrete(self) -> str:
        return "value"
""",
        )

        violation_codes = {
            violation.violation_code for violation in validator.violations
        }
        assert {"SPI001", "SPI002", "SPI003", "SPI004", "SPI005", "SPI006"} <= (
            violation_codes
        )
        assert validator.protocols[0].name == "Widget"
        assert "read_file" in validator.protocols[0].sync_io_methods

    def test_accepts_runtime_checkable_async_protocol(self, tmp_path: Path) -> None:
        validator = _validate_source(
            tmp_path,
            """
from typing import Protocol, runtime_checkable


@runtime_checkable
class ProtocolWidget(Protocol):
    async def fetch(self, key: str) -> str:
        ...
""",
        )

        assert validator.violations == []
        assert validator.protocols[0].is_runtime_checkable is True
        assert validator.protocols[0].async_methods == ["fetch"]
        assert validator.protocols[0].protocol_type == "functional"

    def test_type_checking_protocols_are_ignored(self, tmp_path: Path) -> None:
        validator = _validate_source(
            tmp_path,
            """
from typing import TYPE_CHECKING, Protocol


if TYPE_CHECKING:
    class ProtocolForwardOnly(Protocol):
        def fetch(self) -> str:
            return "not checked"
""",
        )

        assert validator.violations == []
        assert validator.protocols == []


@pytest.mark.unit
class TestFileDiscovery:
    def test_discovers_python_files_excluding_tests_private_and_cache(
        self, tmp_path: Path
    ) -> None:
        src = tmp_path / "src"
        kept = _write_python_file(src / "protocol_kept.py", "VALUE = 1")
        _write_python_file(src / "test_skipped.py", "VALUE = 1")
        _write_python_file(src / "_private.py", "VALUE = 1")
        _write_python_file(src / "__pycache__" / "cached.py", "VALUE = 1")

        assert discover_python_files(src) == [kept]


@pytest.mark.unit
class TestValidateProtocolDuplicates:
    def test_reports_real_duplicate_in_same_domain_and_type(self) -> None:
        first = ProtocolInfo(
            name="ProtocolCache",
            file_path="src/omnibase_spi/protocols/cache/protocol_cache.py",
            methods=["get(key) -> str"],
            signature_hash="same",
            line_number=10,
            domain="cache",
            protocol_type="functional",
        )
        second = ProtocolInfo(
            name="ProtocolCache",
            file_path="src/omnibase_spi/protocols/cache/protocol_cache_copy.py",
            methods=["get(key) -> str"],
            signature_hash="same",
            line_number=20,
            domain="cache",
            protocol_type="functional",
        )

        violations = validate_protocol_duplicates([first, second])

        assert [violation.violation_code for violation in violations] == ["SPI010"]

    def test_strict_mode_reports_known_allowed_conflict_as_info(self) -> None:
        first = ProtocolInfo(
            name="ProtocolValidationResult",
            file_path="src/a.py",
            methods=["ok() -> bool"],
            signature_hash="one",
            line_number=1,
            domain="validation",
        )
        second = ProtocolInfo(
            name="ProtocolValidationResult",
            file_path="src/b.py",
            methods=["errors() -> list[str]"],
            signature_hash="two",
            line_number=2,
            domain="validation",
        )

        violations = validate_protocol_duplicates([first, second], strict_mode=True)

        assert [violation.violation_code for violation in violations] == ["SPI012"]
        assert violations[0].severity == "info"


@pytest.mark.unit
class TestValidateFile:
    def test_returns_syntax_error_violation(self, tmp_path: Path) -> None:
        bad_file = _write_python_file(
            tmp_path / "bad_protocol.py",
            "from typing import Protocol\nclass ProtocolBad(Protocol",
        )

        violations, protocols = validate_file(bad_file)

        assert protocols == []
        assert violations[0].violation_code == "SPI000"
        assert violations[0].violation_type == "syntax_error"
