"""
Protocol interface for code quality validation in ONEX ecosystem.

This protocol defines the interface for validating code quality standards,
complexity metrics, and best practices compliance for NodeQualityValidatorEffect
implementations.
"""

from typing import List, Protocol, runtime_checkable

from .protocol_validation import ProtocolValidationResult


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
    naming_conventions: List[str]
    required_patterns: List[str]

    async def check_complexity_compliance(self, complexity: int) -> bool: ...

    async def check_maintainability_compliance(self, score: float) -> bool: ...


@runtime_checkable
class ProtocolQualityReport(Protocol):
    """Protocol for comprehensive quality assessment report."""

    file_path: str
    metrics: "ProtocolQualityMetrics"
    issues: List[ProtocolQualityIssue]
    standards_compliance: bool
    overall_score: float
    recommendations: List[str]

    async def get_critical_issues(self) -> List[ProtocolQualityIssue]: ...


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
        self, directory_path: str, file_patterns: List[str] | None = None
    ) -> List[ProtocolQualityReport]: ...

    def calculate_quality_metrics(
        self, file_path: str, content: str | None = None
    ) -> ProtocolQualityMetrics: ...

    def detect_code_smells(
        self, file_path: str, content: str | None = None
    ) -> List[ProtocolQualityIssue]: ...

    async def check_naming_conventions(
        self, file_path: str, content: str | None = None
    ) -> List[ProtocolQualityIssue]: ...

    async def analyze_complexity(
        self, file_path: str, content: str | None = None
    ) -> List[ProtocolQualityIssue]: ...

    async def validate_documentation(
        self, file_path: str, content: str | None = None
    ) -> List[ProtocolQualityIssue]: ...

    def suggest_refactoring(
        self, file_path: str, content: str | None = None
    ) -> List[str]: ...

    def configure_standards(self, standards: "ProtocolQualityStandards") -> None: ...

    async def get_validation_summary(
        self, reports: List[ProtocolQualityReport]
    ) -> ProtocolValidationResult: ...
