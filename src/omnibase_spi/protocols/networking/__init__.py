"""Protocols for network communication, HTTP requests, and data exchange."""

from __future__ import annotations

from .protocol_circuit_breaker import ProtocolCircuitBreaker
from .protocol_communication_bridge import ProtocolCommunicationBridge
from .protocol_http_client import ProtocolHttpClient
from .protocol_http_extended import ProtocolHttpExtendedClient

__all__ = [
    # Core networking protocols
    "ProtocolCircuitBreaker",
    "ProtocolCommunicationBridge",
    "ProtocolHttpClient",
    "ProtocolHttpExtendedClient",
]
