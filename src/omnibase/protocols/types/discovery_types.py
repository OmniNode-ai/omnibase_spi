"""
Discovery protocol types for ONEX SPI interfaces.

Domain: Service and node discovery protocols
"""

from typing import Dict, Literal, Protocol
from uuid import UUID

from omnibase.protocols.types.core_types import ProtocolSemVer

# Discovery result types
DiscoveryStatus = Literal["found", "not_found", "error", "timeout"]
HandlerStatus = Literal["available", "busy", "offline", "error"]

# Handler capability types
CapabilityValue = str | int | float | bool | list[str]


# Handler discovery protocols
class ProtocolHandlerCapability(Protocol):
    """Protocol for node capability objects."""

    capability_name: str
    capability_value: CapabilityValue
    is_required: bool
    version: ProtocolSemVer


class ProtocolHandlerInfo(Protocol):
    """Protocol for node information objects."""

    node_id: UUID
    node_name: str
    node_type: str
    status: HandlerStatus
    capabilities: list[str]
    metadata: dict[str, CapabilityValue]


class ProtocolDiscoveryQuery(Protocol):
    """Protocol for discovery query objects."""

    query_id: UUID
    target_type: str
    required_capabilities: list[str]
    filters: dict[str, str]
    timeout_seconds: float


class ProtocolDiscoveryResult(Protocol):
    """Protocol for discovery result objects."""

    query_id: UUID
    status: DiscoveryStatus
    nodes_found: int
    discovery_time: float
    error_message: str | None


# Handler registration protocols
class ProtocolHandlerRegistration(Protocol):
    """Protocol for node registration objects."""

    node_id: UUID
    registration_data: dict[str, CapabilityValue]
    registration_time: float
    expires_at: float | None
    is_active: bool
