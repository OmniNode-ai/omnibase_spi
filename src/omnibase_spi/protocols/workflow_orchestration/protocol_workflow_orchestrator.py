"""
Protocol interface for Workflow orchestrator tools in ONEX systems.

This protocol defines the interface for tools that can orchestrate
complex workflows with event-driven coordination and strict SPI purity.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable
from uuid import UUID

if TYPE_CHECKING:
    from omnibase_spi.protocols.node.protocol_node_registry import ProtocolNodeRegistry
    from omnibase_spi.protocols.types.protocol_file_handling_types import (
        ProtocolResult,
    )
    from omnibase_spi.protocols.types.protocol_workflow_orchestration_types import (
        ProtocolHealthCheckResult,
        ProtocolWorkflowExecutionState,
        ProtocolWorkflowInputState,
        ProtocolWorkflowParameters,
    )


@runtime_checkable
class ProtocolWorkflowOrchestrator(Protocol):
    """
    Protocol for Workflow orchestrator tools that coordinate complex workflow execution.

    This protocol defines the interface for tools that manage the execution of multiple
    workflow nodes, handle dependencies, and coordinate overall workflow state across
    different operation types with strict SPI purity compliance.

    Key Features:
        - Multi-node workflow coordination and execution
        - Dependency management and resolution
        - State management and persistence
        - Health monitoring and error recovery
        - Registry integration for tool access

    Usage Example:
        ```python
        # Protocol usage example (SPI-compliant)
        orchestrator: ProtocolWorkflowOrchestrator = get_workflow_orchestrator()

        # Set up registry for tool access
        registry: "ProtocolNodeRegistry" = get_node_registry()
        orchestrator.set_registry(registry)

        # Create input state
        input_state: "ProtocolWorkflowInputState" = create_workflow_input(
            action="execute_workflow",
            parameters={"workflow_type": "data_processing"}
        )

        # Run workflow orchestration
        result = orchestrator.run(input_state)

        # Check execution state
        execution_state = orchestrator.get_execution_state("scenario-123")
        ```
    """

    def set_registry(self, registry: "ProtocolNodeRegistry") -> None:
        """
        Set the registry for accessing other tools and dependencies.

        Args:
            registry: The registry containing other tools and dependencies
        """
        ...

    async def run(self, input_state: "ProtocolWorkflowInputState") -> "ProtocolResult":
        """
        Run the Workflow orchestrator with the provided input state.

        Args:
            input_state: Input state containing action and parameters for workflow execution

        Returns:
            Result of Workflow orchestration including execution status and output data
        """
        ...

    async def orchestrate_operation(
        self,
        operation_type: str,
        scenario_id: str,
        correlation_id: UUID,
        parameters: "ProtocolWorkflowParameters",
    ) -> "ProtocolResult":
        """
        Orchestrate a specific operation type within a workflow scenario.

        Args:
            operation_type: Type of operation (model_generation, bootstrap_validation,
                           extraction, generic, or custom operation types)
            scenario_id: ID of the scenario to orchestrate
            correlation_id: Correlation ID for tracking and debugging
            parameters: Additional parameters for the operation

        Returns:
            Result of operation orchestration including status and output data
        """
        ...

    async def get_execution_state(
        self,
        scenario_id: str,
    ) -> "ProtocolWorkflowExecutionState | None":
        """
        Get the current execution state for a workflow scenario.

        Args:
            scenario_id: ID of the scenario to query

        Returns:
            Current execution state or None if scenario not found
        """
        ...

    async def health_check(self) -> "ProtocolHealthCheckResult":
        """
        Perform health check for the Workflow orchestrator.

        Returns:
            Health check result with status, capabilities, and performance metrics
        """
        ...
