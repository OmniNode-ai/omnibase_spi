"""
Protocol interface for code quality validation in ONEX ecosystem.

This protocol defines the interface for validating code quality standards,
complexity metrics, and best practices compliance for NodeQualityValidatorEffect
implementations.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.validation.protocol_validation import (
        ProtocolValidationResult,
    )


@runtime_checkable
class ProtocolQualityMetrics(Protocol):
    """Protocol for code quality metrics."""

    cyclomatic_complexity: int
    maintainability_index: float
    lines_of_code: int
    code_duplication_percentage: float
    test_coverage_percentage: float
    technical_debt_score: float

    async def get_complexity_rating(self) -> str: ...


@runtime_checkable
class ProtocolQualityIssue(Protocol):
    """Protocol for quality issue representation."""

    issue_type: str
    severity: str
    file_path: str
    line_number: int
    column_number: int
    message: str
    rule_id: str
    suggested_fix: str | None

    async def get_issue_summary(self) -> str: ...


@runtime_checkable
class ProtocolQualityStandards(Protocol):
    """Protocol for quality standards configuration."""

    max_complexity: int
    min_maintainability_score: float
    max_line_length: int
    max_function_length: int
    max_class_length: int
    naming_conventions: list[str]
    required_patterns: list[str]

    async def check_complexity_compliance(self, complexity: int) -> bool: ...

    async def check_maintainability_compliance(self, score: float) -> bool: ...


@runtime_checkable
class ProtocolQualityReport(Protocol):
    """Protocol for comprehensive quality assessment report."""

    file_path: str
    metrics: "ProtocolQualityMetrics"
    issues: list[ProtocolQualityIssue]
    standards_compliance: bool
    overall_score: float
    recommendations: list[str]

    async def get_critical_issues(self) -> list[ProtocolQualityIssue]: ...


@runtime_checkable
class ProtocolQualityValidator(Protocol):
    """
    Protocol interface for code quality validation in ONEX systems.

    This protocol defines the interface for NodeQualityValidatorEffect nodes
    that assess code quality, complexity metrics, maintainability, and
    compliance with coding standards.
    """

    standards: "ProtocolQualityStandards"
    enable_complexity_analysis: bool
    enable_duplication_detection: bool
    enable_style_checking: bool

    async def validate_file_quality(
        self, file_path: str, content: str | None = None
    ) -> ProtocolQualityReport: ...

    async def validate_directory_quality(
        self, directory_path: str, file_patterns: list[str] | None = None
    ) -> list[ProtocolQualityReport]: ...

    def calculate_quality_metrics(
        self, file_path: str, content: str | None = None
    ) -> ProtocolQualityMetrics: ...

    def detect_code_smells(
        self, file_path: str, content: str | None = None
    ) -> list[ProtocolQualityIssue]: ...

    async def check_naming_conventions(
        self, file_path: str, content: str | None = None
    ) -> list[ProtocolQualityIssue]: ...

    async def analyze_complexity(
        self, file_path: str, content: str | None = None
    ) -> list[ProtocolQualityIssue]: ...

    async def validate_documentation(
        self, file_path: str, content: str | None = None
    ) -> list[ProtocolQualityIssue]: ...

    def suggest_refactoring(
        self, file_path: str, content: str | None = None
    ) -> list[str]: ...

    def configure_standards(self, standards: "ProtocolQualityStandards") -> None: ...

    async def get_validation_summary(
        self, reports: list[ProtocolQualityReport]
    ) -> ProtocolValidationResult: ...
