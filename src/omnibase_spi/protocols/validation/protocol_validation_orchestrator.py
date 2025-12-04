"""
Protocol interface for validation orchestration in ONEX ecosystem.

This protocol defines the interface for coordinating validation workflows
across multiple validation nodes, providing comprehensive validation
orchestration for NodeValidationOrchestrator implementations.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.validation.protocol_validation import (
        ProtocolValidationResult,
    )


@runtime_checkable
class ProtocolValidationScope(Protocol):
    """
    Protocol for defining validation scope and target specification.

    Defines the boundaries and parameters for validation operations,
    including which files to validate, which validation types to apply,
    and exclusion patterns for filtering. Enables precise control over
    validation coverage in repository-wide validation workflows.

    Attributes:
        repository_path: Absolute path to the repository root directory.
        validation_types: List of validation types to perform (e.g., "imports", "quality").
        file_patterns: Glob patterns for files to include (e.g., "**/*.py").
        exclusion_patterns: Glob patterns for files to exclude (e.g., "**/tests/**").
        validation_depth: Depth of validation ("shallow", "standard", "deep").

    Example:
        ```python
        class PythonValidationScope:
            repository_path: str = "/workspace/omnibase_spi"
            validation_types: list[str] = ["imports", "quality", "compliance"]
            file_patterns: list[str] = ["**/*.py"]
            exclusion_patterns: list[str] = ["**/tests/**", "**/__pycache__/**"]
            validation_depth: str = "standard"

            async def should_validate_file(self, file_path: str) -> bool:
                return file_path.endswith(".py") and "/tests/" not in file_path

            async def get_repository_name(self) -> str:
                return "omnibase_spi"

        scope = PythonValidationScope()
        assert isinstance(scope, ProtocolValidationScope)
        ```
    """

    repository_path: str
    validation_types: list[str]
    file_patterns: list[str]
    exclusion_patterns: list[str]
    validation_depth: str

    async def should_validate_file(self, file_path: str) -> bool: ...

    async def get_repository_name(self) -> str: ...


@runtime_checkable
class ProtocolValidationWorkflow(Protocol):
    """
    Protocol for validation workflow definition and execution planning.

    Defines a validation workflow including ordered steps, dependencies
    between steps, and execution parameters. Supports both sequential
    and parallel execution modes with configurable timeout handling.

    Attributes:
        workflow_id: Unique identifier for this workflow instance.
        workflow_name: Human-readable name for the workflow.
        validation_steps: Ordered list of validation step identifiers.
        dependencies: List of external dependencies required by the workflow.
        parallel_execution: Whether steps can execute in parallel when possible.
        timeout_seconds: Maximum execution time before workflow timeout.

    Example:
        ```python
        class ComprehensiveValidationWorkflow:
            workflow_id: str = "wf_comprehensive_001"
            workflow_name: str = "Comprehensive ONEX Validation"
            validation_steps: list[str] = ["imports", "quality", "compliance", "security"]
            dependencies: list[str] = ["omnibase_core"]
            parallel_execution: bool = True
            timeout_seconds: int = 300

            async def get_execution_order(self) -> list[str]:
                return ["imports", "quality", "compliance", "security"]

        workflow = ComprehensiveValidationWorkflow()
        assert isinstance(workflow, ProtocolValidationWorkflow)
        ```
    """

    workflow_id: str
    workflow_name: str
    validation_steps: list[str]
    dependencies: list[str]
    parallel_execution: bool
    timeout_seconds: int

    async def get_execution_order(self) -> list[str]: ...


@runtime_checkable
class ProtocolValidationMetrics(Protocol):
    """
    Protocol for validation execution metrics and performance tracking.

    Captures performance metrics during validation execution including
    file counts, timing information, resource usage, and caching
    effectiveness. Enables performance monitoring and optimization
    of validation workflows.

    Attributes:
        total_files_processed: Number of files validated in this execution.
        validation_duration_seconds: Total wall-clock execution time.
        memory_usage_mb: Peak memory usage during validation in megabytes.
        parallel_executions: Number of parallel validation tasks executed.
        cache_hit_rate: Percentage of validation results served from cache (0.0-1.0).

    Example:
        ```python
        class ValidationMetricsResult:
            total_files_processed: int = 150
            validation_duration_seconds: float = 45.3
            memory_usage_mb: float = 256.5
            parallel_executions: int = 4
            cache_hit_rate: float = 0.75

            async def get_performance_summary(self) -> str:
                return f"Processed {self.total_files_processed} files in {self.validation_duration_seconds}s"

        metrics = ValidationMetricsResult()
        assert isinstance(metrics, ProtocolValidationMetrics)
        assert metrics.cache_hit_rate == 0.75
        ```
    """

    total_files_processed: int
    validation_duration_seconds: float
    memory_usage_mb: float
    parallel_executions: int
    cache_hit_rate: float

    async def get_performance_summary(self) -> str: ...


@runtime_checkable
class ProtocolValidationSummary(Protocol):
    """
    Protocol for validation result summary with aggregated statistics.

    Provides a high-level summary of validation results including
    pass/fail counts, warning tallies, and success rate calculations.
    Used for quick assessment of validation outcomes and reporting.

    Attributes:
        total_validations: Total number of validation checks performed.
        passed_validations: Number of validations that passed.
        failed_validations: Number of validations that failed.
        warning_count: Number of warnings generated during validation.
        critical_issues: Number of critical-severity issues found.
        success_rate: Ratio of passed to total validations (0.0-1.0).

    Example:
        ```python
        class ValidationSummaryResult:
            total_validations: int = 500
            passed_validations: int = 475
            failed_validations: int = 25
            warning_count: int = 12
            critical_issues: int = 3
            success_rate: float = 0.95

            async def get_overall_status(self) -> str:
                if self.critical_issues > 0:
                    return "FAILED"
                return "PASSED" if self.success_rate >= 0.9 else "WARNING"

        summary = ValidationSummaryResult()
        assert isinstance(summary, ProtocolValidationSummary)
        assert summary.success_rate == 0.95
        ```
    """

    total_validations: int
    passed_validations: int
    failed_validations: int
    warning_count: int
    critical_issues: int
    success_rate: float

    async def get_overall_status(self) -> str: ...


@runtime_checkable
class ProtocolValidationReport(Protocol):
    """
    Protocol for comprehensive validation reports with full execution details.

    Aggregates all validation information including scope, workflow,
    individual results, summary statistics, performance metrics, and
    actionable recommendations. Serves as the primary output artifact
    from validation orchestration operations.

    Attributes:
        validation_id: Unique identifier for this validation run.
        repository_name: Name of the validated repository.
        scope: Validation scope configuration used for this run.
        workflow: Workflow definition that was executed.
        results: List of individual validation results.
        summary: Aggregated summary statistics.
        metrics: Performance and execution metrics.
        recommendations: List of actionable improvement recommendations.

    Example:
        ```python
        class FullValidationReport:
            validation_id: str = "val_20240115_001"
            repository_name: str = "omnibase_spi"
            scope: ProtocolValidationScope = scope_instance
            workflow: ProtocolValidationWorkflow = workflow_instance
            results: list[ProtocolValidationResult] = [...]
            summary: ProtocolValidationSummary = summary_instance
            metrics: ProtocolValidationMetrics = metrics_instance
            recommendations: list[str] = [
                "Add type hints to 15 functions",
                "Resolve 3 circular import patterns"
            ]

            async def get_critical_issues(self) -> list[ProtocolValidationResult]:
                return [r for r in self.results if r.severity == "critical"]

        report = FullValidationReport()
        assert isinstance(report, ProtocolValidationReport)
        ```
    """

    validation_id: str
    repository_name: str
    scope: "ProtocolValidationScope"
    workflow: "ProtocolValidationWorkflow"
    results: list["ProtocolValidationResult"]
    summary: "ProtocolValidationSummary"
    metrics: "ProtocolValidationMetrics"
    recommendations: list[str]

    async def get_critical_issues(self) -> list["ProtocolValidationResult"]: ...


@runtime_checkable
class ProtocolValidationOrchestrator(Protocol):
    """
    Protocol interface for validation orchestration in ONEX systems.

    This protocol defines the interface for NodeValidationOrchestratorOrchestrator
    nodes that coordinate validation workflows across multiple validation nodes
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
