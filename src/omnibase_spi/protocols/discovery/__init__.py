"""
Discovery Protocols - SPI Interface Exports.

Node discovery and registration protocols:
- Handler discovery for finding file type handlers
- Node registry for dynamic registration
- Base handler protocol for simple handler patterns
"""

from .protocol_base_handler import ProtocolBaseHandler
from .protocol_handler_discovery import (
    ProtocolFileHandlerRegistry,
    ProtocolHandlerDiscovery,
    ProtocolHandlerInfo,
)

__all__ = [
    "ProtocolBaseHandler",
    "ProtocolFileHandlerRegistry",
    "ProtocolHandlerDiscovery",
    "ProtocolHandlerInfo",
]
