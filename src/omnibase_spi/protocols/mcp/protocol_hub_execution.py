"""
Hub Execution Protocol for ONEX CLI Interface

Defines the protocol interface for hub workflow execution,
providing abstracted hub operations without direct tool imports.
"""

from typing import Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_core_types import ContextValue


@runtime_checkable
class ProtocolModelCliExecutionResult(Protocol):
    """
    Protocol for CLI execution result models.

    Defines the standardized interface for CLI execution results with comprehensive
    metadata tracking, execution metrics, and domain-specific workflow information.

    Example:
        @runtime_checkable
        class CliExecutionResult(Protocol):
            @property
            def success(self) -> bool: ...
            @property
            def domain(self) -> str: ...
            @property
            def workflow_name(self) -> str: ...
            @property
            def execution_id(self) -> str | None: ...
            @property
            def result_data(self) -> dict[str, ContextValue] | None: ...
            @property
            def message(self) -> str: ...
            @property
            def exit_code(self) -> int: ...
            @property
            def execution_time_ms(self) -> int | None: ...
            @property
            def dry_run(self) -> bool: ...
            @property
            def timestamp(self) -> str: ...
            @property
            def metadata(self) -> dict[str, ContextValue]: ...

            def to_dict(self) -> dict[str, ContextValue]: ...
    """

    success: bool
    domain: str
    workflow_name: str
    execution_id: str | None
    result_data: dict[str, ContextValue] | None
    message: str
    exit_code: int
    execution_time_ms: int | None
    dry_run: bool
    timestamp: str
    metadata: dict[str, ContextValue]


@runtime_checkable
class ProtocolHubExecution(Protocol):
    """
    Protocol interface for hub workflow execution.

    Provides abstracted hub execution capabilities for workflow
    operations without requiring direct tool imports.
    """

    async def execute_workflow(
        self,
        domain: str,
        workflow_name: str,
        dry_run: bool | None = None,
        timeout: int | None = None,
        parameters: dict[str, ContextValue] | None = None,
    ) -> ProtocolModelCliExecutionResult:
        """
        Execute a workflow in the specified domain hub.

        Args:
            domain: Hub domain (e.g., 'generation')
            workflow_name: Name of the workflow to execute
            dry_run: Perform dry run validation only
            timeout: Override workflow timeout
            parameters: Additional workflow parameters

        Returns:
            ModelCliExecutionResult with execution results
        """
        ...

    async def get_hub_introspection(
        self, domain: str
    ) -> ProtocolModelCliExecutionResult:
        """
        Get hub introspection data including available workflows.

        Args:
            domain: Hub domain to introspect

        Returns:
            ModelCliExecutionResult with introspection data including:
            - description: Hub description
            - coordination_mode: Hub coordination mode
            - workflows: Dictionary of available workflows with metadata
        """
        ...

    async def validate_workflow(
        self,
        domain: str,
        workflow_name: str,
    ) -> ProtocolModelCliExecutionResult:
        """
        Validate a workflow exists and is executable.

        Args:
            domain: Hub domain
            workflow_name: Name of the workflow to validate

        Returns:
            ModelCliExecutionResult with validation results
        """
        ...
