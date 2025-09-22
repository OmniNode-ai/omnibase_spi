"""
Protocol interface for validation orchestration in ONEX ecosystem.

This protocol defines the interface for coordinating validation workflows
across multiple validation nodes, providing comprehensive validation
orchestration for NodeValidationOrchestratorOrchestrator implementations.
"""

from typing import List, Optional, Protocol

from .protocol_validation import ProtocolValidationResult


class ProtocolValidationScope(Protocol):
    """Protocol for defining validation scope."""

    repository_path: str
    validation_types: List[str]  # ["imports", "quality", "compliance", "security"]
    file_patterns: List[str]
    exclusion_patterns: List[str]
    validation_depth: str  # "surface", "deep", "comprehensive"

    def should_validate_file(self, file_path: str) -> bool:
        """Determine if a file should be validated."""
        ...

    def get_repository_name(self) -> str:
        """Get repository name from path."""
        ...


class ProtocolValidationWorkflow(Protocol):
    """Protocol for validation workflow definition."""

    workflow_id: str
    workflow_name: str
    validation_steps: List[str]
    dependencies: List[str]  # Step dependency names
    parallel_execution: bool
    timeout_seconds: int

    def get_execution_order(self) -> List[str]:
        """Get execution order considering dependencies."""
        ...

    def is_step_ready(self, step: str, completed_steps: List[str]) -> bool:
        """Check if a validation step is ready for execution."""
        ...


class ProtocolValidationMetrics(Protocol):
    """Protocol for validation execution metrics."""

    total_files_processed: int
    validation_duration_seconds: float
    memory_usage_mb: float
    parallel_executions: int
    cache_hit_rate: float

    def get_performance_summary(self) -> str:
        """Get human-readable performance summary."""
        ...


class ProtocolValidationSummary(Protocol):
    """Protocol for validation result summary."""

    total_validations: int
    passed_validations: int
    failed_validations: int
    warning_count: int
    critical_issues: int
    success_rate: float

    def get_overall_status(self) -> str:
        """Get overall validation status: PASS, FAIL, or WARNING."""
        ...


class ProtocolValidationReport(Protocol):
    """Protocol for comprehensive validation reports."""

    validation_id: str
    repository_name: str
    scope: ProtocolValidationScope
    workflow: ProtocolValidationWorkflow
    results: List[ProtocolValidationResult]
    summary: ProtocolValidationSummary
    metrics: ProtocolValidationMetrics
    recommendations: List[str]

    def get_critical_issues(self) -> List[ProtocolValidationResult]:
        """Get list of critical validation issues."""
        ...

    def generate_markdown_report(self) -> str:
        """Generate markdown-formatted validation report."""
        ...


class ProtocolValidationOrchestrator(Protocol):
    """
    Protocol interface for validation orchestration in ONEX systems.

    This protocol defines the interface for NodeValidationOrchestratorOrchestrator
    nodes that coordinate validation workflows across multiple validation nodes
    including import, quality, compliance, and security validation.
    """

    orchestration_id: str
    default_scope: ProtocolValidationScope

    def orchestrate_validation(
        self,
        scope: ProtocolValidationScope,
        workflow: Optional[ProtocolValidationWorkflow] = None,
    ) -> ProtocolValidationReport:
        """
        Orchestrate comprehensive validation across multiple validators.

        Args:
            scope: Validation scope defining what to validate
            workflow: Optional custom validation workflow

        Returns:
            ProtocolValidationReport with comprehensive results
        """
        ...

    def validate_imports(
        self, scope: ProtocolValidationScope
    ) -> List[ProtocolValidationResult]:
        """
        Orchestrate import validation.

        Args:
            scope: Validation scope for import validation

        Returns:
            List of import validation results
        """
        ...

    def validate_quality(
        self, scope: ProtocolValidationScope
    ) -> List[ProtocolValidationResult]:
        """
        Orchestrate code quality validation.

        Args:
            scope: Validation scope for quality validation

        Returns:
            List of quality validation results
        """
        ...

    def validate_compliance(
        self, scope: ProtocolValidationScope
    ) -> List[ProtocolValidationResult]:
        """
        Orchestrate compliance validation.

        Args:
            scope: Validation scope for compliance validation

        Returns:
            List of compliance validation results
        """
        ...

    def create_validation_workflow(
        self,
        workflow_name: str,
        validation_steps: List[str],
        dependencies: List[str],
        parallel_execution: bool = True,
    ) -> ProtocolValidationWorkflow:
        """
        Create custom validation workflow.

        Args:
            workflow_name: Name for the workflow
            validation_steps: List of validation steps
            dependencies: Step dependency names
            parallel_execution: Whether to execute steps in parallel

        Returns:
            ProtocolValidationWorkflow instance
        """
        ...

    def create_validation_scope(
        self,
        repository_path: str,
        validation_types: Optional[List[str]] = None,
        file_patterns: Optional[List[str]] = None,
        exclusion_patterns: Optional[List[str]] = None,
    ) -> ProtocolValidationScope:
        """
        Create validation scope for a repository.

        Args:
            repository_path: Path to repository to validate
            validation_types: Types of validation to perform
            file_patterns: File patterns to include
            exclusion_patterns: File patterns to exclude

        Returns:
            ProtocolValidationScope instance
        """
        ...

    def get_orchestration_metrics(self) -> ProtocolValidationMetrics:
        """
        Get orchestration performance and usage metrics.

        Returns:
            ProtocolValidationMetrics with orchestration statistics
        """
        ...

    def reset_orchestration_state(self) -> None:
        """Reset orchestration state for fresh validation cycle."""
        ...
