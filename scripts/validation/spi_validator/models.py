# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ValidationRule:
    rule_id: str
    name: str
    description: str
    severity: str  # 'error', 'warning', 'info'
    enabled: bool = True
    auto_fixable: bool = False
    category: str = "general"
    priority: int = 1
    dependencies: list[str] = field(default_factory=list)
    configuration: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProtocolViolation:
    file_path: str
    line_number: int
    column_offset: int
    rule_id: str
    violation_type: str
    message: str
    severity: str
    suggestion: str = ""
    auto_fix_available: bool = False
    context_lines: list[str] = field(default_factory=list)
    related_violations: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    performance_impact: str = "none"  # 'none', 'low', 'medium', 'high'

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_path": self.file_path,
            "line_number": self.line_number,
            "column_offset": self.column_offset,
            "rule_id": self.rule_id,
            "violation_type": self.violation_type,
            "message": self.message,
            "severity": self.severity,
            "suggestion": self.suggestion,
            "auto_fix_available": self.auto_fix_available,
            "context_lines": self.context_lines,
            "related_violations": self.related_violations,
            "tags": self.tags,
            "performance_impact": self.performance_impact,
        }


@dataclass
class ProtocolInfo:
    name: str
    file_path: str
    module_path: str
    line_number: int
    methods: list[str] = field(default_factory=list)
    properties: list[str] = field(default_factory=list)
    signature_hash: str = ""
    is_runtime_checkable: bool = False
    has_init: bool = False
    async_methods: list[str] = field(default_factory=list)
    sync_io_methods: list[str] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    forward_references: list[str] = field(default_factory=list)
    protocol_dependencies: list[str] = field(default_factory=list)
    domain: str = "unknown"
    complexity_score: int = 0
    line_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "file_path": self.file_path,
            "module_path": self.module_path,
            "line_number": self.line_number,
            "methods": self.methods,
            "properties": self.properties,
            "signature_hash": self.signature_hash,
            "is_runtime_checkable": self.is_runtime_checkable,
            "has_init": self.has_init,
            "async_methods": self.async_methods,
            "sync_io_methods": self.sync_io_methods,
            "imports": self.imports,
            "forward_references": self.forward_references,
            "protocol_dependencies": self.protocol_dependencies,
            "domain": self.domain,
            "complexity_score": self.complexity_score,
            "line_count": self.line_count,
        }


@dataclass
class ValidationReport:
    total_files: int = 0
    total_protocols: int = 0
    violations: list[ProtocolViolation] = field(default_factory=list)
    protocols: list[ProtocolInfo] = field(default_factory=list)
    execution_time: float = 0.0
    validation_rules_applied: int = 0
    auto_fixes_applied: int = 0
    performance_metrics: dict[str, Any] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)

    @property
    def error_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == "warning")

    @property
    def info_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == "info")

    def to_dict(self) -> dict[str, Any]:
        return {
            "summary": {
                "total_files": self.total_files,
                "total_protocols": self.total_protocols,
                "error_count": self.error_count,
                "warning_count": self.warning_count,
                "info_count": self.info_count,
                "execution_time": self.execution_time,
                "validation_rules_applied": self.validation_rules_applied,
                "auto_fixes_applied": self.auto_fixes_applied,
            },
            "violations": [v.to_dict() for v in self.violations],
            "protocols": [p.to_dict() for p in self.protocols],
            "performance_metrics": self.performance_metrics,
            "recommendations": self.recommendations,
        }
