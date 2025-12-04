"""
DEPRECATED: Legacy node protocol interfaces.

This module contains deprecated interfaces that will be removed in v0.5.0.
Use the standard interfaces from omnibase_spi.protocols.nodes instead.

Migration:
    - ProtocolEffectNodeLegacy -> ProtocolEffectNode
    - ProtocolComputeNodeLegacy -> ProtocolComputeNode
    - ProtocolReducerNodeLegacy -> ProtocolReducerNode
    - ProtocolOrchestratorNodeLegacy -> ProtocolOrchestratorNode
"""
import warnings

warnings.warn(
    "The omnibase_spi.protocols.nodes.legacy module is deprecated. "
    "Use omnibase_spi.protocols.nodes for standard interfaces. "
    "Legacy interfaces will be removed in v0.5.0.",
    DeprecationWarning,
    stacklevel=2,
)

from omnibase_spi.protocols.nodes.legacy.compute import ProtocolComputeNodeLegacy
from omnibase_spi.protocols.nodes.legacy.effect import ProtocolEffectNodeLegacy
from omnibase_spi.protocols.nodes.legacy.orchestrator import ProtocolOrchestratorNodeLegacy
from omnibase_spi.protocols.nodes.legacy.reducer import ProtocolReducerNodeLegacy

__all__ = [
    "ProtocolComputeNodeLegacy",
    "ProtocolEffectNodeLegacy",
    "ProtocolOrchestratorNodeLegacy",
    "ProtocolReducerNodeLegacy",
]
