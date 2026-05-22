# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""Unit tests for the comprehensive SPI validation script."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

SCRIPTS_VALIDATION_ROOT = Path(__file__).resolve().parents[3] / "scripts" / "validation"
sys.path.insert(0, str(SCRIPTS_VALIDATION_ROOT))

from scripts.validation.comprehensive_spi_validator import (
    AutoFixEngine,
    ComprehensiveSPIValidationEngine,
    ComprehensiveSPIValidator,
    DuplicateProtocolAnalyzer,
    ProtocolInfo,
    ValidationConfig,
    ValidationReport,
)


def _write_protocol_file(path: Path, source: str) -> Path:
    path.write_text(source.strip() + "\n", encoding="utf-8")
    return path


@pytest.mark.unit
class TestValidationConfig:
    def test_default_rules_are_sorted_by_priority_then_rule_id(self) -> None:
        config = ValidationConfig()

        enabled_rule_ids = [rule.rule_id for rule in config.get_enabled_rules()]

        assert enabled_rule_ids[:3] == ["SPI001", "SPI003", "SPI004"]
        assert "SPI016" in enabled_rule_ids

    def test_yaml_config_updates_rule_and_global_settings(self, tmp_path: Path) -> None:
        config_path = tmp_path / "validation.yaml"
        config_path.write_text(
            """
global_settings:
  timeout_seconds: 12
rules:
  - rule_id: SPI014
    enabled: false
  - rule_id: SPI005
    severity: warning
""".strip()
            + "\n",
            encoding="utf-8",
        )

        config = ValidationConfig(str(config_path))

        assert config.global_settings["timeout_seconds"] == 12
        assert config.get_rule("SPI014").enabled is False
        assert config.get_rule("SPI005").severity == "warning"


@pytest.mark.unit
class TestComprehensiveSPIValidator:
    def test_reports_missing_runtime_checkable_and_concrete_method_body(
        self, tmp_path: Path
    ) -> None:
        protocol_file = _write_protocol_file(
            tmp_path / "protocol_widget.py",
            """
from typing import Protocol


class ProtocolWidget(Protocol):
    \"\"\"Protocol widget boundary with enough documentation for rule SPI014.\"\"\"

    def fetch(self, key: str) -> str:
        return key
""",
        )
        config = ValidationConfig()
        tree = ast.parse(protocol_file.read_text(encoding="utf-8"))
        validator = ComprehensiveSPIValidator(str(protocol_file), config)

        validator.visit(tree)

        rule_ids = {violation.rule_id for violation in validator.violations}
        assert {"SPI003", "SPI004"}.issubset(rule_ids)
        assert validator.protocols[0].name == "ProtocolWidget"
        assert validator.protocols[0].methods == ["fetch(key: str) -> str"]

    def test_accepts_runtime_checkable_async_protocol(self, tmp_path: Path) -> None:
        protocol_file = _write_protocol_file(
            tmp_path / "protocol_fetcher.py",
            """
from typing import Protocol, runtime_checkable


@runtime_checkable
class ProtocolFetcher(Protocol):
    \"\"\"Protocol fetcher boundary with a detailed contract description.\"\"\"

    async def fetch(self, key: str) -> str:
        \"\"\"Fetch a value by key.\"\"\"
        ...
""",
        )
        config = ValidationConfig()
        tree = ast.parse(protocol_file.read_text(encoding="utf-8"))
        validator = ComprehensiveSPIValidator(str(protocol_file), config)

        validator.visit(tree)

        assert validator.violations == []
        assert validator.protocols[0].is_runtime_checkable is True
        assert validator.protocols[0].async_methods == ["fetch"]


@pytest.mark.unit
class TestDuplicateProtocolAnalyzer:
    def test_flags_identical_protocol_name_and_signature(self) -> None:
        config = ValidationConfig()
        analyzer = DuplicateProtocolAnalyzer(config)
        first = ProtocolInfo(
            name="ProtocolStore",
            file_path="src/omnibase_spi/protocols/store/protocol_store.py",
            module_path="omnibase_spi.protocols.store.protocol_store",
            line_number=10,
            methods=["get(key: str) -> str"],
            signature_hash="same",
        )
        second = ProtocolInfo(
            name="ProtocolStore",
            file_path="src/omnibase_spi/protocols/cache/protocol_store.py",
            module_path="omnibase_spi.protocols.cache.protocol_store",
            line_number=20,
            methods=["get(key: str) -> str"],
            signature_hash="same",
        )

        violations = analyzer.analyze_duplicates([first, second])

        assert [violation.rule_id for violation in violations] == ["SPI010", "SPI010"]
        assert any("identical" in violation.message for violation in violations)


@pytest.mark.unit
class TestAutoFixEngine:
    def test_adds_runtime_checkable_decorator(self, tmp_path: Path) -> None:
        protocol_file = _write_protocol_file(
            tmp_path / "protocol_missing_decorator.py",
            """
from typing import Protocol, runtime_checkable


class ProtocolMissingDecorator(Protocol):
    \"\"\"Protocol with enough documentation to isolate the decorator fix.\"\"\"

    async def fetch(self, key: str) -> str:
        \"\"\"Fetch a value by key.\"\"\"
        ...
""",
        )
        config = ValidationConfig()
        engine = ComprehensiveSPIValidationEngine(config)
        report = engine.validate_single_file(protocol_file)

        remaining, fixes_applied = AutoFixEngine(config).apply_auto_fixes(
            report.violations
        )

        assert fixes_applied == 1
        assert not [
            violation for violation in remaining if violation.rule_id == "SPI003"
        ]
        assert (
            "@runtime_checkable\nclass ProtocolMissingDecorator"
            in protocol_file.read_text(encoding="utf-8")
        )


@pytest.mark.unit
class TestComprehensiveSPIValidationEngine:
    def test_directory_validation_discovers_protocol_files_only(
        self, tmp_path: Path
    ) -> None:
        protocol_dir = tmp_path / "src"
        protocol_dir.mkdir()
        _write_protocol_file(
            protocol_dir / "protocol_valid.py",
            """
from typing import Protocol, runtime_checkable


@runtime_checkable
class ProtocolValid(Protocol):
    \"\"\"Protocol valid boundary with a detailed contract description.\"\"\"

    async def fetch(self, key: str) -> str:
        \"\"\"Fetch a value by key.\"\"\"
        ...
""",
        )
        _write_protocol_file(
            protocol_dir / "test_ignored.py", "class ProtocolIgnored: ..."
        )
        _write_protocol_file(protocol_dir / "plain.py", "VALUE = 1")

        report: ValidationReport = ComprehensiveSPIValidationEngine(
            ValidationConfig()
        ).validate_directory(protocol_dir)

        assert report.total_files == 1
        assert report.total_protocols == 1
        assert report.error_count == 0
