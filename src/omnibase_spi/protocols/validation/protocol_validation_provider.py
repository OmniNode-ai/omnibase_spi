"""
    Protocol interface for validation model providers in ONEX ecosystem.

    This protocol defines the interface for validation providers that orchestrate
    validation workflows, manage validation rules, and provide comprehensive
    quality assurance capabilities for ONEX services and components.

Domain: Core validation orchestration and quality assurance
Author: ONEX Framework Team
"""

from typing import TYPE_CHECKING, Protocol, TypeAlias, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.types.protocol_core_types import (
        ContextValue,
        ProtocolDateTime,
        ProtocolMetadata,
        ProtocolSemVer,
        ProtocolValidatable,
    )
    from omnibase_spi.protocols.validation.protocol_validation import (
        ProtocolValidationResult,
    )

from omnibase_spi.protocols.types.protocol_core_types import (
    LiteralValidationCategory,
    LiteralValidationLevel,
    LiteralValidationMode,
    LiteralValidationSeverity,
)

# ValidationTarget accepts any object for validation, not just ProtocolValidatable.
# While ProtocolValidatable objects provide built-in validation capabilities,
# validation rules often need to inspect arbitrary objects (configurations,
# data structures, etc.) that don't implement the protocol. The `object` type
# makes this explicit - validators should handle both protocol-conforming
# objects and plain Python objects gracefully.
ValidationTarget: TypeAlias = "ProtocolValidatable | object"


@runtime_checkable
class ProtocolValidationRule(Protocol):
    """
            Protocol for individual validation rules.

            Defines the structure for validation rules that can be applied
            to validate different aspects of ONEX components, configurations,
        and data structures.

        Key Features:
        - Rule identification and metadata
        - Severity levels for validation outcomes
        - Conditional rule application
        - Rule composition and dependencies

    Usage Example:
        ```python
    rule: "ProtocolValidationRule" = SomeValidationRule()
    if rule.is_applicable(target_object):
        result = rule.validate(target_object, context)
    if not result.is_valid:
        handle_validation_failure(result.errors)
        ```
    """

    rule_id: str
    rule_name: str
    rule_description: str
    rule_version: "ProtocolSemVer"
    severity: "LiteralValidationSeverity"
    category: "LiteralValidationCategory"

    def is_applicable(
        self, target: ValidationTarget, context: dict[str, "ContextValue"]
    ) -> bool: ...

    async def validate(
        self, target: ValidationTarget, context: dict[str, "ContextValue"]
    ) -> "ProtocolValidationResult": ...

    async def get_dependencies(self) -> list[str]: ...


@runtime_checkable
class ProtocolValidationRuleSet(Protocol):
    """
            Protocol for collections of validation rules.

            Manages groups of related validation rules with dependency resolution,
            conditional execution, and rule composition capabilities.

        Key Features:
        - Rule collection management
        - Dependency resolution and ordering
        - Conditional rule set application
        - Performance optimization through rule batching

    Usage Example:
        ```python
    rule_set: "ProtocolValidationRuleSet" = ComplianceRuleSet()
        applicable_rules = rule_set.get_applicable_rules(target, context)
        execution_order = rule_set.resolve_dependencies(applicable_rules)

    for rule in execution_order:
        result = rule.validate(target, context)
    if not result.is_valid:
        handle_rule_failure(rule, result)
        ```
    """

    rule_set_id: str
    rule_set_name: str
    rule_set_version: "ProtocolSemVer"
    rules: list["ProtocolValidationRule"]

    async def get_applicable_rules(
        self, target: ValidationTarget, context: dict[str, "ContextValue"]
    ) -> list["ProtocolValidationRule"]: ...

    def resolve_dependencies(
        self, rules: list["ProtocolValidationRule"]
    ) -> list["ProtocolValidationRule"]: ...

    async def validate_rule_set(self, context: dict[str, "ContextValue"]) -> bool: ...


@runtime_checkable
class ProtocolValidationSession(Protocol):
    """
            Protocol for validation execution sessions.

            Manages the execution context and state for validation operations,
            providing session isolation, progress tracking, and result aggregation.

        Key Features:
        - Session isolation and state management
        - Progress tracking and cancellation
        - Result aggregation and reporting
        - Performance metrics and diagnostics

    Usage Example:
        ```python
    session: "ProtocolValidationSession" = ValidationSession()
        session.start_validation("component_validation", targets)

    try:
        results = session.execute_validation_rules(rule_set, level, mode)
        summary = session.get_session_summary()
    if not summary.overall_success:
        handle_validation_failures(results)
    finally:
        session.end_validation()
        ```
    """

    session_id: str
    session_name: str
    start_time: "ProtocolDateTime"
    end_time: "ProtocolDateTime | None"
    is_active: bool

    async def start_validation(
        self,
        validation_name: str,
        targets: list[ValidationTarget],
        metadata: "ProtocolMetadata | None" = None,
    ) -> None: ...

    async def execute_validation_rules(
        self,
        rule_set: "ProtocolValidationRuleSet",
        level: "LiteralValidationLevel",
        mode: "LiteralValidationMode",
        context: dict[str, "ContextValue"] | None = None,
    ) -> list["ProtocolValidationResult"]: ...

    async def get_session_progress(self) -> dict[str, "ContextValue"]: ...

    async def get_session_summary(self) -> dict[str, "ContextValue"]: ...

    def cancel_validation(self) -> bool: ...

    def end_validation(self) -> None: ...


