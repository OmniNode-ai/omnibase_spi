"""
Protocol interface for compliance validation in ONEX ecosystem.

This protocol defines the interface for validating compliance with ONEX
standards, architectural patterns, and ecosystem requirements for
NodeComplianceValidatorReducer implementations.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.validation.protocol_validation import (
        ProtocolValidationResult,
    )


@runtime_checkable
class ProtocolComplianceRule(Protocol):
    """
    Protocol for ONEX compliance rule definition and checking.

    Defines a single compliance rule with validation logic, severity
    classification, and automated fix suggestions. Rules validate code
    against ONEX standards including naming conventions, architecture
    patterns, and ecosystem requirements.

    Example:
        ```python
        async def apply_rule(rule: ProtocolComplianceRule, code: str) -> dict:
            # Check if code complies with the rule
            complies = await rule.check_compliance(code, "validation")

            if not complies:
                # Get automated fix suggestion
                suggestion = await rule.get_fix_suggestion()
                return {
                    "complies": False,
                    "rule_id": rule.rule_id,
                    "severity": rule.severity,
                    "message": rule.violation_message,
                    "fix": suggestion
                }

            return {"complies": True, "rule_id": rule.rule_id}
        ```

    Key Features:
        - **Unique Identification**: Rule ID and descriptive name
        - **Categorization**: Category-based rule organization
        - **Severity Levels**: Critical, high, medium, low classifications
        - **Pattern Matching**: Required pattern for compliance checking
        - **Violation Messages**: Clear violation explanations
        - **Fix Suggestions**: Automated remediation guidance

    See Also:
        - ProtocolComplianceViolation: Violation representation
        - ProtocolComplianceValidator: Complete validation system
        - ProtocolONEXStandards: ONEX ecosystem standards
    """

    rule_id: str
    rule_name: str
    category: str
    severity: str
    description: str
    required_pattern: str
    violation_message: str

    async def check_compliance(self, content: str, context: str) -> bool: ...

    async def get_fix_suggestion(self) -> str: ...


@runtime_checkable
class ProtocolComplianceViolation(Protocol):
    """
    Protocol for representing a detected compliance violation.

    Captures complete violation information including the violated rule,
    location, severity, and automated fix capabilities. Provides violation
    summaries and impact analysis for prioritization and remediation.

    Example:
        ```python
        async def process_violation(
            violation: ProtocolComplianceViolation
        ) -> dict:
            # Get violation details
            summary = await violation.get_violation_summary()
            impact = await violation.get_compliance_impact()

            print(f"File: {violation.file_path}:{violation.line_number}")
            print(f"Rule: {violation.rule.rule_name}")
            print(f"Severity: {violation.severity}")
            print(f"Summary: {summary}")
            print(f"Impact: {impact}")

            # Attempt automated fix if possible
            if violation.auto_fixable:
                print(f"Fix: {violation.fix_suggestion}")
                return {"status": "auto_fixable", "fix": violation.fix_suggestion}

            return {"status": "manual_review", "impact": impact}
        ```

    Key Features:
        - **Rule Reference**: Associated compliance rule details
        - **Location Tracking**: File path and line number precision
        - **Violation Context**: Actual violating text/code
        - **Severity Classification**: Severity level inheritance
        - **Fix Automation**: Auto-fixable flag and suggestions
        - **Impact Analysis**: Compliance impact assessment

    See Also:
        - ProtocolComplianceRule: Rule definition protocol
        - ProtocolComplianceReport: Aggregated violation reporting
        - ProtocolComplianceValidator: Validation orchestration
    """

    rule: "ProtocolComplianceRule"
    file_path: str
    line_number: int
    violation_text: str
    severity: str
    fix_suggestion: str
    auto_fixable: bool

    async def get_violation_summary(self) -> str: ...

    async def get_compliance_impact(self) -> str: ...


@runtime_checkable
class ProtocolONEXStandards(Protocol):
    """
    Protocol for ONEX ecosystem architectural standards and conventions.

    Defines and validates ONEX naming conventions, directory structure
    requirements, and forbidden patterns. Ensures consistent architecture
    across ONEX components including protocols, models, nodes, and enums.

    Example:
        ```python
        async def validate_onex_component(
            standards: ProtocolONEXStandards,
            component_type: str,
            name: str
        ) -> bool:
            # Validate based on component type
            if component_type == "enum":
                is_valid = await standards.validate_enum_naming(name)
                pattern = standards.enum_naming_pattern
            elif component_type == "model":
                is_valid = await standards.validate_model_naming(name)
                pattern = standards.model_naming_pattern
            elif component_type == "protocol":
                is_valid = await standards.validate_protocol_naming(name)
                pattern = standards.protocol_naming_pattern
            elif component_type == "node":
                is_valid = await standards.validate_node_naming(name)
                pattern = standards.node_naming_pattern
            else:
                return False

            if not is_valid:
                print(f"Invalid {component_type} name: {name}")
                print(f"Expected pattern: {pattern}")

            return is_valid
        ```

    Key Features:
        - **Naming Patterns**: Regex patterns for ONEX components
        - **Enum Standards**: EnumXxx naming convention validation
        - **Model Standards**: ModelXxx naming convention validation
        - **Protocol Standards**: ProtocolXxx naming convention validation
        - **Node Standards**: NodeXxxType naming convention validation
        - **Directory Structure**: Required directory enforcement
        - **Forbidden Patterns**: Anti-pattern detection

    See Also:
        - ProtocolComplianceRule: Individual compliance rules
        - ProtocolComplianceValidator: Complete validation system
        - ProtocolArchitectureCompliance: Architecture layer validation
    """

    enum_naming_pattern: str
    model_naming_pattern: str
    protocol_naming_pattern: str
    node_naming_pattern: str
    required_directories: list[str]
    forbidden_patterns: list[str]

    async def validate_enum_naming(self, name: str) -> bool: ...

    async def validate_model_naming(self, name: str) -> bool: ...

    async def validate_protocol_naming(self, name: str) -> bool: ...

    async def validate_node_naming(self, name: str) -> bool: ...


@runtime_checkable
class ProtocolArchitectureCompliance(Protocol):
    """
    Protocol for architectural compliance checking and layer separation.

    Defines and enforces architectural rules including allowed and forbidden
    dependencies, required code patterns, and layer separation violations.
    Ensures ONEX components follow the prescribed architecture with proper
    dependency direction between SPI, Core, and Infra layers.

    Attributes:
        allowed_dependencies: List of allowed import patterns (e.g., "omnibase_core.*").
        forbidden_dependencies: List of forbidden import patterns (e.g., "omnibase_infra.*").
        required_patterns: List of patterns that must be present in compliant code.
        layer_violations: Accumulated list of detected layer violations.

    Example:
        ```python
        class SPIArchitectureRules:
            allowed_dependencies: list[str] = [
                "typing",
                "omnibase_core.models.*",
                "omnibase_spi.protocols.*"
            ]
            forbidden_dependencies: list[str] = [
                "omnibase_infra.*",
                "omniagent.*"
            ]
            required_patterns: list[str] = ["@runtime_checkable", "Protocol"]
            layer_violations: list[str] = []

            async def check_dependency_compliance(self, imports: list[str]) -> list[str]:
                violations = []
                for imp in imports:
                    if any(imp.startswith(f) for f in self.forbidden_dependencies):
                        violations.append(f"Forbidden import: {imp}")
                return violations

            async def validate_layer_separation(
                self, file_path: str, imports: list[str]
            ) -> list[str]:
                return await self.check_dependency_compliance(imports)

        rules = SPIArchitectureRules()
        assert isinstance(rules, ProtocolArchitectureCompliance)
        ```
    """

    allowed_dependencies: list[str]
    forbidden_dependencies: list[str]
    required_patterns: list[str]
    layer_violations: list[str]

    async def check_dependency_compliance(self, imports: list[str]) -> list[str]: ...

    async def validate_layer_separation(
        self, file_path: str, imports: list[str]
    ) -> list[str]: ...


@runtime_checkable
class ProtocolComplianceReport(Protocol):
    """
    Protocol for comprehensive compliance report with scores and recommendations.

    Aggregates compliance validation results for a single file including
    all violations, compliance scores for ONEX and architecture rules,
    overall compliance status, and prioritized fix recommendations.
    Serves as the primary output artifact from file-level compliance checks.

    Attributes:
        file_path: Path to the file that was validated.
        violations: List of all detected compliance violations.
        onex_compliance_score: ONEX naming and convention compliance (0.0-1.0).
        architecture_compliance_score: Architecture layer compliance (0.0-1.0).
        overall_compliance: Boolean indicating overall compliance status.
        critical_violations: Count of critical-severity violations.
        recommendations: List of prioritized recommendations for improvement.

    Example:
        ```python
        class FileComplianceReport:
            file_path: str = "/workspace/omnibase_spi/protocols/memory/protocol_example.py"
            violations: list[ProtocolComplianceViolation] = [violation1, violation2]
            onex_compliance_score: float = 0.85
            architecture_compliance_score: float = 1.0
            overall_compliance: bool = False
            critical_violations: int = 1
            recommendations: list[str] = [
                "Fix critical: Add @runtime_checkable decorator",
                "Minor: Use Protocol suffix in class name"
            ]

            async def get_compliance_summary(self) -> str:
                return f"Compliance: {self.onex_compliance_score:.0%} ONEX, {self.architecture_compliance_score:.0%} Architecture"

            async def get_priority_fixes(self) -> list[ProtocolComplianceViolation]:
                return sorted(self.violations, key=lambda v: v.severity)

        report = FileComplianceReport()
        assert isinstance(report, ProtocolComplianceReport)
        assert report.critical_violations == 1
        ```
    """

    file_path: str
    violations: list[ProtocolComplianceViolation]
    onex_compliance_score: float
    architecture_compliance_score: float
    overall_compliance: bool
    critical_violations: int
    recommendations: list[str]

    async def get_compliance_summary(self) -> str: ...

    async def get_priority_fixes(self) -> list[ProtocolComplianceViolation]: ...


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
    custom_rules: list[ProtocolComplianceRule]
    strict_mode: bool

    async def validate_file_compliance(
        self, file_path: str, content: str | None = None
    ) -> ProtocolComplianceReport: ...

    async def validate_repository_compliance(
        self, repository_path: str, file_patterns: list[str] | None = None
    ) -> list[ProtocolComplianceReport]: ...

    async def validate_onex_naming(
        self, file_path: str, content: str | None = None
    ) -> list[ProtocolComplianceViolation]: ...

    async def validate_architecture_compliance(
        self, file_path: str, content: str | None = None
    ) -> list[ProtocolComplianceViolation]: ...

    async def validate_directory_structure(
        self, repository_path: str
    ) -> list[ProtocolComplianceViolation]: ...

    async def validate_dependency_compliance(
        self, file_path: str, imports: list[str]
    ) -> list[ProtocolComplianceViolation]: ...

    async def aggregate_compliance_results(
        self, reports: list["ProtocolComplianceReport"]
    ) -> "ProtocolValidationResult": ...

    def add_custom_rule(self, rule: "ProtocolComplianceRule") -> None: ...

    def configure_onex_standards(self, standards: "ProtocolONEXStandards") -> None: ...

    async def get_compliance_summary(
        self, reports: list[ProtocolComplianceReport]
    ) -> str: ...
