"""Protocol for ONEX reducer nodes (legacy).

.. deprecated::
    This module contains the legacy ONEX reducer node protocol.
    For new implementations, use the canonical v0.3.0 protocol at
    ``omnibase_spi.protocols.nodes.ProtocolReducerNode``.

    This protocol will be removed in v0.5.0.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class ProtocolOnexReducerNodeLegacy(Protocol):
    """
    Legacy protocol for ONEX reducer node implementations.

    .. deprecated::
        This protocol is deprecated. Use ``protocols.nodes.ProtocolReducerNode``
        for the canonical v0.3.0 node interface instead. This legacy protocol
        will be removed in v0.5.0.

    Reducer nodes aggregate and transform data from multiple sources,
    implementing reduction operations that combine, summarize, or synthesize
    outputs from other nodes. They are the final stage in many workflows,
    producing consolidated results.

    Key Responsibilities:
        - Data aggregation from multiple node outputs
        - Result synthesis and transformation
        - State persistence and snapshot creation
        - Final workflow result generation
        - Metrics and summary computation

    Implementation Notes:
        Reducer nodes should:
        - Implement associative reduction operations when possible
        - Handle partial results gracefully during failures
        - Support incremental reduction for streaming workflows
        - Maintain idempotent behavior for replay scenarios
        - Provide clear error context for reduction failures

    Type Safety:
        This protocol is runtime checkable, enabling isinstance() validation
        for dynamic node loading and dependency injection systems.

    Example Usage:
        ```python
        from omnibase_spi.protocols.onex import ProtocolOnexReducerNodeLegacy

        class MyReducer:
            async def execute_reduction(self, contract: ReductionContract) -> AggregatedResult:
                # Aggregate and transform results
                ...

            @property
            def node_id(self) -> str:
                return "reducer-aggregation-1"

            @property
            def node_type(self) -> str:
                return "reducer"

        # Runtime validation
        reducer = MyReducer()
        assert isinstance(reducer, ProtocolOnexReducerNodeLegacy)
        ```

    Common Patterns:
        - Map-Reduce: Combine outputs from parallel Compute nodes
        - Event Sourcing: Create workflow state projections from events
        - Metrics Aggregation: Summarize performance and execution metrics
        - Result Synthesis: Combine outputs into final workflow result
    """

    async def execute_reduction(self, contract: object) -> object:
        """
        Execute reduction workflow.

        Aggregates data from multiple sources and transforms it into a
        consolidated result. The reduction operation combines inputs
        according to the contract specification.

        Args:
            contract: Reduction contract containing input data to aggregate,
                     reduction configuration, and output specifications.
                     Type is typically a ModelContract subclass specific
                     to the reduction operation.

        Returns:
            Aggregated result containing the combined and transformed data.
            Return type matches the contract's output specification.

        Raises:
            ReductionError: When aggregation fails due to invalid inputs
            DataConsistencyError: When input data is inconsistent or incomplete
            PersistenceError: When state snapshot or result storage fails

        Implementation Requirements:
            - Should implement associative operations when possible
            - Must handle missing or partial inputs gracefully
            - Should support incremental reduction for streaming data
            - Must be idempotent for workflow replay scenarios
            - Should preserve error context from failed inputs
            - Must emit metrics for reduction performance
        """
        ...

    @property
    def node_id(self) -> str:
        """
        Get unique node identifier.

        Returns a globally unique identifier for this reducer node instance.
        Used for node registration, discovery, and tracking in distributed systems.

        Returns:
            str: Unique node identifier, typically in format:
                 "reducer-{operation-type}-{instance-id}"

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

        Returns the node type classification for this reducer.
        Used for node routing, capability discovery, and workflow planning.

        Returns:
            str: Node type identifier, always "reducer" for this protocol.
                 May include subtypes like "reducer:aggregation" or
                 "reducer:projection" for specialized implementations.

        Implementation Notes:
            - Must return "reducer" or a subtype of reducer
            - Used by node registry for capability-based routing
            - Enables workflow engine to select appropriate reducers
            - May be used for load balancing and node selection
        """
        ...
