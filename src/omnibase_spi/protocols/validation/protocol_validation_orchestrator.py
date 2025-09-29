"""
Protocol interface for validation orchestration in ONEX ecosystem.

This protocol defines the interface for coordinating validation workflows
across multiple validation nodes, providing comprehensive validation
orchestration for NodeValidationOrchestrator implementations.
"""

from typing import List, Protocol, runtime_checkable

from omnibase_spi.protocols.validation.protocol_validation import (
    ProtocolValidationResult,
)


@runtime_checkable
class ProtocolValidationScope(Protocol):
    """Protocol for defining validation scope."""

    repository_path: str
    validation_types: List[str]
    file_patterns: List[str]
    exclusion_patterns: List[str]
    validation_depth: str

    async def should_validate_file(self, file_path: str) -> bool: ...

    async def get_repository_name(self) -> str: ...


@runtime_checkable
class ProtocolValidationWorkflow(Protocol):
    """Protocol for validation workflow definition."""

    workflow_id: str
    workflow_name: str
    validation_steps: List[str]
    dependencies: List[str]
    parallel_execution: bool
    timeout_seconds: int

    async def get_execution_order(self) -> List[str]: ...


@runtime_checkable
class ProtocolValidationMetrics(Protocol):
    """Protocol for validation execution metrics."""

    total_files_processed: int
    validation_duration_seconds: float
    memory_usage_mb: float
    parallel_executions: int
    cache_hit_rate: float

    async def get_performance_summary(self) -> str: ...


@runtime_checkable
class ProtocolValidationSummary(Protocol):
    """Protocol for validation result summary."""

    total_validations: int
    passed_validations: int
    failed_validations: int
    warning_count: int
    critical_issues: int
    success_rate: float

    async def get_overall_status(self) -> str: ...


@runtime_checkable
class ProtocolValidationReport(Protocol):
    """Protocol for comprehensive validation reports."""

    validation_id: str
    repository_name: str
    scope: "ProtocolValidationScope"
    workflow: "ProtocolValidationWorkflow"
    results: List[ProtocolValidationResult]
    summary: "ProtocolValidationSummary"
    metrics: "ProtocolValidationMetrics"
    recommendations: List[str]

    async def get_critical_issues(self) -> List[ProtocolValidationResult]: ...


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
    ) -> List[ProtocolValidationResult]: ...

    async def validate_quality(
        self, scope: "ProtocolValidationScope"
    ) -> List[ProtocolValidationResult]: ...

    async def validate_compliance(
        self, scope: "ProtocolValidationScope"
    ) -> List[ProtocolValidationResult]: ...

    async def create_validation_workflow(
        self,
        workflow_name: str,
        validation_steps: List[str],
        dependencies: List[str],
        parallel_execution: bool = True,
    ) -> ProtocolValidationWorkflow: ...

    async def create_validation_scope(
        self,
        repository_path: str,
        validation_types: List[str] | None = None,
        file_patterns: List[str] | None = None,
        exclusion_patterns: List[str] | None = None,
    ) -> ProtocolValidationScope: ...

    async def get_orchestration_metrics(self) -> ProtocolValidationMetrics: ...