@runtime_checkable
class ProtocolValidationProvider(Protocol):
    """
            Protocol interface for comprehensive validation model providers in ONEX systems.

            This protocol defines the interface for validation providers that orchestrate
            validation workflows, manage validation rules and rule sets, and provide
        comprehensive quality assurance capabilities for ONEX services and components.

        The validation provider serves as the central orchestration point for all
        validation activities, managing rule execution, result aggregation, and
        quality reporting across different validation levels and modes.

    Key Features:
        - Multi-level validation orchestration (BASIC, STANDARD, COMPREHENSIVE, PARANOID)
        - Multiple execution modes (strict, lenient, smoke, regression, integration)
        - Dynamic rule management and composition
        - Session-based validation execution with progress tracking
        - Comprehensive result reporting and quality metrics
        - Performance optimization and caching
        - Plugin architecture for custom validation rules

    Validation Levels:
    - BASIC: Essential validation only (fast performance)
    - STANDARD: Normal validation with common checks
    - COMPREHENSIVE: Thorough validation with detailed analysis
    - PARANOID: Maximum validation with all possible checks

    Validation Modes:
    - strict: Fail on any validation error
    - lenient: Allow warnings but fail on errors
    - smoke: Basic functionality validation
    - regression: Validate against known good states
    - integration: Cross-system validation testing

    Usage Example:
        ```python
        # Initialize validation provider
    provider: "ProtocolValidationProvider" = SomeValidationProvider()

    # Register validation rules
        compliance_rules = provider.create_rule_set(
        "compliance_validation",
        ["namespace_isolation", "protocol_purity", "import_validation"]
        )

    # Execute comprehensive validation
        session = provider.create_validation_session("component_audit")
        results = provider.validate_with_session(
        session=session,
        targets=[component1, component2],
        rule_sets=[compliance_rules],
        level="COMPREHENSIVE",
        mode="strict"
        )

    # Process results
    if not provider.is_validation_successful(results):
        failures = provider.get_critical_issues(results)
        handle_validation_failures(failures)

    # Generate quality report
        report = provider.generate_quality_report(session, results)
        save_validation_report(report)
        ```

    Integration Patterns:
        - Works with existing ProtocolValidationResult from protocol_core_types
        - Integrates with ONEX observability and monitoring systems
        - Supports custom rule development and plugin architecture
        - Compatible with CI/CD pipeline integration
        - Provides metrics for quality dashboards and alerting
    """

    provider_id: str
    provider_name: str
    provider_version: "ProtocolSemVer"
    supported_levels: list["LiteralValidationLevel"]
    supported_modes: list["LiteralValidationMode"]

    async def register_validation_rule(
        self, rule: "ProtocolValidationRule"
    ) -> bool: ...

    async def unregister_validation_rule(self, rule_id: str) -> bool: ...

    async def get_validation_rule(
        self, rule_id: str
    ) -> "ProtocolValidationRule | None": ...

    async def list_validation_rules(
        self,
        category_filter: "LiteralValidationCategory | None" = None,
        severity_filter: "LiteralValidationSeverity | None" = None,
    ) -> list["ProtocolValidationRule"]: ...

    async def create_rule_set(
        self,
        rule_set_name: str,
        rule_ids: list[str],
        rule_set_metadata: dict[str, "ContextValue"] | None = None,
    ) -> "ProtocolValidationRuleSet": ...

    async def create_validation_session(
        self,
        session_name: str,
        session_metadata: dict[str, "ContextValue"] | None = None,
    ) -> "ProtocolValidationSession": ...

    async def get_active_sessions(self) -> list["ProtocolValidationSession"]: ...

    def cleanup_completed_sessions(
        self, older_than_hours: int | None = None
    ) -> int: ...

    async def validate(
        self,
        targets: list[ValidationTarget],
        rule_sets: list["ProtocolValidationRuleSet"],
        level: "LiteralValidationLevel" = "STANDARD",
        mode: "LiteralValidationMode" = "strict",
        context: dict[str, "ContextValue"] | None = None,
    ) -> list["ProtocolValidationResult"]: ...

    async def validate_with_session(
        self,
        session: "ProtocolValidationSession",
        targets: list[ValidationTarget],
        rule_sets: list["ProtocolValidationRuleSet"],
        level: "LiteralValidationLevel" = "STANDARD",
        mode: "LiteralValidationMode" = "strict",
        context: dict[str, "ContextValue"] | None = None,
    ) -> list["ProtocolValidationResult"]: ...

    async def validate_single(
        self,
        target: ValidationTarget,
        rule_set: "ProtocolValidationRuleSet",
        level: "LiteralValidationLevel" = "STANDARD",
        mode: "LiteralValidationMode" = "strict",
        context: dict[str, "ContextValue"] | None = None,
    ) -> "ProtocolValidationResult": ...

    def is_validation_successful(
        self, results: list["ProtocolValidationResult"]
    ) -> bool: ...

    async def get_critical_issues(
        self, results: list["ProtocolValidationResult"]
    ) -> list["ProtocolValidationResult"]: ...

    async def get_validation_summary(
        self, results: list["ProtocolValidationResult"]
    ) -> dict[str, "ContextValue"]: ...

    async def generate_quality_report(
        self,
        session: "ProtocolValidationSession",
        results: list["ProtocolValidationResult"],
        report_format: str | None = None,
    ) -> str: ...

    async def get_provider_metrics(self) -> dict[str, "ContextValue"]: ...

    def optimize_rule_execution(
        self, rule_sets: list["ProtocolValidationRuleSet"]
    ) -> list["ProtocolValidationRuleSet"]: ...

    def clear_validation_cache(self) -> bool: ...

    def configure_provider(self, configuration: dict[str, "ContextValue"]) -> bool: ...

    async def get_provider_health(self) -> dict[str, "ContextValue"]: ...

    async def reset_provider_state(self) -> bool: ...
