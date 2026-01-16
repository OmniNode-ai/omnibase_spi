"""
CLI Workflow Protocol for ONEX CLI Interface

Defines the protocol interface for CLI workflow discovery and execution,
providing abstracted workflow operations without direct tool imports.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_core.types import JsonType


@runtime_checkable
class ProtocolCliExecutionResult(Protocol):
    """
    Protocol for CLI workflow execution result with full output capture.

    Provides comprehensive execution outcome including stdout/stderr
    capture, timing metrics, and workflow-specific data output for
    detailed execution analysis and debugging.

    Attributes:
        success: Whether workflow executed successfully
        exit_code: UNIX-style exit code from execution
        stdout: Captured standard output stream
        stderr: Captured standard error stream
        execution_time: Total execution time in seconds
        workflow_data: Optional structured workflow output data

    Example:
        ```python
        workflow: ProtocolCliWorkflow = get_cli_workflow()
        result = await workflow.execute_workflow(
            domain="generation",
            workflow_name="model_generator",
            parameters={"contract_path": "/path/to/contract.yaml"}
        )

        if result.success:
            print(f"Completed in {result.execution_time:.2f}s")
            if result.workflow_data:
                print(f"Generated files: {result.workflow_data.get('files')}")
        else:
            print(f"Failed (exit {result.exit_code})")
            print(f"Error output: {result.stderr}")
        ```

    See Also:
        - ProtocolCliWorkflow: Workflow execution interface
        - ProtocolCLIResult: Basic CLI result structure
    """

    success: bool
    exit_code: int
    stdout: str
    stderr: str
    execution_time: float
    workflow_data: dict[str, "JsonType"] | None

    def to_dict(self) -> "JsonType":
        """Convert the workflow result to a dictionary representation.

        Serializes the execution result including success status, output,
        timing, and workflow data for logging or API responses.

        Returns:
            JSON-compatible dictionary containing 'success', 'exit_code',
            'stdout', 'stderr', 'execution_time', and 'workflow_data' keys.
        """
        ...


@runtime_checkable
class ProtocolCliWorkflow(Protocol):
    """
    Protocol interface for CLI workflow discovery and execution.

    Provides abstracted workflow discovery and execution capabilities
    for the CLI without requiring direct tool imports, enabling
    domain-based workflow organization and parameterized execution.

    Example:
        ```python
        workflow: ProtocolCliWorkflow = get_cli_workflow()

        # List available domains
        domains = await workflow.list_domains()
        print(f"Available domains: {domains.workflow_data}")

        # List workflows in a domain
        workflows = await workflow.list_workflows(domain="generation")
        print(f"Generation workflows: {workflows.workflow_data}")

        # Get workflow details
        info = await workflow.get_workflow_info("generation", "model_generator")
        print(f"Workflow info: {info.workflow_data}")

        # Execute workflow with parameters
        result = await workflow.execute_workflow(
            domain="generation",
            workflow_name="model_generator",
            dry_run=True,
            timeout=300,
            parameters={"contract_path": "/path/to/contract.yaml"}
        )
        ```

    See Also:
        - ProtocolCliExecutionResult: Workflow execution results
        - ProtocolCLI: Basic CLI operations
        - ProtocolCLIToolDiscovery: Tool discovery for workflows
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
        parameters: dict[str, "JsonType"] | None = None,
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
