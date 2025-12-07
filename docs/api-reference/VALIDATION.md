# Validation API Reference

![Version](https://img.shields.io/badge/SPI-v0.3.0-blue) ![Status](https://img.shields.io/badge/status-stable-green) ![Since](https://img.shields.io/badge/since-v0.3.0-lightgrey)

> **SPI Version**: 0.3.0 | **Status**: Stable | **Since**: v0.3.0

---

## Overview

The ONEX validation protocols provide comprehensive input validation, schema checking, compliance validation, and quality assurance capabilities. These protocols enable sophisticated validation patterns with contract compliance, import validation, and pre-commit checking.

## 🏗️ Protocol Architecture

The validation domain consists of **11 specialized protocols** that provide complete validation infrastructure:

### Validation Protocol

```python
from omnibase_spi.protocols.validation import ProtocolValidation
from omnibase_spi.protocols.types.protocol_core_types import ContextValue

@runtime_checkable
class ProtocolValidation(Protocol):
    """
    Core validation protocol for data validation operations.

    Provides comprehensive validation capabilities with
    schema validation, rule-based validation, and custom validators.

    Key Features:
        - Schema-based validation
        - Rule-based validation
        - Custom validator support
        - Performance optimization
        - Error reporting and diagnostics
        - Validation result caching
    """

    async def validate_data(
        self,
        data: ContextValue,
        validation_schema: ProtocolValidationSchema,
        options: ProtocolValidationOptions | None = None,
    ) -> ProtocolValidationResult: ...

    async def validate_against_rules(
        self,
        data: ContextValue,
        rules: list[ProtocolValidationRule],
    ) -> ProtocolValidationResult: ...

    async def validate_schema(
        self, schema: ProtocolValidationSchema
    ) -> ProtocolValidationResult: ...

    async def register_custom_validator(
        self,
        validator_name: str,
        validator_func: ProtocolCustomValidator,
    ) -> bool: ...

    async def unregister_custom_validator(
        self, validator_name: str
    ) -> bool: ...

    async def get_validation_metrics(
        self, time_range_hours: int = 24
    ) -> ProtocolValidationMetrics: ...

    async def clear_validation_cache(self) -> int: ...

    async def get_validation_statistics(
        self,
    ) -> ProtocolValidationStatistics: ...
```

### Compliance Validator Protocol

```python
@runtime_checkable
class ProtocolComplianceValidator(Protocol):
    """
    Protocol for compliance validation operations.

    Provides compliance checking with standards validation,
    policy enforcement, and regulatory compliance.

    Key Features:
        - Standards compliance checking
        - Policy enforcement
        - Regulatory compliance
        - Audit trail generation
        - Compliance reporting
        - Risk assessment
    """

    async def validate_compliance(
        self,
        data: ContextValue,
        compliance_standard: str,
        options: ProtocolComplianceOptions,
    ) -> ProtocolComplianceResult: ...

    async def check_policy_compliance(
        self,
        data: ContextValue,
        policy: ProtocolCompliancePolicy,
    ) -> ProtocolComplianceResult: ...

    async def validate_regulatory_compliance(
        self,
        data: ContextValue,
        regulation: str,
        jurisdiction: str,
    ) -> ProtocolComplianceResult: ...

    async def generate_compliance_report(
        self,
        compliance_results: list[ProtocolComplianceResult],
        format: LiteralReportFormat = "json",
    ) -> ProtocolComplianceReport: ...

    async def get_compliance_standards(
        self,
    ) -> list[ProtocolComplianceStandard]: ...

    async def register_compliance_standard(
        self, standard: ProtocolComplianceStandard
    ) -> bool: ...

    async def get_compliance_metrics(
        self, time_range_hours: int = 24
    ) -> ProtocolComplianceMetrics: ...

    async def assess_compliance_risk(
        self, data: ContextValue, context: dict[str, Any]
    ) -> ProtocolRiskAssessment: ...
```

### Contract Compliance Protocol

```python
@runtime_checkable
class ProtocolContractCompliance(Protocol):
    """
    Protocol for contract compliance validation.

    Provides contract validation with interface compliance,
    protocol adherence, and contract testing.

    Key Features:
        - Interface compliance checking
        - Protocol adherence validation
        - Contract testing and verification
        - API contract validation
        - Service contract compliance
        - Contract evolution support
    """

    async def validate_interface_compliance(
        self,
        implementation: Any,
        interface: Type[Any],
    ) -> ProtocolComplianceResult: ...

    async def validate_protocol_adherence(
        self,
        implementation: Any,
        protocol: Type[Protocol],
    ) -> ProtocolComplianceResult: ...

    async def validate_api_contract(
        self,
        api_spec: ProtocolAPIContract,
        implementation: Any,
    ) -> ProtocolComplianceResult: ...

    async def validate_service_contract(
        self,
        service_contract: ProtocolServiceContract,
        service_implementation: Any,
    ) -> ProtocolComplianceResult: ...

    async def generate_contract_report(
        self,
        compliance_results: list[ProtocolComplianceResult],
    ) -> ProtocolContractReport: ...

    async def validate_contract_evolution(
        self,
        old_contract: ProtocolContract,
        new_contract: ProtocolContract,
    ) -> ProtocolEvolutionResult: ...

    async def get_contract_metrics(
        self, time_range_hours: int = 24
    ) -> ProtocolContractMetrics: ...
```

### Input Validation Tool Protocol

```python
@runtime_checkable
class ProtocolInputValidationTool(Protocol):
    """
    Protocol for input validation tool operations.

    Provides specialized input validation with
    sanitization, format checking, and security validation.

    Key Features:
        - Input sanitization and cleaning
        - Format validation and conversion
        - Security validation and filtering
        - Performance optimization
        - Error handling and reporting
        - Validation rule management
    """

    async def validate_input(
        self,
        input_data: ContextValue,
        input_type: str,
        validation_rules: list[ProtocolInputValidationRule],
    ) -> ProtocolInputValidationResult: ...

    async def sanitize_input(
        self,
        input_data: ContextValue,
        sanitization_rules: list[ProtocolSanitizationRule],
    ) -> ContextValue: ...

    async def validate_format(
        self,
        input_data: ContextValue,
        expected_format: str,
    ) -> bool: ...

    async def convert_format(
        self,
        input_data: ContextValue,
        from_format: str,
        to_format: str,
    ) -> ContextValue: ...

    async def validate_security(
        self,
        input_data: ContextValue,
        security_rules: list[ProtocolSecurityRule],
    ) -> ProtocolSecurityValidationResult: ...

    async def get_validation_rules(
        self, input_type: str
    ) -> list[ProtocolInputValidationRule]: ...

    async def register_validation_rule(
        self,
        input_type: str,
        rule: ProtocolInputValidationRule,
    ) -> bool: ...

    async def get_input_validation_metrics(
        self, time_range_hours: int = 24
    ) -> ProtocolInputValidationMetrics: ...
```

### Import Validator Protocol

```python
@runtime_checkable
class ProtocolImportValidator(Protocol):
    """
    Protocol for import validation operations.

    Provides import validation with dependency checking,
    circular import detection, and import optimization.

    Key Features:
        - Import dependency validation
        - Circular import detection
        - Import optimization suggestions
        - Dependency graph analysis
        - Import performance monitoring
        - Import security validation
    """

    async def validate_imports(
        self,
        file_path: str,
        import_statements: list[str],
    ) -> ProtocolImportValidationResult: ...

    async def detect_circular_imports(
        self, file_path: str
    ) -> list[ProtocolCircularImport]: ...

    async def validate_import_dependencies(
        self,
        file_path: str,
        dependencies: list[str],
    ) -> ProtocolDependencyValidationResult: ...

    async def optimize_imports(
        self, file_path: str
    ) -> ProtocolImportOptimizationResult: ...

    async def get_import_graph(
        self, file_path: str
    ) -> ProtocolImportGraph: ...

    async def validate_import_security(
        self,
        file_path: str,
        import_statements: list[str],
    ) -> ProtocolSecurityValidationResult: ...

    async def get_import_metrics(
        self, file_path: str
    ) -> ProtocolImportMetrics: ...

    async def suggest_import_improvements(
        self, file_path: str
    ) -> list[ProtocolImportSuggestion]: ...
```

### Pre-commit Checker Protocol

```python
@runtime_checkable
class ProtocolPrecommitChecker(Protocol):
    """
    Protocol for pre-commit validation operations.

    Provides pre-commit validation with code quality checks,
    security scanning, and compliance validation.

    Key Features:
        - Code quality validation
        - Security vulnerability scanning
        - Compliance checking
        - Performance validation
        - Documentation validation
        - Test coverage checking
    """

    async def run_precommit_checks(
        self,
        file_paths: list[str],
        check_types: list[LiteralPrecommitCheckType],
    ) -> ProtocolPrecommitResult: ...

    async def validate_code_quality(
        self, file_paths: list[str]
    ) -> ProtocolCodeQualityResult: ...

    async def scan_security_vulnerabilities(
        self, file_paths: list[str]
    ) -> ProtocolSecurityScanResult: ...

    async def validate_compliance(
        self, file_paths: list[str]
    ) -> ProtocolComplianceResult: ...

    async def check_performance(
        self, file_paths: list[str]
    ) -> ProtocolPerformanceCheckResult: ...

    async def validate_documentation(
        self, file_paths: list[str]
    ) -> ProtocolDocumentationValidationResult: ...

    async def check_test_coverage(
        self, file_paths: list[str]
    ) -> ProtocolTestCoverageResult: ...

    async def get_precommit_metrics(
        self, time_range_hours: int = 24
    ) -> ProtocolPrecommitMetrics: ...
```

### Quality Validator Protocol

```python
@runtime_checkable
class ProtocolQualityValidator(Protocol):
    """
    Protocol for quality validation operations.

    Provides comprehensive quality validation with
    code quality metrics, performance validation, and maintainability checks.

    Key Features:
        - Code quality metrics
        - Performance validation
        - Maintainability assessment
        - Complexity analysis
        - Documentation quality
        - Test quality validation
    """

    async def validate_code_quality(
        self,
        file_paths: list[str],
        quality_standards: ProtocolQualityStandards,
    ) -> ProtocolQualityValidationResult: ...

    async def assess_maintainability(
        self, file_paths: list[str]
    ) -> ProtocolMaintainabilityAssessment: ...

    async def analyze_complexity(
        self, file_paths: list[str]
    ) -> ProtocolComplexityAnalysis: ...

    async def validate_performance(
        self, file_paths: list[str]
    ) -> ProtocolPerformanceValidationResult: ...

    async def check_documentation_quality(
        self, file_paths: list[str]
    ) -> ProtocolDocumentationQualityResult: ...

    async def validate_test_quality(
        self, file_paths: list[str]
    ) -> ProtocolTestQualityResult: ...

    async def get_quality_metrics(
        self, file_paths: list[str]
    ) -> ProtocolQualityMetrics: ...

    async def generate_quality_report(
        self,
        quality_results: list[ProtocolQualityValidationResult],
        format: LiteralReportFormat = "json",
    ) -> ProtocolQualityReport: ...
```

### Validation Orchestrator Protocol

```python
@runtime_checkable
class ProtocolValidationOrchestrator(Protocol):
    """
    Protocol for validation orchestration operations.

    Provides validation orchestration with workflow management,
    parallel validation, and result aggregation.

    Key Features:
        - Validation workflow orchestration
        - Parallel validation execution
        - Result aggregation and reporting
        - Validation pipeline management
        - Performance optimization
        - Error handling and recovery
    """

    async def orchestrate_validation(
        self,
        validation_requests: list[ProtocolValidationRequest],
        orchestration_options: ProtocolOrchestrationOptions,
    ) -> ProtocolOrchestrationResult: ...

    async def execute_validation_pipeline(
        self,
        pipeline: list[ProtocolValidationStep],
        data: ContextValue,
    ) -> ProtocolPipelineResult: ...

    async def parallel_validate(
        self,
        validation_tasks: list[ProtocolValidationTask],
        max_concurrent: int = 5,
    ) -> list[ProtocolValidationResult]: ...

    async def aggregate_validation_results(
        self,
        results: list[ProtocolValidationResult],
        aggregation_strategy: LiteralAggregationStrategy,
    ) -> ProtocolAggregatedResult: ...

    async def get_orchestration_metrics(
        self, time_range_hours: int = 24
    ) -> ProtocolOrchestrationMetrics: ...

    async def optimize_validation_workflow(
        self, workflow: ProtocolValidationWorkflow
    ) -> ProtocolOptimizationResult: ...
```

### Validation Provider Protocol

```python
@runtime_checkable
class ProtocolValidationProvider(Protocol):
    """
    Protocol for validation provider operations.

    Provides validation provider management with
    provider registration, discovery, and coordination.

    Key Features:
        - Validation provider registration
        - Provider discovery and selection
        - Provider coordination
        - Performance monitoring
        - Error handling and recovery
        - Provider lifecycle management
    """

    async def register_validation_provider(
        self,
        provider_info: ProtocolValidationProviderInfo,
        capabilities: list[str],
    ) -> str: ...

    async def unregister_validation_provider(
        self, provider_id: str
    ) -> bool: ...

    async def discover_validation_providers(
        self, capability: str | None = None
    ) -> list[ProtocolValidationProviderInfo]: ...

    async def select_validation_provider(
        self,
        validation_request: ProtocolValidationRequest,
        selection_criteria: ProtocolSelectionCriteria,
    ) -> ProtocolValidationProviderInfo: ...

    async def coordinate_validation_providers(
        self,
        coordination_task: ProtocolValidationCoordinationTask,
    ) -> ProtocolCoordinationResult: ...

    async def get_provider_metrics(
        self, provider_id: str
    ) -> ProtocolProviderMetrics: ...

    async def get_provider_health(
        self, provider_id: str
    ) -> ProtocolProviderHealth: ...
```

## 🔧 Type Definitions

### Validation Types

```python
LiteralReportFormat = Literal["json", "xml", "html", "pdf", "csv"]
"""
Report format types.

Values:
    json: JSON format
    xml: XML format
    html: HTML format
    pdf: PDF format
    csv: CSV format
"""

LiteralPrecommitCheckType = Literal[
    "code_quality", "security", "compliance", "performance", "documentation", "tests"
]
"""
Pre-commit check types.

Values:
    code_quality: Code quality validation
    security: Security vulnerability scanning
    compliance: Compliance checking
    performance: Performance validation
    documentation: Documentation validation
    tests: Test coverage and quality
"""

LiteralAggregationStrategy = Literal["all_pass", "any_pass", "majority_pass", "weighted"]
"""
Validation result aggregation strategies.

Values:
    all_pass: All validations must pass
    any_pass: Any validation can pass
    majority_pass: Majority of validations must pass
    weighted: Weighted aggregation based on importance
"""
```

## 🚀 Usage Examples

### Basic Validation

```python
from omnibase_spi.protocols.validation import ProtocolValidation

# Initialize validation
validator: ProtocolValidation = get_validator()

# Validate data against schema
validation_result = await validator.validate_data(
    data={"name": "John Doe", "age": 30, "email": "john@example.com"},
    validation_schema=ProtocolValidationSchema(
        type="object",
        properties={
            "name": {"type": "string", "minLength": 1},
            "age": {"type": "integer", "minimum": 0, "maximum": 120},
            "email": {"type": "string", "format": "email"}
        },
        required=["name", "age", "email"]
    )
)

print(f"Validation passed: {validation_result.valid}")
if not validation_result.valid:
    print(f"Validation errors: {validation_result.errors}")

# Validate against rules
rules = [
    ProtocolValidationRule("min_length", 5),
    ProtocolValidationRule("max_length", 100),
    ProtocolValidationRule("pattern", r"^[a-zA-Z\s]+$")
]

rule_result = await validator.validate_against_rules(
    data="Hello World",
    rules=rules
)
print(f"Rule validation passed: {rule_result.valid}")
```

### Compliance Validation

```python
from omnibase_spi.protocols.validation import ProtocolComplianceValidator

# Initialize compliance validator
compliance_validator: ProtocolComplianceValidator = get_compliance_validator()

# Validate compliance
compliance_result = await compliance_validator.validate_compliance(
    data=user_data,
    compliance_standard="GDPR",
    options=ProtocolComplianceOptions(
        strict_mode=True,
        include_audit_trail=True
    )
)

print(f"GDPR compliance: {compliance_result.compliant}")
print(f"Compliance score: {compliance_result.score}")

# Check policy compliance
policy_result = await compliance_validator.check_policy_compliance(
    data=user_data,
    policy=ProtocolCompliancePolicy(
        name="Data Retention Policy",
        rules=["max_retention_7_years", "encryption_required"]
    )
)

# Generate compliance report
report = await compliance_validator.generate_compliance_report(
    compliance_results=[compliance_result, policy_result],
    format="html"
)
```

### Input Validation

```python
from omnibase_spi.protocols.validation import ProtocolInputValidationTool

# Initialize input validation tool
input_validator: ProtocolInputValidationTool = get_input_validator()

# Validate input
input_result = await input_validator.validate_input(
    input_data="user@example.com",
    input_type="email",
    validation_rules=[
        ProtocolInputValidationRule("format", "email"),
        ProtocolInputValidationRule("max_length", 254),
        ProtocolInputValidationRule("allowed_domains", ["example.com", "test.com"])
    ]
)

print(f"Input validation passed: {input_result.valid}")

# Sanitize input
sanitized_input = await input_validator.sanitize_input(
    input_data="<script>alert('xss')</script>Hello World",
    sanitization_rules=[
        ProtocolSanitizationRule("remove_html_tags"),
        ProtocolSanitizationRule("escape_special_chars")
    ]
)
print(f"Sanitized input: {sanitized_input}")

# Validate security
security_result = await input_validator.validate_security(
    input_data=user_input,
    security_rules=[
        ProtocolSecurityRule("no_sql_injection"),
        ProtocolSecurityRule("no_xss"),
        ProtocolSecurityRule("no_path_traversal")
    ]
)
print(f"Security validation passed: {security_result.valid}")
```

### Pre-commit Validation

```python
from omnibase_spi.protocols.validation import ProtocolPrecommitChecker

# Initialize pre-commit checker
precommit_checker: ProtocolPrecommitChecker = get_precommit_checker()

# Run pre-commit checks
precommit_result = await precommit_checker.run_precommit_checks(
    file_paths=["src/main.py", "src/utils.py"],
    check_types=["code_quality", "security", "compliance"]
)

print(f"Pre-commit checks passed: {precommit_result.all_passed}")
print(f"Failed checks: {precommit_result.failed_checks}")

# Validate code quality
quality_result = await precommit_checker.validate_code_quality(
    file_paths=["src/main.py"]
)
print(f"Code quality score: {quality_result.quality_score}")

# Scan security vulnerabilities
security_scan = await precommit_checker.scan_security_vulnerabilities(
    file_paths=["src/main.py"]
)
print(f"Security vulnerabilities: {security_scan.vulnerability_count}")

# Check test coverage
coverage_result = await precommit_checker.check_test_coverage(
    file_paths=["src/main.py"]
)
print(f"Test coverage: {coverage_result.coverage_percentage}%")
```

### Quality Validation

```python
from omnibase_spi.protocols.validation import ProtocolQualityValidator

# Initialize quality validator
quality_validator: ProtocolQualityValidator = get_quality_validator()

# Validate code quality
quality_result = await quality_validator.validate_code_quality(
    file_paths=["src/main.py", "src/utils.py"],
    quality_standards=ProtocolQualityStandards(
        min_complexity_score=8.0,
        max_cyclomatic_complexity=10,
        min_test_coverage=80.0
    )
)

print(f"Quality validation passed: {quality_result.valid}")
print(f"Quality score: {quality_result.quality_score}")

# Assess maintainability
maintainability = await quality_validator.assess_maintainability(
    file_paths=["src/main.py"]
)
print(f"Maintainability score: {maintainability.score}")

# Analyze complexity
complexity = await quality_validator.analyze_complexity(
    file_paths=["src/main.py"]
)
print(f"Cyclomatic complexity: {complexity.cyclomatic_complexity}")
print(f"Cognitive complexity: {complexity.cognitive_complexity}")
```

### Validation Orchestration

```python
from omnibase_spi.protocols.validation import ProtocolValidationOrchestrator

# Initialize validation orchestrator
orchestrator: ProtocolValidationOrchestrator = get_validation_orchestrator()

# Orchestrate validation
orchestration_result = await orchestrator.orchestrate_validation(
    validation_requests=[
        ProtocolValidationRequest(
            data=user_data,
            validation_type="schema",
            priority="high"
        ),
        ProtocolValidationRequest(
            data=user_data,
            validation_type="compliance",
            priority="medium"
        )
    ],
    orchestration_options=ProtocolOrchestrationOptions(
        parallel_execution=True,
        max_concurrent=3,
        timeout_seconds=30
    )
)

print(f"Orchestration completed: {orchestration_result.success}")
print(f"Total validations: {orchestration_result.total_validations}")
print(f"Passed validations: {orchestration_result.passed_validations}")

# Execute validation pipeline
pipeline_result = await orchestrator.execute_validation_pipeline(
    pipeline=[
        ProtocolValidationStep("sanitize", {"rules": ["trim", "lowercase"]}),
        ProtocolValidationStep("validate", {"schema": "user_schema"}),
        ProtocolValidationStep("compliance", {"standard": "GDPR"})
    ],
    data=user_data
)

print(f"Pipeline result: {pipeline_result.success}")
print(f"Pipeline steps completed: {pipeline_result.completed_steps}")
```

## 🔍 Implementation Notes

### Custom Validators

Registering custom validation logic:

```python
# Register custom validator
async def custom_email_validator(data: str) -> bool:
    return "@" in data and "." in data.split("@")[-1]

await validator.register_custom_validator(
    "custom_email",
    custom_email_validator
)
```

### Validation Caching

Performance optimization with caching:

```python
# Clear validation cache
cache_cleared = await validator.clear_validation_cache()
print(f"Cleared {cache_cleared} cached validations")
```

### Parallel Validation

Efficient parallel validation:

```python
# Parallel validation
validation_tasks = [
    ProtocolValidationTask(data, "schema"),
    ProtocolValidationTask(data, "compliance"),
    ProtocolValidationTask(data, "security")
]

results = await orchestrator.parallel_validate(
    validation_tasks,
    max_concurrent=3
)
```

## 📊 Protocol Statistics

- **Total Protocols**: 11 validation protocols
- **Validation Types**: Schema, rule-based, compliance, security
- **Quality Assurance**: Code quality, maintainability, performance
- **Pre-commit Support**: Comprehensive pre-commit validation
- **Orchestration**: Parallel validation and workflow management
- **Provider Management**: Validation provider coordination
- **Reporting**: Multiple report formats and aggregation strategies

---

## See Also

- **[CONTRACTS.md](./CONTRACTS.md)** - Contract compilers that use validation for YAML contract validation
- **[CORE.md](./CORE.md)** - Core protocols including error handling patterns
- **[FILE-HANDLING.md](./FILE-HANDLING.md)** - File validation protocols
- **[EXCEPTIONS.md](./EXCEPTIONS.md)** - Exception hierarchy for validation errors
- **[README.md](./README.md)** - Complete API reference index

---

*This API reference is automatically generated from protocol definitions and maintained alongside the codebase.*
