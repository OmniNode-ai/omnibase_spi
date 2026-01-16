"""Legacy protocol for ONEX node implementations with dynamic loading support.

.. deprecated:: 0.3.0
    This module contains the legacy ProtocolOnexNodeLegacy protocol.
    For new implementations, use the canonical v0.3.0 protocol at
    :class:`omnibase_spi.protocols.nodes.ProtocolNode` instead.

    The canonical ProtocolNode provides a cleaner interface with:
    - Async execute() method instead of sync run()
    - Better separation of concerns
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
        Use :class:`omnibase_spi.protocols.nodes.ProtocolNode` instead.
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
        For existing implementations, migrate to the canonical protocol:
        ```python
        # Old (ProtocolOnexNodeLegacy)
        class MyNode(ProtocolOnexNodeLegacy):
            def run(self, *args, **kwargs) -> ContextValue: ...

        # New (protocols.nodes.ProtocolNode)
        from omnibase_spi.protocols.nodes import ProtocolNode

        class MyNode(ProtocolNode):
            async def execute(self, input_data: ModelNodeInput) -> ModelNodeOutput: ...
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
        """
        ...

    async def get_input_model(self) -> type[ContextValue]:
        """
        Get the input model type for this node.

        Returns the type class representing the expected input data
        structure for this node's execution.

        Returns:
            type[ContextValue]: The input model type class.
        """
        ...

    async def get_output_model(self) -> type[ContextValue]:
        """
        Get the output model type for this node.

        Returns the type class representing the output data structure
        produced by this node's execution.

        Returns:
            type[ContextValue]: The output model type class.
        """
        ...
