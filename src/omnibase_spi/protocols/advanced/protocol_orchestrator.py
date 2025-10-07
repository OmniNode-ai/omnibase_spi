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
    """Protocol for graph models."""

    nodes: list["ProtocolNodeModel"]
    edges: list["ProtocolEdgeModel"]
    metadata: dict[str, object]

    def validate(self) -> bool: ...

    def to_dict(self) -> dict[str, object]: ...


@runtime_checkable
class ProtocolNodeModel(Protocol):
    """Protocol for node models."""

    node_id: str
    node_type: str
    configuration: dict[str, object]
    dependencies: list[str]

    async def get_dependencies(self) -> list[str]: ...

    def validate(self) -> bool: ...


@runtime_checkable
class ProtocolEdgeModel(Protocol):
    """Protocol for edge models."""

    source: str
    target: str
    edge_type: str
    metadata: dict[str, object]

    def to_dict(self) -> dict[str, object]: ...


@runtime_checkable
class ProtocolPlanModel(Protocol):
    """Protocol for plan models."""

    plan_id: str
    steps: list["ProtocolStepModel"]
    dependencies: dict[str, list[str]]

    async def get_execution_order(self) -> list[str]: ...

    def validate(self) -> bool: ...


@runtime_checkable
class ProtocolStepModel(Protocol):
    """Protocol for step models."""

    step_id: str
    node_id: str
    operation: str
    parameters: dict[str, object]

    async def execute(self) -> object: ...


@runtime_checkable
class ProtocolOrchestratorResultModel(Protocol):
    """Protocol for orchestrator result models."""

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
