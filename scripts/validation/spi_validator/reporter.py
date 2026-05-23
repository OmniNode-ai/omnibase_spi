# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT
"""Report generation in console, JSON, and HTML formats."""

from __future__ import annotations

import json
import time
from collections import defaultdict
from pathlib import Path

from .config import ValidationConfig
from .models import ValidationReport


class ReportGenerator:
    def __init__(self, config: ValidationConfig):
        self.config = config

    def generate_console_report(self, report: ValidationReport) -> None:
        print("\n" + "=" * 90)
        print("🔍 COMPREHENSIVE SPI PROTOCOL VALIDATION REPORT")
        print("=" * 90)
        self._print_executive_summary(report)
        if report.violations:
            self._print_violations_by_category(report)
        self._print_protocol_statistics(report)
        self._print_performance_metrics(report)
        if report.recommendations:
            self._print_recommendations(report)
        self._print_final_status(report)

    def generate_json_report(
        self, report: ValidationReport, output_file: str | None = None
    ) -> None:
        if output_file is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S", time.gmtime())
            output_file = f"comprehensive_spi_validation_{timestamp}.json"
        json_data = report.to_dict()
        json_data["metadata"] = {
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "validator_version": "2.0.0",
            "config_rules": len(self.config.rules),
            "format_version": "1.0",
        }
        with open(output_file, "w") as f:
            json.dump(json_data, f, indent=2, default=str)
        print(f"📊 JSON report saved to: {output_file}")

    def generate_html_report(
        self,
        report: ValidationReport,
        output_file: str = "spi_validation_report.html",
    ) -> None:
        with open(output_file, "w") as f:
            f.write(self._generate_html_content(report))
        print(f"🌐 HTML report saved to: {output_file}")

    # -------------------------------------------------------------------------
    # Console sub-sections
    # -------------------------------------------------------------------------

    def _print_executive_summary(self, report: ValidationReport) -> None:
        print("\n📊 EXECUTIVE SUMMARY:")
        print(f"   Files analyzed: {report.total_files}")
        print(f"   Protocols found: {report.total_protocols}")
        print(f"   Total violations: {len(report.violations)}")
        print(f"   ❌ Errors: {report.error_count}")
        print(f"   ⚠️  Warnings: {report.warning_count}")
        print(f"   ℹ️  Info: {report.info_count}")
        print(f"   🔧 Auto-fixes applied: {report.auto_fixes_applied}")
        print(f"   ⏱️  Execution time: {report.execution_time:.2f}s")

    def _print_violations_by_category(self, report: ValidationReport) -> None:
        print("\n🚨 VIOLATIONS BY CATEGORY:")
        by_category: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))
        for violation in report.violations:
            rule = self.config.get_rule(violation.rule_id)
            category = rule.category if rule else "unknown"
            by_category[category][violation.severity].append(violation)

        for category, severity_groups in sorted(by_category.items()):
            total = sum(len(vs) for vs in severity_groups.values())
            print(f"\n   📁 {category.title().replace('_', ' ')} ({total} violations)")
            for severity in ["error", "warning", "info"]:
                violations = severity_groups.get(severity, [])
                if not violations:
                    continue
                icon = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}[severity]
                print(f"      {icon} {severity.title()}: {len(violations)} violations")
                for v in violations[:3]:
                    print(
                        f"         • {Path(v.file_path).name}:{v.line_number} - {v.message}"
                    )
                if len(violations) > 3:
                    print(f"         ... and {len(violations) - 3} more")

    def _print_protocol_statistics(self, report: ValidationReport) -> None:
        if not report.protocols:
            return
        print("\n📈 PROTOCOL STATISTICS:")
        runtime_checkable = sum(1 for p in report.protocols if p.is_runtime_checkable)
        with_init = sum(1 for p in report.protocols if p.has_init)
        with_async = sum(1 for p in report.protocols if p.async_methods)
        total = len(report.protocols)
        print(
            f"   @runtime_checkable: {runtime_checkable}/{total} ({runtime_checkable / total * 100:.1f}%)"
        )
        print(f"   With __init__ methods: {with_init} (should be 0)")
        print(f"   With async methods: {with_async}")

        domain_counts: dict[str, int] = defaultdict(int)
        for p in report.protocols:
            domain_counts[p.domain] += 1
        print("\n   📁 Domain Distribution:")
        for domain, count in sorted(
            domain_counts.items(), key=lambda x: x[1], reverse=True
        ):
            print(f"      {domain}: {count} protocols ({count / total * 100:.1f}%)")

        complexities = [p.complexity_score for p in report.protocols]
        if complexities:
            avg = sum(complexities) / len(complexities)
            print("\n   🧮 Complexity Analysis:")
            print(f"      Average complexity: {avg:.1f}")
            print(f"      Maximum complexity: {max(complexities)}")
            top3 = sorted(
                report.protocols, key=lambda p: p.complexity_score, reverse=True
            )[:3]
            print("      Most complex protocols:")
            for p in top3:
                print(f"         • {p.name} (score: {p.complexity_score})")

    def _print_performance_metrics(self, report: ValidationReport) -> None:
        if not report.performance_metrics:
            return
        print("\n⚡ PERFORMANCE METRICS:")
        for metric, value in report.performance_metrics.items():
            label = metric.replace("_", " ").title()
            if isinstance(value, float):
                print(f"   {label}: {value:.2f}")
            else:
                print(f"   {label}: {value}")

    def _print_recommendations(self, report: ValidationReport) -> None:
        print("\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(report.recommendations, 1):
            print(f"   {i}. {rec}")

    def _print_final_status(self, report: ValidationReport) -> None:
        print("\n" + "=" * 90)
        if report.error_count == 0:
            print("✅ VALIDATION PASSED")
            if report.warning_count > 0:
                print(
                    f"   ⚠️  {report.warning_count} warnings should be addressed for optimal code quality"
                )
            if report.info_count > 0:
                print(
                    f"   ℹ️  {report.info_count} informational items for continuous improvement"
                )
        else:
            print("❌ VALIDATION FAILED")
            print(f"   {report.error_count} errors must be fixed before merging")
            if report.auto_fixes_applied > 0:
                print(
                    f"   🔧 {report.auto_fixes_applied} issues were automatically fixed"
                )
        print(f"   📊 Code quality score: {self._calculate_quality_score(report):.1%}")

    def _calculate_quality_score(self, report: ValidationReport) -> float:
        if report.total_protocols == 0:
            return 1.0
        error_penalty = min(0.5, report.error_count * 0.05)
        warning_penalty = min(0.3, report.warning_count * 0.02)
        checkable_ratio = (
            sum(1 for p in report.protocols if p.is_runtime_checkable)
            / len(report.protocols)
            if report.protocols
            else 0
        )
        return max(0.0, 1.0 - error_penalty - warning_penalty + checkable_ratio * 0.1)

    # -------------------------------------------------------------------------
    # HTML
    # -------------------------------------------------------------------------

    def _generate_html_content(self, report: ValidationReport) -> str:
        violation_html = "".join(
            f'<div class="violation {v.severity}"><strong>{v.rule_id}: {v.violation_type}</strong>'
            f"<br>{v.file_path}:{v.line_number}<br>{v.message}</div>"
            for v in report.violations[:50]
        )
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>SPI Validation Report</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f8f9fa; padding: 20px; border-radius: 5px; }}
        .summary {{ display: flex; justify-content: space-around; margin: 20px 0; }}
        .metric {{ text-align: center; padding: 10px; }}
        .violations {{ margin: 20px 0; }}
        .violation {{ margin: 10px 0; padding: 10px; border-left: 4px solid #dc3545; background: #f8f9fa; }}
        .error {{ border-color: #dc3545; }}
        .warning {{ border-color: #ffc107; }}
        .info {{ border-color: #17a2b8; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>SPI Protocol Validation Report</h1>
        <p>Generated: {time.strftime("%Y-%m-%d %H:%M:%S")}</p>
    </div>
    <div class="summary">
        <div class="metric"><h3>{report.total_files}</h3><p>Files Analyzed</p></div>
        <div class="metric"><h3>{report.total_protocols}</h3><p>Protocols Found</p></div>
        <div class="metric"><h3>{report.error_count}</h3><p>Errors</p></div>
        <div class="metric"><h3>{report.warning_count}</h3><p>Warnings</p></div>
    </div>
    <div class="violations"><h2>Violations</h2>{violation_html}</div>
</body>
</html>"""
