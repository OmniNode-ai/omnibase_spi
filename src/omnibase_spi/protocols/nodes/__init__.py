"""Node protocol interfaces for omnibase_spi v0.3.0."""

from omnibase_spi.protocols.nodes.base import ProtocolNode
from omnibase_spi.protocols.nodes.compute import ProtocolComputeNode
from omnibase_spi.protocols.nodes.effect import ProtocolEffectNode
from omnibase_spi.protocols.nodes.orchestrator import ProtocolOrchestratorNode
from omnibase_spi.protocols.nodes.reducer import ProtocolReducerNode

__all__ = [
    "ProtocolComputeNode",
    "ProtocolEffectNode",
    "ProtocolNode",
    "ProtocolOrchestratorNode",
    "ProtocolReducerNode",
]
