"""Protocols for network communication, HTTP requests, and data exchange."""

from __future__ import annotations

from abc import ABC

from .protocol_circuit_breaker import ProtocolCircuitBreaker
from .protocol_communication_bridge import ProtocolCommunicationBridge
from .protocol_http_client import ProtocolHttpClient
from .protocol_http_extended import ProtocolHttpExtendedClient
from .protocol_kafka_client import ProtocolKafkaClient
from .protocol_kafka_extended import ProtocolKafkaExtendedClient

__all__ = [
    "ProtocolCircuitBreaker",
    "ProtocolCommunicationBridge",
    "ProtocolHttpClient",
    "ProtocolHttpExtendedClient",
    "ProtocolKafkaClient",
    "ProtocolKafkaExtendedClient",
]
