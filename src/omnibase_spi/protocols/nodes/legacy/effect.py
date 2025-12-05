"""DEPRECATED: Legacy effect node protocol.

.. deprecated:: 0.3.0
    Use :class:`omnibase_spi.protocols.nodes.ProtocolEffectNode` instead.
    This module will be removed in v0.5.0.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ProtocolEffectNodeLegacy(Protocol):
    """
    DEPRECATED: Legacy protocol for imperative effect nodes.

    This interface is deprecated and will be removed in v0.5.0.
    Migrate to ProtocolEffectNode for contract-driven effect nodes.

    Migration guide:
        - Replace execute_effect() with execute()
        - Use ModelEffectInput/ModelEffectOutput types
        - Add initialize() and shutdown() lifecycle methods

    .. deprecated:: 0.3.0
        Use :class:`ProtocolEffectNode` instead.
    """

    async def execute_effect(self, contract: Any) -> Any:
        """
        Execute effect operation (legacy signature).

        DEPRECATED: Use ProtocolEffectNode.execute() instead.
        """
        ...

    @property
    def node_id(self) -> str:
        """Unique node identifier."""
        ...
