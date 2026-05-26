# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Protocol definitions for workflow orchestration in ONEX systems."""

from typing import Protocol, runtime_checkable


@runtime_checkable
class ProtocolOrchestrator(Protocol):
    """
    Protocol for workflow and graph execution orchestration in ONEX systems.

    Defines the contract for orchestrator components that plan and execute complex
    workflow graphs with dependency management, parallel execution, and failure
    handling. Enables distributed workflow coordination across ONEX nodes and services.

    Example:
        ```python
        from omnibase_spi.protocols.advanced import ProtocolOrchestrator

        async def execute_workflow(
            orchestrator: ProtocolOrchestrator,
        ) -> None:
            # Plan execution order based on dependencies
            execution_plans = orchestrator.plan(workflow_graph)

            # Execute plans with dependency coordination
            result = await orchestrator.execute(execution_plans)
        ```

    Key Features:
        - Dependency-aware execution planning
        - Parallel step execution where possible
        - Failure detection and handling
        - Execution time tracking
        - Step-level result aggregation
        - Graph validation and optimization

    See Also:
        - ProtocolWorkflowEventBus: Event-driven workflow coordination
        - ProtocolNodeRegistry: Node discovery and management
    """

    def plan(self, graph: object) -> list[object]:
        """Generate execution plans from a workflow graph.

        Args:
            graph: The workflow graph to plan execution for.

        Returns:
            List of execution plans that cover all nodes in the graph.

        Raises:
            SPIError: If planning fails due to invalid graph structure.
            ValueError: If the graph is empty or contains unresolvable dependencies.
        """
        ...

    async def execute(self, plan: list[object]) -> object:
        """Execute a list of workflow plans and return aggregated results.

        Args:
            plan: List of execution plans to execute.

        Returns:
            Aggregated result containing success status, executed steps,
            failed steps, output data, and timing information.

        Raises:
            SPIError: If orchestration encounters an unrecoverable error.
            RuntimeError: If execution is interrupted or cancelled.
            TimeoutError: If overall execution exceeds the configured timeout.
        """
        ...
