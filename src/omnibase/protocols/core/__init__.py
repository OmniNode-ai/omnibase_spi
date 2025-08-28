"""
Core Protocol Interfaces

System-level contracts for serialization, schema loading, workflow processing,
logging, and other core functionality.
"""

from omnibase.protocols.core.protocol_simple_example import (
    ProtocolSimpleEventHandler,
    ProtocolSimpleLogger,
    ProtocolSimpleSerializer,
)

__all__ = [
    "ProtocolSimpleSerializer",
    "ProtocolSimpleLogger",
    "ProtocolSimpleEventHandler",
]
