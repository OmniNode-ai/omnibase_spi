"""Protocol for legacy ONEX compute nodes.

.. deprecated::
    This module contains the legacy ONEX-specific compute node protocol.
    For new implementations, use the canonical v0.3.0 protocol from
    ``omnibase_spi.protocols.nodes.ProtocolComputeNode`` instead.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class ProtocolOnexComputeNodeLegacy(Protocol):
    """
    Legacy protocol for ONEX compute node implementations.

    .. deprecated::
        This is the legacy ONEX-specific compute node protocol with an
        ``execute_compute()`` method signature. For new implementations,
        use the canonical v0.3.0 protocol:
        ``omnibase_spi.protocols.nodes.ProtocolComputeNode``

        The v0.3.0 protocol provides:
        - Typed ``execute()`` method with ``ModelComputeInput``/``ModelComputeOutput``
        - Inheritance from ``ProtocolNode`` base protocol
        - ``is_deterministic`` property for optimization hints

    Compute nodes perform pure computational transformations without side effects.
    They implement algorithms, data transformations, business logic, and
    computational operations that produce outputs solely based on their inputs.

    Key Responsibilities:
        - Pure functional transformations
        - Business logic execution
        - Data validation and sanitization
        - Algorithm implementation (sorting, filtering, mapping)
        - Mathematical and statistical computations
        - Data format conversions

    Implementation Notes:
        Compute nodes should:
        - Be pure functions (no side effects)
        - Be deterministic (same inputs → same outputs)
        - Be stateless (no shared mutable state)
        - Be easily testable and composable
        - Support parallel execution when possible
        - Optimize for computational efficiency

    Type Safety:
        This protocol is runtime checkable, enabling isinstance() validation
        for dynamic node loading and dependency injection systems.

    Example Usage:
        ```python
        from omnibase_spi.protocols.onex import ProtocolOnexComputeNodeLegacy

        class MyCompute:
            async def execute_compute(self, contract: ComputeContract) -> ComputeResult:
                # Perform pure computation
                ...

            @property
            def node_id(self) -> str:
                return "compute-transform-1"

            @property
            def node_type(self) -> str:
                return "compute"

        # Runtime validation
        compute = MyCompute()
        assert isinstance(compute, ProtocolOnexComputeNodeLegacy)
        ```

    See Also:
        - ``omnibase_spi.protocols.nodes.ProtocolComputeNode``: Canonical v0.3.0 protocol
        - ``omnibase_spi.protocols.nodes.ProtocolNode``: Base node protocol

    Common Patterns:
        - Data Transformation: Convert between formats or schemas
        - Validation: Check business rules and constraints
        - Filtering: Select subsets based on predicates
        - Mapping: Transform collections element-wise
        - Aggregation: Compute statistics and summaries
        - Enrichment: Add computed fields to data structures
    """

    async def execute_compute(self, contract: object) -> object:
        """
        Execute compute workflow.

        Performs a pure computational transformation that produces outputs
        based solely on inputs without causing side effects. The operation
        should be deterministic and stateless.

        Args:
            contract: Compute contract containing input data, transformation
                     configuration, and output specifications. Type is typically
                     a ModelContract subclass specific to the computation.

        Returns:
            Computation result containing the transformed data. Return type
            matches the contract's output specification.

        Raises:
            ComputationError: When computation fails due to invalid inputs
            ValidationError: When input validation fails
            TransformationError: When data transformation cannot be completed
            TimeoutError: When computation exceeds allowed duration

        Implementation Requirements:
            - Must be a pure function (no side effects)
            - Should be deterministic (same inputs → same outputs)
            - Must not modify input data (immutable operations)
            - Should not maintain internal state between invocations
            - Must handle edge cases (empty inputs, null values, etc.)
            - Should validate inputs before performing computations
            - Must emit metrics for computation duration
            - Should optimize for performance and memory efficiency
            - Must be thread-safe for parallel execution

        Performance Considerations:
            - Avoid blocking I/O operations (use Effect nodes instead)
            - Minimize memory allocations for large datasets
            - Consider streaming for large data transformations
            - Use efficient algorithms and data structures
            - Profile and optimize hot paths
        """
        ...

    @property
    def node_id(self) -> str:
        """
        Get unique node identifier.

        Returns a globally unique identifier for this compute node instance.
        Used for node registration, discovery, and tracking in distributed systems.

        Returns:
            str: Unique node identifier, typically in format:
                 "compute-{operation-type}-{instance-id}"

        Implementation Notes:
            - Must be unique across all nodes in the system
            - Should be stable across restarts for workflow replay
            - Used as key in service registry and discovery systems
            - Included in all workflow events for tracing
            - Useful for performance profiling and optimization
        """
        ...

    @property
    def node_type(self) -> str:
        """
        Get node type identifier.

        Returns the node type classification for this compute node.
        Used for node routing, capability discovery, and workflow planning.

        Returns:
            str: Node type identifier, always "compute" for this protocol.
                 May include subtypes like "compute:transform",
                 "compute:validate", or "compute:aggregate" for specialized
                 implementations.

        Implementation Notes:
            - Must return "compute" or a subtype of compute
            - Used by node registry for capability-based routing
            - Enables workflow engine to select appropriate compute nodes
            - May be used for load balancing and parallel execution
            - Helps identify CPU-intensive nodes for resource allocation
        """
        ...
