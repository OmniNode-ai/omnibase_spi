"""
Discovery protocol types for ONEX SPI interfaces.

Domain: Service and node discovery protocols
"""

from typing import Literal, Protocol, runtime_checkable
from uuid import UUID

from omnibase_spi.protocols.types.protocol_core_types import ProtocolSemVer

# Discovery result types
LiteralDiscoveryStatus = Literal["found", "not_found", "error", "timeout"]
LiteralHandlerStatus = Literal["available", "busy", "offline", "error"]

# === Capability Value Protocol Hierarchy (Eliminates Union anti-patterns) ===


@runtime_checkable
class ProtocolCapabilityValue(Protocol):
    """Protocol for capability data values supporting validation and serialization."""

    def validate_for_capability(self) -> bool:
        """Validate value is safe for capability storage."""
        ...

    def serialize_for_capability(self) -> dict[str, object]:
        """Serialize value for capability metadata."""
        ...

    def get_capability_type_hint(self) -> str:
        """Get type hint for capability schema validation."""
        ...


@runtime_checkable
class ProtocolCapabilityStringValue(ProtocolCapabilityValue, Protocol):
    """Protocol for string-based capability values (names, descriptions, IDs)."""

    value: str


@runtime_checkable
class ProtocolCapabilityNumericValue(ProtocolCapabilityValue, Protocol):
    """Protocol for numeric capability values (counts, measurements, scores)."""

    value: int | float


@runtime_checkable
class ProtocolCapabilityBooleanValue(ProtocolCapabilityValue, Protocol):
    """Protocol for boolean capability values (flags, enabled/disabled)."""

    value: bool


@runtime_checkable
class ProtocolCapabilityStringListValue(ProtocolCapabilityValue, Protocol):
    """Protocol for string list capability values (tags, categories, identifiers)."""

    value: list[str]


# Backward compatibility alias - use ProtocolCapabilityValue for new code
CapabilityValue = ProtocolCapabilityValue


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
    status: LiteralHandlerStatus
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
    status: LiteralDiscoveryStatus
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
