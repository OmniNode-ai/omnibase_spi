"""DEPRECATED: Legacy reducer node protocol.

.. deprecated:: 0.3.0
    Use :class:`omnibase_spi.protocols.nodes.ProtocolReducerNode` instead.
    This module will be removed in v0.5.0.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ProtocolReducerNodeLegacy(Protocol):
    """
    DEPRECATED: Legacy protocol for imperative reducer nodes.

    This interface is deprecated and will be removed in v0.5.0.
    Migrate to ProtocolReducerNode for contract-driven reducer nodes.

    Migration guide:
        - Replace execute_reduction() with execute()
        - Use ModelReductionInput/ModelReductionOutput types

    .. deprecated:: 0.3.0
        Use :class:`ProtocolReducerNode` instead.
    """

    async def execute_reduction(self, contract: Any) -> Any:
        """
        Execute reduction (legacy signature).

        DEPRECATED: Use ProtocolReducerNode.execute() instead.

        Args:
            contract: The reduction contract specifying the operation.

        Returns:
            The result of the reduction operation.

        Raises:
            NotImplementedError: When not implemented by concrete class.
        """
        ...

    @property
    def node_id(self) -> str:
        """Unique node identifier.

        Returns:
            The unique identifier string for this node.
        """
        ...
