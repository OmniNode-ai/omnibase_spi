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
    """
    Protocol for code quality metrics collection and representation.

    Captures comprehensive code quality measurements including complexity,
    maintainability, coverage, and technical debt metrics for quality
    assessment and improvement tracking.

    Attributes:
        cyclomatic_complexity: McCabe cyclomatic complexity score
        maintainability_index: Maintainability index (0-100 scale)
        lines_of_code: Total lines of code analyzed
        code_duplication_percentage: Percentage of duplicated code
        test_coverage_percentage: Test coverage percentage
        technical_debt_score: Estimated technical debt score

    Example:
        ```python
        validator: ProtocolQualityValidator = get_quality_validator()
        metrics = validator.calculate_quality_metrics("path/to/file.py")

        print(f"Complexity: {metrics.cyclomatic_complexity}")
        print(f"Maintainability: {metrics.maintainability_index:.1f}")
        print(f"Coverage: {metrics.test_coverage_percentage:.1f}%")

        rating = await metrics.get_complexity_rating()
        print(f"Rating: {rating}")  # e.g., "A", "B", "C"
        ```

    See Also:
        - ProtocolQualityValidator: Quality validation interface
        - ProtocolQualityReport: Aggregated quality reporting
    """

    cyclomatic_complexity: int
    maintainability_index: float
    lines_of_code: int
    code_duplication_percentage: float
    test_coverage_percentage: float
    technical_debt_score: float

    async def get_complexity_rating(self) -> str: ...


@runtime_checkable
class ProtocolQualityIssue(Protocol):
    """
    Protocol for code quality issue representation.

    Captures a single quality issue with precise location information,
    severity classification, rule identification, and optional fix
    suggestions for actionable quality improvement.

    Attributes:
        issue_type: Type of issue (complexity, naming, style, etc.)
        severity: Severity level (critical, error, warning, info)
        file_path: Path to the file containing the issue
        line_number: Line number of the issue
        column_number: Column number of the issue
        message: Human-readable issue description
        rule_id: Identifier of the rule that detected this issue
        suggested_fix: Optional suggested fix for the issue

    Example:
        ```python
        report: ProtocolQualityReport = await validator.validate_file_quality(path)

        for issue in report.issues:
            print(f"[{issue.severity}] {issue.file_path}:{issue.line_number}")
            print(f"  Rule: {issue.rule_id}")
            print(f"  Message: {issue.message}")
            if issue.suggested_fix:
                print(f"  Suggested fix: {issue.suggested_fix}")

            summary = await issue.get_issue_summary()
        ```

    See Also:
        - ProtocolQualityReport: Issue container
        - ProtocolQualityValidator: Issue detection
    """

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
    """
    Protocol for code quality standards configuration.

    Defines configurable thresholds and requirements for code quality
    validation including complexity limits, length restrictions,
    naming conventions, and required patterns.

    Attributes:
        max_complexity: Maximum allowed cyclomatic complexity
        min_maintainability_score: Minimum maintainability index
        max_line_length: Maximum allowed line length
        max_function_length: Maximum function line count
        max_class_length: Maximum class line count
        naming_conventions: List of naming convention patterns
        required_patterns: List of required code patterns

    Example:
        ```python
        validator: ProtocolQualityValidator = get_quality_validator()
        standards = validator.standards

        print(f"Max complexity: {standards.max_complexity}")
        print(f"Min maintainability: {standards.min_maintainability_score}")

        # Check compliance
        is_ok = await standards.check_complexity_compliance(15)
        is_ok = await standards.check_maintainability_compliance(75.0)
        ```

    See Also:
        - ProtocolQualityValidator: Uses standards for validation
        - ProtocolQualityMetrics: Metrics compared against standards
    """

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
    """
    Protocol for comprehensive code quality assessment report.

    Aggregates quality metrics, issues, compliance status, and
    recommendations for a file or directory into a structured
    report for quality assessment and improvement planning.

    Attributes:
        file_path: Path to the assessed file/directory
        metrics: Calculated quality metrics
        issues: List of detected quality issues
        standards_compliance: Whether standards are met
        overall_score: Aggregate quality score (0-100)
        recommendations: List of improvement recommendations

    Example:
        ```python
        validator: ProtocolQualityValidator = get_quality_validator()
        report = await validator.validate_file_quality("path/to/file.py")

        print(f"File: {report.file_path}")
        print(f"Score: {report.overall_score:.1f}/100")
        print(f"Compliant: {report.standards_compliance}")

        critical = await report.get_critical_issues()
        print(f"Critical issues: {len(critical)}")

        for rec in report.recommendations:
            print(f"  - {rec}")
        ```

    See Also:
        - ProtocolQualityValidator: Report generation
        - ProtocolQualityMetrics: Metric details
        - ProtocolQualityIssue: Issue details
    """

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
    ) -> "ProtocolValidationResult": ...
