"""
Hub Execution Protocol for ONEX CLI Interface

Defines the protocol interface for hub workflow execution,
providing abstracted hub operations without direct tool imports.
"""

from typing import Any, Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_core_types import ContextValue


@runtime_checkable
class ProtocolModelCliExecutionResult(Protocol):
    """
    Protocol for CLI execution result models.

    Defines the standardized interface for CLI execution results with comprehensive
    metadata tracking, execution metrics, and domain-specific workflow information.

    Example:
        class CliExecutionResult(ProtocolModelCliExecutionResult):
            def __init__(self, success, domain, workflow_name, execution_id,
                         result_data, message, exit_code, execution_time_ms,
                         dry_run, timestamp, metadata):
                self.success = success
                self.domain = domain
                self.workflow_name = workflow_name
                self.execution_id = execution_id
                self.result_data = result_data
                self.message = message
                self.exit_code = exit_code
                self.execution_time_ms = execution_time_ms
                self.dry_run = dry_run
                self.timestamp = timestamp
                self.metadata = metadata or {}

            def to_dict(self):
                return {
                    "success": self.success,
                    "domain": self.domain,
                    "workflow_name": self.workflow_name,
                    "execution_id": self.execution_id,
                    "result_data": self.result_data,
                    "message": self.message,
                    "exit_code": self.exit_code,
                    "execution_time_ms": self.execution_time_ms,
                    "dry_run": self.dry_run,
                    "timestamp": self.timestamp,
                    "metadata": self.metadata
                }
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
        dry_run: bool = False,
        timeout: int | None = None,
        parameters: dict[str, Any] | None = None,
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
