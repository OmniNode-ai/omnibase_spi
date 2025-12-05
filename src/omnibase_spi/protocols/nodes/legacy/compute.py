"""DEPRECATED: Legacy compute node protocol.

.. deprecated:: 0.3.0
    Use :class:`omnibase_spi.protocols.nodes.ProtocolComputeNode` instead.
    This module will be removed in v0.5.0.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ProtocolComputeNodeLegacy(Protocol):
    """
    DEPRECATED: Legacy protocol for imperative compute nodes.

    This interface is deprecated and will be removed in v0.5.0.
    Migrate to ProtocolComputeNode for contract-driven compute nodes.

    Migration guide:
        - Replace execute_compute() with execute()
        - Use ModelComputeInput/ModelComputeOutput types
        - Add is_deterministic property

    .. deprecated:: 0.3.0
        Use :class:`ProtocolComputeNode` instead.
    """

    async def execute_compute(self, contract: Any) -> Any:
        """
        Execute computation (legacy signature).

        DEPRECATED: Use ProtocolComputeNode.execute() instead.

        Args:
            contract: The compute contract specifying the operation.

        Returns:
            The result of the computation.

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
