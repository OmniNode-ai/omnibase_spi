"""DEPRECATED: Legacy orchestrator node protocol.

.. deprecated:: 0.3.0
    Use :class:`omnibase_spi.protocols.nodes.ProtocolOrchestratorNode` instead.
    This module will be removed in v0.5.0.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ProtocolOrchestratorNodeLegacy(Protocol):
    """
    DEPRECATED: Legacy protocol for imperative orchestrator nodes.

    This interface is deprecated and will be removed in v0.5.0.
    Migrate to ProtocolOrchestratorNode for contract-driven orchestrator nodes.

    Migration guide:
        - Replace execute_orchestration() with execute()
        - Use ModelOrchestrationInput/ModelOrchestrationOutput types

    .. deprecated:: 0.3.0
        Use :class:`ProtocolOrchestratorNode` instead.
    """

    async def execute_orchestration(self, contract: Any) -> Any:
        """
        Execute orchestration (legacy signature).

        DEPRECATED: Use ProtocolOrchestratorNode.execute() instead.
        """
        ...

    @property
    def node_id(self) -> str:
        """Unique node identifier."""
        ...
