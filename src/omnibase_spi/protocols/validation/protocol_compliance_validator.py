"""
Protocol interface for compliance validation in ONEX ecosystem.

This protocol defines the interface for validating compliance with ONEX
standards, architectural patterns, and ecosystem requirements for
NodeComplianceValidatorReducer implementations.
"""

from typing import List, Protocol, runtime_checkable

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

    async def check_compliance(self, content: str, context: str) -> bool: ...

    async def get_fix_suggestion(self) -> str: ...


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

    async def get_violation_summary(self) -> str: ...

    async def get_compliance_impact(self) -> str: ...


@runtime_checkable
class ProtocolONEXStandards(Protocol):
    """Protocol for ONEX ecosystem standards."""

    enum_naming_pattern: str
    model_naming_pattern: str
    protocol_naming_pattern: str
    node_naming_pattern: str
    required_directories: List[str]
    forbidden_patterns: List[str]

    async def validate_enum_naming(self, name: str) -> bool: ...

    async def validate_model_naming(self, name: str) -> bool: ...

    async def validate_protocol_naming(self, name: str) -> bool: ...

    async def validate_node_naming(self, name: str) -> bool: ...


@runtime_checkable
class ProtocolArchitectureCompliance(Protocol):
    """Protocol for architectural compliance checking."""

    allowed_dependencies: List[str]
    forbidden_dependencies: List[str]
    required_patterns: List[str]
    layer_violations: List[str]

    async def check_dependency_compliance(self, imports: List[str]) -> List[str]: ...

    async def validate_layer_separation(
        self, file_path: str, imports: List[str]
    ) -> List[str]: ...


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

    async def get_compliance_summary(self) -> str: ...

    async def get_priority_fixes(self) -> List[ProtocolComplianceViolation]: ...


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
    ) -> ProtocolComplianceReport: ...

    async def validate_repository_compliance(
        self, repository_path: str, file_patterns: List[str] | None = None
    ) -> List[ProtocolComplianceReport]: ...

    async def validate_onex_naming(
        self, file_path: str, content: str | None = None
    ) -> List[ProtocolComplianceViolation]: ...

    async def validate_architecture_compliance(
        self, file_path: str, content: str | None = None
    ) -> List[ProtocolComplianceViolation]: ...

    async def validate_directory_structure(
        self, repository_path: str
    ) -> List[ProtocolComplianceViolation]: ...

    async def validate_dependency_compliance(
        self, file_path: str, imports: List[str]
    ) -> List[ProtocolComplianceViolation]: ...

    def aggregate_compliance_results(
        self, reports: List["ProtocolComplianceReport"]
    ) -> ProtocolValidationResult: ...

    def add_custom_rule(self, rule: "ProtocolComplianceRule") -> None: ...

    def configure_onex_standards(self, standards: "ProtocolONEXStandards") -> None: ...

    async def get_compliance_summary(
        self, reports: List[ProtocolComplianceReport]
    ) -> str: ...
