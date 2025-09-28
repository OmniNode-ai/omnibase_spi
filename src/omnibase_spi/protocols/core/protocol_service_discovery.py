"""
Protocol for Service Discovery abstraction.

Provides a clean interface for service discovery systems (Consul, etcd, etc.)
with proper fallback strategies and error handling.
"""

from typing import Protocol, runtime_checkable

from omnibase_spi.protocols.types.protocol_core_types import (
    ProtocolServiceHealthStatus,
    ProtocolServiceInstance,
    ProtocolServiceMetadata,
)


@runtime_checkable
class ProtocolServiceDiscovery(Protocol):
    """
        Protocol for service discovery systems.

        Abstracts service registration, discovery, and health checking
    from specific implementations like Consul, etcd, or in-memory fallbacks.

        Key Features:
            - Service registration and deregistration
            - Service discovery with health filtering
            - Key-value store functionality
            - Health monitoring capabilities
            - Clean resource management
    """

    async def register_service(
        self,
        service_name: str,
        service_id: str,
        host: str,
        port: int,
        metadata: "ProtocolServiceMetadata",
        health_check_url: str | None = None,
        tags: list[str] | None = None,
    ) -> bool: ...

    async def deregister_service(self, service_id: str) -> bool: ...

    async def discover_services(
        self,
        service_name: str,
        healthy_only: bool = True,
        tags: list[str] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> tuple[list["ProtocolServiceInstance"], bool]: ...

    async def get_service_health(
        self, service_id: str
    ) -> "ProtocolServiceHealthStatus": ...

    async def set_key_value(self, key: str, value: str) -> bool: ...

    async def get_key_value(self, key: str) -> str | None: ...

    async def delete_key(self, key: str) -> bool: ...

    async def list_keys(self, prefix: str) -> list[str]: ...

    async def health_check(self) -> bool: ...
