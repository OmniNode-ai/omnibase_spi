"""
Discovery Protocols - SPI Interface Exports.

Node discovery and registration protocols:
- Handler discovery for finding file type handlers
- Node registry for dynamic registration
"""

from .protocol_handler_discovery import (
    ProtocolHandlerDiscovery,
    ProtocolHandlerInfo,
    ProtocolNodeDiscoveryRegistry,
)

__all__ = [
    "ProtocolHandlerDiscovery",
    "ProtocolHandlerInfo",
    "ProtocolNodeDiscoveryRegistry",
]
