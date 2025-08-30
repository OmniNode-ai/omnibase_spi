"""
Core Protocol Interfaces

System-level contracts for serialization, schema loading, workflow processing,
logging, node registry, and other core functionality supporting the ONEX 
Messaging Design v0.3.
"""

from omnibase.protocols.core.protocol_node_registry import (
    ProtocolNodeInfo,
    ProtocolNodeRegistry,
)
from omnibase.protocols.core.protocol_workflow_reducer import ProtocolWorkflowReducer

__all__ = [
    # Advanced workflow protocols
    "ProtocolWorkflowReducer",
    # Node discovery and registry
    "ProtocolNodeInfo",
    "ProtocolNodeRegistry",
]
