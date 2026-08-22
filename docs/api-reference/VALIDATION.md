# Validation API Reference

![Version](https://img.shields.io/badge/SPI-v0.23.2-blue) ![Status](https://img.shields.io/badge/status-stable-green) ![Since](https://img.shields.io/badge/since-v0.3.0-lightgrey)

> **Package Version**: 0.23.2 | **Status**: Stable | **Since**: v0.3.0

---

## Overview

The `omnibase_spi.protocols.validation` domain provides the interfaces behind
four ONEX validation node archetypes — import validation (`NodeImportValidatorCompute`),
quality validation (`NodeQualityValidatorEffect`), compliance validation
(`NodeComplianceValidatorReducer`), and validation orchestration
(`NodeValidationOrchestratorOrchestrator`) — plus a generic protocol-conformance
validator and a validation-provider/session management surface. It does **not**
define a generic input-sanitization or pre-commit-checking protocol; those
concerns live elsewhere (see the notes on each section below).

> This page was rewritten against the live package for OMN-16127. Every
> class name below imports at the shown path; the previous revision
> documented several fabricated protocols (`ProtocolContractCompliance`,
> `ProtocolInputValidationTool`, `ProtocolPrecommitChecker`) that do not
> exist anywhere in `omnibase_spi`.

## 🏗️ Protocol Architecture

The validation domain exports **26 names** across generic protocol
validation, import validation, quality validation, compliance validation,
validation orchestration, provider/session management, and one standalone
execution-constraint validator.

### Generic Protocol Validator

```python
from omnibase_spi.protocols.validation import (
    ProtocolValidationError,
    ProtocolValidationResult,
    ProtocolValidator,
)

@runtime_checkable
class ProtocolValidator(Protocol):
    """
    Protocol for protocol compliance validation functionality.

    Validates whether an implementation satisfies a `typing.Protocol`
    requirement, with a configurable strict mode for additional rigor.
    This is the core "does this object implement that protocol"
    validation primitive; see `ProtocolValidationDecorator` for the
    protocol interface that concrete implementation packages may provide
    when they support decorator-based wrappers around the same check.
    """

    strict_mode: bool

    async def validate_implementation(
        self, implementation: object, protocol: type
    ) -> ProtocolValidationResult: ...
```

`ProtocolValidationResult` captures `is_valid`, `protocol_name`,
`implementation_name`, and lists of `ProtocolValidationError` (`errors`,
`warnings`), plus `add_error()` / `add_warning()` for incremental building
and `get_summary()`. `ProtocolValidationDecorator` is also only a protocol:
it specifies the optional interface a concrete implementation package may
offer for a class decorator (`validation_decorator(protocol)`) or an explicit
async call
(`validate_protocol_implementation(implementation, protocol, strict=...)`).
`omnibase_spi` exports these protocol names but does not ship concrete
decorators or runtime validation functions.

> There is no `ProtocolValidation` (singular, no trailing "or") name in this
> domain — that name lives in a different domain entirely:
> `omnibase_spi.protocols.onex.ProtocolValidation`, which validates ONEX
> envelope/reply/contract structures, not arbitrary implementations. Do not
> confuse the two.

### Import Validator Protocol

For `NodeImportValidatorCompute` implementations: validates import
statements and dependency chains against a repository-type-aware allow list.

```python
from omnibase_spi.protocols.validation import (
    ProtocolImportAnalysis,
    ProtocolImportValidationConfig,
    ProtocolImportValidator,
)

@runtime_checkable
class ProtocolImportValidator(Protocol):
    """
    Protocol interface for import validation in ONEX systems.

    Defines the interface for NodeImportValidatorCompute nodes that
    validate import statements, dependencies, and security implications
    across ONEX repositories.
    """

    validation_config: "ProtocolImportValidationConfig"
    security_scanning_enabled: bool
    dependency_analysis_enabled: bool

    async def validate_import(
        self, import_path: str, description: str, context: "JsonType | None" = None
    ) -> "ProtocolValidationResult": ...

    async def validate_from_import(
        self,
        from_path: str,
        import_items: str,
        description: str,
        context: "JsonType | None" = None,
    ) -> "ProtocolValidationResult": ...

    async def validate_import_security(
        self, import_path: str, context: "JsonType | None" = None
    ) -> ProtocolImportAnalysis: ...

    async def validate_dependency_chain(
        self, import_path: str, max_depth: int | None = None
    ) -> list[ProtocolImportAnalysis]: ...

    async def validate_repository_imports(
        self, repository_path: str, patterns: list[str] | None = None
    ) -> list["ProtocolValidationResult"]: ...

    async def get_validation_summary(self) -> "JsonType": ...

    async def configure_validation(
        self, config: "ProtocolImportValidationConfig"
    ) -> None: ...

    async def reset_validation_state(self) -> None: ...
```

`ProtocolImportValidationConfig` carries `allowed_imports`,
`allowed_import_items`, `repository_type`, and `validation_mode`.
`ProtocolImportAnalysis` is the result of a single-import security check:
`import_path`, `is_valid`, `security_risk`, `dependency_level`, plus
`get_risk_summary()` / `get_recommendations()`.

### Quality Validator Protocol

For `NodeQualityValidatorEffect` implementations: code quality, complexity,
and maintainability assessment.

```python
from omnibase_spi.protocols.validation import (
    ProtocolQualityIssue,
    ProtocolQualityMetrics,
    ProtocolQualityReport,
    ProtocolQualityStandards,
    ProtocolQualityValidator,
)

@runtime_checkable
class ProtocolQualityValidator(Protocol):
    """
    Protocol interface for code quality validation in ONEX systems.

    Defines the interface for NodeQualityValidatorEffect nodes that
    assess code quality, complexity metrics, maintainability, and
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
```

`ProtocolQualityMetrics` carries `cyclomatic_complexity`,
`maintainability_index`, `lines_of_code`, `code_duplication_percentage`,
`test_coverage_percentage`, `technical_debt_score`.
`ProtocolQualityStandards` defines the configurable thresholds
(`max_complexity`, `min_maintainability_score`, `max_line_length`, etc.)
that a `ProtocolQualityReport` is checked against.

### Compliance Validator Protocol

For `NodeComplianceValidatorReducer` implementations: ONEX naming,
architecture-layer, and directory-structure compliance.

```python
from omnibase_spi.protocols.validation import (
    ProtocolArchitectureCompliance,
    ProtocolComplianceReport,
    ProtocolComplianceRule,
    ProtocolComplianceValidator,
    ProtocolComplianceViolation,
    ProtocolONEXStandards,
)

@runtime_checkable
class ProtocolComplianceValidator(Protocol):
    """
    Protocol interface for compliance validation in ONEX systems.

    Defines the interface for NodeComplianceValidatorReducer nodes that
    validate compliance with ONEX standards, architectural patterns,
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
```

`ProtocolONEXStandards` defines naming-pattern regexes (`enum_naming_pattern`,
`model_naming_pattern`, `protocol_naming_pattern`, `node_naming_pattern`) and
`required_directories` / `forbidden_patterns`. `ProtocolArchitectureCompliance`
enforces the SPI/Core/Infra dependency direction (`allowed_dependencies`,
`forbidden_dependencies`). `ProtocolComplianceReport` aggregates
`ProtocolComplianceViolation` instances with `onex_compliance_score` and
`architecture_compliance_score`.

### Validation Orchestrator Protocol

For `NodeValidationOrchestratorOrchestrator` implementations: coordinates
import, quality, and compliance validation across a repository.

```python
from omnibase_spi.protocols.validation import (
    ProtocolValidationMetrics,
    ProtocolValidationOrchestrator,
    ProtocolValidationReport,
    ProtocolValidationScope,
    ProtocolValidationSummary,
    ProtocolValidationWorkflow,
)

@runtime_checkable
class ProtocolValidationOrchestrator(Protocol):
    """
    Protocol interface for validation orchestration in ONEX systems.

    Defines the interface for NodeValidationOrchestratorOrchestrator nodes
    that coordinate validation workflows across multiple validation nodes
    including import, quality, compliance, and security validation.
    """

    orchestration_id: str
    default_scope: "ProtocolValidationScope"

    def orchestrate_validation(
        self,
        scope: "ProtocolValidationScope",
        workflow: "ProtocolValidationWorkflow | None" = None,
    ) -> ProtocolValidationReport: ...

    async def validate_imports(
        self, scope: "ProtocolValidationScope"
    ) -> list["ProtocolValidationResult"]: ...

    async def validate_quality(
        self, scope: "ProtocolValidationScope"
    ) -> list["ProtocolValidationResult"]: ...

    async def validate_compliance(
        self, scope: "ProtocolValidationScope"
    ) -> list["ProtocolValidationResult"]: ...

    async def create_validation_workflow(
        self,
        workflow_name: str,
        validation_steps: list[str],
        dependencies: list[str],
        parallel_execution: bool | None = None,
    ) -> ProtocolValidationWorkflow: ...

    async def create_validation_scope(
        self,
        repository_path: str,
        validation_types: list[str] | None = None,
        file_patterns: list[str] | None = None,
        exclusion_patterns: list[str] | None = None,
    ) -> ProtocolValidationScope: ...

    async def get_orchestration_metrics(self) -> ProtocolValidationMetrics: ...
```

`ProtocolValidationScope` bounds a run (`repository_path`,
`validation_types`, `file_patterns`, `exclusion_patterns`).
`ProtocolValidationWorkflow` orders the steps (`validation_steps`,
`dependencies`, `parallel_execution`, `timeout_seconds`).
`ProtocolValidationReport` aggregates `scope`, `workflow`, `results`,
`summary` (`ProtocolValidationSummary`), and `metrics`
(`ProtocolValidationMetrics`) into one artifact.

### Validation Provider Protocol

Session-based validation-rule management — the central orchestration point
for rule registration, rule sets, and validation sessions.

```python
from omnibase_spi.protocols.validation import ProtocolValidationProvider

@runtime_checkable
class ProtocolValidationProvider(Protocol):
    """
    Protocol interface for comprehensive validation model providers.

    Orchestrates validation workflows, manages validation rules and rule
    sets, and provides quality-assurance capabilities across
    BASIC/STANDARD/COMPREHENSIVE/PARANOID validation levels and
    strict/lenient/smoke/regression/integration execution modes.
    """

    provider_id: str
    provider_name: str

    async def register_validation_rule(self, rule) -> bool: ...

    async def create_rule_set(
        self, rule_set_name: str, rule_ids: list[str], rule_set_metadata=None
    ): ...

    async def create_validation_session(
        self, session_name: str, session_metadata=None
    ): ...

    async def validate(
        self,
        targets: list,
        rule_sets: list,
        level: str = "STANDARD",
        mode: str = "strict",
        context: dict | None = None,
    ) -> list["ProtocolValidationResult"]: ...

    def is_validation_successful(
        self, results: list["ProtocolValidationResult"]
    ) -> bool: ...

    async def generate_quality_report(
        self, session, results: list["ProtocolValidationResult"], report_format=None
    ) -> str: ...
```

This is an abridged signature — the full protocol also defines rule
lifecycle management (`unregister_validation_rule`, `get_validation_rule`,
`list_validation_rules`), session management (`get_active_sessions`,
`cleanup_completed_sessions`), and provider health/caching
(`get_provider_health`, `clear_validation_cache`,
`optimize_rule_execution`). See
`src/omnibase_spi/protocols/validation/protocol_validation_provider.py`.

### Constraint Validator Protocol

A standalone protocol (not part of the four-node validation family above)
for `NodeConstraintValidatorCompute` implementations: validates that a set
of `ModelExecutionConstraints` are internally consistent for a given
`ModelExecutionProfile` — cycle detection, phase validation, and
determinism checks.

```python
from omnibase_core.models.common import ModelValidationResult
from omnibase_core.models.contracts import ModelExecutionProfile
from omnibase_core.models.contracts.model_execution_constraints import (
    ModelExecutionConstraints,
)
from omnibase_core.models.execution import ModelExecutionConflict
from omnibase_spi.protocols.validation import ProtocolConstraintValidator

@runtime_checkable
class ProtocolConstraintValidator(Protocol):
    """Protocol for validating execution constraints don't conflict.

    Detects circular dependencies, impossible phase constraints,
    conflicting must_run declarations, and nondeterministic effects
    scheduled in disallowed phases.
    """

    async def validate(
        self,
        profile: ModelExecutionProfile,
        constraints: list[ModelExecutionConstraints],
    ) -> ModelValidationResult[ModelExecutionConflict]: ...

    async def detect_cycles(
        self, constraints: list[ModelExecutionConstraints]
    ) -> list[ModelExecutionConflict]: ...

    async def validate_phase_constraints(
        self,
        profile: ModelExecutionProfile,
        constraints: list[ModelExecutionConstraints],
    ) -> list[ModelExecutionConflict]: ...

    async def validate_determinism(
        self,
        profile: ModelExecutionProfile,
        constraints: list[ModelExecutionConstraints],
    ) -> list[ModelExecutionConflict]: ...
```

Note this protocol returns `omnibase_core` models directly
(`ModelValidationResult`, `ModelExecutionConflict`) rather than the
`ProtocolValidationResult` used elsewhere on this page — it predates and is
independent of the four-node validation family.

### Input Validator Protocol

> Lives in the `schema` domain, not `validation` — imported here because it
> is the input-sanitization/security-validation counterpart to the
> validation-domain protocols above. There is no `ProtocolInputValidationTool`
> anywhere in the package.

```python
from omnibase_spi.protocols.schema import ProtocolInputValidator
from omnibase_spi.protocols.types import (
    ContextValue,
    LiteralValidationLevel,
    LiteralValidationMode,
)
from omnibase_spi.protocols.validation import ProtocolValidationResult

@runtime_checkable
class ProtocolInputValidator(Protocol):
    """
    Protocol for standardized input validation across ONEX services.

    Provides comprehensive input validation, sanitization, and security
    checking to prevent injection attacks and ensure data integrity.

    Key Features:
        - Multi-level validation (basic to paranoid)
        - Type-specific validation rules (string, numeric, collection)
        - Security-focused validation (SQL injection, XSS, path traversal)
        - Custom validation rule support
        - Batch validation for performance
    """

    async def validate_input(
        self,
        value: ContextValue,
        rules: list[str],
        validation_level: LiteralValidationLevel = "STANDARD",
    ) -> ProtocolValidationResult: ...

    async def validate_string(
        self,
        value: str,
        min_length: int | None,
        max_length: int | None,
        pattern: str | None,
        allow_empty: bool,
    ) -> ProtocolValidationResult: ...

    async def sanitize_input(
        self,
        value: str,
        remove_html: bool | None = None,
        escape_special_chars: bool | None = None,
        normalize_whitespace: bool | None = None,
    ) -> str: ...

    async def validate_batch(
        self,
        inputs: list[dict[str, object]],
        validation_mode: LiteralValidationMode = "strict",
    ) -> list[ProtocolValidationResult]: ...

    async def check_security_patterns(
        self,
        value: str,
        check_sql_injection: bool,
        check_xss: bool,
        check_path_traversal: bool,
        check_command_injection: bool,
    ) -> ProtocolValidationResult: ...
```

> Abridged — the full protocol also defines `validate_numeric`,
> `validate_collection`, `validate_email`, `validate_url`, and
> `add_custom_rule`. See
> `src/omnibase_spi/protocols/schema/protocol_input_validator.py`.

There is also no `ProtocolPrecommitChecker` in the package — no protocol in
`omnibase_spi` documents pre-commit-check orchestration. Pre-commit checking
in the ONEX platform is implemented directly in each repo's
`scripts/validation/` tree (see e.g. `omnibase_spi/scripts/validation/run_all_validations.py`
in this repository), not through an SPI protocol.

## 🚀 Usage Examples

### Generic Protocol Compliance

```python
from omnibase_spi.protocols.validation import ProtocolValidator

validator: ProtocolValidator = get_validator()
validator.strict_mode = True

result = await validator.validate_implementation(my_node_impl, ProtocolNode)

print(f"Valid: {result.is_valid}")
print(f"Protocol: {result.protocol_name}")
if not result.is_valid:
    for error in result.errors:
        print(f"[{error.severity}] {error.error_type}: {error.message}")
```

### Import Validation

```python
from omnibase_spi.protocols.validation import ProtocolImportValidator

import_validator: ProtocolImportValidator = get_import_validator()

analysis = await import_validator.validate_import_security("subprocess")
print(f"Security risk: {analysis.security_risk}")

result = await import_validator.validate_from_import(
    from_path="omnibase_infra.plugins",
    import_items="PluginComputeBase",
    description="spi module must not import infra",
)
if not result.is_valid:
    for error in result.errors:
        print(f"[{error.severity}] {error.message}")
```

### Compliance Validation

```python
from omnibase_spi.protocols.validation import ProtocolComplianceValidator

compliance_validator: ProtocolComplianceValidator = get_compliance_validator()

report = await compliance_validator.validate_file_compliance(
    "src/omnibase_spi/protocols/memory/protocol_example.py"
)

print(f"ONEX compliance: {report.onex_compliance_score:.0%}")
print(f"Architecture compliance: {report.architecture_compliance_score:.0%}")
if not report.overall_compliance:
    for fix in await report.get_priority_fixes():
        print(f"  - {fix.rule.rule_name}: {fix.violation_text}")
```

### Quality Validation

```python
from omnibase_spi.protocols.validation import ProtocolQualityValidator

quality_validator: ProtocolQualityValidator = get_quality_validator()

report = await quality_validator.validate_file_quality("src/main.py")
print(f"Score: {report.overall_score:.1f}/100")
print(f"Compliant: {report.standards_compliance}")

for issue in await report.get_critical_issues():
    print(f"[{issue.severity}] {issue.file_path}:{issue.line_number} {issue.message}")
```

### Validation Orchestration

```python
from omnibase_spi.protocols.validation import ProtocolValidationOrchestrator

orchestrator: ProtocolValidationOrchestrator = get_validation_orchestrator()

scope = await orchestrator.create_validation_scope(
    repository_path="/workspace/omnibase_spi",
    validation_types=["imports", "quality", "compliance"],
)

report = orchestrator.orchestrate_validation(scope)
print(f"Validation id: {report.validation_id}")
print(f"Success rate: {report.summary.success_rate:.0%}")
```

## 📊 Protocol Statistics

- **Total exported names**: 26 (`omnibase_spi.protocols.validation`)
- **Node families covered**: import, quality, compliance, orchestration
- **Related but not exported here**: `ProtocolInputValidator` (`schema`
  domain), `ProtocolConstraintValidator` (standalone, `omnibase_core`-typed
  return values)
- **Not in the package**: `ProtocolValidation`, `ProtocolContractCompliance`,
  `ProtocolInputValidationTool`, `ProtocolPrecommitChecker`

---

## See Also

- **[CONTRACTS.md](./CONTRACTS.md)** - Contract compilers that use validation for YAML contract validation
- **[CORE.md](./CORE.md)** - Core protocols including error handling patterns
- **[FILE-HANDLING.md](./FILE-HANDLING.md)** - File validation protocols
- **[EXCEPTIONS.md](./EXCEPTIONS.md)** - Exception hierarchy for validation errors
- **[README.md](./README.md)** - Complete API reference index

---

*This API reference is maintained alongside the codebase; verified against `src/omnibase_spi/protocols/validation/` on this refresh.*
