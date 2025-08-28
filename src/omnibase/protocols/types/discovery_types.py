"""
Discovery protocol types for ONEX SPI interfaces.

Domain: Service and handler discovery protocols
"""

from typing import Dict, Literal, Protocol, Union
from uuid import UUID

# Discovery result types
DiscoveryStatus = Literal["found", "not_found", "error", "timeout"]
HandlerStatus = Literal["available", "busy", "offline", "error"]

# Handler capability types
CapabilityValue = Union[str, int, float, bool, list[str]]


# Handler discovery protocols
class ProtocolHandlerCapability(Protocol):
    """Protocol for handler capability objects."""

    capability_name: str
    capability_value: CapabilityValue
    is_required: bool
    version: str


class ProtocolHandlerInfo(Protocol):
    """Protocol for handler information objects."""

    handler_id: UUID
    handler_name: str
    handler_type: str
    status: HandlerStatus
    capabilities: list[str]
    metadata: Dict[str, CapabilityValue]


class ProtocolDiscoveryQuery(Protocol):
    """Protocol for discovery query objects."""

    query_id: UUID
    target_type: str
    required_capabilities: list[str]
    filters: Dict[str, str]
    timeout_seconds: float


class ProtocolDiscoveryResult(Protocol):
    """Protocol for discovery result objects."""

    query_id: UUID
    status: DiscoveryStatus
    handlers_found: int
    discovery_time: float
    error_message: str | None


# Handler registration protocols
class ProtocolHandlerRegistration(Protocol):
    """Protocol for handler registration objects."""

    handler_id: UUID
    registration_data: Dict[str, CapabilityValue]
    registration_time: float
    expires_at: float | None
    is_active: bool
