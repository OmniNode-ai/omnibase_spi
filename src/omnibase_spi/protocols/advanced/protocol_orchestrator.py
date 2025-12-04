# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:27.245096'
# description: Stamped by ToolPython
# entrypoint: python://protocol_orchestrator
# hash: 97f3deb8b8a9392539a52dfda4cdc7af0929d195897f0a11b292637d0614a372
# last_modified_at: '2025-05-29T14:14:00.303902+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: protocol_orchestrator.py
# namespace: python://omnibase.protocol.protocol_orchestrator
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 4ea8f61f-93a5-4e91-91ad-75b22a6b4060
# version: 1.0.0
# === /OmniNode:Metadata ===


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

    nodes: list["ProtocolNodeModel"]
    edges: list["ProtocolEdgeModel"]
    metadata: dict[str, object]

    def validate(self) -> bool: ...

    def to_dict(self) -> dict[str, object]: ...


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

    async def get_dependencies(self) -> list[str]: ...

    def validate(self) -> bool: ...


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

    def to_dict(self) -> dict[str, object]: ...


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
    steps: list["ProtocolStepModel"]
    dependencies: dict[str, list[str]]

    async def get_execution_order(self) -> list[str]: ...

    def validate(self) -> bool: ...


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

    async def execute(self) -> object: ...


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

    async def get_summary(self) -> dict[str, object]: ...

    def has_failures(self) -> bool: ...


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

    def plan(self, graph: ProtocolGraphModel) -> list[ProtocolPlanModel]: ...

    async def execute(
        self, plan: list[ProtocolPlanModel]
    ) -> ProtocolOrchestratorResultModel: ...
