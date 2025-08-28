"""
ONEX Protocol Interfaces

This package contains all protocol definitions that define the contracts
for ONEX services. These protocols enable duck typing and dependency 
injection without requiring concrete implementations.
"""

# Import working protocols for easy access
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
