"""Protocol definitions for workflow orchestration in ONEX systems.

This module defines protocols for workflow graph representation, execution planning,
and orchestration of complex multi-step workflows with dependency management.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class ProtocolGraphModel(Protocol):
    """
    Protocol for directed acyclic graph (DAG) workflow representation.

    Defines the structure for workflow graphs containing nodes (execution units)
    and edges (dependencies), enabling dependency-aware execution planning and
    parallel workflow coordination in ONEX orchestration systems.

    Attributes:
        nodes: List of execution nodes in the graph
        edges: List of dependency edges connecting nodes
        metadata: Additional graph-level configuration and metadata

    Example:
        ```python
        orchestrator: ProtocolOrchestrator = get_orchestrator()
        graph: ProtocolGraphModel = build_workflow_graph()

        # Validate graph structure
        if graph.validate():
            print(f"Graph has {len(graph.nodes)} nodes, {len(graph.edges)} edges")

            # Plan execution based on dependencies
            plans = orchestrator.plan(graph)
            for plan in plans:
                print(f"Plan {plan.plan_id}: {len(plan.steps)} steps")
        ```

    See Also:
        - ProtocolNodeModel: Individual node definitions
        - ProtocolEdgeModel: Edge/dependency definitions
        - ProtocolOrchestrator: Graph execution orchestration
    """

    nodes: list[ProtocolNodeModel]
    edges: list[ProtocolEdgeModel]
    metadata: dict[str, object]

    def validate(self) -> bool:
        """Validate the workflow graph structure.

        Checks that all nodes and edges form a valid DAG with no cycles
        and all edge references point to existing nodes.

        Returns:
            True if the graph is valid, False otherwise.

        Raises:
            SPIError: If validation encounters an unrecoverable error.
            ValueError: If the graph contains invalid node or edge references.
        """
        ...

    def to_dict(self) -> dict[str, object]:
        """Convert the graph model to a dictionary representation.

        Serializes the entire workflow graph including nodes, edges,
        and metadata for persistence or transmission.

        Returns:
            Dictionary containing 'nodes', 'edges', and 'metadata' keys
            with their respective serialized values.

        Raises:
            SPIError: If serialization fails due to invalid graph state.
            ValueError: If nodes, edges, or metadata contain non-serializable values.
        """
        ...


@runtime_checkable
class ProtocolNodeModel(Protocol):
    """
    Protocol for individual execution node within a workflow graph.

    Represents a single unit of work in a workflow DAG with unique
    identification, type classification, configuration parameters, and
    explicit dependency declarations for orchestration planning.

    Attributes:
        node_id: Unique identifier within the workflow graph
        node_type: Classification of node (compute, effect, reducer, etc.)
        configuration: Node-specific configuration parameters
        dependencies: List of node IDs this node depends on

    Example:
        ```python
        graph: ProtocolGraphModel = get_workflow_graph()

        for node in graph.nodes:
            if node.validate():
                deps = await node.get_dependencies()
                print(f"Node {node.node_id} ({node.node_type})")
                print(f"  Dependencies: {deps}")
                print(f"  Config: {node.configuration}")
        ```

    See Also:
        - ProtocolGraphModel: Container for workflow nodes
        - ProtocolEdgeModel: Dependency edge definitions
        - ProtocolStepModel: Execution step representation
    """

    node_id: str
    node_type: str
    configuration: dict[str, object]
    dependencies: list[str]

    async def get_dependencies(self) -> list[str]:
        """Get the list of node IDs this node depends on.

        Returns the declared dependencies that must complete before
        this node can begin execution.

        Returns:
            List of node IDs that this node depends on.

        Raises:
            SPIError: If dependency resolution fails.
            RuntimeError: If the node is in an invalid state for dependency lookup.
        """
        ...

    def validate(self) -> bool:
        """Validate the node configuration.

        Checks that the node has valid configuration parameters
        and properly formed dependency declarations.

        Returns:
            True if the node configuration is valid, False otherwise.

        Raises:
            SPIError: If validation encounters an unrecoverable error.
            ValueError: If configuration contains invalid values or types.
        """
        ...


@runtime_checkable
class ProtocolEdgeModel(Protocol):
    """
    Protocol for dependency edge between workflow graph nodes.

    Represents a directed edge in the workflow DAG connecting a source
    node to a target node, indicating that the target depends on the
    source completing before execution can begin.

    Attributes:
        source: Node ID of the dependency source (must complete first)
        target: Node ID of the dependent node (waits for source)
        edge_type: Classification of dependency (data, control, resource)
        metadata: Additional edge configuration and annotations

    Example:
        ```python
        graph: ProtocolGraphModel = get_workflow_graph()

        for edge in graph.edges:
            edge_dict = edge.to_dict()
            print(f"Dependency: {edge.source} -> {edge.target}")
            print(f"  Type: {edge.edge_type}")
            if edge.metadata.get("optional"):
                print("  (Optional dependency)")
        ```

    See Also:
        - ProtocolGraphModel: Container for workflow edges
        - ProtocolNodeModel: Source and target node definitions
        - ProtocolPlanModel: Execution planning from edges
    """

    source: str
    target: str
    edge_type: str
    metadata: dict[str, object]

    def to_dict(self) -> dict[str, object]:
        """Convert the edge model to a dictionary representation.

        Serializes the edge including source, target, type, and metadata
        for persistence or transmission.

        Returns:
            Dictionary containing 'source', 'target', 'edge_type', and
            'metadata' keys with their respective values.

        Raises:
            SPIError: If serialization fails due to invalid edge state.
            ValueError: If metadata contains non-serializable values.
        """
        ...


@runtime_checkable
class ProtocolPlanModel(Protocol):
    """
    Protocol for workflow execution plan representation.

    Encapsulates a sequence of execution steps derived from a workflow
    graph, with dependency mappings and ordered step execution for
    coordinated workflow orchestration.

    Attributes:
        plan_id: Unique identifier for this execution plan
        steps: Ordered list of steps to execute in this plan
        dependencies: Mapping of step IDs to their prerequisite step IDs

    Example:
        ```python
        orchestrator: ProtocolOrchestrator = get_orchestrator()
        graph: ProtocolGraphModel = build_workflow_graph()
        plans = orchestrator.plan(graph)

        for plan in plans:
            if plan.validate():
                execution_order = await plan.get_execution_order()
                print(f"Plan {plan.plan_id}:")
                for step_id in execution_order:
                    deps = plan.dependencies.get(step_id, [])
                    print(f"  {step_id} (after: {deps})")
        ```

    See Also:
        - ProtocolOrchestrator: Plan generation and execution
        - ProtocolStepModel: Individual execution steps
        - ProtocolGraphModel: Source graph for planning
    """

    plan_id: str
    steps: list[ProtocolStepModel]
    dependencies: dict[str, list[str]]

    async def get_execution_order(self) -> list[str]:
        """Compute the optimal execution order for steps in this plan.

        Analyzes step dependencies to produce a topologically sorted order
        that respects all dependency constraints while maximizing parallelism.

        Returns:
            List of step IDs in valid execution order.

        Raises:
            SPIError: If execution order cannot be determined.
            ValueError: If the plan contains circular dependencies.
        """
        ...

    def validate(self) -> bool:
        """Validate the execution plan structure and consistency.

        Checks that all steps are valid, dependencies are resolvable,
        and the plan can be executed without conflicts.

        Returns:
            True if the plan is valid and ready for execution.

        Raises:
            SPIError: If validation encounters an unrecoverable error.
            ValueError: If the plan contains invalid step references or dependencies.
        """
        ...


@runtime_checkable
class ProtocolStepModel(Protocol):
    """
    Protocol for individual execution step within an execution plan.

    Represents a single executable action in a workflow plan, linking
    to a specific node and operation with parameterized execution
    for coordinated workflow step processing.

    Attributes:
        step_id: Unique identifier for this execution step
        node_id: Reference to the source node being executed
        operation: Specific operation to perform on the node
        parameters: Operation-specific parameters and configuration

    Example:
        ```python
        plan: ProtocolPlanModel = get_execution_plan()

        for step in plan.steps:
            print(f"Step {step.step_id}: {step.operation} on {step.node_id}")
            print(f"  Parameters: {step.parameters}")

            # Execute the step
            result = await step.execute()
            print(f"  Result: {result}")
        ```

    See Also:
        - ProtocolPlanModel: Container for execution steps
        - ProtocolNodeModel: Node being executed
        - ProtocolOrchestratorResultModel: Aggregated step results
    """

    step_id: str
    node_id: str
    operation: str
    parameters: dict[str, object]

    async def execute(self) -> object:
        """Execute this step and return the result.

        Performs the operation specified by this step on the target node
        using the configured parameters.

        Returns:
            The result of step execution, type depends on the operation.

        Raises:
            SPIError: If step execution fails.
            RuntimeError: If the step is in an invalid state for execution.
            TimeoutError: If step execution exceeds the configured timeout.
        """
        ...


@runtime_checkable
class ProtocolOrchestratorResultModel(Protocol):
    """
    Protocol for workflow orchestration execution result.

    Captures the complete outcome of workflow execution including
    success status, step-level results, timing metrics, and aggregated
    output data for workflow result processing and reporting.

    Attributes:
        success: Whether the entire workflow completed successfully
        executed_steps: List of step IDs that completed execution
        failed_steps: List of step IDs that failed during execution
        output_data: Aggregated output data from all executed steps
        execution_time: Total workflow execution time in seconds

    Example:
        ```python
        orchestrator: ProtocolOrchestrator = get_orchestrator()
        plans = orchestrator.plan(graph)
        result = await orchestrator.execute(plans)

        if result.success:
            summary = await result.get_summary()
            print(f"Workflow completed in {result.execution_time:.2f}s")
            print(f"Executed {len(result.executed_steps)} steps")
        else:
            print(f"Workflow failed: {result.failed_steps}")
            if result.has_failures():
                print("Critical failures detected")
        ```

    See Also:
        - ProtocolOrchestrator: Workflow execution orchestration
        - ProtocolPlanModel: Execution plans producing results
        - ProtocolStepModel: Individual step execution
    """

    success: bool
    executed_steps: list[str]
    failed_steps: list[str]
    output_data: dict[str, object]
    execution_time: float

    async def get_summary(self) -> dict[str, object]:
        """Generate a summary of the orchestration result.

        Compiles execution statistics, timing information, and outcome
        details into a comprehensive summary for reporting and analysis.

        Returns:
            Dictionary containing execution summary with keys for success rate,
            timing metrics, step counts, and any error details.

        Raises:
            SPIError: If summary generation fails.
            RuntimeError: If the result is in an incomplete state.
        """
        ...

    def has_failures(self) -> bool:
        """Check whether any steps failed during execution.

        Provides a quick check for workflow failure without examining
        the full failed_steps list.

        Returns:
            True if one or more steps failed during execution.
        """
        ...


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
        from omnibase_spi.protocols.types import ProtocolGraphModel

        async def execute_workflow(
            orchestrator: ProtocolOrchestrator,
            workflow_graph: ProtocolGraphModel
        ) -> "ProtocolOrchestratorResultModel":
            # Plan execution order based on dependencies
            execution_plans = orchestrator.plan(workflow_graph)

            print(f"Generated {len(execution_plans)} execution plans")
            for plan in execution_plans:
                print(f"  - Plan {plan.plan_id}: {len(plan.steps)} steps")

            # Execute plans with dependency coordination
            result = await orchestrator.execute(execution_plans)

            if result.success:
                print(f"Workflow completed: {len(result.executed_steps)} steps")
            else:
                print(f"Workflow failed: {result.failed_steps}")

            return result
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
        - ProtocolDirectKnowledgePipeline: Workflow execution tracking
    """

    def plan(self, graph: ProtocolGraphModel) -> list[ProtocolPlanModel]:
        """Generate execution plans from a workflow graph.

        Analyzes the graph structure to produce one or more execution plans
        that respect dependencies while optimizing for parallel execution.

        Args:
            graph: The workflow graph to plan execution for.

        Returns:
            List of execution plans that cover all nodes in the graph.

        Raises:
            SPIError: If planning fails due to invalid graph structure.
            ValueError: If the graph is empty or contains unresolvable dependencies.
        """
        ...

    async def execute(
        self, plan: list[ProtocolPlanModel]
    ) -> ProtocolOrchestratorResultModel:
        """Execute a list of workflow plans and return aggregated results.

        Coordinates execution of all steps across all plans, managing
        dependencies, parallelism, and failure handling.

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
