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
    """
    Protocol for service metadata including capabilities and tags.

    Provides comprehensive metadata about a service including version,
    capabilities, and classification tags. Used for service discovery
    and capability matching.

    Attributes:
        data: Key-value metadata storage.
        version: Semantic version of the service.
        capabilities: List of capability identifiers the service provides.
        tags: Classification tags for service categorization.

    Example:
        ```python
        class AuthServiceMetadata:
            data: dict[str, ContextValue] = {"region": "us-east"}
            version: ProtocolSemVer = semver_impl
            capabilities: list[str] = ["oauth2", "jwt", "saml"]
            tags: list[str] = ["security", "identity", "production"]

            async def validate_service_metadata(self) -> bool:
                return bool(self.capabilities)

            def has_capabilities(self) -> bool:
                return len(self.capabilities) > 0

        metadata = AuthServiceMetadata()
        assert isinstance(metadata, ProtocolServiceMetadata)
        ```
    """

    data: dict[str, "ContextValue"]
    version: "ProtocolSemVer"
    capabilities: list[str]
    tags: list[str]

    async def validate_service_metadata(self) -> bool: ...

    def has_capabilities(self) -> bool: ...


@runtime_checkable
class ProtocolServiceInstance(Protocol):
    """
    Protocol for service instance registration and discovery.

    Represents a running service instance with network location,
    metadata, and health information. Used for service registry
    and load balancing.

    Attributes:
        service_id: Unique identifier for this service instance.
        service_name: Human-readable name of the service.
        host: Hostname or IP address of the service.
        port: Network port the service is listening on.
        metadata: Service metadata including capabilities.
        health_status: Current health state of the instance.
        last_seen: When the instance last reported its status.

    Example:
        ```python
        from uuid import uuid4

        class ApiGatewayInstance:
            service_id: UUID = uuid4()
            service_name: str = "api-gateway"
            host: str = "192.168.1.100"
            port: int = 8080
            metadata: ProtocolServiceMetadata = metadata_impl
            health_status: LiteralHealthStatus = "healthy"
            last_seen: ProtocolDateTime = datetime_impl

            async def validate_service_instance(self) -> bool:
                return bool(self.host and self.port)

            def is_available(self) -> bool:
                return self.health_status == "healthy"

        instance = ApiGatewayInstance()
        assert isinstance(instance, ProtocolServiceInstance)
        ```
    """

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
    """
    Protocol for service health status reporting.

    Contains the health status of a specific service instance with
    check timestamp and diagnostic details. Used for health monitoring
    and alerting.

    Attributes:
        service_id: UUID of the service instance.
        status: Current health status.
        last_check: When health was last checked.
        details: Additional diagnostic information.

    Example:
        ```python
        from uuid import uuid4

        class DatabaseHealthStatus:
            service_id: UUID = uuid4()
            status: LiteralHealthStatus = "healthy"
            last_check: ProtocolDateTime = datetime_impl
            details: dict[str, ContextValue] = {
                "connections_active": 45,
                "connections_idle": 5,
                "replication_lag_ms": 12
            }

            async def validate_health_status(self) -> bool:
                return self.last_check is not None

            def is_healthy(self) -> bool:
                return self.status == "healthy"

        health = DatabaseHealthStatus()
        assert isinstance(health, ProtocolServiceHealthStatus)
        ```
    """

    service_id: UUID
    status: "LiteralHealthStatus"
    last_check: "ProtocolDateTime"
    details: dict[str, "ContextValue"]

    async def validate_health_status(self) -> bool: ...

    def is_healthy(self) -> bool: ...
