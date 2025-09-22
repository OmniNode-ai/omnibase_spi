"""
Protocol interface for code quality validation in ONEX ecosystem.

This protocol defines the interface for validating code quality standards,
complexity metrics, and best practices compliance for NodeQualityValidatorEffect
implementations.
"""

from typing import List, Optional, Protocol

from .protocol_validation import ProtocolValidationResult


class ProtocolQualityMetrics(Protocol):
    """Protocol for code quality metrics."""

    cyclomatic_complexity: int
    maintainability_index: float
    lines_of_code: int
    code_duplication_percentage: float
    test_coverage_percentage: float
    technical_debt_score: float

    def get_complexity_rating(self) -> str:
        """Get complexity rating: LOW, MEDIUM, HIGH, CRITICAL."""
        ...

    def get_maintainability_rating(self) -> str:
        """Get maintainability rating: EXCELLENT, GOOD, FAIR, POOR."""
        ...


class ProtocolQualityIssue(Protocol):
    """Protocol for quality issue representation."""

    issue_type: str
    severity: str  # "critical", "high", "medium", "low", "info"
    file_path: str
    line_number: int
    column_number: int
    message: str
    rule_id: str
    suggested_fix: Optional[str]

    def get_issue_summary(self) -> str:
        """Get concise issue summary."""
        ...

    def is_fixable(self) -> bool:
        """Check if issue has an automated fix."""
        ...


class ProtocolQualityStandards(Protocol):
    """Protocol for quality standards configuration."""

    max_complexity: int
    min_maintainability_score: float
    max_line_length: int
    max_function_length: int
    max_class_length: int
    naming_conventions: List[str]
    required_patterns: List[str]

    def check_complexity_compliance(self, complexity: int) -> bool:
        """Check if complexity meets standards."""
        ...

    def check_maintainability_compliance(self, score: float) -> bool:
        """Check if maintainability meets standards."""
        ...


class ProtocolQualityReport(Protocol):
    """Protocol for comprehensive quality assessment report."""

    file_path: str
    metrics: ProtocolQualityMetrics
    issues: List[ProtocolQualityIssue]
    standards_compliance: bool
    overall_score: float
    recommendations: List[str]

    def get_critical_issues(self) -> List[ProtocolQualityIssue]:
        """Get list of critical quality issues."""
        ...

    def get_fix_suggestions(self) -> List[str]:
        """Get automated fix suggestions."""
        ...


class ProtocolQualityValidator(Protocol):
    """
    Protocol interface for code quality validation in ONEX systems.

    This protocol defines the interface for NodeQualityValidatorEffect nodes
    that assess code quality, complexity metrics, maintainability, and
    compliance with coding standards.
    """

    standards: ProtocolQualityStandards
    enable_complexity_analysis: bool
    enable_duplication_detection: bool
    enable_style_checking: bool

    def validate_file_quality(
        self, file_path: str, content: Optional[str] = None
    ) -> ProtocolQualityReport:
        """
        Validate quality of a single file.

        Args:
            file_path: Path to file for quality validation
            content: Optional file content (if not provided, reads from file)

        Returns:
            ProtocolQualityReport with quality assessment
        """
        ...

    def validate_directory_quality(
        self, directory_path: str, file_patterns: Optional[List[str]] = None
    ) -> List[ProtocolQualityReport]:
        """
        Validate quality of all files in a directory.

        Args:
            directory_path: Directory path for quality validation
            file_patterns: File patterns to include (default: ["*.py"])

        Returns:
            List of ProtocolQualityReport for all validated files
        """
        ...

    def calculate_quality_metrics(
        self, file_path: str, content: Optional[str] = None
    ) -> ProtocolQualityMetrics:
        """
        Calculate quality metrics for a file.

        Args:
            file_path: Path to file for metric calculation
            content: Optional file content

        Returns:
            ProtocolQualityMetrics with calculated metrics
        """
        ...

    def detect_code_smells(
        self, file_path: str, content: Optional[str] = None
    ) -> List[ProtocolQualityIssue]:
        """
        Detect code smells and anti-patterns.

        Args:
            file_path: Path to file for smell detection
            content: Optional file content

        Returns:
            List of ProtocolQualityIssue representing detected smells
        """
        ...

    def check_naming_conventions(
        self, file_path: str, content: Optional[str] = None
    ) -> List[ProtocolQualityIssue]:
        """
        Check compliance with naming conventions.

        Args:
            file_path: Path to file for naming validation
            content: Optional file content

        Returns:
            List of ProtocolQualityIssue for naming violations
        """
        ...

    def analyze_complexity(
        self, file_path: str, content: Optional[str] = None
    ) -> List[ProtocolQualityIssue]:
        """
        Analyze code complexity and identify high-complexity areas.

        Args:
            file_path: Path to file for complexity analysis
            content: Optional file content

        Returns:
            List of ProtocolQualityIssue for complexity violations
        """
        ...

    def validate_documentation(
        self, file_path: str, content: Optional[str] = None
    ) -> List[ProtocolQualityIssue]:
        """
        Validate documentation completeness and quality.

        Args:
            file_path: Path to file for documentation validation
            content: Optional file content

        Returns:
            List of ProtocolQualityIssue for documentation issues
        """
        ...

    def suggest_refactoring(
        self, file_path: str, content: Optional[str] = None
    ) -> List[str]:
        """
        Suggest refactoring opportunities.

        Args:
            file_path: Path to file for refactoring analysis
            content: Optional file content

        Returns:
            List of refactoring suggestions
        """
        ...

    def configure_standards(self, standards: ProtocolQualityStandards) -> None:
        """
        Configure quality standards.

        Args:
            standards: Quality standards configuration
        """
        ...

    def get_validation_summary(
        self, reports: List[ProtocolQualityReport]
    ) -> ProtocolValidationResult:
        """
        Generate validation summary from quality reports.

        Args:
            reports: List of quality reports to summarize

        Returns:
            ProtocolValidationResult with overall quality assessment
        """
        ...
