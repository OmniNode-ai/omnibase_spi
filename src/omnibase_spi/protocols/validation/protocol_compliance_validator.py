"""
Protocol interface for compliance validation in ONEX ecosystem.

This protocol defines the interface for validating compliance with ONEX
standards, architectural patterns, and ecosystem requirements for
NodeComplianceValidatorReducer implementations.
"""

from typing import List, Optional, Protocol, runtime_checkable

from .protocol_validation import ProtocolValidationResult


@runtime_checkable
class ProtocolComplianceRule(Protocol):
    """Protocol for compliance rule definition."""

    rule_id: str
    rule_name: str
    category: str
    severity: str
    description: str
    required_pattern: str
    violation_message: str

    async def check_compliance(self, content: str, context: str) -> bool:
        """Check if content complies with this rule."""
        ...

    async def get_fix_suggestion(self) -> str:
        """Get suggestion for fixing compliance violation."""
        ...


@runtime_checkable
class ProtocolComplianceViolation(Protocol):
    """Protocol for compliance violation representation."""

    rule: "ProtocolComplianceRule"
    file_path: str
    line_number: int
    violation_text: str
    severity: str
    fix_suggestion: str
    auto_fixable: bool

    async def get_violation_summary(self) -> str:
        """Get concise violation summary."""
        ...

    async def get_compliance_impact(self) -> str:
        """Get description of compliance impact."""
        ...


@runtime_checkable
class ProtocolONEXStandards(Protocol):
    """Protocol for ONEX ecosystem standards."""

    enum_naming_pattern: str
    model_naming_pattern: str
    protocol_naming_pattern: str
    node_naming_pattern: str
    required_directories: List[str]
    forbidden_patterns: List[str]

    async def validate_enum_naming(self, name: str) -> bool:
        """Validate enum follows ONEX naming convention."""
        ...

    async def validate_model_naming(self, name: str) -> bool:
        """Validate model follows ONEX naming convention."""
        ...

    async def validate_protocol_naming(self, name: str) -> bool:
        """Validate protocol follows ONEX naming convention."""
        ...

    async def validate_node_naming(self, name: str) -> bool:
        """Validate node follows ONEX naming convention."""
        ...


@runtime_checkable
class ProtocolArchitectureCompliance(Protocol):
    """Protocol for architectural compliance checking."""

    allowed_dependencies: List[str]
    forbidden_dependencies: List[str]
    required_patterns: List[str]
    layer_violations: List[str]

    async def check_dependency_compliance(self, imports: List[str]) -> List[str]:
        """Check dependency compliance, return violations."""
        ...

    async def validate_layer_separation(
        self, file_path: str, imports: List[str]
    ) -> List[str]:
        """Validate architectural layer separation."""
        ...


@runtime_checkable
class ProtocolComplianceReport(Protocol):
    """Protocol for comprehensive compliance report."""

    file_path: str
    violations: List[ProtocolComplianceViolation]
    onex_compliance_score: float
    architecture_compliance_score: float
    overall_compliance: bool
    critical_violations: int
    recommendations: List[str]

    async def get_compliance_summary(self) -> str:
        """Get overall compliance summary."""
        ...

    async def get_priority_fixes(self) -> List[ProtocolComplianceViolation]:
        """Get violations that should be fixed first."""
        ...


@runtime_checkable
class ProtocolComplianceValidator(Protocol):
    """
    Protocol interface for compliance validation in ONEX systems.

    This protocol defines the interface for NodeComplianceValidatorReducer nodes
    that validate compliance with ONEX standards, architectural patterns,
    and ecosystem requirements.
    """

    onex_standards: "ProtocolONEXStandards"
    architecture_rules: "ProtocolArchitectureCompliance"
    custom_rules: List[ProtocolComplianceRule]
    strict_mode: bool

    async def validate_file_compliance(
        self, file_path: str, content: str | None = None
    ) -> ProtocolComplianceReport:
        """
        Validate compliance of a single file.

        Args:
            file_path: Path to file for compliance validation
            content: Optional file content (if not provided, reads from file)

        Returns:
            ProtocolComplianceReport with compliance assessment
        """
        ...

    async def validate_repository_compliance(
        self, repository_path: str, file_patterns: List[str] | None = None
    ) -> List[ProtocolComplianceReport]:
        """
        Validate compliance of entire repository.

        Args:
            repository_path: Repository path for compliance validation
            file_patterns: File patterns to include (default: ["*.py"])

        Returns:
            List of ProtocolComplianceReport for all validated files
        """
        ...

    async def validate_onex_naming(
        self, file_path: str, content: str | None = None
    ) -> List[ProtocolComplianceViolation]:
        """
        Validate ONEX naming conventions.

        Args:
            file_path: Path to file for naming validation
            content: Optional file content

        Returns:
            List of ProtocolComplianceViolation for naming violations
        """
        ...

    async def validate_architecture_compliance(
        self, file_path: str, content: str | None = None
    ) -> List[ProtocolComplianceViolation]:
        """
        Validate architectural compliance.

        Args:
            file_path: Path to file for architecture validation
            content: Optional file content

        Returns:
            List of ProtocolComplianceViolation for architecture violations
        """
        ...

    async def validate_directory_structure(
        self, repository_path: str
    ) -> List[ProtocolComplianceViolation]:
        """
        Validate repository directory structure compliance.

        Args:
            repository_path: Repository path for structure validation

        Returns:
            List of ProtocolComplianceViolation for structure violations
        """
        ...

    async def validate_dependency_compliance(
        self, file_path: str, imports: List[str]
    ) -> List[ProtocolComplianceViolation]:
        """
        Validate dependency compliance.

        Args:
            file_path: File path for context
            imports: List of import statements to validate

        Returns:
            List of ProtocolComplianceViolation for dependency violations
        """
        ...

    def aggregate_compliance_results(
        self, reports: List[ProtocolComplianceReport]
    ) -> ProtocolValidationResult:
        """
        Aggregate multiple compliance reports into single result.

        Args:
            reports: List of compliance reports to aggregate

        Returns:
            ProtocolValidationResult with aggregated compliance assessment
        """
        ...

    def add_custom_rule(self, rule: "ProtocolComplianceRule") -> None:
        """
        Add custom compliance rule.

        Args:
            rule: Custom compliance rule to add
        """
        ...

    def configure_onex_standards(self, standards: "ProtocolONEXStandards") -> None:
        """
        Configure ONEX standards.

        Args:
            standards: ONEX standards configuration
        """
        ...

    async def get_compliance_summary(
        self, reports: List[ProtocolComplianceReport]
    ) -> str:
        """
        Generate compliance summary from reports.

        Args:
            reports: List of compliance reports

        Returns:
            Human-readable compliance summary
        """
        ...
