"""
ONEX Security Protocols - SPI Interface Exports.

Security-related protocols for breaking circular import dependencies:
- ProtocolSecurityEvent for security event interfaces
- ProtocolDetectionMatch for detection match interfaces
"""

from .protocol_detection_match import ProtocolDetectionMatch
from .protocol_security_event import ProtocolSecurityEvent

__all__ = [
    "ProtocolDetectionMatch",
    "ProtocolSecurityEvent",
]
