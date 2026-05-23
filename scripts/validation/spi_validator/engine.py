# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""Main validation engine orchestrating all validation components."""

from __future__ import annotations

import ast
import time
from pathlib import Path
from typing import Any

from timeout_utils import timeout_context

from .autofix import AutoFixEngine
from .config import ValidationConfig
from .duplicate_analyzer import DuplicateProtocolAnalyzer
from .file_validator import ComprehensiveSPIValidator
from .models import ProtocolInfo, ProtocolViolation, ValidationReport
from .reporter import ReportGenerator


class ComprehensiveSPIValidationEngine:
    def __init__(self, config: ValidationConfig):
        self.config = config
        self.duplicate_analyzer = DuplicateProtocolAnalyzer(config)
        self.auto_fix_engine = AutoFixEngine(config)
        self.report_generator = ReportGenerator(config)

    def validate_directory(
        self,
        directory: Path,
        apply_fixes: bool = False,
        generate_json: bool = False,
        generate_html: bool = False,
    ) -> ValidationReport:
        start_time = time.time()
        python_files = self._discover_protocol_files(directory)

        if not python_files:
            print("✅ No protocol files found to validate")
            return ValidationReport()

        print(f"🔍 Found {len(python_files)} protocol files to validate")

        report = ValidationReport()
        report.total_files = len(python_files)
        all_violations: list[ProtocolViolation] = []
        all_protocols: list[ProtocolInfo] = []

        with timeout_context(
            "validation", self.config.global_settings.get("timeout_seconds", 300)
        ):
            for py_file in python_files:
                print(f"   📄 Validating {py_file.name}...")
                violations, protocols = self._validate_file(py_file)
                all_violations.extend(violations)
                all_protocols.extend(protocols)

        all_violations.extend(self.duplicate_analyzer.analyze_duplicates(all_protocols))

        if apply_fixes:
            print("🔧 Applying automatic fixes...")
            all_violations, fixes_applied = self.auto_fix_engine.apply_auto_fixes(
                all_violations
            )
            report.auto_fixes_applied = fixes_applied

        report.violations = all_violations
        report.protocols = all_protocols
        report.total_protocols = len(all_protocols)
        report.execution_time = time.time() - start_time
        report.validation_rules_applied = len(self.config.get_enabled_rules())
        report.performance_metrics = self._generate_performance_metrics(report)
        report.recommendations = self._generate_recommendations(report)

        self.report_generator.generate_console_report(report)
        if generate_json:
            self.report_generator.generate_json_report(report)
        if generate_html:
            self.report_generator.generate_html_report(report)

        return report

    def validate_single_file(self, file_path: Path) -> ValidationReport:
        start_time = time.time()
        print(f"🔍 Validating single file: {file_path}")
        violations, protocols = self._validate_file(file_path)

        report = ValidationReport()
        report.total_files = 1
        report.violations = violations
        report.protocols = protocols
        report.total_protocols = len(protocols)
        report.execution_time = time.time() - start_time
        report.validation_rules_applied = len(self.config.get_enabled_rules())
        report.recommendations = self._generate_recommendations(report)
        self.report_generator.generate_console_report(report)
        return report

    def _discover_protocol_files(self, directory: Path) -> list[Path]:
        protocol_files = []
        try:
            for py_file in directory.rglob("*.py"):
                if (
                    py_file.name.startswith("test_")
                    or py_file.name.startswith("__")
                    or "__pycache__" in str(py_file)
                    or ".git" in py_file.parts
                ):
                    continue
                try:
                    with open(py_file, encoding="utf-8") as f:
                        content = f.read(2048)
                    if self._looks_like_protocol_file(content):
                        protocol_files.append(py_file)
                except Exception:
                    continue
        except Exception as e:
            print(f"❌ Error discovering files in {directory}: {e}")
        return sorted(protocol_files)

    def _looks_like_protocol_file(self, content: str) -> bool:
        indicators = [
            "Protocol",
            "@runtime_checkable",
            "class Protocol",
            "from typing import Protocol",
        ]
        return any(indicator in content for indicator in indicators)

    def _validate_file(
        self, file_path: Path
    ) -> tuple[list[ProtocolViolation], list[ProtocolInfo]]:
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            max_size = self.config.global_settings.get("max_file_size", 1024 * 1024)
            if len(content) > max_size:
                return [
                    ProtocolViolation(
                        file_path=str(file_path),
                        line_number=1,
                        column_offset=0,
                        rule_id="SPI000",
                        violation_type="File Too Large",
                        message=f"File size {len(content)} bytes exceeds limit {max_size} bytes",
                        severity="error",
                    )
                ], []

            tree = ast.parse(content)
            validator = ComprehensiveSPIValidator(str(file_path), self.config)
            validator.visit(tree)
            return validator.violations, validator.protocols

        except SyntaxError as e:
            return [
                ProtocolViolation(
                    file_path=str(file_path),
                    line_number=e.lineno or 1,
                    column_offset=e.offset or 0,
                    rule_id="SPI000",
                    violation_type="Syntax Error",
                    message=f"Python syntax error: {e.msg}",
                    severity="error",
                    suggestion="Fix Python syntax before validation",
                )
            ], []

        except Exception as e:
            return [
                ProtocolViolation(
                    file_path=str(file_path),
                    line_number=1,
                    column_offset=0,
                    rule_id="SPI000",
                    violation_type="Validation Error",
                    message=f"Failed to validate file: {e!s}",
                    severity="error",
                    suggestion="Check file for parsing issues",
                )
            ], []

    def _generate_performance_metrics(self, report: ValidationReport) -> dict[str, Any]:
        t = report.execution_time
        return {
            "files_per_second": report.total_files / t if t > 0 else 0,
            "protocols_per_second": report.total_protocols / t if t > 0 else 0,
            "average_protocols_per_file": (
                report.total_protocols / report.total_files
                if report.total_files > 0
                else 0
            ),
            "violation_density": (
                len(report.violations) / report.total_files
                if report.total_files > 0
                else 0
            ),
        }

    def _generate_recommendations(self, report: ValidationReport) -> list[str]:
        recommendations = []
        if report.error_count > 0:
            recommendations.append(
                f"Fix {report.error_count} critical errors before merging code"
            )
        if report.protocols:
            non_checkable = sum(
                1 for p in report.protocols if not p.is_runtime_checkable
            )
            if non_checkable > 0:
                recommendations.append(
                    f"Add @runtime_checkable decorator to {non_checkable} protocols"
                )
            with_init = sum(1 for p in report.protocols if p.has_init)
            if with_init > 0:
                recommendations.append(
                    f"Remove __init__ methods from {with_init} protocols - use properties instead"
                )
        if report.execution_time > 60:
            recommendations.append(
                "Consider splitting large files for better validation performance"
            )
        if report.warning_count > report.error_count * 2:
            recommendations.append(
                "Address warnings to improve code quality and maintainability"
            )
        return recommendations


def create_sample_config_file(config_path: str) -> None:
    import yaml

    sample_config = {
        "global_settings": {
            "timeout_seconds": 300,
            "max_file_size": 1048576,
            "enable_caching": True,
            "max_violations_per_file": 100,
        },
        "rules": [{"rule_id": f"SPI{i:03d}", "enabled": True} for i in range(1, 17)],
    }
    with open(config_path, "w") as f:
        yaml.dump(sample_config, f, default_flow_style=False)
    print(f"📝 Sample configuration created: {config_path}")
