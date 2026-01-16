"""Protocol for legacy ONEX orchestrator nodes.

.. deprecated::
    This module contains the legacy ONEX-specific orchestrator protocol.
    For v0.3.0 compliant code, use :class:`omnibase_spi.protocols.nodes.ProtocolOrchestratorNode`
    which provides the canonical node interface with typed execute() methods.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class ProtocolOnexOrchestratorNodeLegacy(Protocol):
    """
    Legacy protocol for ONEX orchestrator node implementations.

    .. deprecated::
        This is a legacy ONEX-specific protocol with a simplified interface.
        For new implementations, use the canonical v0.3.0 protocol:
        :class:`omnibase_spi.protocols.nodes.ProtocolOrchestratorNode`

        The v0.3.0 protocol in ``protocols.nodes`` provides:
        - Inheritance from ProtocolNode base
        - Typed execute() method signature
        - Full integration with the node registry system

    Orchestrator nodes coordinate workflow execution across multiple nodes,
    managing task distribution, dependency resolution, and workflow state
    transitions. They implement the orchestration logic that drives complex
    multi-node workflows.

    Key Responsibilities:
        - Workflow coordination and task distribution
        - Dependency resolution and execution ordering
        - State management across distributed nodes
        - Error handling and compensation logic
        - Workflow lifecycle management

    Implementation Notes:
        Orchestrator nodes should:
        - Implement idempotent orchestration logic
        - Handle partial failures gracefully
        - Support workflow replay and recovery
        - Track workflow progress and state
        - Coordinate with Effect, Compute, and Reducer nodes

    Type Safety:
        This protocol is runtime checkable, enabling isinstance() validation
        for dynamic node loading and dependency injection systems.

    Example Usage:
        ```python
        from omnibase_spi.protocols.onex import ProtocolOnexOrchestratorNodeLegacy

        class MyOrchestrator:
            async def execute_orchestration(self, contract: WorkflowContract) -> WorkflowResult:
                # Coordinate workflow execution
                ...

            @property
            def node_id(self) -> str:
                return "orchestrator-workflow-1"

            @property
            def node_type(self) -> str:
                return "orchestrator"

        # Runtime validation
        orchestrator = MyOrchestrator()
        assert isinstance(orchestrator, ProtocolOnexOrchestratorNodeLegacy)
        ```

    Integration:
        Works with ONEX container system for:
        - Dynamic node discovery and registration
        - Dependency injection of supporting services
        - Health monitoring and metrics collection
        - Workflow event sourcing and state management

    See Also:
        - :class:`omnibase_spi.protocols.nodes.ProtocolOrchestratorNode`: Canonical v0.3.0 protocol
        - :class:`omnibase_spi.protocols.nodes.ProtocolNode`: Base node protocol
    """

    async def execute_orchestration(self, contract: object) -> object:
        """
        Execute orchestration workflow.

        Coordinates the execution of a workflow by distributing tasks to
        appropriate nodes, managing dependencies, and tracking state transitions.

        Args:
            contract: Workflow contract containing orchestration configuration,
                     input data, and execution context. Type is typically a
                     ModelContract subclass specific to the workflow.

        Returns:
            Orchestration result containing workflow state, execution metadata,
            and any produced outputs. Return type matches the contract's output
            specification.

        Raises:
            WorkflowExecutionError: When orchestration fails due to invalid state
            DependencyResolutionError: When node dependencies cannot be resolved
            CompensationError: When compensation actions fail during rollback

        Implementation Requirements:
            - Must be idempotent for workflow replay scenarios
            - Should implement compensation logic for failed workflows
            - Must track workflow state changes via event sourcing
            - Should handle partial node failures gracefully
            - Must respect workflow timeout constraints
        """
        ...

    @property
    def node_id(self) -> str:
        """
        Get unique node identifier.

        Returns a globally unique identifier for this orchestrator node instance.
        Used for node registration, discovery, and tracking in distributed systems.

        Returns:
            str: Unique node identifier, typically in format:
                 "orchestrator-{workflow-type}-{instance-id}"

        Implementation Notes:
            - Must be unique across all nodes in the system
            - Should be stable across restarts for workflow replay
            - Used as key in service registry and discovery systems
            - Included in all workflow events for tracing
        """
        ...

    @property
    def node_type(self) -> str:
        """
        Get node type identifier.

        Returns the node type classification for this orchestrator.
        Used for node routing, capability discovery, and workflow planning.

        Returns:
            str: Node type identifier, always "orchestrator" for this protocol.
                 May include subtypes like "orchestrator:saga" or
                 "orchestrator:choreography" for specialized implementations.

        Implementation Notes:
            - Must return "orchestrator" or a subtype of orchestrator
            - Used by node registry for capability-based routing
            - Enables workflow engine to select appropriate orchestrators
            - May be used for load balancing and node selection
        """
        ...
