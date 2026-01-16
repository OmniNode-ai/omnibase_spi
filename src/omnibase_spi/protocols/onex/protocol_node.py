"""Legacy protocol for ONEX node implementations with dynamic loading support.

.. deprecated:: 0.3.0
    This module contains the legacy ProtocolOnexNodeLegacy protocol.
    For new implementations, use the specialized v0.3.0 node protocols:
    - :class:`omnibase_spi.protocols.nodes.ProtocolComputeNode` for pure transformations
    - :class:`omnibase_spi.protocols.nodes.ProtocolEffectNode` for side-effecting operations
    - :class:`omnibase_spi.protocols.nodes.ProtocolReducerNode` for aggregations
    - :class:`omnibase_spi.protocols.nodes.ProtocolOrchestratorNode` for workflow coordination

    The v0.3.0 node protocols provide a cleaner interface with:
    - Async execute() method with typed input/output models
    - Better separation of concerns (compute vs effect vs orchestration)
    - Alignment with the v0.3.0 node architecture
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from omnibase_spi.protocols.node.protocol_node_configuration import (
        ProtocolNodeConfiguration,
    )
    from omnibase_spi.protocols.types.protocol_core_types import ContextValue


@runtime_checkable
class ProtocolOnexNodeLegacy(Protocol):
    """
    Legacy protocol for ONEX node implementations.

    .. deprecated:: 0.3.0
        Use a specialized node protocol instead (e.g., ProtocolComputeNode, ProtocolEffectNode).
        This protocol is maintained for backward compatibility with existing
        node_loader.py implementations but will be removed in v0.5.0.

    All ONEX nodes must implement these methods to be compatible with the
    dynamic node loading system and container orchestration.

    This protocol defines the standard interface that node_loader.py expects
    when loading and validating nodes.

    Key Features:
        - Standard execution interface
        - Configuration metadata access
        - Input/output type definitions
        - Runtime compatibility validation

    Breaking Changes (v2.0):
        - get_input_type() -> get_input_model() for clarity
        - get_output_type() -> get_output_model() for clarity

    Migration Guide:
        For existing implementations, migrate to one of the specialized node protocols.
        The base ProtocolNode provides only identity/metadata; use a specialized protocol
        for execution behavior:

        ```python
        # Old (ProtocolOnexNodeLegacy)
        from omnibase_spi.protocols.types.protocol_core_types import ContextValue

        class MyNode(ProtocolOnexNodeLegacy):
            def run(
                self, *args: ContextValue, **kwargs: ContextValue
            ) -> ContextValue: ...

        # New - For pure transformations (no side effects):
        from typing import TYPE_CHECKING

        if TYPE_CHECKING:
            from omnibase_core.models.compute import (
                ModelComputeInput,
                ModelComputeOutput,
            )

        class MyComputeNode:
            '''Implements ProtocolComputeNode interface.'''

            @property
            def node_id(self) -> str:
                return "my_node.v1"

            @property
            def node_type(self) -> str:
                return "compute"

            @property
            def version(self) -> str:
                return "1.0.0"

            @property
            def is_deterministic(self) -> bool:
                return True

            async def execute(
                self, input_data: "ModelComputeInput"
            ) -> "ModelComputeOutput":
                # Implementation here
                ...

        # New - For side-effecting operations (I/O, API calls, etc.):
        from typing import TYPE_CHECKING

        if TYPE_CHECKING:
            from omnibase_core.models.effect import (
                ModelEffectInput,
                ModelEffectOutput,
            )

        class MyEffectNode:
            '''Implements ProtocolEffectNode interface.'''

            @property
            def node_id(self) -> str:
                return "my_effect_node.v1"

            @property
            def node_type(self) -> str:
                return "effect"

            @property
            def version(self) -> str:
                return "1.0.0"

            async def initialize(self) -> None:
                # Set up connections, load resources
                ...

            async def shutdown(self, timeout_seconds: float = 30.0) -> None:
                # Clean up connections, flush pending operations
                ...

            async def execute(
                self, input_data: "ModelEffectInput"
            ) -> "ModelEffectOutput":
                # Implementation here
                ...
        ```
    """

    def run(self, *args: ContextValue, **kwargs: ContextValue) -> ContextValue:
        """
        Execute the node with provided arguments.

        Runs the node's primary operation with positional and keyword arguments.
        This is the main entry point for node execution.

        Args:
            *args: Positional arguments for node execution.
            **kwargs: Keyword arguments for node execution.

        Returns:
            ContextValue: The result of the node execution.

        Raises:
            NodeExecutionError: When node execution fails.
            ValidationError: When input validation fails.
        """
        ...

    async def get_node_config(self) -> ProtocolNodeConfiguration:
        """
        Get the node's configuration.

        Retrieves the configuration metadata for this node including
        node type, capabilities, and runtime settings.

        Returns:
            ProtocolNodeConfiguration: The node's configuration object.

        Raises:
            NodeNotInitializedError: If the node is not properly initialized.
        """
        ...

    async def get_input_model(self) -> type[ContextValue]:
        """
        Get the input model type for this node.

        Returns the type class representing the expected input data
        structure for this node's execution.

        Returns:
            type[ContextValue]: The input model type class.

        Raises:
            NodeNotInitializedError: If the node is not properly initialized.
        """
        ...

    async def get_output_model(self) -> type[ContextValue]:
        """
        Get the output model type for this node.

        Returns the type class representing the output data structure
        produced by this node's execution.

        Returns:
            type[ContextValue]: The output model type class.

        Raises:
            NodeNotInitializedError: If the node is not properly initialized.
        """
        ...
