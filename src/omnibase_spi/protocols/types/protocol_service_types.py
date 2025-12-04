"""Service protocol types for ONEX SPI interfaces."""

from typing import Protocol, runtime_checkable
from uuid import UUID

from omnibase_spi.protocols.types.protocol_base_types import (
    ContextValue,
    LiteralHealthStatus,
    ProtocolDateTime,
    ProtocolSemVer,
)


@runtime_checkable
class ProtocolServiceMetadata(Protocol):
    """Protocol for service metadata."""

    data: dict[str, "ContextValue"]
    version: "ProtocolSemVer"
    capabilities: list[str]
    tags: list[str]

    async def validate_service_metadata(self) -> bool: ...

    def has_capabilities(self) -> bool: ...


@runtime_checkable
class ProtocolServiceInstance(Protocol):
    """Protocol for service instance information."""

    service_id: UUID
    service_name: str
    host: str
    port: int
    metadata: "ProtocolServiceMetadata"
    health_status: "LiteralHealthStatus"
    last_seen: "ProtocolDateTime"

    async def validate_service_instance(self) -> bool: ...

    def is_available(self) -> bool: ...


@runtime_checkable
class ProtocolServiceHealthStatus(Protocol):
    """Protocol for service health status."""

    service_id: UUID
    status: "LiteralHealthStatus"
    last_check: "ProtocolDateTime"
    details: dict[str, "ContextValue"]

    async def validate_health_status(self) -> bool: ...

    def is_healthy(self) -> bool: ...
