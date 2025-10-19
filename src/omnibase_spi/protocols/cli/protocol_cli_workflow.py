"""
CLI Workflow Protocol for ONEX CLI Interface

Defines the protocol interface for CLI workflow discovery and execution,
providing abstracted workflow operations without direct tool imports.
"""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ProtocolCliExecutionResult(Protocol):
    """Protocol for CLI execution results."""

    success: bool
    exit_code: int
    stdout: str
    stderr: str
    execution_time: float
    workflow_data: dict[str, Any] | None

    def to_dict(self) -> dict[str, Any]: ...


@runtime_checkable
class ProtocolCliWorkflow(Protocol):
    """
    Protocol interface for CLI workflow operations.

    Provides abstracted workflow discovery and execution capabilities
    for the CLI without requiring direct tool imports.
    """

    async def list_workflows(
        self, domain: str | None = None
    ) -> ProtocolCliExecutionResult:
        """
        List available workflows for a domain.

        Args:
            domain: Domain to filter workflows (e.g., 'generation')

        Returns:
            ProtocolCliExecutionResult with workflow data
        """
        ...

    async def execute_workflow(
        self,
        domain: str,
        workflow_name: str,
        dry_run: bool | None = None,
        timeout: int | None = None,
        parameters: dict[str, Any] | None = None,
    ) -> ProtocolCliExecutionResult:
        """
        Execute a workflow in the specified domain.

        Args:
            domain: Hub domain (e.g., 'generation')
            workflow_name: Name of the workflow to execute
            dry_run: Perform dry run validation only
            timeout: Override workflow timeout
            parameters: Additional workflow parameters

        Returns:
            ProtocolCliExecutionResult with execution results
        """
        ...

    async def get_workflow_info(
        self,
        domain: str,
        workflow_name: str,
    ) -> ProtocolCliExecutionResult:
        """
        Get detailed information about a specific workflow.

        Args:
            domain: Hub domain
            workflow_name: Name of the workflow

        Returns:
            ProtocolCliExecutionResult with workflow information
        """
        ...

    async def list_domains(self) -> ProtocolCliExecutionResult:
        """
        List available workflow domains.

        Returns:
            ProtocolCliExecutionResult with available domains
        """
        ...
